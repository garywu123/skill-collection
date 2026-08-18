[CmdletBinding()]
param(
    [string]$TemplatePath = '',
    [string[]]$RequiredFonts = @(
        'Amasis MT Pro Medium',
        'Aptos',
        'Consolas'
    ),
    [switch]$StrictFonts
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($TemplatePath)) {
    $TemplatePath = Join-Path $PSScriptRoot '..\designs\Crown Template.pptx'
}

function Release-ComObject {
    param([object]$ComObject)

    if ($null -ne $ComObject -and [System.Runtime.InteropServices.Marshal]::IsComObject($ComObject)) {
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($ComObject)
    }
}

if ($env:OS -ne 'Windows_NT') {
    throw 'Crown PowerPoint automation requires Windows.'
}
if (-not (Test-Path -LiteralPath $TemplatePath -PathType Leaf)) {
    throw "Crown PowerPoint template is missing: $TemplatePath"
}

$resolvedTemplatePath = (Resolve-Path -LiteralPath $TemplatePath).Path

$installedFonts = @()
try {
    Add-Type -AssemblyName System.Drawing
    $fontCollection = New-Object System.Drawing.Text.InstalledFontCollection
    $installedFonts = @($fontCollection.Families | ForEach-Object { $_.Name })
}
catch {
    Write-Warning "Unable to enumerate installed Windows fonts: $($_.Exception.Message)"
}

$fontChecks = foreach ($fontName in $RequiredFonts) {
    [pscustomobject]@{
        Name = $fontName
        InstalledInWindows = $installedFonts -contains $fontName
    }
}

$powerPoint = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.DisplayAlerts = 1
    $powerPoint.AutomationSecurity = 3

    $report = [pscustomobject]@{
        Windows = $true
        PowerPointComAvailable = $true
        PowerPointVersion = [string]$powerPoint.Version
        TemplatePath = $resolvedTemplatePath
        RequiredFonts = @($fontChecks)
        Note = 'Office cloud fonts may be usable in PowerPoint even when they are not registered as Windows-installed fonts.'
    }

    $report | ConvertTo-Json -Depth 4

    $missingFonts = @($fontChecks | Where-Object { -not $_.InstalledInWindows })
    if ($StrictFonts -and $missingFonts.Count -gt 0) {
        throw "Required Windows fonts are missing: $($missingFonts.Name -join ', ')"
    }
}
finally {
    if ($null -ne $powerPoint) {
        try { $powerPoint.Quit() } catch { Write-Warning $_.Exception.Message }
        Release-ComObject $powerPoint
    }

    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
