# AUTOSAR flavor context (read once, do not re-derive)

> Loaded by all three skills **when `project.type: autosar`**. Project-specific
> facts (project name, compiler, target, ASIL, source-tree roots) are NOT
> asserted here — they are read from `20_AI/ai_project.yaml`. This file holds the
> AUTOSAR-flavor *conventions* that are true for any AUTOSAR project of this shape.

## Project identity — read from config, never hardcode

Resolve these from `20_AI/ai_project.yaml` (and the module manifest) at run time:

- **Project / standard:** `project.name` — an AUTOSAR Classic project.
- **Safety:** module ASIL from the manifest `module.asil` (falls back to
  `safety.default_asil`); may be a decomposed form e.g. `ASIL-B(D)`.
- **Target / compiler:** `toolchain.target` / `toolchain.compiler`. This is where
  the GreenHills-vs-TASKING difference is resolved — **per project, in config.**
  Whatever it is, **no toolchain runs in this environment** (see
  [../common/no-fabrication.md](../common/no-fabrication.md)).
- **Unit-test coverage:** `coverage.unit_test` — for AUTOSAR projects this is
  normally **STATEMENT+MCDC**.

## Source & test layout (roots from `layout.*`; substitute `<MODULE>`/`<ENV>`)

- Application source: `<layout.app_root>/<MODULE>/inc/<MODULE>.h`,
  `.../src/<MODULE>.c` (some modules also have `<layout.app_root>/Common/...`).
- **Agnosar-generated stub** (interface contract, DO NOT edit):
  `<layout.app_root>/Common/src/<MODULE>.c` — mirror its runnable prototypes,
  MemMap pragma pairs, and `PROTECTED REGION` markers verbatim.
- RTE interface: `<layout.rte_inc>/Rte_<MODULE>.h` and `Rte_<MODULE>_Type.h`.
- VectorCAST env: `<layout.vcast_env>/<ENV>/` (`<ENV>.env`, `.cfg`, `.mfg`, `.tst`).

## Coding conventions

- **No floating point.** Scaled integers only (e.g. angles in 0.1° units as
  `uint16`: `16.3° → 163`). No `float`/`double`/`%f`/`sin`/`cos`/fractional
  division. (Enforced as a hard rule — see [forbidden-constructs.md](forbidden-constructs.md).)
- **Naming:** module-prefixed macros (`<MODULE_UPPER>_*`); variables use
  Hungarian suffixes (`_u8`, `_u16`, `_u08`, `_b`, `_e`, `_st`, `_en`).
- **I/O only through RTE** APIs listed in the stub's runnable header. Never
  invent `Rte_*` calls; never touch peripherals directly.
- **RTE stub names need the SWC prefix** in VectorCAST `.tst` and when reasoning
  about calls: `Rte_Read_<MODULE>_R_...`, not the bare `Rte_Read_R_...` macro alias.
- **MemMap:** module-level variables wrapped in `Appl_MemMap.h`
  `START_SEC`/`STOP_SEC` pairs (`CLEARED_UNSPECIFIED` for zero-init,
  `INIT_UNSPECIFIED` for value-init). Calibration/tunables in `NO_INIT`/`CLEARED`
  are initialised inside the module's `Init` runnable, not at declaration.
- **Traceability:** every non-trivial branch/assignment carries a
  `/* SW_Requ-NNN: short rationale */` comment using the `ID` from the
  requirements workbook.

## Symbol grounding (identifiers must be real)

Every identifier you write that is **not** a subprogram parameter — file-scope
globals/statics, `extern` structs, callbacks, RTE stubs — must be copied verbatim
from one of: (1) the module's own `<MODULE>.c`/`.h` (plus `Common/...` only if the
module references it), (2) the module's `Rte_<MODULE>.h`/`_Type.h`, or (3) the
manifest's input documents. **Do not** source names from `00_SW/06_Test/**`,
`Polyspace/**`, `*.drs`, generated-config trees, `ECU_Extract/**`, or another
module's BSW — those carry stale or foreign names that look valid but don't match
the current UUT.
