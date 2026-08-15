[CmdletBinding()]
param(
    [Parameter()]
    [string]$ProjectRoot = (Get-Location).Path,

    [Parameter()]
    [ValidateRange(1, 1000)]
    [int]$MaxAgentLines = 100,

    [Parameter()]
    [switch]$RequireClaude,

    [Parameter()]
    [switch]$RequireCopilot,

    [Parameter()]
    [switch]$SkipReferencedMarkdown
)

$ErrorActionPreference = 'Stop'
$resolvedRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$errors = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Add-ValidationError {
    param([string]$Message)
    $errors.Add($Message)
}

function Read-RequiredFile {
    param(
        [string]$Path,
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Add-ValidationError "$Label is missing: $Path"
        return $null
    }

    $content = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ([string]::IsNullOrWhiteSpace($content)) {
        Add-ValidationError "$Label is empty: $Path"
    }
    return $content
}

$agentsPath = Join-Path $resolvedRoot 'AGENTS.md'
$agentsContent = Read-RequiredFile -Path $agentsPath -Label 'Canonical AGENTS.md'
$roadmapPath = Join-Path $resolvedRoot 'roadmap.yaml'
$roadmapContent = Read-RequiredFile -Path $roadmapPath -Label 'Project roadmap.yaml'

if ($null -ne $agentsContent) {
    $lineCount = @(Get-Content -LiteralPath $agentsPath -Encoding UTF8).Count
    if ($lineCount -gt $MaxAgentLines) {
        Add-ValidationError "AGENTS.md has $lineCount lines; maximum is $MaxAgentLines."
    }

    $placeholderPattern = '(?im)(\bTODO\b|\bTBD\b|\bTBC\b|\[command\]|\[.*?path\]|<[^>]+>)'
    if ($agentsContent -match $placeholderPattern) {
        Add-ValidationError 'AGENTS.md contains placeholder text.'
    }

    if (-not $SkipReferencedMarkdown) {
        $matches = [regex]::Matches($agentsContent, '`([^`\r\n]+\.md)`')
        foreach ($match in $matches) {
            $reference = $match.Groups[1].Value.TrimStart('@')
            if ($reference -match '^(https?://|[A-Za-z]:\\)' -or $reference -match '[*?]') {
                continue
            }

            $candidate = Join-Path $resolvedRoot $reference
            if (-not (Test-Path -LiteralPath $candidate)) {
                Add-ValidationError "Referenced Markdown path does not exist: $reference"
            }
        }
    }

    if ($agentsContent -notmatch '(?i)roadmap\.yaml') {
        Add-ValidationError 'AGENTS.md must route readers to roadmap.yaml.'
    }

    if ($agentsContent -notmatch '(?is)(same turn|before (the )?final response|结束前|同一回合).{0,240}roadmap\.yaml|roadmap\.yaml.{0,240}(same turn|before (the )?final response|结束前|同一回合)') {
        Add-ValidationError 'AGENTS.md must include a roadmap.yaml write-back/reconciliation rule.'
    }
}

if ($null -ne $roadmapContent) {
    foreach ($field in @('project', 'stage', 'docs', 'functions')) {
        if ($roadmapContent -notmatch "(?m)^$([regex]::Escape($field)):\s*") {
            Add-ValidationError "roadmap.yaml is missing top-level field: $field"
        }
    }

    $functionMatches = [regex]::Matches(
        $roadmapContent,
        '(?ms)^\s{2}-\s+id:\s*(F\d{3})\s*$.*?(?=^\s{2}-\s+id:|\z)'
    )
    foreach ($functionMatch in $functionMatches) {
        $functionId = $functionMatch.Groups[1].Value
        $block = $functionMatch.Value
        if ($block -notmatch '(?m)^\s{4}domain:\s*[a-z0-9]+(?:-[a-z0-9]+)*\s*$') {
            Add-ValidationError "Function $functionId is missing a valid domain key."
        }

        $statusMatch = [regex]::Match($block, '(?m)^\s{4}status:\s*([a-z-]+)\s*$')
        if ($statusMatch.Success -and $statusMatch.Groups[1].Value -in @('implementing', 'verifying', 'accepted')) {
            if ($block -notmatch '(?m)^\s{4}plan:\s*\S+\s*$') {
                Add-ValidationError "Function $functionId at $($statusMatch.Groups[1].Value) is missing plan."
            }
            if ($block -notmatch '(?m)^\s{4}checklist:\s*\S+\s*$') {
                Add-ValidationError "Function $functionId at $($statusMatch.Groups[1].Value) is missing checklist."
            }
        }
    }
}

if ($RequireClaude) {
    $claudePath = Join-Path $resolvedRoot 'CLAUDE.md'
    $claudeContent = Read-RequiredFile -Path $claudePath -Label 'Claude wrapper'
    if ($null -ne $claudeContent -and $claudeContent -notmatch '(?m)^\s*@AGENTS\.md\s*$') {
        Add-ValidationError 'CLAUDE.md must import @AGENTS.md on its own line.'
    }
}

if ($RequireCopilot) {
    $copilotPath = Join-Path $resolvedRoot '.github\copilot-instructions.md'
    $copilotContent = Read-RequiredFile -Path $copilotPath -Label 'Copilot instructions'
    if ($null -ne $copilotContent -and $copilotContent -notmatch 'AGENTS\.md') {
        Add-ValidationError 'Copilot instructions must identify AGENTS.md as canonical guidance.'
    }
}

if ($null -ne $agentsContent -and $agentsContent -notmatch '(?i)(source|truth|authoritative|precedence|权威|优先级)') {
    $warnings.Add('AGENTS.md does not appear to state source precedence.')
}

[pscustomobject]@{
    ProjectRoot = $resolvedRoot
    Passed = ($errors.Count -eq 0)
    ErrorCount = $errors.Count
    WarningCount = $warnings.Count
    Errors = @($errors)
    Warnings = @($warnings)
}

if ($errors.Count -gt 0) {
    exit 1
}
