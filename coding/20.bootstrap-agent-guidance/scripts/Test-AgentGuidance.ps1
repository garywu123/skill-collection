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
