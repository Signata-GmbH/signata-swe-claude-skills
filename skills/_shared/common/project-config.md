# Project config bootstrap — `20_AI/ai_project.yaml`

> The **single** authoritative procedure for creating, validating, and repairing
> the per-repo project config. Owned by the `project-init` skill; loaded by
> `code-dev` / `code-review` / `unit-test` when the config is missing, so there is
> exactly one code path and one set of guards.

`20_AI/ai_project.yaml` is **one per repository, shared by every engineer and
every module**. It is created **once**, **on the repo's base branch**, and
committed. Two engineers scaffolding it independently on their own feature
branches is the failure this procedure exists to prevent: the two files will
disagree (different compiler string, different layout roots, different doc
paths), both will be committed, and the merge conflict is in the one file every
skill run depends on.

## 1. Locate the repo and the base branch

1. Confirm the working directory is the **repo root** (`git rev-parse --show-toplevel`).
   If Claude was opened in a subdirectory, use the toplevel — the config path
   `20_AI/ai_project.yaml` is relative to it. Not a git repo → **STOP** and say so.
2. Determine the **base branch** — derive, never assume:
   - `git symbolic-ref refs/remotes/origin/HEAD` (strip `refs/remotes/origin/`), else
   - the first of `develop`, `main`, `master` that exists as `origin/<name>`, else
   - **ask** the engineer which branch is the integration branch.
   Report which branch you concluded and how.
3. Record the current branch (`git rev-parse --abbrev-ref HEAD`) and whether the
   worktree is clean (`git status --porcelain`).

## 2. Has someone already created it? (check BEFORE writing anything)

The local working tree is not evidence. Run all three checks and report them:

| Check | Command | Meaning |
|---|---|---|
| Local | `test -f 20_AI/ai_project.yaml` | present here → go to §5 (validate, never overwrite) |
| Base branch | `git ls-tree -r --name-only origin/<base> -- 20_AI/ai_project.yaml` | already integrated → **do not create a second one** |
| Any fetched branch | `git log --all --oneline -- 20_AI/ai_project.yaml` | someone's in-flight version exists elsewhere |

Run `git fetch` first (or say you could not, and why) so these reflect reality.

- **Present on `origin/<base>`** → **STOP creating.** Tell the engineer to
  `git pull` / merge the base branch and re-run; then validate it (§5). Never
  author a competing file.
- **Present only on another branch** → **STOP creating.** Name the branch and the
  commit, and say the config is already in flight — it should be merged, not
  duplicated. Only an explicit engineer decision overrides this.
- **Nowhere** → continue.

## 3. Base-branch guard (HARD GATE)

If the current branch **is** the base branch and the worktree is clean, proceed.

Otherwise **stop and ask** (`AskUserQuestion`) — never switch, stash, or discard
anything on your own:

- **Switch to `<base>` and create it there** (recommended; offer only when the
  worktree is clean, and only for a plain `git switch <base>` — never combined
  with a stash, reset, or checkout of files).
- **Create it on this branch anyway** — allowed, but state plainly that it must be
  merged to `<base>` promptly, and that if a teammate does the same on their
  branch the two configs will conflict.
- **Abort** — do nothing.

Record the outcome in the run summary. A dirty worktree on the base branch is not
a blocker for writing one new file, but say so rather than silently mixing your
new file into an unrelated set of pending changes.

## 4. Resolve every field — derive, discover, or ask

Scaffold from [../ai_project.template.yaml](../ai_project.template.yaml). Work
field by field. **No `<PLACEHOLDER>` may survive into the written file** — each
field ends as an engineer-confirmed value, or `N/A` plus a one-line reason.

### 4.1 Derive with evidence, then confirm

Never conclude silently: show the evidence (the paths you found) and confirm.

- **`project.name`** — propose from the repo directory / `origin` remote name.
- **`project.type`** — the most consequential field; it selects the flavor for the
  whole repo. Search for both signatures and show what you found:
  - *autosar* → `Rte_*.h`, `Appl_MemMap.h`, an `Rte` / BSW tree, Agnosar stubs
    under a `Common/src/`.
  - *nonautosar* → a `*.ldf`, `l_u8_rd_*` / `motor3ph_*` accessors, `<Module>_cfg.h`
    IF-macro headers, a `Scheduler/` main loop.
  Ambiguous or both/neither → **ask**, do not pick the majority signature.
- **`layout.*`** — glob for the roots (`app_root`, `rte_inc`, `vcast_env`, and for
  non-AUTOSAR `lin_ldf`, `linif`, `stubs`). Write a path **only if it exists on
  disk**; set the other flavor's fields to `N/A`. A root you cannot find is asked
  for, never invented (no-fabrication applies to config too).
- **`requirements.workbook`** and **`docs.*`** — discover by globbing under
  `docs.root` (default `20_AI/`); several candidates → pick-one popup; none →
  ask for the path. `docs.architecture` follows the §1 *ask* tier of
  [workflow-discipline.md](workflow-discipline.md): explicitly offer it, and
  record `N/A` + reason only if the engineer declines. Never let one document
  stand in for another.
- **`requirements.scoping`** — `by-module-filter` for autosar,
  `explicit-id-list` for nonautosar; confirm.
- **`coverage.unit_test`** — `STATEMENT+MCDC` for autosar, `Statement+Branch` for
  nonautosar; confirm.

### 4.2 Ask — not derivable from the repo

- **`toolchain.compiler`** — e.g. GreenHills / TASKING / mlx16-gcc. A compiler
  name found in a makefile is a *proposal*, not an answer; confirm it.
- **`toolchain.target`** — MCU + core, free text.
- **`safety.default_asil`** — `N/A` for nonautosar.
- **`requirements.variants`** (autosar only) — mind the two-line cell trap: a
  variant value may contain an embedded newline (`"MQB\nCEA"`), so quote it
  exactly as the workbook holds it. `[]` for nonautosar.

Use `AskUserQuestion` popups for the categorical choices (type, scoping,
coverage, ASIL, and pick-one document choices); typed input only for genuinely
free text (target, variants, a path discovery missed).

## 5. If the config already exists — validate, never overwrite

Do not rewrite the file. Emit a validation table
(`field | value | valid? | evidence / problem`) covering:

- `schema_version` present and understood;
- no surviving `<PLACEHOLDER>` values;
- `project.type` consistent with what the repo actually looks like (§4.1) —
  a mismatch is a **loud finding**, since it silently selects the wrong flavor;
- every `layout.*` path (other than `N/A`) exists on disk;
- every `docs.*` / `requirements.workbook` path resolves to a **readable** file.

Then offer to repair **only the invalid fields**, asking for each, and rewrite
just those. Leave valid fields byte-identical — engineers may have hand-tuned
them. If everything is valid, say so and stop; there is nothing to do.

## 6. Confirm → write → hand off (HARD GATE)

1. **Present the complete resolved YAML** in chat, plus a table of where each
   value came from (`derived from <path>` / `answered by engineer` /
   `N/A — <reason>`). **STOP and wait for approval.**
2. On approval, write `20_AI/ai_project.yaml` (create `20_AI/` if needed). Write
   nothing else — **no per-module manifests, no `manifests/history/`**; those
   belong to the three module skills, which scaffold them per module.
3. **Then ask** whether to commit and push it to `<base>` (commit message e.g.
   `Add 20_AI/ai_project.yaml (AI skills project config)`). Never commit, never
   push, and never open a PR without an explicit yes; if declined, print the exact
   commands so the engineer can do it.
4. Close with the hand-off: the config is repo-wide and one-time — the next step
   is `/code-dev`, `/code-review`, or `/unit-test` on a module, which scaffolds
   that module's manifest.

## 7. When a module skill hits a missing config

`code-dev` / `code-review` / `unit-test` must not quietly scaffold a config on a
feature branch — that is exactly how the competing-file conflict arises. On a
missing config they:

1. Run §1–§2. If the config exists on `origin/<base>` or another branch → **STOP**
   and say to merge it, not to create one.
2. If it exists nowhere and the current branch **is** the base branch → run the
   full procedure inline (§4, §6) and continue with the module work afterwards.
3. If the current branch is **not** the base branch → tell the engineer to run
   **`/project-init` on `<base>`** and commit it, and **ask** whether to
   nevertheless bootstrap here for this run (§3's middle option). Proceed only on
   an explicit yes, and record in the run summary that the config still needs to
   reach `<base>`.
