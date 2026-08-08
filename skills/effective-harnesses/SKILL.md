---
name: effective-harnesses
description: Long-running agent project harness for Codex, OpenClaw, Claude Code, and other coding agents. Use to initialize or maintain projects that need feature decomposition, resumable progress tracking, test-gated completion, session recovery, and git-backed checkpoints through files such as feature_list.json, init.sh, progress logs, and coding standards.
---

# Effective Harnesses

## Purpose

Use this skill to keep long-running implementation or research projects reliable across many agent sessions. Maintain a small set of durable project files so any compatible agent can resume work without relying on hidden chat context.

## Core Principles

- Work on one feature at a time unless the user explicitly requests parallel work.
- Track every feature in `feature_list.json`.
- Run each feature's test/check command before marking it complete.
- Keep a human-readable progress log for recovery.
- Commit meaningful checkpoints when the environment and user instructions require git commits.
- Prefer portable files and commands over host-specific slash commands.

## Harness Files

Create or maintain these files at the project root:

| File | Purpose |
|---|---|
| `feature_list.json` | Canonical list of features, priorities, statuses, and test results. |
| `init.sh` / `init.ps1` / `init.py` | Optional project bootstrap/start command for future sessions. Prefer `init.ps1` or `init.py` on Windows native. |
| `agent-progress.md` | Chronological progress notes, decisions, blockers, and next steps. |
| `CODING_STANDARDS.md` | Optional project-specific coding/test/review conventions. |

If the project already has Claude-specific names such as `claude-progress.txt`, keep them if users rely on them, but prefer the portable `agent-progress.md` name for new projects.

## Initialize a Project

1. Identify the project goal, stack, default test command, and startup command.
2. Create `feature_list.json` from the schema below.
3. Create a repeatable bootstrap if useful: `init.sh` for Unix-like shells, `init.ps1` or `init.py` for Windows native. Do not require Bash on Windows.
4. Create `agent-progress.md` with initial context, assumptions, and next feature.
5. Create or update `CODING_STANDARDS.md` only when project conventions are known or requested.
6. Run the bootstrap and/or test command if safe in the current environment.

## Add a Feature

Append a new feature object with:

- Unique sequential ID such as `feat-001`.
- Category: `functional`, `bugfix`, `refactor`, `research`, or another user-approved category.
- Priority: lower number means higher priority.
- Clear description and concrete steps.
- Test/check command that proves completion.
- Initial status: `pending` and `passes: false`.

## Resume a Session

At the beginning of a resumed project:

1. Read `feature_list.json`.
2. Read recent git history if available.
3. Read `agent-progress.md` or legacy progress logs.
4. Select the highest-priority feature with status other than `completed`.
5. Run `init.sh`, `init.ps1`, `init.py`, or the documented startup command when appropriate for the host OS.
6. Run a baseline test/check when safe, then begin work.

## Complete a Feature

Before marking a feature complete:

1. Verify implementation/research artifacts exist.
2. Run the feature's `test_command` or a justified equivalent.
3. Store a concise `test_output` summary.
4. Set `test_status` to `passed` only on success; otherwise use `failed` and leave `passes: false`.
5. Update `agent-progress.md` with what changed, validation, and next steps.
6. Commit if required by user or project policy.

## File-Mode Research Harness Pattern

For large research tasks, prefer a file-mode harness instead of chat-heavy handoff:

1. Create a domain data directory such as `data/<domain>/` plus a `depth/` subdirectory.
2. Track run status and convergence in `data/<domain>/index.json`.
3. Split research into independent dimensions and write each dimension to `depth/<dimension>.json`.
4. If the user explicitly requests/allows parallel agents and the host supports them, workers should write JSON files and reply only `DONE`; otherwise perform the same dimensions sequentially.
5. Merge depth files into a main JSON data file, export any required CSV tables, then generate deliverables.
6. Validate JSON/CSV/report files before marking the feature complete.

For renewable-energy market intelligence, use `$renewable-market-research`, which specializes this pattern for country + technology research and full/lite report generation.

## `feature_list.json` Schema

```json
{
  "version": "1.1",
  "project": "Project name",
  "description": "One-sentence project goal",
  "test_command": "npm test",
  "created": "YYYY-MM-DD",
  "features": [
    {
      "id": "feat-001",
      "category": "functional",
      "priority": 1,
      "description": "Feature description",
      "steps": ["Step 1", "Step 2"],
      "test_command": "npm test",
      "test_status": "pending",
      "test_output": "",
      "status": "pending",
      "passes": false
    }
  ]
}
```

Allowed `status` values: `pending`, `in_progress`, `blocked`, `completed`.
Allowed `test_status` values: `pending`, `running`, `passed`, `failed`, `skipped`.
Use `skipped` only with a clear reason in `test_output`.

## Progress Log Format

Append entries like:

```markdown
## YYYY-MM-DD — feat-001 short title

- Status: in_progress/completed/blocked
- Changed: ...
- Validation: `command` → result summary
- Decisions: ...
- Next: ...
```

## Host Portability Notes

- Codex: use normal file edits, terminal commands, plan updates, and git commits according to the current instructions.
- OpenClaw: keep the same project files; place this skill under an OpenClaw skills directory or workspace skills directory.
- Windows native: prefer PowerShell (`.ps1`) or Python (`.py`) startup/validation scripts; avoid Bash-only `make.sh`, `sed`, `awk`, `chmod`, or Unix path assumptions.
- Claude Code: legacy slash commands may be used if present, but do not require them for portability.
