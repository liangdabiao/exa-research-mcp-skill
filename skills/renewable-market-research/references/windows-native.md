# Windows Native Operation

Use this reference when the host runs on Windows without WSL, Git Bash, or a Unix shell. Prefer PowerShell and Python entry points so the workflow works in Codex, OpenClaw, and Claude Code on Windows native installs.

## Command Rules

- Prefer `py -3` on Windows; fall back to `python` or `python3` only after checking what exists.
- Prefer PowerShell cmdlets over Bash utilities:
  - create directories: `New-Item -ItemType Directory -Force data/renewable-market/depth`
  - validate JSON: `py -3 -m json.tool data/renewable-market/index.json > $env:TEMP\renewable-index.validated.json`
  - list files: `Get-ChildItem -Recurse data/renewable-market`
  - remove generated caches: `Remove-Item -Recurse -Force __pycache__`
- Do not require `bash`, `sed`, `awk`, `xargs`, `chmod`, or `make.sh` for normal operation.
- Keep all reusable automation in `.py` scripts when possible. Add `.ps1` wrappers only for operator convenience.
- Quote paths that may contain spaces and use `Path`/`Join-Path` in PowerShell or `pathlib.Path` in Python.

## PowerShell Startup Pattern

If a project needs a startup script, create `init.ps1` and/or `init.py` instead of requiring `init.sh`:

```powershell
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force "data/renewable-market/depth" | Out-Null
py -3 -m json.tool "feature_list.json" > "$env:TEMP\feature_list.validated.json"
```

For Python startup scripts:

```powershell
py -3 .\init.py
```

## CSV Export

Use either direct Python:

```powershell
py -3 .\skills\renewable-market-research\scripts\export_projects_csv.py `
  .\data\renewable-market\uzbekistan-wind.json `
  .\data\renewable-market\uzbekistan-wind.csv
```

Or the PowerShell wrapper:

```powershell
.\skills\renewable-market-research\scripts\export_projects_csv.ps1 `
  -InputJson .\data\renewable-market\uzbekistan-wind.json `
  -OutputCsv .\data\renewable-market\uzbekistan-wind.csv
```

## Integrity Validation

After the master JSON and canonical ledger are built, run the source-to-final integrity validator:

```powershell
.\skills\renewable-market-research\scripts\validate_market_integrity.ps1 `
  -MarketJson .\data\renewable-market\uzbekistan-wind.json `
  -DepthDir .\data\renewable-market\depth `
  -Output .\data\renewable-market\uzbekistan-wind-integrity.json
```

Use `-Strict` only when warnings should fail the run. Duplicate candidates, critical-field verification gaps, report-card field gaps, and depth-to-master propagation gaps always require review because they can indicate unmerged records, confirmed-project fields that still lack Chrome MCP/original-file verification, or rich depth data that was lost before reporting.

## PDF Rendering on Windows

- Prefer Python or Node commands that run directly in PowerShell.
- If a prior pipeline has `make.sh`, translate it into explicit steps (`py -3 script.py`, `node script.js`) rather than invoking Bash.
- Configure CJK fonts explicitly. Common Windows paths:
  - `C:/Windows/Fonts/simsun.ttc`
  - `C:/Windows/Fonts/simhei.ttf`
  - `C:/Windows/Fonts/msyh.ttc`
- If PDF generation is unstable, keep Markdown as source of truth and record the PDF limitation in `index.json`.

## Chrome MCP as Human Browser

Chrome MCP is allowed as a first-class fallback/verification tool when it has already been sanitized and configured by the user.

Use Chrome MCP when:

- Exa misses dynamic pages, official PDFs, tables, maps, ecommerce listings, dashboards, or JavaScript-rendered content.
- A source must be verified visually as a real browser user.
- Login-free pages behave differently for bots/search extraction.
- Downloading a PDF/CSV/report requires a browser click flow.

Rules:

- Treat Chrome MCP output as evidence, but still store source URL, page title, accessed date, and concise facts in JSON.
- Do not copy cookies, credentials, account identifiers, private profile data, or unrelated browsing history into files.
- Do not stream screenshots or full page dumps into the main chat unless the user specifically asks; write distilled evidence to JSON.
- Record Chrome MCP usage in the depth record `notes` or `collectionMethod` field.

## Search Plan and Coverage Validation

Use the Python search orchestration helper through PowerShell when you need a reproducible search plan and coverage report:

```powershell
.\skills\renewable-market-research\scripts\search_orchestration.ps1 plan `
  --country Kazakhstan `
  --technology wind `
  --audience "Mingyang OEM commercial entry" `
  --official-languages "Kazakh,Russian" `
  --known-projects "Sho'rkul,Zhanatas,Arkalyk" `
  --slug kazakhstan-wind `
  --output data\renewable-market\kazakhstan-wind-search-plan.json

.\skills\renewable-market-research\scripts\search_orchestration.ps1 validate `
  --plan data\renewable-market\kazakhstan-wind-search-plan.json `
  --depth-dir data\renewable-market\depth `
  --output data\renewable-market\kazakhstan-wind-search-coverage.json
```

The helper is standard-library Python only. It does not call network APIs; it plans and validates worker search coverage so Exa, Chrome MCP, and other host tools can be used consistently.
