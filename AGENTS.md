# Repository Agent Guide

This repository contains portable `SKILL.md` skills for Exa-powered company research, foreign-trade market research, renewable-energy market intelligence, and long-running project harnesses.

## Key Locations

- `skills/`: portable Codex/OpenClaw skill packages. Each skill must contain a `SKILL.md` with only `name` and `description` in YAML frontmatter.
- `skills/*/agents/openai.yaml`: Codex/OpenAI UI metadata. Keep it aligned with the corresponding `SKILL.md`.
- `.claude/skills/`: legacy Claude Code skill packages retained for compatibility.
- `research-output/`: generated research reports and examples.
- `feature_list.json`: example progress tracker for long-running research.
- `skills/renewable-market-research/references/`: detailed file-mode research, data-model, and PDF pipeline guidance.

## Editing Rules

- Prefer updating `skills/` for cross-agent compatibility.
- Do not add Claude-only frontmatter fields such as `triggers`, `requires_mcp`, `context`, or `allowed-tools` to portable `skills/*/SKILL.md` files.
- Keep research skills source-driven: require citations, confidence notes, and clear separation between verified facts and inference.
- For large research skills, prefer file-mode outputs under `data/<domain>/` and avoid returning large raw search results through chat.
- Keep workflows Windows-native friendly: prefer Python and PowerShell entry points; do not require Bash, WSL, `make.sh`, `chmod`, `sed`, or `awk` for normal operation.
- Chrome MCP is an accepted sanitized human-browser fallback/verification tool; record only distilled evidence and never persist cookies, credentials, private account data, or unrelated browsing history.
- If adding or changing a skill, validate it with the Codex skill validator when available.

## Testing

- For skill metadata changes, run:
  - `python3 /opt/codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>`
- For JSON changes, run the host Python launcher, for example:
  - Unix-like: `python3 -m json.tool feature_list.json >/tmp/feature_list.validated.json`
  - Windows PowerShell: `py -3 -m json.tool feature_list.json > $env:TEMP\feature_list.validated.json`
