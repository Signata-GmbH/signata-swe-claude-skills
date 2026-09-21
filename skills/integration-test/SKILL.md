---
name: integration-test
description: >-
  Generate draft software integration test cases (ASPICE SWE.5) for one module
  and the peer modules its interfaces run to, as a 3-sheet Excel workbook (Test
  Cases / Traceability / Open Points) an engineer reviews and enters into DOORS
  by hand. Test basis is the Functional_Architecture DOORS export, including its
  UserDefinedTypes chapter — never the SW requirements export, which is SWE.6's.
  Runs against a vTestStudio project folder's own per-repo config
  (20_AI/ai_test_project.yaml), not the SWE.3 code repo's ai_project.yaml. v1 is
  Excel-only (no .vtt / vTestStudio automation-script generation) and
  RTE-debugger-based (AUTOSAR only) — it stops rather than inventing a black-box
  pattern for a module with no RTE symbols. Author by inspection only — never
  claims a DOORS write or a test execution. Use when asked to generate, draft,
  or update SWE.5 integration test cases for a module.
argument-hint: [module]
---

# Integration-Test Generation (SWE.5)

Generate (or update in place) draft integration test cases for one module. The
module is the argument — an `aFunctionModule` value (e.g.
`/integration-test FUSA_ParkLckCtrl`); if omitted, ask for it.

An integration test case exercises **one interface across two modules**: one
writes it (`Rte_Write`), the other reads it (`Rte_Read`). So naming a module
also brings in the **peer modules** at the other end of its ports — their
objects come into scope, and each interface is authored under both modules'
sections (integration-test-patterns §2–§3).

The test basis is the **Functional_Architecture** export — one DOORS module,
whose section 1.2 is the **UserDefinedTypes** chapter that resolves its data
types. The SW requirements export is SWE.6's basis and is not read here.

Follow these steps in order. Detailed rules live in the linked shared files —
load them as you reach each step (progressive disclosure).

## Step 1 — Resolve the test-spec project config

Read `20_AI/ai_test_project.yaml`. This is a **separate** config from
`20_AI/ai_project.yaml` — this skill runs in the vTestStudio project folder, not
the SWE.3 C-source repo, and has no compiler/target/RTE-layout facts to read.
If **absent**, follow
[../_shared/testspec/project-config.md](../_shared/testspec/project-config.md)
§7 (missing-config path): **stop** if it already exists on the base branch or
is in flight elsewhere (merge it, never duplicate it); otherwise bootstrap it
inline only when already on the base branch, per §3's guard.

## Step 2 — Load the discipline

Always load:
[../_shared/testspec/workflow-discipline.md](../_shared/testspec/workflow-discipline.md),
[../_shared/testspec/no-fabrication.md](../_shared/testspec/no-fabrication.md),
[../_shared/testspec/output-format.md](../_shared/testspec/output-format.md),
[../_shared/testspec/integration-test-patterns.md](../_shared/testspec/integration-test-patterns.md).

## Step 3 — Manifest: scaffold → validate → confirm (HARD GATE)

Per workflow-discipline §3: compute derivable values, read
`20_AI/manifests/integration-test/<MODULE>.yaml` (scaffold from
[../_shared/testspec/integration-test-manifest-template.yaml](../_shared/testspec/integration-test-manifest-template.yaml)
if absent), discover the per-module input docs (existing test cases for this
module **and its peers**; RTE headers if needed), and **confirm the resolved
inputs**. Run the **export-completeness gate** (workflow-discipline §1.3) — the
run needs each object's **name** *and* its **text**, which a
single-content-column DOORS view cannot both carry; one export with both
columns, or two views of the module joined on `ID`. Missing either is a stop,
not an Open Point. Apply the **AUTOSAR-only guard** (integration-test-patterns §0) before
going further — if the module shows no RTE symbols to work from, stop here and
say so. **Stop and wait** for confirmation. Remember workflow-discipline §0 — this may be the
first skill ever run against this module in this project.

## Step 4 — Phase 1 — Analysis → phase gate (STOP)

Per integration-test-patterns §1–§6 and workflow-discipline §1/§2/§4:
1. **Pre-flight input acquisition** (workflow-discipline §1, incl. the §1.3
   completeness gate) and **pin the baseline** — `release.id`/`variants` + a
   content hash of every supplied export (§2). Every symbol/value is valid only
   at that baseline.
2. **Resolve the peers** (integration-test-patterns §2) — direction per port
   from its text, then the writer→reader pairing; reuse the cached
   `integration_test.peer_modules` if present, otherwise discover, confirm and
   offer to cache. Present the **peer matrix**. Ambiguous pairings become
   numbered questions, never a pick.
3. **Scope** — apply the filter over the target **and** its peers, report
   attrition at each step.
4. **Resolve the module-name mapping** (integration-test-patterns §4) for the
   target and every peer — reuse the cached mapping if present; otherwise
   discover it, cross-check the `aFeature` mix, and offer to cache it.
5. **Interface inventory**, **value derivation from the `1.2` UserDefinedTypes
   chapter**, and **coverage/gap** (integration-test-patterns §5) — state per
   interface which range the Min/Mid/Max came from, and where each enum literal
   came from (the chapter names enum types but lists no literals).
6. **Pattern per object** from its `aTestCriteria` (integration-test-patterns
   §6) — including the objects that map to P-08 and get no case.
7. **Proposed test cases** — one line each, no steps yet, marking primary vs
   mirror.
Present the scope, the peer matrix, the mapping/interface analysis, the
proposed-cases table, and numbered questions (written to
`20_AI/<MODULE>_Phase1_Questions_IntegrationTest.xlsx`, workflow-discipline §5).
**STOP.**

## Step 5 — Phase 2 — Generation

Only after acknowledgement. Apply the patterns (P-01…P-09) and attributes from
[integration-test-patterns.md](../_shared/testspec/integration-test-patterns.md)
§7–§8, and mirror each interface into its peer's section per §3. Every symbol,
struct member, enum literal and boundary value traced to a supplied input
(workflow-discipline §4); an unresolved one goes to Open Points, never a guess.
For a re-run, apply the in-place diff (workflow-discipline §8): new → add,
changed → update the mapped case in place, removed → flag.

## Step 6 — Self-check & output

Run the checklist in workflow-discipline §6; fix failures or list them as Open
Points. Write the 3-sheet workbook per
[output-format.md](../_shared/testspec/output-format.md) (Object Heading before
Object Text for this skill) to
`20_AI/IntegrationTest/<MODULE>_SWE5_TestCases.xlsx`. Print the workbook
summary in chat plus the no-fabrication disclaimer.

## Step 7 — Ledger & history

Overwrite `last_run` in the manifest (workflow-discipline §8) and **append**
one record to
`20_AI/manifests/integration-test/history/<MODULE>.jsonl`.
