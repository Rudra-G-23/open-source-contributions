#!/usr/bin/env python3
"""Render the README preview from contributions.csv.

Dates are dropped on purpose: entries are bucketed by repo or by impact, and a
date column under those headings is noise.

    python3 scripts/render_readme.py --by repo      # one section per repo
    python3 scripts/render_readme.py --by impact    # one section per impact
    python3 scripts/render_readme.py --write        # update README in place
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from contributions import CSV_PATH, PREVIEW_COLUMNS, Contribution, read_csv

# Generated block is fenced by these markers so `--write` can replace it
# in place and leave the rest of the README untouched.
BEGIN_MARKER = "<!-- contributions:begin -->"
END_MARKER = "<!-- contributions:end -->"

PREVIEW_HEADER = (
    "## 🧑‍💻 Merged Open Source Contributions\n\n"
    "> [!NOTE]\n"
    "> Every row below is a **merged** pull request. Duplicates are removed and\n"
    "> dates are omitted — entries are bucketed instead.\n"
)

BUCKETS_BY_IMPACT: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "New features & capabilities",
        ("feat", "add support", "add a", "implement", "introduce", "integration", "adapter"),
    ),
    (
        "Bug fixes & hardening",
        ("fix", "bug", "hardening", "prevent", "resolve", "correct", "validat", "isolate"),
    ),
    (
        "Docs, skills & templates",
        ("doc", "changelog", "readme", "template", "skill", "guide", "example", "format"),
    ),
    (
        "Tests & compatibility",
        ("test", "port ", "compat", "python 3", "ci ", "pipeline"),
    ),
)


def escape_cell(text: str) -> str:
    """Markdown tables break on raw pipes, so escape them."""
    return text.replace("|", "\\|").strip()


def classify(contribution: Contribution) -> str:
    haystack = f"{contribution.title} {contribution.pr_type} {contribution.impact}".lower()
    for bucket, keywords in BUCKETS_BY_IMPACT:
        if any(keyword in haystack for keyword in keywords):
            return bucket
    return "Other contributions"


def bucket_by_repo(items: list[Contribution]) -> dict[str, list[Contribution]]:
    buckets: dict[str, list[Contribution]] = {}
    for item in items:
        buckets.setdefault(item.repository, []).append(item)
    return buckets


def bucket_by_impact(items: list[Contribution]) -> dict[str, list[Contribution]]:
    buckets: dict[str, list[Contribution]] = {}
    for item in items:
        buckets.setdefault(classify(item), []).append(item)
    return buckets


def render(items: list[Contribution], by: str) -> str:
    if not items:
        return "_No merged contributions yet._\n"

    bucket_fn = bucket_by_repo if by == "repo" else bucket_by_impact
    buckets = bucket_fn(items)

    # Put the biggest buckets first, alphabetically within equal sizes.
    ordered = sorted(buckets.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))

    lines: list[str] = [PREVIEW_HEADER, ""]
    lines.append(f"**{len(items)}** merged PRs across **{len(buckets)}** {'repos' if by == 'repo' else 'buckets'}.\n")

    for name, entries in ordered:
        lines.append(f"### {escape_cell(name)} ({len(entries)})\n")
        lines.append("| " + " | ".join("PR" if c == "pr_title" else "Impact" for c in PREVIEW_COLUMNS) + " |")
        lines.append("| :--- | :--- |")
        for entry in entries:
            cells = [entry.linked_title, escape_cell(entry.impact)]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def splice(existing: str, generated: str) -> str:
    block = f"{BEGIN_MARKER}\n\n{generated}\n{END_MARKER}\n"
    if BEGIN_MARKER in existing and END_MARKER in existing:
        head, _, rest = existing.partition(BEGIN_MARKER)
        _, _, tail = rest.partition(END_MARKER)
        return head + block + tail.lstrip("\n")
    separator = "" if existing.endswith("\n\n") or not existing else "\n"
    return f"{existing}{separator}\n{block}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--by", choices=("repo", "impact"), default="repo")
    parser.add_argument("--csv", type=Path, default=CSV_PATH, help="input CSV path")
    parser.add_argument("--write", action="store_true", help="update README.md in place")
    parser.add_argument("--out", default=None, help="write to this file instead of stdout")
    args = parser.parse_args()

    csv_path = args.csv
    if not csv_path.exists():
        print(f"{csv_path} not found. Run scripts/build_csv.py first.", file=sys.stderr)
        return 1

    items = read_csv(csv_path)
    generated = render(items, args.by)
    block = f"{BEGIN_MARKER}\n\n{generated}\n{END_MARKER}\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(block)
        print(f"Wrote preview -> {args.out}")
    elif args.write:
        from contributions import README_PATH

        existing = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""
        README_PATH.write_text(splice(existing, generated), encoding="utf-8")
        print(f"Updated {README_PATH} (bucketed by {args.by}, {len(items)} PRs)")
    else:
        sys.stdout.write(block)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
