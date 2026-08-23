<#
.SYNOPSIS
    Deploy all skills in this repository to AI tool skill directories.

.DESCRIPTION
    Reads an explicit source-to-name mapping from scripts/deploy-skills.json
    and copies those skills to the configured target directories. Existing
    folders managed by this script are replaced.

    The deployed folder name comes from the SKILL.md frontmatter `name` field,
    so repository ordering prefixes are not copied
    (`10.product-brief` -> `product-brief`).

    Path resolution order (first non-empty value wins):
      1. Command-line parameter
      2. scripts/deploy-paths.json  (machine-local, gitignored)
      3. $env:USERPROFILE defaults  (~\.copilot\skills, ~\.claude\skills, ~\.agents\skills)

    Copy scripts/deploy-paths.example.json to scripts/deploy-paths.json and
    edit it to override any path for this machine. Copy
    scripts/deploy-skills.example.json to scripts/deploy-skills.json and edit
    the explicit deployment set. Both real config files are machine-local and
    gitignored.

.PARAMETER SkillConfigPath
    Path to the explicit skill deployment mapping. Defaults to
    scripts/deploy-skills.json.

.PARAMETER CopilotSkillsPath
    Target directory for GitHub Copilot skills. Overrides config file and default.

.PARAMETER ClaudeSkillsPath
    Target directory for Claude Code skills. Overrides config file and default.

.PARAMETER AgentsSkillsPath
    Target directory for Codex / OpenAI Agents skills. Overrides config file and default.

.PARAMETER Target
    Restrict deployment to a single tool: copilot | claude | agents | all (default).

.PARAMETER ListOnly
    List active skill folders without writing to any deployment target.

.EXAMPLE
    # Use config file / defaults — deploy to all tools
    .\Deploy-Skills.ps1

.EXAMPLE
    # Deploy to GitHub Copilot only
    .\Deploy-Skills.ps1 -Target copilot

.EXAMPLE
    # Override a single path on the command line
    .\Deploy-Skills.ps1 -CopilotSkillsPath "D:\my-skills\copilot"
#>

param(
    [string]$CopilotSkillsPath = "",
    [string]$ClaudeSkillsPath  = "",
    [string]$AgentsSkillsPath  = "",
    [string]$SkillConfigPath = "",
    [ValidateSet("all", "copilot", "claude", "agents")]
    [string]$Target = "all",
    [switch]$ListOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Resolve repository root (two levels above scripts/deploy-skill/)
# ---------------------------------------------------------------------------
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# ---------------------------------------------------------------------------
# Load the explicit source-to-deployment-name mapping.
# ---------------------------------------------------------------------------
if (-not $SkillConfigPath) {
    $SkillConfigPath = Join-Path $PSScriptRoot 'deploy-skills.json'
}
if (-not (Test-Path -LiteralPath $SkillConfigPath -PathType Leaf)) {
    throw "Skill deployment config is missing: $SkillConfigPath. Copy deploy-skills.example.json to deploy-skills.json."
}

$skillConfig = Get-Content -LiteralPath $SkillConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $skillConfig.PSObject.Properties['skills'] -or @($skillConfig.skills).Count -eq 0) {
    throw "Skill deployment config must contain a non-empty 'skills' array: $SkillConfigPath"
}

# ---------------------------------------------------------------------------
# Load machine-local path overrides from deploy-paths.json (gitignored).
# Command-line parameters take precedence over the config file.
# ---------------------------------------------------------------------------
$configFile = Join-Path $PSScriptRoot "deploy-paths.json"
if (Test-Path $configFile) {
    Write-Host "Loading paths from $(Split-Path $configFile -Leaf)" -ForegroundColor DarkGray
    $cfg = Get-Content $configFile -Raw | ConvertFrom-Json
    if (-not $CopilotSkillsPath -and $cfg.PSObject.Properties["CopilotSkillsPath"]) { $CopilotSkillsPath = $cfg.CopilotSkillsPath }
    if (-not $ClaudeSkillsPath  -and $cfg.PSObject.Properties["ClaudeSkillsPath"])  { $ClaudeSkillsPath  = $cfg.ClaudeSkillsPath  }
    if (-not $AgentsSkillsPath  -and $cfg.PSObject.Properties["AgentsSkillsPath"])  { $AgentsSkillsPath  = $cfg.AgentsSkillsPath  }
}

# Fall back to standard $env:USERPROFILE locations
$userProfile = $env:USERPROFILE
if (-not $userProfile) {
    $userProfile = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
}
if (-not $userProfile) {
    throw "Unable to resolve the current user's profile directory."
}

if (-not $CopilotSkillsPath) { $CopilotSkillsPath = Join-Path $userProfile '.copilot\skills' }
if (-not $ClaudeSkillsPath)  { $ClaudeSkillsPath  = Join-Path $userProfile '.claude\skills'  }
if (-not $AgentsSkillsPath)  { $AgentsSkillsPath  = Join-Path $userProfile '.agents\skills'  }

# ---------------------------------------------------------------------------
# Apply -Target filter (blank out paths not in scope)
# ---------------------------------------------------------------------------
if ($Target -ne "all") {
    if ($Target -ne "copilot") { $CopilotSkillsPath = "" }
    if ($Target -ne "claude")  { $ClaudeSkillsPath  = "" }
    if ($Target -ne "agents")  { $AgentsSkillsPath  = "" }
}

# ---------------------------------------------------------------------------
# Resolve and validate explicitly configured skill mappings.
# ---------------------------------------------------------------------------
$skillFolders = @()
foreach ($mapping in @($skillConfig.skills)) {
    if (-not $mapping.PSObject.Properties['source'] -or [string]::IsNullOrWhiteSpace($mapping.source)) {
        throw "Every skill mapping must contain a non-empty 'source'."
    }
    if (-not $mapping.PSObject.Properties['name'] -or $mapping.name -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
        throw "Every skill mapping must contain a lowercase kebab-case 'name'. Invalid source: $($mapping.source)"
    }
    if ([System.IO.Path]::IsPathRooted($mapping.source) -or $mapping.source -match '(^|[\\/])\.\.([\\/]|$)') {
        throw "Skill source must be a repository-relative path without '..': $($mapping.source)"
    }

    $source = Join-Path $repoRoot $mapping.source
    if (-not (Test-Path -LiteralPath $source -PathType Container)) {
        throw "Configured skill folder not found: $($mapping.source)"
    }

    $skillFile = Join-Path $source 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
        throw "Configured skill folder has no SKILL.md: $($mapping.source)"
    }

    $frontmatter = Get-Content -LiteralPath $skillFile -Raw -Encoding UTF8
    $nameMatch = [regex]::Match($frontmatter, '(?m)^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$')
    if (-not $nameMatch.Success) {
        throw "SKILL.md has no valid lowercase kebab-case frontmatter name: $skillFile"
    }
    if ($mapping.name -ne $nameMatch.Groups[1].Value) {
        throw "Configured name '$($mapping.name)' does not match SKILL.md name '$($nameMatch.Groups[1].Value)': $($mapping.source)"
    }

    $skillFolders += [pscustomobject]@{
        Source     = $source
        SourceName = Split-Path $source -Leaf
        DeployName = $mapping.name
    }
}

$duplicateSources = @($skillFolders | Group-Object Source | Where-Object Count -gt 1)
if ($duplicateSources.Count -gt 0) {
    $sources = ($duplicateSources.Name | Sort-Object) -join ', '
    throw "Skill deployment config contains duplicate sources: $sources"
}

$duplicateNames = @($skillFolders | Group-Object DeployName | Where-Object Count -gt 1)
if ($duplicateNames.Count -gt 0) {
    $names = ($duplicateNames.Name | Sort-Object) -join ', '
    throw "Multiple source folders resolve to the same deployed skill name: $names"
}

Write-Host ""
Write-Host "Configured skills:" -ForegroundColor Cyan
$skillFolders | ForEach-Object { Write-Host "  - $($_.DeployName) <- $($_.SourceName)" }

# ---------------------------------------------------------------------------
# Build target map (skip empty paths)
# ---------------------------------------------------------------------------
$targets = [ordered]@{
    "GitHub Copilot" = $CopilotSkillsPath
    "Claude Code"    = $ClaudeSkillsPath
    "Codex / Agents" = $AgentsSkillsPath
}

$activeTargets = $targets.GetEnumerator() | Where-Object { $_.Value -ne "" }

if (-not $activeTargets) {
    Write-Host ""
    Write-Host "No target paths provided. Nothing to deploy." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Targets:" -ForegroundColor Cyan
foreach ($entry in $activeTargets) {
    Write-Host "  - $($entry.Key) -> $($entry.Value)"
}

if ($ListOnly) {
    Write-Host ""
    Write-Host "List-only mode: no files were deployed." -ForegroundColor Yellow
    exit 0
}

function Remove-DeployedEntry {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }

    $item = Get-Item -LiteralPath $Path -Force
    $isReparsePoint = ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq [System.IO.FileAttributes]::ReparsePoint
    if ($isReparsePoint) {
        [System.IO.Directory]::Delete($Path, $false)
    }
    else {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    return $true
}

# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------
$deployedCount = 0

foreach ($entry in $activeTargets) {
    $toolName   = $entry.Key
    $targetRoot = $entry.Value

    Write-Host ""
    Write-Host "=== $toolName ===" -ForegroundColor Cyan
    Write-Host "    $targetRoot"

    if (-not (Test-Path $targetRoot)) {
        Write-Host "    Creating target directory..." -ForegroundColor DarkGray
        New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
    }

    foreach ($skill in $skillFolders) {
        $dest = Join-Path $targetRoot $skill.DeployName
        Remove-DeployedEntry -Path $dest | Out-Null

        if ($skill.SourceName -ne $skill.DeployName -and $skill.SourceName -match '^\d+[._-]') {
            $legacyDest = Join-Path $targetRoot $skill.SourceName
            if (Remove-DeployedEntry -Path $legacyDest) {
                Write-Host "    - $($skill.SourceName) (legacy name)" -ForegroundColor DarkYellow
            }
        }

        Copy-Item -LiteralPath $skill.Source -Destination $dest -Recurse -Force
        Write-Host "    + $($skill.DeployName)" -ForegroundColor Green
        $deployedCount++
    }
}

Write-Host ""
Write-Host "Done. $($skillFolders.Count) skill(s) x $(@($activeTargets).Count) target(s) = $deployedCount deployment(s)." -ForegroundColor Yellow
