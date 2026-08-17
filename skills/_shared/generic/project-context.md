# non-AUTOSAR flavor context (read once, do not re-derive)

> Loaded by all three skills when `project.type: nonautosar`. Project-specific
> facts (project name, compiler, target, layout roots) are read from
> `20_AI/ai_project.yaml`, not asserted here. This file holds the non-AUTOSAR
> *conventions* true for a project of this shape (e.g. Small_Actuator / MLX81332).

## Project identity — read from config, never hardcode

- **Project:** `project.name` — a **non-AUTOSAR** firmware project. **There is no
  RTE.** Never invent `Rte_Read_*/Write_*/Call_*`, `Dem_*`, `NvM_*`,
  `Std_ReturnType`, or SWC-prefixed symbols — they do not exist here.
- **Target / compiler:** `toolchain.target` / `toolchain.compiler` (e.g.
  Melexis MLX81332, 16-bit MLX core, `mlx16-gcc`). No toolchain runs here (see
  [../common/no-fabrication.md](../common/no-fabrication.md)).
- **Unit-test coverage:** `coverage.unit_test` — normally **Statement+Branch**
  (not MC/DC).

## The interface model — LIN + `_cfg.h` macros

- **Comms:** LIN 2.2 slave. Signals are defined in the LDF (`layout.lin_ldf`);
  the **only** LIN I/O paths are the generated accessors under `layout.linif`:
  `l_u8_rd_<sig>()` / `l_u16_rd_<sig>()`, `l_u8_wr_<sig>(v)`, `l_flg_tst_f_<frame>()`,
  `l_flg_clr_f_<frame>()`. The LDF + these accessors are the authority for names,
  widths, scaling, and enum encodings.
- **`_cfg.h` indirection (per module — check, don't assume):** many modules wrap
  every external touch-point (LIN accessor, sibling API, motor/library call) in a
  `<Module>_IF_<Purpose>()` macro in `<Module>_cfg.h`; the `.c` calls only those
  macros. Some modules (e.g. `SAPF_EH`, `SAPF_DiagWrap`) call externals directly —
  derive the boundary per module, assume neither shape.
- **Motor:** 3-phase stepper, driven **only** via `motor3ph_stepper_*` /
  `motor3ph_*` library APIs — never PWM/ADC/IO registers directly.
- **Consumed APIs:** MCAL under `00_SW/04_MCAL/`, libraries under
  `00_SW/03_LIBRARIES/` (swtimer, filters, mathlib…), sibling modules under
  `layout.app_root`. Read from their headers, never re-invent signatures.

## Execution model

- Application code runs in the **main-loop `SAPF_<Module>_Run()`** context (10 ms
  cadence) via the scheduler (`00_SW/05_OS/Scheduler/`). Do not add ISRs or hook
  interrupt vectors; keep `*_Run()` non-blocking (use `swtimer` for timing/debounce).

## Coding conventions (SIGNATA guideline is authoritative)

- Functions `SAPF_<Module>_<Action>()`; interface macros `<Module>_IF_<Purpose>()`;
  module globals `<Module>_<Name>_g_<t>` with Hungarian suffixes
  (`_g_u8`, `_g_u16`, `_g_s16`, `_g_b`, `_g_e`); macros `UPPER_SNAKE` with prefix;
  enum types `_en` with `SAPF_*` enumerators.
- Module pattern (P3): Signata copyright block, SRC-MODULE header, Change/Revision
  History, `static` prototypes before definitions — mirror `SAPF_Mode.c`.
- Arithmetic: MLX16 has **no FPU** — prefer scaled integers (state the scaling).
  See [forbidden-constructs.md](forbidden-constructs.md) for the (limited) float rule.

## Symbol grounding (non-AUTOSAR sources)

Every non-parameter identifier is copied **verbatim, at the pinned revision**, from
only: (1) the module's own `<MODULE>.c`/`.h`/`_cfg.h`; (2) the declaring header of a
called external (`layout.linif` `lin_signals.h`, `00_SW/03_LIBRARIES/**`,
`00_SW/04_MCAL/**`, `00_SW/05_OS/**`, a sibling `.h`); (3) the input documents
(Requirements, LDF, SwDD/AD exports). **Never** from `10_Test/**` stub bodies,
`20_AI/Analysis/**`, `80_RELEASE/**`, build/Polyspace artifacts, or another branch.
A stub's **parameter name** comes from the *real declaration*, never from a
hand-written stub body or a `_cfg.h` macro's argument name.
