[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$IconName,
    [ValidatePattern('^[0-9A-Fa-f]{6}$')]
    [string]$Color = '515151',
    [string]$OutputDirectory,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $PSScriptRoot '..\assets\icons'
}

$resolvedOutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
[void](New-Item -ItemType Directory -Path $resolvedOutputDirectory -Force)

$fileName = "$IconName.svg"
$outputPath = Join-Path $resolvedOutputDirectory $fileName
$manifestPath = Join-Path $resolvedOutputDirectory 'icon-manifest.json'
$uri = "https://api.iconify.design/fluent/$IconName.svg?color=%23$($Color.ToUpperInvariant())"

if ((Test-Path -LiteralPath $outputPath) -and -not $Force) {
    Write-Output $outputPath
    return
}

$response = Invoke-WebRequest -Uri $uri -UseBasicParsing
if ($response.StatusCode -ne 200) {
    throw "Iconify returned HTTP $($response.StatusCode) for '$IconName'."
}

$svg = [string]$response.Content
if ($svg -notmatch '<svg\b' -or $svg -notmatch '</svg>') {
    throw "The response for '$IconName' is not a complete SVG document."
}
if ($svg -match '<script\b' -or $svg -match '(?:href|xlink:href)\s*=\s*["'']\s*(?:https?:|data:)') {
    throw "The SVG for '$IconName' contains disallowed executable or external content."
}

$svg | Set-Content -LiteralPath $outputPath -Encoding UTF8
$hash = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash

$manifestEntries = @()
if (Test-Path -LiteralPath $manifestPath) {
    $existingManifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
    $manifestEntries = @($existingManifest | Where-Object { $_.File -ne $fileName })
}
$manifestEntries += [pscustomobject]@{
    File = $fileName
    Provider = 'Iconify public API'
    Collection = 'fluent'
    Upstream = 'Microsoft Fluent UI System Icons'
    License = 'MIT'
    Icon = $IconName
    Color = "#$($Color.ToUpperInvariant())"
    Source = $uri
    RetrievedAtUtc = [DateTime]::UtcNow.ToString('o')
    Sha256 = $hash
}
$sortedManifestEntries = @($manifestEntries | Sort-Object File)
ConvertTo-Json -InputObject $sortedManifestEntries -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

Write-Output $outputPath
