# Command Reference

Every command in this repo, one line each. Copy-paste ready.

All paths are relative to the repo root. Python 3.10+ (uses `match`-free 3.10 syntax; runs on 3.14).

## Setup

| Command | What it does |
| :--- | :--- |
| `python3 scripts/build_csv.py` | Refresh `contributions.csv` from the raw TSV export in `data/`. |
| `python3 scripts/update_impacts.py` | Preview the pending `impact` rewrites as a diff (dry run). |
| `python3 scripts/update_impacts.py --apply` | Write the approved `impact` values into `data/*.tsv`. |
| `python3 scripts/render_readme.py --by repo --write` | Regenerate the README contributions block, grouped by repository. |
| `python3 scripts/render_readme.py --by impact --write` | Regenerate the README contributions block, grouped by impact theme. |
| `python3 scripts/test_pipeline.py` | Run all 24 pipeline checks (filtering, dedupe, CSV, markdown). |

Run those three in that order for a full refresh.

## build_csv.py — raw export to CSV

| Command | What it does |
| :--- | :--- |
| `python3 scripts/build_csv.py` | Filter to merged PRs, drop duplicates, write `contributions.csv`. |
| `python3 scripts/build_csv.py --data data/` | Read the TSV export from a different folder. |
| `python3 scripts/build_csv.py --out /tmp/merged.csv` | Write the CSV somewhere else, leaving the repo copy alone. |
| `python3 scripts/build_csv.py --quiet` | Print only the one-line summary, no per-row skip report. |
| `python3 scripts/build_csv.py --help` | Show usage with examples. |

Keeps only rows where `Status` is `Merged` (case-insensitive). Rows with any other
status are reported under "Skipped", never silently dropped.

## render_readme.py — CSV to Markdown preview

| Command | What it does |
| :--- | :--- |
| `python3 scripts/render_readme.py --by repo` | Print the preview to stdout, one section per repo. |
| `python3 scripts/render_readme.py --by impact` | Print the preview to stdout, one section per impact theme. |
| `python3 scripts/render_readme.py --by repo --write` | Update the marked block inside `README.md`. |
| `python3 scripts/render_readme.py --by repo --out preview.md` | Save the preview to its own file, leave `README.md` untouched. |
| `python3 scripts/render_readme.py --csv other.csv --by repo` | Render from a different CSV. |
| `python3 scripts/render_readme.py --help` | Show usage. |

`--write` only replaces the text between `<!-- contributions:begin -->` and
`<!-- contributions:end -->`. Anything outside those markers is preserved, and
running it twice produces the same file.

## Bucket modes

| Mode | Section headings |
| :--- | :--- |
| `--by repo` | `### owner/repo (N)` — one per repository, PRs listed inside. |
| `--by impact` | `### New features & capabilities` / `### Bug fixes & hardening` / `### Docs, skills & templates` / `### Tests & compatibility` / `### Other contributions` |

Sections are ordered by size, largest first, alphabetical on ties.

## Useful one-liners

| Command | What it does |
| :--- | :--- |
| `python3 scripts/build_csv.py && python3 scripts/render_readme.py --by impact --write` | Full refresh, impact buckets. |
| `python3 scripts/build_csv.py --quiet && python3 scripts/render_readme.py --by repo --out /tmp/preview.md` | Rebuild CSV and preview without touching `README.md`. |
| `python3 scripts/test_pipeline.py 2>&1 \| tail -3` | Run the checks and show just the verdict. |
| `git diff --stat contributions.csv README.md` | See what a refresh changed. |

## Files

| Path | Role |
| :--- | :--- |
| `data/*.tsv` | Raw export. Gitignored — the source of truth lives outside the repo. |
| `contributions.csv` | Merged PRs only, deduped. Generated, safe to delete and rebuild. |
| `README.md` | Hand-written calendar table plus the generated contributions block. |
| `scripts/contributions.py` | Shared parsing: filtering, dedupe, impact resolution, CSV I/O. |
| `scripts/build_csv.py` | CLI: raw export to CSV. |
| `scripts/update_impacts.py` | CLI: approved `impact` rewrites into `data/*.tsv`. |
| `scripts/render_readme.py` | CLI: CSV to Markdown preview. |
| `scripts/test_pipeline.py` | Pipeline checks. |
| `docs/COMMANDS.md` | This file. |
| `.agents/prompts/` | Reusable agent prompts. |

## Impact quality check

The `impact` column is written by hand and varies in strength. Rows like
`airtable mcp` or `Help other contributor` describe the activity, not the effect,
so the README reads thin next to entries that state a real outcome.

To review and rewrite the weak ones against what the PRs actually do:

| Command | What it does |
| :--- | :--- |
| Open `.agents/prompts/impact-review.md` | Prompt that opens each PR in Chrome and upgrades vague impact text. |

The prompt leaves CSV rows alone unless you approve the rewrite, then you re-run
`build_csv.py` and `render_readme.py` as usual.

## Changing impact text

Impact rewrites go in `data/*.tsv` under the `Impact / Notes` column.
`contributions.csv` is generated — an edit there is lost on the next build.

`scripts/update_impacts.py` holds the approved rewrites as a
`repo#PR-number -> text` map so a repeated run is idempotent:

| Command | What it does |
| :--- | :--- |
| `python3 scripts/update_impacts.py` | Print the before/after diff for every rewrite, change nothing. |
| `python3 scripts/update_impacts.py --apply` | Write the rewrites into `data/*.tsv`. |
| `python3 scripts/update_impacts.py --data other/` | Target a different export folder. |

Then rebuild:

```bash
python3 scripts/build_csv.py
python3 scripts/render_readme.py --by repo --write
```

To add a new rewrite, append an entry to `IMPACT_REWRITES` in
`scripts/update_impacts.py`. Keys are `owner/repo#PR-number`, so a rewrite
lands on exactly one row. If a key matches nothing the script warns about it
rather than failing quietly.