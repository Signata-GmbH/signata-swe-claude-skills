# Qualification-test (SWE.6) mechanics

> Loaded by `qualification-test/SKILL.md` on top of
> [workflow-discipline.md](workflow-discipline.md),
> [no-fabrication.md](no-fabrication.md), and
> [output-format.md](output-format.md).

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

## 2. Existing coverage

Split the in-scope set into: **already covered** (leave alone unless asked to
re-derive), **not covered** (your generation scope), **partially covered**
(covered, but a clause of the requirement text has no corresponding test case —
say which clause).

## 3. Vocabulary resolution

List every signal, variable, parameter, state and error name needed. Name the
source for each: `docs.signals_params`, `docs.a2l_or_varlist`, `docs.diagspec`,
or an existing test case for this feature. Any identifier that cannot be
resolved goes to Open Points — never invented, never a guessed variant of one
you can see.

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
`docs.signals_params`. Where a requirement states a limit but no backing
parameter/resolution exists, put it on Open Points rather than inventing a step
size.

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
| `atcRemark` | `Series SW` or `Debug SW`, per the feature's entry in the Test Plan |
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
