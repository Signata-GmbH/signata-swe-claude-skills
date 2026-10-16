# qualification-test (SWE.6) — refinement plan from the QA validation

**Status:** QA answered (§4); implemented 2026-10-06 on branch
`fix/swe6-validation-feedback-2026-10` (§6). The re-run was validated by QA —
every case accepted, with two rewritten examples showing the expected case
design; implemented 2026-10-16 on branch `fix/swe6-qa-stepped-cases-2026-10`
(§7). Next: re-run the same feature and compare with QA's examples.

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

