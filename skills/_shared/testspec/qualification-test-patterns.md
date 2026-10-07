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

**One narrow exception: the name of a fault-injection variable.** A fault
condition (a sensor fault, a lost signal, a corrupted counter) is often injected
by writing a variable over XCP, and the A2L alone may not say which variable
produces which fault. Then the code may be searched for **the name only** of a
variable that injects the requirement's fault condition, and only where the
A2L/variable list does not settle it. That name:

- must exist in `docs.a2l_or_varlist` — XCP reaches only what the A2L
  describes; a variable the A2L lacks cannot be written on the bench, and is an
  Open Point;
- is marked `from code` in `Traceability`, with file and line, and is offered
  as a proposal in the Phase-1 catalogue (§3.2), never used unconfirmed;
- carries **nothing else** from the code — not the value to write, not the
  expected reaction, not a debounce time or threshold. Those still come from
  the requirement and its specifications, or are Open Points.

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
`docs.comm_database`, a reference specification (`docs.reference_specs`, §3.1), or an
existing test case for this feature — never the source code (§0). Any identifier that cannot be resolved goes to Open Points —
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

**No database notation in test text.** Write a signal's layout in words —
"start bit 23, length 9 bits", "factor 0.1, offset 0" — never in a database
tool's shorthand such as `(23|9)` or `[0.1,0]`. The reviewer and the bench
operator read the case, not the DBC.

**Name the kind of every item.** The first time a case names a message,
signal or variable, say which it is — "message `<Msg>`", "signal `<Sig>` in
message `<Msg>`", "XCP variable `<Var>`" — so nobody has to guess what a bare
identifier refers to.

### 3.1 Reference specifications

Some behaviour is defined outside the requirements: in an OEM performance
specification, a network-management specification or test catalogue, a
standard. Requirements cite such documents, or rely on them without naming
them. They are **reference specifications**: sources of values and
procedures, like the communication database. They are **not** the test basis —
every case still traces to a requirement.

- **Registered once for the project.** They apply across features (a CAN
  specification serves every CAN feature), so they are listed in
  `ai_test_project.yaml` under `docs.reference_specs` — title, version, path —
  never per feature.
- **Asked at the start of every run** (Step 3, the input confirmation). Read
  the in-scope requirements, list every document they cite, and match each
  against the registered list. Show both in the inputs table: the registered
  ones that will be used, and the cited ones not registered. For each missing
  one, ask for the file, or a recorded `N/A` with the reason, and write the
  answer to the list. A run whose requirements cite nothing new asks nothing.
- **Read every registered specification, not only the cited one.** Search all
  of them for the behaviour a requirement names — a network-management test
  catalogue applies to the network-management requirements whether or not they
  cite it by name.
- **Use the version supplied.** Where a requirement cites a different version
  of a registered document, use the supplied version — do not stop or ask. In
  `Traceability`, record the version the requirement cites next to the version
  read, and raise **one** `Input hygiene` Open Point per document (not per
  case), naming both versions and the requirements citing the other one, so the
  difference stays visible to the requirement owner.
- **Read the relevant sections only.** These documents run to hundreds of
  pages. Read the sections that define the behaviour a requirement names, and
  record them in `last_run.reference_specs`.
- **Cite it like any other source.** A value or behaviour taken from it names
  the document, its version and the section in `Traceability`.
- **A test specification is a procedure source.** Where a reference
  specification is itself a test specification and one of its tests covers the
  requirement, follow that test's conditions and steps and put its test ID in
  `atsReference`, rather than writing a procedure of your own. Whether a case
  that only repeats an OEM test is wanted at all — or is already covered by the
  OEM's own testing — is one Phase-1 question per document, not per case.
- **Language.** A reference specification may be in another language. The
  case text stays in the workbook's language; test IDs, signal names and
  section titles are quoted as the document writes them.
- **Not available** (`N/A` recorded) → every requirement that depends on it is
  listed in Open Points with the document named, and gets no case with a
  placeholder pass criterion.

### 3.2 Stimulus and observation catalogue (Phase 1)

A case is only executable if it says **how** each stimulus is applied and
**where** each observation is read. Before proposing cases, list every item
the proposed cases will set or read, as its own sheet `Catalogue` in the
Phase-1 workbook (workflow-discipline §5), one row per item:

`CID | Item | Kind (message / signal / variable / DID / I/O / supply) | Source |
Set by | Read in | Manual steps | Series SW | Debug SW | Answer | Status`

- **Set by / Read in** — the means: a CANoe panel and the control on it,
  rest-bus simulation, an XCP measurement or calibration window, a CAPL
  function, the diagnostic tester, a HIL channel, the power supply, the CANoe
  Trace or Graphics window. Taken from `docs.test_environment` (including the
  CANoe configuration's panel list, where supplied). Where it does not name
  the panel or control, the AI proposal says what is needed (e.g. "a panel
  control that sets signal `<Sig>`") and the engineer names it — **never
  invent a panel or control name**.
- **Manual steps** — how an operator does it by hand, step by step (open which
  panel, which control, which value, which button). The generated cases repeat
  these steps, so a case can be run manually as well as automated.
- **Series SW / Debug SW** — whether the item exists on each software. An XCP
  or A2L variable may exist on Debug SW only; a case for a feature tested on
  Series SW (§8, `atcRemark`) may not depend on it.
- **One answer per row.** Each row is answered on its own — never "confirm the
  whole table" as one question (workflow-discipline §5, one question per QID).
- **Cached for the project.** Means belong to the bench, not to a feature:
  confirmed rows are written to `qualification_test.bench_catalogue` in
  `ai_test_project.yaml`, and the next feature shows them as already confirmed
  and asks only about new items. A cached row whose item is not in this run's
  inputs any more is reported, not deleted.

An item whose means stays unconfirmed is not used: the case that needs it is an
Open Point.

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

**Only on a quantity the bench can set.** A boundary value is a stimulus, so
the quantity must have a confirmed **Set by** means in the catalogue (§3.2): a
signal the ECU *receives* (set by rest-bus simulation or a panel), an
XCP-writable variable, a supply voltage. A database factor and range make a
signal *reportable*, not settable — a signal the ECU *sends* cannot be set to
its boundary. For such a dependent quantity (a measured current, a computed
angle, a reported status), drive the **source** to an operating point that
puts it at the boundary, and capture the source and the reported signal
together; the pass criterion compares the two within the stated resolution. If
no settable source drives it, the boundary is an Open Point.

## 7. Writing the steps

- `atcPreconditions` — required ECU state, numbered or dash-prefixed. A
  precondition must not contradict the case's own actions (a precondition
  "signal `<Sig>` absent" for a case whose first action sets `<Sig>`).
- `atcActions` — numbered, one action per number; actions sharing a number run
  in parallel.
- `atcResult` — numbered to match actions. **Exactly one result marked as the
  pass/fail criterion.**
- `atcPostconditions` — how the system is left.
- Two test cases distinguishable only by title are redundant — merge them; the
  distinction must be visible in `atcPreconditions`/`atcActions`.
- Expected results must be unambiguous: name the exact variable and value
  (`"CDD_Sent_XCP_Angle_g_u16 is updated to 163"`), never a vague description.

**Every action names its means.** Each `atcActions` entry opens with the means
from the catalogue (§3.2) in square brackets, then the item with its kind, then
the value:

```
1. [CANoe panel <Panel> / <Control>] Set signal <Sig> (message <Msg>) to <value>.
   Manual: open panel <Panel>, enter <value> in <Control>, press <Button>.
2. [XCP] Write variable <Var> = <value>.
3. [Rest-bus simulation] Stop sending message <Msg>.
4. [Diagnostic tester] Send 22 <byte1> <byte2>.
```

- The `Manual:` line repeats the catalogue row's manual steps, so the case can
  be run by hand. Leave it out only where the means is already a single manual
  action (a diagnostic request typed into the tester).
- **Never write a state as an action.** "ECU is in normal mode" or "the fault is
  active" is not something an operator does. Either it is a precondition, or
  the action says how it is brought about (`[XCP] Write variable <Var> =
  <value>`).
- A bare identifier ("Record `<X>`") is never enough: say whether `<X>` is a
  message, signal or variable, and where it is recorded.

**Every result names what is observed and where.** Each `atcResult` entry opens
with the observation means from the catalogue, then the item, then the
expected value:

```
1. [CANoe Trace] Message <Msg> is sent every <cycle> ms; signal <Sig> = <value>.
2. [XCP measurement] Variable <Var> = <value>.
```

- **An internal state is not an observation.** "The ECU uses the substitute
  value" or "the mode is active" cannot be checked; name the signal or the
  A2L variable that shows it. If none exists, the requirement is an Open
  Point.
- **No result on what the case removed.** A result may not expect a value from
  a signal or message the case's own actions stopped or removed from the bus.
- **Windows come from the inputs.** An observation window ("absent for
  ≥ N ms", "within N cycles") uses a cycle time, timeout or timing from a
  supplied input — the communication database, the requirement, a cited
  specification — and cites it. Never pick a window because it looks
  reasonable.

**Merged requirements — one case, one pass/fail result.** Requirements that
are outcomes of the **same stimulus setup** (the same preconditions and
actions, different observations) may share one case. A merge is **proposed**
in the Phase-1 proposed-cases table, listing the requirements it covers, and
made only once confirmed. The merged case still has exactly one result marked
as the pass/fail criterion: it covers every merged requirement together, and
the case passes or fails as a whole — the verdict is kept on the test case,
not per requirement. `Traceability` lists each merged requirement, with the
clause and the result step that checks it.

## 8. Attributes specific to this skill

| Attribute | How to fill |
|---|---|
| `atcRemark` | `Series SW` or `Debug SW`, per the feature's entry in the Test Plan (`docs.test_plan`). Without a Test Plan — or with a feature it does not list — ask once, as a Phase-1 question, and record the answer in the manifest (`feature.test_software`) so later runs reuse it. Never guess it: a case meant for Series SW that relies on a Debug SW variable cannot run. Every item a case sets or reads must exist on that software (the catalogue's Series SW / Debug SW columns, §3.2); one that does not is an Open Point |
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
