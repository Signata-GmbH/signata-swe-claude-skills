# Test-spec project config bootstrap — `20_AI/ai_test_project.yaml`

> The **single** authoritative procedure for creating, validating, and repairing
> the per-repo test-spec project config. Loaded by `integration-test` /
> `qualification-test` when the config is missing, so there is exactly one code
> path and one set of guards — the same shape as
> [../common/project-config.md](../common/project-config.md), which owns
> `20_AI/ai_project.yaml`. Both files live in the **same** repository — the
> SWE.3 project repository, where every skill runs — but they stay two files:
> this one holds test-spec facts (the DOORS baseline, attribute values, test
> documents) the code skills never read. Where `ai_project.yaml` already holds
> a fact, this config **reads** it rather than copying it (§4.3).

`20_AI/ai_test_project.yaml` is **one per repository, shared by every engineer
running either skill**. It is created **once**, **on the repo's base branch**,
and committed. Two engineers scaffolding it independently on their own feature
branches is the failure this procedure exists to prevent — the two files will
disagree (different `RELEASE`, different `ENVIRONMENT` spelling, different doc
paths), both get committed, and the merge conflict lands in the one file every
run depends on.

## 1. Locate the repo and the base branch

Identical to `common/project-config.md` §1: confirm the repo root
(`git rev-parse --show-toplevel`; not a git repo → **STOP** and say so), derive
the base branch (`git symbolic-ref refs/remotes/origin/HEAD`, else
`develop`/`main`/`master`, else **ask**), and record the current branch + worktree
cleanliness.

**Where the skills run.** The default is the **SWE.3 project repository** —
the same repo `code-dev`, `code-review` and `unit-test` run in. The one
fallback, for a team whose QA engineers cannot commit there, is a **separate
Git repository** for the test artefacts, with `docs.source_repo.path` pointing
at the SWE.3 repo. A folder outside Git is neither — typically a vTestStudio
project folder, which is often not under version control. Stop there and say
why: the one-config guard, the run history and the in-place updates all depend
on Git. Tell the engineer to run the skill from the SWE.3 repository; the
vTestStudio folder is configured as an external path (`vteststudio.project`),
never used as the place to run.

## 2. Has someone already created it? (check BEFORE writing anything)

Same three checks as `common/project-config.md` §2, targeted at
`20_AI/ai_test_project.yaml`: local working tree, `git ls-tree -r --name-only
origin/<base> -- 20_AI/ai_test_project.yaml`, and `git log --all --oneline --
20_AI/ai_test_project.yaml`. `git fetch` first. Present on `origin/<base>` or on
another branch → **STOP creating**, tell the engineer to merge/pull instead.
Nowhere → continue.

## 3. Base-branch guard (HARD GATE)

Identical to `common/project-config.md` §3: on the base branch with a clean
worktree, proceed. Otherwise **stop and ask** (`AskUserQuestion`) — switch to
`<base>` (only if clean, only a plain switch), create here anyway (state
plainly it must be merged promptly), or abort. Never switch/stash/discard
unilaterally.

## 4. Resolve every field — derive, discover, or ask

Scaffold from
[ai_test_project.template.yaml](ai_test_project.template.yaml). No
`<PLACEHOLDER>` survives into the written file — each field ends as an
engineer-confirmed value, or `N/A` plus a one-line reason.

### 4.1 Ask — these must never be guessed

The source prompts mark these "To confirm" for a reason: near-identical strings
in the DOORS export are a known trap (digit `0` vs letter `O` in a release ID;
seven near-duplicate spellings of an environment name; a status wording the
Test Plan uses that isn't an actual attribute value). **Always ask, never infer
from the "most common" spelling seen:**

- `release.id`, `release.variants`
- `attributes.environment`
- `attributes.status_filter`
- `attributes.classification_rule` (a pointer to the governing document
  section, not a value — confirm which document/section governs)
- `attributes.classification_attribute_rules` — whether any tiers of that
  document are decided purely by `aC_SAF`/`aC_SEC`/`aC_REG`. If so, the
  engineer transcribes those rules (tier, rule number, condition); never derive
  them from the document yourself, and never add a tier that needs judgement.
  Write `[]` for "none" — never leave the key out, because a missing key means
  "not asked yet" and is asked again (workflow-discipline.md §3). One answer
  serves the whole project and both skills; it is not asked per module.
- `integration_test.testability_filter`
- `integration_test.authoring_mode` — `from_scratch` or `extend_existing`
  (integration-test-patterns.md §0.1). Ask it even when an export-shaped file
  sits in the folder: a file's presence is not the engineer's decision to use
  it. Then set `docs.integration_test_spec_export` to match — a path iff
  `extend_existing`, `N/A` iff `from_scratch`.
- `integration_test.peer_depth` and `integration_test.peer_module_mirroring`
  (integration-test-patterns.md §2–§3) — propose `target_ports` and `false`, and
  say that the other values typically multiply the output several times over.
- `integration_test.reference_columns` and `qualification_test.reference_columns`
  — whether the project wants the validity columns beside the 21
  (output-format.md); propose off. The ID column (column A) is always written
  and is not asked.

`integration_test.architecture_text_fallback` is **not** asked here: it starts
as `stop` and changes only by an engineer decision at the export-completeness
gate (workflow-discipline.md §1.3), when a names-only export is actually on the
table.

### 4.2 Discover, then confirm

- **`docs.*`** — glob under `docs.root` (default `20_AI/`) for each document;
  several candidates → pick-one popup; none → ask for the path. Every document
  may be `.pdf` or `.xlsx`. For `functional_architecture_export`, filenames are
  weak evidence — the same DOORS module exported twice from two views (one
  showing object names, one showing object text) looks like two documents and is
  easily mistaken for two modules. Confirm by content and by `ID` set: an
  identical `ID` set means one module in two views, so point
  `functional_architecture_export` at the view with the names and
  `functional_architecture_export_text_view` at the other, rather than treating
  them as separate documents.
- **`docs.source_repo`** — `path: .` (this repository) in the default setup;
  in the fallback setup, ask for the SWE.3 repo's path and confirm it is a git
  working tree (`git -C <path> rev-parse --show-toplevel`). Ask for `ref` (the
  revision test cases are authored against); `N/A` means "whatever is checked
  out", pinned per run. Declining the code is allowed only as a recorded
  decision with its reason, and makes every integration-test run degraded
  (integration-test-patterns.md §9) — say so before writing it.
- **`docs.reference_specs`** (qualification-test) — starts empty; filled at
  the start of each run from the documents its requirements cite
  (qualification-test-patterns.md §3.1), and reused by every feature after.
- **`docs.comm_database`, `docs.test_plan`, `docs.test_environment`** —
  discover like any other document, then **offer** each explicitly, saying what
  is lost without it (workflow-discipline.md §1.1). In the SWE.3 repo the bus
  database (DBC/LDF/ARXML system extract) is often already under version
  control; propose that copy before asking for another.
- **`docs.os_config`, `docs.debug_build`** (integration-test) — the OS/RTE
  configuration is usually in this repository already: propose the ECUC ARXML
  that defines the tasks and the event-to-task mapping, or the generated OS/RTE
  sources, and confirm. The debug build is a build output, usually outside Git
  and rebuilt often: ask for its usual location (the ELF and/or the map file of
  the **Debug** SW, not the series build), and offer both explicitly, saying
  what is not checked without them (workflow-discipline.md §1.1).
- **`vteststudio.project`** — reserved for v2. Ask for the path only if the
  engineer knows it; otherwise `N/A`. Keep `write_access: false`.
- **`qualification_test.valid_features`** — derive from the distinct `aFeature`
  values in `docs.requirements_workbook` once it is available; present the list
  for confirmation (it is a **learned** field, re-validated on later runs, not
  a one-time fixed enum — a repo's requirements export can gain a feature).
- **`integration_test.peer_modules`** — starts empty; each `integration-test`
  run that resolves a module's writer→reader pairings appends them here after
  engineer confirmation, so a later run of the same module (or of one of its
  peers) reuses the pairing instead of re-deriving it. Never seeded by analogy.
- **`qualification_test.bench_catalogue`** — starts empty; each
  `qualification-test` run appends the stimulus/observation means confirmed in
  its Phase-1 catalogue (qualification-test-patterns.md §3.2), so the next
  feature confirms only new items. Never seeded by analogy.
- **`integration_test.module_name_mapping`** — starts empty; each
  `integration-test` run that resolves a new module's mapping (per
  `integration-test-patterns.md`'s discovery method) appends its entry here so
  later runs/engineers reuse it instead of re-deriving it. Never seed this file
  by analogy with another project.

Use `AskUserQuestion` popups for the categorical choices and pick-one document
choices; typed input only for genuinely free text (release id, environment
string, a path discovery missed).

### 4.3 Read from `ai_project.yaml`, never copy

When `20_AI/ai_project.yaml` exists in the repository whose code is read (this
one, or the SWE.3 repo in the fallback setup), these facts come from it **at
run time** and are not written into this config, so the two files cannot drift
apart:

| Fact | From `ai_project.yaml` | Used for |
|---|---|---|
| AUTOSAR or not | `project.type` | integration-test's AUTOSAR-only guard |
| Application source root | `layout.app_root` | finding the module's `.c` files |
| RTE headers | `layout.rte_inc` | RTE symbols and enum literals — set `docs.rte_type_headers: N/A` |
| SW requirements export | `requirements.workbook` | SWE.6 test basis — write `docs.requirements_workbook: ai_project` |

`release.variants` is **proposed** from `requirements.variants` and then
confirmed, never copied silently: the test-spec variant strings must match the
values in the DOORS test module, which is not guaranteed. Without an
`ai_project.yaml`, ask for each of these as before — suggest running
`/project-init` first, since the code skills will need it anyway.

## 5. If the config already exists — validate, never overwrite

Do not rewrite the file. Emit a validation table (`field | value | valid? |
evidence / problem`) covering: `schema_version` present; no surviving
`<PLACEHOLDER>`; every `docs.*` path (other than `N/A`) resolves to a readable
file; every `N/A` carries its reason; `integration_test.authoring_mode` is set
and agrees with `docs.integration_test_spec_export` (path ⇔ `extend_existing`,
`N/A` ⇔ `from_scratch`); `docs.source_repo.path` is a git working tree (`.`
in the default setup) and `ref`, if set, resolves in it; no fact that §4.3
reads from `ai_project.yaml` is duplicated here with a different value;
`vteststudio.write_access` is `false` while v1 is the running version;
`integration_test.peer_depth` and
`peer_module_mirroring` are set (absent in an older config → ask, do not
default silently); `attributes.classification_attribute_rules` is present
(absent → never asked: ask once, record `[]` for "none"); every rule in it has a
tier, a rule number and a condition on one `aC_*` attribute;
`qualification_test.valid_features` still matches the
distinct `aFeature` values seen in the requirements workbook (a mismatch is a
loud finding, not a silent skip). Offer to repair only the invalid fields. If everything is valid,
say so and stop.

## 6. Confirm → write → hand off (HARD GATE)

Same as `common/project-config.md` §6: present the complete resolved YAML plus
a `derived from <path>` / `answered by engineer` / `N/A — <reason>` table,
**STOP and wait for approval**, write `20_AI/ai_test_project.yaml` on approval
(create `20_AI/` if needed, write nothing else), then **ask** whether to commit
and push to `<base>` — never commit/push/PR without an explicit yes.

## 7. When a skill hits a missing config

`integration-test` / `qualification-test` must not quietly scaffold this config
on a feature branch. On a missing config:

1. Run §1–§2. Exists on `origin/<base>` or another branch → **STOP**, say to
   merge it.
2. Exists nowhere and the current branch **is** the base branch → run §4–§6
   inline and continue with the module/feature work afterwards.
3. Current branch is **not** the base branch → tell the engineer to bootstrap
   it on `<base>` and commit, and **ask** whether to nevertheless bootstrap here
   for this run (§3's middle option). Proceed only on an explicit yes, and
   record in the run summary that the config still needs to reach `<base>`.
