# Test-spec workflow discipline (both DOORS test-generation skills)

> Loaded by `integration-test` (SWE.5) and `qualification-test` (SWE.6). This is
> the shared backbone for that pair — the same role
> [../common/workflow-discipline.md](../common/workflow-discipline.md) plays for
> the three SWE.3 code skills, rewritten for a domain with no source code, no
> compiler, and no git-SHA build to pin against. The two files are not merged:
> the pinning mechanism (§2 below) and the input matrix (§1) are genuinely
> different here.

## 0. Standalone & idempotent — NO pipeline assumption

- Either skill may be the first (and only) one ever run in this vTestStudio
  project folder. Never assume the other one ran first.
- On every run, ensure `20_AI/ai_test_project.yaml` and the module/feature
  manifest exist. The **project config** is per-repo and belongs on the base
  branch — a missing one goes through
  [project-config.md](project-config.md) §7. The **manifest** is per-module
  (`integration-test`) or per-feature (`qualification-test`) — scaffold +
  confirm it here (§3).
- `integration-test` and `qualification-test` never share a manifest — a module
  name and a feature name are different axes and can collide as strings
  (`Motor Control` the feature vs. a module named similarly), so their manifests
  live in separate directories (§3).

## 1. Pre-flight & input acquisition (before any analysis) — FAIL-CLOSED

### 1.1 Required inputs

| Document (config/manifest key) | integration-test (SWE.5) | qualification-test (SWE.6) |
|---|:--:|:--:|
| Architecture export (`docs.architecture_export`) | ✔ | – |
| Requirements workbook (`docs.requirements_workbook`) | – | ✔ |
| Signals & Parameters (`docs.signals_params`) | where signal values are exercised | ✔ |
| Existing test-spec export for this module/feature | ✔ | ✔ |
| ARXML / `Rte_*.h` / `Rte_Type.h` | only for interfaces with no existing test cases | – |
| A2L file or code variable list (`docs.a2l_or_varlist`) | – | ✔ |
| DiagSpec (`docs.diagspec`) | – | diagnostic features only |

✔ = mandatory · **ask** = optional but must be **explicitly offered** at the
gate · – = not applicable to this skill. Any document may be **`.pdf` or
`.xlsx`**.

### 1.2 Fail-closed acquisition loop

**Never self-substitute or self-waive.** Do not set a document to `N/A` on your
own reasoning, and never treat one document as fulfilling another's role. Only
an **explicit engineer decision at this gate** resolves a missing input.

For each required input, in order: resolve its path from config/manifest to a
real, readable file → if missing/unreadable, **explicitly ask** the engineer to
provide it (path or attach), then write the answer back (project-wide →
`ai_test_project.yaml`; per-module/feature → the manifest) → mandatory and not
provided is a **hard STOP**, reporting which one and why.

Emit a pre-flight table: `input | required? | resolved path | present &
readable? | acquisition outcome`. **Never emit a workbook while a mandatory
input is unresolved.**

## 2. Baseline pinning (the audit spine — no source code, no git SHA)

There is no compiler and no build here, so the equivalent of revision pinning
is:

- **`release.id` + `release.variants`** from `ai_test_project.yaml` — every test
  case's `atsRelease`/`aVariant` attribute is valid only at that baseline.
- **A content hash of every supplied input file**, via `git hash-object
  <file>` (the same primitive the SWE.3 skills use for blob hashes — it works
  on any file, tracked or not, as long as you're inside a git working tree).
  Record `{file: hash}` for every DOORS export/xlsx read this run.
- **Per-requirement/per-interface hash** — hash each in-scope requirement's or
  interface's Object Text, so a later run can tell *new* from *changed* from
  *unchanged* (§8) without re-reading the whole export.

Carry all of this into the ledger (§8). A wrong release/variant produces test
cases that look plausible but assert the wrong baseline — treat a mismatch the
same way a wrong git SHA is treated in the SWE.3 skills: as invalidating.

## 3. Manifest: scaffold → validate → confirm (HARD GATE)

- **integration-test** → `20_AI/manifests/integration-test/<MODULE>.yaml`,
  scaffolded from
  [integration-test-manifest-template.yaml](integration-test-manifest-template.yaml).
- **qualification-test** →
  `20_AI/manifests/qualification-test/<FEATURE_SLUG>.yaml`, scaffolded from
  [qualification-test-manifest-template.yaml](qualification-test-manifest-template.yaml).
  `FEATURE_SLUG` = the `aFeature` value lowercased, every run of
  non-alphanumeric characters collapsed to a single `_` (documented in the
  skill since several feature names carry spaces/brackets, e.g.
  `Diagnostic - Identification [SID 0x22] [SID 0x2E]` → `diagnostic_identification_sid_0x22_sid_0x2e`).

Both manifests **inherit** `ai_test_project.yaml` (`release`, `variants`,
`attributes`, `docs.*`) — never duplicate those fields in the manifest.

- If the manifest is **absent**: derive what you can, discover per-module/
  per-feature documents (existing test cases for this module/feature) by
  globbing under `docs.root`, scaffold from the template, and **present it for
  confirmation**.
- If **present**: validate required fields; flag/repair anything malformed
  rather than proceeding on it.
- **Scope-count gate (mandatory).** After applying the scope filter (§4 of the
  relevant patterns file), report the resulting count and **require the
  engineer to confirm or enter the expected count** before proceeding — persist
  it as `expected_row_count`. Never silently learn it; a mismatch on a later run
  halts (§8).
- **STOP and wait for confirmation** before doing any work.

## 4. Grounding & no silent assumptions

- **Symbol/value grounding.** Every `Rte_` symbol, source file name, signal
  name, DID/RID/NRC, enum value, and numeric threshold used in a test case is
  copied **verbatim** from a supplied input — never fabricated, and never
  constructed by analogy with a similar-looking symbol that does exist.
  Self-check before emitting; list any symbol you cannot confirm and **stop**
  rather than guess.
- **Discover before define.** Before treating a project fact as fixed
  (`integration_test.module_name_mapping`, `qualification_test.valid_features`,
  the `CLASSIFICATION_RULE` a case falls under), check whether it is already
  cached in `ai_test_project.yaml` and reuse it; if not yet cached, derive it
  with evidence and offer to cache it for next time (§4.2 of
  [project-config.md](project-config.md)).
- **No silent assumptions.** Every ambiguity, mismatch, or gap becomes a
  numbered Phase-1 question **or** an Open Points row — never a silent guess.

## 5. Phase-1 questions → workbook (offline-answerable)

Identical mechanism to `common/workflow-discipline.md` §5: write numbered
questions to `20_AI/<MODULE_or_FEATURE_SLUG>_Phase1_Questions_<Skill>.xlsx`
(`<Skill>` = `IntegrationTest` / `QualificationTest`), one row each:
`QID | Requirement or Interface | Question | AI Proposal | Answer(blank) |
Status(open)`. If the workbook already exists, read it back first — rows with a
non-empty `Answer` (or `Status` = `answered`/`deferred`) are resolved; re-emit
only still-`open` rows under their existing `QID`s. Every question cites the
source document + row/section it rests on.

## 6. Self-check before output

Run every item, report the result, fix before output or list as an Open Points
row:

1. Every mandatory attribute filled, values from the allowed set.
2. Every concrete test case linked to a requirement/architecture object, or
   `atsReference` populated with a stated origin.
3. Actions and results numbered and correspond; exactly one pass/fail result
   marked per case.
4. No two test cases distinguishable only by title.
5. Every symbol, file name, and value traceable to a supplied input — report
   the source of each.
6. Positive/negative balance reported per requirement or interface; flag any
   with no negative case.
7. `atsState` = `in work` and `ID` empty on every row.
8. Every in-scope requirement/interface either has a test case or appears in
   Open Points with a reason.

## 7. Traceability & Open Points (both skills, every run)

Every generated workbook carries the 3-sheet contract from
[output-format.md](output-format.md): `Test Cases`, `Traceability` (one row per
generated case — the engineer creates the DOORS links from this sheet by hand,
so it must be complete and readable on its own), `Open Points` (every
unresolved symbol/value, every classification judgement, every requirement/
interface you could not cover and why, every spelling variant normalized).

## 8. Ledger & run history (audit)

Same two-record shape as `common/workflow-discipline.md` §9, adapted to this
domain's pin:

- **`last_run:` in the manifest — working state, overwritten each run.** Holds
  `timestamp`, `skill_version`, `release_id`, `variants`, `input_hashes` (§2),
  the requirement/interface snapshot (`ID -> {hash, cases: [...]}`), and the
  delta. Drives re-runs; not history.
- **`20_AI/manifests/{integration-test,qualification-test}/history/<KEY>.jsonl`
  — append-only audit trail.** After each run, **append** one immutable record
  (never edit prior lines): `{ts, skill, skill_v, release_id, variants,
  input_hashes, reqs_delta:{added,updated,removed}, notes}`.

**In-place re-run**: recompute each in-scope requirement's/interface's hash and
compare to `last_run`:
- **new** (ID absent) → author the test case(s), append.
- **changed** (hash differs) → **update the mapped test case(s) in place**
  (keep title/history stable), tag revised.
- **removed** (was present, now absent) → **flag it; never silently delete** —
  surface the orphaned case for the engineer to decide.
- **unchanged** → leave untouched.
Show the delta and **confirm before writing**.

## 9. No fabrication

See [no-fabrication.md](no-fabrication.md). No DOORS write access and no test
execution happen here — never claim a result you did not produce, and never
write to DOORS yourself.
