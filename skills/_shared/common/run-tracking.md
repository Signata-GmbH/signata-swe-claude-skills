# Run tracking — identity, timing, commits (all ledger-keeping skills)

> Loaded by every skill that keeps a run ledger: `code-dev`, `code-fix`,
> `code-review`, `unit-test`, `integration-test`, `qualification-test`.
> (`project-init` writes one config file and keeps no ledger; it keeps its own
> ask-before-commit rule in [project-config.md](project-config.md) §6.)
>
> **Why this exists.** Skill outputs, manifests, run history and inputs written
> back at pre-flight used to be left for the engineer to commit by hand. When
> they were not committed, the next run diffed against a ledger git never saw,
> history lines were lost on branch switches, and nobody could tell what a run
> had done. Every run now **commits its own files at every gate and at the
> end**, and records **when** each run, phase and gate started and ended.
>
> The `signata-swe` plugin also ships **hooks** (`hooks/hooks.json`) that stamp
> wall-clock times and refuse to let a run end with its files uncommitted. The
> rules below hold with or without them: the hooks are a backstop, never a
> substitute — the skill still runs every step here itself.

## 1. Run identity & the active-run marker

**Timestamps are never written from memory.** Every time in this file comes
from the shell clock, in UTC ISO-8601:

```
date -u +%Y-%m-%dT%H:%M:%SZ
```

**Start the run as soon as the key is known** — the module (code skills,
`integration-test`) or the feature slug (`qualification-test`) — and before
reading the config or any input, so the intake is timed too.

1. **Check for an open run first** (§5): if `20_AI/.active_run.json` exists, deal
   with it before starting a new one.
2. Take the start time `T0`. If `20_AI/.skill_invoked.json` exists, was written
   by the hook for this skill, and is less than one hour old, use its `ts` as
   `T0` instead (it was stamped when the skill was invoked) and delete it.
3. `run_id = <skill>-<KEY>-<T0 as YYYYMMDDTHHMMSSZ>`, e.g.
   `code-review-SAPF_Mode-20261006T091200Z`.
4. Write the marker `20_AI/.active_run.json` (untracked; §3.1 ignores it):

   ```json
   { "run_id": "...", "skill": "code-review", "skill_version": "<plugin version or commit>",
     "key": "SAPF_Mode", "started": "<T0>",
     "history": "20_AI/manifests/history/SAPF_Mode.jsonl",
     "owned_paths": [], "phase": "intake", "hook_events": [] }
   ```

   `owned_paths` lists the files **outside `20_AI/`** this run writes (source
   for `code-dev`/`code-fix`, the `.tst` for `unit-test`); add to it as soon as
   you decide to write one. The hooks read this marker — keep it current.
5. **Append** a `run_start` event to the history file (§2).

## 2. Events in the history file

The history file stays where each skill already keeps it
(`20_AI/manifests/history/<MODULE>.jsonl` for the code skills,
`20_AI/manifests/{integration-test,qualification-test}/history/<KEY>.jsonl` for
the test-spec skills). It is still **append-only** — never edit a prior line —
but it now holds **events**, one JSON object per line, each with
`ev`, `run_id`, `ts`:

| `ev` | When | Extra fields |
|---|---|---|
| `run_start` | §1 step 5 | `skill`, `skill_v`, `key`, `branch`, `sha` (HEAD), `dirty` (paths outside this run's scope with uncommitted changes) |
| `phase_start` | entering a phase (`intake`, `preflight`, `analysis`, `phase2`, `output`) | `phase` |
| `gate_reached` | just before stopping at a HARD GATE / STOP | `gate` (e.g. `step3-manifest`, `step4-phase1`, `step5-proposal`), `phase` |
| `gate_ack` | first action after the engineer answers a gate | `gate`, `outcome` (`approved` / `changed` / `rejected`) |
| `output_written` | each deliverable written | `path`, `hash` (`git hash-object`) |
| `run_end` | last event of a completed run | the former per-run record — `skill_v`, `sha`, `reqs_sha`, `delta:{added,updated,removed}`, `notes` — plus `timing` (§4) and `commits` (the SHAs this run made so far, from `git log --grep "AI-Run: <run_id>"`) |
| `run_aborted` | an open run closed without completing (§5) | `reason`, `last_phase` |

Lines written before this rule (no `ev` field) are legacy per-run records:
read them as `run_end` events and never rewrite them.

Write `gate_reached` and `gate_ack` with the clock **yourself**. The hooks add
their own `stop` / `prompt` stamps to the marker (§6); at `run_end` you merge
them into `timing` — you do not need to wait for them.

## 3. Commits — automatic, at every gate and at the end

### 3.1 Before the first commit of a run

- **Not a git work tree, detached HEAD, or a merge / rebase / cherry-pick in
  progress** → do not commit; say so once at the first gate, record
  `commit: skipped (<reason>)` in each event that would have committed, and
  carry on. The run is still tracked in the history file.
- **On the base branch** (derived as in project-config §1) → ask **once**, at
  the first gate, as a popup: commit here, or create and switch to
  `ai/<skill>/<KEY>` from the current HEAD. Record the answer in the marker
  (`commit_branch`) and do not ask again this run. Anywhere else → commit on the
  current branch without asking.
- **`20_AI/.gitignore`** — ensure it contains these three lines (create the file
  if absent, add a missing line otherwise) and commit it with the first gate:

  ```
  .active_run.json
  .skill_invoked.json
  ~$*
  ```

- **Ignored outputs** — run `git check-ignore -v` on each path you will stage.
  If a skill output (an `.xlsx`, say) is ignored by a repo rule, ask once
  whether to force-add this run's outputs (`git add -f`); record the answer in
  the marker. Never edit the repo's own `.gitignore` to get around it.

### 3.2 What a run commits, and when

| Commit | When | Stages | Message (subject) |
|---|---|---|---|
| **gate** | at every HARD GATE / STOP, after `gate_reached` is appended, **before** you stop | everything this run wrote or changed under `20_AI/` (manifest, history, Phase-1 questions workbook, inputs written back to config/manifest, copied input documents, partial outputs) | `AI(<skill>): <KEY> — gate <gate>` |
| **code** | `code-dev`, `code-fix`: right after the source is written and the self-review is done, **before** the final commit | only the files in `owned_paths` (`.c` / `.h` / `.mak` / build files) | `AI(<skill>): <KEY> — generated code` / `— fix <ISSUE_ID>` |
| **final** | after `run_end` is appended | the outputs, the manifest `last_run`, the history file, `20_AI/.gitignore` if changed, and — for `unit-test` — the `.tst` in `owned_paths` | `AI(<skill>): <KEY> — run complete` |
| **abort** | when an open run is closed as aborted (§5) | whatever the aborted run left under `20_AI/` + its history | `AI(<skill>): <KEY> — run aborted` |

**Inputs count.** A document the engineer supplies at pre-flight that lives in
the repository (new, or changed since HEAD) is staged with the next gate commit,
and so is an engineer-edited file this run reads back — a Phase-1 questions
workbook with answers, a findings list with author statements. That is how the
next reader of the history knows which inputs a run actually saw.

**Every commit message** carries these trailers, then the attribution line(s)
the session requires:

```
AI-Run: <run_id>
AI-Skill: <skill>@<skill_version>
AI-Key: <KEY>
AI-Phase: <phase or gate>
```

`git log --grep "AI-Run: <run_id>"` then lists everything a run committed, and
`git log --grep "AI-Key: <KEY>"` every run on a module or feature.

### 3.3 Staging rules — never anything else

- `git add -- <explicit paths>` only. **Never** `git add -A`, `git add .`,
  `git commit -a`, or a directory wildcard outside `20_AI/<this run's area>`.
- Changes **outside this run's scope** — the engineer's own edits, another
  module's manifest — are never staged. List them once in `run_start.dirty` and
  in the first gate summary, and leave them alone.
- If an owned source file already had uncommitted engineer changes **before**
  the run wrote to it, do not mix them into the run's commit: stop at the code
  step and ask the engineer to commit or stash their change first.
- Never push, amend, rebase, or force. Never skip hooks or signing
  (`--no-verify`, `--no-gpg-sign`). If the commit fails (a pre-commit hook
  rejects it, say), report the error verbatim, leave the files staged, and stop
  at that gate — do not work around it.
- Nothing to commit at a gate (nothing changed since the last commit) → skip
  the commit and say so.

Commits are **not** logged as history events — a line appended after a commit
would leave the history file permanently uncommitted. The commit trailers are
the record: `run_end.commits` lists the run's commits up to then, and the final
commit is found by its `AI-Run` trailer. **Order at the end of a run:** append
`run_end` → update `last_run` → **final** commit → delete the marker → stop.
At a gate: append `gate_reached` → **gate** commit → stop.

## 4. Timing — what is recorded, what it means

At `run_end` compute and record, from the events of this `run_id` plus the
marker's `hook_events`:

```json
"timing": {
  "started": "<T0>", "ended": "<clock now>",
  "total_s": 0,
  "engineer_wait_s": 0,
  "ai_active_s": 0,
  "phases": [ { "phase": "analysis", "start": "...", "end": "...", "s": 0 } ],
  "gates":  [ { "gate": "step4-phase1", "reached": "...", "ack": "...", "wait_s": 0 } ],
  "sessions": 1
}
```

- Several hook `stop` stamps in a row (a stop the Stop hook blocked, then the
  real one) count as one: use the **last** `stop` before each `prompt`.
- **`wait_s`** of a gate = `ack − reached`. Where the hooks stamped a `stop`
  and the following `prompt`, use those (they are exact); otherwise use your
  own `gate_reached` / `gate_ack`.
- **`engineer_wait_s`** = sum of every gate's `wait_s` **plus** every other
  `stop → prompt` gap the hooks recorded (a question asked mid-phase).
  **`ai_active_s`** = `total_s − engineer_wait_s`. These two numbers are what
  the team's time-efficiency metrics use; never report `total_s` alone as
  "time taken by the AI".
- **`sessions`** = how many sessions the run spanned (a resumed run, §5).
- Copy `started`, `ended`, `run_id` and the `timing` totals into the manifest
  `last_run` (overwritten each run, as before).

## 5. Open runs — resume or abort, never ignore

A marker left behind means a run did not reach `run_end` (session closed at a
gate, crash, engineer walked away). At the start of any run — and whenever the
SessionStart hook reports one — read `20_AI/.active_run.json` and:

- **Same skill and same key** → ask (popup): **resume** it (keep the `run_id`,
  append `gate_ack` for the gate it stopped at, continue from that step; count
  one more session) or **abort** it and start fresh.
- **Different skill or key** → ask: **abort** that run and continue with this
  one, or **stop** here so it can be resumed first. One run at a time per work
  tree.

Abort = append `run_aborted` (with `last_phase`), make the **abort** commit
(§3.2), delete the marker — in that order. Never delete a marker without one of these two
outcomes recorded.

## 6. What the hooks do (backstop, installed with the plugin)

| Hook event | Action |
|---|---|
| `UserPromptSubmit` | If the prompt invokes a `signata-swe` skill, write `20_AI/.skill_invoked.json` (`skill`, `ts`). If a run is open, append `{ev: prompt, ts}` to the marker's `hook_events`. |
| `PostToolUse` (Skill) | Same as above when the skill is invoked through the Skill tool. |
| `Stop` | If a run is open, append `{ev: stop, ts}` to `hook_events`. If anything under `20_AI/` or in `owned_paths` is uncommitted (the history file excepted — its newest events are picked up by the next commit), **block the stop** with a reason telling you to commit per §3 — or, if you are mid-step and not at a gate, to say so and stop. It blocks at most once per distinct set of dirty files. |
| `SessionStart` | If a run is open, add a note to the session context: name the `run_id` and its last phase, and say to resume or abort it per §5 before doing anything else. |

The hooks never commit, never edit tracked files, and never fail a session: on
any error they exit quietly. When the Stop hook blocks, treat its reason as an
instruction from the engineer: commit what §3 says, or explain why you are
stopping mid-step.

## 7. One output per key — git is the version history

Each skill keeps **one living output** per module or feature, at a fixed path
with no date or run number in its name. Earlier versions live in git (the
commit trailers of §3.2 find them), not as sibling files:

| Skill | Living output |
|---|---|
| `code-review` | `20_AI/CodeReview/<MODULE>_CodeReview_Findings.xlsx` (review-quality.md "Living findings list") |
| `unit-test` | the `.tst` under `layout.vcast_env` |
| `code-fix` | `20_AI/CodeFix/<MODULE>_<ISSUE_ID>_FixReport.md` (one per issue) |
| `code-dev` | the module sources + its Implementation Review document |
| `integration-test` | `20_AI/IntegrationTest/<MODULE>_SWE5_TestCases.xlsx` |
| `qualification-test` | `20_AI/QualificationTest/<FEATURE_SLUG>_SWE6_TestCases.xlsx` |

**Before any re-run writes its output, check three things** (the code skills
now do what the test-spec skills already did, testspec workflow-discipline §8):

1. **Is the previous output still there?** If `last_run.output.path` is gone,
   say so: the run regenerates rather than updating.
2. **Was it edited since?** If its `git hash-object` differs from
   `last_run.output.hash`, someone changed it after the last run. For the code
   review that is expected (authors fill their columns) — merge, never
   overwrite. For any other output, show what changed (`git diff` against the
   run's final commit) and ask before writing over it.
3. **Is it committed?** If the previous output has uncommitted changes, stage
   them with this run's first gate commit — before you change the file — so the
   engineer's edits are preserved as their own revision.

Record the new `output: {path, hash}` in `last_run` after writing.
