<#
.SYNOPSIS
    Reports broken local links in Markdown and HTML files and broken route
    cells in AGENTS.md tables. Read-only.

.DESCRIPTION
    Inside a Git work tree, scans the files below -Path that Git lists as
    tracked or untracked and not ignored. Outside Git, walks every file below
    -Path, skipping node_modules, bin, obj, and .git.
    Markdown: inline links, images, and reference definitions outside fenced
    and inline code, including heading and explicit <a id>/<a name> anchors.
    A whole destination <name> with no dot and no slash is a template
    placeholder and is skipped. AGENTS.md: path-like backtick spans in table
    cells, resolved from that file's folder; spans starting with / are URL
    paths and are skipped. HTML: literal href and src values; a leading /
    resolves from the HTML file's folder; fragments are not checked.

.PARAMETER Path
    Folder to scan. Defaults to the current folder. A leading / in a Markdown
    link resolves from this folder.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/Test-DocLinks.ps1

.EXAMPLE
    pwsh -File scripts/Test-DocLinks.ps1 -Path docs

.NOTES
    Version: 1.0.0
    Output: one line per broken link, "file:line -> target (reason)", then a
    count line. Exit codes: 0 no broken link, 1 broken links, 2 missing path.
    Runs in Windows PowerShell 5.1 and pwsh 7 without modules.
#>
[CmdletBinding()]
param(
    [string]$Path = '.'
)

$ErrorActionPreference = 'Stop'

$skipFolders = @('node_modules', 'bin', 'obj', '.git')
$anchorCache = @{}

$rootPath = [IO.Path]::GetFullPath([IO.Path]::Combine((Get-Location).ProviderPath, $Path))
if (-not [IO.Directory]::Exists($rootPath)) {
    [Console]::Error.WriteLine("Path not found: $Path")
    exit 2
}
$rootPrefix = $rootPath
if (-not $rootPrefix.EndsWith([string][IO.Path]::DirectorySeparatorChar)) {
    $rootPrefix += [IO.Path]::DirectorySeparatorChar
}

function Test-DocFile([string]$File) {
    $extension = [IO.Path]::GetExtension($File).ToLowerInvariant()
    return ($extension -eq '.md' -or $extension -eq '.html' -or $extension -eq '.htm')
}

function Get-DocFiles([string]$Folder) {
    foreach ($file in [IO.Directory]::GetFiles($Folder)) {
        if (Test-DocFile $file) {
            $file
        }
    }
    foreach ($directory in [IO.Directory]::GetDirectories($Folder)) {
        if ($skipFolders -notcontains [IO.Path]::GetFileName($directory)) {
            Get-DocFiles $directory
        }
    }
}

function Get-GitDocFiles([string]$Folder) {
    # Returns $null outside a Git work tree, so the caller falls back to the folder walk.
    $previousPreference = $ErrorActionPreference
    $previousEncoding = $null
    $ErrorActionPreference = 'Continue'
    try {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            return $null
        }
        $inside = & git -C $Folder rev-parse --is-inside-work-tree 2>$null
        if ($LASTEXITCODE -ne 0 -or "$inside".Trim() -ne 'true') {
            return $null
        }
        # Git writes UTF-8 paths; Windows PowerShell 5.1 decodes native output with the console encoding.
        try {
            $previousEncoding = [Console]::OutputEncoding
            [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
        }
        catch {
            $previousEncoding = $null
        }
        $listing = & git -C $Folder ls-files -z --cached --others --exclude-standard 2>$null
        if ($LASTEXITCODE -ne 0) {
            return $null
        }
        $files = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        foreach ($relative in (@($listing) -join "`n").Split([char]0)) {
            if ($relative -eq '') {
                continue
            }
            $full = [IO.Path]::GetFullPath([IO.Path]::Combine($Folder, $relative))
            if ((Test-DocFile $full) -and [IO.File]::Exists($full)) {
                $null = $files.Add($full)
            }
        }
        return , ([string[]]@($files))
    }
    finally {
        if ($null -ne $previousEncoding) {
            try {
                [Console]::OutputEncoding = $previousEncoding
            }
            catch {
            }
        }
        $ErrorActionPreference = $previousPreference
    }
}

function Read-Lines([string]$File) {
    # Explicit UTF-8: Windows PowerShell 5.1 Get-Content defaults to ANSI.
    $text = [IO.File]::ReadAllText($File, [Text.Encoding]::UTF8)
    return , ([string[]]($text -split '\r?\n'))
}

function Get-CodeMask([string[]]$Lines) {
    # Marks fence lines and the lines between them, which hold no links.
    $mask = New-Object bool[] $Lines.Count
    $fenceChar = $null
    $fenceLength = 0
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        $match = [regex]::Match($Lines[$i], '^\s*(`{3,}|~{3,})(.*)$')
        if ($null -eq $fenceChar) {
            if ($match.Success -and -not ($match.Groups[1].Value[0] -eq '`' -and $match.Groups[2].Value.Contains('`'))) {
                $fenceChar = $match.Groups[1].Value[0]
                $fenceLength = $match.Groups[1].Value.Length
                $mask[$i] = $true
            }
        }
        else {
            $mask[$i] = $true
            if ($match.Success -and $match.Groups[1].Value[0] -eq $fenceChar -and
                $match.Groups[1].Value.Length -ge $fenceLength -and $match.Groups[2].Value.Trim() -eq '') {
                $fenceChar = $null
            }
        }
    }
    return , $mask
}

function Get-Slug([string]$Text) {
    # GitHub style: rendered text, lowercase, keep letters, digits, spaces, - and _.
    $slug = [regex]::Replace($Text, '<[^>]*>', '')
    $slug = [regex]::Replace($slug, '!?\[([^\]]*)\]\([^)]*\)', '$1')
    $slug = $slug.ToLowerInvariant()
    $slug = [regex]::Replace($slug, '[^\p{L}\p{M}\p{N} _-]', '')
    return $slug.Replace(' ', '-')
}

function Get-Anchors([string]$File) {
    if ($anchorCache.ContainsKey($File)) {
        return , $anchorCache[$File]
    }
    $anchors = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $counts = @{}
    $lines = Read-Lines $File
    $mask = Get-CodeMask $lines
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($mask[$i]) {
            continue
        }
        $heading = [regex]::Match($lines[$i], '^\s{0,3}#{1,6}\s+(.*?)(?:\s+#+)?\s*$')
        if ($heading.Success) {
            $slug = Get-Slug $heading.Groups[1].Value
            # Repeated headings get -1, -2, ... in document order.
            if ($counts.ContainsKey($slug)) {
                $counts[$slug]++
                $null = $anchors.Add("$slug-$($counts[$slug])")
            }
            else {
                $counts[$slug] = 0
                $null = $anchors.Add($slug)
            }
        }
        foreach ($explicit in [regex]::Matches($lines[$i], '<a\s[^>]*?\b(?:id|name)\s*=\s*["'']([^"'']+)["'']', 'IgnoreCase')) {
            $null = $anchors.Add($explicit.Groups[1].Value)
        }
    }
    $anchorCache[$File] = $anchors
    return , $anchors
}

function Test-Target([string]$SourceFile, [string]$Target, [bool]$Decode, [bool]$CheckAnchor, [string]$RootFolder) {
    # Returns the broken-link reason, or $null when the target resolves.
    # A leading / resolves from $RootFolder.
    $pathPart = $Target
    $fragment = ''
    $hashIndex = $pathPart.IndexOf('#')
    if ($hashIndex -ge 0) {
        $fragment = $pathPart.Substring($hashIndex + 1)
        $pathPart = $pathPart.Substring(0, $hashIndex)
    }
    $queryIndex = $pathPart.IndexOf('?')
    if ($queryIndex -ge 0) {
        $pathPart = $pathPart.Substring(0, $queryIndex)
    }
    if ($Decode) {
        $pathPart = [Uri]::UnescapeDataString($pathPart)
        $fragment = [Uri]::UnescapeDataString($fragment)
    }

    if ($pathPart -eq '') {
        $resolved = $SourceFile
    }
    else {
        if ($pathPart.StartsWith('/') -or $pathPart.StartsWith('\')) {
            $baseFolder = $RootFolder
            $relative = $pathPart.TrimStart([char[]]@('/', '\'))
        }
        else {
            $baseFolder = [IO.Path]::GetDirectoryName($SourceFile)
            $relative = $pathPart
        }
        try {
            $resolved = [IO.Path]::GetFullPath([IO.Path]::Combine($baseFolder, $relative))
        }
        catch {
            return 'missing file'
        }
        if ($pathPart.EndsWith('/') -or $pathPart.EndsWith('\')) {
            if ([IO.Directory]::Exists($resolved)) {
                return $null
            }
            return 'missing folder'
        }
        if ([IO.Directory]::Exists($resolved)) {
            return $null
        }
        if (-not [IO.File]::Exists($resolved)) {
            return 'missing file'
        }
    }

    if ($CheckAnchor -and $fragment -ne '' -and [IO.Path]::GetExtension($resolved) -eq '.md') {
        $anchors = Get-Anchors $resolved
        if (-not $anchors.Contains($fragment)) {
            return 'missing anchor'
        }
    }
    return $null
}

function Get-MarkdownDestinations([string]$Line) {
    # Returns raw destinations of inline links, images, and reference definitions.
    $scan = [regex]::Replace($Line, '(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)', ' ')
    $definition = [regex]::Match($scan, '^\s{0,3}\[([^\]]+)\]:\s*(<[^>]*>|\S+)')
    if ($definition.Success -and -not $definition.Groups[1].Value.StartsWith('^')) {
        $definition.Groups[2].Value
    }
    $position = 0
    while (($index = $scan.IndexOf('](', $position)) -ge 0) {
        $start = $index + 2
        while ($start -lt $scan.Length -and $scan[$start] -eq ' ') {
            $start++
        }
        if ($start -lt $scan.Length -and $scan[$start] -eq '<') {
            $end = $scan.IndexOf('>', $start)
            if ($end -lt 0) {
                $position = $start
                continue
            }
            $scan.Substring($start, $end - $start + 1)
            $position = $end + 1
        }
        else {
            # Unbracketed destination: ends at whitespace or an unbalanced ')'.
            $depth = 0
            $end = $start
            while ($end -lt $scan.Length) {
                $char = $scan[$end]
                if ($char -eq ' ' -or $char -eq "`t") {
                    break
                }
                if ($char -eq '(') {
                    $depth++
                }
                elseif ($char -eq ')') {
                    if ($depth -eq 0) {
                        break
                    }
                    $depth--
                }
                $end++
            }
            if ($end -gt $start) {
                $scan.Substring($start, $end - $start)
            }
            $position = $end
        }
    }
}

function Test-RouteCandidate([string]$Span) {
    # A span such as /api/v1 is a URL path, not a repository route.
    if ($Span.StartsWith('/') -or $Span -match '[<>{*]' -or $Span.Contains('://')) {
        return $false
    }
    $endsWithMarkdown = $Span.EndsWith('.md', [StringComparison]::OrdinalIgnoreCase)
    if (-not ($Span -match '[/\\]' -or $endsWithMarkdown)) {
        return $false
    }
    # A span with a space is a command unless its first word is a path.
    if ($Span.Contains(' ') -and -not ($Span.Split(' ')[0] -match '[/\\]' -or $endsWithMarkdown)) {
        return $false
    }
    return $true
}

function Test-External([string]$Target) {
    return ($Target.StartsWith('//') -or $Target -match '^[A-Za-z][A-Za-z0-9+.-]*:')
}

$broken = New-Object System.Collections.Generic.List[string]

$gitFiles = Get-GitDocFiles $rootPath
if ($null -ne $gitFiles) {
    [string[]]$files = $gitFiles
}
else {
    [string[]]$files = @(Get-DocFiles $rootPath)
}
[string[]]$relativePaths = @($files | ForEach-Object { $_.Substring($rootPrefix.Length).Replace('\', '/') })
[Array]::Sort($relativePaths, $files, [StringComparer]::Ordinal)

for ($f = 0; $f -lt $files.Count; $f++) {
    $file = $files[$f]
    $relativePath = $relativePaths[$f]
    $lines = Read-Lines $file
    $extension = [IO.Path]::GetExtension($file).ToLowerInvariant()

    if ($extension -eq '.md') {
        $mask = Get-CodeMask $lines
        $isAgents = [IO.Path]::GetFileName($file) -eq 'AGENTS.md'
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($mask[$i]) {
                continue
            }
            $line = $lines[$i]
            foreach ($destination in @(Get-MarkdownDestinations $line)) {
                $target = $destination
                if ($target.StartsWith('<') -and $target.EndsWith('>')) {
                    $target = $target.Substring(1, $target.Length - 2)
                    # A placeholder such as <architecture-path> has no dot and no slash.
                    if ($target -notmatch '[./\\]') {
                        continue
                    }
                }
                if ($target -eq '' -or (Test-External $target)) {
                    continue
                }
                $reason = Test-Target $file $target $true $true $rootPath
                if ($null -ne $reason) {
                    $broken.Add("${relativePath}:$($i + 1) -> $target ($reason)")
                }
            }
            if ($isAgents -and $line.TrimStart().StartsWith('|') -and $line -notmatch '^\s*\|[\s:|-]*-[\s:|-]*$') {
                foreach ($span in [regex]::Matches($line, '`([^`]+)`')) {
                    $route = $span.Groups[1].Value
                    if (Test-RouteCandidate $route) {
                        $reason = Test-Target $file $route $false $false $rootPath
                        if ($null -ne $reason) {
                            $broken.Add("${relativePath}:$($i + 1) -> $route ($reason)")
                        }
                    }
                }
            }
        }
    }
    else {
        for ($i = 0; $i -lt $lines.Count; $i++) {
            foreach ($attribute in [regex]::Matches($lines[$i], '(?<![\w-])(?:href|src)\s*=\s*(["''])(.*?)\1', 'IgnoreCase')) {
                $target = $attribute.Groups[2].Value
                if ($target -eq '' -or $target.StartsWith('#') -or $target.Contains('{') -or
                    $target.Contains('$') -or (Test-External $target)) {
                    continue
                }
                # A leading / in a built or Vite page resolves from that page's folder.
                $reason = Test-Target $file $target $true $false ([IO.Path]::GetDirectoryName($file))
                if ($null -ne $reason) {
                    $broken.Add("${relativePath}:$($i + 1) -> $target ($reason)")
                }
            }
        }
    }
}

foreach ($entry in $broken) {
    Write-Output $entry
}
Write-Output "Broken links: $($broken.Count)"
if ($broken.Count -gt 0) {
    exit 1
}
exit 0
