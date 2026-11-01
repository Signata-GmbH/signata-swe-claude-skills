# qualification-test (SWE.6) — refinement plan from the QA validation

**Status:** QA answered (§4); implemented 2026-10-06 on branch
`fix/swe6-validation-feedback-2026-10` (§6). The re-run was validated by QA —
every case accepted, with two rewritten examples showing the expected case
design; implemented 2026-10-16 on branch `fix/swe6-qa-stepped-cases-2026-10`
(§7). A third round — QA's validation of a motor-control feature, plus what
its Phase-1 answers showed — was implemented 2026-10-26 on branch
`fix/swe6-qa-motor-control-2026-10` (§8). A fourth round — the analysis of
nineteen customer HiL findings on one release — was implemented 2026-10-30 on
branch `feat/swe5-arch-only-swe6-scenarios` (§9). A fifth round — the QA
validation of the Actuator Data and Motor Control workbooks, consolidated in
the project lead's "QA Feedback for Test Case Generation Skill" (30 October)
— was implemented 2026-10-30 on branch `fix/swe6-qa-round5-2026-10` (§10).
Round 11 — QA columns are QA's only — is §11. Round 12 — requirements left
without a case, found by comparing a project's second-stage runs with the
manual SWE.6 module — was implemented 2026-11-01 on branch
`fix/swe6-coverage-round12-2026-11` (§12).
Next: re-run Actuator Data, Motor Control and CAN and check the coverage table
against the requirements listed in §12.1.

**Source:** the QA validation of a generated SWE.6 workbook for one CAN
feature — 37 concrete cases accepted, 77 rejected. The detailed feedback is
kept out of Git (it holds customer-project details; this repository is public).

---

## 1. The finding in one paragraph

Grounding worked: no case was rejected for a wrong signal, identifier or value.
Every rejection was about the **procedure**. Cases said *what* to establish and
observe, but not *how*: no stimulus mechanism in the actions (25 rows), no
observation channel in the results (22), procedures written for behaviour no
supplied document describes (14), requirements that should share one case (8),
boundary values on a quantity the bench cannot set (4), database notation in
the text (2), a precondition that blocks its own action (1), and a pass
criterion left as a placeholder because a cited specification was missing (1).
`main` checks that a stimulus and an observation are *feasible on the bench*
(workflow-discipline §4, self-check 17); it never requires the step to *name*
the mechanism.

## 2. Proposals and verdicts

| # | Proposal | File | Verdict |
|---|---|---|---|
| P1 | Stimulus/observation catalogue at the Phase-1 gate | `qualification-test/SKILL.md` Step 4 | **Adopt with changes:** the catalogue is its own sheet in the Phase-1 workbook, one row per item with its own answer (never "the whole table as one question" — one question per QID, workflow-discipline §5); confirmed rows cached project-wide (N4) |
| P2 | Every `atcActions` entry names its mechanism, e.g. `[<tool/channel>] <action>`; never a state written as an action | qualification-test-patterns §7 | **Adopt;** notation waits for QA question 1 |
| P3 | Every `atcResult` names what is observed and where; internal states (“the ECU uses …”, “mode is active”) are not observables; no result may name a signal the case's own actions removed from the bus | qualification-test-patterns §7 | **Adopt, plus:** an observation window (e.g. “absent for ≥ N ms”) comes from a cycle time or timing in a supplied input, never invented |
| P4 | Never invent a test procedure — behaviour from a state machine, init sequence or mode transition no input describes is a Phase-1 question or an Open Point | `no-fabrication.md` (both skills) | **Adopt,** paired with N2 |
| P5 | Boundary values only on quantities the bench can **set**; a database factor and range make a signal reportable, not settable. Dependent quantities (e.g. a measured current): drive an operating point, capture the source and the reported signal together | qualification-test-patterns §6 — **corrects** the `comm_database` sentence added on 2026-10-05 | **Adopt as written** |
| P6 | Merge requirements that are outcomes of one stimulus setup | qualification-test-patterns §7 | **Adopt the idea, rework the rule:** as written it contradicts its own example and §7's “exactly one pass/fail result”. Merges are **proposed** in the Phase-1 proposed-cases table, not decided at generation. Pass/fail marking waits for QA question 3 |
| P7 | No database notation in test text: write “start bit 23, length 9 bits”, not `(23\|9)` | qualification-test-patterns §3 | **Adopt as written** |
| P8 | Self-checks 22 (actions open with a mechanism; no state as action), 23 (no internal-state result; no result on a removed signal), 24 (both skills: no precondition contradicts its own actions) | workflow-discipline §6 | **Adopt** |
| P9 | SWE.6 reference columns: `requirement_id` → `Requirement ID` before the 21, keyed to `qualification_test.reference_columns`; `validity_review` for both skills | `output-format.md`, config template | **Adopt and extend:** column headings **and** value vocabulary configurable per skill (the reviewer used `QA Validation`/`QA Comment` with `valid`/`invalid`) — waits for QA question 4 |

## 3. Gaps the feedback missed

- **N1 — Re-runs read the reviewer's verdicts.** *Most urgent.* Nothing on
  `main` reads a reviewed workbook back; a re-run only notices that the output
  was edited and asks before overwriting. Rule: read the verdict columns;
  leave accepted cases untouched; rework rejected ones answering the reviewer's
  comment (cited in Traceability); never overwrite the reviewer's columns.
  Both skills (workflow-discipline §8).
- **N2 — Specifications a requirement cites.** A requirement that names a
  document, or whose behaviour is defined by a standard specification (e.g. the
  OEM network-management specification), gets that document requested at
  Phase 1 and recorded in the manifest (`docs.extra`) — never a placeholder
  pass criterion. Revises the earlier advice to skip OEM specifications.
- **N3 — Observations must exist on the software under test.** An XCP/A2L
  observation may not exist on Series SW; check each observation against the
  feature's `test_software` (Series/Debug).
- **N4 — Cache the catalogue project-wide.** Mechanisms belong to the bench,
  not to a feature: cache confirmed rows in `ai_test_project.yaml` (like
  `peer_modules`) so the next feature confirms only new rows.
- **N5 — Generic examples only.** The rules are written with generic
  examples; customer signals, IDs and document names stay out of this public
  repository.

## 4. Questions sent to the QA engineer

1. **Mechanism notation** — `[<tool/channel>] <action>` at the start of each
   step, or plain sentences (“Using <tool>, …”)?
2. **Manual vs automation** — is naming the tool and the action enough in the
   Excel/DOORS test case, or are more detailed manual instructions expected?
   (vTestStudio scripts are parked: `VTESTSTUDIO-AUTOMATION-PLAN.md`.)
3. **Merged cases** — when one case covers several requirements: one pass/fail
   result per requirement inside the case, or one combined result?
4. **Review columns** — which column names and values (`QA Validation`/
   `QA Comment`, `valid`/`invalid`, or `isValid`/`Reason for Invalid`), and do
   they apply to SWE.5 too?
5. **Missing documents** — a specification cited by a requirement, and the
   network-management specification.
6. **Bench capabilities** — supply control, sensor stimulation, fault
   injection, XCP availability on Series/Debug SW.

## 5. Order of work once the answers are in

1. **N1** — before any re-run, so the accepted cases are not regenerated.
2. **P1 + N4**, then **P2 + P3 + P8** — the catalogue, then the writing rules
   and their checks (aimed at the 47 mechanism/observation rejections).
3. **P4 + N2** — no invented procedures; ask for cited specifications.
4. **P5, P7, P9 + N3.**
5. **P6** — with QA's answer to question 3.

Then re-run the same CAN feature with the same inputs and reviewer, and
compare against the 37 / 77 baseline.

Not blocked by QA: N1, P1 (without the notation), P3, P4, N2, N3, N4, P5,
P7, P8 (items 23–24). Blocked: P2's notation (Q1), P6 (Q3), P9's names (Q4).

## 6. QA's answers and what was implemented

| Q | Answer (summarised) | Implemented as |
|---|---|---|
| 1 | The `[<tool/channel>] <action>` format is fine; every step must name the message, signal or variable — saying which it is — the value, and how it is set (CANoe panel, XCP, CAPL, …) | qualification-test-patterns §3 (kind of every item), §7 (actions open with the means) |
| 2 | Manual instructions are wanted: which panel, which steps | §3.2 catalogue `Manual steps` column; a `Manual:` line under each action (§7) |
| 3 | A merged case has one final result covering all its requirements; the verdict is on the test case, not per requirement | §7 merged requirements: proposed at Phase 1, one pass/fail result, each requirement traced to its result step |
| 4 | Review columns `Review_Test`, `Review_Peer` (Minor Findings / Major Findings / Questions / No Findings) and `Comment_Review_Test`, `Comment_Review_Peer` | **Not adopted** — by decision, both skills keep `isValid` / `Reason for Invalid` as the only validation columns; a re-run reads them back (N1) |
| 5 | The cited specifications were supplied (an OEM CAN performance specification and an OEM network-management test specification) | §3.1 reference specifications: registered once per project, asked at the start of each run. QA's follow-up on the version difference: refer to all the documents — so every registered document is searched, the supplied version is used, and each version difference is one Open Point |
| 6 | XCP is available for injecting values; refer to the code for the variables that inject a fault | §0 narrow exception: the code may give the **name** of a fault-injection variable, which must be in the A2L and is marked `from code`; never a value or an expected result |

All of P1–P9 and N1–N4 are in. Changed files: `qualification-test/SKILL.md`,
`integration-test/SKILL.md` (re-runs read the validity verdicts),
`qualification-test-patterns.md` (§0, §3, §3.1, §3.2, §6, §7, §8),
`workflow-discipline.md` (§1.1, §5, §6 items 22–27, §8),
`no-fabrication.md`, `output-format.md`, `project-config.md`, the config and
manifest templates, README and USING-THE-BETA.

Still open:

- **The supplied specifications stay out of Git** — they are OEM documents.

## 7. Second QA round — case design (2026-10-16)

**Source:** QA validated the re-run workbook of the same CAN feature. Every
case was marked valid — grounding, attributes, traceability and Open Points
were accepted — and QA rewrote two cases (a supply-voltage boundary
requirement and a received-message length requirement) beside the generated
ones to show how they write cases. The workbook stays out of Git (§1).

| # | QA's example shows | Rule on `main` that produced the generated form | Implemented as |
|---|---|---|---|
| R1 | One case per requirement; the boundary points are **steps** of it, alternating valid and invalid values and ending on a nominal one (recovery is checked too) | §4 logical parent with one child per value; §5 value in the title; §6 one case per point | §4 parent only for variants; §5 no value in a stepped title; §6 points are steps, ordered to show recovery |
| R2 | Every step has its own expected value | §7 exactly one result marked pass/fail (from Q3 in §6) | §7 every result is a check; the case passes when all hold. **Supersedes Q3**, by the engineer's decision |
| R3 | Action *n* is a stimulus, result *n* verifies it; no observation steps among the actions, no `-` results | §7 action/result templates ("Record …" as an action) | §7 numbered stimuli, one `Verify …` per action |
| R4 | Preconditions set a baseline **and verify it** on the bus; the common bench setup is not repeated | §7 "required ECU state" only | §7 preconditions as set-and-verify steps; bench setup left to `atsTestEnvironment`/`atcRemark` |
| R5 | Postconditions restore the baseline and verify it | §7 "how the system is left" | §7 restore-and-verify steps |
| R6 | Means in plain words inside the step (which panel or generator block, which value); no bracket tag, no `Manual:` line, no Open Point notes | §7 `[means]` tag plus `Manual:` line (from Q1/Q2 in §6) | §7 the step itself is the manual instruction, from the confirmed catalogue; remarks only in Open Points/Traceability. Keeps Q2's intent (runnable by hand), drops its separate line |
| R7 | The outcome is read on a signal the ECU sends (a timeout flag), not an XCP qualifier | §0 allows XCP as a boundary observation; no preference stated | §7 observe on the bus first; XCP only where no sent signal shows it |
| R8 | Requirements that vary **one stimulus** and read **one signal** share a case (valid / longer / shorter message length) | §7 merges only for the same stimulus with different observations | §7 second merge kind, still proposed at Phase 1; `Requirement ID` lists every requirement a step verifies (engineer's decision) |
| R9 | A stepped case that goes out of range is `positive` | §6/§8 `negative` outside the range | §8 `positive` for specified behaviour, out-of-range reaction included; `negative` for a wholly invalid stimulus. Self-check 6 counts out-of-range steps as negative coverage |
| R10 | Enumerated values as `Text(raw)` | `raw (Text)` | §7 notation |

QA confirmed that, for a message whose length is too short, the timeout flag
is the expected observation; where no input gives the timeout time, the
result checks the end state without a window and the time stays an Open Point
(§7).

Self-checks: `workflow-discipline.md` §6 items 3, 6, 18, 22, 23 revised; item
28 added. Integration-test keeps one marked pass/fail result per case.


## 8. Third QA round — values, state outputs, answers (2026-10-26)

**Source:** one SWE.6 run on a motor-control feature (64 requirements in
scope, 23 case rows). QA validated the workbook: 17 cases valid, 1 invalid,
5 marked `Question`. The run itself also showed where the Phase-1 questions
produced answers that could not be used. Customer details stay out of Git (§1).

### 8.1 QA's validation of the generated cases

| # | QA's feedback | Cause on `main` | Implemented as |
|---|---|---|---|
| V1 | "`× 48` — is it hex?" on a channel-count check derived from a duty-cycle percentage | §7 asked for unambiguous results, not for derived values to be written out | patterns §7: a derived expected value is its formula with units and a worked decimal example; a comparison across resolutions states a tolerance of one step of the coarser side. Self-check 29 |
| V2 | "What is R16 / R13?" — the case said "note the raw value for 16 V (R16), write R16 × 5 / 16" | an A2L item without a scaling was answered at Phase 1 with "derive it on the bench" | patterns §3: a scaling question per such item, with a concrete proposal; §7: every value is a number the operator can type, otherwise a marked placeholder and `isValid = No`. Self-check 29 |
| V3 | Invalid: a direction-change case checked that the idle state occurs, but not the output pattern another requirement specifies for idle | §7 merges covered "same stimulus" and "one stimulus varied", not states passed through | patterns §7: third merge situation — a state a case passes through is checked against the outputs other in-scope requirements give it, marked by the bus signal for the state where one exists; proposed at Phase 1. Self-check 30 |
| V4 | QA wrote `Valid` / `Invalid` / `Question` in `isValid` | the allowed values were `Yes` / `No` / blank, typed by hand | output-format: `isValid` is a `Yes,No,Question` drop-down (both skills); no-fabrication: the skill never writes `Question`; workflow-discipline §8: `Question` → written reply for QA, rework only after QA accepts, an exposed change is its own item in the reply; reworks resting on a fact only QA stated are recorded as QA's statement plus an `Input hygiene` Open Point (engineer's decision) |

QA accepted the answers and the reworks (including a tolerance the question
had exposed but not asked for); no re-validation was needed.

### 8.2 What the run's Phase-1 answers showed

| # | Observed | Implemented as |
|---|---|---|
| A1 | Five "Which …?" questions were answered "Yes" — their proposal was "No proposal" or deferred the value | workflow-discipline §5: every proposal concrete, "Yes" accepts it; otherwise the question lists options |
| A2 | Four "Is there X, or does it go to Open Points?" questions were answered "No" — two readings | §5: one yes/no per question, "No" means the opposite of the proposal |
| A3 | Two answers contradicted each other (a function accessible vs. not accessible on Series SW) | §5 and SKILL Step 5: check the answers for unresolved and contradicting ones before generation; ask what changes a case now |
| A4 | A catalogue row came back unanswered: the question had been written into its `Answer` cell | patterns §3.2: `Answer` is the engineer's column, left empty; a means to be named is asked as a name |
| A5 | A value the engineer picked from an AI proposal was recorded as "given by QA" in four places | workflow-discipline §4 "record who said it", no-fabrication. Self-check 31 |
| A6 | The engineer suggested reading the code for a motor-direction mapping | patterns §0: decline in one sentence and search the supporting specifications — the mapping was settled from three of them, a fourth flagged as contradicting |
| A7 | Values the feature's inputs left open (a direction, a task period, a supply read-back) were in other features' requirements, the system requirements and the architecture text | patterns §3: supporting specifications, cited not traced, disagreements as `Input hygiene` |
| A8 | A requirement's timing (one task cycle of a few ms, a slope per ms) was finer than the fastest observation (a 10 ms DAQ event) | patterns §7: compare every stated timing with the fastest observation; finer → Open Point stating the false-fail risk |
| A9 | The feature argument was not an `aFeature` value (twice in this project, each costing an aborted run) | patterns §1, SKILL: offer the nearest `aFeature` values with counts and modules |

Changed files: `qualification-test/SKILL.md`, `integration-test/SKILL.md`
(the `Question` value and the drop-down only), `qualification-test-patterns.md`
(§0, §1, §3, §3.2, §7), `workflow-discipline.md` (§4, §5, §6 items 16 and
29–31, §8), `no-fabrication.md`, `output-format.md`, STATUS.

## 9. Fourth round — customer HiL findings (2026-10-30)

**Source:** the customer's HiL acceptance test of one release raised nineteen
problem tickets (an internal Jira extract of 12 October; the detailed list is
kept out of Git, as before). Each was classified by where the defect sits and
by which test level should have caught it.

### 9.1 What the classification showed

| Bucket | Tickets | What it says about the skills |
|---|---|---|
| Sequences at the bus boundary — start-up counters and NM state, suppression exit, a fault arriving while the actuator moves, recovery after the fault, repeated or reversed requests | 12 | Requirement-by-requirement cases check settled states; none had driven these sequences. Every one was visible in the frames the ECU sends. |
| Timing measurements — time to first output, timeout detection window, cycle time and burst count, payload coherency on change | 4 (overlapping) | The bus database already carries the attributes; no case measured them. One had an existing DOORS case that was either not run on the release or did not fail. |
| Requirements that were missing, unreleased (`ready for implementation`, `to review`), contradictory between documents (a delay of 500 vs 1000 ms, a threshold of 4 vs 5, a tolerance of ±5 vs ±10 %) or changed after the release | 6 | The 12 October run had already raised several as Open Points; they needed a standing place and an owner. |
| Module-to-module interface mismatches of the SWE.5 kind | 0 | Four tickets had an integration flavour (application ↔ basic-software bus layer: coherent signal writes, single start-up of message groups, timeout semantics), none of which the RTE value-pass-through pattern tests, with or without code. |

### 9.2 Changes made

| # | Change | Where |
|---|---|---|
| R1 | Eight **scenario families** checked at Phase 1; each applies (with cases) or is declined with a reason; family marked in Proposed Cases and Traceability; repetition count for start-up/exit sequences confirmed at the gate | `qualification-test-patterns.md` §10, SKILL Step 4.8, self-check 32 |
| R2 | **Timing cases from the communication database**: cycle time, fast cycle / repetitions / delay, payload coherency on change, two-sided timeout detection, time to first frame; tolerance always sourced, stricter of two used | §11, SKILL Step 4.9, self-check 33, config `comm_database` comment |
| R3 | **Spec-governed features**: the OEM specification is a mandatory input for features it defines (E2E, NM, diagnostics, bus); every state/timing/error rule cites its section | §3.1, `qualification_test.spec_governed_features`, workflow-discipline §1.1, self-check 35 |
| R4 | **Requirements Hygiene sheet** at Phase 1 — status lag, parameter/threshold/tolerance conflicts, cited-but-absent, changed after release, no verification criterion — each row with an owner; mirrored to Open Points | §12, SKILL Step 4.6, workflow-discipline §5/§7, self-check 34 |
| R5 | (SWE.5, same branch) the integration-test skill no longer reads source code — README decision 17 | `integration-test-patterns.md` §9 and throughout |
| R6 | (SWE.5, same branch) **pattern P-10, application ↔ basic-software integration** — five shapes per basic-software-facing port, stimulated at the RTE call, observed on the bus, expected values from the ARXML data mapping / timing / `ALIVE-TIMEOUT` / E2E entries and the database attributes — README decision 19 | `integration-test-patterns.md` §2, §5.1, §6, §7 P-10, §9; self-check 36; `integration_test.bsw_service_patterns` |

### 9.3 Deliberately not done

- No change to how an existing DOORS case is executed per release — a test
  management question, not a generation one.

**P-10 was first parked, then built the same day** at the project lead's
request (maximum coverage over caution). It has no validated case template
from the engineers yet; the PoC run on the planned modules is its first
validation, and the five shapes should be reviewed by QA like any other
pattern before they are relied on.

### 9.4 How to validate this round

A blind test, not a reproduction run: run `/qualification-test` on the
communication, end-to-end protection and mode-management features using only
the inputs that existed before the customer test, **without** the ticket list,
and count how many of the nineteen scenarios appear as cases. The 12 October
cross-feature run cannot answer that, because it was given the tickets.

## 10. Fifth round — QA validation of two features (2026-10-30)

**Source:** QA's validity columns in the Actuator Data and Motor Control
SWE.6 workbooks — four cases `Invalid`, eight `Question`, none in CAN — as
consolidated by the project lead in "QA Feedback for Test Case Generation
Skill" (kept beside this file, not committed: it names project requirement IDs
and values). The SWE.5 runs drew no rejections.

### 10.1 What the generated cases showed

The four rejections and eight questions were re-read in the workbooks before
writing rules, with two results that differ from the consolidated document:

| Finding | Document's root cause | What the workbook shows |
|---|---|---|
| F4, direction change through IDLE | the PWM channel values and the state signal were not checked | They **were** checked — all four channels at zero and the state signal at zero — inside one 90-word result sentence. The reviewer could not find them. The defect is one compound result line, not a missing check. |
| F5–F9, "× 48" and "R16 / R13" | expected values in a foreign unit, symbolic placeholders | Already corrected in the workbooks by round 3 (§8): the cases now read `× 4800 / 100 ± 48 ticks (decimal, e.g. 50 % = 2400)` and `16000 / 13000`, `5000 / 4000`. The QA comments predate that fix. |

F1, F2/F3, F10/F11 and F12 are as the document describes.

### 10.2 Changes made

| # | Rule (document numbering) | Where |
|---|---|---|
| R1 | An engineer or QA answer overrides a criterion step; the step is dropped, the conflict goes to `Requirements Hygiene`; a step the run's own Open Point doubts never stays in a case presented as valid | patterns §1.1; §12 finding types; self-check 37; no-fabrication validity rule |
| R2 | Every parameter an expected result rests on has a provenance step — read, set, or fixed-in-build with source — and a Phase-1 **parameter table**; an "inaccessible" verdict applies to every case using the parameter | patterns §3 (before §3.1); SKILL Step 4.4; self-check 38; no-fabrication validity rule |
| R3 | **One observable per result line** (sub-numbered `2a`, `2b`…; no range expressions); a named state is followed by its defining outputs as their own lines. The round-3 "state outputs" rule stands; this round fixes how the checks are written | patterns §7; self-check 39 |
| R4 | The requirement's unit first, raw or converted form after it with the derivation | patterns §7 (strengthens the round-3 formula rule) |
| R5 | No symbolic placeholders | already in force since round 3 (§8, self-check 29); no change |
| R6a | A bound borrowed from another requirement or parameter names its source **and direction inline** in the result | patterns §7; self-check 39 |
| R6b | An error-guessing line in the criterion is a Phase-1 question with the criterion's expectation as proposal; unconfirmed → `isValid = No` with a `Decision` Open Point. **Deviation from the document:** not written into `atcRemark`, which carries the software level (§8) | patterns §1.1; §12; self-check 40; no-fabrication validity rule |

### 10.3 For the requirement owners (project side)

The document's four input findings — a criterion naming a stimulus that
cannot produce the value, a criterion whose error-guessing expectation QA
disputes, criteria resting on a parameter the A2L does not expose, and
calibrations with no documented scaling — are exactly the finding types the
new `Requirements Hygiene` sheet (§9, patterns §12) now reports with an owner.
They are tracked in the project repository, not here.

## 11. QA columns belong to QA; blocked cases get `Notes` (2026-11-01)

**Source:** project lead's change request after the fifth round. The skill
wrote `isValid = No` on cases it knew could not run as written (§10, R1, R2,
R6b; round 3, V2), and listed those cases in a standing Open Point (`OP-02` in
the delivered workbooks). QA's verdict column therefore held two authors'
values with two meanings, and QA could not tell "rejected" from "waiting for
the bench".

| # | Change | Where |
|---|---|---|
| N1 | `isValid` / `Reason for Invalid` (or `isValid?` / `Reason for not Valid`) are QA's only; the skill leaves them empty on every row. The `isValid = No` rule for SWE.6 is removed; the standing Open Point listing those cases is rewritten as withdrawn on the next re-run | no-fabrication (validity columns split by skill); output-format reference columns; workflow-discipline §8 |
| N2 | New last column `Notes`: one plain-language paragraph `BLOCKED - <category>. <what the test does>. <what is missing (id)>. Action: … QA: …`, with five categories and a jargon list; it refers to Open Points instead of repeating them | patterns §13; output-format (column spec, example rows) |
| N3 | Every case that traces a requirement is written even when blocked, complete, with any assumed value (the Phase-1 proposal or a supporting specification's value) named in `Notes`. Former `isValid = No` triggers — no scaling, no parameter provenance, unconfirmed error guessing, a self-doubted step, a reference document `N/A`, an unconfirmed catalogue means — now produce blocked cases | patterns §1.1, §3, §3.1, §3.2, §7, §8, §13; no-fabrication (assumed value is not an invention) |
| N4 | A re-run writes version N with a `Change vs v<N-1>` column (`Content updated in v<N> - re-review` / `New in v<N> - review` / empty); QA's verdict is kept only where the case text did not change, and cleared on changed cases after being copied to `Traceability` and `last_run.review` | workflow-discipline §8; manifest `last_run.output.version`, `last_run.review` |
| N5 | Hard read-back check on the written file: fails on any QA cell the skill wrote, a `Notes` cell not starting `BLOCKED - <category>.` or lacking `Action:` / `QA:`, `Notes` not last, or a wrong change marker. README and the config template show the column convention | output-format (final read-back check); self-checks 16, 26, 27, 37, 40, 41, 42; SKILL Steps 4–7; README §3.10 and decision 20 |

**Deliberately not done:** `integration-test` (SWE.5) keeps writing
`isValid = No`; the shared rules now say which skill each policy applies to.
Moving SWE.5 to the same convention is a separate decision.

## 12. No requirement leaves scope at classification (2026-11-01)

**Source:** a project's second-stage runs (2026-11-01). In-scope requirements
that got no generated case were compared afterwards with the manual SWE.6
module. The requirement IDs and the comparison stay out of Git, as in §10:
this repository is public (N5).

### 12.1 Five causes

| # | Cause | Where it showed | What the skill did |
|---|---|---|---|
| A | The observable is an internal value, reachable only by XCP on a symbol absent from the supplied A2L, or by a debugger | 3 Actuator Data requirements; 27 Motor Control controller-internal requirements (count as reported — the ID ranges in the evidence add up to 37; to be reconciled) | §7 "an internal state is not an observation" → Open Point, no case |
| B | The requirement is a read-cycle or peripheral configuration | 14 Actuator Data requirements; 4 Motor Control requirements | classed as integration level by the skill, no case proposed |
| C | The stimulus must be injected by writing a calibration (several inputs, one of them a hardware-ID voltage) | 3 Actuator Data requirements, plus the hardware-ID voltage | §0 allowed only fault-injection variable names |
| D | The requirement delegates to a specification ("implemented according to `<doc>`") | 4 CAN requirements | classed as configuration review or "covered by the OEM package" |
| E | `release.variants` excluded a second variant | 13 CAN requirements | dropped by the filter with no line saying so |

None of them was visible at the row-count gate: it counts output rows, and a
requirement with no row does not change the count the engineer confirms.

### 12.2 Changes made

| # | Change | Where |
|---|---|---|
| 1 | **No requirement leaves scope at classification.** Only the four filters — feature, testability, status, variant — remove a requirement (the variant filter is now explicit in §1); the attrition report names no other reason. Every in-scope requirement gets at least one proposed case and a written one, blocked where needed (§13). A doubt about the level or the observable goes to `Requirements Hygiene` as `possibly integration level` or `observable not on bench`, with an owner, beside the case. Removed: §1.1 "the criterion rules the test level out → no case", §2 "already covered → leave alone" (the split is now information only), §7 "no observable → Open Point", §13 "not blocked, still `Not covered`", §3.1 "covered by the OEM's own testing" question | patterns §1, §1.1, §2, §6, §7, §12, §13; workflow-discipline §5, §6 item 8; no-fabrication; output-format (Open Points `Not covered`) |
| 2 | **Observation means by bench capability.** `qualification_test.debug_means`: `none` (default) / `xcp_varlist` / `xcp_and_debugger`; new optional `docs.variable_list` (map file, ELF symbol export, Debug-SW A2L). Under `xcp_varlist` any listed symbol is an XCP observable, scaling and data type asked at Phase 1; under `xcp_and_debugger` the catalogue kinds `breakpoint at symbol` (period or hit count, as a timing case, tolerance from an input or an Open Point) and `debugger variable`, on Debug-SW cases only. Symbols from the two lists only. §7 keeps "an internal state is not an observation"; its consequence is now a written case, blocked `bench capability not confirmed`, proposing the symbol | patterns §0, §3, §3.2, new §3.3, §7, §8, §11 (period at a symbol), §13; workflow-discipline §1.1; project-config §4.1, §4.2, §5; config template |
| 3 | **Stimulus injection.** §0's name-only exception now covers any input the bench cannot drive physically (ADC voltage, sensor angle, hardware-ID pin, supply measurement), not only faults. Same rules: name only, in a variable list, marked `from code`, offered in the catalogue, no value or expected result from the code | patterns §0, §3.2 (`injection variable` kind), §6 (an injection variable is a settable source); SKILL intro and description |
| 4 | **Spec-delegating requirements are expanded, not reviewed.** Registered document → cases from its observable rules (E2E counter, CRC, timeout, invalid-data reaction; NM states, timings, bit fields; development-message database: each message present with its cycle), traced to the requirement. Not registered → one blocked case per requirement, `missing test equipment`, naming the document, which is asked for at the gate. "Covered by the OEM test package" is never a reason to omit a case — a `Traceability` note at most | patterns new §3.4, §3.1; self-check 26 |
| 5 | **Variant scope report** at the Phase-1 gate: per variant outside `release.variants`, the requirements it excluded, by ID, with one question each whether to include them; answers in `scope.included_variants`; included cases carry that variant in `aVariant` | patterns new §1.2; output-format `aVariant`; manifest template |
| 6 | **Coverage gate** replaces the SWE.6 row-count gate: in-scope requirements, cases per requirement, every zero-case requirement with its reason. A zero-case requirement is a STOP; the engineer's decision is recorded in `last_run.coverage` and repeated in Open Points as `Not covered`. Recomputed after generation. Self-checks 43 (hard: no requirement without a case or a recorded decision), 44 (no symbol outside the variable list / A2L), 45 (no `possibly integration level` finding without a written case); 23, 25, 26 extended. integration-test keeps its row-count gate | workflow-discipline §3, §5, §6, §8; SKILL Steps 4.11, 6, 7; manifest template |
| 7 | Documentation | README §3.10 and decision 21; config template (`debug_means`, `docs.variable_list`); manifest template (`last_run.coverage`); this section |

### 12.3 Decisions

- **`debug_means` defaults to `none`.** Whether the bench reaches a symbol
  outside the delivered A2L, or runs a debugger, is the project's fact to
  state, not the skill's to assume. Under `none` nothing is lost: the case is
  written, blocked, proposing the symbol, and the Hygiene row tells the bench
  owner what would unblock it.
- **The manual DOORS test module is not an input**, and the comparison that
  found these causes is not repeated by the skill. The existing-cases export
  (`docs.qualification_test_spec_export` / the manifest's
  `existing_qualification_test_cases`) is unchanged and is not used by
  anything new: the coverage gate counts this run's cases only.
- `integration-test` is untouched; the shared files say which rule applies to
  which skill.
