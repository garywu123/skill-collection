<#
.SYNOPSIS
    Checks simplification review documents against their word budgets.

.DESCRIPTION
    A file whose name starts with "00." is a review plan (1,000 words). Any other
    file is a batch findings document (2,000 words), and each of its level-three
    sections is an item (150 words). Words are whitespace-separated tokens; each
    CJK character counts as one word. Exits with code 1 when any budget is exceeded.

.PARAMETER Path
    A Markdown file, or a folder whose *.md files are checked (not recursive).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File Measure-ReviewDoc.ps1 -Path ../project/docs/reviews
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Path
)

$PlanBudget = 1000
$BatchBudget = 2000
$ItemBudget = 150
$CjkPattern = '[\p{IsCJKUnifiedIdeographsExtensionA}\p{IsCJKUnifiedIdeographs}\p{IsCJKCompatibilityIdeographs}]'

function Measure-Word {
    param([string]$Text)

    $cjk = [regex]::Matches($Text, $CjkPattern).Count
    $rest = [regex]::Replace($Text, $CjkPattern, ' ')
    $tokens = [regex]::Matches($rest, '\S+') | Where-Object { $_.Value -notmatch '^[|:\-#*>`]+$' }
    return $cjk + @($tokens).Count
}

$files = if (Test-Path -LiteralPath $Path -PathType Container) {
    Get-ChildItem -LiteralPath $Path -Filter '*.md' -File
} else {
    Get-Item -LiteralPath $Path
}

$failed = $false
foreach ($file in $files) {
    $text = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $isPlan = $file.Name.StartsWith('00.')
    $budget = if ($isPlan) { $PlanBudget } else { $BatchBudget }
    $words = Measure-Word $text
    $state = if ($words -le $budget) { 'ok' } else { $failed = $true; 'OVER' }
    Write-Output ("{0,-5} {1,6}/{2} {3}" -f $state, $words, $budget, $file.Name)

    if ($isPlan) { continue }

    # Each level-three section of a findings document is one item.
    $sections = [regex]::Split($text, '(?m)^(?=### )') | Where-Object { $_.StartsWith('### ') }
    foreach ($section in $sections) {
        $itemWords = Measure-Word $section
        if ($itemWords -gt $ItemBudget) {
            $failed = $true
            $title = ($section -split "`n")[0].Trim()
            Write-Output ("OVER  {0,6}/{1}   {2}" -f $itemWords, $ItemBudget, $title)
        }
    }
}

if ($failed) { exit 1 }
