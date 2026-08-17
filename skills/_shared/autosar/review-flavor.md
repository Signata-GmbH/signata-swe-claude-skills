# AUTOSAR code-review flavor

> Loaded by the code-review skill when `project.type: autosar`. Layers the
> AUTOSAR-specific stance on top of [../common/review-quality.md](../common/review-quality.md)
> (finding quality, false-negative prevention, checklist walk, traceability,
> output mechanics) — which still fully applies. This file only states what is
> **different** on AUTOSAR projects.

## Standards in scope — MISRA is IN, AUTOSAR-isms are EXPECTED

- **Raise MISRA-C:2012 rule-number findings.** Cite the rule (e.g. `MISRA-17.7`,
  `MISRA-10.3`, `Dir-2.4`). Common ones: Rule 17.7 (unchecked safety-relevant
  return — but honour the `(void)Rte_Write_*` exception in common/review-quality),
  Rule 10.x (raw int → enum), Dir 2.4/2.5 (dead code / unused entities).
- **AUTOSAR vocabulary is expected**, not a smell: `Rte_Read_*/Write_*/Call_*`,
  `Dem_*`, `NvM_*`, `Std_ReturnType`, MemMap sections, runnables. Recommend AUTOSAR
  idioms where appropriate.
- Review target is the **user-implemented** `.c`/`.h` under `<layout.app_root>/<MODULE>/`,
  **not** the Agnosar-generated stub under `<layout.app_root>/Common/`. Generated
  files are exempt from header/structure/naming findings — note and skip.

## Severity — five levels (adds `Critical`)

Use `Critical / Major / Minor / Trivial / Question`.

- **Critical** — directly impacts safety, causes incorrect functional behaviour,
  or undefined runtime behaviour; blocks release. Examples: wrong signal compared
  in a safety path; buffer overflow; race affecting actuator control; a state
  machine that can deadlock; **any forbidden construct present**.
- **Major** — significant rework + re-review: missing requirement implementation;
  phantom traceability ID; logic error in a non-safety path; missing MemMap
  section pairing/type.
- **Minor / Trivial / Question** — as in common/review-quality; documentation-only
  issues are Minor/Trivial, never Critical.

Fixed severity rules: any forbidden construct listed in
[forbidden-constructs.md](forbidden-constructs.md) → **always Critical**; MemMap section-type mismatch / missing pair / inline-init on
`NO_INIT`/`CLEARED` → **Major**; cyclomatic complexity over
`code_review.complexity_threshold` → Major, else Minor.

## Memory-mapping completeness (AUTOSAR-specific check)

For every module-level variable:
1. **Section pairing** — enclosed in a matching `START_SEC_*` / `STOP_SEC_*`
   include pair (correct `*_MemMap.h`), each `START_SEC` with exactly one
   `STOP_SEC` in order.
2. **Section-type correctness** — zero-init → `*_CLEARED_UNSPECIFIED`; init-on-every-reset
   → `*_INIT_UNSPECIFIED`; retain-across-warm-reset → `*_NO_INIT`.
3. **Calibration/tunables** in `NO_INIT`/`CLEARED` must be initialised in the
   module `Init` runnable — inline initialisers there are silently dropped. Do
   **not** flag inline initialisers on `INIT_UNSPECIFIED` variables (those are valid).

Note: `APPL_*` data sections with `Appl_MemMap.h` are the project convention — do
**not** flag them as a prefix mismatch.

## Phase 0 — domain-model derivation gate (AUTOSAR-only)

The four domain fields in `code_review.domain_model` drive the substance of the
review. For each field set to `AUTO`:
1. **Derive** a draft — `rte_io_signatures` by grepping `Rte_*` calls;
   `upstream_producers` per `Rte_Read_*` (cross-check the Architecture Diagram);
   `signal_keyword_equivalents` from I/O + code + requirement terms;
   `domain_functional_checks` from the filtered requirements + SDD + safety manual.
2. **Present** it as a *"Phase 0 — Derived Domain Model (for confirmation)"* block,
   each item marked with its source and any low-confidence flag.
3. **Gate** — STOP and wait for confirmation (interactive); or if non-interactive,
   proceed but label every item `[DERIVED — unconfirmed]` and raise one `Question`
   finding. **Once confirmed, write the model back into `code_review.domain_model`**
   so later reviews of this module reuse it.

Fields the engineer filled in explicitly are authoritative — do not re-derive.

## Finding ID tags

`FUNC-SAFETY` · `FUNC-LOGIC` · `FUNC-REQ` · `MISRA-<RuleID>` · `FORBIDDEN` ·
`MEMMAP` · `DOC-HEADER` · `NAMING` · `FORMAT` · `DEAD-CODE` · `TYPE-CONV` ·
`INTERRUPT` · `INIT` · `COMPLEXITY` — each finding's description starts with a
unique tag (e.g. `MISRA-17.7-001`, `MEMMAP-003`). This list is **not exhaustive**:
when none fits, coin a clear `UPPER-KEBAB` tag (e.g. `DESIGN`, `TRACE`) and use it
consistently.

## Output (Findings List sheet)

Columns: `# | Review Date | Reviewer | Location of Finding | Description of Finding |
Type of Finding | Author's statement (blank) | Status of rework (Open) |
Finder's Comment on Rework (blank)`. Checklist sheet name:
`SWE.3 Code Review Checklist`. Save a **new copy** under `20_AI/CodeReview/` as
`<Module>_CodeReview_Findings_<YYYY-MM-DD>.xlsx` — never overwrite the template.
Otherwise follow common/review-quality output mechanics.
