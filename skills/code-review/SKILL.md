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

## Step 1 — Resolve project config

Read `20_AI/ai_project.yaml` (scaffold + confirm from
[../_shared/ai_project.template.yaml](../_shared/ai_project.template.yaml) if
absent). Note `project.type`.

## Step 2 — Load the discipline

Always load
[../_shared/common/review-quality.md](../_shared/common/review-quality.md),
[../_shared/common/workflow-discipline.md](../_shared/common/workflow-discipline.md),
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
treat absent code-gen artifacts as findings, not blockers. **Stop for
acknowledgement.**

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

## Step 6 — Populate the Findings List & report

Write findings into a **new copy** of the checklist workbook's `Findings List`
sheet under `20_AI/CodeReview/` (never overwrite the template); columns per the
flavor. Print the full table in chat with counts by severity, the list of
in-scope requirements with no traceable implementation, and the inspection-only
disclaimer.

## Step 7 — Ledger & history

Overwrite `code_review.last_run` (findings file path, counts, checklist coverage)
and **append** the run record to `20_AI/manifests/history/<MODULE>.jsonl`
(workflow-discipline §9).
