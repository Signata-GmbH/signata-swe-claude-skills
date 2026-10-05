---
name: qualification-test
description: >-
  Generate draft software qualification test cases (ASPICE SWE.6) for one
  feature, as a 3-sheet Excel workbook (Test Cases / Traceability / Open
  Points) an engineer reviews and enters into DOORS by hand. Runs in the SWE.3
  project repository like the code skills, with its own test-spec config
  (20_AI/ai_test_project.yaml) beside ai_project.yaml — but tests black-box and
  never reads the source code. v1 is Excel-only (no .vtt /
  vTestStudio automation-script generation). Handles requirements-based,
  boundary-value, and diagnostic (UDS DID/RID) test cases. Author by
  inspection only — never claims a DOORS write or a test execution. Use when
  asked to generate, draft, or update SWE.6 qualification test cases for a
  feature.
argument-hint: [feature]
---

# Qualification-Test Generation (SWE.6)

Generate (or update in place) draft qualification test cases for one feature.
**The feature is the argument** — an `aFeature` value (e.g.
`/qualification-test "Actuator Data"`); if omitted, **ask for it first** —
before reading the config or any export — and never take it from the folder
instead (an existing manifest, a previous run, a file name). Check it against
`qualification_test.valid_features` once the config is loaded; a module name
(an `aFunctionModule` value) is recognised as one and refused as a feature.

**Run it from the SWE.3 project repository**, like the code skills — never from
a vTestStudio project folder, which is usually outside Git (project-config §1).
The code is within reach there, and **must not be read**: qualification testing
is black-box, and an expected result taken from the code would test the code
against itself (qualification-test-patterns §0).

Follow these steps in order. Detailed rules live in the linked shared files —
load them as you reach each step (progressive disclosure).

## Step 1 — Resolve the test-spec project config

Read `20_AI/ai_test_project.yaml`, and `20_AI/ai_project.yaml` beside it: with
`docs.requirements_workbook: ai_project`, the SW requirements export is the one
`ai_project.yaml` names — one copy, shared with the code skills
(project-config §4.3). Not in a Git repository → stop, and say to run from the
SWE.3 repository (project-config §1). If the test-spec config is **absent**,
follow
[../_shared/testspec/project-config.md](../_shared/testspec/project-config.md)
§7 (missing-config path): **stop** if it already exists on the base branch or
is in flight elsewhere (merge it, never duplicate it); otherwise bootstrap it
inline only when already on the base branch, per §3's guard.

## Step 2 — Load the discipline

Always load:
[../_shared/testspec/workflow-discipline.md](../_shared/testspec/workflow-discipline.md),
[../_shared/testspec/no-fabrication.md](../_shared/testspec/no-fabrication.md),
[../_shared/testspec/output-format.md](../_shared/testspec/output-format.md),
[../_shared/testspec/qualification-test-patterns.md](../_shared/testspec/qualification-test-patterns.md).

## Step 3 — Manifest: scaffold → validate → confirm (HARD GATE)

Per workflow-discipline §3: compute `FEATURE_SLUG`, read
`20_AI/manifests/qualification-test/<FEATURE_SLUG>.yaml` (scaffold from
[../_shared/testspec/qualification-test-manifest-template.yaml](../_shared/testspec/qualification-test-manifest-template.yaml)
if absent), discover the per-feature input docs whose config entry is unset
(existing test cases for this feature; workflow-discipline §1.2), offer the
communication database, the Test Plan and the test environment description if
they are not configured (workflow-discipline §1.1), and **confirm the resolved
inputs** — including whether the target is a diagnostic feature (routes to §9
of the patterns file). **Stop and wait**
for confirmation. Remember workflow-discipline §0 — this may be the first
skill ever run against this feature in this project.

## Step 4 — Phase 1 — Analysis → phase gate (STOP)

Per qualification-test-patterns §1–§3 and workflow-discipline §1/§2/§4:
1. **Pre-flight input acquisition** (workflow-discipline §1) and **pin the
   baseline** — `release.id`/`variants` + a content hash of every supplied
   export (§2).
2. **Scope** — apply the filter, report attrition at each step; confirm the
   feature name against `qualification_test.valid_features`. Report each
   in-scope requirement's verification criterion (`aTestCriteria`,
   qualification-test-patterns §1.1): followed, ruling the level out, or empty.
3. **Existing coverage** split (covered / not covered / partially covered).
4. **Vocabulary resolution** — every signal/variable/parameter/state/error
   name, with its source; bus signals with their encoding, cycle time and
   timeout from the communication database (qualification-test-patterns §3) —
   never from the source code.
5. **Proposed test cases** — one line each, no steps yet.
6. **Row-count gate** (workflow-discipline §5) — the number of rows that table
   produces, heading and logical-parent rows included, as the last question.
Present all of the above and numbered questions (written to
`20_AI/<FEATURE_SLUG>_Phase1_Questions_QualificationTest.xlsx`,
workflow-discipline §5). **STOP.**

## Step 5 — Phase 2 — Generation

Only after acknowledgement. First **re-hash every input** (workflow-discipline
§2) — anything changed since pre-flight is a stop, not a mixed baseline. Apply
the structure, title convention, boundary-
value rule, and (for diagnostic features) the DID/RID templates from
[qualification-test-patterns.md](../_shared/testspec/qualification-test-patterns.md)
§4–§9. Every symbol/value traced to a supplied input (workflow-discipline §4);
an unresolved one goes to Open Points, never a guess. For a re-run, run the
three checks of workflow-discipline §8 first — previous output gone or edited
since, scope changed (→ regeneration, not a delta), layout-only (→ re-render,
no analysis) — then apply the in-place diff: new → add, changed → update the
mapped case in place, removed → flag.

## Step 6 — Self-check & output

Run the checklist in workflow-discipline §6; fix failures or list them as Open
Points. Write the 3-sheet workbook per
[output-format.md](../_shared/testspec/output-format.md) (Object Text before
Object Heading for this skill) to
`20_AI/QualificationTest/<FEATURE_SLUG>_SWE6_TestCases.xlsx`. Print the
workbook summary in chat plus the no-fabrication disclaimer.

## Step 7 — Ledger & history

Overwrite `last_run` in the manifest (workflow-discipline §8) — including the
scope, the output path + hash, and the inputs supplied but not read — through a
comment-preserving YAML writer, and **append** one record to
`20_AI/manifests/qualification-test/history/<FEATURE_SLUG>.jsonl`.
