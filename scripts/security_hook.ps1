param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('pre-commit', 'pre-push')]
    [string]$Mode
)

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
    throw 'Gitleaks is required. Install it, then run scripts/install_security_hooks.ps1.'
}

$scannerPath = if ($scanner -is [System.IO.FileInfo]) { $scanner.FullName } else { $scanner.Source }
if ($Mode -eq 'pre-commit') {
    & $scannerPath --redact --no-banner protect --staged
} else {
    & $scannerPath --redact --no-banner git $repoRoot
}
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
