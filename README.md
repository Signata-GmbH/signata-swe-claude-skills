# AUTOSAR / non-AUTOSAR AI Skills — Technical Documentation

A Claude Code **plugin** that turns SIGNATA's three engineering AI prompts —
**Code Development**, **Code Review**, and **Unit-Test Generation** — into
reusable **skills** developers invoke by name, instead of copy-pasting a large
prompt and hand-filling inputs every time.

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

- `/code-dev`, `/code-review`, `/unit-test` — three commands, any repo.
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
| **Project config** | `20_AI/ai_project.yaml` — **one per repo**. Holds everything that varies by project (type, compiler, target, layout roots, coverage, variants, docs). |
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
│   │   ├── workflow-discipline.md   #   gates, revision pinning, Gate Table, ledger/history
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
├── code-dev/     SKILL.md        # orchestrator — two-phase hard gate
├── code-review/  SKILL.md        # orchestrator — findings + checklist walk
└── unit-test/    SKILL.md        # orchestrator — .tst authoring
```

### 3.2 Three *adaptive* skills, not six

We chose **three skills that adapt to the project** over six flavor-specific
ones. Because `project.type` is fixed per repo, a skill reads it and loads the
right flavor automatically — the developer always types the same `/unit-test`
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

### 3.4 How inputs are collected

Developers never copy-paste a fill block. On first run a skill:

1. **Derives** what it can (module upper-case, env name, all layout paths).
2. **Discovers** the input docs by globbing under `docs.root`.
3. **Scaffolds** `ai_project.yaml` (once per repo) and the module manifest from
   the templates.
4. **Confirms** via an `AskUserQuestion` popup for the categorical choices; when
   discovery finds several candidate documents, that becomes a pick-one popup.
   Only the genuinely unknowable (the module name) is a typed argument.
5. **Validates** the manifest on every later run; malformed fields are flagged,
   not silently used.

This is a **hard gate** — the skill stops and waits for confirmation before
doing any work.

### 3.5 Re-runs are in-place

A re-run is a diff, not a rewrite. The skill recomputes each in-scope
requirement's hash and compares it to `last_run`:

- **new** → author + append,
- **changed** (hash differs) → **update the mapped artifact in place** (case /
  code / finding keeps its identity),
- **removed** → flag the orphan (never silently delete),
- **unchanged** → leave it.

The delta is shown and confirmed before anything is written.

### 3.6 Audit: ledger + history + revision pinning

Two records with different jobs:

- **`last_run:`** (manifest) — *working state*, overwritten each run, drives the
  in-place diff.
- **`history/<MODULE>.jsonl`** — *append-only audit trail*, one immutable record
  per run: timestamp, workflow, skill version, **source git SHA + blob hashes**,
  requirements SHA, and the delta.

**Revision pinning** ties every output to the exact code state it was authored
against — essential for ASIL-B traceability. Git provides a second,
corroborating trail.

### 3.7 No pipeline assumption

The three workflows are **decoupled**. Any skill can be the first to run for a
module (review may run on code Code-Gen never produced). Each skill independently
scaffolds the config + manifest and populates **only its own** section; a shared
requirement-hash spine is used opportunistically but never required.

---

## 4. Key decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | **Skills, not slash commands or CLAUDE.md** | Progressive disclosure keeps context lean; shared files factor out triplicated rules; auto-selectable per project. |
| 2 | **One plugin, three *adaptive* skills** (not six) | `project.type` is one-per-repo, so the skill auto-loads the flavor; the shared skeleton is maintained once. |
| 3 | **Two-level config** (`ai_project.yaml` → manifest) | Separates reusable *workflow* from project-specific *data*; makes compiler/target/layout dynamic per project. |
| 4 | **One manifest per module**, at `20_AI/manifests/` | Shared by all three workflows; collected next to the prompts/inputs for easy review. |
| 5 | **Harmonize up** into `common/` | The non-AUTOSAR prompts were more evolved (revision pinning, Gate Table, questions-xlsx, run history); both flavors now inherit those. |
| 6 | **In-place re-runs** driven by `last_run` hashes | A re-run updates changed artifacts in place instead of duplicating or clobbering. |
| 7 | **Ledger (working state) + append-only JSONL history** | `last_run` powers re-runs; the JSONL is the immutable audit trail. Git corroborates. |
| 8 | **No pipeline assumption** | Any skill runs standalone; review never assumes code-gen produced the module. |
| 9 | **Scaffold → validate → confirm inputs** | Developer never copy-pastes a fill block; the skill owns the path, schema, and defaults. |
| 10 | **Develop as project skills, then promote to a plugin repo** | Fast local iteration now; a dedicated marketplace repo for org-wide, versioned distribution later. |

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
- Neither builds/runs a toolchain in-session — the **no-fabrication** rule is
  absolute across all three skills.
