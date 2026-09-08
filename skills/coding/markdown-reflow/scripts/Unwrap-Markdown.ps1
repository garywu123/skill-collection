<#
.SYNOPSIS
    Joins hard-wrapped Markdown paragraph lines back into a single line per paragraph.

.DESCRIPTION
    Leaves blank lines, headings, list items, blockquotes, table rows, thematic
    breaks, and fenced code blocks untouched. Within a plain paragraph, lines are
    merged with a single space unless a line ends with an explicit CommonMark
    hard-break marker (two or more trailing spaces, or a trailing backslash), in
    which case the break is preserved.

.PARAMETER Path
    A Markdown file, or a folder to scan recursively for *.md files.

.PARAMETER Preview
    Report which files would change without writing them.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File Unwrap-Markdown.ps1 -Path docs/notes.md -Preview
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [string]$Path,

    [switch]$Preview
)

function Test-SpecialMarkdownLine {
    param([string]$Line)

    if ($Line -match '^\s*$') { return $true }                     # blank line
    if ($Line -match '^\s{0,3}#{1,6}(\s|$)') { return $true }       # ATX heading
    if ($Line -match '^\s{0,3}>') { return $true }                  # blockquote
    if ($Line -match '^\s*([-*+]|\d+[.\)])\s+') { return $true }    # list item
    if ($Line -match '^\s*\|') { return $true }                     # table row
    if ($Line -match '^\s{0,3}([-*_]\s*){3,}$') { return $true }    # thematic break
    if ($Line -match '^\s{0,3}(=+|-+)\s*$') { return $true }        # setext underline
    if ($Line -match '^[ \t]+\S') { return $true }                  # indented continuation (list/code)
    return $false
}

function ConvertTo-UnwrappedMarkdown {
    param([string[]]$Lines)

    $output = [System.Collections.Generic.List[string]]::new()
    $paragraphBuffer = [System.Collections.Generic.List[string]]::new()
    $inCodeBlock = $false

    function Write-ParagraphBuffer {
        if ($paragraphBuffer.Count -eq 0) { return }

        $segment = [System.Collections.Generic.List[string]]::new()
        foreach ($line in $paragraphBuffer) {
            $hardBreak = ($line -match '  +$') -or ($line -match '\\$')
            $trimmed = $line.Trim()
            if ($trimmed.Length -gt 0) { $segment.Add($trimmed) }

            if ($hardBreak) {
                $output.Add((($segment -join ' ') + '  '))
                $segment.Clear()
            }
        }
        if ($segment.Count -gt 0) {
            $output.Add(($segment -join ' '))
        }
        $paragraphBuffer.Clear()
    }

    foreach ($line in $Lines) {
        if ($line -match '^\s{0,3}(`{3,}|~{3,})') {
            Write-ParagraphBuffer
            $output.Add($line)
            $inCodeBlock = -not $inCodeBlock
            continue
        }
        if ($inCodeBlock) {
            $output.Add($line)
            continue
        }
        if (Test-SpecialMarkdownLine $line) {
            Write-ParagraphBuffer
            $output.Add($line)
            continue
        }
        $paragraphBuffer.Add($line)
    }
    Write-ParagraphBuffer

    return $output
}

$targetFiles = if (Test-Path -LiteralPath $Path -PathType Container) {
    Get-ChildItem -LiteralPath $Path -Recurse -Filter '*.md' -File
} else {
    Get-Item -LiteralPath $Path
}

$noBomUtf8 = [System.Text.UTF8Encoding]::new($false)

foreach ($file in $targetFiles) {
    $original = [System.IO.File]::ReadAllLines($file.FullName)
    $result = ConvertTo-UnwrappedMarkdown -Lines $original

    if (($original -join "`n") -eq ($result -join "`n")) {
        Write-Host "No change: $($file.FullName)"
        continue
    }

    if ($Preview) {
        Write-Host "--- Would update: $($file.FullName) ---"
        Compare-Object -ReferenceObject $original -DifferenceObject $result | Format-Table -AutoSize
        continue
    }

    if ($PSCmdlet.ShouldProcess($file.FullName, 'Unwrap markdown paragraphs')) {
        [System.IO.File]::WriteAllLines($file.FullName, $result, $noBomUtf8)
        Write-Host "Updated: $($file.FullName)"
    }
}
