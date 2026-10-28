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
$paths = @(
    '.env.example', '.gitignore', '.vscode', '.github', '.githooks',
    'README.md', 'backend', 'clockwork-data-starter', 'config', 'data',
    'docs', 'frontend/.env.example', 'frontend/src', 'frontend/tests',
    'frontend/eslint.config.js', 'frontend/index.html', 'frontend/package.json',
    'frontend/package-lock.json', 'frontend/playwright.config.js',
    'frontend/playwright.demo.config.js', 'frontend/vite.config.js', 'infra', 'scripts'
)

foreach ($path in $paths) {
    $target = Join-Path $repoRoot $path
    if (Test-Path -LiteralPath $target) {
        Write-Host "Scanning working files: $path"
        & $scannerPath --redact --no-banner dir $target
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
}

Write-Host 'Scanning all available Git history...'
& $scannerPath --redact --no-banner git $repoRoot
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host 'Secret scan completed without findings.'
