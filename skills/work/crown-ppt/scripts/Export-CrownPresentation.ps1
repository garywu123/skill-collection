[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$PresentationPath,
    [Parameter(Mandatory)]
    [string]$OutputDirectory,
    [int]$Width = 1600,
    [int]$Height = 900
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Release-ComObject {
    param([object]$ComObject)

    if ($null -ne $ComObject -and [System.Runtime.InteropServices.Marshal]::IsComObject($ComObject)) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($ComObject)
    }
}

if ($env:OS -ne 'Windows_NT') {
    throw 'Crown PowerPoint rendering requires Windows.'
}
if ($Width -lt 320 -or $Height -lt 180) {
    throw 'Render dimensions are too small.'
}

$resolvedPresentationPath = (Resolve-Path -LiteralPath $PresentationPath).Path
$resolvedOutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
[void](New-Item -ItemType Directory -Path $resolvedOutputDirectory -Force)

$powerPoint = $null
$presentation = $null
$renderIndex = @()

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.DisplayAlerts = 1
    $powerPoint.AutomationSecurity = 3
    $presentation = $powerPoint.Presentations.Open($resolvedPresentationPath, -1, 0, 0)

    for ($slideIndex = 1; $slideIndex -le $presentation.Slides.Count; $slideIndex++) {
        $slide = $null
        try {
            $slide = $presentation.Slides.Item($slideIndex)
            $fileName = 'slide_{0:D2}.png' -f $slideIndex
            $outputPath = Join-Path $resolvedOutputDirectory $fileName
            $slide.Export($outputPath, 'PNG', $Width, $Height)
            $renderIndex += [pscustomobject]@{
                Slide = $slideIndex
                File = $fileName
            }
        }
        finally {
            Release-ComObject $slide
        }
    }

    $indexPath = Join-Path $resolvedOutputDirectory 'index.json'
    $renderIndex | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $indexPath -Encoding UTF8
    Write-Output $resolvedOutputDirectory
}
finally {
    if ($null -ne $presentation) {
        try { $presentation.Close() } catch { Write-Warning $_.Exception.Message }
    }
    if ($null -ne $powerPoint) {
        try { $powerPoint.Quit() } catch { Write-Warning $_.Exception.Message }
    }

    Release-ComObject $presentation
    Release-ComObject $powerPoint
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
