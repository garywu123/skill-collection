<#
.SYNOPSIS
    Install skills from this collection into one project's agent skill directory.

.DESCRIPTION
    Project-scoped counterpart to Deploy-Skills.ps1 (which installs
    machine-wide under $env:USERPROFILE).

    Two modes:

      Link (default)  Create a directory junction from the project into this
                      repository. One source of truth: `git pull` here updates
                      every linked project at once. Nothing is duplicated, and
                      the link must not be committed.

      Copy            Copy the folders in. The project becomes self-contained
                      and the skills can be committed and pinned, at the cost
                      of a copy that no longer tracks this repository.

    Numeric ordering prefixes are stripped on install, so the installed folder
    name matches the `name:` field in each SKILL.md
    (`10.product-brief` -> `product-brief`).

    Presets and per-tool target directories are defined in skill-presets.json.

.PARAMETER ProjectPath
    Project root to install into. Defaults to the current directory.

.PARAMETER Preset
    Named skill set from skill-presets.json. Defaults to "coding".

.PARAMETER Skill
    Explicit repo-relative skill folders, overriding -Preset.

.PARAMETER Mode
    Link (default) or Copy.

.PARAMETER Tool
    claude (default), copilot, agents, or all.

.PARAMETER List
    Show what would be installed and exit.

.PARAMETER Uninstall
    Remove previously installed skills of the selected set instead of installing.

.EXAMPLE
    # Link the coding preset into the current project
    d:\code\personal-projects\skill-collection\scripts\Install-Skills.ps1

.EXAMPLE
    # Copy a pinned, committable set into a specific project
    .\Install-Skills.ps1 -ProjectPath D:\code\work-projects\wms -Mode Copy

.EXAMPLE
    # Install only the planning skills
    .\Install-Skills.ps1 -Skill skills/coding/10.product-brief,skills/coding/20.feature-map,skills/coding/30.feature-plan

.EXAMPLE
    .\Install-Skills.ps1 -Uninstall
#>

param(
    [string]$ProjectPath = ".",
    [string]$Preset = "coding",
    [string[]]$Skill,
    [ValidateSet("Link", "Copy")]
    [string]$Mode = "Link",
    [ValidateSet("claude", "copilot", "agents", "all")]
    [string]$Tool = "claude",
    [switch]$List,
    [switch]$Uninstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

# ---------------------------------------------------------------------------
# Load presets
# ---------------------------------------------------------------------------
$presetFile = Join-Path $PSScriptRoot "skill-presets.json"
if (-not (Test-Path -LiteralPath $presetFile)) {
    throw "Preset file is missing: $presetFile"
}
$cfg = Get-Content -LiteralPath $presetFile -Raw | ConvertFrom-Json

# ---------------------------------------------------------------------------
# Resolve which skill folders to install
# ---------------------------------------------------------------------------
if ($Skill) {
    $wanted = $Skill
}
else {
    if (-not $cfg.presets.PSObject.Properties[$Preset]) {
        $available = ($cfg.presets.PSObject.Properties.Name) -join ", "
        throw "Unknown preset '$Preset'. Available: $available"
    }
    $wanted = $cfg.presets.$Preset
}

$sources = @()
foreach ($rel in $wanted) {
    $full = Join-Path $repoRoot $rel
    if (-not (Test-Path -LiteralPath $full -PathType Container)) {
        throw "Skill folder not found: $rel"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $full 'SKILL.md') -PathType Leaf)) {
        throw "Not a skill folder (no SKILL.md): $rel"
    }
    # Strip an ordering prefix such as "05." so the folder matches SKILL.md name.
    $leaf = Split-Path $full -Leaf
    $installName = $leaf -replace '^\d+[._-]', ''
    $sources += [pscustomobject]@{
        Source      = $full
        InstallName = $installName
        RepoPath    = $rel
    }
}

# ---------------------------------------------------------------------------
# Resolve project and target directories
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $ProjectPath -PathType Container)) {
    throw "Project path not found: $ProjectPath"
}
$projectRoot = (Resolve-Path -LiteralPath $ProjectPath).Path

if ($projectRoot -eq $repoRoot) {
    throw "Refusing to install the collection into itself."
}

$toolNames = @()
if ($Tool -eq "all") { $toolNames = @($cfg.targets.PSObject.Properties.Name) }
else { $toolNames = @($Tool) }

Write-Host ""
Write-Host "Collection : $repoRoot" -ForegroundColor DarkGray
Write-Host "Project    : $projectRoot" -ForegroundColor DarkGray
if ($Skill) { Write-Host "Skills     : explicit (-Skill)" -ForegroundColor DarkGray }
else { Write-Host "Preset     : $Preset" -ForegroundColor DarkGray }
Write-Host "Mode       : $Mode" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Skills:" -ForegroundColor Cyan
foreach ($s in $sources) { Write-Host "  - $($s.InstallName)   <- $($s.RepoPath)" }

if ($List) {
    Write-Host ""
    Write-Host "Targets:" -ForegroundColor Cyan
    foreach ($t in $toolNames) { Write-Host "  - $t -> $(Join-Path $projectRoot $cfg.targets.$t)" }
    Write-Host ""
    Write-Host "List mode: nothing was written." -ForegroundColor Yellow
    exit 0
}

# ---------------------------------------------------------------------------
# Remove an existing entry safely.
# A junction must be unlinked, never recursed into: Remove-Item -Recurse on a
# reparse point can delete the TARGET contents on Windows PowerShell.
# ---------------------------------------------------------------------------
function Remove-InstalledEntry {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) { return $false }

    $item = Get-Item -LiteralPath $Path -Force
    $isReparse = ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq [System.IO.FileAttributes]::ReparsePoint

    if ($isReparse) {
        [System.IO.Directory]::Delete($Path, $false)
    }
    else {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
    return $true
}

# ---------------------------------------------------------------------------
# Install / uninstall
# ---------------------------------------------------------------------------
$changed = 0

foreach ($t in $toolNames) {
    if (-not $cfg.targets.PSObject.Properties[$t]) {
        Write-Host "  ! no target configured for tool '$t' - skipped" -ForegroundColor Yellow
        continue
    }

    $targetRoot = Join-Path $projectRoot $cfg.targets.$t

    Write-Host ""
    Write-Host "=== $t ===" -ForegroundColor Cyan
    Write-Host "    $targetRoot"

    if ($Uninstall) {
        foreach ($s in $sources) {
            $dest = Join-Path $targetRoot $s.InstallName
            if (Remove-InstalledEntry -Path $dest) {
                Write-Host "    - $($s.InstallName)" -ForegroundColor Yellow
                $changed++
            }
        }
        continue
    }

    if (-not (Test-Path -LiteralPath $targetRoot)) {
        New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
    }

    foreach ($s in $sources) {
        $dest = Join-Path $targetRoot $s.InstallName
        Remove-InstalledEntry -Path $dest | Out-Null

        if ($Mode -eq "Link") {
            New-Item -ItemType Junction -Path $dest -Target $s.Source | Out-Null
            Write-Host "    -> $($s.InstallName)  (junction)" -ForegroundColor Green
        }
        else {
            Copy-Item -LiteralPath $s.Source -Destination $dest -Recurse -Force
            Write-Host "    +  $($s.InstallName)  (copy)" -ForegroundColor Green
        }
        $changed++
    }
}

Write-Host ""
if ($Uninstall) {
    Write-Host "Removed $changed entr(ies)." -ForegroundColor Yellow
    exit 0
}

Write-Host "Installed $changed entr(ies)." -ForegroundColor Yellow

if ($Mode -eq "Link") {
    Write-Host ""
    Write-Host "Junctions must not be committed. Add to the project's .gitignore:" -ForegroundColor Yellow
    foreach ($t in $toolNames) {
        if ($cfg.targets.PSObject.Properties[$t]) { Write-Host "    $($cfg.targets.$t)/" }
    }
}
