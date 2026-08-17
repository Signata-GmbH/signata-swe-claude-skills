# VectorCAST `.tst` syntax reference (both flavors)

> Loaded by the unit-test skill regardless of `project.type`. The `.tst` grammar
> is identical across AUTOSAR and non-AUTOSAR. What DIFFERS lives in the flavor
> packs and is NOT repeated here: **stub naming** (AUTOSAR SWC-prefixed
> `Rte_*` vs plain-C `l_*`/`motor3ph_*`), **coverage target** (STATEMENT+MCDC vs
> Statement+Branch), and **layout** (env path). Follow the grammar below exactly.

## File header

Preserve an existing file's header. For a fresh file, **record the pinned
revision** (workflow-discipline §2):

```
-- VectorCAST Test Case Script
-- Environment    : <ENV>
-- Unit(s) Under Test: <MODULE>
-- Authored against : <git SHA>   <MODULE>.c blob <hash>
-- Authored by inspection only -- NOT built, NOT run, NO coverage measured.
TEST.SCRIPT_FEATURE:C_DIRECT_ARRAY_INDEXING
TEST.SCRIPT_FEATURE:CPP_CLASS_OBJECT_REVISION
TEST.SCRIPT_FEATURE:MULTIPLE_UUT_SUPPORT
TEST.SCRIPT_FEATURE:REMOVED_CL_PREFIX
TEST.SCRIPT_FEATURE:MIXED_CASE_NAMES
TEST.SCRIPT_FEATURE:STATIC_HEADER_FUNCS_IN_UUTS
TEST.SCRIPT_FEATURE:VCAST_MAIN_NOT_RENAMED
```

## Single test case skeleton

```
TEST.UNIT:<MODULE>
TEST.SUBPROGRAM:<subprogram>
TEST.NEW
TEST.NAME:<subprogram>.<NNN>
TEST.NOTES:
Requirement: <SW_Req(u)-NNN> -- <one-line restatement of verified behaviour>.
Mapping: <input> set to <value>; expect <output/side-effect>.
Writes at <MODULE>.c:<line>; guarded by <guard vars> (see Gate Table).
TEST.END_NOTES:
TEST.VALUE:<input assignments>
TEST.EXPECTED:<expected output assignments>
TEST.END
```

## Value / expected path grammar — `<UNIT>.<scope>.<symbol>[index].<member>:<value>`

- File-scope globals & statics ....... `<MODULE>.<<GLOBAL>>.<symbol>:<value>`
- Subprogram parameters .............. `<MODULE>.<subprogram>.<param>:<value>`
- Subprogram return .................. `<MODULE>.<subprogram>.return:<value>`
- Pointer/array allocation ........... `...<param>:<<malloc N>>`  (allocate **before** indexing)
- Array element / struct member ...... `...<param>[0]:<value>` / `...<param>[0].<field>:<value>`
- Stub return value .................. `uut_prototype_stubs.<function>.return:<value>`
- Stub captured arg / out-data ....... `uut_prototype_stubs.<function>.<param>:<value>`
- Special value tokens ............... `<<MIN>>`, `<<MAX>>`, `<<malloc N>>`, enum literals, `ERR`
- Replace a called fn with a stub .... `TEST.STUB:<MODULE>.<function>`
- Per-case option .................... `TEST.VALUE:<<OPTIONS>>.SHOW_ONLY_DATA_WITH_EXPECTED_RESULTS:TRUE`

> The **stub symbol spelling** is flavor-specific — take it from the flavor pack
> (AUTOSAR: SWC-prefixed `Rte_*`; non-AUTOSAR: the plain C name from the source).
> The **stub parameter name** comes from the *real declaration*, never from a
> wrapper macro's argument name.

## Assertion paths must belong to the subprogram under test

A `TEST.EXPECTED` may only be `<MODULE>.<<GLOBAL>>.*`,
`<MODULE>.<subprogram-under-test>.*`, or `uut_prototype_stubs.*`. **Never**
`<MODULE>.<other-subprogram>.return` — VectorCAST discards it as an *"Unused
Expected Value"* and fails the case even when the logic behaved correctly. To
observe a mode/result another function would return, assert the **backing global**
directly.

## Compound tests — state built across calls

For behaviour that depends on state accumulated over cycles (function-local
`static`s, debounce/timeout counters, edge detection, timers, state machines),
create the individual cases as `TEST.COMPOUND_ONLY`, then chain them. **Reuse
existing cases as slots by name — never author a duplicate with identical values
and expecteds.**

```
TEST.SUBPROGRAM:<<COMPOUND>>
TEST.NEW
TEST.NAME:<<COMPOUND>>.001
TEST.SLOT: "1", "<MODULE>", "<subprogram>", "<iterations>", "<case-name>"
TEST.SLOT: "2", "<MODULE>", "<subprogram>", "<iterations>", "<case-name>"
TEST.END
```

## Settable state

- **File-scope globals/statics** are settable via `<<GLOBAL>>` (given
  `WHITE_BOX:YES` in the env).
- **Function-local statics are NOT settable** — VectorCAST silently ignores
  `TEST.VALUE` on them. Exercise them via a compound test whose first slot primes
  the function through the path that sets the static.
- **`<<malloc N>>` before indexing** — allocate a pointer parameter before
  assigning `[index]`/`.member`.
- **Enum literals, not raw ints**, wherever the parameter/signal is an enum — exact
  spelling from the type definition.
