# Common code-review quality (both flavors)

> Loaded by the code-review skill regardless of `project.type`. The flavor packs
> ([../autosar/review-flavor.md](../autosar/review-flavor.md) /
> [../generic/review-flavor.md](../generic/review-flavor.md)) layer the
> MISRA-scope stance, AUTOSAR-ism stance, severity **set**, and output **columns**
> on top of this. Also obey [workflow-discipline.md](workflow-discipline.md)
> (esp. §0 standalone, §2 revision pinning, §5 Phase-1 gate).

## Finding quality

- **One issue per row.** No bundling unrelated issues.
- **Concrete, real location** — `<file>:<line(s)>`, **verified with a search/grep
  tool**, never estimated from memory. Quote the exact 2–5 lines so the line can
  be independently checked. If a line truly cannot be confirmed, mark it
  `~NNN (unverified)` and say why.
- **Description states three things:** (a) what is wrong, (b) what to rework,
  (c) the rule/requirement reference (guideline §, checklist #, or `SW_Req(u)-NNN`).
  Specific enough that the author can act without asking.
- **No vague findings** ("improve readability"). **No duplicates** — one finding,
  note "also at lines a, b, c".
- **Consolidate floods** — one finding for "all 9 function headers are
  placeholders", not nine.

## False-negative prevention (verify before flagging)

- **Return values:** flag as discarded only if truly unstored **and** unused.
  `(void)Rte_Write_*` / `(void)`-cast on a known-safe call is intentional — don't
  flag without a specific error-handling requirement.
- **Initialization:** not a defect if the variable lives in a `CLEARED`/zero-init
  section or is initialised by BSW/RTE before use.
- **Types:** confirm the actual typedefs before claiming a mismatch.
- **"Unused":** search all references in the file before flagging.

## Severity (definitions come from the flavor pack — do not invent)

- Apply the project's exact severity definitions; the flavor pack supplies the set
  (AUTOSAR adds `Critical`; generic uses Major/Minor/Trivial/Question).
- **Do not inflate.** A lead reviewer's list is trusted because each top-severity
  item genuinely is one. Use **Question** when you lack the knowledge/rationale to
  classify — that is what it is for.
- **Documentation-only** issues (missing/placeholder headers, comments) →
  Minor/Trivial, never top severity.
- Distinguish a genuine deviation from an **established project-wide pattern** — if
  the whole codebase already does it, say so in the finding so the engineer can
  accept it as a known deviation.

## Checklist walk (MANDATORY)

- Walk **every** C-relevant checkpoint of the project review-checklist workbook
  (`docs.checklist`, sheet as named per flavor). For each: **Pass** / **Fail**
  (→ finding, quote the checkpoint) / **N/A** (justify) / **Question** (missing
  input). Skip model-based (Matlab/Simulink/TargetLink) rows where the code is
  hand-written C.
- Emit a **checklist-coverage summary**: walked / pass / fail / N/A / question
  counts, with the row indices marked N/A and why.
- **Never silently skip the checklist** — skipping it is itself a `Question`
  finding ("checklist not walked — review incomplete").

## Requirement traceability (all three directions)

- **Forward:** every in-scope requirement implemented? Map `ID → function/line`;
  raise a finding where coverage can't be confirmed.
- **Reverse (phantom check):** every `/* SW_Req(u)-NNN */` comment maps to a
  **real** in-scope ID — flag phantoms.
- **Test-criteria coverage:** each populated `aTestCriteria` is **observable** in
  the code at/near the traceability comment.

## Output mechanics — one living findings list

There is **one** findings workbook per module, at a fixed path with no date in
its name:

`20_AI/CodeReview/<MODULE>_CodeReview_Findings.xlsx`

The first run creates it from a copy of the checklist template (`docs.checklist`)
— **never overwrite the template itself**. Every later run, full or diff,
**updates that same file in place**, and every run commits it
([run-tracking.md](run-tracking.md) §3), so each earlier state of the review is a
commit, found with `git log --grep "AI-Key: <MODULE>" -- <path>`. Column layout
of A–J comes from the flavor pack; preserve every other sheet.

### Columns added after the flavor's columns

| Col | Header | Written by | Content |
|---|---|---|---|
| K | `Finding ID` | AI, once | `CR-NNN`, from `code_review.finding_seq`; never renumbered, never reused |
| L | `First Found (Run)` | AI, once | `run_id` that raised it |
| M | `Last Seen (Run)` | AI, every run that re-checked it | `run_id` |
| N | `AI Re-check` | AI, every run | `Present` · `Not reproduced — confirm closure` · `Not re-checked (diff run)` · `Present — author status says closed` |

Column A (`#`) keeps the finding's number (`NNN` of its ID) — it is **not** a
row counter, so rows are never renumbered when findings are added.

### Finding identity across runs

Line numbers move, so they cannot identify a finding. Each finding has a
**fingerprint**, stored in `code_review.findings` in the manifest:

`<tag class> | <file> | <enclosing function> | <normalised quoted code>`

— tag class without its counter (`MISRA-17.7`, `MEMMAP`, `FUNC-LOGIC`),
normalised code = the quoted line(s) with whitespace collapsed. On a re-run,
match each new finding to the register: same fingerprint → same finding. A
fingerprint that differs only in the quoted code (the line was edited but the
defect is still there) is a match only when you can say why in one line; list
every such fuzzy match at the gate for the engineer to confirm.

### Re-run merge rules

Before touching the file, run run-tracking.md §7: an edited hash is **expected**
here (authors fill G–I) — read it back and merge; uncommitted author edits are
committed with the first gate commit, before the AI changes anything.

| Finding on this run | What happens to its row |
|---|---|
| matched, still present | Keep the row. Update **D** (location) if the line moved and say so in chat; keep **B** (original review date), **E**/**F** unless the finding itself changed (then revise E and note it). M = this run, N = `Present`. If the author's status (H) says closed/done, N = `Present — author status says closed` and list it in chat. |
| matched, gone from the code | **Never delete the row.** N = `Not reproduced — confirm closure`; M unchanged. The author/finder decides closure in H/I. |
| outside a diff-mode run's scope | Untouched except N = `Not re-checked (diff run)`. Never mark it not reproduced. |
| new | Append a row with the next ID; B = today; L = M = this run; N = `Present`. |

**Never write the author's or finder's columns** (`Author's statement`, `Status
of rework`, `Finder's Comment on Rework` — G, H, I) — carry them forward
byte-for-byte. A finding the author disputed in G is still reported if present;
quote their statement in chat.

### Statistics sheet

If the workbook has a statistics sheet (`Statistics`, or the template's
equivalent), it must agree with the Findings List after every run:
- **First time:** locate the count cells (by type / severity, by rework status,
  totals) and present the mapping `statistic → cell` at the first gate for
  confirmation; store it in `code_review.statistics_map`. Never guess a cell.
- **Cells with formulas** → keep the formulas and make sure their ranges cover
  every findings row (extend a range that stops short); set the workbook to
  recalculate on open (`wb.calculation.fullCalcOnLoad = True`) — openpyxl does
  not evaluate formulas.
- **Static values** → rewrite them from the Findings List counts.
- No statistics sheet → none is created; the Run History sheet carries the
  counts.

### Run History sheet

Create a `Run History` sheet on the first run and append one row per run, never
editing earlier rows:

`Run ID | Started (UTC) | Ended (UTC) | Mode (full/diff) | Source SHA | New |
Still present | Not reproduced | Not re-checked | Total open (status not closed) |
Checklist walked/pass/fail/na/question`

### Migration from dated copies

Earlier versions of this skill saved `<MODULE>_CodeReview_Findings_<YYYY-MM-DD>.xlsx`
per day. On the first run under this rule, if the living file is absent and
dated copies exist: take the newest (the one `last_run.findings_file` names, else
the latest date) as the baseline, `git mv` it to the living name (copy + `git
add` if it was never committed), give its rows IDs in their existing order,
carry G–I forward, and say so at the first gate. Leave the other dated copies
untouched and list them.

### Report & ledger

- Print the full findings table in chat (with the suggested-fix column, if the
  flavor has one) **grouped by N**, and the counts new / still present / not
  reproduced / not re-checked.
- Record `output: {path, hash}`, `mode`, `counts` and checklist coverage in
  `code_review.last_run`, the finding register and `finding_seq` in
  `code_review`, and close the run per workflow-discipline §9 and
  run-tracking.md §2–§3.
