# No fabrication — test-generation honesty rule (shared)

> The single most important integrity rule across both DOORS test-generation
> skills. There is no DOORS write access and no test execution available in
> this environment. Never present an unavailable result, or a DOORS write you
> did not make, as if it happened.

## Never

- Invent an `Rte_` symbol, source file name, port, signal name, enum value, DID,
  RID, or NRC name. If it is not in a supplied input, it goes in Open Points.
- Construct a symbol by analogy with one that does exist (`Rte_Write_P_X_X`
  existing does not license writing `Rte_Write_P_Y_Y`).
- Invent a numeric value, threshold, tolerance, or step size. Where a
  requirement states a limit but no parameter backs it with a resolution, put
  the requirement on Open Points rather than inventing a step size.
- Assign a `SW_TST` ID, or any DOORS object ID — `ID` stays empty; DOORS assigns
  it.
- Set `atsState` to `agreed` — that is a post-review value only a human sets.
- Report a test case as executed, passed, failed, or covered by execution — you
  have authored a draft by inspection, nothing has run.
- Write to DOORS. The output is a workbook for an engineer to review and enter
  by hand.
- State a property of the code — a missing `default:` branch, an absent
  counter, an unreachable path, "no caller" — without having read the lines
  that prove it. Cite file and line, or do not make the claim. Such a claim is
  **never** carried into a Phase-1 question, where it would steer the
  engineer's answer: in FUSA_MotDrv Q-06 a wrong "and no default branch" was
  offered as an argument for generating a case, and the switch in question had
  a `default:` on the line after the one cited.
- Copy a misspelling or inconsistent casing forward from a source export
  (near-duplicate environment strings, inconsistent signal-name casing) without
  normalizing to the dominant form and noting the variant in Open Points.
- Skip the Phase-1 analysis gate because the engineer asked to. **Decline and
  explain why** — the gate is what keeps scope, symbol grounding, and the
  count-confirmation honest; generating test cases straight from an
  unconfirmed scope is exactly the failure mode it exists to prevent.

## Always state explicitly

Every generated workbook includes a line stating plainly:

> *"Draft test cases by inspection only — not entered into DOORS, not executed,
> no coverage claimed."*

## Deferral is preferred over a guess

A tracked Open Points row always beats a fabricated value or a silent
assumption — list the unresolved symbol/value/classification and move on;
never guess a plausible-looking value to keep a row "complete."
