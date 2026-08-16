[CmdletBinding()]
param(
    [string]$TemplatePath,
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($TemplatePath)) {
    $TemplatePath = Join-Path $PSScriptRoot '..\assets\Template - Crown Branded Powerpoint (MGT20013) Light Version.pptx'
}
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $PSScriptRoot '..\references\template-profile.json'
}

function Release-ComObject {
    param([object]$ComObject)

    if ($null -ne $ComObject -and [System.Runtime.InteropServices.Marshal]::IsComObject($ComObject)) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($ComObject)
    }
}

function Convert-OleRgbToHex {
    param([int64]$Rgb)

    $red = $Rgb -band 0xFF
    $green = ($Rgb -shr 8) -band 0xFF
    $blue = ($Rgb -shr 16) -band 0xFF
    return '#{0:X2}{1:X2}{2:X2}' -f $red, $green, $blue
}

function Get-ShapeProfile {
    param([object]$Shape)

    $placeholderType = $null
    if ($Shape.Type -eq 14) {
        try { $placeholderType = [int]$Shape.PlaceholderFormat.Type } catch { $placeholderType = $null }
    }

    $text = $null
    $fontName = $null
    $fontSize = $null
    $textRange = $null
    try {
        if ($Shape.HasTextFrame -eq -1) {
            $textRange = $Shape.TextFrame.TextRange
            $text = [string]$textRange.Text
            $fontName = [string]$textRange.Font.Name
            $fontSize = [double]$textRange.Font.Size
        }
    }
    catch {
        $text = $null
    }
    finally {
        Release-ComObject $textRange
    }

    return [pscustomobject]@{
        Name = [string]$Shape.Name
        Type = [int]$Shape.Type
        PlaceholderType = $placeholderType
        Left = [math]::Round([double]$Shape.Left, 2)
        Top = [math]::Round([double]$Shape.Top, 2)
        Width = [math]::Round([double]$Shape.Width, 2)
        Height = [math]::Round([double]$Shape.Height, 2)
        HasTextFrame = $Shape.HasTextFrame -eq -1
        Text = $text
        FontName = $fontName
        FontSize = $fontSize
    }
}

if ($env:OS -ne 'Windows_NT') {
    throw 'Crown PowerPoint template inspection requires Windows.'
}

$resolvedTemplatePath = (Resolve-Path -LiteralPath $TemplatePath).Path
$resolvedOutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$outputDirectory = Split-Path -Parent $resolvedOutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    [void](New-Item -ItemType Directory -Path $outputDirectory -Force)
}

$powerPoint = $null
$presentation = $null
$slideMaster = $null
$theme = $null
$themeFontScheme = $null
$themeColorScheme = $null
$customLayouts = $null

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.DisplayAlerts = 1
    $powerPoint.AutomationSecurity = 3
    $presentation = $powerPoint.Presentations.Open($resolvedTemplatePath, -1, 0, 0)
    $slideMaster = $presentation.SlideMaster
    $theme = $slideMaster.Theme
    $themeFontScheme = $theme.ThemeFontScheme
    $themeColorScheme = $theme.ThemeColorScheme
    $customLayouts = $slideMaster.CustomLayouts

    $majorFonts = @()
    foreach ($font in $themeFontScheme.MajorFont) {
        try {
            if (-not [string]::IsNullOrWhiteSpace([string]$font.Name)) {
                $majorFonts += [string]$font.Name
            }
        }
        finally {
            Release-ComObject $font
        }
    }

    $minorFonts = @()
    foreach ($font in $themeFontScheme.MinorFont) {
        try {
            if (-not [string]::IsNullOrWhiteSpace([string]$font.Name)) {
                $minorFonts += [string]$font.Name
            }
        }
        finally {
            Release-ComObject $font
        }
    }

    $colorNames = @(
        'Dark1', 'Light1', 'Dark2', 'Light2',
        'Accent1', 'Accent2', 'Accent3', 'Accent4',
        'Accent5', 'Accent6', 'Hyperlink', 'FollowedHyperlink'
    )
    $themeColors = @()
    for ($colorIndex = 1; $colorIndex -le 12; $colorIndex++) {
        $themeColor = $null
        try {
            $themeColor = $themeColorScheme.Colors($colorIndex)
            $themeColors += [pscustomobject]@{
                Name = $colorNames[$colorIndex - 1]
                Hex = Convert-OleRgbToHex ([int64]$themeColor.RGB)
            }
        }
        finally {
            Release-ComObject $themeColor
        }
    }

    $layoutProfiles = @()
    for ($layoutIndex = 1; $layoutIndex -le $customLayouts.Count; $layoutIndex++) {
        $layout = $null
        try {
            $layout = $customLayouts.Item($layoutIndex)
            $shapeProfiles = @()
            for ($shapeIndex = 1; $shapeIndex -le $layout.Shapes.Count; $shapeIndex++) {
                $shape = $null
                try {
                    $shape = $layout.Shapes.Item($shapeIndex)
                    $shapeProfiles += Get-ShapeProfile $shape
                }
                finally {
                    Release-ComObject $shape
                }
            }

            $layoutProfiles += [pscustomobject]@{
                Index = $layoutIndex
                Name = [string]$layout.Name
                ShapeCount = [int]$layout.Shapes.Count
                Shapes = @($shapeProfiles)
            }
        }
        finally {
            Release-ComObject $layout
        }
    }

    $profile = [ordered]@{
        SchemaVersion = 1
        GeneratedAtUtc = [DateTime]::UtcNow.ToString('o')
        TemplateFile = [System.IO.Path]::GetFileName($resolvedTemplatePath)
        TemplateSha256 = (Get-FileHash -LiteralPath $resolvedTemplatePath -Algorithm SHA256).Hash
        PowerPointVersion = [string]$powerPoint.Version
        Canvas = [ordered]@{
            WidthPoints = [math]::Round([double]$presentation.PageSetup.SlideWidth, 2)
            HeightPoints = [math]::Round([double]$presentation.PageSetup.SlideHeight, 2)
            WidthInches = [math]::Round([double]$presentation.PageSetup.SlideWidth / 72, 3)
            HeightInches = [math]::Round([double]$presentation.PageSetup.SlideHeight / 72, 3)
        }
        SlideCount = [int]$presentation.Slides.Count
        MasterCount = [int]$presentation.Designs.Count
        LayoutCount = [int]$customLayouts.Count
        Theme = [ordered]@{
            MajorFonts = @($majorFonts | Select-Object -Unique)
            MinorFonts = @($minorFonts | Select-Object -Unique)
            Colors = @($themeColors)
        }
        Layouts = @($layoutProfiles)
    }

    $profile | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $resolvedOutputPath -Encoding UTF8
    Write-Output $resolvedOutputPath
}
finally {
    if ($null -ne $presentation) {
        try { $presentation.Close() } catch { Write-Warning $_.Exception.Message }
    }
    if ($null -ne $powerPoint) {
        try { $powerPoint.Quit() } catch { Write-Warning $_.Exception.Message }
    }

    Release-ComObject $customLayouts
    Release-ComObject $themeColorScheme
    Release-ComObject $themeFontScheme
    Release-ComObject $theme
    Release-ComObject $slideMaster
    Release-ComObject $presentation
    Release-ComObject $powerPoint
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
