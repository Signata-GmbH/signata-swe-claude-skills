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
internal variables are named from `docs.a2l_or_varlist` or `docs.variable_list`
(§3.3) — lists of what can be observed, not specifications of values — never
from the source.

**One narrow exception: the name of an injection variable.** Some inputs
cannot be driven physically on the bench: a fault condition (a sensor fault, a
lost signal, a corrupted counter), and any other input the bench has no
physical source for — an ADC voltage, a sensor angle, a hardware-ID pin, a
supply measurement. Such an input is injected by writing a variable over XCP,
and the A2L or the variable list alone may not say which variable feeds which
input. Then the code may be searched for **the name only** of a variable that
injects the requirement's stimulus, and only where the A2L/variable list does
not settle it. That name:

- must exist in `docs.a2l_or_varlist` — or in `docs.variable_list` where
  `qualification_test.debug_means` is `xcp_varlist` or `xcp_and_debugger`
  (§3.3). XCP reaches only what those describe; a variable in neither cannot
  be written on the bench, and the case that needs it is written blocked —
  `bench capability not confirmed` (§13), never dropped;
- is marked `from code` in `Traceability`, with file and line, and is offered
  as a proposal in the Phase-1 catalogue (§3.2), never used unconfirmed;
- carries **nothing else** from the code — not the value to write, not the
  expected reaction, not a debounce time or threshold. The value written is the
  requirement's stimulus value, converted with the scaling confirmed at
  Phase 1 (§3); the expected result comes from the requirement and its
  specifications, or is an Open Point.

**When the engineer asks for a value "from the code".** An engineer stuck on
a question may suggest reading the source ("check the code for which request
drives forward"). Decline, say why in one sentence — the expected result would
then be whatever the code does — and search the **supporting specifications**
instead (§3): requirements of other features, the system requirements, the
architecture text. Offer what they establish as the proposal, with each source
and any source that contradicts it. *(Observed: a motor-direction mapping no
in-feature input gave was settled from three specification sources — a
direction-naming requirement, a sensor-direction requirement and the end-stop
positions in the system requirements — with a fourth system requirement
flagged as contradicting them.)*

## 1. Scope

Select requirements where **all** hold:

- `aFeature` = the target feature (must be in `qualification_test.valid_features`
  — if not, stop and ask rather than proceeding on an unrecognized feature name).
  Not cached and not an `aFeature` value in the export either → offer the
  nearest `aFeature` values as a popup, each with its object count and the
  `aFunctionModule` values its objects carry. If the argument looks like a
  module (it names one, or a module's requirements are spread over several
  features), say which features that module's requirements carry — the
  engineer may want one of them, or one with `scope.requirement_ids`
  narrowed to that module's objects.
- `aTestability` = `test` — exclude `verification`, `test =>` and
  `verification =>` (owned by another test level)
- `aStatusOfAnalysis` ∈ `attributes.status_filter`
- `aVariant` carries one of `release.variants` — a two-line cell
  (`MQB\nCEA`) is split on its newlines and matches when any line matches.
  What this filter removes is reported by variant at the Phase-1 gate (§1.2),
  never dropped silently.

An object must also **be a requirement** to be counted at all:
`aRequirementObjectType` = `functional requirement` or `non functional
requirement`, and Object Text non-empty. Headings and information objects are
not requirements; they are counted separately in the report, not as attrition.

Report: total objects for the feature, survivors at each filter, final in-scope
count. **The four filters — feature, testability, status, variant — are the
only reasons a requirement leaves scope**, and the attrition report names no
other.

**No requirement leaves scope at classification.** Every in-scope requirement
gets **at least one proposed case** at Phase 1 and is written in Phase 2,
blocked where something is missing (§13). The skill never rules a requirement
out on its own judgement — not because it reads like integration level, a
read cycle or a peripheral configuration; not because its observable is an
internal value or its stimulus cannot be driven physically (§0, §3.3, §7); not
because it delegates to a specification (§3.4); not because an OEM test
package or an existing test case covers it (§2, §3.1). A doubt about the test
level or the observable is written to the `Requirements Hygiene` sheet
(`possibly integration level`, `observable not on bench`, §12) with its owner,
**and** the case is still proposed and written. Only the engineer takes a
requirement's case away, at the coverage gate (workflow-discipline §5), as a
recorded decision. *(Observed, one project's second stage: requirements in
scope with no generated case, for five reasons — an internal observable
reachable only by XCP on a symbol absent from the A2L or by a debugger;
read-cycle and peripheral-configuration requirements classed as integration
level; a stimulus that had to be injected by writing a calibration;
requirements delegating to a specification classed as configuration review or
"covered by the OEM package"; and a variant excluded by `release.variants`.
Each was the skill's own decision, and none was shown to the engineer as a
gap.)*

### 1.1 `aTestCriteria` is the requirement's verification criterion

Each requirement's `aTestCriteria` states how the requirement is to be shown
fulfilled — the verification criterion SWE.1 asks every requirement to carry.
It is an input, not decoration, exactly as on the architecture side
(integration-test-patterns.md §1.3):

- **It names the pass criterion.** The case's results (§7) implement it — the
  measurement, tolerance or observation it states. Where a
  generated case cannot follow it, say so in Open Points instead of
  substituting another criterion.
- **It may name another level or method — the case is still written.** A
  criterion that asks for a review, an analysis or an inspection, or names
  another test level, does not take the requirement out of scope: its
  `aTestability` says `test`. The case is proposed and written from the
  requirement text and its specifications as usual (§1), the criterion is
  quoted verbatim on the `Requirements Hygiene` sheet as `possibly integration
  level` with the requirements engineer as owner (§12), and the proposed-cases
  table marks the case so the engineer sees the conflict at the coverage gate
  (workflow-discipline §5).
- **Empty** → derive the pass criterion from the requirement text, as before,
  and list the requirement once in Open Points as "no verification criterion:
  pass criterion derived from the requirement text", so the gap goes back to
  the requirement owner. This is not a Phase-1 question: it is common, and a
  question per requirement would bury the real ones.
- **An engineer or QA answer overrides it.** Where a Phase-1 answer (or a
  validity reason on a re-run) contradicts a step the criterion prescribes —
  the stimulus it names does not produce the behaviour, the value it names
  cannot occur — the **answer wins**: the criterion-derived step is dropped
  from the case, the case is built on the answer, and the conflict goes to the
  `Requirements Hygiene` sheet (§12) and Open Points as `Input hygiene` for
  the requirement owner, quoting both. Never keep both readings — a separate
  case for the answer *and* the contradicted step in the original case — and
  never leave a step the run's **own** Open Point doubts in a case presented
  as runnable: either the step goes, or the case is blocked — `two inputs
  contradict each other` — with a `Notes` entry naming that Open Point (§13). *(Observed: the criterion said "set an out-of-range angle and
  read 4095"; the Phase-1 answer said 4095 appears only when the sensor loses
  its magnet. The run wrote the magnet-loss case, kept the out-of-range step
  in the range case, and doubted that step in an Open Point. QA rejected the
  case.)*
- **An error-guessing line in the criterion is an assumption, not a pass
  criterion.** Criteria sometimes end with an expectation that no requirement
  text or specification states ("reset to Init → Intermediate to be sent").
  Such an expectation is raised as a Phase-1 **question** whose proposal is
  the criterion's expectation, so the engineer confirms or corrects it before
  it decides pass or fail. Confirmed → the case is written to it, the
  confirmation recorded (workflow-discipline §4), `atsTestDesignTechnique`
  carries `ErrorGuessing`. Unanswered → the case is generated with the
  criterion's expectation as its assumption, blocked — `needs
  clarification` — with a `Notes` entry naming the question (§13), and an
  Open Point of category `Decision`. `atcRemark` is not the place for it: it carries the software
  level (§8). *(Observed: an Init-during-replacement case made "Intermediate
  stays" the pass criterion straight from the error-guessing line; QA
  expected the actuator to return to its position.)*

Typos and case vary ("wehther", "CHnage") — match on meaning, and never copy a
misspelling into a generated case.

### 1.2 Variant scope report (Phase-1 gate)

The variant filter removes requirements whose every other attribute is in
order, so its effect is the easiest to miss. At the Phase-1 gate, for the
chosen `release.variants`, report the requirements that pass the feature,
testability and status filters but not the variant filter, grouped by the
variant value they carry:

`Variant | Requirements excluded | IDs`

and ask **one question per variant** (workflow-discipline §5): "Proposal:
include the <n> requirements carried only by variant `<V>` (<IDs>) in this
run; their cases carry `aVariant` = `<V>`. Accept?" — "No" keeps them out.
Record the answer in the manifest (`scope.included_variants`, with its source,
workflow-discipline §4) so later runs of the feature reuse it, and add the
included requirements to the scope like any other: they get proposed cases
and count at the coverage gate. A run in which the variant filter removes
nothing says so in one line. *(Observed: thirteen requirements of a bus
feature carried only by a second variant were excluded with no line saying
so.)*

## 2. Existing coverage

Split the in-scope set into: **already covered**, **not covered**, **partially
covered** (covered, but a clause of the requirement text has no corresponding
test case — say which clause). The split is **information, not a filter**:
every in-scope requirement still gets at least one proposed case (§1),
whichever group it falls in. A requirement the existing cases cover is marked
in the proposed-cases table with the existing case named (module and ID,
output-format.md), so the engineer can decline the new case at the coverage
gate (workflow-discipline §5) — a recorded decision, never the skill's. The
existing cases are not counted by the coverage gate.

## 3. Vocabulary resolution

List every signal, variable, parameter, state and error name needed. Name the
source for each: `docs.signals_params`, `docs.a2l_or_varlist`,
`docs.variable_list` (§3.3), `docs.diagspec`, `docs.comm_database`, a reference
specification (`docs.reference_specs`, §3.1), or an existing test case for this
feature — never the source code (§0). Any identifier that cannot be resolved goes to Open Points —
never invented, never a guessed variant of one you can see.

**Supporting specifications.** Where the feature's own inputs do not settle a
value, a mapping or a stimulus (which request moves the actuator which way,
which supply value the ECU reports for a set voltage, which task period
applies), search the specifications that are already supplied for other
purposes: **requirements of other features** in the same export, the **system
requirements** export, and the **architecture** text. Use what they state,
cite the object ID in `Traceability` as *supporting* — the case never traces
to it — and raise one `Input hygiene` Open Point where two of them disagree.
Offer anything they settle as the Phase-1 proposal, with its sources; it is
still the engineer's to accept.

**A2L items without a scaling.** An A2L `MEASUREMENT` or `CHARACTERISTIC` with
`NO_COMPU_METHOD` has no physical unit. For every one a case writes or checks
with a physical value, ask its scaling as its own Phase-1 question, with a
**concrete** proposal ("1 mV per LSB, so 16 V = 16000") taken from a
related item where one exists (the bus signal carrying the same quantity, a
parameter's specified default compared against the same variable's other
form). Never propose reading the raw value on the bench and scaling it there:
it puts a symbol for an unknown number into the case (§7) and a "Yes" to it
settles nothing (workflow-discipline §5). Unanswered → the case is written
with the proposed scaling's numbers and blocked — `needs clarification` —
with the scaling stated as an assumption in `Notes` (§13). A symbol from
`docs.variable_list` (§3.3) is treated the same way: a map file or ELF export
carries no scaling and often no data type, so both are asked per symbol, with
a concrete proposal. *(Observed: "R16 × 5 / 16" —
"note the raw value for 16 V, then write 5/16 of it" — was accepted at
Phase 1 and then returned by QA as "What is R16?".)*

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

**Every parameter a case depends on states where its value comes from.** A
calibration or timing parameter that an expected result rests on — a recovery
time, a debounce, a limit, a threshold — is established in the preconditions
in one of three ways, and the step says which:

- **read** — `Verify XCP variable <Var> = <value> (<Param>, SW_Param-n)` /
  a DID read-back, where the A2L or the DiagSpec exposes it;
- **set** — `Write XCP variable <Var> = <value>`, then the read-back check,
  where a writable item exists in the catalogue (§3.2);
- **fixed** — a precondition stating `<Param> = <value> (<source>) is fixed
  in this SW build and not readable on the bench`, where neither exists.

A parameter with none of the three — its value is not in Signals &
Parameters, the A2L, the DiagSpec or a specification — leaves the case
blocked — `needs clarification` — with the value it assumes and the
parameter named in `Notes` (§13). Keep a **parameter table** in the Phase-1
analysis: parameter, value and source, means (read / set / fixed / none),
every case that uses it. A verdict reached for one requirement ("not in the
A2L, cannot be set") applies to **every** case in the table that uses the
parameter, in this run and in the cache for later ones — never to the one
requirement where it was first noticed. *(Observed: two cases built a 400 ms
window on a recovery-time parameter with no step saying where the 400 ms came
from, while an Open Point for a third requirement had already concluded the
same parameter was not in the A2L. QA rejected both: "how are you setting it,
and where".)*

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
- **Mandatory for a spec-governed feature.** Some features' behaviour is
  *defined* by an OEM or standard specification and merely transcribed by the
  SW requirements: end-to-end protection (counter and checksum rules, the
  receiver state machine, recovery after a gap, when an error is documented),
  network management (the state machine, the first state after wake-up,
  minimum active times, timeouts), diagnostics, bus communication. For a
  feature listed in `qualification_test.spec_governed_features`, the named
  document is a **mandatory input**: a run without it stops at the gate like
  any other mandatory input (workflow-discipline §1.1), because the cases need
  the state machine, the timings and the error-handling rules the requirement
  only points at. Every state, timing and error-handling rule a case checks
  then cites the specification's section beside the requirement. *(Observed:
  of nineteen customer HiL findings on one release, the network-management
  start-up state, the end-to-end recovery after a reception gap and the rule
  for documenting a changed error type were each decided by the OEM
  specification, not by the SW requirement that cited it.)*
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
  `atsReference`, rather than writing a procedure of your own. The case is
  written whether or not the OEM tests the same behaviour in its own package:
  "covered by the OEM test package" is **never a reason to omit a case** — it
  may appear only as a note in the case's `Traceability` row (§1).
- **Language.** A reference specification may be in another language. The
  case text stays in the workbook's language; test IDs, signal names and
  section titles are quoted as the document writes them.
- **Not available** (`N/A` recorded) → every requirement that depends on it is
  listed in Open Points with the document named. Its case is still written,
  with the values the Phase-1 proposals give, and blocked — `needs
  clarification` — naming the document in `Notes` (§13); never a case with a
  placeholder pass criterion.

### 3.2 Stimulus and observation catalogue (Phase 1)

A case is only executable if it says **how** each stimulus is applied and
**where** each observation is read. Before proposing cases, list every item
the proposed cases will set or read, as its own sheet `Catalogue` in the
Phase-1 workbook (workflow-discipline §5), one row per item:

`CID | Item | Kind (message / signal / variable / injection variable / DID /
I/O / supply / breakpoint at symbol / debugger variable) | Source | Set by |
Read in | Manual steps | Series SW | Debug SW | Answer | Status`

The two debugger kinds are offered only where `qualification_test.debug_means`
is `xcp_and_debugger`, and only for Debug-SW cases (§3.3); an `injection
variable` is a variable written to stand in for an input the bench cannot
drive physically (§0), marked `from code` in `Source` where its name came from
the code search.

- **Set by / Read in** — the means: a CANoe panel and the control on it,
  rest-bus simulation, an XCP measurement or calibration window, a CAPL
  function, the diagnostic tester, a HIL channel, the power supply, the CANoe
  Trace or Graphics window. Taken from `docs.test_environment` (including the
  CANoe configuration's panel list, where supplied). Where it does not name
  the panel or control, the AI proposal says what is needed (e.g. "a panel
  control that sets signal `<Sig>`") and the engineer names it — **never
  invent a panel or control name**.
- **Manual steps** — how an operator does it by hand, step by step (open which
  panel, which control, which value, which button). The generated steps are
  written from these, in plain words (§7), so a case can be run manually as
  well as automated.
- **Series SW / Debug SW** — whether the item exists on each software. An XCP
  or A2L variable may exist on Debug SW only; a case for a feature tested on
  Series SW (§8, `atcRemark`) may not depend on it unblocked — it is written
  blocked (§8, §13), or, for a debugger kind, moved to Debug SW by a Phase-1
  answer (§3.3).
- **One answer per row.** Each row is answered on its own — never "confirm the
  whole table" as one question (workflow-discipline §5, one question per QID).
- **`Answer` is the engineer's column — leave it empty.** A cached row shows
  `confirmed` in `Status` and the cache in `Source`; a row with something
  still to ask puts the question in `Manual steps` or `Item` and leaves
  `Answer` blank. A pre-filled `Answer` cell reads as answered, and gets
  skipped. *(Observed: a row asking whether a development message exists on
  Series SW had the question written into `Answer`; it came back unanswered
  while every other row was answered.)*
- **A means the engineer must name is asked as a name.** Where `Set by` is
  unknown (a mechanical block, a pin-voltage step), the row's AI proposal says
  what is needed and the row asks "which device / procedure?"; an answer of
  "yes" names nothing — the row stays `answered` but unconfirmed, the case
  says the step in plain words without a device name, and the name is
  re-emitted as a question (workflow-discipline §5).
- **Cached for the project.** Means belong to the bench, not to a feature:
  confirmed rows are written to `qualification_test.bench_catalogue` in
  `ai_test_project.yaml`, and the next feature shows them as already confirmed
  and asks only about new items. A cached row whose item is not in this run's
  inputs any more is reported, not deleted.

An item whose means stays unconfirmed gets no invented name: the case that
needs it is still written, says the step in plain words without a means name,
and is blocked — `bench capability not confirmed` — naming the `CID` in
`Notes` (§13).

### 3.3 Observation and injection means by bench capability (`debug_means`)

Many requirements specify an internal value — a filtered sensor value, a
controller's set-point or limit, a peripheral's read cycle — that no bus
signal shows and the delivered A2L does not describe. Whether the bench can
reach such a value is a fact about the bench, not about the requirement, so
it is configured once per project — `qualification_test.debug_means` in
`ai_test_project.yaml` — and never decided per requirement by the skill.

| `debug_means` | What cases may observe and inject, beyond bus signals, diagnostic requests and `docs.a2l_or_varlist` items |
|---|---|
| `none` (default) | nothing more. A case whose observable or injection exists only in `docs.variable_list`, or only under a debugger, is written blocked — `bench capability not confirmed` — proposing the symbol |
| `xcp_varlist` | any symbol in `docs.variable_list` is a valid XCP observable or injection variable |
| `xcp_and_debugger` | as `xcp_varlist`, plus the catalogue kinds `breakpoint at symbol` and `debugger variable`, on Debug-SW cases only |

`docs.variable_list` is an optional, project-wide input beside
`docs.a2l_or_varlist`: a symbol list of the software under test — a linker map
file, an ELF symbol export, or a Debug-SW A2L. Like the A2L it says what can be
reached, not what a value should be (§0): the run reads symbol names and,
where the file carries them, sizes and data types — nothing else.

- **Symbols come from the two lists only.** Every variable, breakpoint symbol
  and debugger variable a case names exists verbatim in `docs.variable_list`
  or `docs.a2l_or_varlist`, and `Traceability` says which. The source code is
  never searched for an observable; an injection variable's name may come from
  the name-only search of §0, and must still be in one of the two lists. A
  symbol is matched to the requirement's quantity by name, offered as a
  proposal in the catalogue (§3.2), and used only once confirmed.
- **`xcp_varlist`** — a symbol from `docs.variable_list` is measured or
  written over XCP like an A2L item. Its scaling and data type are asked at
  Phase 1, one question per symbol with a concrete proposal (§3, A2L items
  without a scaling); unanswered → the case uses the proposal and is blocked
  — `needs clarification`.
- **`xcp_and_debugger`** — two further catalogue kinds:
  - **`breakpoint at symbol`** — a breakpoint on a function or code symbol
    from the lists. A breakpoint case checks the symbol's **period or hit
    count**, as a timing case (§11): `Verify the breakpoint at <Sym> is hit
    every <T> ms (<requirement>), tolerance ± <tol> (<source>)`, or its hit
    count over `k` periods, `k` confirmed at Phase 1 (proposal 10). The
    tolerance comes from an input; without one, the case checks the nominal
    value and the missing tolerance is an Open Point (§11). The catalogue row
    asks whether the debugger counts hits without halting the CPU — a halting
    breakpoint disturbs the timing it measures; unconfirmed → the case is
    blocked — `bench capability not confirmed`.
  - **`debugger variable`** — a variable read or written in the debugger's
    watch window, for a value no XCP item reaches.

  Both are allowed **only on Debug-SW cases** (§8, `atcRemark`). For a
  feature the Test Plan puts on Series SW, each debugger case is a Phase-1
  question — "Proposal: `<title>` runs on Debug SW, `atcRemark` = `Debug SW`.
  Accept?" — and an unconfirmed one is written blocked — `needs
  clarification`.
- **Bus first still holds** (§7): a variable-list or debugger observation is
  used only where no sent bus signal and no A2L item shows the behaviour.
- **Beyond the configured means → blocked, never dropped.** A case whose
  observable or stimulus needs more than `debug_means` grants is written in
  full with the proposed symbol and the means it needs, blocked — `bench
  capability not confirmed` — and the requirement is reported on
  `Requirements Hygiene` as `observable not on bench` (§12), owner: the bench
  owner. Raising `debug_means` is the project's decision; the skill never
  assumes a means the config does not grant. *(Observed: Actuator Data
  requirements and dozens of controller-internal Motor Control requirements
  had no case, because their values were reachable only by XCP on symbols
  absent from the delivered A2L, or by a debugger.)*

### 3.4 Requirements that delegate to a specification

A requirement whose text hands its content to a document — "implemented
according to `<doc>`", "configured according to `<doc>`", "as per `<spec>`" —
is **expanded, not reviewed**. It is not a configuration review and not
something "covered by the OEM package" (§3.1): its behaviour is the document's
observable rules, and those are tested.

- **Document registered** in `docs.reference_specs` → derive cases from the
  document's observable rules in its relevant sections, and trace each to the
  delegating requirement (`Requirement ID`), with the section cited in
  `Traceability` (§3.1):
  - an E2E protection profile — the counter sequence, the CRC, the reception
    timeout, the reaction to invalid data;
  - a network-management specification — the states and transitions, the
    timings, the bit fields of the NM message;
  - a development-message or other database — each message present on the bus
    with its cycle time (§11);
  - any other document the same way: every rule it states that is observable
    at the software's boundary.

  The cases are proposed at Phase 1 like any other, each marked with the
  document section it expands.
- **Document not registered** → ask for it at the Phase-1 gate (§3.1), and
  write **one blocked case per requirement** — `missing test equipment`,
  naming the document in `Notes` (§13). The case is complete for what the
  requirement text and the supplied inputs state — for a message the
  requirement names, its presence and its cycle time from `docs.comm_database`
  — and never carries a placeholder pass criterion. The expanded cases follow
  on the run after the document is supplied.
- A document recorded `N/A` (§3.1) is handled the same way as one not
  registered: the one blocked case is written, the document named — as
  `missing test equipment`, because the document is what the case is missing,
  not one value of it.

*(Observed: four bus-feature requirements delegating to an E2E profile, a
network-management specification and a development-message database were
classed as configuration review or "covered by the OEM package", and got no
case.)*

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
- **A logical parent is for variants, not for values.** Use parent and
  children where the variants need different setups or trace to different
  requirements (one case per message, per DID, per operating mode). Values of
  one parameter under the same setup — boundary points, equivalence-class
  representatives — are the **steps of one case** (§6), never children.
- Every Object Heading / Object Text must be unique within the module.

## 5. Title convention

`TC_<what is being verified>`, followed where parameterised by the value in
square brackets, e.g. `TC_PosActuator_A1_ON_angle_with_in_range
[EP_phiActuator = 16.3°]`. The title states intent, not mechanism. No leading
number. A stepped case (§6) carries no value in its title — its steps hold the
values.

## 6. Boundary value rule

For a parameter given as `Name / Value / Min-Max / Resolution`:

| Point | Value | Expected |
|---|---|---|
| At the boundary | `boundary` | the specified value |
| One resolution step inside | `boundary ∓ Resolution` | the specified value |
| One resolution step outside | `boundary ± Resolution` | the reaction the requirement specifies outside the range (clamped value, substitute value, error flag) |

**The points are the steps of one case, not separate cases.** For one parameter
of one requirement, write **one** case: each action sets one point, and the
result with the same number gives what is expected at that point. Order the
steps so the case also shows the software **recovers** from an invalid value:
start inside the range, alternate between valid and invalid points, and end on
a valid nominal value. For example, for a range `Min`–`Max` clamped outside:

```
Actions                     Results
1. Set <Qty> = Min.         1. Verify signal <Sig> in message <Msg> = Min.
2. Set <Qty> = Max − Res.   2. Verify ... = Max − Res.
3. Set <Qty> = Max.         3. Verify ... = Max.
4. Set <Qty> = Min − Res.   4. Verify ... = Min (clamped).
5. Set <Qty> = Max + Res.   5. Verify ... = Max (clamped).
6. Set <Qty> = <nominal>.   6. Verify ... = <nominal>.
```

The case is `positive` (§8) — it checks specified behaviour, the out-of-range
reaction included — and `atsTestDesignTechnique` carries both the
requirements-based and the boundary-value technique.

Apply only where a parameter with a stated resolution exists in
`docs.signals_params` — or, for a bus signal, in `docs.comm_database`, where the
signal's factor is its resolution and its physical min/max are its range.
Where a requirement states a limit but no backing parameter/resolution exists,
put the boundary steps on Open Points rather than inventing a step size — the
requirement's own case is still written (§1), without them.

**Only on a quantity the bench can set.** A boundary value is a stimulus, so
the quantity must have a confirmed **Set by** means in the catalogue (§3.2): a
signal the ECU *receives* (set by rest-bus simulation or a panel), an
XCP-writable variable, a supply voltage. A database factor and range make a
signal *reportable*, not settable — a signal the ECU *sends* cannot be set to
its boundary. For such a dependent quantity (a measured current, a computed
angle, a reported status), drive the **source** to an operating point that
puts it at the boundary, and capture the source and the reported signal
together; the result compares the two within the stated resolution. An
injection variable (§0) that stands in for the source is a settable source. If
no settable source drives it, the boundary steps are an Open Point; the
requirement's case is still written (§1).

## 7. Writing the steps

A case is a sequence of **stimulus → check** pairs that an operator runs top
to bottom.

- `atcPreconditions` — numbered steps that bring the ECU into the case's
  **baseline and verify it**: every value set is followed by a step checking
  it on the observation point.
  ```
  1. ECU is awake (normal operation).
  2. Set the supply voltage = <nominal> V.
  3. Verify signal <Sig> in message <Msg> = <nominal>.
  ```
  The bench setup common to every case (software flashed, tools connected,
  rest-bus simulation running with its default values) is not repeated in each
  case — `atsTestEnvironment` and `atcRemark` carry it. A precondition must not
  contradict the case's own actions (a precondition "signal `<Sig>` absent"
  for a case whose first action sets `<Sig>`).
- `atcActions` — numbered **stimuli**, one per number; actions sharing a number
  run in parallel. Observing is not an action: no "Record `<X>`" or "Read
  `<X>`" step — what is read, and where, is the result's job.
- `atcResult` — **one result per action, same number**, each a check:
  `Verify <kind> <item> = <value>`. **Every result is a pass/fail check**; the
  case passes only when every result holds. No placeholder result (`-`) and no
  separate pass/fail marker. An action with nothing to check is either a
  precondition or part of the next action.
- **One observable per result line.** Where one action has several things to
  check, the result is a numbered list of sub-items — `2a`, `2b`, `2c` — each
  checking **one** item with its value, in the order they occur. Never a
  single sentence that checks a state, a signal and four variables at once,
  and never a range expression (`channels 0 .. 3 = 0`): each channel is its
  own line with its own value. A reviewer who cannot find the value in the
  result marks the case invalid even when the check is there. *(Observed: a
  direction-change case checked the idle state, the state signal and all four
  PWM channels at zero in one 90-word result; QA rejected it as "channel
  values not mentioned".)*
- **A state is asserted by its defining outputs, listed.** When a result
  checks that the system is in a named state (idle, stop, mute), the outputs
  that define that state in the feature's requirements follow as their own
  sub-items — the same checks the sibling case for the defining requirement
  uses — and that requirement joins `Requirement ID` (merged requirements,
  below).
- `atcPostconditions` — numbered steps that **restore the baseline** from the
  preconditions **and verify it**, the same way.
- Two test cases distinguishable only by title are redundant — merge them; the
  distinction must be visible in `atcPreconditions`/`atcActions`.
- Expected results must be unambiguous: name the exact variable and value
  (`"CDD_Sent_XCP_Angle_g_u16 is updated to 163"`), never a vague description.
  An enumerated value is written as the database text with the raw value in
  brackets: `<Text>(<raw>)`, e.g. `Active(1)`.
- **Every value is a number the operator can type.** A step never holds a
  symbol for a value to be noted on the bench and reused later ("note the
  raw value R, then write R × 5 / 16"). Where the scaling that would give the
  number is unknown, it is a Phase-1 question (§3); unanswered, the case
  uses the proposed scaling's number and is blocked, with the assumption in
  `Notes` (§13) — never a placeholder.
- **The requirement's unit comes first.** An expected value is stated in the
  unit the requirement uses — percent, volts, degrees, milliseconds — and only
  then, where the bench reads something else, in the raw or converted form
  with its derivation: `CH0 = DutyCyc % (raw counts = DutyCyc % × 4800 / 100,
  since 100 % = 4800 counts; e.g. 50 % = 2400)`. A result that leads with the
  converted form reads as a different quantity to the reviewer.
- **A derived expected value is written as its formula, with units and a
  worked example.** When the expected value follows from another observed
  value through a scaling, write the whole relation in decimal with its
  units, plus one example: `<Var A> = <Var B> (%) × 4800 / 100 ticks,
  e.g. 50 % = 2400` — never a bare factor such as `× 48`, which a reader
  can take for hexadecimal or a typo. *(Observed: QA returned "× 48" as
  "is it hex?")*
- **A comparison across resolutions has a tolerance.** When the two sides
  of a check resolve differently (a percentage in whole steps against a
  counter in ticks, a 1 mV value against a 0.1 % one), state a tolerance of
  at least one step of the coarser side — derived from the scalings, cited
  in `Traceability`. An exact match would fail on rounding alone.
- **No remarks inside a step.** Open Point numbers, "to be confirmed", source
  notes and explanations belong in `Open Points` and `Traceability` — and,
  for a blocked case, what holds it back in `Notes` (§13) — never in a
  precondition, action, result or postcondition.

**Every action names its means — in plain words.** The step is the manual
instruction itself: the tool, panel or generator block and the control from
the confirmed catalogue (§3.2), the item with its kind, and the value — so the
case can be run by hand as well as automated, with no separate `Manual:` line
and no bracket tag:

```
1. Set the supply voltage = <value> V.
2. Set the DLC of message <Msg> = <n> in <generator block>.
3. Stop sending message <Msg> from <panel>; send it periodically from <generator block>.
4. Set signal <Sig> in message <Msg> = <value> in <panel>.
5. Write XCP variable <Var> = <value>.
6. Send diagnostic request 22 <byte1> <byte2>.
```

- **Never invent a panel, block or control name.** A means the catalogue has
  not confirmed is described in plain words without a name, and the case is
  blocked — `bench capability not confirmed` (§3.2, §13).
- **Never write a state as an action.** "ECU is in normal mode" or "the fault is
  active" is not something an operator does. Either it is a precondition, or
  the action says how it is brought about (`Write XCP variable <Var> =
  <value>`).
- A bare identifier is never enough: say whether it is a message, signal or
  variable.

**Every result names what is observed.** Each `atcResult` entry is a check of
one observable item, with its kind and the expected value:

```
1. Verify signal <Sig> in message <Msg> = <value>.
2. Verify message <Msg> is sent every <cycle> ms.
3. Verify XCP variable <Var> = <value>.
4. Verify the breakpoint at function <Sym> is hit every <T> ms ± <tol> ms.
```

Item 4 only under `qualification_test.debug_means: xcp_and_debugger`, on a
Debug-SW case (§3.3).

- **Observe on the bus first.** Where a signal the ECU sends shows the
  behaviour — the value itself, a timeout or error flag, a status — check that
  signal. Use an XCP variable only where no sent signal shows it. A bus signal
  is there on Series SW, and one signal can serve every step of a sweep.
- **An internal state is not an observation.** "The ECU uses the substitute
  value" or "the mode is active" cannot be checked; name the signal or the
  variable that shows it — a sent bus signal first, then an A2L item, then,
  as `qualification_test.debug_means` allows, a symbol from
  `docs.variable_list` or a debugger observation (§3.3). Where the bench's
  confirmed means reach none of them, the requirement does **not** become an
  Open Point instead of a case: the case is **written**, its result names the
  symbol proposed from `docs.variable_list` / `docs.a2l_or_varlist` that holds
  the value, and it is blocked — `bench capability not confirmed` — proposing
  that symbol and the means it needs (§13); the requirement goes to
  `Requirements Hygiene` as `observable not on bench` (§12). Where neither list
  carries a symbol for it, the result names the requirement's quantity in the
  requirement's own words and the case is blocked — `missing test equipment`
  — asking for a variable list that carries it.
- **No result on what the case removed.** A result may not expect a value from
  a signal or message the case's own actions stopped or removed from the bus.
- **Windows come from the inputs.** An observation window ("absent for
  ≥ N ms", "within N cycles") uses a cycle time, timeout or timing from a
  supplied input — the communication database, the requirement, a cited
  specification — and cites it. Never pick a window because it looks
  reasonable. Where no input gives the time, the result checks the end state
  ("changes to `<value>`") without a window, and the missing time is an Open
  Point.
- **A borrowed bound names its source in the result itself.** When the time
  or limit in a result comes from a requirement or parameter **other than the
  one the case traces to**, the result says so inline — `within 400 ms
  (tRecoverPosition, SW_Param-60, via SW_Requ-93)` — not only in
  `Traceability`, and states whether it is an upper bound, a lower bound or an
  exact value. A bare "less than 400 ms" borrowed from a neighbouring
  requirement reads as the case's own claim, and the reviewer asks where it
  came from. Where the borrowed bound is only implied by the neighbouring
  requirement, it is a Phase-1 question with the bound as the proposal.
- **The observation must be faster than the timing it checks.** Compare
  every timing a requirement states (one task cycle, a slope per ms, a
  window) with the fastest observation the bench offers for that item — the
  message cycle in the communication database, the fastest XCP DAQ event in
  the test environment. Where the requirement's timing is finer, the timing
  clause is an Open Point; the case checks only what the sampling can
  resolve (an order of states, an end value), and the Open Point says when
  a short state can be missed between samples and fail the case falsely.
  Take the task period from the architecture text where it states one
  (§3, supporting specifications).

**Merged requirements — one case.** Requirements may share one case in three
situations:

- **Same stimulus, different observations** — they are outcomes of the same
  preconditions and actions.
- **One stimulus varied, same observation** — each requirement covers part of
  the range of one input (e.g. a valid, a longer-than-specified and a
  shorter-than-specified length of one message), and one signal shows the
  outcome for all of them. The case is a stepped case (§6) with a step for
  each requirement's values.
- **A state the case passes through** — the case drives the ECU through a
  state (an idle phase in a direction change, a braking phase, a fault
  state) whose outputs another in-scope requirement specifies. Checking that
  the state *occurs* is not enough: the result also checks the outputs that
  requirement gives for it, at that point, and the case traces that
  requirement too. Mark the state with the signal the ECU sends for it where
  one exists (bus first), the XCP state variable otherwise. When proposing
  cases at Phase 1, list for each case the states it passes through and
  match them against the in-scope requirements; each match is a proposed
  merge. *(Observed: a case checking "idle occurs between forward and
  reverse" was marked invalid by QA because it did not check the output
  channel pattern the idle-state requirement specifies.)*

A merge is **proposed** in the Phase-1 proposed-cases table, listing the
requirements it covers, and made only once confirmed. The verdict is kept on
the test case: it passes only when every result holds. `Requirement ID` lists
**every** requirement a step verifies — including one the case covers only
because its stimulus range reaches it — and `Traceability` lists each, with
its clause and the result steps that check it.

## 8. Attributes specific to this skill

| Attribute | How to fill |
|---|---|
| `atcRemark` | `Series SW` or `Debug SW`, per the feature's entry in the Test Plan (`docs.test_plan`). Without a Test Plan — or with a feature it does not list — ask once, as a Phase-1 question, and record the answer in the manifest (`feature.test_software`) so later runs reuse it. Never guess it: a case meant for Series SW that relies on a Debug SW variable cannot run. Every item a case sets or reads must exist on that software (the catalogue's Series SW / Debug SW columns, §3.2); one that does not is an Open Point, and the case is blocked — `needs clarification` (§13). A case using a debugger kind (`breakpoint at symbol`, `debugger variable`, §3.3) is always `Debug SW`; on a Series-SW feature that needs the Phase-1 confirmation of §3.3 |
| `aFeature` | The target feature |
| `atsClassification` | Per `attributes.classification_rule`, derived from the linked requirement's safety/security/regulatory/OBD attributes where the governing matrix defines that mapping — state your reasoning in Open Points whenever the case falls to error-severity judgement (A/B/C) rather than a rule-driven class |
| `atsTestKind` | `Functional test` by default; the robustness/EMC wording for robustness cases; `Performance test` for timing/resource cases |
| `atsTestDesignTechnique` | `RequirementsBased` always; add `BoundaryValueAnalysis` for boundary cases, `EquivalenceClasses` for class representatives, `ErrorGuessing` for cases with no requirement link. Multi-valued. |
| `atsType` | `positive` for a case that checks specified behaviour — including a stepped case (§6) whose steps go outside the range to check the specified reaction there; `negative` for a case whose stimulus as a whole is invalid (a lost message, an injected fault) or for error guessing; `qualitative` for non-functional cases |

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

## 10. Scenario families — the sequences requirements-based cases miss

A requirement-by-requirement case checks one behaviour in a settled state.
Customer HiL testing exercises **sequences**: what the software does on the
way into a state, on the way out, under a fault that arrives mid-operation, and
when a request is repeated or reversed. *(Observed: of nineteen customer HiL
findings on one release, twelve were start-up, mute-exit, fault-during-motion
or repeated-request sequences that no internal case had driven; every one of
them was visible on the bus.)* So every run checks the feature against the
scenario families below, in Phase 1, before cases are proposed.

| Family | What the cases drive | Typical observations |
|---|---|---|
| **F1 Start-up and wake-up** | each wake-up source (ignition, bus, request); an expected input absent from the start | the first frames the ECU sends — message counter sequence, network-management state, initial signal values; time from wake-up to the first valid output; the timeout flag for the absent input |
| **F2 Shutdown and timeouts** | loss of each received message and of the ignition signal, one at a time and all at once | detection within the specified window (not before, not after); what the ECU stops sending and in what order; the state of the network-management frames |
| **F3 Suppression entry and exit** (mute, transmission off, bus-off) | entering by each path the requirements name; leaving by each path (command, network stop, ignition) | outputs during suppression; on exit, re-initialisation of counters, debounce timers and error flags; the first frame after exit |
| **F4 Fault injection during an operation** | a counter, checksum, timeout or qualifier fault on a command while the actuator moves or a request is pending | the command on the faulty frame is not executed; error flags set coherently (never two in one frame unless specified); the movement's outcome |
| **F5 Fault recovery** | the first valid frames after each fault of F4, after a short and after a long gap | the number of frames until the flag clears; no secondary error raised by the recovery itself; the flag transition order |
| **F6 Repeated, reversed and overlapping requests** | short request pulses; a new request during settling; the opposite request mid-movement; a request during an autonomous action | the reported position/state at each step; which request wins; no stuck state |
| **F7 Autonomous and safety reactions from each starting state** | the triggering condition from every initial state the requirements distinguish (engaged, disengaged, intermediate, just restarted) | the reaction happens from each state, or the requirement says why not; abort when the trigger disappears |
| **F8 Operating-voltage edges** | the supply crossing each threshold the requirements name, both directions, slowly and as a step | flags and derating reported for the specified debounce, not for one cycle; recovery above the threshold |

Rules:

- **At Phase 1, list the families against the feature.** For each family say
  whether it applies — from the in-scope requirements, the governing
  specification (§3.1) and the supporting specifications (§3) — and, where it
  applies, which requirements it exercises and the cases proposed for it. A
  family that does not apply gets one line in Open Points with the reason;
  none is skipped silently. The project may narrow or extend the list
  (`qualification_test.scenario_families`).
- **Every scenario case still traces to requirements.** The family is a
  design lens, not a test basis: each step's check comes from a requirement or
  the governing specification, and `Requirement ID` lists every requirement a
  step verifies (§7, merged requirements). A sequence no requirement and no
  specification describes is a Phase-1 question or an Open Point — never a
  procedure written from how such systems usually behave (no-fabrication.md).
- **The states passed through are checked.** A scenario case drives the ECU
  through several states; at each one, the outputs the in-scope requirements
  specify for that state are checked (§7, "a state the case passes through").
- **Observe on the bus.** Every family above is visible in the frames the ECU
  sends — counters, states, flags, positions, timestamps — which is why
  customer testing finds them. Use an XCP variable only where no sent signal
  shows the behaviour (§7).
- **Repeat where the finding is sporadic.** A start-up or exit sequence
  (F1, F3) is run the number of times the engineer confirms at Phase 1 — the
  proposal is 10 — and the case fails if any repetition fails; the count is in
  the case text, not in a remark.
- **Mark the family** in the proposed-cases table and in `Traceability`.
  `atsTestDesignTechnique` keeps the project's allowed values
  (`RequirementsBased`, plus the boundary or equivalence technique where it
  applies); `atsType` is `negative` for F4 and F5 and for an F2 loss case,
  `positive` otherwise (§8).

## 11. Timing and cycle-time cases from the communication database

Timing findings are the easiest to miss by inspection and the easiest to
measure on a bench. For every message in the feature's scope, generate the
cases the database attributes support — and, for every requirement that states
a period inside the software, the period-at-a-symbol case (last row) — with
`atsTestKind = Performance test`:

| Case | For | Measures | Pass criterion source |
|---|---|---|---|
| **Cycle time** | each message the ECU transmits | the spacing of `k` consecutive frames in steady state | the message's cycle time in `docs.comm_database`; tolerance from the OEM communication specification (§3.1) or the requirement — never assumed |
| **Fast cycle on change** | each transmitted message with a fast-cycle attribute (e.g. `GenMsgCycleTimeFast`, `GenMsgNrOfRepetition`, `GenMsgDelayTime`) | after one signal change: the number of repeated frames, their spacing, the delay before the first | the database attributes, quoted by name and value |
| **Payload coherency on change** | each transmitted message carrying several signals the ECU updates on one event | the first frame after the event carries every changed signal at its new value | the requirement that defines the event's outputs; a frame with a partial update fails |
| **Timeout detection** | each received message with a timeout the requirements or the database define | with the message stopped: the flag is set no earlier than `T − tol` and no later than `T + tol`; with the message interrupted for `T − tol` it is not set | the timeout value and its tolerance, each with its source; where two documents give two tolerances, the stricter one is used and the difference goes to `Requirements Hygiene` (§12) |
| **Time to first frame** | wake-up and start-up (F1) | the time from the wake-up stimulus to the first frame of each transmitted message, and to the first valid value where a requirement states it | the requirement or system requirement that states the limit |
| **Period at a symbol** | each requirement stating a read cycle, a task period or a peripheral sampling rate, where `debug_means` is `xcp_and_debugger` (§3.3) | the period of hits of a breakpoint at the symbol, or its hit count over `k` periods | the requirement; tolerance from an input, or the nominal value checked and the tolerance an Open Point. With a lower `debug_means`, the case is written blocked — `bench capability not confirmed` |

Rules:

- **Numbers come from the database and the specification, named.** Each case
  quotes the attribute (`cycle time 200 ms`, `fast cycle 20 ms, 5
  repetitions, delay 10 ms`) and the tolerance with its document, version and
  section in `Traceability`. Without a tolerance from an input, the case
  checks the nominal value and the missing tolerance is an Open Point; no
  tolerance is assumed.
- **Both sides of a timeout.** A detection case alone passes an
  implementation that detects too early; the "not before `T − tol`" step is
  mandatory where the tolerance is known.
- **The observation is faster than the timing** (§7): the trace timestamp
  resolution and the message cycle are compared with the timing measured, and
  a timing the bench cannot resolve is an Open Point.
- **Mark the attribute** measured in the proposed-cases table and in
  `Traceability` so the engineer can see which attributes have no case.

## 12. Requirements hygiene — findings about the inputs, reported to their owner

Many customer findings are not test gaps: the requirement was missing,
unreleased, contradicted by another document or changed after the release.
A run sees these while reading its inputs, and reports them at Phase 1 on the
`Requirements Hygiene` sheet of the Phase-1 workbook (workflow-discipline §5),
one row per finding: `RID | Finding | Documents | Values seen | Proposal |
Owner | Status`. The sheet is mirrored into the final workbook's Open Points
under `Input hygiene`. Check, every run:

- **Status lags the software.** A requirement outside
  `attributes.status_filter` (`to review`, `ready for implementation`) whose
  behaviour the ECU demonstrably shows — it is cited by an in-scope
  requirement, by a ticket in `docs.extra`, or its signal is in the database
  the ECU transmits — is reported with its status. The run does not author
  from it (the filter stands), but the owner must know the test spec cannot
  cover a behaviour the software already has.
- **Parameter and threshold conflicts.** A value that differs between the
  requirement text, Signals & Parameters, the communication database and the
  governing specification (a delay of 500 ms in one and 1000 ms in another, an
  error threshold of 4 against an expectation of 5) is reported with every
  value and its source. The case follows one of them — the governing
  specification first, then the requirement, then the parameter list — and
  says which in `Traceability`.
- **Tolerance conflicts.** A tolerance that differs between the requirement
  and the specification it implements (±10 % against ±5 %) is reported; the
  stricter one is used (§11).
- **Cited but absent.** A requirement, parameter or document another input
  cites that is not in the export, not registered or not supplied.
- **Changed after the release under test.** A requirement whose
  `aChangeRequID` or status changed after `release.id`, where the export shows
  it; the test case is authored to the version in the export and the change is
  reported.
- **No verification criterion** (§1.1) — reported here as before, one row per
  requirement.
- **Criterion contradicted by the bench or by an answer** (§1.1) — a
  criterion step whose stimulus or value an engineer or QA answer says cannot
  occur; the case follows the answer and the owner rewrites the criterion.
- **Criterion rests on a parameter the bench cannot reach** (§3, parameter
  provenance) — a criterion that says "start timer X" or "set limit Y" where
  X or Y is in no A2L, DiagSpec or writable item; owner decision between an
  A2L entry and moving the requirement to another test level.
- **Criterion carries an unconfirmed error-guessing expectation** (§1.1) —
  reported with the engineer's confirmation or correction once given.
- **Possibly integration level** (§1, §1.1) — a requirement with `aTestability`
  = `test` whose criterion names a review, an analysis, an inspection or
  another test level, or whose text reads as a read-cycle, peripheral or
  configuration setting rather than behaviour at the software's boundary.
  Owner: the requirements engineer. **The finding never replaces the case:**
  every requirement reported here has a written case in the same run
  (self-check 45).
- **Observable not on bench** (§3.3, §7) — the requirement's observable or
  stimulus is reachable only through a means the project's
  `qualification_test.debug_means` does not grant, or through a symbol neither
  `docs.a2l_or_varlist` nor `docs.variable_list` carries. The row names the
  proposed symbol and the means needed. Owner: the bench owner (means) or the
  software integrator (the symbol in the A2L / variable list). The case is
  written, blocked (§13).

Each row names an **owner** — requirements engineer, system engineer,
architect, database owner — so the sheet can be split and passed on without
the test engineer rewriting it. A finding becomes a Phase-1 **question** only
where it changes a case's value, and then it carries a concrete proposal that
"Yes" accepts (workflow-discipline §5); otherwise it is a finding, and the case
is written as the rules above say.

## 13. Blocked cases and the `Notes` column

A case is **blocked** when it is complete — preconditions, actions, results
and postconditions an operator could run top to bottom — but cannot be
executed yet, because something outside the workbook is missing or
unconfirmed. Blocked cases are **written, never dropped**: every case that
traces a requirement is on the `Test Cases` sheet, and what holds it back is
said in its `Notes` cell (output-format.md, reference columns). The QA
columns stay empty (no-fabrication.md): "blocked" is the generator's
statement of what is missing, not a verdict on the case — that is QA's to
give.

**When a case is blocked, and its category.**

| Category | When | Typical triggers |
|---|---|---|
| `needs clarification` | an input is ambiguous or missing a value | an A2L item or a variable-list symbol without a scaling, unanswered (§3, §3.3); a parameter with no provenance (§3, parameter provenance); an unconfirmed error-guessing expectation (§1.1); a value only a document marked `N/A` would give (§3.1); an item that exists only on the other software (§8); a debugger case on a Series-SW feature, unconfirmed (§3.3) |
| `missing test equipment` | a file, tool or sample is not delivered | the A2L, the communication database, the CANoe configuration, a flash file, a sample part or harness the case needs; the document a requirement delegates to (§3.4); a variable list carrying the symbol for a requirement's internal value (§7) |
| `bench capability not confirmed` | a means from the bench catalogue is unconfirmed | a `Catalogue` row (§3.2) still open, or answered without naming the panel, control or device; an observable, injection variable or breakpoint that needs more than `qualification_test.debug_means` grants (§3.3); a hit count the debugger may only take by halting (§3.3) |
| `missing test method` | no one has said how to do a physical step | disconnecting a connector, shorting a line, blocking the actuator — no input or answer says how |
| `two inputs contradict each other` | two inputs disagree and no answer has picked one | a criterion step the run's own Open Point doubts (§1.1); a value that differs between documents with no ruling (§12) |

One category per note. Where several apply, use the one whose item the
expected result rests on, and name the other items in the same note.

**A blocked case is still complete.** Every step follows §7 — no placeholder,
no "to be confirmed", no Open Point number inside a step. A value that is not
confirmed is written as the number the case **assumes**, and the assumption
is stated in `Notes`. The assumed value is the concrete AI proposal of the
open Phase-1 question for that item (workflow-discipline §5), or the value a
supporting specification states (§3) — never a number with no source. An
item with neither is a Phase-1 question that was missed: ask it now
(workflow-discipline §5, check the answers), never invent the value. A means
the catalogue has not named is described in plain words without a name
("switch off the motor supply"), never with an invented one (§3.2).

**There is no unwritten "not covered" path.** A requirement whose observable
or stimulus the bench cannot reach is written blocked (§3.3, §7); one whose
criterion names another level or method is written and reported (§1.1, §12);
one that delegates to a missing document is written blocked (§3.4). Only the
engineer's decision at the coverage gate (workflow-discipline §5) leaves an
in-scope requirement without a case, and that decision is an Open Point `Not
covered` quoting it, with who decided and when.

**The note — one paragraph, fixed structure:**

```
BLOCKED - <category>. <What the test has to do, in one sentence.> <What is
missing or unconfirmed, in plain words, with the catalogue / OP / Q id in
brackets.> Action: <who has to deliver or confirm what>. QA: <what the
reviewer should do now, e.g. review the logic; execution waits for ...>.
```

- It starts with `BLOCKED - ` exactly, then one of the five categories
  verbatim, then a full stop.
- **Written for a reader without automotive background.** Use the plain word
  where one works; keep the exact signal, variable, panel and document names,
  because the tester needs them.

  | Instead of | Write |
  |---|---|
  | UDS service, `22` / `2E` / `31` request | diagnostic command (read data / write data / start routine) |
  | NV block, NvM | memory block |
  | HIL, HiL bench | test bench |
  | DTC | stored fault code |
  | ECU | control unit |
  | DID / RID | diagnostic data item / diagnostic routine |
  | XCP variable | variable `<Var>` (read with the measurement tool) |

- An **assumed value** goes in the "missing" sentence: "The case assumes
  <value>, the value proposed in the question list (Q-nn)".
- **Refer, do not repeat.** The analysis behind the gap — the documents
  compared, the values seen, the reasoning — is in `Traceability` and
  `Open Points`; the note names the OP id instead of restating it.
- `Action:` names a role (requirements engineer, bench owner, database owner,
  test engineer, project lead), not a person, unless an input names one.
- `QA:` says what the reviewer can do now and what execution waits for.
- **Empty** on every case that can run, and on every heading row.

Examples:

```
BLOCKED - bench capability not confirmed. The test switches off the motor
supply while the actuator is moving and checks that the control unit reports
the fault in signal MotCtrl_ErrSt. Nobody has confirmed that the test bench
can switch the motor supply off on command (catalogue CID-14, OP-07).
Action: the bench owner names the panel control or device that switches the
motor supply. QA: review the steps and expected results now; execution waits
for the bench confirmation.

BLOCKED - needs clarification. The test checks that the actuator is back at
its rest position within the recovery time after a voltage drop. No document
gives the recovery time; the case assumes 400 ms, the value proposed in the
question list (Q-12, OP-04). Action: the requirements engineer confirms or
corrects the recovery time. QA: review the logic now; execution waits for the
confirmed value, and the time in result 3 changes if it differs.

BLOCKED - missing test equipment. The test sends the diagnostic command that
reads the actuator position and checks the reply against signal
PosActuator_Act. The variable list file (A2L) for the delivered software has
not been supplied, so the variable used in precondition 2 cannot be looked up
(OP-09). Action: the software integrator delivers the A2L for the release
under test. QA: review the logic now; execution waits for the file.
```
