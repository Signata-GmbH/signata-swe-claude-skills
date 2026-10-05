# Qualification-test (SWE.6) mechanics

> Loaded by `qualification-test/SKILL.md` on top of
> [workflow-discipline.md](workflow-discipline.md),
> [no-fabrication.md](no-fabrication.md), and
> [output-format.md](output-format.md).

## 0. Black-box — the source code is never read

Qualification testing checks the software against its requirements from the
outside: stimulus and observation at the software's boundary — bus signals,
diagnostic requests, XCP/A2L measurements, I/O. The skill runs in the SWE.3
repository, so the code is within reach; **do not open it.** An expected value,
threshold, timing or state name taken from the code would test the code
against itself, and a defect in the code would become the expected result.

Every expected result comes from the requirement and its verification
criterion (§1.1) and the specifications behind them — Signals & Parameters,
the A2L, the DiagSpec, the communication database. Where those do not settle
a value, it is an Open Point, never a look at the implementation. Measurable
internal variables are named from the A2L/variable list, which is a
specification of what can be observed, not from the source.

## 1. Scope

Select requirements where **all** hold:

- `aFeature` = the target feature (must be in `qualification_test.valid_features`
  — if not, stop and ask rather than proceeding on an unrecognized feature name)
- `aTestability` = `test` — exclude `verification`, `test =>` and
  `verification =>` (owned by another test level)
- `aStatusOfAnalysis` ∈ `attributes.status_filter`
- `aRequirementObjectType` = `functional requirement` or `non functional requirement`
- Object Text is non-empty

Report: total objects for the feature, survivors at each filter, final in-scope
count.

### 1.1 `aTestCriteria` is the requirement's verification criterion

Each requirement's `aTestCriteria` states how the requirement is to be shown
fulfilled — the verification criterion SWE.1 asks every requirement to carry.
It is an input, not decoration, exactly as on the architecture side
(integration-test-patterns.md §1.3):

- **It names the pass criterion.** The one result marked as pass/fail (§7)
  implements it — the measurement, tolerance or observation it states. Where a
  generated case cannot follow it, say so in Open Points instead of
  substituting another criterion.
- **It can rule the test level out.** A criterion that asks for a review, an
  analysis or an inspection, or names another test level, gets **no** test
  case: list the requirement in Open Points with the criterion verbatim. If the
  requirement nevertheless has a concrete, observable behaviour in the
  specifications, that disagreement is a Phase-1 question — default proposal:
  author the case.
- **Empty** → derive the pass criterion from the requirement text, as before,
  and list the requirement once in Open Points as "no verification criterion:
  pass criterion derived from the requirement text", so the gap goes back to
  the requirement owner. This is not a Phase-1 question: it is common, and a
  question per requirement would bury the real ones.

Typos and case vary ("wehther", "CHnage") — match on meaning, and never copy a
misspelling into a generated case.

## 2. Existing coverage

Split the in-scope set into: **already covered** (leave alone unless asked to
re-derive), **not covered** (your generation scope), **partially covered**
(covered, but a clause of the requirement text has no corresponding test case —
say which clause).

## 3. Vocabulary resolution

List every signal, variable, parameter, state and error name needed. Name the
source for each: `docs.signals_params`, `docs.a2l_or_varlist`, `docs.diagspec`,
`docs.comm_database`, or an existing test case for this feature — never the
source code (§0). Any identifier that cannot be resolved goes to Open Points —
never invented, never a guessed variant of one you can see.

**Bus signals come from the communication database.** For a signal on CAN, LIN
or another bus, copy from `docs.comm_database` (DBC, LDF or ARXML system
extract): the signal and message name, its encoding (length, factor, offset,
physical min/max, unit), the message's cycle time, and any timeout or
invalid/init value it defines. A case that waits for a timeout, counts missed
cycles or sends an out-of-range raw value takes those numbers from there.
Without the database, write the signal name only where another source gives
it, and put every encoding, cycle time and timeout the case needs on Open
Points — never assume a common value such as a 10 ms cycle. Where Signals &
Parameters and the database disagree on a signal, that is an Open Point
(input hygiene), not a choice to make.

## 4. Structure

```
test group  (atsType = no testcase)
  └─ logical test case      (atsType = logical testcase)   ← only when parameterised
       └─ concrete test case (atsType = positive | negative | qualitative)
```

- A non-specific test case (heading, group, parameterised parent) goes in
  `Object Heading`; a specific test case goes in `Object Text`.
- In a logical test case, write parameters in square brackets with a question
  mark — `[EP_phiActuator = ?]` — and replace with concrete values in the
  children.
- In a concrete child, `atcPreconditions`/`atcActions`/`atcResult` may be left
  blank where unchanged from the parent.
- Every Object Heading / Object Text must be unique within the module.

## 5. Title convention

`TC_<what is being verified>`, followed where parameterised by the value in
square brackets, e.g. `TC_PosActuator_A1_ON_angle_with_in_range
[EP_phiActuator = 16.3°]`. The title states intent, not mechanism. No leading
number.

## 6. Boundary value rule

For a parameter given as `Name / Value / Min-Max / Resolution`:

| Point | Value | `atsType` |
|---|---|---|
| At the boundary | `boundary` | positive |
| One resolution step inside | `boundary ∓ Resolution` | positive |
| One resolution step outside | `boundary ± Resolution` | negative |

Apply only where a parameter with a stated resolution exists in
`docs.signals_params` — or, for a bus signal, in `docs.comm_database`, where the
signal's factor is its resolution and its physical min/max are its range.
Where a requirement states a limit but no backing parameter/resolution exists,
put it on Open Points rather than inventing a step size.

## 7. Writing the steps

- `atcPreconditions` — required ECU state, numbered or dash-prefixed.
- `atcActions` — numbered, one action per number; actions sharing a number run
  in parallel.
- `atcResult` — numbered to match actions. **Exactly one result marked as the
  pass/fail criterion.**
- `atcPostconditions` — how the system is left.
- Two test cases distinguishable only by title are redundant — merge them; the
  distinction must be visible in `atcPreconditions`/`atcActions`.
- Expected results must be unambiguous: name the exact variable and value
  (`"CDD_Sent_XCP_Angle_g_u16 is updated to 163"`), never a vague description.

## 8. Attributes specific to this skill

| Attribute | How to fill |
|---|---|
| `atcRemark` | `Series SW` or `Debug SW`, per the feature's entry in the Test Plan (`docs.test_plan`). Without a Test Plan — or with a feature it does not list — ask once, as a Phase-1 question, and record the answer in the manifest (`feature.test_software`) so later runs reuse it. Never guess it: a case meant for Series SW that relies on a Debug SW variable cannot run |
| `aFeature` | The target feature |
| `atsClassification` | Per `attributes.classification_rule`, derived from the linked requirement's safety/security/regulatory/OBD attributes where the governing matrix defines that mapping — state your reasoning in Open Points whenever the case falls to error-severity judgement (A/B/C) rather than a rule-driven class |
| `atsTestKind` | `Functional test` by default; the robustness/EMC wording for robustness cases; `Performance test` for timing/resource cases |
| `atsTestDesignTechnique` | `RequirementsBased` always; add `BoundaryValueAnalysis` for boundary cases, `EquivalenceClasses` for class representatives, `ErrorGuessing` for cases with no requirement link. Multi-valued. |
| `atsType` | `positive` inside the specified range, `negative` outside it or for error guessing, `qualitative` for non-functional cases |

## 9. Diagnostic feature templates

Use only when the target feature is diagnostic. Slots come from
`docs.diagspec`'s DID/RID tables.

**Read a DID — positive**
- Title: `TC_<DID Description>_APP` (or `_BL`)
- Action: `1. Send Diag Request for <DID Description> - 22 <byte1> <byte2>`
- Result: `<n>. Response: -62 <byte1> <byte2>`, value of the stated data type
  within the physical range
- One per readable DID per session where the read matrix says Y

**Read a DID in an unsupported session — negative**
- Candidates: every session where the read matrix says N
- If `qualification_test.nrc_table` is `not available`, write the expected
  response as `<expected NRC — to be completed>` and list the case in Open
  Points rather than guessing the NRC

**Write a DID — positive**
- Only for DIDs whose write matrix has a Y
- Action: enter the permitted session; `2E <byte1> <byte2> <data>`; read back
  with `22`
- Result: `-6E <byte1> <byte2>`, then the read-back returns the written value

**Routine control**
- `31 01 <RID>` to start; `31 03 <RID>` where a result record exists
- Honour the security level and session columns

If the DiagSpec's cover sheet notes an exception for services `0x22`/`0x2E`
(the service table not applying to them), take the per-DID matrices as
authoritative for those two services and flag the exception in Open Points.
