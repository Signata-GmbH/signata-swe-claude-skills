# DOORS test-case output format (shared by both skills)

## The 21-column schema

Both SWE.5 and SWE.6 DOORS exports use the same 21 attributes. **Only the
position of two columns differs** — see below.

`ID`, `Object Heading` / `Object Text` (order per skill), `Object Text` /
`Object Heading`, `atcPreconditions`, `atcActions`, `atcResult`,
`atcPostconditions`, `atcRemark`, `atsReference`, `aVariant`, `atsRelease`,
`aFeature`, `atsRegression`, `atsClassification`, `atsTestKind`,
`atsTestDesignTechnique`, `atsType`, `atsTestExecution`, `atsTestEnvironment`,
`atsState`, `aChangeRequID`

- **integration-test (SWE.5)**: `Object Heading` comes **before** `Object Text`.
- **qualification-test (SWE.6)**: `Object Text` comes **before** `Object
  Heading`.

Get this backwards and the workbook won't align with the DOORS import filter —
confirm which skill is running before writing the header row.

## Structure: heading rows vs. concrete-case rows

A heading row (module, interface, test group, parameterised logical parent) is
included as its own row with `atsType`, `atsRegression`, `atsClassification`
and `atsState` all set to `no testcase`, so the DOORS hierarchy is reproducible
from the sheet alone. A concrete test case is a row with a real `atsType`
(`positive` / `negative` / `qualitative`, or `logical testcase` for a SWE.6
parameterised parent).

## Attribute values common to both skills

| Attribute | Rule |
|---|---|
| `ID` | **Always empty.** DOORS assigns it and never reuses a deleted one. |
| `atsReference` | Empty unless the case has no requirement/architecture link — then state the origin (norm, standard, error tracker ID, `error guessing execution`). |
| `aVariant` | From `ai_test_project.yaml` `release.variants`. |
| `atsRelease` | From `ai_test_project.yaml` `release.id`. |
| `atsRegression` | `new`. |
| `atsClassification` | Per `attributes.classification_rule` — **not** a constant; justify every choice in Open Points. |
| `atsTestExecution` | `automated` unless the case genuinely cannot be automated. |
| `atsTestEnvironment` | From `ai_test_project.yaml` `attributes.environment`. |
| `atsState` | `in work`. **Never `agreed`.** |
| `aChangeRequID` | Empty. |

Everything else (`atcPreconditions`/`atcActions`/`atcResult`/`atcPostconditions`,
`atcRemark`, `aFeature`, `atsTestKind`, `atsTestDesignTechnique`, `atsType`) is
skill-specific — see `integration-test-patterns.md` / `qualification-test-patterns.md`.

## The 3-sheet workbook contract

**Sheet 1 — `Test Cases`.** Exactly the 21 columns above, in the order for the
running skill.

**Sheet 2 — `Traceability`.** One row per generated test case: proposed title,
the requirement/architecture object it covers (and, for SWE.6, which clause of
the requirement text), the interface + sender/receiver modules (SWE.5 only).
The engineer creates the DOORS links by hand from this sheet — it must be
complete and readable on its own.

The integration-test and qualification-test DOORS modules share the `SW_TST-`
prefix and their ID numbers **collide** — a reference to an *existing* test
case (in Open Points, in a "already covered" note, anywhere) must always name
the module (SWE.5 or SWE.6) alongside the ID, never the bare ID alone.

**Sheet 3 — `Open Points`.** Every unresolved symbol/value, every
classification judgement, every requirement/interface you could not cover and
why, every assumption made, every spelling variant normalized.

## Output location & filename

- `integration-test` → `20_AI/IntegrationTest/<MODULE>_SWE5_TestCases.xlsx`
- `qualification-test` → `20_AI/QualificationTest/<FEATURE_SLUG>_SWE6_TestCases.xlsx`

On a re-run (workflow-discipline §8), update the existing workbook in place per
the delta rather than creating a new dated copy.
