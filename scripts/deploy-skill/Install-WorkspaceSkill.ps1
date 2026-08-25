<#
.SYNOPSIS
    Install this repository's workspace-only skill into supported project paths.

.DESCRIPTION
    Copies skills/coding/skill-deployment to the project-local discovery paths
    for GitHub Copilot, Claude Code, and Codex / Agents. It does not modify
    user-level skill directories and it installs no globally reusable skills.
#>

param(
    [switch]$ListOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$source = Join-Path $repoRoot 'skills\coding\skill-deployment'
$skillFile = Join-Path $source 'SKILL.md'

if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
    throw "Workspace skill is missing: $skillFile"
}

$targets = [ordered]@{
    'GitHub Copilot' = Join-Path $repoRoot '.github\skills\skill-deployment'
    'Claude Code' = Join-Path $repoRoot '.claude\skills\skill-deployment'
    'Codex / Agents' = Join-Path $repoRoot '.agents\skills\skill-deployment'
}

Write-Host ''
Write-Host 'Workspace-only skill:' -ForegroundColor Cyan
Write-Host "  - skill-deployment <- $source"
Write-Host ''

foreach ($target in $targets.GetEnumerator()) {
    Write-Host "$($target.Key) -> $($target.Value)"
}

if ($ListOnly) {
    Write-Host ''
    Write-Host 'List-only mode: no files were installed.' -ForegroundColor Yellow
    exit 0
}

foreach ($target in $targets.GetEnumerator()) {
    $targetParent = Split-Path -Parent $target.Value
    New-Item -ItemType Directory -Path $targetParent -Force | Out-Null

    if (Test-Path -LiteralPath $target.Value) {
        Remove-Item -LiteralPath $target.Value -Recurse -Force
    }

    Copy-Item -LiteralPath $source -Destination $target.Value -Recurse -Force
    Write-Host "  + $($target.Key)" -ForegroundColor Green
}

Write-Host ''
Write-Host 'Installed workspace-only skill into 3 platform directories.' -ForegroundColor Yellow