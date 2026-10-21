<#
.SYNOPSIS
    Reports Markdown documents and sections that exceed a word budget.
    Read-only.

.DESCRIPTION
    Words are whitespace-separated tokens; each CJK ideograph counts as one
    word, and tokens made only of Markdown punctuation are skipped. Folders
    contribute their *.md files recursively. With -Total, the budget applies to
    the sum of all files, for example a Plan and its detail folder; otherwise it
    applies to each file.

    -Section adds budgets as "Name=words". A name matches a level-two heading
    ("## Name", up to the next level-two heading) or a bold label paragraph
    ("**Name:** ...", up to the next blank line), compared case-insensitively.

    A document may raise its own total budget with one HTML comment:
    <!-- budget: 4000; reason: why this document needs more -->
    The reason is printed for review; an override without a reason is
    reported. With -Total, the first file's override applies.

    An overrun is a warning for the author and reviewer. The exit code stays 0
    unless -Strict is given.

.PARAMETER Path
    One or more Markdown files or folders; commas also separate entries.

.PARAMETER MaxWords
    The default total budget.

.PARAMETER Section
    Optional section budgets, each "Name=words".

.PARAMETER Total
    Apply the budget to the sum of all files instead of each file.

.PARAMETER Strict
    Exit with code 1 when any budget is exceeded.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/Test-DocBudget.ps1 -Path docs/feature-map.md -MaxWords 1500

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/Test-DocBudget.ps1 -Path docs/features/F10-login.md,docs/features/F10-login -MaxWords 2500 -Total -Section "Current position=100","Validation=600"

.NOTES
    Version: 1.0.0
    Output: "ok|OVER words/budget target" per file (or one total line), then
    "OVER words/budget section 'Name' in file" and "override ..." lines.
    Exit codes: 0 done (overruns are warnings), 1 overrun with -Strict,
    2 missing path or invalid argument.
    Runs in Windows PowerShell 5.1 and pwsh 7 without modules.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string[]]$Path,

    [Parameter(Mandatory)]
    [int]$MaxWords,

    [string[]]$Section = @(),

    [switch]$Total,

    [switch]$Strict
)

$ErrorActionPreference = 'Stop'

$cjkPattern = '[\p{IsCJKUnifiedIdeographsExtensionA}\p{IsCJKUnifiedIdeographs}\p{IsCJKCompatibilityIdeographs}]'
$overridePattern = '<!--\s*budget:\s*(\d+)\s*(?:;\s*reason:\s*(.*?))?\s*-->'

function Measure-Word([string]$Text) {
    $cjk = [regex]::Matches($Text, $cjkPattern).Count
    $rest = [regex]::Replace($Text, $cjkPattern, ' ')
    $tokens = @([regex]::Matches($rest, '\S+') | Where-Object { $_.Value -notmatch '^[|:\-#*>`]+$' })
    return $cjk + $tokens.Count
}

function Get-SectionText([string]$Text, [string]$Name) {
    $escaped = [regex]::Escape($Name)
    $heading = [regex]::Match($Text, '(?ims)^##[ \t]+' + $escaped + '[ \t]*\r?$(.*?)(?=^##[ \t]|\z)')
    if ($heading.Success) {
        return $heading.Groups[1].Value
    }
    $label = [regex]::Match($Text, '(?ims)^\*\*' + $escaped + '\s*:\*\*(.*?)(?=^\s*$|\z)')
    if ($label.Success) {
        return $label.Groups[1].Value
    }
    return $null
}

# powershell -File passes "a","b" as one comma-joined string, so split both lists.
$Path = @($Path | ForEach-Object { $_ -split ',' } | Where-Object { $_ })
$Section = @($Section | ForEach-Object { $_ -split ',' } | Where-Object { $_ })

$sectionBudgets = @()
foreach ($entry in $Section) {
    if ($entry -notmatch '^\s*(.+?)\s*=\s*(\d+)\s*$') {
        Write-Output "invalid -Section value '$entry'; expected Name=words"
        exit 2
    }
    $sectionBudgets += [pscustomobject]@{ Name = $Matches[1]; Words = [int]$Matches[2] }
}

$files = @()
foreach ($item in $Path) {
    $full = [IO.Path]::GetFullPath([IO.Path]::Combine((Get-Location).ProviderPath, $item))
    if ([IO.Directory]::Exists($full)) {
        $files += @(Get-ChildItem -LiteralPath $full -Filter '*.md' -File -Recurse | Sort-Object FullName | ForEach-Object { $_.FullName })
    }
    elseif ([IO.File]::Exists($full)) {
        $files += $full
    }
    else {
        Write-Output "missing path: $item"
        exit 2
    }
}

$over = $false
$sum = 0
$totalBudget = $MaxWords
$first = $true
foreach ($file in $files) {
    $text = [IO.File]::ReadAllText($file, [Text.Encoding]::UTF8)
    $relative = Resolve-Path -LiteralPath $file -Relative
    $words = Measure-Word $text
    $sum += $words

    $budget = $MaxWords
    $override = [regex]::Match($text, $overridePattern)
    if ($override.Success) {
        $budget = [int]$override.Groups[1].Value
        $reason = $override.Groups[2].Value.Trim()
        if ($reason) {
            Write-Output "override $budget in ${relative}: $reason"
        }
        else {
            Write-Output "override $budget in $relative has no reason"
        }
    }
    if ($first) {
        $totalBudget = $budget
        $first = $false
    }

    if (-not $Total) {
        $state = if ($words -le $budget) { 'ok' } else { $over = $true; 'OVER' }
        Write-Output ("{0,-4} {1}/{2} {3}" -f $state, $words, $budget, $relative)
    }

    foreach ($sectionBudget in $sectionBudgets) {
        $sectionText = Get-SectionText $text $sectionBudget.Name
        if ($null -eq $sectionText) {
            continue
        }
        $sectionWords = Measure-Word $sectionText
        if ($sectionWords -gt $sectionBudget.Words) {
            $over = $true
            Write-Output ("OVER {0}/{1} section '{2}' in {3}" -f $sectionWords, $sectionBudget.Words, $sectionBudget.Name, $relative)
        }
    }
}

if ($Total) {
    $state = if ($sum -le $totalBudget) { 'ok' } else { $over = $true; 'OVER' }
    Write-Output ("{0,-4} {1}/{2} total of {3} file(s)" -f $state, $sum, $totalBudget, $files.Count)
}

if ($over -and $Strict) {
    exit 1
}
exit 0
