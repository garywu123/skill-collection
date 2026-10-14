<#
.SYNOPSIS
    Tests Test-DocLinks.ps1 against a temporary fixture under Windows
    PowerShell and, when installed, pwsh.

.DESCRIPTION
    Builds the fixture at run time, so no committed file holds broken links.
    Compares exit codes and exact output lines, deletes the fixture, and exits
    0 on pass and 1 on failure.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File skills/coding/15.coding-agent-instructions/scripts/tests/Invoke-DocLinksTests.ps1
#>
$ErrorActionPreference = 'Continue'

$checker = Join-Path (Split-Path -Parent $PSScriptRoot) 'Test-DocLinks.ps1'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('DocLinksTest-' + [guid]::NewGuid().ToString('N'))
$gitFixture = Join-Path ([IO.Path]::GetTempPath()) ('DocLinksGitTest-' + [guid]::NewGuid().ToString('N'))
$utf8 = New-Object System.Text.UTF8Encoding($false)
$failures = 0

# Keep Git discovery inside the temp folder, so the plain fixture always uses the folder walk.
$env:GIT_CEILING_DIRECTORIES = [IO.Path]::GetTempPath().TrimEnd([char[]]@('\', '/'))

function Write-Fixture([string]$RelativePath, [string[]]$Lines, [string]$Root = $fixture) {
    $full = Join-Path $Root $RelativePath
    $folder = Split-Path -Parent $full
    if (-not (Test-Path -LiteralPath $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
    }
    [IO.File]::WriteAllText($full, (($Lines -join "`n") + "`n"), $utf8)
}

function Invoke-Checker([string]$Shell, [string]$Target) {
    $output = & $Shell -NoProfile -ExecutionPolicy Bypass -File $checker -Path $Target
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Lines = @($output | Where-Object { $null -ne $_ })
    }
}

function Assert-Run([string]$Name, $Result, [int]$ExitCode, [string[]]$Lines) {
    $actual = $Result.Lines -join "`n"
    $expected = $Lines -join "`n"
    if ($Result.ExitCode -eq $ExitCode -and ($null -eq $Lines -or $actual -ceq $expected)) {
        Write-Output "PASS $Name"
        return
    }
    $script:failures++
    Write-Output "FAIL $Name (exit $($Result.ExitCode), expected $ExitCode)"
    if ($null -ne $Lines) {
        Write-Output '  expected:'
        $Lines | ForEach-Object { Write-Output "    $_" }
        Write-Output '  actual:'
        $Result.Lines | ForEach-Object { Write-Output "    $_" }
    }
}

# Chinese heading built from code points, so this file stays ASCII for Windows PowerShell 5.1.
$chinese = [string][char]0x4E2D + [char]0x6587
$title = [string][char]0x6807 + [char]0x9898

try {
    Write-Fixture 'index.md' @(
        '# Intro',
        '',
        '[a](b.md) [a](my%20file.md) [f](docs/)',
        '[a](missing.md)',
        ('[i](#intro) [s](b.md#setup) [d](b.md#setup-1) [z](#' + $chinese + '-' + $title + ')'),
        '[n](b.md#nope)',
        '![img](img.png) ![m](missing.png)',
        '[r]: b.md',
        '[g]: gone.md',
        '```',
        '[x](fenced-missing.md)',
        '```',
        '`[y](inline-missing.md)` [h](https://example.com/x.md) [m](mailto:a@b.c)',
        '[p](<architecture-path>) [q](<root-code-style-path>) [w](<my file.md>)',
        '[v](<missing.md>)',
        '[o](nofolder/)',
        '',
        ('## ' + $chinese + ' ' + $title)
    )
    Write-Fixture 'b.md' @('# B', '', '## Setup', '', 'one', '', '## Setup', '', 'two')
    Write-Fixture 'my file.md' @('# My File')
    Write-Fixture 'docs/b.md' @('# Docs B')
    [IO.File]::WriteAllBytes((Join-Path $fixture 'img.png'), [byte[]](1, 2, 3))
    Write-Fixture 'page.html' @(
        '<html><body>',
        '<a href="b.md">ok</a> <img src="img.png">',
        '<a href="https://example.com/">x</a>',
        '<a href="gone.html">x</a>',
        '<img src="gone.png">',
        '</body></html>'
    )
    Write-Fixture 'AGENTS.md' @(
        '# Agents',
        '',
        '| Need | Read |',
        '|---|---|',
        '| Doc | `docs/b.md` |',
        '| Placeholder | `<path>` |',
        '| Tool | `Node.js` |',
        '| Test | `dotnet test src/App.Tests` |',
        '| Gone | `docs/gone.md` |',
        '| Guide | `docs/User Guide.md` |'
    )
    Write-Fixture 'sub/AGENTS.md' @('# Sub', '', '| Need | Read |', '|---|---|', '| Doc | `docs/b.md` |')
    Write-Fixture 'sub/docs/b.md' @('# Sub Docs')
    foreach ($skipped in @('node_modules', 'bin', 'obj', '.git')) {
        Write-Fixture "$skipped/x.md" @('[a](nope.md)')
    }
    Write-Fixture 'clean/a.md' @('# Clean', '', '[b](b.md#clean-b) [r](/b.md) [s](#clean)')
    Write-Fixture 'clean/b.md' @('# Clean B')

    $expectedBroken = @(
        'AGENTS.md:9 -> docs/gone.md (missing file)',
        'AGENTS.md:10 -> docs/User Guide.md (missing file)',
        'index.md:4 -> missing.md (missing file)',
        'index.md:6 -> b.md#nope (missing anchor)',
        'index.md:7 -> missing.png (missing file)',
        'index.md:9 -> gone.md (missing file)',
        'index.md:15 -> missing.md (missing file)',
        'index.md:16 -> nofolder/ (missing folder)',
        'page.html:4 -> gone.html (missing file)',
        'page.html:5 -> gone.png (missing file)',
        'Broken links: 10'
    )

    $shells = @()
    foreach ($shell in @('powershell', 'pwsh')) {
        if (Get-Command $shell -ErrorAction SilentlyContinue) {
            $shells += $shell
        }
        else {
            Write-Output "SKIP $shell (not installed, not run)"
        }
    }
    if ($shells.Count -eq 0) {
        Write-Output 'FAIL no PowerShell host found'
        $failures++
    }

    # Git work tree: only tracked and untracked-not-ignored files are scanned; a leading /
    # in HTML resolves from the page's folder; AGENTS.md spans starting with / are URL paths.
    $hasGit = [bool](Get-Command git -ErrorAction SilentlyContinue)
    if ($hasGit) {
        & git init -q $gitFixture
        Write-Fixture '.gitignore' @('dist/', '.cross-agent/') $gitFixture
        Write-Fixture 'index.html' @('<script type="module" src="/src/main.tsx"></script>') $gitFixture
        Write-Fixture 'src/main.tsx' @('export {};') $gitFixture
        Write-Fixture 'site/index.html' @('<link rel="stylesheet" href="/assets/site.css">') $gitFixture
        Write-Fixture 'site/assets/site.css' @('body {}') $gitFixture
        Write-Fixture 'AGENTS.md' @(
            '# Agents',
            '',
            '| Need | Read |',
            '|---|---|',
            '| API | `/api` |',
            '| Capabilities | `/api/v1/capabilities` |',
            '| Gone | `docs/gone.md` |'
        ) $gitFixture
        Write-Fixture 'dist/x.md' @('[a](nope.md)') $gitFixture
        Write-Fixture 'dist/index.html' @('<script src="/assets/gone.js"></script>') $gitFixture
        Write-Fixture '.cross-agent/x.md' @('[a](nope.md)') $gitFixture
    }
    else {
        Write-Output 'SKIP git work tree (git not installed, not run)'
    }
    $expectedGit = @(
        'AGENTS.md:7 -> docs/gone.md (missing file)',
        'Broken links: 1'
    )

    foreach ($shell in $shells) {
        Assert-Run "$shell fixture" (Invoke-Checker $shell $fixture) 1 $expectedBroken
        Assert-Run "$shell clean subset" (Invoke-Checker $shell (Join-Path $fixture 'clean')) 0 @('Broken links: 0')
        Assert-Run "$shell missing path" (Invoke-Checker $shell (Join-Path $fixture 'does-not-exist')) 2 $null
        if ($hasGit) {
            Assert-Run "$shell git work tree" (Invoke-Checker $shell $gitFixture) 1 $expectedGit
        }
    }
}
finally {
    foreach ($folder in @($fixture, $gitFixture)) {
        if (Test-Path -LiteralPath $folder) {
            Remove-Item -LiteralPath $folder -Recurse -Force
        }
    }
}

if ($failures -gt 0) {
    Write-Output "$failures test(s) failed"
    exit 1
}
Write-Output 'All tests passed'
exit 0
