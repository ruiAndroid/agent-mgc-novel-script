param(
    [string]$SkillsJsonDir = "skills",
    [switch]$Overwrite,
    [switch]$RemoveSource
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-BasePath {
    if ($PSScriptRoot) {
        return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    }
    return (Get-Location).Path
}

function Convert-SkillJsonToMarkdown {
    param(
        [string]$JsonPath,
        [string]$TargetDir,
        [switch]$Overwrite
    )

    $raw = Get-Content -Raw -Path $JsonPath -Encoding UTF8
    $obj = $raw | ConvertFrom-Json

    if (-not $obj.skill_id) {
        throw "Missing skill_id in: $JsonPath"
    }

    $skillId = [string]$obj.skill_id
    $description = ""
    if ($obj.PSObject.Properties.Name -contains "description" -and $obj.description) {
        $description = [string]$obj.description
    }
    $version = ""
    if ($obj.PSObject.Properties.Name -contains "version" -and $obj.version) {
        $version = [string]$obj.version
    }
    $promptTemplate = ""
    if ($obj.PSObject.Properties.Name -contains "prompt_template" -and $obj.prompt_template) {
        $promptTemplate = [string]$obj.prompt_template
    }

    $skillDir = Join-Path $TargetDir $skillId
    if (-not (Test-Path -Path $skillDir)) {
        New-Item -Path $skillDir -ItemType Directory | Out-Null
    }

    $skillMdPath = Join-Path $skillDir "SKILL.md"
    if ((Test-Path -Path $skillMdPath) -and -not $Overwrite) {
        Write-Host "skip existing: $skillMdPath"
        return
    }

    $builder = New-Object System.Text.StringBuilder
    [void]$builder.AppendLine("# $skillId")
    [void]$builder.AppendLine()
    if ($description) {
        [void]$builder.AppendLine("## Description")
        [void]$builder.AppendLine($description)
        [void]$builder.AppendLine()
    }
    if ($version) {
        [void]$builder.AppendLine("## Version")
        [void]$builder.AppendLine($version)
        [void]$builder.AppendLine()
    }
    [void]$builder.AppendLine("## Instructions")
    [void]$builder.AppendLine("Follow the instructions below exactly when this skill is selected.")
    [void]$builder.AppendLine()
    [void]$builder.Append($promptTemplate)
    [void]$builder.AppendLine()

    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($skillMdPath, $builder.ToString(), $utf8NoBom)
    Write-Host "generated: $skillMdPath"
}

$basePath = Resolve-BasePath
$jsonDirPath = Join-Path $basePath $SkillsJsonDir
if (-not (Test-Path -Path $jsonDirPath)) {
    throw "Skills directory not found: $jsonDirPath"
}

$jsonFiles = Get-ChildItem -Path $jsonDirPath -Filter "*.json" -File | Sort-Object Name
if (-not $jsonFiles) {
    throw "No JSON skill files found in: $jsonDirPath"
}

foreach ($file in $jsonFiles) {
    Convert-SkillJsonToMarkdown -JsonPath $file.FullName -TargetDir $jsonDirPath -Overwrite:$Overwrite
    if ($RemoveSource) {
        Remove-Item -Path $file.FullName -Force
        Write-Host "removed source: $($file.FullName)"
    }
}

Write-Host ""
Write-Host "done. generated skill directories under: $jsonDirPath"
