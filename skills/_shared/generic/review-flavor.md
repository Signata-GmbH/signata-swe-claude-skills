# non-AUTOSAR code-review flavor

> Loaded by the code-review skill when `project.type: nonautosar`. Layers the
> non-AUTOSAR stance on top of [../common/review-quality.md](../common/review-quality.md)
> (finding quality, false-negative prevention, checklist walk, traceability,
> output mechanics) — which still fully applies. This file states only what is
> **different**.

## Standards in scope — MISRA is OUT, no AUTOSAR-isms

- **Do NOT raise MISRA-C:2012 rule-number findings.** MISRA conformance is owned
  by the static-analysis tools (QAC / Polyspace) and is out of scope. If an issue
  also happens to be a coding-guideline rule (braces, no `goto`), raise it **as the
  guideline rule** (`Guideline §x.y`), never as a MISRA rule number.
- **No AUTOSAR-isms in recommendations.** Do not expect or recommend `Rte_`,
  `Dem_`, `NvM_`, `Std_ReturnType`, ECU-configurator XML, or BSW/MCAL-layering
  vocabulary — the project is intentionally non-AUTOSAR.
- **Ignore Matlab / Simulink / TargetLink / Stateflow checklist rows** — this is
  hand-written C.
- Judge against three rubrics: the **SIGNATA Coding Guideline** (`docs.coding_guideline`
  — cite §), the **SWE.3 Code Review Checklist** sheet (cite `Checklist #n`), and
  the **HIS metric ranges** (§8).

## Severity — four levels (NO `Critical`)

Use `Major / Minor / Trivial / Question`, per the project checklist's `Guideline`
sheet definitions:
- **Major** — review must be repeated after correction (feature misunderstood or
  missing; wrong logic; requirement violated; unsafe default; uninitialised use;
  missing NULL check that can crash; HW access above the HAL).
- **Minor** — correctable without repeating the review (missing value, local
  guideline deviation, naming slip, missing brace, magic number).
- **Trivial** — cosmetic. **Question** — genuinely unsure / missing rationale.

Do not inflate. Use `Question` rather than forcing a Major/Minor when you lack the
design rationale. Forbidden constructs (see
[forbidden-constructs.md](forbidden-constructs.md)) are raised as **guideline
violations**, not as a separate `Critical` tier.

## Read-only, advisory fixes

Produce findings only — never edit source. Provide a concrete **`AI Suggested Fix`**
per finding (advisory guidance for the author, not a code change). For a `Question`,
state what information/decision is needed instead of a code change.

## Output columns (Findings List sheet)

Fill **A–F** and **J**; leave **G, H, I** blank (author's rework cycle):

`A #` · `B Review Date (today, YYYY-MM-DD)` · `C Reviewer (AI Reviewer)` ·
`D Location of Finding (<file>:<line(s)>, + SW_Req-NNNN / SwDD ch. where relevant)` ·
`E Description (what's wrong + what to rework + Guideline §/Checklist #/SW_Req ref)` ·
`F Type (Major/Minor/Trivial/Question)` · `J AI Suggested Fix`.

Add the `AI Suggested Fix` header in `J1` if absent. Save a **new copy** under
`20_AI/CodeReview/` as `<Module>_CodeReview_Findings_<YYYY-MM-DD>.xlsx` — never
overwrite the template; preserve the other sheets (an openpyxl data-validation
drop warning is acceptable). Checklist sheet name: `SWE.3 Code Review Checklist`.
Otherwise follow common/review-quality output mechanics.
