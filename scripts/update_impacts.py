#!/usr/bin/env python3
"""Rewrite the `Impact / Notes` column in the raw TSV export.

Impact rewrites belong in `data/*.tsv`, not in the generated `contributions.csv` —
editing the CSV directly loses the change on the next build.

    python3 scripts/update_impacts.py --apply
    python3 scripts/update_impacts.py            # dry run, prints the diff

Each rewrite is matched on `repo#PR-number` so it lands on exactly one row.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from contributions import DATA_DIR, PR_URL_RE

# repo#number -> new Impact / Notes text.
# Every value below was verified against the PR description, the linked issue,
# and the maintainer review thread. See .agents/prompts/impact-review.md.
IMPACT_REWRITES: dict[str, str] = {
    "lancedb/lancedb#4211": (
        "Python dict/list values now serialize to JSON strings on ingestion, "
        "including inside structs and lists, so JSON columns accept nested objects "
        "instead of erroring on add and merge_insert"
    ),
    "HelpCode-ai/anythingmcp#610": (
        "Adds Airtable as a read-only MCP adapter (base discovery, schemas, records, "
        "formula filtering, pagination), so agents can read Airtable data through "
        "AnythingMCP without a custom connector"
    ),
    "kayba-ai/agentic-context-engine#143": (
        "Isolates SkillManager state per recursive child session, so failed or "
        "parallel child agents can no longer leak skill mutations back into the "
        "parent session"
    ),
    "pytorch/pytorch#196498": (
        "Ports CPython 3.13 `test_str` to the Dynamo suite: 135 tests run under "
        "Dynamo with the 74 currently-unsupported cases recorded as expected "
        "failures, part of the #196238 porting meta-issue"
    ),
    "pytorch/pytorch#196482": (
        "Ports CPython 3.13 `test_grammar` to the Dynamo suite with the unsupported "
        "cases marked as expected failures, closing one task under the #196238 "
        "porting meta-issue"
    ),
    "traccia-ai/traccia-node#22": (
        "Adds auto-instrumentation for `@google/genai` Interactions calls, and fixes "
        "BatchSpanProcessor dropping queued spans on forceFlush/shutdown — spans were "
        "being lost whenever an export was already in flight"
    ),
    "systempromptio/awesome-ai-agent-governance#40": (
        "Adds Traccia to the governance index's Audit, Observability, and Cost "
        "Control section, listing it as an OpenTelemetry-native option alongside the "
        "OpenAI Agents, CrewAI, and LangChain integrations"
    ),
    "sickn33/agentic-awesome-skills#818": (
        "Adds a vendor-neutral warehouse analytics skill scoped to authorized "
        "read-only work, with explicit access, privacy, and least-privilege "
        "boundaries instead of vendor-specific assumptions"
    ),
    "traccia-ai/traccia-py#25": (
        "Adds bug, feature, and documentation issue templates, so reporters get "
        "structured forms instead of a free-form issue and triage stops depending "
        "on the reporter knowing what to include"
    ),
    "traccia-ai/traccia-py#24": (
        "Repairs CONTRIBUTING.md — working table-of-contents links, a correct "
        "LICENSE reference, and issue-reporting steps that no longer render as "
        "broken code blocks"
    ),
}


def row_key(url: str, repository: str) -> str | None:
    """`owner/repo#number` for a TSV row, or None if the URL is not a PR link."""
    match = PR_URL_RE.match(url.strip())
    if not match:
        return None
    repo = repository.strip() or f"{match['owner']}/{match['repo']}"
    return f"{repo}#{match['number']}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, default=DATA_DIR, help="folder holding the raw *.tsv export")
    parser.add_argument("--apply", action="store_true", help="write changes (default is a dry run)")
    args = parser.parse_args()

    applied: set[str] = set()

    for path in sorted(args.data.glob("*.tsv")):
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            fieldnames = reader.fieldnames or []
            rows = list(reader)

        if "Impact / Notes" not in fieldnames:
            print(f"skip {path.name}: no 'Impact / Notes' column", file=sys.stderr)
            continue

        changed = 0
        for row in rows:
            key = row_key(row.get("URL", ""), row.get("Repository", ""))
            if key not in IMPACT_REWRITES:
                continue
            new_text = IMPACT_REWRITES[key]
            old_text = (row.get("Impact / Notes") or "").strip()
            # Count the key as matched even when the text is already current, so
            # a re-run on an already-updated export does not report false misses.
            applied.add(key)
            if old_text == new_text:
                continue
            print(f"\n{key}")
            print(f"  - {old_text or '(empty)'}")
            print(f"  + {new_text}")
            row["Impact / Notes"] = new_text
            changed += 1

        if not changed:
            continue
        print(f"\n{path.name}: {changed} row(s) {'updated' if args.apply else 'would change'}")
        if args.apply:
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t")
                writer.writeheader()
                writer.writerows(rows)

    missing = set(IMPACT_REWRITES) - applied
    if missing:
        print(f"\nWARNING: {len(missing)} rewrite(s) matched no row:", file=sys.stderr)
        for key in sorted(missing):
            print(f"  - {key}", file=sys.stderr)

    if not args.apply:
        print("\nDry run. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())