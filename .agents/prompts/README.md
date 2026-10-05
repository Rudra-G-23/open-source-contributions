# Agent Prompts

Reusable prompts for this repo. Each one is a self-contained block you can paste
into an agent session.

| Prompt | What it does |
| :--- | :--- |
| [`impact-review.md`](impact-review.md) | Opens each merged PR in Chrome, checks what it really changed, and rewrites weak `impact` text in `contributions.csv`. |

These are plain Markdown, not a plugin format — copy the fenced block and go. No
installation step.

## Conventions these prompts follow

- Edit `data/*.tsv`, not `contributions.csv`. The CSV is generated; direct edits
  vanish on the next `build_csv.py` run.
- Never invent impact. If a PR's real effect cannot be read off the diff or the
  linked issue, the row gets flagged for a human instead of guessed.
- Stop for approval before writing, then rebuild with
  `build_csv.py` → `render_readme.py` → `test_pipeline.py`.
- Rebuild commands are listed in [`docs/COMMANDS.md`](../../docs/COMMANDS.md).