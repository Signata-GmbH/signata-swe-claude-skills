# Using the SWE AI Skills — Beta (v0.0.1)

Claude Code skills for our AUTOSAR **and** non-AUTOSAR firmware projects — three
per-module workflows plus a one-time per-repo setup. They replace the old
copy-paste prompts. **This is a beta** — please try them on real modules and
report what breaks.

## What you get

| Command | Does |
|---|---|
| `/project-init` | **Run once per repo, on `develop`.** Creates `20_AI/ai_project.yaml` (the shared project config) and commits it. Refuses to create a second one if it already exists. |
| `/code-dev <MODULE>` | Implement a module (or a feature in one) from its requirements + an Implementation Review doc. Two-phase: analysis & questions first, code only after you approve. |
| `/code-review <MODULE>` | Formal SWE.3 review of the user-implemented C → a populated Findings List, with the checklist walked. |
| `/unit-test <MODULE>` | Generate / update a VectorCAST `.tst` suite from requirements + code, with an auditable requirement→case ledger. |

Each skill **adapts automatically** to whether the repo is AUTOSAR or non-AUTOSAR.

## Getting it

The marketplace is pushed to everyone via Claude Code **managed settings**, so you
just need **one click** to install it — no CLI, no GitHub login (the repo is public).

**One-time, per engineer (VS Code extension):**
1. **Restart VS Code** (so managed settings register the `signata` marketplace).
2. Type **`/plugins`** (plural) in the Claude prompt → opens the **Manage plugins** UI.
   *(Note: the `/plugin` singular subcommands don't work in the extension — use `/plugins`.)*
3. Under **Available plugins**, find **`signata-swe-claude-skills`** → click **Install**.
4. **Restart** when prompted.

The skills then appear in the `/` menu as `/signata-swe-claude-skills:project-init`,
`…:unit-test`, `…:code-review`, `…:code-dev` — and you never install them again
(updates are automatic).

**If it's not under "Available":** the marketplace didn't register (usually a stale
cache). Close VS Code, delete the folder `%USERPROFILE%\.claude\plugins`
(`~/.claude/plugins` on macOS/Linux), reopen, and try `/plugins` again.

**If a new skill or fix doesn't show up after a restart** (e.g. `/project-init`
missing from the `/` menu), your plugin copy is pinned to an older commit. Check and
update it from a terminal:

```bash
claude plugin list      # shows Version: <commit> and Scope: managed
claude plugin update signata-swe-claude-skills@signata --scope managed
```

Then **reload VS Code** (Cmd/Ctrl+Shift+P → *Developer: Reload Window*), or quit and
reopen it. Two gotchas worth knowing:

- **`--scope managed` is required.** The command defaults to `user` scope and fails
  with *"not installed at scope user"* — which reads like the plugin is missing when
  it is actually installed org-wide at `managed` scope.
- **`/reload-skills` will not help here.** It re-reads the skills already loaded in
  the session; the plugin *cache* is only resolved at startup, so a restart is what
  picks up a new version.

Seeing the skill on **claude.ai** but not in VS Code is expected during this window:
claude.ai resolves the repo server-side, while the extension goes through the plugin
cache on your machine.

## Using it

### Once per repo — `/project-init` on `develop`

`20_AI/ai_project.yaml` holds the project facts every skill run needs (AUTOSAR vs
non-AUTOSAR, compiler, target, ASIL, source/test roots, where the input documents
live). It is **one file per repository**, shared by everyone.

1. On the **base branch** (`develop`), at the **repo root**, run `/project-init`.
2. It detects AUTOSAR vs non-AUTOSAR (showing you the evidence), discovers the
   layout roots and input documents, and asks only for what it cannot derive —
   compiler, target, ASIL, and (AUTOSAR) the variant list.
3. It shows you the finished YAML for approval, writes it, then **asks** whether to
   commit and push. Say yes — once it is on `develop`, nobody else needs to do this.

**Only one engineer per repo does this.** If you run it and the config already
exists — on `develop` or on a teammate's branch — it **stops** and tells you to
merge that one instead of creating a competing copy. Two configs created on two
feature branches means a merge conflict in the file every run depends on; that is
what the guard prevents. Re-running it later on an existing config switches to
**validate/repair** mode: it checks the paths still resolve and offers to fix only
the broken fields, never overwriting your file.

### Then, per module

1. Open Claude Code at your **repo root** and run e.g. `/unit-test FUSA_PosDet`.
2. **First run for a module** scaffolds that module's manifest
   (`20_AI/manifests/<MODULE>.yaml`) and confirms the scope with you. If the
   project config is missing and you are not on `develop`, the skill will point you
   at `/project-init` rather than quietly creating one on your branch.
3. The skill will **ask you for the input documents it needs** (requirements
   workbook, SDD, signals & parameters, and for reviews the coding guideline +
   checklist). Provide the path or attach — `.pdf` or `.xlsx` both work. It will
   **stop rather than guess** if a mandatory one is missing.
4. It confirms the **requirement count** and its plan, then does the work and writes
   an audit record under `20_AI/manifests/<MODULE>.yaml`.

## What to expect (and what it will NOT do)

- **It never builds, runs Polyspace, or executes VectorCAST** — no toolchain is
  available to it. It works *by inspection* and says so. Never trust a "compiles /
  passes" claim; there won't be one.
- It **asks before overwriting** existing validated code and **stops** instead of
  inventing missing inputs. If it seems to pause a lot, that's the safety design.
- **Re-runs update in place** — change a requirement and re-run; it revises just the
  affected cases/findings, and logs the run.

## It's a beta — please report

Tell us (with the module + what you ran):
- anything it got factually wrong (a wrong signal, a phantom requirement, a bad line
  number),
- anywhere it proceeded without asking for something it should have,
- anything confusing in what it asked for.

Fixes ship automatically — with `autoUpdate` on, you'll get them on the next refresh.
