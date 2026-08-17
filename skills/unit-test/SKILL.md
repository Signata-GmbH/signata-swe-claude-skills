---
name: unit-test
description: >-
  Generate or update a VectorCAST unit-test (.tst) suite for a target module from
  its requirements and code. Adapts automatically to the repo's project.type
  (AUTOSAR or non-AUTOSAR). Authors by inspection only — never builds, runs, or
  reports coverage it did not measure. Use when asked to create, extend,
  regenerate, or update the unit tests / .tst suite for a module.
argument-hint: [module]
---

# Unit-Test Generation

Author (or update in place) a VectorCAST `.tst` suite for a module. The module is
the argument (e.g. `/unit-test CDD_MotDrv`); if omitted, ask for it.

Follow these steps in order. Detailed rules live in the linked shared files — load
them as you reach each step (progressive disclosure).

## Step 1 — Resolve project config

Read `20_AI/ai_project.yaml`. If it is **absent**, scaffold it from
[../_shared/ai_project.template.yaml](../_shared/ai_project.template.yaml),
pre-filling derivable fields and asking for the rest (compiler, target, type),
then confirm before continuing. Note `project.type` — it selects the flavor below.

## Step 2 — Load the discipline

Always load:
[../_shared/common/workflow-discipline.md](../_shared/common/workflow-discipline.md),
[../_shared/common/unittest-design.md](../_shared/common/unittest-design.md),
[../_shared/common/vectorcast-syntax.md](../_shared/common/vectorcast-syntax.md),
[../_shared/common/no-fabrication.md](../_shared/common/no-fabrication.md).

Then, by `project.type`:
- **autosar** → [../_shared/autosar/project-context.md](../_shared/autosar/project-context.md)
  + [../_shared/autosar/requirements-filter.md](../_shared/autosar/requirements-filter.md)
- **nonautosar** → [../_shared/generic/project-context.md](../_shared/generic/project-context.md)
  + [../_shared/generic/requirements-scope.md](../_shared/generic/requirements-scope.md)

## Step 3 — Manifest: scaffold → validate → confirm (HARD GATE)

Per workflow-discipline §3: compute derivable values (`module.upper`,
`unit_test.env`, layout paths from config), read
`20_AI/manifests/<MODULE>.yaml` (scaffold from
[../_shared/manifest-template.yaml](../_shared/manifest-template.yaml) if absent),
discover the input docs, and **confirm the resolved inputs** (popup for the
categorical choices: subprograms scope, requirement filter / `sw_req_ids`).
**Stop and wait** for confirmation. Remember §0 — this skill may be the first to
run for the module; never assume code-gen ran.

## Step 4 — Analysis phase → phase gate (STOP)

Per workflow-discipline §2/§4/§6:
1. **Pin the revision** (SHA + blob hashes) — every symbol/value is valid only at it.
2. **Requirements** — the in-scope set (via the flavor's filter/scope file); capture
   each ID, statement, procedure, Expected Result.
3. **Signals & ranges** — resolve each to its accessor/scaling/range/enum set.
4. **Subprograms** — enumerate every function in `<MODULE>.c` (incl. statics);
   diff against the requested scope and raise the delta; record observable outputs.
5. **Stub boundary** — derive mechanically (flavor-specific stub naming); note
   existing vs new stubs.
6. **Gate Table (§6)** and **duplication table** — one row per asserted effect;
   drop duplicates of the existing suite.
Present scope, analysis summary, Gate Table, duplication table, and the numbered
questions (write them to `20_AI/<MODULE>_Phase1_Questions_UnitTest.xlsx`, §5).
**STOP.**

## Step 5 — Author the `.tst`

Only after acknowledgement. Follow the **test-design rules** in
[unittest-design.md](../_shared/common/unittest-design.md) and the grammar in
[vectorcast-syntax.md](../_shared/common/vectorcast-syntax.md): requirement-driven
cases first (assert a real effect), then close structural coverage to the target
in `coverage.unit_test`; compound tests for stateful logic; every case carries a
true `TEST.NOTES` block. Write to the env path under `layout.vcast_env`. For a
re-run, apply the in-place diff (workflow-discipline §9): new→add, changed→update
the mapped case in place, removed→flag.

## Step 6 — Deliverables

Per the **deliverables list** in
[unittest-design.md](../_shared/common/unittest-design.md): a traceability table
(`req → case → subprogram`, incl. uncovered + why), a coverage-closure report
(every subprogram listed), and a notes/assumptions list including the
**symbol-grounding self-check** (unittest-design.md) and any code findings.
**No build/run/coverage claims.**

## Step 7 — Ledger & history

Overwrite `unit_test.last_run` in the manifest (working state) and **append** one
record to `20_AI/manifests/history/<MODULE>.jsonl` (workflow-discipline §9): ts,
workflow, skill_version, source SHA + blob hashes, requirements SHA, delta.
