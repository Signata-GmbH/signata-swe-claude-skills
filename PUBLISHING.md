# Publishing & Maintenance Runbook

How to ship these skills to the org as a plugin, update them, and what lives in
each product repo. Verified against code.claude.com/docs (Claude Code 2.1.232+).

> **Two homes.** The *skills* (this tree) become a **plugin** in its own repo,
> distributed org-wide. The *per-project config + manifests + input docs* live in
> each **product repo** (e.g. CEA). Don't mix them.

---

## A. Stand up the plugin repo (one-time)

Create a dedicated repo **`Signata-GmbH/signata-swe-claude-skills`** with this
layout (single-plugin marketplace, plugin at the repo root):

```
signata-swe-claude-skills/
├── .claude-plugin/
│   ├── marketplace.json      # catalog (already scaffolded)
│   └── plugin.json           # plugin manifest + version (already scaffolded)
├── skills/                   # ← the CURRENT .claude/skills/ content goes here
│   ├── _shared/
│   ├── unit-test/SKILL.md
│   ├── code-review/SKILL.md
│   └── code-dev/SKILL.md
├── README.md
└── STATUS.md
```

Assembly from this dev branch:

```bash
# from a clean clone of the new empty repo
mkdir -p skills .claude-plugin
# copy skill content (from the CEA dev branch .claude/skills/)
cp -R <CEA>/.claude/skills/{_shared,unit-test,code-review,code-dev} skills/
cp    <CEA>/.claude/skills/{README.md,STATUS.md} .
cp    <CEA>/.claude/skills/.claude-plugin/{plugin.json,marketplace.json} .claude-plugin/
# (the skill files reference ../_shared/... relatively — that resolves under skills/)
git add . && git commit -m "Initial plugin: signata-swe-claude-skills v0.0.1"
```

Validate and tag the release:

```bash
claude plugin validate . --strict          # catches manifest typos
claude plugin tag . --push --message "Release %s"
#   → creates + pushes tag  signata-swe-claude-skills--v0.0.1  (name--v<version>)
```

**Version lives in ONE place** — `plugin.json` `version`. Do **not** also put a
`version` in the marketplace.json plugin entry (double-declaration masks stale
manifests).

---

## B. Publish org-wide (managed settings — Teams/Enterprise)

Admin: **claude.ai → Admin Settings → Claude Code → Managed settings.** Paste:

```json
{
  "extraKnownMarketplaces": {
    "signata": {
      "source": { "source": "github", "repo": "Signata-GmbH/signata-swe-claude-skills" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "signata-swe-claude-skills@signata": true
  }
}
```

- The marketplace source is specified **inline** — no separate registry key needed.
- Marketplace + plugin are **auto-installed and auto-enabled** for every member on
  next authentication; settings refresh hourly. Nobody runs an install command.
- Changes are recorded in the org **audit log**.

**Pin a version org-wide** (optional, for reproducibility) by pinning the
marketplace to a git ref instead of tracking the branch tip:

```json
"signata": {
  "source": { "source": "github", "repo": "Signata-GmbH/signata-swe-claude-skills" },
  "ref": "signata-swe-claude-skills--v0.0.1"
}
```

(Self-service alternative, any plan: an engineer runs
`/plugin marketplace add Signata-GmbH/signata-swe-claude-skills` then
`/plugin install signata-swe-claude-skills@signata`.)

---

## C. Updating the skills (e.g. refining the UT approach from a validation report)

The **skill is now canonical**; `20_AI/prompts/` is provenance. To ship a change:

1. **Edit the skill file** in the plugin repo — a test-design refinement lands in
   `skills/_shared/common/unittest-design.md`; a workflow/governance change in
   `workflow-discipline.md`; a flavor change in `autosar/` or `generic/`.
2. **Bump `version`** in `.claude-plugin/plugin.json` (semver: patch = tweak,
   minor = new behavior, major = breaking).
3. `claude plugin validate . --strict`
4. `claude plugin tag . --push --message "Release %s"`
5. The org **auto-updates** on the next hourly refresh (with `autoUpdate: true`);
   or, if pinned by `ref`, bump the `ref` in managed settings.

The version flows into each run's ledger (`skill_version`), so every generated
`.tst` / review / implementation is **traceable to the exact skill version** that
produced it — e.g. "this suite came from UT-skill v1.1 after the validation-report
refinement."

---

## D. What each PRODUCT repo commits (e.g. CEA)

| File | Commit? | When / where |
|---|---|---|
| `20_AI/ai_project.yaml` | ✅ **once, to `develop`** | Scaffold on first skill run, review, commit → every branch inherits the same compiler/layout/variants/doc paths |
| `20_AI/manifests/<MODULE>.yaml` + `history/*.jsonl` | ✅ per module | In that module's PR — these are the audit/traceability ledgers |
| Input docs (requirements, signals&params, SDD, guideline, checklist) | **decision** | Commit if size/licensing allows so paths resolve for everyone; else keep in a shared location and let the fail-closed gate prompt |
| `.claude/skills/` | ❌ **never on product branches** | The plugin provides the skills; a committed copy would *shadow/conflict* with the installed plugin (project skills override plugin skills) |

**Rollout procedure (run once in the base branch):**
1. On `develop`, scaffold + commit `20_AI/ai_project.yaml`.
2. Add to the repo README/CONTRIBUTING: "The `signata-swe-claude-skills` plugin is
   installed org-wide; `ai_project.yaml` is committed — run `/unit-test <MODULE>`,
   `/code-review <MODULE>`, `/code-dev <MODULE>`."
3. Everyone branching off `develop` inherits `ai_project.yaml`; manifests accrue
   per module.

> ⚠️ The current `MQBST2-AI-Skills-Development` branch (skills in `.claude/skills/`)
> is the **dev staging area** — its content seeds the plugin repo. Do **not** merge
> `.claude/skills/` into `develop`; only `20_AI/ai_project.yaml` (+ manifests) belong
> in the product repo.
