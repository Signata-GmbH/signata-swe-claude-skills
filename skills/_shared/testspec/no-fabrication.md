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
- Invent a test procedure. Behaviour no supplied input describes — a state
  machine, an initialisation sequence, a mode transition, a wake-up or
  shut-down order — is a Phase-1 question or an Open Point, never a procedure
  written from what such systems usually do. Where a requirement cites a
  specification that describes it, ask for that document
  (qualification-test-patterns.md §3.1).
- Invent the name of a bench means — a CANoe panel, a panel control, a CAPL
  function, a HIL channel. It comes from the test environment description or
  from the engineer's answer in the Phase-1 catalogue.
- Assign a `SW_TST` ID, or any DOORS object ID — `ID` stays empty; DOORS assigns
  it.
- Set `atsState` to `agreed` — that is a post-review value only a human sets.
- Write `Yes` in a validity column (below) — nothing was built, flashed or
  executed, so nothing is known to work.
- Change a validity value or reason QA entered — on a re-run, QA's `Yes`, `No`
  and reasons stay as QA left them (workflow-discipline.md §8).
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

## The validity column (`isValid`, when configured)

Where the config declares the validity columns (output-format.md, reference
columns), `isValid` says whether a case can be executed **as written** — and
authoring by inspection can only ever establish that it **cannot**:

- **`No`** — only where you *know* the case cannot run as written: a symbol,
  breakpoint line, observed variable or expected value is still a placeholder.
  `Reason for Invalid` names the missing item, the file that would resolve it,
  and the Open Point number.
- **blank** — every other case. That is the reviewer's verdict to give.
- **`Yes`** — **never**.

State the number of `No` rows in the run summary, and say that blank means
"for the reviewer", not "not checked": a fully grounded run has an all-blank
column, which otherwise reads as a broken feature. Read across runs, the count
is a grounding score — a run with unresolved far ends marks most of its cases
`No`; a run with every symbol and line resolved marks none.

## Deferral is preferred over a guess

A tracked Open Points row always beats a fabricated value or a silent
assumption — list the unresolved symbol/value/classification and move on;
never guess a plausible-looking value to keep a row "complete."
