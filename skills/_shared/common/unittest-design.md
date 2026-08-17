# Unit-test design rules & deliverables (both flavors)

> Loaded by the unit-test skill. These rules are flavor-agnostic; the flavor
> supplies only the **coverage target** (`coverage.unit_test`) and the **stub
> naming** (AUTOSAR SWC-prefixed `Rte_*` vs plain-C `l_*`/`motor3ph_*`). Use with
> [vectorcast-syntax.md](vectorcast-syntax.md) (grammar) and
> [workflow-discipline.md](workflow-discipline.md) (§2 revision pinning, §6 Gate
> Table, §8 traceability).

## Test-design rules

- **Requirement-driven cases first.** Author ≥1 case per in-scope requirement,
  realising its procedure and asserting its **Expected Result** via
  `TEST.EXPECTED`. Use meaningful, traceable values — named enum literals, real
  macro values, boundary values from the stated ranges — not arbitrary
  `<<MIN>>`/`<<MAX>>` where a concrete condition is specified.
- **Assert a real effect — never an input, never nothing.** Every non
  `COVERAGE-ONLY` case has ≥1 `TEST.EXPECTED`, and each asserts an output the
  subprogram **actually produces** on the exercised path: its return, an out-param,
  a stub-captured argument, or a file-scope global it **writes**. Never assert a
  global it only reads or leaves unchanged (a tautology). `COVERAGE-ONLY` relaxes
  requirement-tracing, **not** this rule.
- **Assert the value's source, not the branch selector** (per Gate Table §6): set
  the global that supplies the written value, not merely the one in the condition.
- **Satisfy every gate on the asserted path.** Trace inputs → each guard/helper →
  the writing statement; confirm every conjunct holds; cite the `file:line` and
  guard variables in `TEST.NOTES`.
- **Set every input that gates the path — never rely on defaults.** An unset stub
  returns 0, which is often a meaningful enum; if flipping an input could change
  which branch runs, set it explicitly.
- **Boundary discipline.** For each range test at least below-min, min, in-range,
  max, above-max as the requirement implies. Respect signal scaling; watch
  signed/unsigned width changes at the call boundary.
- **Structural coverage is a hard goal** (to `coverage.unit_test`): after the
  requirement-driven set, enumerate remaining uncovered decisions per subprogram
  and **author cases to close them** — don't just flag gaps. One case per
  **distinct reachable** `switch` body (not per label). For a compound decision,
  author the MC/DC independence pair (AUTOSAR STATEMENT+MCDC). A `#ifdef` arm whose
  build flag is inactive is compiled out — not a gap. Never fabricate opaque
  path-only cases or guess basis-path `X of N` indices; never state a coverage %.
- **Cover the target metric, then stop.** No cross-product of independent decisions
  and no re-covering an already-covered outcome via a different route. Exception:
  a distinct requirement or a safety-relevant path no other case exercises **and**
  that this case actually asserts.
- **Sequential / stateful logic → compound tests** (function-local statics,
  debounce/timeout counters, edge detection, state machines). Drive the subprogram
  over real cycles; for function-local statics it is the only way. **Reuse existing
  cases as compound slots by name — never author a duplicate** (identical
  `TEST.VALUE` **and** `TEST.EXPECTED`).
- **Traceability on every case.** `TEST.NOTES` records the requirement ID(s) **or**
  a `COVERAGE-ONLY` label naming the exact decision, a one-line behaviour
  restatement, the input→value rationale, and the `file:line` of the writing
  statement + its guard variables. Cite a `SW_Requ`/`SW_Req` ID **only** when the
  case asserts that requirement's Expected Result.

## Symbol-grounding self-check (before emitting the `.tst`)

For every non-parameter identifier scripted (file-scope globals/statics, macros,
enum literals, stub function + parameter names), confirm the **exact string**
appears in the whitelisted sources (flavor `project-context.md` grounding section).
Report the result and **list any symbol you could not confirm — then stop** rather
than guess.

## Deliverables (this run authors `.tst` only — no build/run)

1. **The `.tst`** at the env path (`layout.vcast_env/<ENV>/<ENV>.tst`) — fresh with
   the §-syntax header (incl. pinned SHA + blob hash) or appended with
   non-colliding names. Every case carries a `TEST.NOTES` block.
2. **Traceability table:** requirement ID (or SwDD page) → case name(s) →
   subprogram, including any in-scope requirement not covered and why.
3. **Coverage-closure report:** list **every subprogram** enumerated in analysis
   with its case count (a zero is visible + justified, never silently skipped);
   then per subprogram the decisions covered and the closing case(s), and any
   decision still uncovered with its justification (unreachable at unit level, or
   compiled out by a build flag). **No coverage percentage.**
4. **Notes / assumptions:** pinned SHA + blob hashes; which signal/scaling source
   used (doc vs code); the symbol-grounding self-check result (with any
   unconfirmed symbols, which block the run); any new stubs **proposed** (propose,
   do not add); ambiguities resolved by reading code; and any **code findings**
   (unreachable branches, selector/value mismatches, header/source discrepancies).
