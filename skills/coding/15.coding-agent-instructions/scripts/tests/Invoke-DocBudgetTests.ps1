<#
.SYNOPSIS
    Tests Test-DocBudget.ps1 against a temporary fixture under Windows
    PowerShell and, when installed, pwsh.

.DESCRIPTION
    Builds the fixture at run time, compares exit codes and exact output lines,
    deletes the fixture, and exits 0 on pass and 1 on failure.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File skills/coding/15.coding-agent-instructions/scripts/tests/Invoke-DocBudgetTests.ps1
#>
$ErrorActionPreference = 'Continue'

$checker = Join-Path (Split-Path -Parent $PSScriptRoot) 'Test-DocBudget.ps1'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('DocBudgetTest-' + [guid]::NewGuid().ToString('N'))
$utf8 = New-Object System.Text.UTF8Encoding($false)
$failures = 0

function Write-Fixture([string]$RelativePath, [string[]]$Lines) {
    $full = Join-Path $fixture $RelativePath
    $folder = Split-Path -Parent $full
    if (-not (Test-Path -LiteralPath $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
    [IO.File]::WriteAllText($full, (($Lines -join "`n") + "`n"), $utf8)
}

function Invoke-Checker([string]$Shell, [string[]]$Arguments) {
    Push-Location $fixture
    try {
        $output = & $Shell -NoProfile -ExecutionPolicy Bypass -File $checker @Arguments
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            Lines = @($output | Where-Object { $null -ne $_ })
        }
    }
    finally {
        Pop-Location
    }
}

function Assert-Run([string]$Name, $Result, [int]$ExitCode, [string[]]$Lines) {
    $actual = $Result.Lines -join "`n"
    $expected = $Lines -join "`n"
    if ($Result.ExitCode -eq $ExitCode -and $actual -ceq $expected) {
        Write-Output "PASS $Name"
        return
    }
    $script:failures++
    Write-Output "FAIL $Name (exit $($Result.ExitCode), expected $ExitCode)"
    Write-Output '  expected:'
    $Lines | ForEach-Object { Write-Output "    $_" }
    Write-Output '  actual:'
    $Result.Lines | ForEach-Object { Write-Output "    $_" }
}

# Two ideographs built from code points, so this file stays ASCII for Windows PowerShell 5.1.
$chinese = [string][char]0x4E2D + [char]0x6587

# short.md: "# Short", "one two three" -> 4 words ("#" is skipped).
Write-Fixture 'short.md' @('# Short', '', 'one two three')
# long.md: 2 + 5 + 1 + 2 + 1 + 5 = 16 words; the Validation body has 5, the label paragraph 3.
Write-Fixture 'long.md' @('# Long plan', '', '**Current position:** next step pending', '', '## Decisions', '', 'keep it', '', '## Validation', '', "a b c $chinese")
# raised.md: an override with a reason (6 counted tokens + 2), and one without (3 + 2).
Write-Fixture 'raised.md' @('<!-- budget: 50; reason: shared glossary -->', '', 'one two')
Write-Fixture 'bare.md' @('<!-- budget: 50 -->', '', 'one two')
Write-Fixture 'plan/detail.md' @('alpha beta gamma')

$sep = [IO.Path]::DirectorySeparatorChar
$shells = @('powershell')
if (Get-Command pwsh -ErrorAction SilentlyContinue) {
    $shells += 'pwsh'
}

try {
    foreach ($shell in $shells) {
        Assert-Run "$shell within budget" (Invoke-Checker $shell @('-Path', 'short.md', '-MaxWords', '10')) 0 @(
            "ok   4/10 .${sep}short.md")
        Assert-Run "$shell over budget warns" (Invoke-Checker $shell @('-Path', 'long.md', '-MaxWords', '10')) 0 @(
            "OVER 16/10 .${sep}long.md")
        Assert-Run "$shell strict fails" (Invoke-Checker $shell @('-Path', 'long.md', '-MaxWords', '10', '-Strict')) 1 @(
            "OVER 16/10 .${sep}long.md")
        Assert-Run "$shell section budgets" (Invoke-Checker $shell @('-Path', 'long.md', '-MaxWords', '100', '-Section', 'Validation=3,Current position=2,Missing=1')) 0 @(
            "ok   16/100 .${sep}long.md",
            "OVER 5/3 section 'Validation' in .${sep}long.md",
            "OVER 3/2 section 'Current position' in .${sep}long.md")
        Assert-Run "$shell overrides" (Invoke-Checker $shell @('-Path', 'raised.md,bare.md', '-MaxWords', '1')) 0 @(
            "override 50 in .${sep}raised.md: shared glossary",
            "ok   8/50 .${sep}raised.md",
            "override 50 in .${sep}bare.md has no reason",
            "ok   5/50 .${sep}bare.md")
        Assert-Run "$shell total" (Invoke-Checker $shell @('-Path', 'short.md,plan', '-MaxWords', '6', '-Total')) 0 @(
            'OVER 7/6 total of 2 file(s)')
        Assert-Run "$shell missing path" (Invoke-Checker $shell @('-Path', 'absent.md', '-MaxWords', '6')) 2 @(
            'missing path: absent.md')
    }
}
finally {
    Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue
}

if ($failures -gt 0) {
    exit 1
}
exit 0
