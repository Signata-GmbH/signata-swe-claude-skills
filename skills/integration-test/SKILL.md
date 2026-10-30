---
name: integration-test
description: >-
  Generate draft software integration test cases (ASPICE SWE.5) for one
  module's interfaces — each case names both ends, the module and the peer at
  the other end of the port — as a 3-sheet Excel workbook (Test Cases /
  Traceability / Open Points) an engineer reviews and enters into DOORS by
  hand. Test basis is the Functional_Architecture DOORS export, including its
  UserDefinedTypes chapter — never the SW requirements export, which is SWE.6's.
  Runs in the SWE.3 project repository like the code skills, with its own
  test-spec config (20_AI/ai_test_project.yaml) beside ai_project.yaml, and
  designs every case from the architecture alone — the DOORS export, the ARXML
  and the RTE headers generated from it — naming breakpoints by RTE symbol and
  module; it never reads the module's source code. Covers the module's
  interfaces to other application modules (RTE data flow, client/server,
  watchdog, runnable timing) and its hand-off to the basic software
  (coherent transmission, transmission trigger, start-up and mode switch,
  reception timeout, E2E protection — observed on the bus). v1 is Excel-only
  (no .vtt / vTestStudio automation-script generation) and RTE-debugger-based
  (AUTOSAR only) — it stops rather than inventing a black-box pattern for a
  module with no RTE symbols. Author by inspection only — never
  claims a DOORS write or a test execution. Use when asked to generate, draft,
  or update SWE.5 integration test cases for a module.
argument-hint: [module]
---

# Integration-Test Generation (SWE.5)

Generate (or update in place) draft integration test cases for one module.
**The module is the argument** (e.g. `/integration-test FUSA_ParkLckCtrl`); if
omitted, **ask for it first** — before reading the config or any export — and
never take it from the folder instead (an existing manifest, a previous run, a
file name). Any of the module's four spellings is accepted and resolved in
Step 3 (integration-test-patterns §4.1); a feature name is recognised as one and
refused as a module.

An integration test case exercises **one interface across two modules**: one
writes it (`Rte_Write`), the other reads it (`Rte_Read`). So every case names
the **peer module** at the other end of the target's port — the RTE call it
breaks on, in the peer module. By default the peer gets no section of its own:
`peer_depth` and mirroring decide that, explicitly (integration-test-patterns
§2–§3).

The test basis is the **Functional_Architecture** export — one DOORS module,
whose section 1.2 is the **UserDefinedTypes** chapter that resolves its data
types. The SW requirements export is SWE.6's basis and is not read here.
Breakpoints are named by **module and RTE symbol** (`Rte_Write_P_<port>_<element>`
in `<WriterSwc>`), taken from the ARXML and the RTE headers generated from it —
never by a line quoted from a `.c` file. The source code is within reach in
this repository and **must not be read**: SWE.5's test basis is the
architectural design, and a case built from the implementation would test the
code against itself (integration-test-patterns §9).

**Run it from the SWE.3 project repository**, like `code-dev`, `code-review` and
`unit-test` — never from a vTestStudio project folder, which is usually outside
Git (project-config §1).

Follow these steps in order. Detailed rules live in the linked shared files —
load them as you reach each step (progressive disclosure).

## Step 0 — Start the run (tracked, committed)

As soon as the module is known — before reading the config — load
[../_shared/common/run-tracking.md](../_shared/common/run-tracking.md) and start the run (§1): resolve any open run first (§5), take the
start time from the shell clock, write the active-run marker, append
`run_start`. From here on **every HARD GATE and STOP below is a gate**: append
`gate_reached` and make the **gate commit** (§3) before you stop, and append
`gate_ack` when the engineer answers. Timestamps come from `date -u`, never
from memory.

## Step 1 — Resolve the test-spec project config

Read `20_AI/ai_test_project.yaml`, and `20_AI/ai_project.yaml` beside it: the
test-spec config takes `project.type` and `layout.rte_inc` from there rather
than holding copies (project-config §4.3). Not in a Git
repository → stop, and say to run from the SWE.3 repository (project-config §1).
If the test-spec config is **absent**, follow
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

Per workflow-discipline §3, in this order:

1. **Resolve the module argument** against all four axes
   (integration-test-patterns §4.1). The manifest is keyed by the resolved
   `aFunctionModule`; a resolved value whose scope holds zero ports is a stop.
2. **Read the manifest** `20_AI/manifests/integration-test/<MODULE>.yaml`
   (scaffold from
   [../_shared/testspec/integration-test-manifest-template.yaml](../_shared/testspec/integration-test-manifest-template.yaml)
   if absent) and compute the derivable values.
3. **Settle `integration_test.authoring_mode` before any discovery**
   (integration-test-patterns §0.1) — ask it if the config lacks it.
4. **Discover only the inputs whose config entry is unset**
   (workflow-discipline §1.2): existing test cases for this module only under
   `extend_existing`, never under `from_scratch`; the ARXML — the module's
   software-component description and the composition it sits in
   (`docs.arxml`) — and the RTE headers (`docs.rte_type_headers`, or
   `layout.rte_inc`) if their entry is unset. A discovered file is a proposal,
   never registered on its own, and a recorded `N/A` is never re-opened. Offer
   the test environment description and the communication database if they
   are not configured (workflow-discipline §1.1) — the database decodes the
   bus for the basic-software patterns (integration-test-patterns §7, P-10). **Never open a `.c` file, the OS configuration
   or a build output** — a question that seems to need one is a Phase-1
   question or an Open Point (integration-test-patterns §9).
5. **Pin the architecture artefacts** (workflow-discipline §2) — a content
   hash of the export, of every ARXML file and of every RTE header read; a
   missing ARXML is a mandatory-input stop.
6. **Run the export-completeness gate** (workflow-discipline §1.3) — the run
   needs each object's **name** *and* its **text**: two columns, one column
   carrying both (split on the first newline), or two views of the module
   joined on `ID`. Text missing is a stop — but first check what the ARXML
   already resolves, and offer the names-only downgrade as the
   AI proposal for the engineer to accept or refuse.
7. **Apply the AUTOSAR-only guard** (integration-test-patterns §0) — if the
   module shows no RTE symbols to work from, stop here and say so.
8. **Confirm the resolved inputs**, then **stop and wait** for confirmation.

Remember workflow-discipline §0 — this may be the first skill ever run against
this module in this project.

## Step 4 — Phase 1 — Analysis → phase gate (STOP)

Per integration-test-patterns §1–§6 and workflow-discipline §1/§2/§4:
1. **Pre-flight input acquisition** (workflow-discipline §1, incl. the §1.3
   completeness gate) and **pin the baseline** — `release.id`/`variants` + a
   content hash of every supplied export, ARXML file and RTE header (§2).
   Every symbol and value is valid only at that baseline.
   On a re-run, read QA's validity verdicts in the previous output here
   (workflow-discipline §8): cases marked `Yes` are kept, every `Reason for
   Invalid` the inputs cannot answer becomes a Phase-1 question, and every
   `Question` gets a written reply for QA before its case is reworked.
2. **Resolve the peers** (integration-test-patterns §2) — direction per port
   from its text, then the writer→reader pairing confirmed by the ARXML
   connector; reuse the cached `integration_test.peer_modules` if present,
   otherwise discover, confirm and offer to cache. Ports whose far end is the
   **basic software** (mapped to a system signal, a mode-switch or service
   port) are listed separately with their message, I-PDU and database
   attributes (§5.1, P-10). Present the **peer matrix**, with the fan-out and
   projected cases per target port. Ambiguous pairings become numbered
   questions, never a pick.
3. **Depth and mirroring** (integration-test-patterns §2 Depth, §3) — use the
   configured `peer_depth` / `peer_module_mirroring` (manifest overrides
   first); if either is unset, ask, stating the projected row count for each
   option. When the scope is narrowed, say that excluded peers still appear in
   the cases as the far end.
4. **Scope** — apply the filter (integration-test-patterns §1.2): the objects
   authored from, and separately the objects only read for grounding. Report
   attrition at each step.
5. **Resolve the module-name mapping** (integration-test-patterns §4) for the
   target and every peer that gets a section — reuse the cached mapping if
   present; otherwise discover it (`extend_existing`) or propose it
   (`from_scratch`), and offer to cache it.
6. **Interface inventory**, **value derivation from the `1.2` UserDefinedTypes
   chapter**, and **coverage/gap** (integration-test-patterns §5) — state per
   interface which range the Min/Mid/Max came from, and where each enum literal
   came from (the chapter names enum types but lists no literals).
7. **Pattern per object** from its `aTestCriteria` (integration-test-patterns
   §6) — including the objects that map to P-08 and get no case. For P-05,
   report each runnable's ARXML symbol and timing/init event next to the
   architecture's period, flagging any mismatch (§7). For each
   basic-software-facing port, the P-10 shapes that apply (coherent
   transmission, trigger, start-up/mode switch, reception timeout, E2E) with
   the ARXML entry and database attribute behind each, and the ones that do
   not apply with the reason.
8. **Proposed test cases** — one line each, no steps yet, marking primary vs
   mirror.
9. **Row-count gate** (workflow-discipline §5) — the number of rows that table
   produces, heading rows included, as the last question.
Present the scope, the peer matrix, the mapping/interface analysis, the
proposed-cases table, and numbered questions (written to
`20_AI/IntegrationTest/<MODULE>/<MODULE>_Phase1_Questions_IntegrationTest.xlsx`, workflow-discipline §5).
**STOP.**

## Step 5 — Phase 2 — Generation

Only after acknowledgement. First **re-hash every input** (workflow-discipline
§2) — anything changed since
pre-flight is a stop, not a mixed baseline. Apply the patterns (P-01…P-10) and attributes from
[integration-test-patterns.md](../_shared/testspec/integration-test-patterns.md)
§7–§8, and — only where mirroring is on — mirror each interface into its
peer's section per §3. Every symbol, struct member, enum literal and boundary
value traced to a supplied input, and every breakpoint named by RTE or
runnable symbol and module from the ARXML and the RTE headers
(workflow-discipline §4, integration-test-patterns §9); an unresolved one goes
to Open Points, never a guess.
For a re-run, read QA's validity verdicts first and leave accepted cases
untouched — a `Question` case is reworked only after QA has accepted the
reply — then run the three checks of workflow-discipline §8 — previous
output gone or edited since, scope changed (→ regeneration, not a delta),
layout-only (→ re-render, no analysis) — then apply the in-place diff: new →
add, changed → update the mapped case in place, removed → flag.

## Step 6 — Self-check & output

Run the checklist in workflow-discipline §6; fix failures or list them as Open
Points. Write the 3-sheet workbook per
[output-format.md](../_shared/testspec/output-format.md) (Object Heading before
Object Text for this skill), with the `Yes,No,Question` drop-down on
`isValid`, to
`20_AI/IntegrationTest/<MODULE>_SWE5_TestCases.xlsx`. Print the workbook
summary in chat plus the no-fabrication disclaimer.

## Step 7 — Ledger, history & final commit

Overwrite `last_run` in the manifest (workflow-discipline §8) — including
`run_id`, `started`, `ended`, `timing`, the
scope, the output path + hash, and the inputs supplied but
not read — through a comment-preserving YAML writer, append `run_end` to
`20_AI/manifests/integration-test/history/<MODULE>.jsonl`, then make the
**final commit** — the workbook, manifest and history — and delete the
active-run marker (run-tracking §2–§4).
