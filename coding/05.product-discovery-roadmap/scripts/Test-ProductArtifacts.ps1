[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string[]]$RequirementsPath,

    [Parameter(Mandatory = $true)]
    [string]$RoadmapPath
)

$ErrorActionPreference = 'Stop'

function Get-ResolvedFile {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "File not found: $Path"
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

function Split-MarkdownRow {
    param([string]$Line)

    return @($Line.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim() })
}

function Get-Ids {
    param(
        [string]$Text,
        [string]$Pattern
    )

    return @([regex]::Matches($Text, $Pattern) | ForEach-Object { $_.Value.ToUpperInvariant() })
}

$errors = [System.Collections.Generic.List[string]]::new()
$requirementDefinitions = @{}
$resolvedRequirementPaths = @($RequirementsPath | ForEach-Object {
    Get-ResolvedFile -Path $_
} | Select-Object -Unique)

foreach ($resolvedPath in $resolvedRequirementPaths) {
    foreach ($line in Get-Content -LiteralPath $resolvedPath) {
        $match = [regex]::Match(
            $line,
            '^\s*(?:-\s+\*\*|#{2,6}\s+)(PR-\d{3})(?:\*\*:|\s*$)',
            [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
        )
        if (-not $match.Success) {
            continue
        }

        $id = $match.Groups[1].Value.ToUpperInvariant()
        if (-not $requirementDefinitions.ContainsKey($id)) {
            $requirementDefinitions[$id] = [System.Collections.Generic.List[string]]::new()
        }
        $requirementDefinitions[$id].Add($resolvedPath)
    }
}

if ($requirementDefinitions.Count -eq 0) {
    $errors.Add('No PR-### requirement definitions were found.')
}

foreach ($entry in $requirementDefinitions.GetEnumerator()) {
    if ($entry.Value.Count -gt 1) {
        $errors.Add("Requirement $($entry.Key) is defined more than once: $($entry.Value -join ', ')")
    }
}

$resolvedRoadmap = Get-ResolvedFile -Path $RoadmapPath
$roadmapLines = @(Get-Content -LiteralPath $resolvedRoadmap)
$featureMapHeading = -1
for ($index = 0; $index -lt $roadmapLines.Count; $index++) {
    if ($roadmapLines[$index] -match '^##\s+Feature Map\s*$') {
        $featureMapHeading = $index
        break
    }
}

if ($featureMapHeading -lt 0) {
    $errors.Add('Roadmap is missing the required Feature Map section.')
}

$headerIndex = -1
if ($featureMapHeading -ge 0) {
    for ($index = $featureMapHeading + 1; $index -lt $roadmapLines.Count; $index++) {
        if ($roadmapLines[$index] -match '^\s*\|' -and $roadmapLines[$index] -match 'Owns Requirements') {
            $headerIndex = $index
            break
        }
        if ($roadmapLines[$index] -match '^##\s+') {
            break
        }
    }
}

$features = @{}
$owners = @{}
$featureOrder = [System.Collections.Generic.List[string]]::new()

if ($headerIndex -lt 0) {
    $errors.Add('Feature Map is missing a table with an Owns Requirements column.')
}
else {
    $headers = @(Split-MarkdownRow -Line $roadmapLines[$headerIndex])
    $column = @{}
    for ($index = 0; $index -lt $headers.Count; $index++) {
        $column[$headers[$index].ToLowerInvariant()] = $index
    }

    foreach ($requiredColumn in @('id', 'owns requirements', 'also bound by', 'depends on', 'delivery', 'ui surface')) {
        if (-not $column.ContainsKey($requiredColumn)) {
            $errors.Add("Feature Map is missing column: $requiredColumn")
        }
    }

    for ($index = $headerIndex + 2; $index -lt $roadmapLines.Count; $index++) {
        $line = $roadmapLines[$index]
        if ($line -notmatch '^\s*\|') {
            break
        }

        $cells = @(Split-MarkdownRow -Line $line)
        if (-not $column.ContainsKey('id') -or $column['id'] -ge $cells.Count) {
            continue
        }

        $featureId = $cells[$column['id']].ToUpperInvariant()
        if ($featureId -notmatch '^F\d{3}$') {
            $errors.Add("Invalid feature ID in Feature Map: $featureId")
            continue
        }
        if ($features.ContainsKey($featureId)) {
            $errors.Add("Feature $featureId appears more than once in Feature Map.")
            continue
        }

        $ownsText = if ($column.ContainsKey('owns requirements') -and $column['owns requirements'] -lt $cells.Count) { $cells[$column['owns requirements']] } else { '' }
        $boundText = if ($column.ContainsKey('also bound by') -and $column['also bound by'] -lt $cells.Count) { $cells[$column['also bound by']] } else { '' }
        $dependsText = if ($column.ContainsKey('depends on') -and $column['depends on'] -lt $cells.Count) { $cells[$column['depends on']] } else { '' }
        $delivery = if ($column.ContainsKey('delivery') -and $column['delivery'] -lt $cells.Count) { $cells[$column['delivery']] } else { '' }
        $uiSurface = if ($column.ContainsKey('ui surface') -and $column['ui surface'] -lt $cells.Count) { $cells[$column['ui surface']] } else { '' }

        $ownedIds = @(Get-Ids -Text $ownsText -Pattern 'PR-\d{3}')
        $boundIds = @(Get-Ids -Text $boundText -Pattern 'PR-\d{3}')
        $dependencies = @(Get-Ids -Text $dependsText -Pattern 'F\d{3}')

        if ($ownedIds.Count -eq 0) {
            $errors.Add("Feature $featureId owns no requirements.")
        }
        if ($delivery -notin @('MVP', 'Post-MVP', 'Deferred', 'Candidate')) {
            $errors.Add("Feature $featureId has invalid Delivery value: $delivery")
        }
        if ($uiSurface -notin @('none', 'reuses existing', 'new screens')) {
            $errors.Add("Feature $featureId has invalid UI Surface value: $uiSurface")
        }

        foreach ($requirementId in $ownedIds) {
            if (-not $owners.ContainsKey($requirementId)) {
                $owners[$requirementId] = [System.Collections.Generic.List[string]]::new()
            }
            $owners[$requirementId].Add($featureId)
        }

        $features[$featureId] = [pscustomobject]@{
            Owned = $ownedIds
            Bound = $boundIds
            Dependencies = $dependencies
        }
        $featureOrder.Add($featureId)
    }
}

foreach ($requirementId in $requirementDefinitions.Keys) {
    if (-not $owners.ContainsKey($requirementId)) {
        $errors.Add("Requirement $requirementId has no owning feature.")
    }
    elseif ($owners[$requirementId].Count -ne 1) {
        $errors.Add("Requirement $requirementId has multiple owners: $($owners[$requirementId] -join ', ')")
    }
}

foreach ($requirementId in $owners.Keys) {
    if (-not $requirementDefinitions.ContainsKey($requirementId)) {
        $errors.Add("Feature Map owns unknown requirement $requirementId.")
    }
}

foreach ($featureId in $featureOrder) {
    foreach ($requirementId in $features[$featureId].Bound) {
        if (-not $requirementDefinitions.ContainsKey($requirementId)) {
            $errors.Add("Feature $featureId is bound by unknown requirement $requirementId.")
        }
    }
    foreach ($dependencyId in $features[$featureId].Dependencies) {
        if (-not $features.ContainsKey($dependencyId)) {
            $errors.Add("Feature $featureId depends on unknown feature $dependencyId.")
        }
        elseif ($dependencyId -eq $featureId) {
            $errors.Add("Feature $featureId depends on itself.")
        }
    }
}

if ($features.Count -gt 0) {
    $indegree = @{}
    $dependents = @{}
    foreach ($featureId in $featureOrder) {
        $indegree[$featureId] = 0
        $dependents[$featureId] = [System.Collections.Generic.List[string]]::new()
    }
    foreach ($featureId in $featureOrder) {
        foreach ($dependencyId in $features[$featureId].Dependencies) {
            if ($features.ContainsKey($dependencyId) -and $dependencyId -ne $featureId) {
                $indegree[$featureId]++
                $dependents[$dependencyId].Add($featureId)
            }
        }
    }

    $queue = [System.Collections.Generic.Queue[string]]::new()
    foreach ($featureId in $featureOrder) {
        if ($indegree[$featureId] -eq 0) {
            $queue.Enqueue($featureId)
        }
    }

    $visited = 0
    while ($queue.Count -gt 0) {
        $featureId = $queue.Dequeue()
        $visited++
        foreach ($dependentId in $dependents[$featureId]) {
            $indegree[$dependentId]--
            if ($indegree[$dependentId] -eq 0) {
                $queue.Enqueue($dependentId)
            }
        }
    }

    if ($visited -ne $features.Count) {
        $errors.Add('Feature dependency graph contains a cycle.')
    }
}

if ($errors.Count -gt 0) {
    throw ("Product artifact validation failed:`n- " + ($errors -join "`n- "))
}

Write-Output "Product artifact validation passed: $($requirementDefinitions.Count) requirements, $($features.Count) features, one owner per requirement, valid references, acyclic dependencies."