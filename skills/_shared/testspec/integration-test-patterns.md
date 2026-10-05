# Integration-test (SWE.5) mechanics

> Loaded by `integration-test/SKILL.md` on top of
> [workflow-discipline.md](workflow-discipline.md),
> [no-fabrication.md](no-fabrication.md), and
> [output-format.md](output-format.md).

## 0. AUTOSAR-only guard (v1)

The only validated pattern here is **RTE-debugger-based, white-box**: the
Debug SW is flashed to the target ECU, breakpoints are set on RTE calls,
variables are edited, and the value is observed at the receiving end. This
only makes sense where the module has `Rte_Write`/`Rte_Read`/`Rte_Call`
symbols to hang a breakpoint on.

If the target module shows **no** RTE symbols to work from — no
`Rte_Write`/`Rte_Read`/`Rte_Call` call in its `.c` files in `docs.source_repo`
(§9), no ARXML/`Rte_*.h` entry for it, no `Rte_Write`/`Rte_Read` calls in the
Signals & Parameters export, and (in `extend_existing` mode only, §0.1) no
existing RTE-pattern test case — **stop** and say plainly that this skill only
supports RTE-based integration testing in its current version, rather than
inventing a black-box equivalent. Where the source repo carries its own
`20_AI/ai_project.yaml`, its `project.type: nonautosar` settles it: stop.

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
  literals behind the RTE headers and the code.
- **`from_scratch`** — `docs.integration_test_spec_export` is `N/A`. This is a
  first-class mode, not a degraded one:
  - the coverage baseline is empty — every interface is "no test cases", every
    row is new, every `ID` empty;
  - module and connection heading spellings are **proposed and confirmed** at
    the Phase-1 gate, never invented silently; the proposal is the
    architecture `1.4.1.<n>` spelling (§4);
  - group headings that follow a pattern form (`Watch Dog for <Module>`, the
    task-configuration heading) are marked as derived in Traceability;
  - symbols, breakpoint lines, checkpoint names and enum literals come from
    `docs.rte_type_headers`, the ARXML and `docs.source_repo` only (§9).
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
and members, the text gives the ranges and the `DataType:` lines. A
single-content-column export shows only one of the two, so the export may
arrive as two views joined on `ID`; workflow-discipline §1.3 gates that.

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
  `Data`). Take the RTE symbol from the RTE headers and the code (§9), never
  by concatenating the architecture's names.
- An object's `aFunctionModule` can disagree with the section it sits under
  (a port under `FUSA_MotCtrl` carrying `aFunctionModule = FUSA_ParkLckCtrl`).
  Use the **section** for ownership and the **attribute** for the scope filter,
  and report every disagreement as an Open Point rather than silently picking
  one.

### 1.2 Scope filter

Two different sets come out of this step, and they must not be confused: the
objects test cases are **authored from** (each gets a section, a heading row
and its cases), and the objects that are only **read** to ground those cases.

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
text, or that are information/feature/feature-description rows, are common).

**Section ownership beats `aFunctionModule` for nested service objects.** Some
ports sit under a module's own section but are owned by a *service* module —
watchdog supervision checkpoints are the standing case (`aFunctionModule =
WdgM` under `1.4.1.<n>.<m>`), and `Os`, `Dem`, `NvM` and `Dcm` behave the same
way where a project uses them. An object like this belongs to the run **when
its section number is a child of the target module's own section**, because
that is the only module whose code calls it.

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

- `P_<Element>` → **write (provide) side** — `Rte_Write_P_<port>_<element>(...)`
  in the writing module's `.c`.
- `R_<Element>` → **read (require) side** — `Rte_Read_R_<port>_<element>(...)`
  in the reading module's `.c`.
- A checkpoint name (`SE01_<Module>_Log_Start_CP`) → watchdog supervision (P-03).
- A bare API name (`Ftm_Pwm_Ip_...`, `Aec_Ip_Spi...`) or a port whose text reads
  *"This client port is used…"* → **client/server**, `Rte_Call_...` (P-06), not
  a data flow.

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
4. Casing drifts (`Mot_Mov_Data_st` vs `Mot_Mov_Data_St`) — match
   case-insensitively, but take the spelling you emit from the RTE header and
   the code (§9), and note the variant in Open Points.
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
  as the far end — a P-01 case must name the `Rte_Write` line in the writer's
  `.c` and the `Rte_Read` line in the reader's — but it gets no section, no
  heading row, and no case sourced from its own objects.
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

| Interface | Data type | Writer module / `.c` | `Rte_Write` line | Reader module / `.c` | `Rte_Read` line | Far ends of this target port | Projected cases | Existing cases (`extend_existing` only) |
|---|---|---|---|---|---|---|---|---|

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

## 4. Resolving the module name (the mapping table)

One module can carry **three** spellings, and they are all in play:

| Where | Example |
|---|---|
| architecture `1.4.1.<n>` section heading | `FUSA_CDD_MotDrv` |
| `aFunctionModule` attribute (the skill's argument) | `FUSA_MotDrv` |
| integration-test-spec section heading | `Mot_Drv` |

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
3. Once resolved, **write all three spellings to `ai_test_project.yaml`
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
heading; (3) ARXML/RTE headers and the `.c` call sites in `docs.source_repo`.
For each interface report its name, writer/reader modules, `Rte_*` symbols,
`.c` files, data type, and — in `extend_existing` mode — how many existing test
cases it already has.

Then split into: already covered, no test cases (your scope), and interfaces
found in the architecture but not resolvable to RTE symbols. Check the standing
obligations: does every module authored from have a `Watch Dog for <module>`
group, a task-configuration group, and a section for every connection.

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
| Enum | **one per literal**, all `positive`; plus one out-of-range `negative` case if the type documents an invalid/reserved value |
| Struct | the **5-case set per member**, member by member (a 5-member struct → 25 cases) |
| Boolean | both values, `positive`; the architecture text usually states the meaning (`0 - Enabled` / `1 - Disabled`) — carry it into the case |

Rules:

The in-range triple and the out-of-range pair come from **different sources**.
Do not derive all five from one range.

- **Min / Mid / Max — the documented `Range:`** in the UserDefinedTypes entry
  when it has one; otherwise the implementation type's limits (`uint8` → 0/255).
  **Mid** is the arithmetic midpoint of whichever range you used. Say which of
  the two you used, per interface, in the Traceability sheet — the existing spec
  is inconsistent about this and the engineer needs to see the choice, not
  discover it.
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

## 6. `aTestCriteria` → pattern

| `aTestCriteria` says (observed wordings) | Pattern |
|---|---|
| "Check in RTE whether the RTE variables is getting updated …" | **P-01** / **P-02** |
| "Interface Test with Min, Mid, MAx and border values." | **P-01** with the full 5-value set (§5.2) |
| "Check for the runnables in the RTE task table … periodicity of periodic runnable" | **P-05** |
| "Check for the alarm configuration for all the TASK …" | **P-05** |
| "These are the client ports … check for the value in the respective server function" | **P-06** |
| "Execute the DID and check for the server function is hit" | **P-07** |
| "review" / "This can only be reviewed" / "Review of SW Architecture" / "The flow needs to be verified by the testing team" / "The Sequence to be checked by the Test Team" | **P-08** — no debugger test case |
| "Can be checked by XCP only" / "using the XCP variable" | **P-08**, noting XCP as the required means |

Typos and case vary between objects ("wehther", "CHnage", "ini runnable") —
match on meaning, and never copy a misspelling into a generated case.

**P-08 is never applied silently.** A `review`-type `aTestCriteria` suppresses
a whole object, so before emitting P-08, check whether the object nevertheless
has a concrete, observable symbol in a supplied input — an `Rte_Call_*`,
`Rte_Write_*` or `Rte_Read_*` in the code, or a driver API the module actually
calls. If it does, the criterion and the code disagree, and that is a
**Phase-1 question**, not a decision to take alone. The default proposal in
that question is **author the case**: `aTestCriteria` is often older than the
code. An object that maps to P-08 *and* has no resolvable symbol needs no
question — Open Points is enough.

Observed failure (FUSA_MotDrv, 2026-10-05): `Ftm_Pwm_Ip_FastUpdatePwmDuty`
(6227), `Ftm_Pwm_Ip_UnMaskOutputChannels` (6230) and the two WdgM checkpoint
ports (5847 / 5904) were all suppressed to heading rows on `aTestCriteria =
"review"` / `"1. Review the flow"`. All four are called directly from
`CDD_MotDrv.c` — the symbols were in hand and nothing was unresolved. The QA
engineer rejected all three heading rows at validation with "TestCases need to
Design for this interfaces".

## 7. Patterns

Pick the pattern that fits; do not invent a new one without saying so.

**P-01 — RTE data flow, writer to reader.** The dominant pattern. Both
breakpoints are named, and each names its own module's file.

```
Object Heading (group):  P_<Element>            (or R_<Element>)
Object Text (case):      Test case to verify the <Element> for <Min|Mid|Max|Min-1|Max+1> Value.

atcPreconditions:
- Reset the ECU
- Wake up the ECU
- Flash the ECU

atcActions:
1. Set the Breakpoint at line <the Rte_Write call, verbatim from <writer>.c> in <writer>.c
2. Edit the variable <writer-side variable> with <value>.
3. Set the Breakpoint at line <the Rte_Read call, verbatim from <reader>.c> in <reader>.c
4. Verify the value

atcResult:
1. Breakpoint should be hit.
2. <writer-side variable> should be update to <displayed-at-writer> value.
3. Breakpoint Should be hit.
4. <reader-side variable> should be update to <displayed-at-reader> value.

atcPostconditions:
- System Shall be stable
- Delete all Breakpoints
```

Both breakpoint lines are quoted **verbatim from the `.c` file** at the pinned
source revision, argument expression included — e.g.
`Rte_Write_P_<port>_<element>(<arg>);` and
`if( E_OK == Rte_Read_R_<port>_<element>( &<reader-side variable> ) )` are the
*shapes* to look for, not text to fill in (§9). The writer-side and reader-side
variables are the ones those lines name: the argument of `Rte_Write`, the
out-parameter of `Rte_Read`. The line **number** goes in Traceability with the
source revision, not into `atcActions` — it goes stale with the next edit to
the file, while the quoted line stays findable.

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
atcActions:   1. Set the Breakpoint at line
              (void)Rte_Call_ApplocalSupervision_WdgM_SE<n>_<checkpoint>_CheckpointReached();
atcResult:    1. Breakpoint should hit and Watch Dog should Reset.
```

Checkpoint names come from the RTE headers, and the breakpoint line is the
`Rte_Call_…_CheckpointReached` call quoted from the module's `.c` (§9) — never
constructed from the module name.

**P-04 — negative / boundary value.** The Min-1 and Max+1 members of the
5-value set, and any documented invalid enum value. `atsType = negative`. The
positive/negative ratio is a sanity check to report, not a quota to enforce.

**P-05 — task configuration & runnable timing.** From the `1.3.1.<n>.1.<m>`
non-functional objects. Two shapes, grouped under a task-configuration section
heading per module:

```
Object Text:  Test case to verify the Initialization of <Module>
atcActions:   1. Set the Breakpoint at line <Module>_Init_counter++;
              2. Add the Variable in Watch window and Verify.
atcResult:    1. Breakpoint should be hit
              2. <Module> counter should be update to 1.

Object Text:  Testcase to verify the Runnable time for <Module> for every <n>msec.
atcActions:   1. Set the Breakpoint at line <Module>_Cyclic_<n>msec_counter++;
              2. Add the Variable in Watch window and Verify.
atcResult:    1. Breakpoint should be hit
              2. <Module> counter should be update every <n>ms.
```

`<Module>_Init_counter` and `<Module>_Cyclic_<n>msec_counter` above are the
**shape of the observation, not symbol names.** They are the symbols of one
legacy stub and exist in no current module — treating them as real is a
fabrication (no-fabrication.md). Resolve the actual observable from the code.

The counter symbol and the period both come from an input — the period from the
architecture object's own text ("This runnable should be called from 2msec
Task_FUSA_2ms"), the counter from the code/RTE or an existing case. Existing
cases in the spec contain period mismatches between action and result; do not
copy one, and flag any you relied on. A counter *name* that contradicts the
architecture period (a `..._1msec_counter` inside a 2 ms runnable) never
overrides the architecture text — use the architecture period and raise the
mismatch in Open Points.

If the init runnable sets **no** counter or flag at all, the case is "set the
breakpoint inside the Init runnable, restart the debugger, the breakpoint shall
be hit" — this is the engineer's stated convention (FUSA_MotDrv Q-19,
2026-09-24), not a deviation from P-05 needing a question of its own.

**P-06 — client/server port.** `Rte_Call_<port>_<operation>` at the caller, the
server runnable entered at the other end. Breakpoint at the call, breakpoint in
the server function, verify the argument passed.

**P-07 — diagnostic DID / routine.** Only for the diagnostic modules
(`DiagReadData`, `DiagWriteData`, `DiagRoutineCtrl`) and only when
`aTestCriteria` names the DID approach:

```
atcActions:  1. Send DiagRequest DID <XX XX> from Diagnostic console.
             2. Set the Breakpoint at line <server function signature>
atcResult:   1. DID Should be Positive Response <SID+0x40> <XX XX> XX XX XX.
             2. Breakpoint should be hit.
```

The DID comes from the DiagSpec and the server-function line from the `.c`
(§9) — or, in `extend_existing` mode, from an existing case. Note that SWE.6 covers diagnostics far more thoroughly — a diagnostic
interface here is tested only as an interface.

**P-08 — not testable by the debugger → no test case.** Where `aTestCriteria`
asks for a review, a sequence walkthrough by the test team, or XCP-only
observation, emit **no** concrete case. Record the object in Open Points with
the criterion verbatim and the reason. If the project's convention is to carry
such objects as heading rows with `no testcase` attributes, emit the heading row
only (output-format.md).

**P-09 — OS trace / timing measurement.** Rare. Only generate if the engineer
asks for it explicitly in this run's instructions.

## 8. Attributes specific to this skill

| Attribute | Value |
|---|---|
| `atcPreconditions` | The three-line P-01 block, verbatim, unless the pattern states otherwise |
| `atcPostconditions` | `- System Shall be stable` / `- Delete all Breakpoints` |
| `atcRemark` | `Debug SW` |
| `aFeature` | Carried from the architecture object. On a mirrored case, carry the feature of the **object the case traces to**, not the section it sits under |
| `atsTestKind` | `Interface test` |
| `atsTestDesignTechnique` | `InterfaceTesting` |
| `atsType` | `positive` or `negative` (§5.2) |

## 9. Symbols and breakpoint lines

Every `Rte_` symbol, source file name, struct member and enum value must come
from a supplied input, and two different things come from two different
sources:

- **Symbols** — `Rte_` names, type names, struct members, enum literals,
  checkpoint names — come from the RTE headers (`docs.rte_type_headers`, or the
  source repo's own `layout.rte_inc`) and the ARXML.
- **Breakpoint lines and observed variables** come from the module's **`.c`
  files** in `docs.source_repo`. A header carries no executable line and no
  observable variable, so a case whose `atcActions` names a `.h` file is wrong.
  Quote the `.c` line verbatim, argument expression included, and record the
  file, the line number and the source revision in Traceability.

The two spellings differ legitimately: code usually calls the RTE's short-name
macro (`Rte_Read_R_<port>_<element>`), which the header defines over the
component-prefixed name (`Rte_Read_<Swc>_R_<port>_<element>`). Quote the `.c`
spelling in `atcActions`; the header is what confirms the symbol exists.

If the call appears on **several** lines of the `.c`, list them and ask which
one the case breaks on — never pick the first. In `extend_existing` mode an
existing case may show which line a project usually breaks on; it never
replaces reading the `.c` at the pinned revision.

Do not construct a symbol by analogy (workflow-discipline §4 /
no-fabrication.md). Do not reproduce inconsistent casing seen in the
architecture text — take the spelling from the RTE headers and the code, and
note the variant in Open Points.

**Without the source repo — a degraded run.** `docs.source_repo` is mandatory
for this skill; only a recorded engineer decision waives it (workflow-discipline
§1.1), and a waived run is **degraded** — say so on the first line of the run
summary. In a degraded run every breakpoint names the RTE symbol only, marked as
a placeholder (`<line in <file>.c — not resolved: no source repo>`), the P-05
observables stay unresolved, and every such case is flagged as not executable as
written (output-format.md, validity columns) with an Open Point. Never derive a
`.c` file name from an ARXML component name and present it as known.

**A different identifier is not a casing variant.** Where the architecture
names a symbol differently from the code, and the code, the RTE headers and the
ARXML all agree against it, use the **code** spelling in the test case and
raise the architecture as the outlier — an **architecture defect to be
corrected**, addressed to the architecture owner, not a naming variant
normalized quietly in a footnote. Observed and ruled on (FUSA_MotDrv,
2026-10-05): architecture `1.4.1.1.3` says `SE01_MotDrv_Log_Stop_CP` where the
code, the RTE header and the ARXML all say `Log_End_CP`; engineer ruling,
"Architecture should be corrected."
