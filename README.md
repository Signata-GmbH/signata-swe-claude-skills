# AUTOSAR / non-AUTOSAR AI Skills — Technical Documentation

A Claude Code **plugin** that turns SIGNATA's engineering AI prompts —
**Code Development**, **Defect Analysis & Fix**, **Code Review**,
**Unit-Test Generation**, and (for a vTestStudio project folder)
**Integration-Test** and **Qualification-Test
Generation** — into reusable **skills** developers invoke by name, instead of
copy-pasting a large prompt and hand-filling inputs every time. Two setup
skills, **Project Init** and (inline, per §3.10) the test-spec config bootstrap,
lay down the per-repo config each group reads.

> Status & roadmap live in [STATUS.md](STATUS.md). This file is the *why* and
> *how*: purpose, architecture, and the key decisions behind them.

---

## 1. Purpose & motivation

We had six hand-crafted prompts — the three use-cases above, each in an
**AUTOSAR** and a **non-AUTOSAR** variant. Used as-is, every run means:

- copying a 300–500 line prompt into the tool,
- hand-editing an "engineer fill block" (module, variants, paths, scope…),
- re-typing the same project facts and the same disciplines each time,
- no memory of prior runs, no audit trail, and three (really six) copies of the
  same shared rules drifting apart.

This project makes the prompts **first-class, versioned, invokable tooling**:

- `/code-dev`, `/code-fix`, `/code-review`, `/unit-test` — four commands, any repo.
- `/project-init` — one command, once per repo, to lay down the shared config.
- Project- and module-specific inputs come from small **config files** the skill
  scaffolds and confirms, not from copy-paste.
- One **shared discipline** maintained once, inherited everywhere.
- Every run is **recorded** (audit trail) and **re-runnable in place**.

---

## 2. Core concepts

| Term | Meaning |
|---|---|
| **Skill** | A packaged capability invoked as `/name`. Its `SKILL.md` is a workflow the model follows; supporting files load on demand (*progressive disclosure*). |
| **Flavor** | `autosar` or `nonautosar` — the project *type*. One flavor per repo. Selects which mechanics a skill loads. |
| **Project config** | `20_AI/ai_project.yaml` — **one per repo**, created once by `/project-init` **on the base branch** and committed. Holds everything that varies by project (type, compiler, target, layout roots, coverage, variants, docs). |
| **Manifest** | `20_AI/manifests/<MODULE>.yaml` — **one per module**. Inherits the project config; holds module-specific inputs + the skill-owned run ledgers. |
| **Ledger** | `last_run:` in the manifest — the latest run's state, used to compute in-place re-runs. Overwritten each run. |
| **Run history** | `20_AI/manifests/history/<MODULE>.jsonl` — append-only audit trail, one immutable record per run. |

---

## 3. Architecture

### 3.1 Directory layout

```
.claude/skills/
├── README.md                     # this file
├── STATUS.md                     # progress / pending work
├── _shared/                      # (leading _ = not itself a skill)
│   ├── ai_project.template.yaml  # per-repo config template
│   ├── manifest-template.yaml    # per-module manifest template
│   ├── common/                   # flavor-AGNOSTIC discipline (both flavors load these)
│   │   ├── project-config.md        #   per-repo config bootstrap: base-branch + duplicate guards
│   │   ├── workflow-discipline.md   #   gates, revision pinning, Gate Table, ledger/history
│   │   ├── defect-analysis.md       #   evidence taxonomy, hypotheses, verdicts, minimal diff
│   │   ├── review-quality.md        #   finding quality, checklist walk, traceability
│   │   ├── vectorcast-syntax.md     #   .tst grammar (shared verbatim)
│   │   └── no-fabrication.md        #   toolchain-honesty rule
│   ├── autosar/                  # AUTOSAR flavor pack
│   │   ├── project-context.md       #   RTE/MemMap/runnables; reads facts from config
│   │   ├── requirements-filter.md   #   workbook filter + variant-newline trap
│   │   ├── forbidden-constructs.md  #   no-float, MISRA-as-findings
│   │   └── review-flavor.md         #   MISRA-in, AUTOSAR-isms, Critical severity
│   └── generic/                  # non-AUTOSAR flavor pack
│       ├── project-context.md       #   LIN/LDF/_cfg.h IF-macros, scheduler
│       ├── requirements-scope.md    #   explicit SW_Req ID list (no reliable module column)
│       ├── forbidden-constructs.md  #   float-allowed-limited, guideline authoritative
│       └── review-flavor.md         #   MISRA-out, no AUTOSAR-isms, AI-Suggested-Fix column
├── project-init/     SKILL.md    # setup — per-repo config, once, on the base branch
├── code-dev/         SKILL.md    # orchestrator — two-phase hard gate
├── code-fix/         SKILL.md    # orchestrator — evidence → root cause → minimal diff
├── code-review/      SKILL.md    # orchestrator — findings + checklist walk
├── unit-test/        SKILL.md    # orchestrator — .tst authoring
├── integration-test/ SKILL.md    # orchestrator — SWE.5 DOORS test-case generation
└── qualification-test/ SKILL.md  # orchestrator — SWE.6 DOORS test-case generation
```

`integration-test` and `qualification-test` run in a **different repo** — a
vTestStudio project folder, not the SWE.3 C-source repo — so they read a
**separate** `_shared/testspec/` pack (own config template, own bootstrap
procedure, own discipline/no-fabrication/output-format files, own manifest
templates) instead of `common/`/`autosar/`/`generic/`. See §3.10.

### 3.2 Four *adaptive* module skills, not eight

We chose **skills that adapt to the project** over flavor-specific pairs.
Because `project.type` is fixed per repo, a skill reads it and loads the right
flavor automatically — the developer always types the same `/unit-test`
regardless of AUTOSAR vs non-AUTOSAR. Each `SKILL.md` is a thin **orchestrator**:

```
read 20_AI/ai_project.yaml  →  load _shared/common/*  +  _shared/<type>/*
   →  scaffold / validate / confirm the module manifest   (hard gate)
   →  run the flavored workflow
   →  write outputs + update the ledger + append run history
```

The ~60–70 % of each use-case that is shared discipline lives in `common/`;
only the genuinely divergent mechanics live in the flavor packs.

### 3.3 Two-level configuration

Nothing project-specific is hardcoded in a skill. It is resolved at run time:

```
20_AI/ai_project.yaml         (one per repo — project facts)
        ▲  inherits
        │
20_AI/manifests/<MODULE>.yaml (one per module — module inputs + ledgers)
```

This is what makes, e.g., the **compiler dynamic**: `toolchain.compiler` is a
field each repo sets (`GreenHills` / `TASKING` / `mlx16-gcc`) — the skills read
it, they never assume it. Same mechanism for target, layout roots, ASIL,
coverage type, and the requirement-scoping method.

### 3.4 Setup is one-time and repo-wide

The project config is **one file per repository** — so it is created **once, on the
base branch, by one engineer**, via `/project-init`, and committed. The procedure
lives in `_shared/common/project-config.md` and is shared by all four skills, so
there is a single code path with a single set of guards:

- **Duplicate guard** — before writing, check the working tree, `origin/<base>`,
  and *all* fetched branches (`git log --all -- 20_AI/ai_project.yaml`). Found
  anywhere → **stop**; the existing config gets merged, never duplicated.
- **Base-branch guard** — creating it on a feature branch is what produces two
  disagreeing configs and a merge conflict in the file every run depends on. Off
  the base branch the skill stops and offers to switch (never switching, stashing,
  or discarding on its own).
- **Never overwrite** — an existing config puts the skill in validate/repair mode:
  a `field | value | valid? | evidence` table, repair of only the invalid fields,
  valid fields left byte-identical.
- **No placeholder survives** — every field ends as a confirmed value or `N/A` plus
  a reason, and a layout root that does not exist on disk is asked for, not
  invented (no-fabrication applies to config too).
- The three module skills keep working standalone: a missing config routes through
  the same guards (`project-config.md` §7) — bootstrap inline when already on the
  base branch, otherwise point at `/project-init`.

`/project-init` writes **exactly one file**; per-module manifests stay with the
module skills.

### 3.5 How inputs are collected

Developers never copy-paste a fill block. On first run a skill:

1. **Derives** what it can (module upper-case, env name, all layout paths).
2. **Discovers** the input docs by globbing under `docs.root`.
3. **Scaffolds** the module manifest from the template (the per-repo
   `ai_project.yaml` is `/project-init`'s job — §3.4).
4. **Confirms** via an `AskUserQuestion` popup for the categorical choices; when
   discovery finds several candidate documents, that becomes a pick-one popup.
   Only the genuinely unknowable (the module name) is a typed argument.
5. **Validates** the manifest on every later run; malformed fields are flagged,
   not silently used.

This is a **hard gate** — the skill stops and waits for confirmation before
doing any work.

### 3.6 Re-runs are in-place

A re-run is a diff, not a rewrite. The skill recomputes each in-scope
requirement's hash and compares it to `last_run`:

- **new** → author + append,
- **changed** (hash differs) → **update the mapped artifact in place** (case /
  code / finding keeps its identity),
- **removed** → flag the orphan (never silently delete),
- **unchanged** → leave it.

The delta is shown and confirmed before anything is written.

### 3.7 Audit: ledger + history + revision pinning

Two records with different jobs:

- **`last_run:`** (manifest) — *working state*, overwritten each run, drives the
  in-place diff.
- **`history/<MODULE>.jsonl`** — *append-only audit trail*, one immutable record
  per run: timestamp, workflow, skill version, **source git SHA + blob hashes**,
  requirements SHA, and the delta.

**Revision pinning** ties every output to the exact code state it was authored
against — essential for ASIL-B traceability. Git provides a second,
corroborating trail.

### 3.8 No pipeline assumption

The four module workflows are **decoupled**. Any of them can be the first to run
for a module (review may run on code Code-Gen never produced; `/code-fix` runs on
a legacy module no skill ever touched). Each independently
scaffolds the manifest and populates **only its own** section; a shared
requirement-hash spine is used opportunistically but never required. `/project-init`
is *not* a pipeline stage either — the module skills fall back to the same guarded
bootstrap if it never ran.

### 3.9 `code-fix`: the symptom-driven counterpart of `code-dev`

`/code-fix` is the follow-up path — for a defect found at the test bench, a
failing SWE.4/5/6 case, or an issue in code `/code-dev` just produced. It reuses
`code-dev`'s entire guard-rail set (fail-closed inputs, hard Phase-1 gate,
revision pinning, grounding, fidelity rules, no-fabrication, ledger) and both
flavor packs. It is a **separate skill**, not a mode, because three things
invert:

- **The input is evidence, not a specification.** A Trace32 dump or a CANoe log
  establishes *what happened*, never *why*; "the bug is in `Foo_Calc()`" is the
  engineer's hypothesis, not a finding. `_shared/common/defect-analysis.md` §2
  is an evidence taxonomy — per artifact kind: what it proves, what it does
  **not** prove, what to ask for when it is missing — behind a fail-closed
  **evidence gate** (observed-vs-expected **+** one artifact or a statically
  traceable reproduction condition **+** the build identity). It also
  **reconciles the evidence's build against the working tree**, because an
  already-fixed defect and a never-existed defect look identical by inspection.
- **The correct answer may be "change nothing here."** Four verdicts (§5):
  **V1** code defect · **V2** requirement defect/ambiguity (the code conforms —
  no change without an explicit engineer decision) · **V3** upstream /
  calibration / build-config / integration / bench-harness defect · **V4** not
  localisable (name the artifact that would decide it, and stop). A
  development-shaped workflow has no such verdict, so it always emits a diff —
  which is how a symptom gets buried instead of fixed.
- **A fix is a minimal diff with a blast radius.** §6 is the mirror of
  code-dev's regenerate guard: every changed line justified by the root cause,
  drive-by cleanups demoted to findings, no renames, and no symptom suppression
  (widening a tolerance or deleting an assertion is a spec change → V2). §7
  then derives what the change can break — callers, shared state, re-derived
  Gate Table, other requirements on those lines, variants, and the existing
  unit-test cases the fix invalidates (read from `unit_test.last_run`, never
  written). §8 is a verification plan **the engineer executes**: nothing is
  reproduced, fixed, or verified in this environment.

The manifest gains a `code_fix:` section whose `issues:` list is keyed by issue
ID (tracker ID, else `<MODULE_UPPER>-FIX-NNN`), so a module accumulates an
auditable defect history and a re-run updates its issue in place.

### 3.10 A second, parallel config: the DOORS test-spec skills

`integration-test` (SWE.5) and `qualification-test` (SWE.6) generate draft
DOORS test-case rows (a 3-sheet Excel workbook an engineer reviews and enters
into DOORS by hand) from DOORS xlsx exports. Two things separate them from the
other four skills:

- **They run in a vTestStudio project folder**, not the SWE.3 C-source repo —
  no compiler, no RTE layout, no `.c`/`.h`. So they read their **own** per-repo
  config, `20_AI/ai_test_project.yaml`, bootstrapped by
  `_shared/testspec/project-config.md` (same base-branch + duplicate guards as
  `ai_project.yaml`, just for a different file and a different repo).
- **They have no source code to pin a git revision against.** The audit spine
  is `release.id` + `variants` (the DOORS baseline) plus a content hash of every
  supplied xlsx export — `_shared/testspec/workflow-discipline.md` §2 is the
  test-spec equivalent of `common/workflow-discipline.md` §2.

Everything else about the shape is deliberately the same: a hard Phase-1→
Phase-2 gate, fail-closed input acquisition, a scope-count confirmation gate, a
skill-namespaced Phase-1-questions workbook, a self-check checklist, and a
`last_run`/history ledger for in-place re-runs. `integration-test` scopes by
**module** (`aFunctionModule`); `qualification-test` scopes by **feature**
(`aFeature`) — a different axis, so their manifests live in separate
directories (`20_AI/manifests/integration-test/` /
`20_AI/manifests/qualification-test/`) rather than sharing
`20_AI/manifests/<MODULE>.yaml` with the SWE.3 skills.

**v1 scope is Excel-only.** A real vTestStudio project folder also holds `.vtt`
test tables and `.vtsoproj`/CAPL automation — generating or updating those is an
explicit **v2**, not attempted here. `integration-test` is also **AUTOSAR-only
for v1**: its only validated pattern is RTE-debugger breakpoint testing
(`Rte_Write`/`Rte_Read`), so it stops rather than inventing a black-box pattern
for a module with no RTE symbols to work from.

---

## 4. Key decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | **Skills, not slash commands or CLAUDE.md** | Progressive disclosure keeps context lean; shared files factor out triplicated rules; auto-selectable per project. |
| 2 | **One plugin, three *adaptive* module skills** (not six) | `project.type` is one-per-repo, so the skill auto-loads the flavor; the shared skeleton is maintained once. |
| 3 | **Two-level config** (`ai_project.yaml` → manifest) | Separates reusable *workflow* from project-specific *data*; makes compiler/target/layout dynamic per project. |
| 4 | **One manifest per module**, at `20_AI/manifests/` | Shared by all four SWE.3 workflows; collected next to the prompts/inputs for easy review. |
| 5 | **Harmonize up** into `common/` | The non-AUTOSAR prompts were more evolved (revision pinning, Gate Table, questions-xlsx, run history); both flavors now inherit those. |
| 6 | **In-place re-runs** driven by `last_run` hashes | A re-run updates changed artifacts in place instead of duplicating or clobbering. |
| 7 | **Ledger (working state) + append-only JSONL history** | `last_run` powers re-runs; the JSONL is the immutable audit trail. Git corroborates. |
| 8 | **No pipeline assumption** | Any skill runs standalone; review never assumes code-gen produced the module. |
| 9 | **Scaffold → validate → confirm inputs** | Developer never copy-pastes a fill block; the skill owns the path, schema, and defaults. |
| 10 | **Develop as project skills, then promote to a plugin repo** | Fast local iteration now; a dedicated marketplace repo for org-wide, versioned distribution later. |
| 11 | **A dedicated `/project-init` skill** for the per-repo config | Setup was a side effect of the first module run, so it happened on whatever branch that engineer was on. Two engineers → two disagreeing configs → a merge conflict in the file every run reads. One owner, one procedure, base-branch + duplicate guards; the module skills keep a guarded fallback so they still run standalone. |
| 12 | **A separate `_shared/testspec/` pack + `ai_test_project.yaml`** for `integration-test`/`qualification-test`, not a third `project.type` flavor | These skills run in a different repo (vTestStudio project folder) with no source code, no compiler, and no git-SHA build to pin against — the SWE.3 flavor mechanism and revision pinning genuinely don't apply. A parallel pack keeps the two domains from growing irrelevant conditionals into each other's shared files. |
| 13 | **Excel-only v1; AUTOSAR-only `integration-test`** | The vTestStudio `.vtt`/CAPL automation-script generation the user ultimately wants is deferred to v2 rather than attempted without a validated pattern. `integration-test`'s only validated pattern is RTE-debugger breakpoint testing, so it stops on a module with no RTE symbols rather than inventing a black-box equivalent. |
| 14 | **`code-fix` as a fifth SWE.3 skill, not a mode of `code-dev`** | The fix workflow inverts the input (evidence, not a requirement set), the allowed output (four verdicts — three of which forbid a diff), and the exit criterion (a verification plan the engineer runs, since nothing is reproducible here). Bolting a second entry path onto `code-dev` would double its branching for both workflows and leave the evidence gate nowhere to live; a separate orchestrator sharing `workflow-discipline`, `no-fabrication`, and both flavor packs keeps the guard-rails identical where they genuinely are identical. |

---

## 5. Distribution & cost (planned)

- **Develop** here as project skills under `.claude/skills/` (instant iteration).
- **Promote** to a dedicated repo (e.g. `Signata-GmbH/claude-autosar-skills`)
  packaged as a plugin: `.claude-plugin/plugin.json` (semver, git-tagged) +
  `marketplace.json`.
- **Distribute** via three tiers:
  1. *Project skills* — committed to a repo (any plan).
  2. *Plugin marketplace* — a git repo teams add + `/plugin install` (any plan).
  3. *Managed settings* — an admin auto-pushes org-wide (**Teams / Enterprise**).
- **Cost:** none from Anthropic for authoring, hosting, or distributing —
  token usage only. A marketplace is just a git repo you host.

---

## 6. Project context recap

- **AUTOSAR** side: MQB ST2 Park-Lock controller, ASIL-B, VectorCAST
  (STATEMENT+MCDC), RTE I/O, MemMap, runnables.
- **non-AUTOSAR** side: Small_Actuator, Melexis MLX81332, LIN 2.2, VectorCAST
  (Statement+Branch), `_cfg.h` IF-macros, scheduler-driven.
- Neither builds/runs a toolchain in-session, and no debugger or test bench is
  reachable either — the **no-fabrication** rule is absolute across every skill.
