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

## Output mechanics

- Populate the checklist workbook's **`Findings List`** sheet via `openpyxl` and
  **save a new copy** under `20_AI/CodeReview/` — **never overwrite the template**.
  Column layout comes from the flavor pack. Preserve the other sheets.
- Also print the full findings table (with any suggested-fix column) in chat.
- Record the saved file path + finding counts in `code_review.last_run` and append
  the run record to the history JSONL (per workflow-discipline §9).
