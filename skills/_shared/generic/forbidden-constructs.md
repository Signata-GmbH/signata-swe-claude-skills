# non-AUTOSAR forbidden constructs & coding rules

> Loaded when `project.type: nonautosar`. The **SIGNATA SW Coding Guideline**
> (`docs.coding_guideline`, §6 naming / §7 rules / §8 HIS metrics) is the
> authoritative standard — read it, do not assume from general knowledge; where it
> differs from a generic rule, it wins. In code review, cite the guideline section
> (e.g. "Guideline §7.3.2"), **not** a MISRA rule number (see
> [review-flavor.md](review-flavor.md)).

## Unconditionally forbidden

| Construct | Rationale |
|-----------|-----------|
| `goto` | Guideline §7.3.1; destroys structured control flow. |
| Recursion (direct or mutual) | Stack depth statically unverifiable. |
| Dynamic memory: `malloc`/`calloc`/`realloc`/`free`; VLAs | Forbidden in this firmware. |
| Direct peripheral / register access from application code | All HW I/O via MCAL/library APIs; app code never touches registers. |
| Comma operator for control flow; side effects in controlling expressions | Hides side effects. |
| New `APP_HAS_*` build flags, or reliance on an **inactive** one | Only flags actually uncommented in `00_SW/97_BUILD/Makefile` are active — verify; a new/inactive flag needs engineer sign-off. |
| Editing generated (`00_SW/02_IF/LINIF/*`), libraries, MCAL, startup, or the LDF | Consumed/generated — never hand-edited. |
| Editing outside the module folder except the two declared integration touch-points (scheduler decl + `main.c` init/run), and only after confirmation | Keeps the change scoped. |

## Floating point — allowed, but LIMITED

Unlike the AUTOSAR flavor (no float at all), the MLX16 project permits `float`
**only where an existing project pattern already uses it** (e.g. compile-time
constant macros like `APP_SPEED_LEVEL*_OUT_RPM`). **Any new runtime floating-point
math is a Phase-1 question, not a default** — prefer scaled integers (state the
scaling, e.g. voltage in 10 mV, angle in 0.1°).

## Coding-guideline highlights (enforced)

- **Braces on every** `if`/`else`/`for`/`while`/`switch` body, even single
  statements; every `switch` has a meaningful `default` leaving the system safe;
  every `if`/`else if` chain ends with `else`.
- No implicit signedness change or silent narrowing — explicit cast on every
  narrowing conversion; `U`/`u` suffix on unsigned literals.
- Variables initialised before use; scope minimised (local → `static` file-scope →
  global, in that order); `volatile` only for ISR-shared / HW data.
- No magic numbers in algorithmic code — promote to a named, module-prefixed macro
  (grep for an existing one first; reuse beats redefinition).
- Module-internal helpers `static`, declared before use; **≤ 5 parameters**;
  **single entry / single exit**.
- **HIS metrics (§8):** cyclomatic v(G) 1–10, nesting depth ≤ 4, ≤ 50 statements,
  ≤ 5 params, GOTO 0.
- Return values of called APIs are checked/handled; errors reported via the
  project error path (`SAPF_EH_*` / `error_logger_LogError` with an
  `E_ENCERRORCODES_*` code), never swallowed.
- No dynamic memory / recursion / VLAs; pointer arithmetic restricted to array
  indexing; NULL-check pointers before dereference; header guard on every header;
  fully-parenthesised function-like macros.
