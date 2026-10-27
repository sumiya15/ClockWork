$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$scanner = Get-Command gitleaks -ErrorAction SilentlyContinue
if (-not $scanner) {
    $packagePath = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
    $scanner = Get-ChildItem -Path $packagePath -Filter gitleaks.exe -Recurse -ErrorAction SilentlyContinue |
        Select-Object -First 1
}
if (-not $scanner) {
    throw 'Gitleaks was not found. Install it with: winget install --id Gitleaks.Gitleaks --exact'
}

$scannerPath = if ($scanner -is [System.IO.FileInfo]) { $scanner.FullName } else { $scanner.Source }
$versionOutput = & $scannerPath version
if ($LASTEXITCODE -ne 0) {
    throw 'Gitleaks is installed but could not be run.'
}
Write-Host "Using Gitleaks $versionOutput"

& git config --local core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) {
    throw 'Could not configure Git to use the repository security hooks.'
}
Write-Host 'Local commit and push secret-scanning hooks are enabled.'
