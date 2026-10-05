# Impact Review Prompt

Reusable prompt for auditing the `impact` column in `contributions.csv` against
what the pull requests actually do, and rewriting the weak ones.

You are reviewing the `impact` column of `contributions.csv` in this repo. The
README renders that column verbatim, and several rows describe an *activity*
rather than an *outcome*, so the README reads thin. Your job is to open each
merged PR in Chrome, work out what it actually changed for users, and rewrite any
impact text that undersells it.

### Context you already have

The pipeline is: `data/*.tsv` (raw export) → `scripts/build_csv.py` →
`contributions.csv` → `scripts/render_readme.py` → the marked block in
`README.md`. Only `Status: Merged` rows reach the CSV, and duplicates on
`repo#PR-number` are dropped.

`impact` is resolved with a fallback chain: `Impact / Notes` → `Extra Info` →
`Contribution` → title. So a row can end up showing its own title in the impact
column, which is always worth flagging.

### What counts as weak

An impact is weak if it fails any of these:

- **Restates the title.** "fix(python): convert objects for JSON fields" tells the
  reader nothing they did not get from the title alone.
- **Names the activity, not the effect.** "mcp", "airtable mcp", "test: Dynamo",
  "docs: fix formatting" describe what was touched.
- **Speaks only about the author.** "Help other contributor", "all my learning
  stuff into a skill", "Contributor helps during reporting" — the reader learns
  nothing about the project.
- **Vague quantifier with no subject.** "Enhanced Python 3.13 Compatibility" is
  fine *if* you know what was made compatible and for whom; on its own it is a
  claim with no content.
- **Grammar-broken or truncated.** e.g. `erialized tests that mutate the process`
  looks like a paste accident. Flag it as a data bug rather than guessing.

An impact is strong when it says what was broken or missing, what now works, and
who benefits — in one or two sentences, in plain language, no marketing tone.

### Steps

1. Read `contributions.csv`. Triage the `impact` column yourself and shortlist
   every row you judge weak or suspicious. Do not open a browser tab for rows
   that already read fine.

2. For each shortlisted row, open its `pr_url` in Chrome. Gather, in this order
   of preference:
   - the PR description, especially any "why" / motivation / linked-issue section
   - the linked issue, if the PR references one
   - the files changed diff, to see the real scope
   - the review discussion, if a maintainer spelled out the significance

   Stop reading once you can write a concrete sentence. These are small PRs.

3. Draft a replacement for each weak row. Shape it as:
   `<what was broken or missing> → <what now works> → <who benefits>`

   Length: one sentence, or two when the change genuinely needs it. No emoji, no
   "Significantly", no restating the title at the front.

   Weak: `airtable mcp`
   Strong: `Adds Airtable as a read-only MCP source, so agents can pull record
   data without a custom connector`

   Weak: `Help other contributor`
   Strong: `Fixes CONTRIBUTING.md formatting so new contributors can follow the
   setup steps without the headings collapsing`

4. Present your findings as a table: `repo#number`, current impact, what the PR
   actually does, proposed impact, and which files or issue you drew it from.

5. **Stop here and wait for my approval.** Do not edit `contributions.csv` yet.
   I may reject individual rewrites, and some rows will need a call I cannot
   make from the diff alone.

6. After I approve, write the approved `impact` values into
   `data/*.tsv` (the `Impact / Notes` column), not into `contributions.csv`.
   `contributions.csv` is generated — editing it directly loses the change on
   the next build. If a row's text genuinely has no home in the export, say so
   and I will decide.

7. Rebuild and regenerate:

   ```bash
   python3 scripts/build_csv.py
   python3 scripts/render_readme.py --by impact --write
   ```

   Then re-run `python3 scripts/test_pipeline.py` and show me the verdict.

### Rules

- Never invent impact that the PR does not support. If you cannot tell what the
  change does from the PR, leave the row alone and tell me it needs a human.
- Never claim a performance win, user count, or adoption number that no source
  in the PR supports. Those are the easiest thing to fabricate and the easiest
  for a reader to catch.
- Keep `pr_title`, `pr_url`, and `created` untouched. You are only rewriting
  `impact`.
- If the same weak phrasing appears across several rows (your own
  `Enhanced Python 3.13 Compatibility` on both Dynamo rows, for example), rewrite
  each one against its own diff rather than reusing one sentence.
- If a rewrite would make the impact longer than the title it sits next to, that
  is a signal the change was small. Say so instead of padding.

---

## Output of a completed run

A refreshed `contributions.csv`, an updated marked block in `README.md`, and a
short note listing which rows changed and which were left alone.
