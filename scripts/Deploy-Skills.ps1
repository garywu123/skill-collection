<#
.SYNOPSIS
    Deploy all skills in this repository to AI tool skill directories.

.DESCRIPTION
    Scans the repository root for skill folders (any subdirectory containing
    a SKILL.md file) and copies each one to the configured target directories.
    Existing folders at the destination are overwritten (Copy-Item -Force).

    Path resolution order (first non-empty value wins):
      1. Command-line parameter
      2. scripts/deploy-paths.json  (machine-local, gitignored)
      3. $env:USERPROFILE defaults  (~\.copilot\skills, ~\.claude\skills, ~\.agents\skills)

    Copy scripts/deploy-paths.example.json to scripts/deploy-paths.json and
    edit it to override any path for this machine.

.PARAMETER CopilotSkillsPath
    Target directory for GitHub Copilot skills. Overrides config file and default.

.PARAMETER ClaudeSkillsPath
    Target directory for Claude Code skills. Overrides config file and default.

.PARAMETER AgentsSkillsPath
    Target directory for Codex / OpenAI Agents skills. Overrides config file and default.

.PARAMETER Target
    Restrict deployment to a single tool: copilot | claude | agents | all (default).

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
    [ValidateSet("all", "copilot", "claude", "agents")]
    [string]$Target = "all"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Resolve repository root (one level above this script's folder)
# ---------------------------------------------------------------------------
$repoRoot = Split-Path -Parent $PSScriptRoot

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
if (-not $CopilotSkillsPath) { $CopilotSkillsPath = "$env:USERPROFILE\.copilot\skills" }
if (-not $ClaudeSkillsPath)  { $ClaudeSkillsPath  = "$env:USERPROFILE\.claude\skills"  }
if (-not $AgentsSkillsPath)  { $AgentsSkillsPath  = "$env:USERPROFILE\.agents\skills"  }

# ---------------------------------------------------------------------------
# Apply -Target filter (blank out paths not in scope)
# ---------------------------------------------------------------------------
if ($Target -ne "all") {
    if ($Target -ne "copilot") { $CopilotSkillsPath = "" }
    if ($Target -ne "claude")  { $ClaudeSkillsPath  = "" }
    if ($Target -ne "agents")  { $AgentsSkillsPath  = "" }
}

# ---------------------------------------------------------------------------
# Discover skill folders: any subdirectory that contains a SKILL.md
# ---------------------------------------------------------------------------
$skillFolders = Get-ChildItem -Path $repoRoot -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") }

if ($skillFolders.Count -eq 0) {
    Write-Host "No skill folders found (looked for subdirectories containing SKILL.md)." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Skills found:" -ForegroundColor Cyan
$skillFolders | ForEach-Object { Write-Host "  - $($_.Name)" }

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
        $dest = Join-Path $targetRoot $skill.Name
        Copy-Item -Path $skill.FullName -Destination $dest -Recurse -Force
        Write-Host "    + $($skill.Name)" -ForegroundColor Green
        $deployedCount++
    }
}

Write-Host ""
Write-Host "Done. $($skillFolders.Count) skill(s) x $(@($activeTargets).Count) target(s) = $deployedCount deployment(s)." -ForegroundColor Yellow
