# Integration-test (SWE.5) mechanics

> Loaded by `integration-test/SKILL.md` on top of
> [workflow-discipline.md](workflow-discipline.md),
> [no-fabrication.md](no-fabrication.md), and
> [output-format.md](output-format.md).

## 0. AUTOSAR-only guard (v1)

The only validated pattern here is **RTE-debugger-based**: the Debug SW is
flashed to the target ECU, breakpoints are set on RTE calls, variables are
edited, and the value is observed at the receiving end. This only makes sense
where the module has `Rte_Write`/`Rte_Read`/`Rte_Call` symbols to hang a
breakpoint on. The cases are **designed from the architecture alone** — the
DOORS export, the ARXML and the RTE headers generated from it — and name each
breakpoint by RTE symbol and module; the debugger is the means of execution,
not a licence to read the implementation (§9).

If the target module shows **no** RTE symbols to work from — no port on its
ARXML software component, no `Rte_Write`/`Rte_Read`/`Rte_Call` symbol for it
in the RTE headers (§9), no `Rte_Write`/`Rte_Read` calls in the Signals &
Parameters export, and (in `extend_existing` mode only, §0.1) no existing
RTE-pattern test case — **stop** and say plainly that this skill only supports
RTE-based integration testing in its current version, rather than inventing a
black-box equivalent. Where this repository's `20_AI/ai_project.yaml` says
`project.type: nonautosar`, that settles it: stop.

## 0.1 Authoring mode — decided once, before any discovery

`integration_test.authoring_mode` in `ai_test_project.yaml` says whether this
project **extends** an existing SWE.5 test-spec module or **authors one from
scratch**. It is an engineer decision recorded once (project-config.md §4.1),
never inferred from which files happen to sit in the project folder. If an
existing config does not carry it yet, ask it at the Step-3 gate — before any
document discovery — quoting `docs.integration_test_spec_export` as evidence.

- **`extend_existing`** — `docs.integration_test_spec_export` points at the
  project's SWE.5 export. It is the coverage baseline (§5.1), the source of
  heading spellings (§3, §4), and a secondary source of symbols and enum
  literals behind the ARXML and the RTE headers.
- **`from_scratch`** — `docs.integration_test_spec_export` is `N/A`. This is a
  first-class mode, not a degraded one:
  - the coverage baseline is empty — every interface is "no test cases", every
    row is new, every `ID` empty;
  - module and connection heading spellings are **proposed and confirmed** at
    the Phase-1 gate, never invented silently; the proposal is the
    architecture `1.4.1.<n>` spelling (§4);
  - group headings that follow a pattern form (`Watch Dog for <Module>`, the
    task-configuration heading) are marked as derived in Traceability;
  - symbols, checkpoint names, runnable names and enum literals come from
    the ARXML and `docs.rte_type_headers` only (§9).
    **Wherever this file names "an existing test case" as a source, that source
    does not exist in this mode** — an item with no other source is an Open
    Point;
  - a legacy or manual test-case workbook found in the project folder is **not**
    a substitute input. Do not open it, register it, mine it for spellings, or
    cite it as evidence. Raise one Phase-1 question quoting the recorded
    decision, and proceed under the decision until the engineer changes the
    config (workflow-discipline §1.2).

*(Observed: in a from-scratch project a run registered a discovered legacy
export as "the existing spec", reasoning that a mandatory input should be
resolved, then built a coverage baseline, a name mapping and four "defects in
the existing spec" on it — all withdrawn once the engineer saw it.)*

## 1. The test basis: Functional_Architecture, not SW requirements

An SWE.5 test case traces to an **architecture object** — a component, a port,
a runnable — so the test basis is the **Functional_Architecture** DOORS export
(`docs.functional_architecture_export`). That is **one** DOORS module, and it
contains its own **UserDefinedTypes chapter** (section 1.2) — the `in
UserDefinedTypes` references point *within* the same document, not at a
separate module. The SW requirements export is the SWE.6 basis and is **not
read by this skill**; do not accept one in place of the other
(workflow-discipline §1.1).

Every object carries a **name** (`Object Heading`) and a **text**
(`Object Text`), and this skill needs both — the names give the ports, types
and members, the text gives the ranges and the `DataType:` lines. The export
may carry them as two columns, as one column holding both, or as two views
joined on `ID`; workflow-discipline §1.3 detects which, and decides what a
names-only export can still support.

### 1.1 How the architecture module is laid out

Numbering varies by project — confirm it at the Phase-1 gate rather than
hardcoding these numbers. Per level, what is in the **name** and what is in the
**text**:

| Section | Name holds | Text holds | Used for |
|---|---|---|---|
| `1.1` | component-diagram entries per module | — | `aFeature` cross-check when resolving a module |
| `1.2` | **the type name** (`Mot_Mov_Data_St`, `ParkLck_State_en`) | the type's prose description | §5.2 |
| `1.2.<n>.<m>` | **a struct member** (`DutyCyc_perc_u08`, `Movement`) | that member's `Range:` / factor / init value | §5.2 |
| `1.3.1.<n>` | the component | purpose, runnable list, ROM/RAM, execution time | P-05 |
| `1.3.1.<n>.1.<m>` | the runnable | task mapping ("should be called from 2msec Task_FUSA_2ms", "Triggered in the rte init") | P-05 |
| `1.4.1.<n>` | **the module** (architecture spelling) | the component's purpose | owns the ports below it |
| `1.4.1.<n>.<m>` | **the port**, direction-prefixed (`P_Mot_Mov_Data`, `R_ActPosn`), or a watchdog checkpoint (`SE01_MotCtrl_Log_Start_CP`), or a called API (`Ftm_Pwm_Ip_FastUpdatePwmDuty`) | "This port sends…" / "This port receives…" + `DataType: <T>` | P-01/P-02/P-03/P-06 — one interface each |
| `1.4.1.<n>.<m>.<k>` | **the data element** (`Data`, `Speed`, `State`) | `DataType: <T> in UserDefinedTypes`, `Range: [...]` | §5.2 |
| `1.5` | sequence/flow entries | the flow description | usually review-only (§6) |

Two traps at the `1.4` level:

- The element name in `1.4.1.<n>.<m>.<k>` is the **architecture's** name for it
  (often just `Data`) and is frequently **not** the element name in the RTE
  symbol (`Rte_Read_R_Mot_Mov_Data_Mot_Mov_Data` — element `Mot_Mov_Data`, not
  `Data`). Take the RTE symbol from the ARXML port and the RTE header (§9),
  never by concatenating the architecture's names.
- An object's `aFunctionModule` can disagree with the section it sits under
  (a port under `FUSA_MotCtrl` carrying `aFunctionModule = FUSA_ParkLckCtrl`).
  Use the **section** for ownership and the **attribute** for the scope filter,
  and report every disagreement as an Open Point rather than silently picking
  one.

### 1.2 Scope filter

Two different sets come out of this step, and they must not be confused: the
objects test cases are **authored from** (they get heading rows and cases, in
their module's section), and the objects that are only **read** to ground those
cases.

**Authored from** — architecture objects where:

- `aFunctionModule` = the target module, **or** the object is a direct child of
  the target module's own architecture section while carrying a different
  `aFunctionModule` (see below), **or** — only under `peer_depth: peer_ports`
  (§2) — `aFunctionModule` = one of the target's direct peers
- `aTestability` ∈ `integration_test.testability_filter`
- `aStatusOfAnalysis` ∈ `attributes.status_filter`
- `aRequirementObjectType` = `functional requirement` or `non functional requirement`
- Object text is non-empty

**Read for grounding, never authored from** — the port at the far end of each
in-scope interface (direction and type cross-check, §2), every `1.2`
type/member object the in-scope ports reference, and the `1.4.1.<n>.<m>.<k>`
information children (type/range detail). Objects of type `information` are
never test-case sources.

Report the count at each filter step — expect heavy attrition (objects with no
text, or that are information/feature/feature-description rows, are common) —
together with the match count of each configured filter value and any
unclassified chapter the filter dropped wholesale (the input-hygiene checks,
workflow-discipline §7).

**Section ownership beats `aFunctionModule` for nested service objects.** Some
ports sit under a module's own section but are owned by a *service* module —
watchdog supervision checkpoints are the standing case (`aFunctionModule =
WdgM` under `1.4.1.<n>.<m>`), and `Os`, `Dem`, `NvM` and `Dcm` behave the same
way where a project uses them. An object like this belongs to the run **when
its section number is a child of the target module's own section**, because
the architecture places the checkpoint in that module's supervised entity (the
ARXML lists it under that software component).

Scope it by **section prefix, not by a blanket allowance on the
`aFunctionModule` value**. Allowing `WdgM` globally would pull every module's
checkpoints into every run — in the MQBST2 baseline that is 15 checkpoint
objects across 8 different modules, of which a run for `FUSA_MotDrv`
(section `1.4.1.1`) must select exactly two: `1.4.1.1.2` and `1.4.1.1.3`.

Such an object sits under the **target module's** section heading and keeps
**its own** `aFeature` on the generated case, never the section's (§8) —
both engineer-confirmed for the watchdog checkpoints on 2026-10-05. Do not
filter on `aFeature` either: it is not uniform even within one service, as the
MQBST2 checkpoints carry `Watchdog` on 13 objects and `System Faults` on 2.

Report these objects separately in the scope count and name them in Open
Points, so the engineer can see which objects came in by section rather than by
`aFunctionModule`.

### 1.3 `aTestCriteria` is the engineer's own stated approach

Every in-scope object carries `aTestCriteria` — the approach the architect
already wrote down. It is an input, not decoration: pick the pattern it names
(§6 maps the observed wordings to patterns), and where a generated case cannot
follow it, say so in Open Points instead of substituting your own approach. An
empty `aTestCriteria` on an in-scope port is a Phase-1 question, not a licence
to choose freely.

## 2. The module and its peers (write side / read side)

An integration test case exercises **one interface across two modules**: the
module that writes it and the module that reads it. So selecting a module
selects every interface it is an end of, and every case names the module at the
other end — but whether that peer also gets a section of its own is a separate,
explicit decision (**Depth**, below, and §3).

**Direction** — the port's **name prefix** is authoritative, because it is also
the spelling the test-spec module uses for its headings:

- `P_<Element>` → **write (provide) side** — the writing module's
  `Rte_Write_P_<port>_<element>` symbol (an ARXML `P-PORT-PROTOTYPE`).
- `R_<Element>` → **read (require) side** — the reading module's
  `Rte_Read_R_<port>_<element>` symbol (an ARXML `R-PORT-PROTOTYPE`).
- A checkpoint name (`SE01_<Module>_Log_Start_CP`) → watchdog supervision (P-03).
- A bare API name (`Ftm_Pwm_Ip_...`, `Aec_Ip_Spi...`) or a port whose text reads
  *"This client port is used…"* → **client/server**, `Rte_Call_...` (P-06), not
  a data flow.
- A port whose **far end is the basic software, not another application
  module** — its data element is mapped to a system signal or signal group in
  the ARXML data mapping (the port feeds or is fed by a bus message), it is a
  mode-switch or service port (`Rte_Switch_…`, `Rte_Mode_…`, a `ComM`/`EcuM`/
  `IoHwAb` service interface), or its text reads *"This port sends the CAN
  message…"* / *"…received from the bus…"* → **application ↔ basic-software
  integration** (P-10). The peer is the service named by the ARXML (`Com` with
  the I-PDU, `ComM`, `EcuM`, `E2E`), never an application module; it gets no
  section and no mirror.

Cross-check the prefix against the text (*"This port sends…"* vs *"This port
receives…"*). They usually agree; where they don't, the prefix wins and the
disagreement is an Open Point. A port with **neither** a prefix nor directional
text is a Phase-1 question.

**Peer resolution** — for each port of the target module, find the port at the
other end:

1. Primary key: **the name with the prefix stripped**. `P_Mot_Mov_Data` in
   `FUSA_MotCtrl` pairs with `R_Mot_Mov_Data` in `FUSA_CDD_MotDrv`.
2. Confirm with the **data type** named on the port's `DataType:` line (and on
   its `1.4.1.<n>.<m>.<k>` child). Name match + type mismatch is an Open Point,
   not a resolved pair.
3. Direction must be opposite: a `P_` port pairs only with an `R_` port.
3a. Confirm with the **ARXML composition**: an `ASSEMBLY-SW-CONNECTOR` joining
   the two port prototypes is the design model's own statement of the pairing.
   A pair the architecture text implies but the composition does not connect,
   or a connector the architecture text does not mention, is an `Input
   hygiene` Open Point — the architecture and its model disagree — and the
   pair is a Phase-1 question, never a pick.
4. Casing drifts (`Mot_Mov_Data_st` vs `Mot_Mov_Data_St`) — match
   case-insensitively, but take the spelling you emit from the ARXML and the
   RTE header (§9), and note the variant in Open Points.
5. **Exactly one candidate** → resolved. **Several, or none** → a numbered
   Phase-1 question. Never pick the closest-looking module. For "none", run a
   near-match search first (a single transposed or extra character is common —
   `P_Hs1_Div_a_Phy` vs `R_Hs1_Div_a_Phyn`, `unplausibel` vs `unplausible`) and
   put the near match in the question as the proposal; never auto-accept it.
6. One writer may have several readers (a broadcast signal). Every reader is a
   peer, and each writer→reader pair is its own interface (but see **Fan-out**).

**Depth — which interfaces are authored.** `integration_test.peer_depth`
(project default in `ai_test_project.yaml`; per-module override in the
manifest's `scope.peer_depth`):

- **`target_ports`** (default) — only the interfaces the **target** module is
  an end of. Each peer is **named, not authored**: it appears inside every case
  as the far end — a P-01 case must name the writer's `Rte_Write` symbol and
  the reader's `Rte_Read` symbol, each with its module — but it gets no
  section, no heading row, and no case sourced from its own objects.
- **`peer_ports`** — also every interface the target's **direct** peers are an
  end of. Their own far ends (peers of peers) are in turn named, not authored.
  This is one extra hop, not a transitive closure, and it is typically an order
  of magnitude larger. An interface between the target and a peer is still
  authored once, under the target.

Whether a peer *also* carries a mirrored copy of the target's interfaces is a
separate setting (§3). If `peer_depth` is unset, it is a Phase-1 question, and
the question states the **projected row count for each depth, with mirroring on
and off**, from the interface inventory — marked as an estimate where a type is
still unresolved. *(Observed: the two depths gave 142 and 12 cases for the same
module; the engineer wanted 12, and the run had chosen 142 without asking.)*

When confirming a narrowed scope, say explicitly that an excluded peer still
appears in the body of each case as the far end. Read literally, "not in scope"
would remove it from the cases too, and no data-flow case could then be
written.

**Fan-out.** Step 6 gives each writer→reader pair its own case set, so a target
port with several far ends multiplies output fast. Show the fan-out per target
port in the peer matrix and, wherever a target port has more than one far end,
ask whether to author every pair or a named subset — recording the answer in
the manifest's `scope.interfaces`. Never multiply silently.

Report the result as a **peer matrix** at the Phase-1 gate, and cache the
pairings in `ai_test_project.yaml` `integration_test.peer_modules`:

| Interface | Data type | Writer module (ARXML SWC) | `Rte_Write` symbol | Reader module (ARXML SWC) | `Rte_Read` symbol | ARXML connector | Far ends of this target port | Projected cases | Existing cases (`extend_existing` only) |
|---|---|---|---|---|---|---|---|---|---|

## 3. Mirroring: a second copy under the peer's section (off by default)

`integration_test.peer_module_mirroring` (default **false**; per-module
override in the manifest's `scope.peer_module_mirroring`) reproduces a
structure some DOORS test modules carry: the same interface authored a second
time, under the peer module's section.

- **Primary** — always under the **target** module's section, headed by the
  target's own port: `P_<Element>` where the target writes it, `R_<Element>`
  where it reads it.
- **Mirror** — only when mirroring is on — under the **peer's** section, headed
  by the connection `<WriterModule> to <ReaderModule>`.

Both copies test the same interface with the same breakpoints; they differ only
in which section they sit under. Mark every row primary or mirror in the
Traceability sheet so the engineer can drop the mirrors.

The connection-heading spelling is a project convention, never an inference:

- `extend_existing` (§0.1) — copy the spelling the existing export uses for
  that pair, which is often neither the `aFunctionModule` spelling nor
  consistent (`FUSA-MotCtrl to CDD_Drv`), and record the variant in Open
  Points.
- `from_scratch` — there is no observed spelling to copy, so every mirror
  heading would be invented. Propose `<WriterModule> to <ReaderModule>` in the
  confirmed test-spec spellings (§4) and confirm it once at the Phase-1 gate.
  This is why mirroring is off by default: it doubles the output, and in a
  from-scratch project every heading it adds is a proposal.

Do not infer a placement rule from a legacy spec either: the one this skill was
first built against put the connection heading mostly, but not consistently,
under the reader's section.

If mirroring is off, emit the primary only, and say once in the run summary
that mirroring is off — not as an Open Point per peer section.

## 4. Resolving the module name

### 4.1 Resolve the argument before filtering

The argument is meant to be an `aFunctionModule` value, but engineers type
whichever spelling they know — the ARXML component name, the architecture
heading, a feature name — and sometimes two of them at once. Before any scope
filtering, resolve every argument against **all four axes** and report which
one matched:

| Axis | Found in | Example |
|---|---|---|
| `aFunctionModule` — the scope filter's key | the attribute column | `FUSA_MotDrv` |
| architecture section heading | the `1.4.1.<n>` object's name | `FUSA_CDD_MotDrv` |
| ARXML component | `APPLICATION-SW-COMPONENT-TYPE` short-name (also the `Rte_<Swc>.h` name and the RTE symbol prefix) | `CDD_MotDrv` |
| `aFeature` — a **different axis**, never a module | the attribute column | `Motor Control` |

- **Exactly one module on the three module axes** → proceed, saying which axis
  matched and which `aFunctionModule` it resolved to. The manifest is keyed by
  that resolved value.
- **An `aFeature` value** → say so; list the modules whose objects carry that
  feature, with their object counts, and ask which one is meant. Never run a
  feature as a module.
- **Several arguments that collapse to one module** (two spellings of the same
  component) → say so and confirm that it is one run, not two.
- **One argument matching several modules, or none** → run the near-match
  search (§2 step 5) and ask.

Then dry-run the resolved value through the scope filter (§1.2) before going
further: one spelling, used as an `aFunctionModule`, can select a handful of
non-port objects while the module's ports carry another. **A scope that yields
zero `1.4.1.<n>.<m>` port objects is a hard STOP**, reported with the attrition
per filter step — never an empty workbook reported as success.

*(Observed on one module across two runs: first an argument that was an
`aFeature` value; then the ARXML component spelling, which as an
`aFunctionModule` selected two objects, neither of them a port.)*

### 4.2 The mapping table

One module can carry **four** spellings, and they are all in play:

| Key in `module_name_mapping` | Where | Example |
|---|---|---|
| *(the key itself)* | `aFunctionModule` attribute | `FUSA_MotDrv` |
| `architecture` | architecture `1.4.1.<n>` section heading | `FUSA_CDD_MotDrv` |
| `arxml_swc` | ARXML `APPLICATION-SW-COMPONENT-TYPE` | `CDD_MotDrv` |
| `test_spec` | integration-test-spec section heading | `Mot_Drv` (found in an existing spec) or the confirmed proposal (from scratch) |

**The integration-test export has no `aFunctionModule` column** — only
`aFeature`. Existing test cases for a module are located by walking the
`Object Heading` hierarchy: a module-level heading opens a section, and
everything until the next module-level heading belongs to it.

In `from_scratch` mode (§0.1) there is no test-spec export to search: skip the
discovery below, propose the architecture `1.4.1.<n>` spelling as the
test-spec heading, confirm it as a Phase-1 question, and cache the confirmed
answer like any other mapping.

The vocabularies rarely match exactly (spelling differences, transposed words,
hyphen vs underscore, inserted `CDD`). **Discovery method** (`extend_existing`
only — apply it to whatever module you're given):

1. Search the integration-test-spec export's Object Headings for the target
   module name and close near-matches (transpositions, common misspellings).
2. Cross-check: the `aFeature` mix of the module's architecture objects should
   broadly match the `aFeature` mix of the candidate section. A large mismatch
   means the wrong section was picked — stop and ask rather than proceed on a
   guess.
3. Once resolved, **write all four spellings to `ai_test_project.yaml`
   `integration_test.module_name_mapping`** keyed by `aFunctionModule`
   (workflow-discipline §4) so the next run — this engineer's or another's —
   doesn't repeat the search. If the module is not on the cached list and cannot
   be resolved by search, ask.

Do this for a peer module only when it gets a section of its own
(`peer_depth: peer_ports`, or mirroring on): a peer section needs the peer's
test-spec spelling, not its architecture spelling. A peer that is only named
inside cases needs no test-spec spelling.

## 5. Interface inventory and the values to exercise

### 5.1 Inventory

The unit of an integration test case is **the interface**. Build the list from,
in order of preference: (1) the architecture's `1.4` port objects of every
module authored from (§1.2, §2 Depth); (2) in `extend_existing` mode only, the
existing test-case section headings — each port heading and each connection
heading; (3) the ARXML (ports, connectors, runnables) and the RTE headers.
For each interface report its name, writer/reader modules, `Rte_*` symbols,
data type, and — in `extend_existing` mode — how many existing test cases it
already has.

Then split into: already covered, no test cases (your scope), and interfaces
found in the architecture but not resolvable to RTE symbols. List the
**basic-software-facing** ports (§2, P-10) separately, each with the system
signal / signal group, I-PDU and message it maps to in the ARXML data mapping
and the communication database, and the attributes the P-10 cases will use
(cycle, fast cycle, repetitions, delay, timeout, E2E protection). Check the standing
obligations: does every module authored from have a `Watch Dog for <module>`
group, a task-configuration group, and a heading for every interface it is an
end of (plus a connection heading per mirror, when mirroring is on).

In `from_scratch` mode (§0.1) source (2) does not exist: the coverage baseline
is empty and every interface is "no test cases". Never substitute a legacy
workbook found in the folder for it.

### 5.2 Values come from the UserDefinedTypes chapter

For each interface, resolve its `DataType:` in the architecture's `1.2` chapter
— the type name is a `1.2.<n>` object's **name**, its struct members are the
`1.2.<n>.<m>` children's **names**, and each member's `Range:` is in that
child's **text** — then generate accordingly:

| Type shape | Cases |
|---|---|
| Scalar with a documented `Range:` | **5** — Min, Mid, Max (`positive`); Min-1, Max+1 (`negative`) |
| Enum | **one per literal**, all `positive`; plus **one** `negative` case by default (rules below) |
| Struct | the **5-case set per member**, member by member (a 5-member struct → 25 cases) |
| Boolean | both values, `positive`; the architecture text usually states the meaning (`0 - Enabled` / `1 - Disabled`) — carry it into the case |

**Reading the range from the text.** Match the label loosely: `Range` followed
by any separator (`:`, `-`, `=`, or none) and a bracketed pair, tolerating
stray spaces inside the bracket and a unit after it — `Range: [0-100]`,
`Range - [0- 100]%` and `Range [0 - 100]` are one and the same range. A strict
`Range:` match misses the variants and silently falls back to the type limits:
a quiet wrong answer. Report every variant that is not `Range: [<min>-<max>]`
in Open Points as an architecture-text finding. Where a bound cannot be read
unambiguously — a negative bound whose minus sign could be the separator, a
factor or offset inside the bracket — ask; never guess which hyphen is which.

Rules:

The in-range triple and the out-of-range pair come from **different sources**.
Do not derive all five from one range.

- **Min / Mid / Max — the documented `Range:`** in the UserDefinedTypes entry
  when it has one; otherwise the implementation type's limits (`uint8` → 0/255).
  In a names-only run (workflow-discipline §1.3) the ARXML `DATA-CONSTR` takes
  the documented range's place where the type has one. **Mid** is the
  arithmetic midpoint of whichever range you used, rounded **toward zero** when
  that is not a whole number on an integer type (`0..255` → `127`,
  `-32768..32767` → `0`); a floating-point type takes the exact midpoint. Say
  which range you used, per interface, in the Traceability sheet — the engineer
  needs to see the choice, not discover it. The source code is never consulted
  for a range (§9): a constant in the implementation is part of the thing under
  test, not a source of expected values.
- **Min-1 / Max+1 — always the IMPLEMENTATION TYPE's limits**, never the
  documented range, even when the documented range is narrower. These two cases
  exist to exercise what the type does at its edges, so for a `uint8` member
  they are *always* written `-1` → reader shows `255`, and written `256` →
  reader shows `0`, whatever the documented `Range:` says.

  A `[0-100]%` `uint8` member therefore gives **Max = 100 and Max+1 = 256**: the
  two are deliberately not arithmetically adjacent, and a run that "corrects"
  Max+1 to 101 for adjacency is wrong.

  **Compute the wrap at both ends, each from its own type.** The writer-side
  variable cannot hold a value its type cannot represent any more than the
  reader can: on a `uint8` member the writer-side variable *displays* `255`
  after `-1` is entered and `0` after `256` is entered, exactly as the reader
  does. P-01's result step 2 therefore states the value the writer displays,
  with the entered value in brackets (§7). Because Min-1 and Max+1 are both
  taken from the type, this applies to **both** negative cases of every member
  — not only to Min-1 on an unsigned type. Only where the writer's and the
  reader's types differ in width do the two ends legitimately display different
  values. If either end's type is unresolved, do **not** guess its wrap — leave
  that expected value as a marked placeholder and raise an Open Point.

  *(Engineer ruling, FUSA_MotDrv SWE.5 validation 2026-10-05: a generated
  Max+1 = 101 was rejected with "If its uint8 max value is 255 so max+1 value
  should b 256 and thes result should be 0." Min = 0 / Mid = 50 / Max = 100 from
  the documented `[0- 100]%` range were accepted in the same review, which is
  what fixes the split between the two sources.)*
- A value **out of the documented range but inside the type** (`101` on a
  `[0-100]%` `uint8`) gets **no case**. It was put to the engineer on
  2026-10-05 and declined — "Not required, we need only for 256" — so the
  five-case set stands as defined above. Do not generate a sixth case and do
  **not** re-raise it as a Phase-1 question on later runs; this answer is
  settled project policy, not a per-run judgement.
- **No documented range and no resolvable implementation type** → the interface
  gets **no** cases and an Open Point. Never invent a limit, a step size, a
  member name or an enum literal (no-fabrication.md). Expect this to be common:
  in a typical export only about a third of struct members carry a `Range:`.
- **Enum literals are not in the architecture module.** An enum type
  (`*_en`) is a single `1.2.<n>` object with no children and no literal list —
  only a prose description ("This enum contains the mute mode types"). So a
  literal (`MOT_MOV_ROT_FWD_E`) is copied verbatim from `docs.rte_type_headers`
  (`Rte_Type.h`/ARXML) or — in `extend_existing` mode only — from an existing
  test case, and an enum interface with no resolvable source gets **no** cases
  and an Open Point. Never
  reconstruct a literal from the description, and never infer the literal set
  from the number of values an existing case happens to exercise — say in the
  Traceability sheet which source each literal came from.

  Reach the literals through the type's **own reference** to its
  `COMPU-METHOD`, never by matching a `COMPU-METHOD`'s name: an ECU extract can
  carry a `COMPU-METHOD` named after one type that holds another type's
  literals. A name-matched `COMPU-METHOD` whose literals do not belong to the
  type is an Open Point, never a source.
- **Enum negative case — one, by default.** Engineers expect a negative case on
  every enum interface, so author one at the first value outside the valid set,
  taken (in order) from: a literal the type documents as invalid/reserved; else
  the ARXML `DATA-CONSTR` upper limit + 1 — the constraint documents the valid
  range even where no literal is marked invalid. State in Traceability which of
  the two it came from. Neither available → no negative case, and an Open Point.
  The number is entered as-is; if it is not representable in the enum's base
  type, the wrap rule above applies. Never support the case with a claim about
  the reader's implementation (a missing `default:`): the code is not read
  (§9), and the reaction to an invalid literal comes from the architecture
  text or is an Open Point (no-fabrication.md).

## 6. `aTestCriteria` → pattern

| `aTestCriteria` says (observed wordings) | Pattern |
|---|---|
| "Check in RTE whether the RTE variables is getting updated …" | **P-01** / **P-02** |
| "Interface Test with Min, Mid, MAx and border values." | **P-01** with the full 5-value set (§5.2) |
| "Check for the runnables in the RTE task table … periodicity of periodic runnable" | **P-05** |
| "Check for the alarm configuration for all the TASK …" | **P-05** |
| "These are the client ports … check for the value in the respective server function" | **P-06** |
| "Execute the DID and check for the server function is hit" | **P-07** |
| "Check the CAN message / signal is transmitted…", "…the message is sent with the updated values", "…the signals are updated in the same frame" | **P-10a** (coherent transmission) |
| "Check the message is sent on change…", "…fast cycle…", "…repetitions…" | **P-10b** (transmission trigger) |
| "Check after reset / wake-up / mode change the message starts…", "…counter starts at…", "…IPDU group…" | **P-10c** (start-up and mode switch) |
| "Check the timeout of the received message…", "…RTE status / E2E status on timeout…", "…substitute value…" | **P-10d** (reception timeout) |
| "Check the E2E counter / CRC of the sent message…" | **P-10e** (E2E at the hand-off) |
| "review" / "This can only be reviewed" / "Review of SW Architecture" / "The flow needs to be verified by the testing team" / "The Sequence to be checked by the Test Team" | **P-08** — no debugger test case |
| "Can be checked by XCP only" / "using the XCP variable" | **P-08**, noting XCP as the required means |

Typos and case vary between objects ("wehther", "CHnage", "ini runnable") —
match on meaning, and never copy a misspelling into a generated case.

**P-08 is never applied silently.** A `review`-type `aTestCriteria` suppresses
a whole object, so before emitting P-08, check whether the object nevertheless
has a concrete, observable symbol in a supplied input — an `Rte_Call_*`,
`Rte_Write_*` or `Rte_Read_*` on the component's ARXML ports or in its RTE
header, or a called API the architecture lists as a port. If it does, the
criterion and the port list disagree, and that is a **Phase-1 question**, not
a decision to take alone. The default proposal in that question is **author
the case**: `aTestCriteria` is often older than the port list. An object that
maps to P-08 *and* has no resolvable symbol needs no question — Open Points is
enough.

Observed failure (FUSA_MotDrv, 2026-10-05): `Ftm_Pwm_Ip_FastUpdatePwmDuty`
(6227), `Ftm_Pwm_Ip_UnMaskOutputChannels` (6230) and the two WdgM checkpoint
ports (5847 / 5904) were all suppressed to heading rows on `aTestCriteria =
"review"` / `"1. Review the flow"`. All four had symbols on the component's
ports in the ARXML and RTE header — the symbols were in hand and nothing was
unresolved. The QA
engineer rejected all three heading rows at validation with "TestCases need to
Design for this interfaces".

## 7. Patterns

Pick the pattern that fits; do not invent a new one without saying so.

**P-01 — RTE data flow, writer to reader.** The dominant pattern. Both
breakpoints are named, each by its RTE symbol and its own module.

```
Object Heading (group):  P_<Element>            (or R_<Element>)
Object Text (case):      Test case to verify the <Element> for <Min|Mid|Max|Min-1|Max+1> Value.

atcPreconditions:
- Reset the ECU
- Wake up the ECU
- Flash the ECU

atcActions:
1. Set the Breakpoint at the call Rte_Write_P_<port>_<element> in module <WriterSwc>
2. Edit the argument of Rte_Write_P_<port>_<element> (<member>, for a struct) with <value>.
3. Set the Breakpoint at the call Rte_Read_R_<port>_<element> in module <ReaderSwc>
4. Verify the value

atcResult:
1. Breakpoint should be hit.
2. The argument of Rte_Write_P_<port>_<element> should be update to <displayed-at-writer> value.
3. Breakpoint Should be hit.
4. The out-parameter of Rte_Read_R_<port>_<element> should be update to <displayed-at-reader> value.

atcPostconditions:
- System Shall be stable
- Delete all Breakpoints
```

Both breakpoints are named by **RTE symbol and module** (§9): the symbol as
the RTE header spells it, the module as the ARXML software component
(`module_name_mapping.arxml_swc`). No file name, no line number and no
variable name from the implementation appears anywhere in the case: the tester
sets a symbol breakpoint on the call, or locates it in the module at execution
time, so the case stays valid across code revisions and never carries an
assumption about how the module is written. The values edited and observed are
described by **role** — the argument of `Rte_Write`, the out-parameter of
`Rte_Read`, the member of either for a struct — which the debugger shows at the
breakpoint. `Traceability` cites the ARXML port and the RTE header the symbol
was confirmed in.

`<displayed-at-…>` is the value that end's variable shows (§5.2). For an
in-range value it equals `<value>`. Where `<value>` is not representable in
that end's type — both negative cases of every member — write the displayed
value and put the entered one in brackets:
`<writer-side variable> should be update to 255 value (entered: -1).`

For a struct, step 2 edits the **member** and the title names the member
(`Test case to verify the MessageTimeout_u8 for Min Value.`). For an enum, the
title names the value (`… of Movement for 0 value.`) and the result names the
literal (`Movement should be update with MOT_MOV_ROT_FWD_E value.`).

**P-02 — inter-module connection (the mirror).** Identical body to P-01;
heading form `<WriterModule> to <ReaderModule>` (§3). Only emitted when
mirroring is on.

**P-03 — watchdog supervision.** Heading `Watch Dog for <Module>`. One case per
supervision checkpoint the module registers (start and end):

```
Object Text:  Test case to verify the <SE0n_<Module>_Log_Start_CP>
atcActions:   1. Set the Breakpoint at the call Rte_Call_<SupervisionPort>_<checkpoint>_CheckpointReached in module <Swc>
atcResult:    1. Breakpoint should hit and Watch Dog should Reset.
```

Checkpoint names come from the ARXML (the supervised entity's checkpoints
under the component) and the `Rte_Call_…_CheckpointReached` symbol from the
RTE header (§9) — never constructed from the module name.

**P-04 — negative / boundary value.** The Min-1 and Max+1 members of the
5-value set, and the enum negative case (§5.2). `atsType = negative`. The
positive/negative ratio is a sanity check to report, not a quota to enforce.

**P-05 — task configuration & runnable timing.** From the `1.3.1.<n>.1.<m>`
non-functional objects. Two shapes, grouped under a task-configuration section
heading per module.

*Initialization* — the test is that the Init runnable runs at start-up: break
on it, restart the debugger, see the breakpoint hit and the runnable return.
That is the shape whatever the runnable does, counter, flag or neither (the
engineer's stated convention, FUSA_MotDrv Q-19):

```
Object Text:  Test case to verify the Initialization of <Module>
atcActions:   1. Set the Breakpoint at the entry of runnable <InitRunnable> in module <Swc>
              2. Restart the debugger.
              3. Run to the return of <InitRunnable>.
atcResult:    1. Breakpoint should be hit at start-up, confirming the initialization of <Module> is triggered.
              2. <InitRunnable> should return, confirming the initialization of <Module> is executed.
```

The runnable's name is the architecture's `1.3.1.<n>.1.<m>` object, confirmed
against the ARXML `RUNNABLE-ENTITY` and its `SYMBOL` (the function the RTE
calls, §9). Break at the **entry** and run to the **return** — the
architecture-only equivalent of the earlier "break on the last statement"
convention, which needed the code to find that statement. Do not add a step
checking an initialised flag: the implementation's variable names are not
read (§9). The Init runnable often has no `1.3.1.<n>.1.<m>` object of its
own; trace the case to the nearest ancestor (output-format.md, a case with no
object of its own).

*Cyclic runnable* — the runnable is called at its period:

```
Object Text:  Testcase to verify the Runnable time for <Module> for every <n>msec.
atcActions:   1. Set the Breakpoint at the entry of runnable <CyclicRunnable> in module <Swc>
              2. Resume and record the timestamps of <k> consecutive hits (debugger trace or OS timestamp).
atcResult:    1. Breakpoint should be hit
              2. Consecutive hits should be <n> ms apart (tolerance: one tick of the task's counter, from the architecture text; otherwise an Open Point).
```

The period is checked from **consecutive hits of the runnable's entry**, never
from a counter or flag named in the implementation: the code is not read (§9),
and the `<Module>_Cyclic_<n>msec_counter` names of earlier versions of this
pattern belonged to one legacy stub and exist in no current module — using
them is a fabrication (no-fabrication.md). Where the engineer prefers to watch
a variable, it must be one the architecture text or an A2L names; otherwise the
hits are the observation.

The period comes from the architecture object's own text ("This runnable should
be called from 2msec Task_FUSA_2ms"). An ARXML `TIMING-EVENT` that contradicts
it never overrides the architecture text — use the architecture period and
raise the mismatch in Open Points. In `extend_existing` mode, existing cases
contain period mismatches between action and result; do not copy one, and flag
any you relied on.

**Check the period and the trigger against the ARXML.** The architecture text
states the intent; the SWC description states what the RTE was generated for.
Before writing a P-05 case, find there:

- **the runnable** — the `RUNNABLE-ENTITY` whose `SYMBOL` the case breaks on;
- **its trigger** — a `TIMING-EVENT` with its `PERIOD` for a cyclic runnable,
  an `INIT-EVENT` (or the project's start-up event) for the Init runnable;
- **the period** — the `TIMING-EVENT` period in seconds, converted to the
  architecture's unit.

Cite what you found in Traceability. Where the ARXML agrees with the
architecture, the case stands as written. Where it disagrees — another period,
no timing event, a runnable the architecture lists but the ARXML lacks — write
the case to the **architecture**, which is the test basis (the case should then
fail on the bench, and that is the point), and raise the mismatch as an `Input
hygiene` Open Point for the architect and the integrator. **Which OS task runs
the runnable is not checked here**: the OS configuration (ECUC tasks, alarms,
event-to-task mapping) and the generated OS/RTE code are implementation and
configuration artefacts, not architecture (§9); the task shows itself on the
bench when the breakpoint hits, and checking it belongs to the execution layer
(v2). Where the architecture text names the task, carry the name into the
case text as the architect's statement.

**P-06 — client/server port.** `Rte_Call_<port>_<operation>` at the caller, the
server runnable entered at the other end. Breakpoint at the call in the caller
module, breakpoint at the entry of the server runnable (its ARXML
`RUNNABLE-ENTITY` symbol, named with the server module), verify the argument
passed.

**P-07 — diagnostic DID / routine.** Only for the diagnostic modules
(`DiagReadData`, `DiagWriteData`, `DiagRoutineCtrl`) and only when
`aTestCriteria` names the DID approach:

```
atcActions:  1. Send DiagRequest DID <XX XX> from Diagnostic console.
             2. Set the Breakpoint at the entry of runnable <ServerRunnable> in module <Swc>
atcResult:   1. DID Should be Positive Response <SID+0x40> <XX XX> XX XX XX.
             2. Breakpoint should be hit.
```

The DID comes from the DiagSpec and the server runnable from the ARXML (the
operation's `RUNNABLE-ENTITY`, §9) — or, in `extend_existing` mode, from an
existing case. Note that SWE.6
covers diagnostics far more thoroughly — a diagnostic interface here is tested
only as an interface.

**P-08 — not testable by the debugger → no test case.** Where `aTestCriteria`
asks for a review, a sequence walkthrough by the test team, or XCP-only
observation, emit **no** concrete case. Record the object in Open Points with
the criterion verbatim and the reason. If the project's convention is to carry
such objects as heading rows with `no testcase` attributes, emit the heading row
only (output-format.md).

**P-09 — OS trace / timing measurement.** Rare. Only generate if the engineer
asks for it explicitly in this run's instructions.

**P-10 — application ↔ basic-software integration.** P-01 tests a value
passed between two application modules. P-10 tests the **hand-off between an
application module and the basic software** — the communication stack (`Com`),
network and ECU state management (`ComM`, `EcuM`), end-to-end protection — at
the ports §2 identifies as basic-software-facing. The stimulus is applied with
the debugger at the module's RTE call, exactly as in P-01; the observation is
the **bus**, in the trace tool, decoded with the communication database. The
expected behaviour comes from the ARXML — the data mapping that ties the port's
data element to a system signal or signal group, the I-PDU and its timing, the
receiver's `ALIVE-TIMEOUT`, the `END-TO-END-PROTECTION` entry — and from the
communication database's message attributes (cycle, fast cycle, repetitions,
delay, timeout). Nothing is taken from the Com or CanNm configuration code.
Enabled by `integration_test.bsw_service_patterns` (default on); the manifest's
`scope.bsw_service_patterns` overrides it per module. *(Observed: of nineteen
customer HiL findings on one release, four were defects at this hand-off — a
frame sent before all its signals were written, two error flags set in one
frame, a message counter reset twice at start-up, a reception timeout taken
from the module's own cycle instead of the stack's — and no test level had a
pattern for them.)*

Five shapes. Each case names the port's `Rte_` symbol with its module, the
message and the signals from the communication database, and the ARXML object
it rests on in `Traceability`. All five keep the P-01 preconditions and
postconditions, with one precondition added: `- Bus trace connected and
decoding with <communication database>`.

*P-10a — coherent transmission of a signal group.* For a `P_` port whose data
element is a struct (or several elements) mapped to one I-PDU:

```
Object Heading (group):  P_<Element>
Object Text (case):      Test case to verify the <Element> is transmitted coherently in message <Msg>.
atcActions:   1. Set the Breakpoint at the call Rte_Write_P_<port>_<element> in module <Swc>
              2. Edit every member of the argument of Rte_Write_P_<port>_<element> with <m1> = <v1>, <m2> = <v2>, … (all values different from the current frame).
              3. Resume.
atcResult:    1. Breakpoint should be hit.
              2. The argument should show <m1> = <v1>, <m2> = <v2>, ….
              3. The first frame of message <Msg> after resume should carry signal <S1> = <v1>, <S2> = <v2>, … all in that same frame; no frame carries a mix of old and new values.
```

The member → signal mapping is the ARXML `SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING`
(or per-signal mapping) and the message layout is the communication
database. Where the port's elements map to **several** I-PDUs, one case per
I-PDU, and an Open Point if the architecture text implies they belong
together. Values: one in-range value per member from §5.2's Mid, stated in
the case.

*P-10b — transmission trigger and repetition.* For a `P_` port whose message
has an on-change or fast-cycle behaviour in the database
(`GenMsgSendType` / `GenMsgCycleTimeFast`, `GenMsgNrOfRepetition`,
`GenMsgDelayTime`) or a `TRIGGERED` / `ON-CHANGE` transmission mode in the
ARXML:

```
Object Text:  Test case to verify the transmission of message <Msg> on change of <Element>.
atcActions:   1. Set the Breakpoint at the call Rte_Write_P_<port>_<element> in module <Swc>
              2. Edit the argument of Rte_Write_P_<port>_<element> with <value> (different from the current frame).
              3. Resume and record the timestamps of message <Msg> for <cycle × 3> ms.
atcResult:    1. Breakpoint should be hit.
              2. The argument should show <value>.
              3. Message <Msg> should be sent <n> times <fast> ms apart starting no later than <delay> ms after resume, every frame carrying <S> = <value>, then return to the <cycle> ms cycle. (<n>, <fast>, <delay>, <cycle> quoted from the database; tolerance from the OEM communication specification or an Open Point.)
```

*P-10c — start-up and mode switch.* For a module that controls a
communication mode or message group through a mode-switch or service port
(`Rte_Switch_<port>_<mode>`, a `ComM` user request, an I-PDU group control
operation), or for a transmitted message with a counter whose initial value
the database or the ARXML defines:

```
Object Text:  Test case to verify message <Msg> starts once after <reset | wake-up | mode <M>>.
atcActions:   1. Set the Breakpoint at the call Rte_Switch_<port>_<mode> in module <Swc>   (omit for a plain reset)
              2. <Reset the ECU | apply the wake-up | resume so the mode switch executes>.
              3. Record the first five frames of message <Msg>.
atcResult:    1. Breakpoint should be hit once (and once only) per <reset | wake-up | mode change>.
              2. Message <Msg> should start within <t> ms of step 2 (<t> from the architecture text or the requirement; otherwise checked as "starts", with an Open Point).
              3. Signal <Counter> in message <Msg> should read <init>, <init+1>, <init+2>, … with no value repeated and no value skipped; signal <S> should carry its initial value <v0> from the database.
```

*P-10d — reception timeout and indication.* For an `R_` port whose receiver
has an `ALIVE-TIMEOUT` in the ARXML or whose message has a timeout in the
database:

```
Object Text:  Test case to verify the timeout of <Element> (message <Msg>) is indicated after <T> ms.
atcActions:   1. Set the Breakpoint at the call Rte_Read_R_<port>_<element> in module <Swc>
              2. Stop message <Msg> on the bus from the rest-bus simulation at t0; resume.
              3. Observe the return value of Rte_Read_R_<port>_<element> at each hit until t0 + <T + tol> ms.
              4. Observe signal <OutSig> in message <OutMsg> (the module's output that reflects the timeout) until t0 + <T + tol> ms.
atcResult:    1. Breakpoint should be hit every <cycle> ms.
              2. —
              3. The return value should be RTE_E_OK (data valid) at every hit before t0 + <T − tol> ms, and RTE_E_TIMEOUT (or the E2E/qualifier status the ARXML names) at every hit after t0 + <T> ms.
              4. <OutSig> should keep its last valid value until t0 + <T − tol> ms and change to <timeout value> between t0 + <T − tol> and t0 + <T + tol> ms — never earlier.
```

`<T>` is the `ALIVE-TIMEOUT` of the port's `RECEIVER-COM-SPEC` or the
database's timeout attribute, `<tol>` the tolerance the OEM communication
specification or the architecture text gives; both quoted. The "never
earlier" check is the point of the case: a module that treats *no new frame
this cycle* as a timeout fails it. Where the module has no output that
reflects the timeout, step 4 is dropped and the case rests on step 3.

*P-10e — end-to-end protection at the hand-off.* For a transmitted message
with an `END-TO-END-PROTECTION` entry in the ARXML (or a counter and CRC signal
in the database):

```
Object Text:  Test case to verify the E2E counter and CRC of message <Msg> on transmission of <Element>.
atcActions:   1. Set the Breakpoint at the call Rte_Write_P_<port>_<element> in module <Swc>
              2. Edit the argument of Rte_Write_P_<port>_<element> with <value>; resume; repeat for <k> hits.
atcResult:    1. Breakpoint should be hit <k> times.
              2. In every frame of message <Msg>, signal <Counter> should increment by one modulo <range> per frame (no repeat, no skip) and signal <CRC> should be valid for the frame's payload under profile <profile> with data ID <id> (<range>, <profile>, <id> from the ARXML E2E entry).
```

Rules for all five: a value, cycle, timeout or tolerance that no ARXML entry,
database attribute or specification gives is an Open Point, never assumed; a
port whose far end is the basic software but matches none of the five shapes
is listed in Open Points with the reason; the trace resolution must be finer
than the timing measured (one message cycle at least), else the timing clause
is an Open Point. SWE.6's §11 timing cases measure the same bus behaviour
black-box; P-10 differs in that the stimulus is applied at the module's RTE
call, so a failure locates the defect at the hand-off rather than somewhere
behind the bus.

## 8. Attributes specific to this skill

| Attribute | Value |
|---|---|
| `atcPreconditions` | The three-line P-01 block, verbatim, unless the pattern states otherwise; P-10 adds the bus-trace line |
| `atcPostconditions` | `- System Shall be stable` / `- Delete all Breakpoints` |
| `atcRemark` | `Debug SW` |
| `aFeature` | Carried from the architecture object. On a mirrored case, carry the feature of the **object the case traces to**, not the section it sits under |
| `atsTestKind` | `Interface test` |
| `atsTestDesignTechnique` | `InterfaceTesting` |
| `atsType` | `positive` or `negative` (§5.2); P-10d is `negative` (the stimulus is a lost message), the other P-10 shapes `positive` |

## 9. Symbols and breakpoints — the architecture only, never the code

**The test basis for SWE.5 is the architectural design.** Every `Rte_` symbol,
runnable name, struct member and enum value in a case comes from one of two
architecture artefacts, and from nothing else:

- **The ARXML** (`docs.arxml`) — the software-component descriptions (ports,
  interfaces and their data elements, runnables with their `SYMBOL` and their
  timing/init/operation-invoked events, supervised entities and checkpoints),
  the composition (the connectors that pair a `P-PORT-PROTOTYPE` with an
  `R-PORT-PROTOTYPE`), and the system or ECU extract (the data mapping from
  port elements to system signals and signal groups, the I-PDUs and their
  timing, receiver `ALIVE-TIMEOUT`s, `END-TO-END-PROTECTION` entries — P-10),
  plus the data types, `COMPU-METHOD`s and `DATA-CONSTR`s behind them. It is
  the formal model of the architecture. The **communication database**
  (`docs.comm_database`) supplies the message layout and attributes P-10
  observes on the bus; it is a design artefact too, never a substitute for the
  ARXML on the RTE side.
- **The RTE headers** (`docs.rte_type_headers`, or the repository's own
  `layout.rte_inc`) — `Rte_<Swc>.h` and `Rte_Type.h`, generated from that model.
  They give the exact spelling of every `Rte_Write_*`, `Rte_Read_*`,
  `Rte_Call_*` symbol and every enum literal, and the width of every
  implementation type (§5.2).

**What is never read** — in this repository or anywhere else: the module's
`.c` files, the generated OS/RTE `.c` files, the ECUC configuration, the ELF
and the linker map. Three reasons, each sufficient on its own:

1. **It is the thing under test.** A breakpoint line, a variable name or a
   constant taken from the implementation puts the implementation's own
   understanding of the interface into the expected result; a module that
   misread the contract then passes its own test. Engineering writes SWE.5
   cases from the architecture documents for exactly this reason.
2. **It couples the case to one code revision.** A quoted line goes stale with
   the next edit; a symbol named with its module stays findable.
3. **It inverts the authority.** When the code and the architecture disagreed,
   the earlier practice used the code spelling and raised the architecture.
   The architecture is the test basis; the case is written to it, and a
   disagreement is a finding for the bench and the architect, not a reason to
   follow the code.

There is **no degraded mode**: a run never needs the code, so nothing is
flagged for its absence. An engineer who asks for a line number or a variable
name "from the code" is declined in one sentence — the expected result would
then be whatever the code does — and offered the symbol-level step, exactly as
qualification-test-patterns §0 handles the same request.

**Naming a breakpoint.** Every breakpoint is written as *the call `<symbol>` in
module `<Swc>`* (P-01, P-03, P-06, P-07) or *the entry of runnable `<name>` in
module `<Swc>`* (P-05, P-06 server side). `<Swc>` is the ARXML component
short-name (`module_name_mapping.arxml_swc`). `<symbol>` is the spelling the RTE
header defines: the component-prefixed name
(`Rte_Read_<Swc>_R_<port>_<element>`) and, where the header also defines the
short-name macro (`Rte_Read_R_<port>_<element>`), that one — quote the
short-name macro where it exists, since that is the call the module makes, and
record both in Traceability. The tester sets a symbol breakpoint, or locates
the call inside the module at execution time. No `.c` or `.h` file name and no
line number is written anywhere in the case.

**Naming a value.** The edited and observed values are described by **role** —
the argument of `Rte_Write`, the out-parameter of `Rte_Read`, the argument of
`Rte_Call`, the member of one of these for a struct — never by an identifier
from the implementation. The debugger shows the role at the breakpoint; the
role does not change when a developer renames a local.

**Several copies of a generated header.** A project folder often holds more
than one `Rte_*.h` of the same name (a copy under `20_AI/`, the BSW tree, a
generator output folder) with different hashes, because generators stamp
timestamps, copyright years and input-file lists. Compare their **exported
symbol sets**, not their bytes. Identical sets → use the configured copy
(`layout.rte_inc` in this repository by default) and note the others once.
Differing sets → a Phase-1 question naming the symbols that differ. The same
applies to several copies of a component's ARXML.

**The architecture text and its model disagree.** Where the architecture
names a symbol differently from the ARXML and the RTE header, the case must
still name a symbol the debugger can resolve: use the **ARXML/RTE-header**
spelling in the case, cite both spellings in Traceability, and raise the
architecture text as an **architecture defect to be corrected**, addressed to
the architecture owner — not a naming variant normalized quietly in a footnote.
A disagreement in *behaviour* (a period, a direction, a connector) is handled
the other way round: the case is written to the architecture text, the test
basis, and the model is raised (§7, P-05). Observed and ruled on (FUSA_MotDrv,
2026-10-05): architecture `1.4.1.1.3` said `SE01_MotDrv_Log_Stop_CP` where the
RTE header and the ARXML said `Log_End_CP`; engineer ruling, "Architecture
should be corrected."

Do not construct a symbol by analogy (workflow-discipline §4 /
no-fabrication.md). Do not reproduce inconsistent casing seen in the
architecture text — take the spelling from the ARXML and the RTE header, and
note the variant in Open Points.
