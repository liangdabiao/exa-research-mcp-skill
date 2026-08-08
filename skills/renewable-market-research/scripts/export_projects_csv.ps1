param(
    [Parameter(Mandatory = $true)]
    [string]$InputJson,

    [Parameter(Mandatory = $true)]
    [string]$OutputCsv
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "export_projects_csv.py"

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    & py -3 $pythonScript $InputJson $OutputCsv
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python $pythonScript $InputJson $OutputCsv
    exit $LASTEXITCODE
}

throw "Python was not found. Install Python 3 or add it to PATH."
