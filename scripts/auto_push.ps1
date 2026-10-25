param(
    [ValidateRange(1, 60)]
    [int]$QuietSeconds = 5,
    [ValidateRange(5, 300)]
    [int]$RetrySeconds = 30
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Get-WorkingTreeStatus {
    $output = & git status --porcelain --untracked-files=all 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Could not read Git status: $($output -join ' ')"
    }
    return ($output -join "`n")
}

function Invoke-Git {
    param([string[]]$Arguments)

    $output = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed: $($output -join ' ')"
    }
    if ($output) {
        $output | ForEach-Object { Write-Host $_ }
    }
}

function Commit-WorkingTree {
    Invoke-Git -Arguments @('add', '--all')

    $null = & git diff --cached --quiet
    $diffExitCode = $LASTEXITCODE
    if ($diffExitCode -eq 0) {
        return $false
    }
    if ($diffExitCode -ne 1) {
        throw 'Could not inspect staged Git changes.'
    }

    $stagedPaths = & git diff --cached --name-only --diff-filter=ACMR
    if ($LASTEXITCODE -ne 0) {
        throw 'Could not inspect staged file names.'
    }

    $blockedPaths = @(
        $stagedPaths | Where-Object {
            ($_ -match '(?i)(^|/)\.env(?:$|\.)' -and
                $_ -notmatch '(?i)(^|/)\.env\.example$') -or
            $_ -match '(?i)(^|/)secrets(/|$)' -or
            (($_ -match '(?i)\.(?:key|pem|p12|pfx|sqlite3?|db)(?:[-.].*)?$') -and
                $_ -notmatch '(?i)^clockwork-data-starter/example/clockwork_fixture\.sqlite3$')
        }
    )
    if ($blockedPaths.Count -gt 0) {
        throw "Refusing to publish sensitive-looking paths: $($blockedPaths -join ', '). Review them and update .gitignore if needed."
    }

    $message = 'Auto-sync: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    Invoke-Git -Arguments @('commit', '-m', $message)
    return $true
}

try {
    $null = Invoke-Git -Arguments @('remote', 'get-url', 'origin')
} catch {
    throw 'No GitHub remote named origin is configured. Add one before starting auto-push.'
}

$lastStatus = Get-WorkingTreeStatus
$pendingSince = if ($lastStatus) { Get-Date } else { $null }
$nextPushAttempt = $null

Write-Host "Auto-push is monitoring $repoRoot. Changes are committed after $QuietSeconds seconds without edits."
Write-Host 'Press Ctrl+C in this terminal to stop auto-push.'

while ($true) {
    Start-Sleep -Seconds 1
    $currentStatus = Get-WorkingTreeStatus

    if ($currentStatus -ne $lastStatus) {
        $lastStatus = $currentStatus
        $pendingSince = Get-Date
    }

    if ($pendingSince -and ((Get-Date) - $pendingSince).TotalSeconds -ge $QuietSeconds) {
        try {
            $createdCommit = Commit-WorkingTree
            if ($createdCommit) {
                Write-Host 'Changes committed. Pushing to GitHub...'
                $nextPushAttempt = Get-Date
            }
            $pendingSince = $null
            $lastStatus = Get-WorkingTreeStatus
        } catch {
            Write-Warning $_
            $pendingSince = $null
            $lastStatus = Get-WorkingTreeStatus
        }
    }

    if ($nextPushAttempt -and (Get-Date) -ge $nextPushAttempt) {
        try {
            Invoke-Git -Arguments @('push')
            Write-Host 'Push completed.'
            $nextPushAttempt = $null
        } catch {
            Write-Warning "Push failed; will retry in $RetrySeconds seconds. $($_.Exception.Message)"
            $nextPushAttempt = (Get-Date).AddSeconds($RetrySeconds)
        }
    }
}
