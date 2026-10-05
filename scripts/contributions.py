"""Shared logic for turning the raw contribution export into a CSV + Markdown preview.

Pipeline:
    data/*.tsv  ->  (filter Merged, drop duplicates)  ->  contributions.csv  ->  README preview

Kept in one module so the CSV builder and the Markdown renderer agree on parsing
rules instead of drifting apart.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
CSV_PATH = REPO_ROOT / "contributions.csv"
README_PATH = REPO_ROOT / "README.md"

# Only rows whose Status is exactly this make it into the CSV.
MERGED_STATUS = "Merged"

PR_URL_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)"
)

# Field names in the source TSV, matched loosely so column reordering / minor
# renames in the export do not break the parse.
SOURCE_ALIASES: dict[str, tuple[str, ...]] = {
    "title": ("title",),
    "url": ("url", "link", "pr url", "pr link"),
    "repository": ("repository", "repo"),
    "status": ("status", "state"),
    "contribution": ("contribution", "type", "category"),
    "impact": ("impact / notes", "impact", "notes"),
    "experience": ("extra info / any experience / feelings", "extra info", "experience"),
    "created": ("created", "date", "opened"),
    "branding": ("branding", "personal branding"),
}

# Written to contributions.csv. `created` is intentionally kept here: the CSV is
# the source of record. The Markdown preview drops it.
CSV_COLUMNS: tuple[str, ...] = (
    "repository",
    "project",
    "pr_title",
    "pr_url",
    "pr_number",
    "pr_type",
    "impact",
    "branding",
    "notes",
    "created",
)

# Columns the Markdown preview is allowed to show. No dates, by design.
PREVIEW_COLUMNS: tuple[str, ...] = ("pr_title", "impact")


@dataclass(slots=True)
class Contribution:
    """One merged pull request."""

    repository: str
    project: str
    title: str
    url: str
    number: str
    pr_type: str
    impact: str
    branding: str
    notes: str
    created: str

    @property
    def key(self) -> str:
        """Identity used for de-duplication: one PR, one row."""
        return f"{self.repository.lower()}#{self.number}"

    @property
    def linked_title(self) -> str:
        """`[#12 title](url)` - the Markdown table cell."""
        return f"[#{self.number} {self.title}]({self.url})"

    def as_row(self) -> dict[str, str]:
        return {
            "repository": self.repository,
            "project": self.project,
            "pr_title": self.title,
            "pr_url": self.url,
            "pr_number": self.number,
            "pr_type": self.pr_type,
            "impact": self.impact,
            "branding": self.branding,
            "notes": self.notes,
            "created": self.created,
        }


@dataclass(slots=True)
class Reject:
    """A source row that was skipped, with the reason, so nothing fails silently."""

    title: str
    reason: str


@dataclass(slots=True)
class ParseResult:
    contributions: list[Contribution] = field(default_factory=list)
    rejects: list[Reject] = field(default_factory=list)
    seen_duplicates: list[Contribution] = field(default_factory=list)


def _norm_header(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _map_headers(header: Sequence[str]) -> dict[str, int]:
    normalized = [_norm_header(h) for h in header]
    mapping: dict[str, int] = {}
    for field_name, aliases in SOURCE_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapping[field_name] = normalized.index(alias)
                break
    return mapping


def read_source_rows(data_dir: Path = DATA_DIR) -> list[dict[str, str]]:
    """Read every TSV in the data folder, keyed by normalized column name."""
    rows: list[dict[str, str]] = []
    if not data_dir.is_dir():
        return rows
    for path in sorted(data_dir.glob("*.tsv")):
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            if not reader.fieldnames:
                continue
            mapping = _map_headers(reader.fieldnames)
            for raw in reader:
                row = {}
                for field_name, idx in mapping.items():
                    value = raw.get(reader.fieldnames[idx], "") or ""
                    row[field_name] = value.strip()
                row["_source"] = path.name
                rows.append(row)
    return rows


def _first_nonempty(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key, "").strip()
        if value:
            return value
    return ""


def _tidy(text: str) -> str:
    """Collapse whitespace so multi-line notes fit inside a CSV cell / table cell."""
    return re.sub(r"\s+", " ", text).strip()


def parse_contributions(rows: Iterable[dict[str, str]]) -> ParseResult:
    """Filter to merged PRs, drop duplicates, and resolve the impact text."""
    result = ParseResult()
    seen: dict[str, Contribution] = {}

    for row in rows:
        title = _tidy(_first_nonempty(row, "title"))
        url = _first_nonempty(row, "url")
        if not title and not url:
            continue

        status = _first_nonempty(row, "status")
        if status.casefold() != MERGED_STATUS.casefold():
            result.rejects.append(Reject(title or url, f"status is {status or 'blank'!r}"))
            continue

        match = PR_URL_RE.match(url)
        if not match:
            result.rejects.append(Reject(title or url, "URL is not a github.com .../pull/N link"))
            continue

        repository = _first_nonempty(row, "repository") or f"{match['owner']}/{match['repo']}"
        contribution = Contribution(
            repository=repository,
            project=match["repo"],
            title=title or f"PR #{match['number']}",
            url=url,
            number=match["number"],
            pr_type=_tidy(_first_nonempty(row, "contribution")),
            impact=_tidy(_first_nonempty(row, "impact", "experience", "contribution", "title")),
            branding=_first_nonempty(row, "branding"),
            notes=_tidy(_first_nonempty(row, "experience")),
            created=_first_nonempty(row, "created"),
        )

        if contribution.key in seen:
            result.seen_duplicates.append(contribution)
            continue
        seen[contribution.key] = contribution
        result.contributions.append(contribution)

    # Newest first. ISO-8601 strings sort correctly as plain strings.
    result.contributions.sort(key=lambda c: c.created, reverse=True)
    return result


def load_source(data_dir: Path = DATA_DIR) -> ParseResult:
    return parse_contributions(read_source_rows(data_dir))


def write_csv(contributions: Sequence[Contribution], path: Path = CSV_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_COLUMNS))
        writer.writeheader()
        for contribution in contributions:
            writer.writerow(contribution.as_row())
    return path


def read_csv(path: Path = CSV_PATH) -> list[Contribution]:
    if not path.exists():
        return []
    out: list[Contribution] = []
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            url = (row.get("pr_url") or "").strip()
            match = PR_URL_RE.match(url)
            out.append(
                Contribution(
                    repository=(row.get("repository") or "").strip(),
                    project=(row.get("project") or "").strip(),
                    title=(row.get("pr_title") or "").strip(),
                    url=url,
                    number=(row.get("pr_number") or match["number"] if match else "").strip(),
                    pr_type=(row.get("pr_type") or "").strip(),
                    impact=(row.get("impact") or "").strip(),
                    branding=(row.get("branding") or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                    created=(row.get("created") or "").strip(),
                )
            )
    return out
