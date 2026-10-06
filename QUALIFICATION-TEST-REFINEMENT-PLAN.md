# qualification-test (SWE.6) — refinement plan from the QA validation

**Status:** waiting for the QA engineer's answers (§4). Recorded 2026-10-06 on
branch `fix/swe6-validation-feedback-2026-10`. Nothing implemented yet.

**Source:** the QA validation of a generated SWE.6 workbook for one CAN
feature — 37 concrete cases accepted, 77 rejected. The detailed feedback is
[QualificationTest_Skill_Feedback_2026-10-06.md](QualificationTest_Skill_Feedback_2026-10-06.md),
on this branch only: it holds customer-project details and this repository is
public, so it is removed before the branch is pushed or merged.

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
