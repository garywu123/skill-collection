<#
.SYNOPSIS
    Clone or fast-forward explicitly configured public Skill repositories.

.DESCRIPTION
    Reads external-skills.json, stores each repository in the gitignored cache
    directory, and validates the configured SKILL.md name and optional license.
    Existing repositories must have the configured origin, configured branch,
    and a clean worktree before `git pull --ff-only` is allowed.

    Removed configuration entries leave their cache folders untouched. This
    script never deletes repositories or deployment targets.

.PARAMETER ConfigPath
    External Skill configuration. Defaults to external-skills.json beside this
    script.

.PARAMETER CacheRoot
    Clone cache. Defaults to cache/ beside this script.

.PARAMETER ListOnly
    Validate and display current cache state without clone, fetch, or pull.

.PARAMETER PassThru
    Return resolved Skill objects for Deploy-Skills.ps1.
#>

param(
    [string]$ConfigPath = "",
    [string]$CacheRoot = "",
    [switch]$ListOnly,
    [switch]$PassThru
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $PSScriptRoot 'external-skills.json'
}
if (-not $CacheRoot) {
    $CacheRoot = Join-Path $PSScriptRoot 'cache'
}

if (-not (Test-Path -LiteralPath $ConfigPath -PathType Leaf)) {
    throw "External Skill config is missing: $ConfigPath"
}

$config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $config.PSObject.Properties['schemaVersion'] -or $config.schemaVersion -ne 1) {
    throw "External Skill config must use schemaVersion 1: $ConfigPath"
}
if (-not $config.PSObject.Properties['skills']) {
    throw "External Skill config must contain a 'skills' array: $ConfigPath"
}
$externalMappings = @($config.skills)

if ($externalMappings.Count -gt 0 -and
    (-not $ListOnly -or (Test-Path -LiteralPath $CacheRoot -PathType Container))) {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "git is required to synchronize external Skills."
    }
}

function Test-RepositoryRelativePath {
    param([string]$Path)

    return -not [string]::IsNullOrWhiteSpace($Path) -and
        -not [System.IO.Path]::IsPathRooted($Path) -and
        $Path -notmatch '(^|[\\/])\.\.([\\/]|$)'
}

function Invoke-GitCapture {
    param([string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        # Windows PowerShell 5.1 wraps native stderr as ErrorRecord objects.
        # Git writes normal clone/pull progress there, so judge the native
        # command by its exit code and capture both streams for diagnostics.
        $ErrorActionPreference = 'Continue'
        $commandOutput = @(& git @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($exitCode -ne 0) {
        $detail = ($commandOutput | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
        throw "git $($Arguments -join ' ') failed with exit code $exitCode.$([Environment]::NewLine)$detail"
    }
    return $commandOutput
}

function Write-GitOutput {
    param([object[]]$Output)

    foreach ($line in @($Output)) {
        if (-not [string]::IsNullOrWhiteSpace($line.ToString())) {
            Write-Host "    $line" -ForegroundColor DarkGray
        }
    }
}

$resolvedSkills = @()
$configuredNames = @()

Write-Host ""
Write-Host "External Skills:" -ForegroundColor Cyan

foreach ($mapping in $externalMappings) {
    if (-not $mapping.PSObject.Properties['name'] -or $mapping.name -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
        throw "Every external Skill must have a lowercase kebab-case 'name'."
    }
    if ($mapping.name -in $configuredNames) {
        throw "External Skill config contains duplicate name '$($mapping.name)'."
    }
    $configuredNames += $mapping.name

    if (-not $mapping.PSObject.Properties['repository'] -or [string]::IsNullOrWhiteSpace($mapping.repository)) {
        throw "External Skill '$($mapping.name)' must have a repository URL."
    }
    $repositoryUri = $null
    if (-not [Uri]::TryCreate($mapping.repository, [UriKind]::Absolute, [ref]$repositoryUri) -or $repositoryUri.Scheme -ne 'https') {
        throw "External Skill '$($mapping.name)' repository must be an absolute HTTPS URL."
    }
    if (-not $mapping.PSObject.Properties['branch'] -or
        $mapping.branch -notmatch '^[A-Za-z0-9][A-Za-z0-9._/-]*$' -or
        $mapping.branch -match '\.\.') {
        throw "External Skill '$($mapping.name)' must have a safe branch name."
    }
    if (-not $mapping.PSObject.Properties['skillPath'] -or -not (Test-RepositoryRelativePath $mapping.skillPath)) {
        throw "External Skill '$($mapping.name)' must have a repository-relative skillPath without '..'."
    }

    $licensePath = $null
    if ($mapping.PSObject.Properties['licensePath'] -and -not [string]::IsNullOrWhiteSpace($mapping.licensePath)) {
        if (-not (Test-RepositoryRelativePath $mapping.licensePath)) {
            throw "External Skill '$($mapping.name)' licensePath must be repository-relative without '..'."
        }
        $licensePath = $mapping.licensePath
    }

    $cachePath = Join-Path $CacheRoot $mapping.name
    $available = Test-Path -LiteralPath $cachePath -PathType Container
    $commit = $null

    if (-not $available) {
        if ($ListOnly) {
            Write-Host "  - $($mapping.name): cache missing; run sync or deployment to clone" -ForegroundColor DarkYellow
        }
        else {
            if (-not (Test-Path -LiteralPath $CacheRoot -PathType Container)) {
                New-Item -ItemType Directory -Path $CacheRoot -Force | Out-Null
            }
            Write-Host "  - $($mapping.name): cloning $($mapping.repository) [$($mapping.branch)]"
            $cloneOutput = @(Invoke-GitCapture -Arguments @(
                'clone', '--branch', $mapping.branch, '--single-branch', '--',
                $mapping.repository, $cachePath
            ))
            Write-GitOutput -Output $cloneOutput
            $available = $true
        }
    }

    if ($available) {
        if (-not (Test-Path -LiteralPath (Join-Path $cachePath '.git') -PathType Container)) {
            throw "External Skill cache is not a Git repository: $cachePath"
        }

        $safeDirectory = $cachePath.Replace('\', '/')
        $gitRepositoryArgs = @(
            '-c', "safe.directory=$safeDirectory",
            '-c', 'core.excludesFile=',
            '-C', $cachePath
        )

        $origin = (@(Invoke-GitCapture -Arguments @($gitRepositoryArgs + @('remote', 'get-url', 'origin'))) -join '').Trim()
        if ($origin -ne $mapping.repository) {
            throw "External Skill '$($mapping.name)' cache origin '$origin' does not match '$($mapping.repository)'."
        }

        $currentBranch = (@(Invoke-GitCapture -Arguments @($gitRepositoryArgs + @('branch', '--show-current'))) -join '').Trim()
        if ($currentBranch -ne $mapping.branch) {
            throw "External Skill '$($mapping.name)' cache branch '$currentBranch' does not match '$($mapping.branch)'."
        }

        $worktreeStatus = @(
            Invoke-GitCapture -Arguments @($gitRepositoryArgs + @('status', '--porcelain', '--untracked-files=all'))
        )
        if ($worktreeStatus.Count -gt 0) {
            if ($ListOnly) {
                Write-Host "  - $($mapping.name): cache is dirty; update is blocked" -ForegroundColor DarkYellow
            }
            else {
                throw "External Skill '$($mapping.name)' cache has local changes; refusing to pull: $cachePath"
            }
        }
        elseif (-not $ListOnly) {
            Write-Host "  - $($mapping.name): checking for updates"
            $pullOutput = @(Invoke-GitCapture -Arguments @(
                $gitRepositoryArgs + @('pull', '--ff-only', 'origin', $mapping.branch)
            ))
            Write-GitOutput -Output $pullOutput
        }

        $skillDirectory = Join-Path $cachePath $mapping.skillPath
        $skillFile = Join-Path $skillDirectory 'SKILL.md'
        if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
            throw "External Skill '$($mapping.name)' has no SKILL.md at '$($mapping.skillPath)'."
        }

        $frontmatter = Get-Content -LiteralPath $skillFile -Raw -Encoding UTF8
        $nameMatch = [regex]::Match($frontmatter, '(?m)^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$')
        if (-not $nameMatch.Success -or $nameMatch.Groups[1].Value -ne $mapping.name) {
            throw "External Skill '$($mapping.name)' does not match SKILL.md frontmatter at '$($mapping.skillPath)'."
        }

        $licenseSource = $null
        if ($licensePath) {
            $licenseSource = Join-Path $cachePath $licensePath
            if (-not (Test-Path -LiteralPath $licenseSource -PathType Leaf)) {
                throw "External Skill '$($mapping.name)' license file is missing: $licensePath"
            }
        }

        $commit = (@(Invoke-GitCapture -Arguments @($gitRepositoryArgs + @('rev-parse', '--short=12', 'HEAD'))) -join '').Trim()
        if ($ListOnly -and $worktreeStatus.Count -eq 0) {
            Write-Host "  - $($mapping.name): cached at $commit [$($mapping.branch)]" -ForegroundColor Green
        }

        $resolvedSkills += [pscustomobject]@{
            Source        = $skillDirectory
            SourceName    = "$($mapping.name)@$($mapping.branch)"
            DeployName    = $mapping.name
            SourceType    = 'external'
            Available     = $true
            Repository    = $mapping.repository
            Branch        = $mapping.branch
            Commit        = $commit
            LicenseSource = $licenseSource
        }
    }
    else {
        $resolvedSkills += [pscustomobject]@{
            Source        = Join-Path $cachePath $mapping.skillPath
            SourceName    = "$($mapping.name)@$($mapping.branch)"
            DeployName    = $mapping.name
            SourceType    = 'external'
            Available     = $false
            Repository    = $mapping.repository
            Branch        = $mapping.branch
            Commit        = $null
            LicenseSource = $null
        }
    }
}

if ($PassThru) {
    $resolvedSkills
}

Write-Host ""
Write-Host "External Skill sync complete: $($resolvedSkills.Count) configured." -ForegroundColor Yellow
