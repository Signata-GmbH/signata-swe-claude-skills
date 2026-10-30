# Test-spec workflow discipline (both DOORS test-generation skills)

> Loaded by `integration-test` (SWE.5) and `qualification-test` (SWE.6). This is
> the shared backbone for that pair — the same role
> [../common/workflow-discipline.md](../common/workflow-discipline.md) plays for
> the three SWE.3 code skills. Both skills run in the SWE.3 project repository
> (project-config.md §1) but never build it and never read its source code:
> every input — DOORS export, ARXML, RTE header, A2L, database — is pinned by
> content hash. The two files are not merged: the pinning mechanism (§2 below)
> and the input matrix (§1) are genuinely different here.

## 0. Standalone & idempotent — NO pipeline assumption

- Either skill may be the first (and only) test-spec skill ever run in this
  repository. Never assume the other one ran first, and never assume a code
  skill ran first either.
- **Neither skill reads the source code.** Both run in the SWE.3 repository,
  where the code is within reach, and neither opens it. `integration-test`'s
  test basis is the architectural design — the DOORS export, the ARXML and the
  RTE headers generated from it (integration-test-patterns §9);
  `qualification-test`'s is the requirements (qualification-test-patterns §0).
  An expected result, a breakpoint or a variable name derived from the code
  would test the code against itself.
- On every run, ensure `20_AI/ai_test_project.yaml` and the module/feature
  manifest exist. The **project config** is per-repo and belongs on the base
  branch — a missing one goes through
  [project-config.md](project-config.md) §7. The **manifest** is per-module
  (`integration-test`) or per-feature (`qualification-test`) — scaffold +
  confirm it here (§3).
- **Per-skill working folder.** As soon as the module/feature is known, ensure
  `20_AI/<Skill>/<MODULE_or_FEATURE_SLUG>/` exists (`<Skill>` =
  `IntegrationTest` / `QualificationTest`; create it with a `.gitkeep` if
  empty). The Phase-1 questions (§5), the test-case workbook and any
  module/feature-specific input the engineer supplies live there; never write
  them directly under `20_AI/`.
- `integration-test` and `qualification-test` never share a manifest — a module
  name and a feature name are different axes and can collide as strings
  (`Motor Control` the feature vs. a module named similarly), so their manifests
  live in separate directories (§3).

## 1. Pre-flight & input acquisition (before any analysis) — FAIL-CLOSED

### 1.1 Required inputs

| Document (config/manifest key) | integration-test (SWE.5) | qualification-test (SWE.6) |
|---|:--:|:--:|
| Functional_Architecture export (`docs.functional_architecture_export`) — includes its UserDefinedTypes chapter | ✔ | – |
| Its second view (`docs.functional_architecture_export_text_view`) | only when one export cannot carry both name and text (§1.3) | – |
| Requirements workbook (`docs.requirements_workbook`) | – | ✔ |
| Signals & Parameters (`docs.signals_params`) | where a signal's raw values are exercised | ✔ |
| Existing test-spec export for this module/feature | ✔ under `integration_test.authoring_mode: extend_existing` · – under `from_scratch` (integration-test-patterns §0.1) | ✔, unless `N/A` by a recorded engineer decision (§1.2) |
| ARXML — software-component descriptions and composition (`docs.arxml`) | ✔ — ports, connectors, runnable symbols and events, checkpoints, types (integration-test-patterns §9) | – |
| RTE headers `Rte_<Swc>.h` / `Rte_Type.h` (`docs.rte_type_headers`, or `layout.rte_inc` in `ai_project.yaml`) | ✔ — the spelling of every RTE symbol and every enum literal | – |
| The source code, the OS configuration, the build (ELF / map) | **never** — the test basis is the architecture; breakpoints are named by symbol and module (integration-test-patterns §9) | **never**, with one exception: a search for the **name only** of a fault-injection variable the A2L does not settle (qualification-test-patterns §0) |
| A2L file or code variable list (`docs.a2l_or_varlist`) | – | ✔ |
| DiagSpec (`docs.diagspec`) | diagnostic interfaces (pattern P-07) only | diagnostic features only |
| Communication database — DBC / LDF / ARXML system extract (`docs.comm_database`) | **ask** — decodes the bus and gives the message attributes for the basic-software patterns (integration-test-patterns §7, P-10); without it, P-10 cases name the I-PDU from the ARXML and every signal value, cycle and timeout is an Open Point | **ask** — every bus signal's encoding, cycle time and timeout; without it those values are Open Points |
| Test Plan (`docs.test_plan`) | – | **ask** — Series SW or Debug SW per feature (`atcRemark`); without it, asked once per feature |
| Test environment description (`docs.test_environment`) | **ask** | **ask** — what the bench can stimulate and observe (§4), including the CANoe configuration's panel list; without it, every means is asked in the Phase-1 catalogue (qualification-test-patterns §3.2) |
| Reference specifications (`docs.reference_specs`) — OEM performance or test specifications, standards | – | ✔ for a feature listed in `qualification_test.spec_governed_features` — the named specification defines the behaviour (E2E, network management, diagnostics) and a run without it stops (qualification-test-patterns §3.1) · **ask** otherwise, at every run, for each document the in-scope requirements cite that is not registered; without one, the requirements depending on it are Open Points |

**The two SWE.5 test-basis documents are not interchangeable with the SWE.6
one.** `integration-test` reads the Functional_Architecture export and never
the SW requirements export — an SWE.5 test case traces to an architecture
object (a component, a port, a runnable), not to a software requirement. A
requirements workbook offered in place of a missing architecture export is
refused at this gate, and vice versa for SWE.6.

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

**A recorded `N/A` is resolved, not missing.** A document the config sets to
`N/A` by a recorded engineer decision — the reason written beside it, or an
explicit mode such as `integration_test.authoring_mode: from_scratch` — is
**resolved** for this gate. Do not re-open it by discovery. If a file turns up
that looks as if it fills that role, do **not** register it, read it, or cite
it: raise one Phase-1 question quoting the recorded decision, and proceed under
the decision until the engineer changes the config. The one exception is a
skill's **test basis** (the Functional_Architecture export for SWE.5, the
requirements workbook for SWE.6): a run without it has nothing to trace to, so
`N/A` there is still a hard STOP.

**Never auto-adopt a discovered file.** Discovery (globbing under `docs.root`)
is only for inputs whose config entry is **unset**, and what it finds is a
**proposal** the engineer confirms at the gate — never registered on the
strength of a filename or a matching column schema. A wrong existing-spec export
contaminates the coverage baseline, the name mapping and every finding built on
them.

Emit a pre-flight table: `input | required? | resolved path | present &
readable? | acquisition outcome`. **Never emit a workbook while a mandatory
input is unresolved.**

### 1.3 Export-completeness gate (an xlsx that opens is not an xlsx that is usable)

A DOORS export can be readable and still be missing the columns or the content
the run depends on, because the view it was taken from omitted them. Check
every supplied export **before** any analysis and report the result in the
pre-flight table.

**1. Columns present.** Every attribute the patterns file reads must exist as a
column — for the Functional_Architecture export: `ID`, `aFunctionModule`,
`aFeature`, `aTestCriteria`, `aTestability`, `aRequirementObjectType`,
`aStatusOfAnalysis`, `aVariant`; for the requirements workbook: `ID`,
`aFeature`, `aTestCriteria`, `aTestability`, `aRequirementObjectType`,
`aStatusOfAnalysis`, `aVariant`. A missing column is a **hard STOP**: name the
column, say which DOORS view carries it, and ask for a re-export. Never
reconstruct a missing attribute from another column.

The `aC_SAF`/`aC_SEC`/`aC_REG` columns are **not** on that list. A configured
classification rule (`attributes.classification_attribute_rules`) needs only
the one column its condition reads, and only in the running skill's test-basis
export. If that column is missing there, the rules that read it are **skipped
for this skill**: the cases they would have classified are classified by
judgement, as without rules, and one Open Point names the missing column and
the skipped rules. Classification can always be done by hand, so a missing
classification column never stops the run. *(Known: the SW requirements export
carries `aC_SAF`; nothing yet shows that it carries `aC_SEC` or `aC_REG`.)*

**2. Name *and* text available per object — the two-view trap.** Every object
carries two things this skill needs:

- its **name** (`Object Heading`) — module, port, data-element, type and
  struct-member names, and the `P_`/`R_` direction prefix;
- its **text** (`Object Text`) — the port-direction prose, the `DataType:` line,
  the `Range:` line.

DOORS views deliver them in one of three shapes. Detect the shape from the
**content**, not the column name, and report `objects | with name | with text |
with both` whichever it is:

- **(a) Two columns** — `Object Heading` and `Object Text` side by side.
  Preferred.
- **(b) One column carrying both** — a single content column (often named after
  the module, e.g. `Architecture Document`) whose cell holds
  `<section> <heading>` on its first line and the object text on the lines
  after it. Split each cell on its **first newline**: line 1 is the name where
  it reads `<section number> <name>`, the remainder is the text. Expect
  heading-only and text-only objects as well (DOORS numbers text-only objects
  `<n>.0-<k>`); count them, never drop them. The signal is unmistakable: the
  text markers (`This port`, `DataType:`, `Range`) appear throughout a
  shape-(b) export and in no cell of a heading-only one.
- **(c) Two views of the same module**, each a single content column — one
  carrying the headings, one the text — joined on `ID`
  (`docs.functional_architecture_export` + `_text_view`). Verify the join
  before using it — identical `ID` sets, same baseline. A differing `ID` set
  means the two views are different baselines: **hard STOP**.

A single column carrying only the *text* has no port, type or member names:
**hard STOP**, asking for the heading view.

**A single column carrying only the *names* — check before stopping.** The
text's job is partly done by inputs the run may already hold, so before
declaring the STOP, check them and put the result in the stop message:

| The text would have supplied | Already resolved by | Still lost |
|---|---|---|
| port direction prose | the `P_`/`R_` prefix, settled by ARXML `P-PORT-PROTOTYPE`/`R-PORT-PROTOTYPE` | nothing |
| the `DataType:` line | the ARXML port interface's data element type | nothing |
| the documented `Range:` | ARXML `DATA-CONSTR`, where the type has one | the **architect's documented range** wherever the ARXML has no constraint — Min/Mid/Max then fall back to the type limits (`0/127/255` where the architecture would have said e.g. `0/50/100`) |

Offer "proceed names-only" as the **AI proposal**, listing for each in-scope
interface where its Min/Mid/Max would come from — but leave the decision to the
engineer: the ranges that change are exactly the quiet wrong answer this gate
exists to prevent. Record an acceptance as
`integration_test.architecture_text_fallback: arxml` in `ai_test_project.yaml`
so later runs do not re-ask; it is ignored as soon as an export carries the
text. In a names-only run, every Min/Mid/Max states in Traceability that the
documented range was not available, and Open Points lists the interfaces that
fell back to the type limits. *(Observed: a run stopped on a names-only export
when the ARXML already held every type, member and literal the run needed; the
engineer had to ask whether the stop was the export's fault or the skill's.)*

**3. Table content survived.** DOORS tables are the first thing an export
loses; the symptom is a block of rows whose content column is empty while their
attribute columns are filled. Count those rows and report the count. If a type
definition an in-scope interface depends on is among them, **hard STOP** and ask
for a re-export rather than inventing a member name or a limit.

**4. Known gap, not a stop: enum literals.** In the architecture module an enum
type is a single object with no children and no literal list — the literals
(`MOT_MOV_ROT_FWD_E`) exist only in `Rte_Type.h`/ARXML and in the existing
test-spec export. Their absence from the architecture export is therefore
expected and does **not** stop the run: resolve them from
`docs.rte_type_headers`, then (in `extend_existing` mode only) from existing
cases, and put an enum interface with no resolvable literals on Open Points
(integration-test-patterns §5.2).
Report which source each literal came from.

This gate is fail-closed like §1.2: only an explicit engineer decision
downgrades a STOP, and the decision is recorded in the run summary and in Open
Points.

### 1.4 Input placement — keep `20_AI/` uncluttered

Two homes, nothing else directly under `20_AI/` besides `ai_project.yaml` (and
`ai_test_project.yaml`), `manifests/` and the skill folders:

- **Project-wide reference documents** (SW requirements, Signals & Parameters,
  architecture, guidelines, checklists, …) → `20_AI/Shared/`. Large archives
  that are gitignored for size (e.g. the CANoe configuration `.zip`) →
  `20_AI/Shared/CANoe/`.
- **Module/feature-specific files** (extra inputs, existing test-spec exports,
  Phase-1 workbooks) → `20_AI/<Skill>/<MODULE>/` (see §0).

After the pre-flight table is resolved, for every input the config/manifest
**already names** (or this run just had confirmed), if the file sits outside its
home — typically directly under `20_AI/` — **move it** there before continuing:

- `git mv` when tracked, a plain move otherwise (an untracked or gitignored file
  stays untracked/ignored). Never copy and leave a duplicate.
- Never overwrite: if the destination exists, leave both and ask.
- Only files inside `20_AI/` of this repository; a path outside it is never moved.
- Update the config/manifest path to the new location. The project config is
  shared and lives on the base branch: say that the path change must be merged
  there (do not silently commit it).
- **Notify the user** with one line per file: `moved <old> → <new>`. A file that
  is merely *discovered* and not yet confirmed is not moved — §1.2's
  never-auto-adopt rule still applies.
- Ensure `20_AI/Shared/CANoe/` is gitignored (`20_AI/Shared/CANoe/*` plus
  `!20_AI/Shared/CANoe/.gitkeep`) before a CANoe archive is placed there; add the
  `.gitignore` lines if missing and say so.

## 2. Baseline pinning (the audit spine)

There is no compiler and no build here, and the DOORS exports carry no git SHA,
so the equivalent of revision pinning is:

- **`release.id` + `release.variants`** from `ai_test_project.yaml` — every test
  case's `atsRelease`/`aVariant` attribute is valid only at that baseline.
- **A content hash of every supplied input file**, via `git hash-object
  <file>` (the same primitive the SWE.3 skills use for blob hashes — it works
  on any file, tracked or untracked, inside a repository or outside one, so a
  document kept outside Git is pinned the same way). Record `{file: hash}` for
  every DOORS export/xlsx read this run.
- **The ARXML and the RTE headers, by content hash** (`integration-test`) —
  `git hash-object` on every `.arxml` and `.h` read, like any other input.
  Generated headers carry generator timestamps, so two copies can differ by
  bytes while exporting the same symbols: compare symbol sets
  (integration-test-patterns §9) and pin the copy actually read. No source
  revision is recorded, because no source file is read.
- **Per-requirement/per-interface hash** — hash each in-scope requirement's or
  interface's Object Text, so a later run can tell *new* from *changed* from
  *unchanged* (§8) without re-reading the whole export. An **interface's** hash
  covers every object its cases are built from, not only the port: the port,
  its data-element child, and the `1.2` type and member objects its values
  resolve through. A range changed in the UserDefinedTypes chapter changes the
  Min/Mid/Max of every interface using that type, so it must register as a
  changed interface, not slip through as "unchanged".
- **Re-hash immediately before generation**, not only at pre-flight. An input
  can change mid-session — a new export dropped into the folder between Phase 1
  and Phase 2 is common — and the analysis the engineer approved is valid only
  for the files it was made from. Re-run `git hash-object` on every input
  right before Phase 2; any difference from
  the pre-flight pin is a **STOP**: name the file, and redo the affected part of
  Phase 1 rather than generate from a mixed baseline.

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

- **The target is the primary input.** `integration-test` takes a **module**,
  `qualification-test` a **feature**, as the command argument — the same way
  the SWE.3 skills take their module. If it was not given, ask for it **before
  anything else** (before the config, before any export), as a typed answer:
  only the engineer knows it. Never infer it from the folder — an existing
  manifest, the last run, a file name, a document lying in `20_AI/` — not even
  when only one candidate exists. The manifest path is derived from it, so
  nothing module- or feature-specific is read until it is known. A module given
  to `qualification-test`, or a feature given to `integration-test`, is said to
  be the other axis (§0) and asked again, never run.
- Collect the other inputs the friendly way: **`AskUserQuestion` popups** for
  categorical choices; **discovery → popup** when a glob finds several
  candidate documents (pick one); typed values only for the genuinely
  unknowable — the module or feature name, a release id, a path discovery
  missed.

- If the manifest is **absent**: derive what you can, discover the
  per-module/per-feature documents **whose config entry is unset** (§1.2) —
  existing test cases for this module/feature, but never under
  `integration_test.authoring_mode: from_scratch` — by globbing under
  `docs.root`, scaffold from the template, and **present it for
  confirmation**, every discovered document marked as a proposal.
- If **present**: validate required fields; flag/repair anything malformed
  rather than proceeding on it.
- **Classification rules in an older config.** If `ai_test_project.yaml` has no
  `attributes.classification_attribute_rules` key at all, it was created before
  the setting existed and the question has never been asked. Ask it once, at
  this gate (project-config.md §4.1), and write the answer back — `[]` when the
  answer is "none" — so no run asks it again. The key missing means *not asked
  yet*; `[]` means *asked, no rules*. Until it is answered, classify by
  judgement as before. It is a project-wide answer: say that the config change
  must reach the base branch, like any other config change.
- The **row-count gate** is not part of this gate: it closes Phase 1 (§5),
  because a count only means something once the scope analysis is on the table.
- **STOP and wait for confirmation** before doing any work.

## 4. Grounding & no silent assumptions

- **Symbol/value grounding.** Every `Rte_` symbol, runnable name, module
  name, signal name, DID/RID/NRC, enum value, and numeric threshold used in a
  test case is
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
- **Record who said it.** Every answer that settles a value, a mapping or a
  decision is recorded with its source, in the same words wherever it
  appears (config comment, manifest, Traceability, Open Points): *QA in the
  workbook* (`QA <date>, Q-nn` / the validity reason), *engineer relaying QA*
  (`QA via engineer <date>`), *engineer's own decision* (`engineer <date>`),
  or *AI proposal accepted by …*. A value the engineer picked from an AI
  proposal is never recorded as QA's; when QA later confirms it, the record
  gains `confirmed by QA <date>` — it is not rewritten as if QA had proposed
  it (no-fabrication.md).
- **Executable on the bench.** Every case stimulates something and observes
  something — a debugger breakpoint and variable, an XCP measurement, a bus
  signal, a diagnostic request, a HIL I/O channel. With
  `docs.test_environment` supplied, check each case's means against it: a case
  that needs a means the bench does not have is listed in Open Points and, where
  the validity columns are configured, marked `isValid = No`
  (no-fabrication.md) — it cannot be run as written. Without it, list once in
  Open Points which means the run assumed, so the engineer can check them in
  one place. This matters more once scripts are generated (v2): a script that
  names a signal or channel the bench lacks fails on the first line.

## 5. Phase-1 questions → workbook (offline-answerable)

Identical mechanism to `common/workflow-discipline.md` §5: write numbered
questions to `20_AI/<Skill>/<MODULE_or_FEATURE_SLUG>/<MODULE_or_FEATURE_SLUG>_Phase1_Questions_<Skill>.xlsx`
(`<Skill>` = `IntegrationTest` / `QualificationTest`), one row each:
`QID | Requirement or Interface | Question | AI Proposal | Answer(blank) |
Status(open) | Note`. If the workbook already exists, read it back first — rows
with a non-empty `Answer` that maps to one outcome (below), or `Status` =
`answered`/`deferred`/`withdrawn`, are resolved; re-emit only still-`open`
rows under their existing `QID`s. Every
question cites the source document + row/section it rests on.

**`withdrawn`** — a question a later ruling made moot (a scope change, an input
ruled out) is **withdrawn**, never deleted: set `Status = withdrawn`, write in
`Note` which answer or decision withdrew it, and grey the row out. Deleting it
would erase the record of why the analysis changed. A withdrawn question is not
re-emitted, and a finding that rested on it is withdrawn with it (and says so in
Open Points).

**One question per QID.** A question containing a "SECOND ISSUE", an "also", or
any two things a reader could answer separately must be split into two QIDs.
Engineers answer in three words — "note it only", "yes", "ok" — and a
three-word answer cannot be mapped back onto a two-part question. The skill has
no licence to choose which part it answered. If an answer arrives that does not
resolve every part of its question, re-emit the unresolved part as a **new
`open` QID** rather than inferring, and say in Open Points that you did.

Observed failure (FUSA_MotDrv Q-13, 2026-09-24): one QID asked both "P-08 or
P-03 for the watchdog checkpoints?" and "SECOND ISSUE: they carry
`aFunctionModule = WdgM` although they sit under the `FUSA_CDD_MotDrv`
section", and the written explanation of it ENDED on that second part, which
was itself framed as "independent of your answer" and "reported as an Open
Point regardless". The answer "note it only" was applied to the first part and
the two test cases were suppressed; the engineer had meant the second, and
rejected the result at validation three weeks later.

Corollary: **end a question on the thing you are asking**, not on background
you have already said you will handle anyway. Whatever a question closes with
is what a short answer attaches to.

**A short answer must have exactly one meaning.** Engineers answer most rows
with "Yes", "No" or "ok", so write every question so that such an answer maps
to one outcome:

- **Every `AI Proposal` is concrete** — a value, a name, a mapping, a
  decision — and the question is phrased so that **"Yes" accepts it**. Never
  write "No proposal", and never a proposal that defers the content ("derived
  on the bench — you confirm the factor", "value given by you"): a "Yes" to it
  settles nothing.
- **Where the AI cannot propose, list the options** in the question
  ("A: `<x>`, B: `<y>`, C: unknown → Open Point") and the proposal names one of
  them, with the reason. An open "Which …?" with no options gets answered "Yes".
- **One yes/no per question, and "No" must mean the opposite of the
  proposal.** "Is there a means for X, or does it go to Open Points?" has two
  readings of "No"; ask "Proposal: X goes to Open Points (no means known).
  Accept?" instead.

*(Observed, one SWE.6 Phase-1 round: of 49 questions, five got "Yes" to a
"Which …?" whose proposal was "No proposal" or deferred the value, and four got
"No" to an either/or question. Each one needed a follow-up before generation.)*

**Check the answers before Phase 2.** A non-empty `Answer` resolves its row
only if it maps to one outcome under the rules above. Before generating:

1. **Unresolved answers** — a "Yes" to an open question, an answer to only one
   of its parts, a value with no unit — are listed, not interpreted.
2. **Contradicting answers** — two answers that cannot both hold on the same
   case (one puts a function on the Series software, another expects it absent
   there) — are listed with both QIDs.
3. If any item in 1–2 changes a case's stimulus, expected value, software or
   direction, **ask it now** (a popup, when the engineer is present) — never
   generate a case from one reading of it. Items that only touch an Open Point
   are re-emitted as new `open` QIDs and generation proceeds.
4. Record each follow-up answer in the row's `Note` with its source (§4), and
   leave the engineer's `Answer` cell as they wrote it.

The **catalogue's `Answer` column** is the engineer's too: it is left empty
for them — a cached row says so in `Status`/`Source`, never in `Answer`
(qualification-test-patterns §3.2).

**qualification-test adds a second sheet, `Catalogue`** — the stimulus and
observation means, one row per item, each answered on its own
(qualification-test-patterns §3.2). Its rows are read back like the questions:
answered rows are resolved, only `open` ones are re-emitted.

**qualification-test adds a third sheet, `Requirements Hygiene`** — one row
per defect found in the inputs themselves (a requirement status that lags the
software, a parameter or tolerance that differs between documents, a cited
specification that is missing), with the owner it goes to
(qualification-test-patterns §12). These rows are findings, not questions: a
row becomes a Phase-1 question only where it changes a case's value, and then
the question carries a concrete proposal as usual. The sheet is mirrored into
the final workbook's Open Points under `Input hygiene`.

**The proposed-cases table carries each case's scenario family**
(qualification-test-patterns §10) and, for a timing case, the database
attribute it measures (§11), so the engineer can see at the gate which
families the run covers and which it says do not apply.

**Row-count gate (mandatory — the last Phase-1 question).** After the
proposed-cases table, state how many rows the `Test Cases` sheet will have —
heading rows and case rows, counted from that table — and require the engineer
to confirm it or enter their own; "accept the AI proposal" is a valid answer.
Persist the answer as `expected_row_count`. Never learn it silently; on a later
run with unchanged scope a mismatch halts (§8). Two things this replaces: the
count used to be asked at the manifest gate, before the scope had been
analysed, so the engineer was asked to predict a number nobody had seen yet;
and it counted the objects the scope filter selected, while
`expected_row_count` holds rows of the output.

## 6. Self-check before output

Run every item, report the result, fix before output or list as an Open Points
row:

1. Every mandatory attribute filled, values from the allowed set.
2. Every concrete test case linked to a requirement/architecture object, or
   `atsReference` populated with a stated origin.
3. Actions and results numbered and correspond. integration-test: exactly one
   pass/fail result marked per case. qualification-test: one result per
   action, every result a check, no placeholder result and no pass/fail marker
   (qualification-test-patterns §7).
4. No two test cases distinguishable only by title.
5. Every symbol, file name, and value traceable to a supplied input — report
   the source of each.
6. Positive/negative balance reported per requirement or interface; flag any
   with no negative case. For qualification-test, the out-of-range steps of a
   stepped case (qualification-test-patterns §6) count as its negative
   coverage.
7. `atsState` = `in work` and `ID` empty on every row.
8. Every in-scope requirement/interface either has a test case or appears in
   Open Points with a reason.
9. **integration-test only** — every case names **both** ends: a `Rte_Write`
   breakpoint in the writer module and a `Rte_Read` breakpoint in the reader
   module (or the `Rte_Call`/server pair), with the two modules actually
   different where the interface crosses modules — including where the peer is
   named but not authored (integration-test-patterns §2, Depth).
10. **integration-test only** — every interface appears under the target
    module's section; a peer has a section only under `peer_depth: peer_ports`
    or with mirroring on, and every mirror row is marked as such in
    `Traceability`.
11. **integration-test only** — every Min/Mid/Max states which range it came
    from (documented `Range:` vs implementation type), and every Min-1/Max+1
    states the implementation type its written value and its wrap came from —
    which must be the **type**, never the documented range, even when the
    documented range is narrower (integration-test-patterns.md §5.2). Each
    result step states the value **that end displays** — the wrapped value
    where the entered one is not representable in that end's type, with the
    entered value in brackets.
12. **integration-test only** — every enum literal used states its source
    (`Rte_Type.h`/ARXML, or an existing test case in `extend_existing` mode);
    no literal is derived from a value's prose description.
13. **integration-test only** — no `atcActions` entry names a source file
    (`.c` or `.h`) or a line number, and no edited or observed value is named
    by an identifier from the implementation. Every breakpoint is an RTE or
    runnable symbol found in the ARXML or the RTE header, named with its
    module, and `Traceability` cites that source (integration-test-patterns
    §9).
14. **integration-test only, `from_scratch`** — nothing in the workbook, the
    Traceability sheet or Open Points cites a legacy test-case workbook.
15. **integration-test only** — every enum interface has its negative case, or
    an Open Point saying why not (integration-test-patterns.md §5.2).
16. **Both skills** — column A holds the traced ID on every case row; the 21
    attributes sit contiguous and in schema order after it; where the validity
    columns are configured, no `isValid` cell says `Yes` or `Question` (as
    written by the skill), every `No` names the missing item and its Open
    Point, every case row's `isValid` cell carries the `Yes,No,Question`
    drop-down, and the run summary states the `No` count; the run summary
    carries the import note (output-format.md).
17. **Both skills** — every case's stimulus and observation means is available
    on the bench described by `docs.test_environment`, or is listed in Open
    Points (§4).
18. **qualification-test only** — every case's results implement its
    requirement's `aTestCriteria`, or an Open Point says why not; nothing in
    the workbook was derived from source code except fault-injection variable
    names, each marked `from code`; every bus-signal value, cycle
    time and timeout cites `docs.comm_database` (qualification-test-patterns
    §0, §1.1, §3).
19. **integration-test only** — every P-05 case cites the runnable's ARXML
    symbol and the timing or init event it was checked against, or an Open
    Point says the ARXML carries none or disagrees with the architecture
    (integration-test-patterns §7).
20. **integration-test only** — nothing in the workbook, `Traceability` or
    Open Points was derived from a `.c` file, the OS configuration or a build
    output (integration-test-patterns §9).
21. **Both skills** — `aChangeRequID` is empty on a first run, and on a re-run
    carries the change request of each new or changed object behind the case,
    or an Open Point says why not (§8).
22. **qualification-test only** — every `atcActions` entry is a stimulus that
    names, in plain words, a confirmed means from the catalogue, the item with
    its kind and the value; no bracket tag and no `Manual:` line; no "Record" or
    "Read" action; no action states a condition instead of doing something; no
    Open Point number or remark inside any step (qualification-test-patterns
    §7).
23. **qualification-test only** — every `atcResult` entry checks an observable
    item (a signal, message or A2L variable), never an internal state; a sent
    bus signal is used wherever one shows the behaviour; no result reads a
    signal or message the case's own actions removed; every observation window
    cites its source (qualification-test-patterns §7).
24. **Both skills** — no precondition contradicts the case's own actions.
25. **qualification-test only** — every item a case sets or reads exists on
    the feature's `test_software`; every boundary value is on a settable
    quantity; no database shorthand in the text (qualification-test-patterns
    §3, §6, §8).
26. **qualification-test only** — every value or procedure taken from a
    reference specification cites its document, version and section in
    `Traceability`; every version difference has its one Open Point; every
    requirement depending on an unavailable document is an Open Point, never a
    case with a placeholder pass criterion (qualification-test-patterns §3.1).
27. **Both skills, when the validity columns are configured** — on a re-run,
    every case QA marked `isValid = Yes` is unchanged, and no value or reason
    QA entered was altered (§8).
28. **qualification-test only** — preconditions set the baseline and verify
    it, postconditions restore it and verify it; the boundary points of one
    parameter are the steps of one case, alternating valid and invalid and
    ending on a valid nominal value, never separate cases; a merged case lists
    every requirement a step verifies in `Requirement ID`
    (qualification-test-patterns §4, §6, §7).
29. **qualification-test only** — every value a step writes or checks is a
    concrete number with its unit; no symbol standing for a value to be noted
    on the bench; every expected value derived from a scaling is written as
    the formula with its units and one worked decimal example; every
    comparison of two quantities with different resolution states a tolerance
    of at least one step of the coarser (qualification-test-patterns §3, §7).
30. **qualification-test only** — every state a case drives the ECU through
    whose outputs another in-scope requirement specifies is checked at that
    point, and that requirement is in the case's `Requirement ID`
    (qualification-test-patterns §7).
31. **Both skills** — every answer or value taken from the engineer or QA
    carries its source as §4 defines it; nothing is attributed to QA that QA
    has not written or confirmed.
32. **qualification-test only** — every scenario family of
    qualification-test-patterns §10 is either covered by at least one case
    whose `Traceability` row names the family, or listed once in Open Points
    with the reason it does not apply to this feature; no family is skipped
    silently.
33. **qualification-test only** — every message the feature transmits has its
    cycle-time case and, where the communication database defines them, its
    fast-cycle, repetition and payload-coherency cases; every message it
    receives with a timeout has its detection-window case; each cites the
    database attribute and the tolerance source, or is an Open Point
    (qualification-test-patterns §11).
34. **qualification-test only** — every finding of the `Requirements Hygiene`
    sheet appears in Open Points under `Input hygiene` with its owner, and no
    case takes a value from a document the sheet marks as conflicting without
    saying which one it followed and why (qualification-test-patterns §12).
35. **qualification-test only** — for a feature in
    `qualification_test.spec_governed_features`, every state, timing and
    error-handling rule a case checks cites the governing specification's
    section, not only the SW requirement that transcribes it
    (qualification-test-patterns §3.1).
36. **integration-test only** — every basic-software-facing port (a port
    mapped to a system signal or signal group, a mode-switch or service port)
    has its P-10 cases — each shape that applies, with the ARXML entry and the
    database attribute it rests on cited in `Traceability` — or one Open Point
    per port saying which shapes do not apply and why; every P-10d case checks
    both that the timeout is indicated and that it is not indicated early
    (integration-test-patterns §7, P-10).

## 7. Traceability & Open Points (both skills, every run)

Every generated workbook carries the 3-sheet contract from
[output-format.md](output-format.md): `Test Cases`, `Traceability` (one row per
generated case — the engineer creates the DOORS links from this sheet by hand,
so it must be complete and readable on its own), `Open Points` (every
unresolved symbol/value, every classification judgement, every requirement/
interface you could not cover and why, every spelling variant normalized).

**Input hygiene — a standing block in Open Points.** Defects in the inputs
themselves are among the most useful things a run finds, and two of them
silently change the scope. Check every run, and report under the Open Points
category `Input hygiene`:

- **Filter values that match nothing.** For each configured filter value
  (`attributes.status_filter`, `integration_test.testability_filter`), the
  number of objects it matches in this baseline. A value that matches **zero**
  — typically one that matched objects in the last run — means the export's
  vocabulary changed under the config: a quietly narrower scope. Report it even
  when the scope is otherwise non-empty.
- **Unclassified duplicate chapters.** Any chapter where more than 20 objects
  were dropped for carrying **no** classification attribute at all
  (`aFunctionModule`, `aTestability`, `aStatusOfAnalysis`,
  `aRequirementObjectType` all empty) — usually a freshly imported or
  untriaged copy of real sections. Name the sections it duplicates and ask
  whether it is being retired or is about to become authoritative, rather than
  only dropping it.
- **Lost table content** — the §1.3(3) count of rows whose content cell is
  empty while their attributes are filled.
- **integration-test** — name disagreements between the architecture text
  and the ARXML/RTE headers, connectors the composition has but the text does
  not describe or vice versa, periods that differ between the text and the
  ARXML timing event, a port's data mapping that disagrees with the message
  the architecture text names, and a cycle, timeout or E2E parameter that
  differs between the ARXML extract and the communication database
  (integration-test-patterns.md §2, §7, §9), mislabelled
  definitions (a `COMPU-METHOD` holding another type's literals, §5.2), and
  range-text variants a strict `Range:` match would have missed (§5.2).
- **qualification-test** — the `Requirements Hygiene` findings
  (qualification-test-patterns §12): a behaviour the software shows whose
  requirement is still `to review` or `ready for implementation`; a parameter,
  threshold or tolerance that differs between the requirement, Signals &
  Parameters, the communication database and the OEM specification it
  implements; a requirement cited by another document but absent from the
  export or outside the status filter; a requirement changed after the
  release under test.

## 8. Ledger & run history (audit)

Run identity, timing, the event format of the history file, and the automatic
commits at every gate and at the end follow
[../common/run-tracking.md](../common/run-tracking.md) — load it with this file.

Same two-record shape as `common/workflow-discipline.md` §9, adapted to this
domain's pin:

- **`last_run:` in the manifest — working state, overwritten each run.** Holds
  `run_id`, `started`, `ended`, `timing` totals, `skill_version`, `release_id`, `variants`, `input_hashes` (§2),
  the **`scope`** the run
  was made at, the **`output`** it wrote (path + hash), the inputs
  **`supplied_but_not_read`**, the requirement/interface snapshot
  (`ID -> {hash, change requests, cases: [...]}`), and the delta. Drives
  re-runs; not history.
- **`20_AI/manifests/{integration-test,qualification-test}/history/<KEY>.jsonl`
  — append-only audit trail.** One immutable JSON **event** per line (never
  edit prior lines; run-tracking.md §2). The closing `run_end` event carries the
  per-run record `{skill, skill_v, release_id, variants, input_hashes, scope,
  output, supplied_but_not_read, reqs_delta:{added,updated,removed}, notes}`
  plus `timing`. Lines without an `ev` field are legacy per-run records.

**Supplied but not read.** Record every input that was supplied (configured or
attached) but not opened this run, each with a one-line reason (`not needed: no
diagnostic interface in scope`). A later run can then tell "not needed" from
"forgot to look".

**Before planning a re-run, check three things, in this order:**

1. **Does the previous output still exist?** If `last_run.output.path` is gone,
   the re-run is a **regeneration**, not an in-place update — say so. If it
   exists but its hash differs from `last_run.output.hash`, someone edited it
   after the run (a reviewer's copy, a validated version): say so, read QA's
   validity verdicts (below), and ask before writing over it.
2. **Has the scope changed?** Compare `last_run.scope` with this run's —
   integration-test: the modules authored, `peer_depth`,
   `peer_module_mirroring`, `authoring_mode`, `scope.interfaces`;
   qualification-test: the feature and `requirement_ids`. If it differs, the
   per-item delta below is **not comparable**: a narrowed scope would surface
   every case that left it as "removed" and flag each one. Say plainly that the
   scope changed, show the old and the new scope side by side, list once what
   left the scope by that decision, treat the run as a regeneration, and
   re-confirm `expected_row_count` (§5).
3. **Is it layout only?** If every input hash and the scope are unchanged and
   only the output layout differs (reference columns, column order —
   output-format.md), **re-render** the existing workbook into the new layout:
   copy every content cell verbatim, run no analysis, ask no Phase-1 questions.
   Show the old→new column map, confirm, and append a history record with
   `notes: layout-only`. No test-case content is generated, so this does not
   skip the Phase-1 gate (no-fabrication.md).

**A validated output is read before anything is planned.** When the previous
workbook carries the validity columns (`isValid`, `Reason for Invalid` —
output-format.md) and QA has filled them, read every case's value and reason
first, and work from them. Tell QA's entries from the skill's own by comparing
with `last_run.review`, which holds what the skill wrote:

- **`Yes`** (QA) → accepted: leave the case **untouched**, even where a rule has
  changed since it was written. A changed input behind it is still a *changed*
  item below; say in the delta that an accepted case is affected.
- **`No` entered or changed by QA** → rework the case to answer the `Reason for
  Invalid`, cite the reason in `Traceability`, and show the old and new case
  side by side in the delta. A reason the inputs cannot answer, or one that is
  a question, becomes a Phase-1 question quoting it.
- **`Question`** (QA) → QA cannot judge the case until the `Reason for
  Invalid` is answered. Answer it from the inputs, then:
  1. Write the **reply to QA** — one numbered item per case or group of cases,
     each stating the answer, the change it implies (if any) and ending on the
     one thing QA must confirm (§5 rules). Give it to the engineer to pass on;
     it is the deliverable of this step.
  2. **Do not rework the case yet.** The answer may show the question was a
     misreading (no change), or the proposed change may not be what QA meant.
     Rework only once QA's acceptance comes back, and record it as
     `QA via engineer <date>` (§4).
  3. A change the question **exposed** but did not ask for (a missing
     tolerance, an ambiguous notation) is its own item in the reply — never
     slipped into the rework of the asked one.
  4. Once QA accepts, rework the case in place, cite the question and the
     acceptance in `Traceability`; no re-validation is needed unless QA asks
     for it. QA's `Question` and reason stay in the cells.
- **A reworked case resting on a fact only QA's reason states** (a state value,
  a scaling no input defines) → use it, record it as QA's statement, raise one
  `Input hygiene` Open Point for the document that should define it, and put
  it in the reply for QA to confirm.
- **`No` the skill wrote** (unchanged since last run) → its own placeholder
  mark: resolve it if the inputs now settle the missing item, otherwise keep it.
- **Blank** → not validated yet; treat as an ordinary case.
- **Never change what QA entered** — a reworked case keeps QA's value and reason
  until QA changes them. Snapshot the column values in `last_run.review` so the
  next run can see what QA changed.
- Any other value, or a column a reviewer added: ask, never map it. The
  drop-down (output-format.md) makes this rare; a workbook from before it
  existed may carry `Valid` / `Invalid` — ask once, record the answer in
  `last_run.review`, and do not ask again for that workbook. *(Observed: QA
  typed `Valid`, `Invalid` and `Question`; the engineer confirmed Valid = Yes
  and Invalid = No, and `Question` was adopted as a value.)*

**In-place re-run** (output present, scope unchanged): recompute each in-scope
requirement's/interface's hash and compare to `last_run`:
- **new** (ID absent) → author the test case(s), append.
- **changed** (hash differs) → **update the mapped test case(s) in place**
  (keep title/history stable), tag revised.
- **removed** (was present, now absent) → **flag it; never silently delete** —
  surface the orphaned case for the engineer to decide.
- **unchanged** → leave untouched.
Show the delta and **confirm before writing**.

**Change requests follow the change.** A case added or updated on a re-run
because its object is new or changed carries that object's `aChangeRequID`,
copied verbatim into the case's `aChangeRequID`; where several objects behind
one case changed, carry every distinct value, separated the way the export
separates multiple values. Record each object's `aChangeRequID` in the
`last_run` snapshot so the next run can compare. Three cases leave it empty:

- **the first run** for a module or feature — authoring the baseline is not a
  change, and an object's old change request says how the object came to be,
  not why the test case was written;
- **an object that changed but carries no change request, or the same one as
  last run** — keep the case's current value and raise an `Input hygiene` Open
  Point: the change may not be tracked;
- **an export without an `aChangeRequID` column** — one Open Point, never a
  stop.

**Writing the config and the manifest.** Both are commented YAML, and the
comments are their documentation. Write them through a **round-trip** YAML
library that keeps comments and key order (`ruamel.yaml` in round-trip mode) —
never by splicing text, and never through a plain loader/dumper such as PyYAML,
which drops every comment. Re-load the file after writing and check that the
keys you meant to change are the only ones that changed. Where no round-trip
library is available, edit only at an anchor that is unique in the file and not
inside a comment, then re-load and check the same way. *(Observed: a manifest
corrupted by splicing at `last_run:` — a string that also appeared in one of
its comments.)*

## 9. No fabrication

See [no-fabrication.md](no-fabrication.md). No DOORS write access and no test
execution happen here — never claim a result you did not produce, and never
write to DOORS yourself.
