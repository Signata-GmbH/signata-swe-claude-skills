# Forbidden constructs (shared hard rules)

> Unconditionally prohibited in this project's application code. In code
> development, never emit these. In code review, flag each occurrence as a
> **Critical** finding regardless of context or apparent safety.

| Construct | Rationale |
|-----------|-----------|
| `float` / `double`; `%f`; `<math.h>`; `sin`/`cos`/`sqrt`; fractional division | Floating point is non-deterministic on this target and violates project rules. Use scaled integers. |
| `goto` | MISRA Rule 15.1; destroys structured control flow. |
| Recursion (direct or mutual) | Stack depth statically unverifiable; MISRA Rule 17.2. |
| Dynamic memory: `malloc`/`calloc`/`realloc`/`free`; VLAs | Heap use forbidden in safety-critical embedded software. |
| Direct peripheral / register writes (MCAL bypass) | All hardware I/O must go through RTE; bypass violates AUTOSAR partitioning. |
| Comma operator for control flow | Hides side-effects; MISRA Rule 12.3. |
| `#include` of files outside the SWC's declared dependencies | Introduces undeclared coupling; makes the build non-reproducible. |
| Magic numbers in algorithmic code | Promote each to a named, module-prefixed macro in the header. |

## Also non-negotiable

- **Editing Agnosar-generated files** under `00_SW/02_App/Common/` — regenerated,
  never hand-edited.
- **Removing/renaming `PROTECTED REGION` markers** or MemMap pragma pairs — user
  code lives strictly between the `Start of user defined code` /
  `End of user defined code` lines.
- **Renaming/reformatting/refactoring code outside the current module's
  deliverable folder** — including peer-module style anchors. Note style issues
  in the review artifact instead of touching the file.

## MISRA-C:2012 essentials to hold (dev self-review + review checks)

No implicit narrowing casts; no signed/unsigned mixing without explicit cast;
every `switch` has `default`; every `if`/`else if` chain ends with `else`; prefer
single return; no unused params; no dead stores; no raw-int-to-enum assignment
(Rule 10.x); no commented-out code (Dir 2.4); no unused entities (Rule 2.5); safe
boolean usage (no `0u` for booleans).
