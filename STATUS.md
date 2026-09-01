# Skill Development — Status & Roadmap

> Living tracker for the AUTOSAR / non-AUTOSAR AI skills plugin.
> Technical design is in [README.md](README.md). Update this file as work lands.

- **Repo:** `Signata-GmbH/signata-swe-claude-skills` (canonical home — edit here, not the CEA staging branch)
- **Release:** **v0.0.1 (first beta)** — tag `signata-swe-claude-skills--v0.0.1`
- **Last updated:** 2026-09-01
- **Overall phase:** Beta — rolling out org-wide via managed settings for real-world testing
- **Origin note:** developed on CEA staging branch `MQBST2-AI-Skills-Development` (now frozen); migrated here 2026-08-17

---

## Legend
✅ done · 🟡 in progress · ⬜ not started · ⚠️ needs attention

---

## Progress by area

### Foundation — config & manifest
- ✅ `_shared/ai_project.template.yaml` — per-repo config (type, toolchain, layout, coverage, variants, docs)
- ✅ `_shared/manifest-template.yaml` — per-module manifest; inherits project config; flavor-tagged `[A]`/`[N]`; `last_run` ledgers with revision pinning

### Shared discipline — `_shared/common/`  (both flavors)
- ✅ `no-fabrication.md` — toolchain honesty rule
- ✅ `project-config.md` — the single per-repo config bootstrap (owned by `project-init`): base-branch derivation, duplicate-config check (local / `origin/<base>` / all fetched branches), base-branch hard gate, evidence-based derivation + ask list, validate-never-overwrite, confirm→write→offer-commit; §7 is the module skills' guarded fallback
- ✅ `workflow-discipline.md` — §0 standalone · §1 **fail-closed input acquisition + mandatory-doc matrix + count gate** · §2 revision pinning · §3 scaffold→validate→confirm · §4 grounding · §5 Phase-1 questions→xlsx (skill-namespaced) · §6 Gate Table · §7 fidelity · §8 traceability · §9 ledger & history · §10 no-fabrication
- ✅ `unittest-design.md` — test-design rules + deliverables + symbol-grounding self-check (was the missing D1 content)
- ✅ `review-quality.md` — finding quality, false-negative prevention, checklist walk, traceability, output mechanics
- ✅ `vectorcast-syntax.md` — `.tst` grammar shared verbatim

### AUTOSAR flavor — `_shared/autosar/`  (complete)
- ✅ `project-context.md` — reads facts from `ai_project.yaml` (compiler loop closed)
- ✅ `requirements-filter.md` — by-module + variant filter; now references `ai_project.yaml` for workbook/variants
- ✅ `forbidden-constructs.md` — no-float, MISRA essentials
- ✅ `review-flavor.md` — MISRA rule-numbers **in**, AUTOSAR-isms required, `Critical` severity, MemMap checks, §0.6 domain-model AUTO gate, output columns

### non-AUTOSAR flavor — `_shared/generic/`  (complete)
- ✅ `project-context.md` — LIN/LDF, `_cfg.h` IF-macros, scheduler, no-RTE, Statement+Branch
- ✅ `requirements-scope.md` — explicit `SW_Req` ID list / release filter (no reliable module column)
- ✅ `forbidden-constructs.md` — float allowed (limited), SIGNATA guideline authoritative
- ✅ `review-flavor.md` — MISRA rule-numbers **out**, no AUTOSAR-isms, 4 severities, `AI Suggested Fix` column, ignore Simulink rows

### Setup skill — `project-init/`
- ✅ `project-init/SKILL.md` — 8-step, one-file-only setup skill: derives the base branch, refuses to author a second config (base branch or in-flight elsewhere), base-branch hard gate, detects `project.type` with shown evidence, discovers layout + docs, asks only compiler/target/ASIL/variants, confirm→write→offer commit+push; validate/repair mode on an existing config (`--validate`)
- ✅ Registered in `.claude-plugin/marketplace.json`; plugin description updated
- ⬜ Dry-run `/project-init` on a real repo (AUTOSAR **and** non-AUTOSAR) — verify type detection, the duplicate guard on a branch that already has the config, and validate/repair mode

### The three skill orchestrators  (complete)
- ✅ `unit-test/SKILL.md` — 7-step orchestrator; adapts by `project.type`
- ✅ `code-review/SKILL.md` — 7-step; flavor review stance + checklist walk
- ✅ `code-dev/SKILL.md` — two-phase hard gate; flavor interface + forbidden rules
- ✅ Step 1 of all three now routes a missing config through `project-config.md` §7 instead of scaffolding one on whatever branch the engineer happens to be on

### Validation & packaging
- ✅ First dry-run of each skill on `FUSA_PosDet` (AUTOSAR) — surfaced defects D1–D10 + confirmed U1–U5
- ✅ Defect fix pass applied (2026-08-13) — see Defect register below
- 🟡 **Re-validate** by re-running each skill on a real module (verify fail-closed acquisition, count gate, regenerate guard)
- ⬜ Dry-run on a non-AUTOSAR module (`SAPF_Mode`) to exercise the generic flavor + D5
- ✅ Scaffolded `.claude-plugin/plugin.json` + `marketplace.json` (plugin `signata-swe-claude-skills`, marketplace `signata`) + `PUBLISHING.md` runbook
- 🟡 Promote to dedicated repo `Signata-GmbH/signata-swe-claude-skills` (skills → `skills/`), tag `…--v0.0.1`
- 🟡 Roll out **org-wide via managed settings** (Teams/Enterprise): `extraKnownMarketplaces` + `enabledPlugins`
- ⬜ Commit `20_AI/ai_project.yaml` (+ manifests) to product-repo `develop` (NOT `.claude/skills/`) — now via `/project-init` on `develop`

---

## Immediate next step (2026-09-01)
`project-init` added as the fourth skill: the per-repo config is no longer a side
effect of whichever module run happens first on whichever branch. Next: **dry-run
`/project-init`** on one AUTOSAR and one non-AUTOSAR repo, exercising (a) fresh
create on `develop`, (b) the duplicate guard when the config already exists on the
base branch, (c) validate/repair on an existing config, (d) a module skill invoked
on a feature branch with no config — it must point at `/project-init`, not scaffold.

## Earlier next step
`/unit-test` re-validated: docs split, count gate, namespaced questions all work;
the silent Architecture substitution is now fixed (optional-but-asked +
no-self-substitution rule). Next: **re-run `/unit-test`** to confirm it now
**explicitly asks** for the ADD instead of substituting; then re-validate
`/code-review` (mandatory guideline+checklist acquisition) and `/code-dev`
(regenerate guard). Then package as a plugin.

---

## Decision log (chronological)

| Date | Decision |
|---|---|
| 2026-08-03 | Package the three prompts as **Skills** (not slash commands / CLAUDE.md). |
| 2026-08-04 | **One plugin, three skills, shared per-module manifest.** Manifest at `20_AI/manifests/<MODULE>.yaml`. Inputs via scaffold→validate→confirm + `AskUserQuestion`. |
| 2026-08-04 | **In-place re-runs**; on a changed requirement, update the case in place (not supersede). |
| 2026-08-05 | Separate **workflow from config**: new per-repo `ai_project.yaml`; compiler/target/layout dynamic per project. `project.type` **one per repo**. |
| 2026-08-05 | **Option B** — three *adaptive* skills (load flavor via `common`/`autosar`/`generic`), not six. |
| 2026-08-05 | **Harmonize up** — `common/` adopts the stronger non-AUTOSAR patterns (revision pinning, Gate Table, questions-xlsx, run history). |
| 2026-08-06 | **Ledger vs history:** `last_run` = working state; append-only `history/<MODULE>.jsonl` = audit trail. Chose JSONL + on-demand table. |
| 2026-08-06 | **No pipeline assumption:** any skill runs standalone; review never assumes code-gen ran. |
| 2026-08-06 | Skill dev moved to branch `MQBST2-AI-Skills-Development` off `release/X541`. |
| 2026-08-07 | Both flavor packs (`autosar/`, `generic/`) completed; `requirements-filter` config-ref fixed. |
| 2026-08-07 | Three `SKILL.md` orchestrators authored — all skill content complete; ready to test. Next: dry-run on a real module, then plugin packaging. |
| 2026-08-13 | First dry-run of all three skills on `FUSA_PosDet`; collected defect register (D1–D10 + U1–U5). |
| 2026-08-13 | **Docs split:** signals&params + architecture project-wide; SDD per-module; architecture may also be per-module. **SDD · Signals&Params · Architecture mandatory for all skills.** |
| 2026-08-13 | **Fail-closed input acquisition** (halt+acquire missing mandatory docs, never emit a deliverable without its rubric) + **mandatory requirements-count gate**. |
| 2026-08-13 | **code-dev regenerate guard:** decide `task_mode` by requirement scope — existing module + all reqs → warn/ask; existing + subset → non-destructive update; none → new module. |
| 2026-08-13 | Defect fix pass applied (D1–D10, U1–U5); links/refs verified. |
| 2026-08-13 | Re-validation `/unit-test`: docs split ✅, count gate ✅, namespaced Phase-1 file ✅ — but **Architecture was silently substituted by the SDD** (fail-open side door). |
| 2026-08-13 | **Architecture → optional but explicitly asked** (was mandatory); added a **no-self-substitution / no-self-waiver** rule (only an explicit engineer decision sets a doc `N/A`); documents may be `.pdf` **or** `.xlsx`. |
| 2026-08-14 | Re-validated `/unit-test` (explicit ADD ask — no substitution) and `/code-review` (hard-stop acquired guideline+checklist; checklist walked 178). Input governance validated both tiers. |
| 2026-08-14 | Packaging: plugin **`signata-swe-claude-skills`** (marketplace `signata`), distributed **org-wide via managed settings**. Scaffolded manifests + `PUBLISHING.md`. |
| 2026-09-01 | **Fourth skill `project-init`** — the per-repo `ai_project.yaml` gets one owner, created **once, on the base branch**, and committed. Rationale: setup was a side effect of the first module run, so it landed on whatever branch that engineer was on; two engineers → two disagreeing configs → a merge conflict in the file every run reads. Guards: duplicate-config check across local/`origin/<base>`/all fetched branches, base-branch hard gate (never auto-switch/stash), validate-never-overwrite, no surviving placeholders, commit/push only on an explicit yes. Procedure factored into `_shared/common/project-config.md`; the three module skills call its §7 as a guarded fallback so they still run standalone. |

---

## Defect register — dry-run findings (all fixed 2026-08-13)

| ID | Sev | Defect | Resolution |
|----|-----|--------|------------|
| D10 | High | code-dev silently regenerated a validated module | Task-mode guard by requirement scope in `code-dev/SKILL.md` §3 |
| U3/U4 | High | no mandatory-doc matrix; missing docs not acquired (fail-open) | `workflow-discipline §1` matrix + fail-closed acquisition loop |
| D1 | High | unit-test referenced test-design rules/deliverables in no loaded file | New `common/unittest-design.md`, wired into `unit-test/SKILL.md` |
| U1 | Med | per-module docs (SDD) in project config | Docs split: project-wide in `ai_project.yaml`, per-module in manifest `docs:` |
| U2 | Med | no prompt for extra docs / free-text instructions | manifest `docs.extra` + `docs.run_instructions`; offered in §1 acquisition |
| U5 | Med | requirements count silently learned | Mandatory count-confirmation gate in `workflow-discipline §3` |
| D9 | Med | Phase-1 questions filename collided across skills | Skill-namespaced `<MODULE>_Phase1_Questions_<Skill>.xlsx` |
| D5 | Med | "RTE-call diff" hardcoded (breaks non-AUTOSAR) | Flavor-adaptive in `code-dev/SKILL.md` §5 (RTE vs `_cfg.h` diff) |
| D2 | Low | dangling "§2.1 symbol-grounding self-check" | Re-pointed to `unittest-design.md` grounding self-check |
| D3 | Low | fossil `§4.1`/`§4.2` refs in autosar review-flavor | Refs de-numbered/corrected |
| D4 | Low | code-dev Phase-1 steps skipped item 6 | Renumbered 1–9 continuous |
| D7 | Low | finding-ID tag list not authoritative | Marked non-exhaustive (coin `UPPER-KEBAB` when none fits) |
| D8 | Low | AUTOSAR review-flavor had no output filename | Added `<Module>_CodeReview_Findings_<YYYY-MM-DD>.xlsx` |

---

## Open items & flags
- ✅ *(resolved 2026-08-07)* `autosar/requirements-filter.md` now references
  `ai_project.yaml` for the workbook + variants.
- ⚠️ **Compiler** was contradictory across the source prompts (GreenHills vs
  TASKING) — **resolved by design**: it's now a per-repo `toolchain.compiler`
  field, no longer asserted anywhere in the plugin.
- ℹ️ Skill command names are provisional (`/code-dev`, `/code-review`,
  `/unit-test`); confirm final names before packaging.
- ℹ️ The six source prompts live in `20_AI/prompts/` and are the authoritative
  material the skills are derived from.
