# Integration-test (SWE.5) mechanics

> Loaded by `integration-test/SKILL.md` on top of
> [workflow-discipline.md](workflow-discipline.md),
> [no-fabrication.md](no-fabrication.md), and
> [output-format.md](output-format.md).

## AUTOSAR-only guard (v1)

The only validated pattern here is **RTE-debugger-based, white-box**: the
Debug SW is flashed to the target ECU, breakpoints are set on RTE calls,
variables are edited, and the value is observed at the receiving end. This
only makes sense where the module has `Rte_Write`/`Rte_Read` symbols to hang a
breakpoint on.

If the target module's architecture entry and existing test cases show **no**
RTE symbols (no ARXML/`Rte_*.h`, no existing RTE-pattern test cases, no
`Rte_Write`/`Rte_Read` calls in the Signals & Parameters export) — **stop** and
say plainly that this skill only supports RTE-based integration testing in its
current version, rather than inventing a black-box equivalent.

## 1. Scope

Select architecture objects where:

- `aFunctionModule` = the target module
- `aTestability` ∈ `integration_test.testability_filter`
- `aStatusOfAnalysis` ∈ `attributes.status_filter`
- `aRequirementObjectType` = `functional requirement` or `non functional requirement`
- Object text is non-empty

Report the count at each filter step — expect heavy attrition (objects with no
text, or that are information/feature/feature-description rows, are common).

## 2. Resolving the module name (the mapping table)

The architecture export uses `aFunctionModule`. **The integration-test export
has no `aFunctionModule` column** — only `aFeature`. Existing test cases for a
module are located by walking the Object Heading hierarchy: a module-level
heading opens a section, and everything until the next module-level heading
belongs to it.

The two vocabularies rarely match exactly (spelling differences, transposed
words). **Discovery method** (generic — apply it to whatever module you're
given):

1. Search the integration-test-spec export's Object Headings for the target
   module name and close near-matches (transpositions, common misspellings).
2. Cross-check: the `aFeature` mix of the module's architecture objects should
   broadly match the `aFeature` mix of the candidate section. A large mismatch
   means the wrong section was picked — stop and ask rather than proceed on a
   guess.
3. Once resolved, **write the mapping to `ai_test_project.yaml`
   `integration_test.module_name_mapping`** (workflow-discipline §4) so the next
   run — this engineer's or another's — doesn't repeat the search. If the
   module is not on the cached list and cannot be resolved by search, ask.

## 3. Interface inventory

The unit of an integration test case is **the interface**. Build the list from,
in order of preference: (1) existing test-case section headings — each port
heading and each connection heading (`<ModuleA> to <ModuleB>`); (2) the
architecture objects' own text; (3) ARXML/RTE headers, if supplied. For each
interface report its name, sender/receiver modules, `Rte_Write`/`Rte_Read`
symbols, source files, and how many existing test cases it already has.

## 4. Coverage and gap

Split into: already covered, no test cases (your scope), and interfaces found
in the architecture but not resolvable to RTE symbols. Check the standing
obligations: does every module have a `Watch Dog for <module>` group, and does
every inter-module connection have a section.

## 5. Patterns

Pick the pattern that fits; do not invent a new one without saying so.

**P-01 — RTE data flow, sender to receiver.** The dominant pattern.

```
atcPreconditions:
- Reset the ECU
- Wake up the ECU
- Flash the ECU

atcActions:
1. Set the Breakpoint at line <Rte_Write_P_<port>_<element>(...)>; in <sender>.c
2. Edit the variable with <value>(<meaning>).
3. Set the Breakpoint at line <Rte_Read_R_<port>_<element>> in <receiver>.c
4. Read the value.

atcResult:
1. Breakpoint should be hit.
2. result should be updated with <value>(<meaning>).
3. Breakpoint Should be hit.
4. <receiver variable> should be updated to <value>(<meaning>).

atcPostconditions:
- System Shall be stable
- Delete all Breakpoints
```

Generate one test case per value to be exercised on that interface — each
valid enum value, and the boundary values for a ranged signal.

**P-02 — inter-module connection.** Same shape; sender and receiver are
different modules, so the two `.c` files differ. Heading form
`<ModuleA> to <ModuleB>`.

**P-03 — watchdog supervision.** Heading `Watch Dog for <Module>`. Verifies the
supervised entity is registered and reports correctly. One per module.

**P-04 — negative / invalid value.** Same structure as P-01 with an
out-of-range or invalid value and the error reaction as the expected result.
`atsType = negative`. A roughly two-positive-to-one-negative ratio is a sanity
check to report, not a quota to enforce.

**P-05 — OS trace / timing.** Rare. Only generate if the engineer asks for it
explicitly in this run's instructions.

## 6. Attributes specific to this skill

| Attribute | Value |
|---|---|
| `atcPreconditions` | The three-line P-01/P-02 block, verbatim, unless the pattern states otherwise |
| `atcPostconditions` | `- System Shall be stable` / `- Delete all Breakpoints` |
| `atcRemark` | `Debug SW` |
| `aFeature` | Carried from the architecture object |
| `atsTestKind` | `Interface test` |
| `atsTestDesignTechnique` | `InterfaceTesting` |
| `atsType` | `positive` or `negative` |

## 7. Symbols

Every `Rte_` symbol, source file name and enum value must come from a supplied
input. Prefer symbols that already appear in the existing test-spec export —
they show real usage. Do not construct a symbol by analogy (workflow-discipline
§4 / no-fabrication.md). Do not reproduce inconsistent casing seen in the
architecture text — take the spelling from the RTE headers or existing test
cases, and note the variant in Open Points.
