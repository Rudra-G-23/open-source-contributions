#!/usr/bin/env python3
"""Checks for the data -> CSV -> Markdown pipeline. Run: python3 scripts/test_pipeline.py"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from contributions import (
    PR_URL_RE,
    Contribution,
    load_source,
    parse_contributions,
    read_csv,
    write_csv,
)
from render_readme import classify, escape_cell, render, splice

failures: list[str] = []


def check(label: str, condition: bool) -> None:
    print(f"{'PASS' if condition else 'FAIL'}  {label}")
    if not condition:
        failures.append(label)


def tsv(*rows: str) -> list[dict[str, str]]:
    """Build source rows the way read_source_rows would hand them over."""
    fields = ("title", "url", "repository", "status", "contribution", "impact", "created")
    out = []
    for row in rows:
        parts = [p.strip() for p in row.split("\t")]
        parts += [""] * (len(fields) - len(parts))
        out.append(dict(zip(fields, parts)))
    return out


def main() -> int:
    # --- filtering ---
    result = parse_contributions(
        tsv(
            "fix: a\thttps://github.com/o/r/pull/1\to/r\tMerged\tfix\tX\t2026-01-02",
            "feat: b\thttps://github.com/o/r/pull/2\to/r\tIn Review\tfeat\tY\t2026-01-03",
            "doc: c\thttps://github.com/o/r/pull/3\to/r\tOpen\tdoc\tZ\t2026-01-04",
            "old: d\thttps://github.com/o/r/pull/4\to/r\tClosed\tfix\tW\t2026-01-05",
            "mix: e\thttps://github.com/o/r/pull/5\to/r\tmerged\tfeat\tV\t2026-01-06",
        )
    )
    check("only merged rows kept (case-insensitive)", [c.number for c in result.contributions] == ["5", "1"])
    check("non-merged rows reported as rejects", len(result.rejects) == 3)

    # --- dedupe ---
    dup = parse_contributions(
        tsv(
            "first title\thttps://github.com/O/R/pull/7\tO/R\tMerged\tfix\tA\t2026-02-01",
            "second title\thttps://github.com/o/r/pull/7\to/r\tMerged\tfix\tB\t2026-02-02",
            "other pr\thttps://github.com/o/r/pull/8\to/r\tMerged\tfix\tC\t2026-02-03",
        )
    )
    check("same PR twice -> one row", len(dup.contributions) == 2)
    check("duplicate tracked", len(dup.seen_duplicates) == 1)
    kept7 = [c for c in dup.contributions if c.number == "7"]
    check("first occurrence wins", kept7[0].title == "first title")

    # --- bad URLs / empty rows ---
    bad = parse_contributions(
        tsv(
            "no link\to/r\tMerged\tfix\tA\t2026-03-01",
            "gitlab\thttps://gitlab.com/o/r/pull/9\to/r\tMerged\tfix\tA\t2026-03-02",
            "\t\t\t\t\t\t",
        )
    )
    check("unparseable URLs rejected", len(bad.contributions) == 0 and len(bad.rejects) == 2)
    check("empty row silently ignored", all(r.title for r in bad.rejects))

    # --- ordering + impact fallback chain ---
    ordered = parse_contributions(
        tsv(
            "older\thttps://github.com/o/r/pull/1\to/r\tMerged\t\t\t2026-01-01",
            "newer\thttps://github.com/o/r/pull/2\to/r\tMerged\t\t\t2026-12-01",
        )
    )
    check("newest first", [c.number for c in ordered.contributions] == ["2", "1"])
    check("impact falls back to title", ordered.contributions[0].impact == "newer")

    # --- CSV round trip ---
    merged = load_source()
    with tempfile.TemporaryDirectory() as tmp:
        path = write_csv(merged.contributions, Path(tmp) / "out.csv")
        round_tripped = read_csv(path)
    check(
        "csv round trip preserves every row",
        len(round_tripped) == len(merged.contributions),
    )
    check(
        "csv round trip preserves fields",
        all(
            a.repository == b.repository and a.number == b.number and a.impact == b.impact
            for a, b in zip(merged.contributions, round_tripped)
        ),
    )

    # --- markdown ---
    md = render(merged.contributions, "repo")
    check("repo mode has no date column", "Date" not in md and "2026-" not in md)
    check("every merged PR rendered", all(c.number in md for c in merged.contributions))
    check("links are hyperlinked", md.count("](https://github.com/") == len(merged.contributions))

    impact_md = render(merged.contributions, "impact")
    check("impact mode buckets by theme", "### Bug fixes & hardening" in impact_md)

    check("pipes escaped in cells", escape_cell("a | b") == "a \\| b")
    check("empty input handled", "No merged contributions" in render([], "repo"))

    # --- splice idempotency ---
    once = splice("# Title\n", "body")
    twice = splice(once, "body")
    check("splice replaces in place, no duplication", once.count("contributions:begin") == 1 and twice.count("contributions:begin") == 1)
    check("splice preserves existing content", twice.startswith("# Title"))

    # --- classify ---
    def fake(title: str) -> Contribution:
        return Contribution("o/r", "r", title, f"https://github.com/o/r/pull/1", "1", "", "", "", "", "")

    check("classify maps fix", "Bug fixes" in classify(fake("fix: thing")))
    check("classify maps docs", "Docs" in classify(fake("doc: add CHANGELOG.md")))
    check("classify falls back to Other", classify(fake("qqq")) == "Other contributions")
    check("PR_URL_RE rejects non-github", PR_URL_RE.match("https://example.com/o/r/pull/1") is None)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())