# Test-spec project config bootstrap — `20_AI/ai_test_project.yaml`

> The **single** authoritative procedure for creating, validating, and repairing
> the per-repo test-spec project config. Loaded by `integration-test` /
> `qualification-test` when the config is missing, so there is exactly one code
> path and one set of guards — the same shape as
> [../common/project-config.md](../common/project-config.md), which owns the
> *separate* `20_AI/ai_project.yaml` for the SWE.3 C-source repo. The two
> configs are never merged: this repo (a vTestStudio project folder) typically
> has no source code, no compiler, and no build to pin a revision against, so
> its config and its pinning mechanism (§2 of
> [workflow-discipline.md](workflow-discipline.md)) are both different.

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
- `integration_test.testability_filter`

### 4.2 Discover, then confirm

- **`docs.*`** — glob under `docs.root` (default `20_AI/`) for each document;
  several candidates → pick-one popup; none → ask for the path. Every document
  may be `.pdf` or `.xlsx`.
- **`qualification_test.valid_features`** — derive from the distinct `aFeature`
  values in `docs.requirements_workbook` once it is available; present the list
  for confirmation (it is a **learned** field, re-validated on later runs, not
  a one-time fixed enum — a repo's requirements export can gain a feature).
- **`integration_test.module_name_mapping`** — starts empty; each
  `integration-test` run that resolves a new module's mapping (per
  `integration-test-patterns.md`'s discovery method) appends its entry here so
  later runs/engineers reuse it instead of re-deriving it. Never seed this file
  by analogy with another project.

Use `AskUserQuestion` popups for the categorical choices and pick-one document
choices; typed input only for genuinely free text (release id, environment
string, a path discovery missed).

## 5. If the config already exists — validate, never overwrite

Do not rewrite the file. Emit a validation table (`field | value | valid? |
evidence / problem`) covering: `schema_version` present; no surviving
`<PLACEHOLDER>`; every `docs.*` path (other than `N/A`) resolves to a readable
file; `qualification_test.valid_features` still matches the distinct `aFeature`
values seen in the requirements workbook (a mismatch is a loud finding, not a
silent skip). Offer to repair only the invalid fields. If everything is valid,
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
