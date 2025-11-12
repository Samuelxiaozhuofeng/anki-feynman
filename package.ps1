Param(
    [string]$Version,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Find-Python {
    foreach ($name in @("python", "python3")) {
        try {
            $cmd = Get-Command $name -ErrorAction Stop
            return $cmd.Path
        } catch {
            continue
        }
    }
    throw "Python executable not found in PATH."
}

$pythonExe = Find-Python
$arguments = @(
    "scripts/package_anki_addon.py",
    "--sync-deps",
    "-s", ".",
    "-o", "dist",
    "--name", "anki_feynman"
)

if ($Version) {
    $arguments += @("--version", $Version)
}
if ($Verbose) {
    $arguments += "-v"
}

Push-Location $repoRoot
try {
    & $pythonExe @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Packaging command failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}
