#!/usr/bin/env python3
"""Build contributions.csv from the raw export in data/.

Keeps only rows whose Status is `Merged`, drops duplicate PRs, and reports what
was skipped so nothing disappears quietly.

    python3 scripts/build_csv.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from contributions import CSV_PATH, DATA_DIR, load_source, write_csv


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Filter the raw TSV export to merged PRs and write contributions.csv.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 scripts/build_csv.py\n"
            "  python3 scripts/build_csv.py --data data/ --out contributions.csv\n"
        ),
    )
    parser.add_argument("--data", type=Path, default=DATA_DIR, help="folder holding the raw *.tsv export")
    parser.add_argument("--out", type=Path, default=None, help="output CSV path (default: contributions.csv)")
    parser.add_argument("--quiet", action="store_true", help="print only the one-line summary")
    args = parser.parse_args()

    result = load_source(args.data)

    if not result.contributions:
        print("No merged contributions found. Nothing written.", file=sys.stderr)
        return 1

    path = write_csv(result.contributions, args.out or CSV_PATH)

    print(f"Wrote {len(result.contributions)} merged PRs -> {path}")
    if args.quiet:
        return 0

    print(f"  duplicates dropped : {len(result.seen_duplicates)}")
    print(f"  rows skipped       : {len(result.rejects)}")

    if result.seen_duplicates:
        print("\nDuplicates ignored (same repo + PR number):")
        for dup in result.seen_duplicates:
            print(f"  - {dup.repository}#{dup.number}  {dup.title}")

    if result.rejects:
        print("\nSkipped (not merged / unparseable):")
        for reject in result.rejects:
            print(f"  - {reject.title}  ({reject.reason})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())