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

## Reference columns (beside the 21, never imported)

Columns DOORS never imports: an ID column that links each row to what it
tests — **always written** — and the validity columns for QA's validation,
declared once in the running skill's config block
(`integration_test.reference_columns` or `qualification_test.reference_columns`
in `ai_test_project.yaml`) instead of re-requested per run:

| Key | Column(s) | Position | Content |
|---|---|---|---|
| — always (SWE.5) | `Architecture Requirement ID` | **before** the 21 (column A) | the ID of the architecture object the row traces to — the same ID as in `Traceability`; empty on a heading row that has no object of its own |
| — always (SWE.6) | `Requirement ID` | **before** the 21 (column A) | the ID of the requirement the row traces to — every ID, separated by newlines, for a merged case; empty on a heading row |
| `validity_review` | `isValid`, `Reason for Invalid` | **after** the 21 | the validity policy in [no-fabrication.md](no-fabrication.md); QA's verdict, read back on a re-run (workflow-discipline.md §8) |

The 21 attributes stay **contiguous and in schema order** between them. State
the import consequence once — in the run summary, and as one Open Points row —
rather than leaving the reviewer to discover it: *a name-based DOORS import
filter is unaffected; a position-based one must skip the leading column and
drop the trailing ones.*

## Structure: heading rows vs. concrete-case rows

A heading row (module, interface, test group, parameterised logical parent) is
included as its own row with `atsType`, `atsRegression`, `atsClassification`
and `atsState` all set to `no testcase`, so the DOORS hierarchy is reproducible
from the sheet alone. For SWE.5 that is two levels — a module-level heading
(`FUSA_MotCtrl`, `Mot_Drv`) opening the section, then an interface-level heading
per port or connection (`P_Mot_Mov_Data`, `FUSA-MotCtrl to CDD_Drv`) — and the
sheet carries one such section per module **authored**: the target's always,
a peer's only under `peer_depth: peer_ports` or with mirroring on
(integration-test-patterns.md §2–§3). A peer that is only named inside the
cases gets no section. A concrete test case is a row with a real `atsType`
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
| `atsClassification` | Per `attributes.classification_rule` — **not** a constant. A tier decided by a configured `attributes.classification_attribute_rules` entry is applied mechanically and cited in `Traceability` (rule + the attribute value it matched); every other choice is a judgement, justified in Open Points. An empty attribute cell matches no rule, and a rule whose column is missing from this skill's export is skipped (workflow-discipline.md §1.3) — both leave the case to judgement. |
| `atsTestExecution` | `automated` unless the case genuinely cannot be automated. |
| `atsTestEnvironment` | From `ai_test_project.yaml` `attributes.environment`. |
| `atsState` | `in work`. **Never `agreed`.** |
| `aChangeRequID` | Empty on a module's or feature's first run. On a re-run, a case added or updated because its object is new or changed carries that object's `aChangeRequID`, copied verbatim (workflow-discipline.md §8). |

Everything else (`atcPreconditions`/`atcActions`/`atcResult`/`atcPostconditions`,
`atcRemark`, `aFeature`, `atsTestKind`, `atsTestDesignTechnique`, `atsType`) is
skill-specific — see `integration-test-patterns.md` / `qualification-test-patterns.md`.

## The 3-sheet workbook contract

**Sheet 1 — `Test Cases`.** The 21 columns above, in the order for the running
skill — framed by the configured reference columns, if any, and nothing else.

**Sheet 2 — `Traceability`.** One row per generated test case: proposed title,
the requirement/architecture object it covers (and, for SWE.6, which clause of
the requirement text). For SWE.5 also: the interface, its data type, the
**writer** module/file and the **reader** module/file, each breakpoint's
**`.c` file and line number** with the **source revision** they were read at
(integration-test-patterns.md §9), which module's section the row sits under,
whether the row is the **primary** or a **mirror** (§3), and which range the
Min/Mid/Max values came from — the documented `Range:` or the implementation
type's limits (§5.2). For SWE.6 also: each merged requirement with the
result step that checks it, the reference specification, version and section a
value or procedure came from (qualification-test-patterns.md §3.1), the
catalogue row (`CID`) behind each means, and any fault-injection variable
named from the code — marked `from code`, with file and line (§0). The engineer creates the DOORS links by hand from this
sheet — it must be complete and readable on its own.

**A case with no object of its own.** A pattern sometimes requires a case that
has no architecture or requirement object to trace to — the standing example is
a P-05 Init case where the runnables group lists only the cyclic runnable. Link
it to the **nearest ancestor** object (there, the runnables group), mark the
link as `ancestor` in `Traceability`, and raise an `Input hygiene` Open Point
recommending that the source document gain the missing object. Never leave the
link empty, and never link to a sibling that merely looks related.

The integration-test and qualification-test DOORS modules share the `SW_TST-`
prefix and their ID numbers **collide** — a reference to an *existing* test
case (in Open Points, in a "already covered" note, anywhere) must always name
the module (SWE.5 or SWE.6) alongside the ID, never the bare ID alone.

**Sheet 3 — `Open Points`.** Every unresolved symbol/value, every
classification judgement, every requirement/interface you could not cover and
why, every assumption made, every spelling variant normalized. Every row
carries a `Category` — `Unresolved`, `Not covered`, `Classification`,
`Spelling variant`, `Decision`, or `Input hygiene` (workflow-discipline.md §7)
— so the input defects, which belong to other owners (the architect, the code
owner, the DOORS admin), can be filtered out and passed on.

**Formula-prone cells.** Any cell whose text begins with `-`, `=`, `+` or `@` —
which is every `atcPreconditions` and `atcPostconditions` block, since both
start with `- ` — must be written with `quotePrefix` set on the cell style, so
Excel does not convert it to a formula the moment a reviewer clicks into it.
Observed: cell `E4` of a returned, engineer-validated workbook had become an
array formula displaying `#NAME?`, silently destroying the preconditions of
that test case.

## Output location & filename

- `integration-test` → `20_AI/IntegrationTest/<MODULE>_SWE5_TestCases.xlsx`
- `qualification-test` → `20_AI/QualificationTest/<FEATURE_SLUG>_SWE6_TestCases.xlsx`

On a re-run (workflow-discipline §8), update the existing workbook in place per
the delta rather than creating a new dated copy.
