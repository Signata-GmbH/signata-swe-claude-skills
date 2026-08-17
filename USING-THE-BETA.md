# Using the SWE AI Skills — Beta (v0.0.1)

Three Claude Code skills for our AUTOSAR **and** non-AUTOSAR firmware projects. They
replace the old copy-paste prompts. **This is a beta** — please try them on real
modules and report what breaks.

## What you get

| Command | Does |
|---|---|
| `/code-dev <MODULE>` | Implement a module (or a feature in one) from its requirements + an Implementation Review doc. Two-phase: analysis & questions first, code only after you approve. |
| `/code-review <MODULE>` | Formal SWE.3 review of the user-implemented C → a populated Findings List, with the checklist walked. |
| `/unit-test <MODULE>` | Generate / update a VectorCAST `.tst` suite from requirements + code, with an auditable requirement→case ledger. |

Each skill **adapts automatically** to whether the repo is AUTOSAR or non-AUTOSAR.

## Getting it

It's pushed to everyone via Claude admin settings — you should just see
`/code-dev`, `/code-review`, `/unit-test` in the `/` menu. If not, **reload the
window**. (Self-install alternative: `/plugin marketplace add
Signata-GmbH/signata-swe-claude-skills` then `/plugin install
signata-swe-claude-skills@signata`.)

## Using it

1. Open Claude Code at your **repo root** and run e.g. `/unit-test FUSA_PosDet`.
2. **First run in a repo** scaffolds `20_AI/ai_project.yaml` and asks you to confirm
   a couple of things it can't derive (compiler, target). Commit that file once to
   `develop` — everyone then shares it.
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
