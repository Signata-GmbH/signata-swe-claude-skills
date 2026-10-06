"""signata-swe run-tracking hooks (skills/_shared/common/run-tracking.md §6).

Invoked by Claude Code with the hook payload as JSON on stdin:
    python run_tracker.py <session-start | prompt | skill | stop>

The hooks are a backstop to the skills, never a substitute:
- they stamp wall-clock times into the untracked active-run marker
  (20_AI/.active_run.json) and the invocation file (20_AI/.skill_invoked.json);
- the Stop hook blocks a stop once while a run's files are uncommitted;
- SessionStart reminds the session of a run left open.

They never commit, never touch tracked files, and never fail a session: any
error exits 0 silently. Standard library only.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

PLUGIN = "signata-swe"
SKILLS = ("code-dev", "code-fix", "code-review", "unit-test",
          "integration-test", "qualification-test")
MARKER = os.path.join("20_AI", ".active_run.json")
INVOKED = os.path.join("20_AI", ".skill_invoked.json")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(root, *args):
    out = subprocess.run(["git", "-C", root, *args], capture_output=True,
                         text=True, timeout=20)
    return out.stdout if out.returncode == 0 else None


def repo_root(cwd):
    top = git(cwd, "rev-parse", "--show-toplevel")
    return top.strip() if top else cwd


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def add_hook_event(root, ev):
    path = os.path.join(root, MARKER)
    marker = read_json(path)
    if marker is None:
        return None
    marker.setdefault("hook_events", []).append({"ev": ev, "ts": now()})
    write_json(path, marker)
    return marker


def skill_of(text):
    """Return the signata-swe skill a prompt or Skill-tool name invokes, if any."""
    m = re.match(r"\s*/?(?:%s:)?(%s)\b" % (PLUGIN, "|".join(SKILLS)), text or "")
    return m.group(1) if m else None


def note_invocation(root, skill):
    if skill and os.path.isdir(os.path.join(root, "20_AI")):
        write_json(os.path.join(root, INVOKED), {"skill": skill, "ts": now()})


def uncommitted(root, marker):
    """Paths this run owns that differ from HEAD (staged, unstaged or untracked)."""
    paths = ["20_AI"] + list(marker.get("owned_paths") or [])
    out = git(root, "status", "--porcelain", "--untracked-files=all", "--", *paths)
    if out is None:
        return []
    ignore = {MARKER.replace(os.sep, "/"), INVOKED.replace(os.sep, "/"),
              (marker.get("history") or "").replace("\\", "/")}
    files = []
    for line in out.splitlines():
        p = line[3:].strip().strip('"')
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        if p in ignore or p.endswith(".tmp") or os.path.basename(p).startswith("~$"):
            continue
        files.append(p)
    return sorted(files)


def on_session_start(root, _payload):
    marker = read_json(os.path.join(root, MARKER))
    if not marker:
        return
    msg = ("signata-swe: an AI run is still open in this repository — run_id "
           f"{marker.get('run_id')} ({marker.get('skill')} on {marker.get('key')}, "
           f"started {marker.get('started')}, last phase {marker.get('phase')}). "
           "Before any other work here, ask the engineer whether to resume it or "
           "abort it, per skills/_shared/common/run-tracking.md §5.")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": msg}}))


def on_prompt(root, payload):
    note_invocation(root, skill_of(payload.get("prompt")))
    add_hook_event(root, "prompt")


def on_skill(root, payload):
    tool_input = payload.get("tool_input") or {}
    note_invocation(root, skill_of(tool_input.get("skill") or tool_input.get("command")))


def on_stop(root, payload):
    marker = add_hook_event(root, "stop")
    if marker is None or payload.get("stop_hook_active"):
        return
    files = uncommitted(root, marker)
    if not files:
        return
    # Block once per distinct set of dirty files, so a mid-step question is
    # interrupted at most once rather than on every turn.
    fingerprint = hashlib.sha1("\n".join(files).encode()).hexdigest()
    if marker.get("last_block") == fingerprint:
        return
    marker["last_block"] = fingerprint
    write_json(os.path.join(root, MARKER), marker)
    shown = "\n".join("  " + f for f in files[:20])
    more = f"\n  … and {len(files) - 20} more" if len(files) > 20 else ""
    reason = (f"signata-swe run {marker.get('run_id')} has uncommitted files:\n"
              f"{shown}{more}\n"
              "If you are stopping at a gate or at the end of the run, commit them "
              "now per skills/_shared/common/run-tracking.md §3 (explicit paths, "
              "AI-Run trailers), then stop. If you are stopping mid-step to ask "
              "the engineer something, say so in one line and stop.")
    print(json.dumps({"decision": "block", "reason": reason}))


HANDLERS = {"session-start": on_session_start, "prompt": on_prompt,
            "skill": on_skill, "stop": on_stop}


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    handler = HANDLERS.get(sys.argv[1] if len(sys.argv) > 1 else "")
    if handler:
        handler(repo_root(payload.get("cwd") or os.getcwd()), payload)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # never break the engineer's session
        pass
    sys.exit(0)
