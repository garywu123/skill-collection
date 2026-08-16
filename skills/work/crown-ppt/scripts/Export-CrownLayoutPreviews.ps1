[CmdletBinding()]
param(
    [string]$TemplatePath,
    [string]$OutputDirectory,
    [int]$Width = 1600,
    [int]$Height = 900,
    [switch]$LabelPlaceholders
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($TemplatePath)) {
    $TemplatePath = Join-Path $PSScriptRoot '..\assets\Template - Crown Branded Powerpoint (MGT20013) Light Version.pptx'
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $PSScriptRoot '..\template-analysis\layouts'
}

function Release-ComObject {
    param([object]$ComObject)

    if ($null -ne $ComObject -and [System.Runtime.InteropServices.Marshal]::IsComObject($ComObject)) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($ComObject)
    }
}

function Get-SafeFileName {
    param([string]$Name)

    $safeName = $Name.ToLowerInvariant() -replace '[^a-z0-9]+', '-'
    return $safeName.Trim('-')
}

if ($env:OS -ne 'Windows_NT') {
    throw 'Crown PowerPoint preview export requires Windows.'
}
if ($Width -lt 320 -or $Height -lt 180) {
    throw 'Preview dimensions are too small.'
}

$resolvedTemplatePath = (Resolve-Path -LiteralPath $TemplatePath).Path
$resolvedOutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
[void](New-Item -ItemType Directory -Path $resolvedOutputDirectory -Force)

$powerPoint = $null
$presentation = $null
$slideMaster = $null
$customLayouts = $null
$previewIndex = @()

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.DisplayAlerts = 1
    $powerPoint.AutomationSecurity = 3
    $presentation = $powerPoint.Presentations.Open($resolvedTemplatePath, -1, -1, 0)
    $slideMaster = $presentation.SlideMaster
    $customLayouts = $slideMaster.CustomLayouts

    for ($layoutIndex = 1; $layoutIndex -le $customLayouts.Count; $layoutIndex++) {
        $layout = $null
        $slide = $null
        try {
            $layout = $customLayouts.Item($layoutIndex)
            $slide = $presentation.Slides.AddSlide($presentation.Slides.Count + 1, $layout)

            if ($LabelPlaceholders) {
                for ($shapeIndex = 1; $shapeIndex -le $slide.Shapes.Count; $shapeIndex++) {
                    $shape = $null
                    $textRange = $null
                    try {
                        $shape = $slide.Shapes.Item($shapeIndex)
                        if ($shape.Type -eq 14 -and $shape.HasTextFrame -eq -1) {
                            $placeholderType = [int]$shape.PlaceholderFormat.Type
                            if ($placeholderType -in @(1, 3, 5)) {
                                $textRange = $shape.TextFrame.TextRange
                                $textRange.Text = "Layout: $($layout.Name)"
                            }
                            elseif ($placeholderType -in @(2, 4, 6, 7, 8, 11, 12, 17, 18)) {
                                $textRange = $shape.TextFrame.TextRange
                                $textRange.Text = "[Placeholder $placeholderType]"
                            }
                        }
                    }
                    finally {
                        Release-ComObject $textRange
                        Release-ComObject $shape
                    }
                }
            }

            $safeName = Get-SafeFileName $layout.Name
            $fileName = '{0:D2}-{1}.png' -f $layoutIndex, $safeName
            $outputPath = Join-Path $resolvedOutputDirectory $fileName
            $slide.Export($outputPath, 'PNG', $Width, $Height)
            $previewIndex += [pscustomobject]@{
                Index = $layoutIndex
                Layout = [string]$layout.Name
                File = $fileName
            }
        }
        finally {
            if ($null -ne $slide) {
                try { $slide.Delete() } catch { Write-Warning $_.Exception.Message }
            }
            Release-ComObject $slide
            Release-ComObject $layout
        }
    }

    $indexPath = Join-Path $resolvedOutputDirectory 'index.json'
    $previewIndex | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $indexPath -Encoding UTF8
    Write-Output $resolvedOutputDirectory
}
finally {
    if ($null -ne $presentation) {
        try { $presentation.Close() } catch { Write-Warning $_.Exception.Message }
    }
    if ($null -ne $powerPoint) {
        try { $powerPoint.Quit() } catch { Write-Warning $_.Exception.Message }
    }

    Release-ComObject $customLayouts
    Release-ComObject $slideMaster
    Release-ComObject $presentation
    Release-ComObject $powerPoint
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
