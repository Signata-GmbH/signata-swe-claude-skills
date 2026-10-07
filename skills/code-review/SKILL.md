---
name: code-review
description: >-
  Perform a formal SWE.3 software code review of a module's user-implemented C,
  producing a populated Findings List. Adapts automatically to the repo's
  project.type (AUTOSAR: MISRA rule-numbers in scope, AUTOSAR-isms expected,
  Critical severity; non-AUTOSAR: MISRA out of scope, no AUTOSAR-isms, four
  severities). Review by inspection only — never claims a build/analysis result.
  Use when asked to review, do a code review of, or find findings in a module.
argument-hint: [module]
---

# Code Review

Review a module's user-implemented `.c`/`.h` (and `_cfg.h` / `_Man` split if
present) and produce a populated **Findings List**. The module is the argument;
if omitted, ask for it. In diff mode, restrict findings to changed lines + their
direct consequences.

## Step 0 — Start the run (tracked, committed)

As soon as the module is known — before reading the config — load
[../_shared/common/run-tracking.md](../_shared/common/run-tracking.md) and start the run (§1): resolve any open run first (§5), take the
start time from the shell clock, write the active-run marker, append
`run_start`. From here on **every HARD GATE and STOP below is a gate**: append
`gate_reached` and make the **gate commit** (§3) before you stop, and append
`gate_ack` when the engineer answers. Timestamps come from `date -u`, never
from memory.

## Step 1 — Resolve project config

Read `20_AI/ai_project.yaml`. If **absent**, follow
[../_shared/common/project-config.md](../_shared/common/project-config.md) §7
(missing-config path) — the config is one-per-repo and belongs on the base
branch: **stop** if it already exists on the base branch or is in flight
elsewhere (merge it, never duplicate it), otherwise route to `/project-init` or
bootstrap inline when already on the base branch. Note `project.type`.

## Step 2 — Load the discipline

Always load
[../_shared/common/review-quality.md](../_shared/common/review-quality.md),
[../_shared/common/workflow-discipline.md](../_shared/common/workflow-discipline.md),
[../_shared/common/run-tracking.md](../_shared/common/run-tracking.md),
[../_shared/common/no-fabrication.md](../_shared/common/no-fabrication.md).

Then, by `project.type`:
- **autosar** → [../_shared/autosar/review-flavor.md](../_shared/autosar/review-flavor.md)
  + [../_shared/autosar/project-context.md](../_shared/autosar/project-context.md)
  + [../_shared/autosar/requirements-filter.md](../_shared/autosar/requirements-filter.md)
  + [../_shared/autosar/forbidden-constructs.md](../_shared/autosar/forbidden-constructs.md)
- **nonautosar** → [../_shared/generic/review-flavor.md](../_shared/generic/review-flavor.md)
  + [../_shared/generic/project-context.md](../_shared/generic/project-context.md)
  + [../_shared/generic/requirements-scope.md](../_shared/generic/requirements-scope.md)
  + [../_shared/generic/forbidden-constructs.md](../_shared/generic/forbidden-constructs.md)

## Step 3 — Manifest + scope confirmation (HARD GATE)

Scaffold/validate `20_AI/manifests/<MODULE>.yaml` (workflow-discipline §3).
Confirm the review target files, review mode (full/diff), and the in-scope
requirements (flavor's filter/scope). **AUTOSAR only:** run the Phase-0
domain-model derivation gate (autosar/review-flavor). Remember §0 — the module
may **not** have been produced by code-gen; review whatever code is present, and
treat absent code-gen artifacts as findings, not blockers. Run the
previous-output checks (run-tracking §7) on the living findings list — say
whether this is a first review, a re-review, or a migration from dated copies,
and how many open findings it carries forward; on a first run with a Statistics
sheet, include the statistics cell mapping for confirmation. **Stop for
acknowledgement** (gate commit).

## Step 4 — Pre-flight read

Pin the revision (workflow-discipline §2). Read the target files + the upstream
caller; identify the active `APP_HAS_*` build flags; identify the HAL/LIN/RTE APIs
the module relies on.

## Step 5 — Walk every review dimension

Apply [review-quality.md](../_shared/common/review-quality.md) (finding quality,
false-negative prevention, three-way traceability) **and** the flavor's stance
(MISRA in/out, severity set, AUTOSAR-ism stance). **Walk every C-relevant
checkpoint** of the checklist workbook (`docs.checklist`) — Pass/Fail/N/A/Question
— and emit a checklist-coverage summary. Verify each finding's line number with a
search tool and quote the code.

## Step 6 — Update the living Findings List & report

Update the module's **one** findings workbook,
`20_AI/CodeReview/<MODULE>_CodeReview_Findings.xlsx`, in place — created from a
copy of the checklist template on the first run, never the template itself.
Match every finding to the register by fingerprint and apply the re-run merge
rules, update the Statistics sheet and append the Run History row
(review-quality "Output mechanics"); columns per the flavor. Never write the
author's columns. Print the full table in chat grouped by AI re-check status,
with counts by severity and new / still present / not reproduced / not
re-checked, the list of in-scope requirements with no traceable implementation,
and the inspection-only disclaimer.

## Step 7 — Ledger, history & final commit

Overwrite `code_review.last_run` (output path + hash, mode, counts, checklist
coverage, `run_id`, `started`, `ended`, `timing`), update the finding register
and `finding_seq`, append `run_end` to `20_AI/manifests/history/<MODULE>.jsonl`
(workflow-discipline §9), then make the **final commit** and delete the
active-run marker (run-tracking §2–§4).
