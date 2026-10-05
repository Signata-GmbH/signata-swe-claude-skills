# vTestStudio automation scripts — plan (parked)

**Status:** parked, not started. Recorded 2026-10-06.
**Pick this up** when `integration-test` (SWE.5) and `qualification-test`
(SWE.6) are extended to generate vTestStudio automation. Until then, v1
produces the Excel workbook only (README decision 13).

---

## 1. Goal

Generate vTestStudio automation from the test cases the two skills already
write, so engineers stop translating reviewed test cases into scripts by hand:

- **SWE.5** — debugger-driven cases: set breakpoints, edit variables, check
  watched values.
- **SWE.6** — black-box cases: bus signals, diagnostic requests, XCP
  measurements, I/O.

## 2. What v1 already puts in place

| Already in v1 | Why it matters for scripts |
|---|---|
| The skills run in the SWE.3 Git repository (README decision 15) | Generated scripts get a versioned master copy — the vTestStudio folder, which is not under Git, cannot provide one |
| `vteststudio:` config block — project path, `write_access: false` | Where to read the project from now, and write into later |
| SWE.5 cases quote the exact `.c` line and variable; Traceability holds file, line and revision | A script needs the exact breakpoint location, not a paraphrase |
| Observed variables checked against the debug build (`docs.debug_build`) | A script that watches a variable the build lacks fails on its first step |
| P-05 task and period checked against the OS configuration (`docs.os_config`) | Timing checks in a script need the configured period, not only the intended one |
| Test environment description and the bench check (`docs.test_environment`) | What the bench can stimulate and observe |
| Communication database for SWE.6 (`docs.comm_database`) | Exact signal and message names, encoding, cycle times, timeouts |
| `isValid = No` and Open Points on cases that cannot run as written | No script is generated for a case already known not to run |

## 3. Ground rules already decided

1. **Master copy in the repository.** Scripts are written first to
   `20_AI/vTestStudio/<module or feature>/` in the SWE.3 repository.
2. **The vTestStudio project is read-only by default.** Copying scripts into
   it needs `vteststudio.write_access: true` **and** a confirmation on each
   run. Every file that would be replaced is backed up first, and the hashes of
   what was written and what was replaced go into the run ledger.
3. **Never overwrite manual edits silently.** A script in the project that
   differs from the last generated version was edited by hand: show the
   difference and ask — the same rule as for an edited workbook
   (testspec `workflow-discipline.md` §8).
4. **No fabrication carries over.** A signal, system variable, channel or
   debugger command not found in a supplied input is an Open Point, never a
   guessed name. Generated scripts are drafts by inspection; the skill never
   claims they ran.

## 4. Work items

### 4.1 Script generation (both skills)

- Map each pattern to the vTestStudio construct the team uses: SWE.5's P-01,
  P-03, P-05 and P-06 to debugger automation; SWE.6 cases to test tables with
  signal stimulation and checks, and diagnostic requests; SWE.6 logical
  (parameterised) test cases to vTestStudio parameters or loops, not copies.
- Learn the target format from the team's real projects, not from general
  knowledge. The original analysis (STATUS.md, 2026-09-15) found `.vtsoproj`
  projects, `.vtt` XML test tables and Lauterbach-debugger automation in the
  SWE.5/SWE.6 folders — use those as the reference.
- Generate from the **reviewed** test cases, not from a fresh analysis — see
  open question 3.

### 4.2 Test environment becomes mandatory and exact (both skills)

- v1 accepts a free-form description of the bench. A script needs exact names:
  system variables, signals, I/O channels, the debugger connection. Read them
  from the vTestStudio project and its CANoe configuration and databases
  (read-only) rather than from a separate document.
- `docs.test_environment` changes from "offered" to mandatory for any run that
  generates scripts.

### 4.3 Operating modes and state machines (SWE.6)

- Today a precondition such as "terminal 15 on, bus awake" is text. A script
  must reach that state: supply and terminal control, network-management
  wake-up, waiting until the state is reached.
- **Input needed:** the project's power-mode and network-management
  definitions — states, transitions, and the signals or channels that drive
  them. Which document holds them is to be confirmed with the team.
- **Output:** a small library of reusable preconditions, one per state, that
  each script references instead of repeating the steps.

### 4.4 Error handling and fault injection (both skills)

- **Input needed:** the error-handling / fault concept — which faults are
  detected, debounce times, reactions, DTCs (SWE.6) — and the safety
  mechanisms to provoke, such as the watchdog and E2E protection (SWE.5).
- What can be injected depends on the bench: HIL fault insertion, bus
  manipulation (wrong CRC or alive counter, missing messages), debugger
  variable overrides. Design this together with 4.2.
- Which ASIL requires fault-injection tests is a project decision (see §7), not
  the skill's to choose.

### 4.5 Timing and resource budgets (SWE.5)

- **Input needed:** runnable execution times, CPU load, stack and RAM budgets.
- **Measurement means to confirm:** OS trace (where the code carries trace
  hooks), CANoe timing, debugger runtime measurement. Today the OS-trace pattern
  P-09 is generated only when explicitly requested.

### 4.6 Re-runs and traceability for scripts

- A re-run updates scripts in place the way it updates the workbook — new,
  changed, removed, unchanged — keyed by test case.
- Link each script to its test case. Before DOORS import a case has no
  `SW_TST` ID, so key it by its Traceability row; after import, by the DOORS
  ID — see open question 4.

## 5. Open questions for the team

1. Which vTestStudio version is in use, and which artefact types (test tables,
   test sequences, CAPL or C# functions)? Provide one reference project per
   level.
2. How is the debugger driven from vTestStudio today (Lauterbach TRACE32, and
   through which interface)?
3. Should scripts be generated from the engineer-validated workbook, or after
   DOORS import, from the DOORS export?
4. Should scripts carry DOORS IDs — and therefore be generated only after
   import?
5. Will the vTestStudio project come under version control (Git or other)? If
   not, the repository master copy (§3, rule 1) is its only history.
6. Who reviews generated scripts, and on which bench are they dry-run before
   use?

## 6. Before starting

- The v1 regression check passes: both skills re-run on the module and the
  feature QA has already validated, and their output matches the validated
  workbooks.
- Open questions 1–3 are answered, and at least one reference vTestStudio
  project per level is available.
- A test environment description exists for the target bench.

## 7. Not part of this plan — still open, needs a project decision

- **Safety-driven test depth.** Which ASIL requires which test methods (fault
  injection, resource tests, coverage) is defined in the project's safety or
  verification plan. Get that mapping from the safety manager; an engineer can
  then write it into the config, the way the classification rules are written.
- **Test strategy beyond Series/Debug SW** — entry criteria (unit verification
  done before SWE.5) and regression selection: decide whether the skills should
  enforce these or only report them.
