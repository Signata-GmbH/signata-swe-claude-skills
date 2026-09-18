---
name: code-fix
description: >-
  Analyse a reported defect in an existing module and produce a root-cause
  analysis plus a minimal, traceable fix — from test-bench evidence (debugger
  dumps, CAN/LIN traces, DTCs, a failing SWE.4/5/6 case, scope measurements), a
  pointer to the suspect code or requirement, or a code-dev/code-review
  follow-up. Adapts automatically to the repo's project.type (AUTOSAR /
  non-AUTOSAR) and obeys the same guard-rails as code-dev. Two-phase workflow
  with a hard gate: evidence + root-cause analysis first, code only after
  acknowledgement. May conclude the code is correct (requirement, config,
  upstream, or bench defect) and propose no change. Analysis by inspection only
  — never claims a reproduction, build, or test result. Use when asked to debug,
  fix, or root-cause an issue, bug, defect, or failing test in a module.
argument-hint: [module] [issue-id]
---

# Code Fix

Root-cause a reported defect in an existing module and produce a **minimal**
fix, from engineer-supplied evidence. Same discipline as `/code-dev`; the input
is a symptom, not a requirement set. The module is the first argument, the
issue/ticket ID the optional second; if the module is omitted, ask for it.
**Two phases with a hard gate between them — no code in Phase 1.**

Runs standalone (workflow-discipline §0): the module need not have been produced
by `/code-dev`, and no prior skill run is assumed.

## Step 1 — Intake: issue identity & evidence

**Parse first, ask second.** Most invocations already carry the bug report, the
bench notes, or a trace path in the same message. Extract what is there before
asking anything — never make the engineer re-type what they just supplied.

Fill five slots — **observed** · **expected** · **expectation source** ·
**build identity** · **artifacts** (defect-analysis §1–2) — and echo them back
as an intake table: `slot | value | where it came from | have / missing / weak`.
Quote the engineer's own words for observed and expected. A stated cause ("I
think it's the debounce") is recorded as a **candidate hypothesis** row — never
as the expectation, and never as the conclusion (defect-analysis §4).

Ask for the holes in **one consolidated turn**: `AskUserQuestion` for the
categorical parts (which evidence kinds can be supplied; new issue vs an
existing `code_fix.issues` entry), free text or a path for content. **Ask at
most twice** — if the Step 4 gate is still unmet after that, stop with the exact
list (defect-analysis §2) instead of negotiating.

Evidence is taken **by reference**: an absolute path to a file (trace/log
export, `.blf`/`.asc`, `.csv`, an xlsx test report, a screenshot), a pasted
block, or a tracker ID. Record path + digest in the ledger; never transcribe a
value into the report as though you measured it here.

**Issue ID** (defect-analysis §1): the second argument if given — which
**resumes** that entry from `code_fix.issues` rather than opening a second issue
for the same defect — else the tracker ID, else `<MODULE_UPPER>-FIX-NNN`. Two
unrelated symptoms → two issues; ask which to take first. Do not start analysing
until the issue is named — it keys the report, the ledger, and every re-run.

**Invoked as a `/code-dev` or `/code-review` follow-up in the same session:**
reuse the analysis already in context (interfaces, requirement table, pinned
revision) instead of re-acquiring it — but run the evidence gate and every hard
stop below unchanged. A fix that skips the gate because the module is familiar
is exactly the failure mode the gate exists for.

## Step 2 — Resolve project config

Read `20_AI/ai_project.yaml`. If **absent**, follow
[../_shared/common/project-config.md](../_shared/common/project-config.md) §7
(missing-config path) — the config is one-per-repo and belongs on the base
branch: **stop** if it already exists on the base branch or is in flight
elsewhere (merge it, never duplicate it), otherwise route to `/project-init` or
bootstrap inline when already on the base branch. Note `project.type`.

## Step 3 — Load the discipline

Always load
[../_shared/common/defect-analysis.md](../_shared/common/defect-analysis.md),
[../_shared/common/workflow-discipline.md](../_shared/common/workflow-discipline.md)
and [../_shared/common/no-fabrication.md](../_shared/common/no-fabrication.md).

Then, by `project.type`:
- **autosar** → [../_shared/autosar/project-context.md](../_shared/autosar/project-context.md)
  + [../_shared/autosar/requirements-filter.md](../_shared/autosar/requirements-filter.md)
  + [../_shared/autosar/forbidden-constructs.md](../_shared/autosar/forbidden-constructs.md)
- **nonautosar** → [../_shared/generic/project-context.md](../_shared/generic/project-context.md)
  + [../_shared/generic/requirements-scope.md](../_shared/generic/requirements-scope.md)
  + [../_shared/generic/forbidden-constructs.md](../_shared/generic/forbidden-constructs.md)

## Step 4 — Manifest, evidence gate & scope (HARD GATE)

Scaffold/validate `20_AI/manifests/<MODULE>.yaml` (workflow-discipline §3) and
open/append the issue's entry under `code_fix.issues`. Run the **pre-flight**
input check (§1) for the code-fix column, and pin the revision (§2) —
**reconciling the working tree against the build the evidence came from**
(defect-analysis §2); list the module's changes between the two if they differ.

**Requirement scope is symptom-driven, not module-wide.** Do not pull the whole
filtered set: identify the requirements the symptom touches (flavor's
filter/scope) and confirm that list. Confirm the target files.

**Existence guard.** No implementation at `layout.app_root/<MODULE>/` → this is
not a fix; stop and route to `/code-dev`.

Apply the **evidence gate** (defect-analysis §2): observed-vs-expected **+** at
least one artifact or a statically traceable reproduction condition **+** the
build identity. Any missing → name exactly what is needed and **stop**. Present
the evidence table with each artifact's limits.

**Stop for confirmation.**

## Step 5 — Phase 1: root-cause analysis (NO code)

1. **Anchor the expectation** (defect-analysis §3) — quote the requirement(s)
   the symptom belongs to; note where none covers the behaviour.
2. **Trace backwards by inspection** — observed effect → writing statement →
   guard → each conjunct's source → caller → input decode, citing `file:line`
   at every hop.
3. **Candidate table** (§4) — **at least two**, one outside the area the
   engineer pointed at; each with mechanism, confirming evidence, killing
   evidence, and the verdict from the evidence in hand.
4. **Reproduce-by-inspection statement** — does the pinned source explain the
   evidence? If not, say so; do not invent a mechanism.
5. **Verdict** (§5) — **V1** code defect · **V2** requirement defect/ambiguity ·
   **V3** not this module (upstream / calibration / build-config / integration /
   bench or test-case defect) · **V4** not localisable.
6. **Numbered questions** → `20_AI/<MODULE>_Phase1_Questions_CodeFix.xlsx` (§5).
7. **Present** the anchored expectation, the trace, the candidate table, the
   verdict, and the questions, and **STOP. Write no `.c`/`.h`/`.mak`.**
   - **V1** → proceed to Step 6 on acknowledgement.
   - **V2** → present the proposed requirement change and the code change it
     *would* imply; write nothing without an explicit engineer decision.
   - **V3** → report the evidence chain and the owning area; propose no change
     here.
   - **V4** → list the surviving candidates and, for each, the specific named
     artifact that would decide it. Stop.

   For V2/V3/V4 the report (Step 7) is still the deliverable. If the engineer
   directs a change anyway, proceed on their authority and record that
   direction, with its author, in the report and Deferred Items.

## Step 6 — Phase 2: minimal fix (after acknowledgement)

8. **Propose the change first** — the line-by-line table
   `file:line | before → after | which part of the cause it addresses` — and
   **discover before define** (workflow-discipline §4); wait for confirmation.
   If the honest fix is structural, say so and scope it separately rather than
   slipping a redesign into a bug fix.
9. **Apply the minimal diff** (defect-analysis §6): no drive-by changes, no
   renames, every fidelity rule preserved, no symptom suppression, traceability
   comments on every changed or added branch plus the issue-ID reference.
10. **Blast radius** (§7) — callers, shared state, re-derived Gate Table for
    changed guards, other requirements on the changed lines, variant impact, the
    existing unit-test cases the fix invalidates (from
    `unit_test.last_run.requirements` when present), and any timing
    consideration (never a measured number).
11. **Self-review** against the flavor's forbidden-constructs + coding rules for
    the changed lines; record deviations with justification. State
    **"syntactic review only — proposed fix, unverified"** (no build, no static
    analysis, no test execution, no reproduction).

## Step 7 — Report, verification plan & follow-ups

Write `20_AI/CodeFix/<MODULE>_<ISSUE_ID>_FixReport.md` with the full section set
of defect-analysis §9, and print in chat: the verdict, the change table, the
blast radius, and the **verification plan** the engineer executes
(defect-analysis §8) — reproduce · expected observable in the same medium as the
original evidence · negative check · unit-test cases to add and to update ·
follow-up runs (`/code-review` in diff mode on the change, `/unit-test` for the
case updates, a requirement change request for a V2). Never write "fixed",
"resolved", or "verified", and state any residual unexplained observation.

## Step 8 — Ledger & history

Update the issue's entry in `code_fix.issues` (verdict, root cause with
`file:line`, files changed, report path, follow-ups, status) and overwrite
`code_fix.last_run` (issue ID, source SHA, evidence digest, deferrals). Append
the run record to `20_AI/manifests/history/<MODULE>.jsonl`
(workflow-discipline §9). A re-run on the same issue ID **updates that entry in
place** — never open a duplicate.
