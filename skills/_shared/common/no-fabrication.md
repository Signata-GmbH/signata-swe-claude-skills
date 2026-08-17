# No fabrication — toolchain honesty rule (shared)

> The single most important integrity rule across all three workflows.
> No compiler, static analyser, or test runner is available in this
> environment. Never present unavailable results as if they were produced.

## Never claim

- That source **compiles** or links.
- That **Polyspace** (Bug Finder / Code Prover) is clean, or fabricate any
  static-analysis finding count.
- That **VectorCAST** tests were built, executed, or passed.
- Any **compiler / MISRA-checker output** you did not actually run.

## Always state explicitly

When a workflow produces code, tests, or a review, include a build/analysis
status line stating plainly:

> *"Syntactic review only — no toolchain run in this environment; no Polyspace
> scan; no VectorCAST execution."*

## Deferral is preferred over a guess

A tracked deferral always beats a fabricated result or a silent assumption:

- In code development, mark unresolved items `/* TODO(SW_Requ-NNN): reason */`
  in the source **and** add a matching row to the Deferred Items table.
- In code review, when a check cannot be evaluated (missing input/document),
  raise it as a `Question` finding — never guess `PASS`.
- In unit testing, list a requirement as not-covered only when the behaviour is
  genuinely not implemented in the UUT (owned by another module/stack), citing
  the absence of the code — not "timing/integration/review."

Best-effort pre-scan review is fine and useful; **claiming verified results that
were never produced is not.**
