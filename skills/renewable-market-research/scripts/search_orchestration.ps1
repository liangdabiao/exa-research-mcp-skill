param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ArgsForPython
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "search_orchestration.py"

$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) {
    & py -3 $PythonScript @ArgsForPython
    exit $LASTEXITCODE
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & python $PythonScript @ArgsForPython
    exit $LASTEXITCODE
}

Write-Error "Python launcher not found. Install Python 3 or ensure py/python is on PATH."
exit 1
