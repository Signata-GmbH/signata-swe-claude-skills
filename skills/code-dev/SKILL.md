---
name: code-dev
description: >-
  Implement an application module (or a feature in an existing module) from a
  filtered set of software requirements, following the project's conventions.
  Adapts automatically to the repo's project.type (AUTOSAR: RTE/runnables/MemMap;
  non-AUTOSAR: _cfg.h IF-macros/scheduler). Two-phase workflow with a hard gate:
  analysis + questions first, code only after acknowledgement. Syntactic review
  only — never claims a build/static-analysis/test result. Use when asked to
  implement, develop, or scaffold a module or feature from requirements.
argument-hint: [module]
---

# Code Development

Implement a module (or a feature inside one) from its requirements, plus an
Implementation Review document. The module is the argument; if omitted, ask for
it. **Two phases with a hard gate between them — no code in Phase 1.**

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
[../_shared/common/workflow-discipline.md](../_shared/common/workflow-discipline.md),
[../_shared/common/run-tracking.md](../_shared/common/run-tracking.md)
and [../_shared/common/no-fabrication.md](../_shared/common/no-fabrication.md).

Then, by `project.type`:
- **autosar** → [../_shared/autosar/project-context.md](../_shared/autosar/project-context.md)
  + [../_shared/autosar/requirements-filter.md](../_shared/autosar/requirements-filter.md)
  + [../_shared/autosar/forbidden-constructs.md](../_shared/autosar/forbidden-constructs.md)
- **nonautosar** → [../_shared/generic/project-context.md](../_shared/generic/project-context.md)
  + [../_shared/generic/requirements-scope.md](../_shared/generic/requirements-scope.md)
  + [../_shared/generic/forbidden-constructs.md](../_shared/generic/forbidden-constructs.md)

## Step 3 — Manifest, task-mode guard & scope (HARD GATE)

Scaffold/validate `20_AI/manifests/<MODULE>.yaml` (workflow-discipline §3); confirm
scope (`related_modules` + `expected_row_count` for AUTOSAR, `sw_req_ids` for
non-AUTOSAR), peer anchors, and seed deferrals/questions.

**Task-mode guard — never overwrite validated code silently.** Detect whether an
implementation already exists at `layout.app_root/<MODULE>/`, then decide
`task_mode` by that **and the requirement scope**:
- **No existing implementation** → `task_mode: new-module`.
- **Existing implementation + ALL requirements in scope** → this is a from-scratch
  regenerate of a validated module. **WARN that it would overwrite existing
  reviewed/tested code and ASK** whether to (a) develop from scratch
  (`regenerate` — destructive; the git original is preserved for diff) or (b) treat
  it as an update. **Do not default to overwrite.**
- **Existing implementation + a specific / subset requirement scope** → treat as a
  **follow-up / change / update** (`task_mode: feature-or-update`): modify only what
  the new or updated requirements demand; never regenerate the whole module.

Record the confirmed `task_mode`. **Stop for confirmation** (gate commit).

## Step 4 — Phase 1: understand & align (NO code)

Pin the revision (§2). Run the **pre-flight** input check (§1). Then:
1. **Read the stub/interface** — runnables + cycle times (AUTOSAR) or the module
   shape + `_cfg.h` boundary (non-AUTOSAR); list every I/O path.
2. **Read requirements** (flavor's filter/scope); numbered table
   `ID | intent | target function | signals/APIs`.
3. **Cross-check coverage** — every interface ↔ a requirement; log every mismatch.
4. **Action × Precondition × Source-signal map** (§6/§7) — one row per action, with
   gates in order, source→mapping→wire encoding, and literal failure behaviour.
5. **Numbered questions** → `20_AI/<MODULE>_Phase1_Questions_CodeDev.xlsx` (§5).
6. **Present** the requirement table, coverage cross-check, action map, and
   question list, and **STOP** (gate commit — the questions workbook is in it).
   **Write no `.c`/`.h`/`.mak` until every question is answered.** If answers
   change scope, return to item 1.

## Step 5 — Phase 2: implement (after acknowledgement)

7. **Propose** macros/types/helpers (and, new module, the exact integration diff);
   **discover before define** (§4); wait for confirmation (gate commit). Add
   every file you will create or change to the marker's `owned_paths` now, and
   check none of them carries uncommitted engineer changes (run-tracking §3.3).
8. **Generate** the header(s), source, build files, and the Implementation Review
   document. Output the requirement-coverage table (`req → file:line`), the
   **interface diff** — AUTOSAR: RTE-call diff; non-AUTOSAR: `_cfg.h` IF-macro diff
   — 1:1 with the stub/interface, and every ambiguity-assumption (also a Deferred
   Items row).
9. **Self-review** against the flavor's forbidden-constructs + coding rules; record
   deviations with justification. State **"syntactic review only"** (no build /
   static analysis / test execution).
10. **Code commit** (run-tracking §3.2) — the generated headers, sources and
    build files in `owned_paths`, alone, as `AI(code-dev): <MODULE> — generated
    code`. The Implementation Review document goes with the final commit.

## Step 6 — Ledger, history & final commit

Overwrite `code_dev.last_run` (source SHA, requirements snapshot, files created,
Implementation Review path, deferrals, `run_id`, `started`, `ended`, `timing`),
append `run_end` to `20_AI/manifests/history/<MODULE>.jsonl`
(workflow-discipline §9), then make the **final commit** and delete the
active-run marker (run-tracking §2–§4). Report both commit SHAs.
