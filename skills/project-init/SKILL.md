---
name: project-init
description: >-
  Create (or validate) the per-repository AI project config 20_AI/ai_project.yaml
  — once per repo, on the repo's base branch, so every engineer and every module
  shares one config instead of conflicting copies. Detects AUTOSAR vs
  non-AUTOSAR, discovers layout roots and input documents, asks only for what it
  cannot derive (compiler, target, ASIL, variants), and refuses to create a
  second config if one already exists on the base branch or is in flight on
  another branch. Use when setting up a repo for the AI skills, or when asked to
  create, initialise, check, or repair ai_project.yaml.
argument-hint: "[--validate]"
---

# Project Init — per-repo AI config

Create the **one-per-repository** project config `20_AI/ai_project.yaml` that
`/code-dev`, `/code-review`, and `/unit-test` all read. Run this **once per repo,
on the repo's base branch**, and commit the result — every engineer and every
module then inherits the same project facts.

**This skill writes exactly one file.** It never creates per-module manifests,
never touches source, and never runs a toolchain.

`--validate` (or an existing config) → validation/repair mode only.

## Step 1 — Load the procedure

Load [../_shared/common/project-config.md](../_shared/common/project-config.md)
— the authoritative bootstrap procedure — and
[../_shared/common/no-fabrication.md](../_shared/common/no-fabrication.md). The
no-fabrication rule applies to config: a layout root or document path that is not
confirmed to exist is **asked for**, never invented.

## Step 2 — Repo & base branch

Per project-config §1: resolve the repo toplevel, **derive** the base branch
(`origin/HEAD` → else `develop`/`main`/`master` → else ask), and record the
current branch + worktree cleanliness. Report what you concluded.

## Step 3 — Duplicate-config check (HARD GATE)

Per project-config §2: `git fetch`, then check **local**, **`origin/<base>`**, and
**all fetched branches** (`git log --all -- 20_AI/ai_project.yaml`).

- Already on `origin/<base>` → **STOP.** Say to pull/merge and re-run; do not
  author a competing file.
- In flight on another branch → **STOP.** Name the branch + commit; it should be
  merged, not duplicated.
- Present locally → go to **Step 6** (validate / repair).
- Nowhere → continue.

## Step 4 — Base-branch guard (HARD GATE)

Per project-config §3. On the base branch with a clean worktree → proceed.
Otherwise **stop and ask**: switch to `<base>` (clean worktree only, plain
`git switch`), create it here anyway (with the merge-it-promptly warning), or
abort. Never switch, stash, or discard on your own.

## Step 5 — Resolve every field

Per project-config §4, scaffolding from
[../_shared/ai_project.template.yaml](../_shared/ai_project.template.yaml):

1. **Detect `project.type`** — search for both the AUTOSAR and the non-AUTOSAR
   signatures, **show the evidence**, and confirm. Ambiguous → ask.
2. **Discover** layout roots, the requirements workbook, and the project-wide
   documents; write only paths that exist; `N/A` the other flavor's fields.
   Several candidates → pick-one popup. `docs.architecture` is *offered
   explicitly* (ask-tier), never self-waived.
3. **Ask** for the non-derivable: `toolchain.compiler`, `toolchain.target`,
   `safety.default_asil`, and (AUTOSAR) `requirements.variants` — quoting an
   embedded-newline variant exactly.
4. **Confirm** the type-implied defaults: `requirements.scoping`,
   `coverage.unit_test`.

**No `<PLACEHOLDER>` may survive** — every field ends as a confirmed value or
`N/A` + a one-line reason.

## Step 6 — Validate / repair mode (existing config)

Per project-config §5: never overwrite. Emit the validation table
(`field | value | valid? | evidence / problem`) — schema version, surviving
placeholders, `project.type` vs what the repo actually looks like (a mismatch is
a loud finding), every `layout.*` path exists, every document path is readable.
Offer to repair **only** the invalid fields, leaving valid ones byte-identical.
All valid → say so and stop.

## Step 7 — Confirm → write → hand off (HARD GATE)

Per project-config §6:

1. Present the **complete resolved YAML** plus a provenance table
   (`derived from <path>` / `answered by engineer` / `N/A — reason`). **STOP for
   approval.**
2. On approval write `20_AI/ai_project.yaml` — and nothing else.
3. **Ask** whether to commit + push to `<base>`. Never commit or push without an
   explicit yes; if declined, print the exact commands.
4. Hand off: config is repo-wide and one-time; next run `/code-dev`,
   `/code-review`, or `/unit-test` on a module to scaffold that module's manifest.

## Step 8 — Run summary

Report: base branch (and how derived), branch the config was written on, the
duplicate-config check results, `project.type` + the evidence for it, fields
derived vs asked vs `N/A`, whether it was committed/pushed, and any follow-up the
engineer still owes (typically: get it merged to `<base>`). No ledger and no
history record — those are per-module, owned by the three module skills.
