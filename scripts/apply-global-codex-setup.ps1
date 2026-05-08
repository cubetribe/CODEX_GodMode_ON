Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Show-Usage {
  @'
Usage:
  ./scripts/apply-global-codex-setup.ps1 [options]

Options:
  --check, -Check        Verify the installed global setup instead of applying it
  --codex-home PATH      Override the target Codex home directory
  --user-skills-home PATH
                         Override the target user skills directory
  --repo PATH            Override the repository root used for templates, agents, skills, and trust
  --no-trust-project     Do not add the repository path to [projects."<path>"]
  -h, --help             Show this help text
'@.Trim()
}

function Fail {
  param(
    [string]$Message,
    [int]$ExitCode = 1
  )

  [Console]::Error.WriteLine($Message)
  exit $ExitCode
}

function Resolve-AbsolutePath {
  param([string]$Path)

  $resolved = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
  [System.IO.Path]::GetFullPath($resolved)
}

function Convert-ToTomlPath {
  param([string]$Path)

  ($Path -replace '\\', '/') -replace '"', '\"'
}

function Same-Path {
  param(
    [string]$Left,
    [string]$Right
  )

  [string]::Equals(
    [System.IO.Path]::GetFullPath($Left).TrimEnd('\'),
    [System.IO.Path]::GetFullPath($Right).TrimEnd('\'),
    [System.StringComparison]::OrdinalIgnoreCase
  )
}

function Write-Utf8File {
  param(
    [string]$Path,
    [string]$Content
  )

  $encoding = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Require-File {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    Fail "Required file missing: $Path"
  }
}

function Require-Directory {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
    Fail "Required directory missing: $Path"
  }
}

function Backup-Path {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    return
  }

  $backupPath = $null
  if (Same-Path $Path $script:targetAgents) {
    $backupPath = Join-Path (Join-Path $script:backupRoot 'root') 'AGENTS.md'
  }
  elseif (Same-Path $Path $script:targetConfig) {
    $backupPath = Join-Path (Join-Path $script:backupRoot 'root') 'config.toml'
  }
  elseif (Same-Path (Split-Path -Parent $Path) $script:targetAgentsDir) {
    $backupPath = Join-Path (Join-Path $script:backupRoot 'agents') (Split-Path -Leaf $Path)
  }
  elseif (Same-Path (Split-Path -Parent $Path) $script:userSkillsHome) {
    $backupPath = Join-Path (Join-Path $script:backupRoot 'skills') (Split-Path -Leaf $Path)
  }
  else {
    $backupPath = Join-Path (Join-Path $script:backupRoot 'misc') (Split-Path -Leaf $Path)
  }

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPath) | Out-Null
  Copy-Item -LiteralPath $Path -Destination $backupPath -Recurse -Force
  Write-Output "Backed up $Path -> $backupPath"
}

function Archive-LegacyDiscoveryConflicts {
  $found = $false

  if (Test-Path -LiteralPath $script:targetAgentsDir -PathType Container) {
    $agentArtifacts = @(Get-ChildItem -LiteralPath $script:targetAgentsDir -Force | Where-Object { $_.Name -like '*.backup-*' } | Sort-Object Name)
    foreach ($artifact in $agentArtifacts) {
      $found = $true
      $archivedPath = Join-Path (Join-Path (Join-Path $script:backupRoot 'legacy-discovery-conflicts') 'agents') $artifact.Name
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $archivedPath) | Out-Null
      Move-Item -LiteralPath $artifact.FullName -Destination $archivedPath -Force
      Write-Output "Archived legacy agent backup $($artifact.FullName) -> $archivedPath"
    }
  }

  if (Test-Path -LiteralPath $script:userSkillsHome -PathType Container) {
    $skillArtifacts = @(Get-ChildItem -LiteralPath $script:userSkillsHome -Force | Where-Object { $_.Name -like '*.backup-*' } | Sort-Object Name)
    foreach ($artifact in $skillArtifacts) {
      $found = $true
      $archivedPath = Join-Path (Join-Path (Join-Path $script:backupRoot 'legacy-discovery-conflicts') 'skills') $artifact.Name
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $archivedPath) | Out-Null
      Move-Item -LiteralPath $artifact.FullName -Destination $archivedPath -Force
      Write-Output "Archived legacy skill backup $($artifact.FullName) -> $archivedPath"
    }
  }

  if ($found) {
    Write-Output "Legacy discovery conflicts were moved under $($script:backupRoot)"
  }
}

function Render-ConfigTemplate {
  $content = [System.IO.File]::ReadAllText($script:sourceConfig)
  $rendered = $content.Replace('__CODEX_HOME__', $script:tomlCodexHome)
  Write-Utf8File -Path $script:targetConfig -Content $rendered
}

function Check-Path {
  param(
    [string]$Path,
    [string]$Label
  )

  if (Test-Path -LiteralPath $Path) {
    Write-Output "[ok] ${Label}: $Path"
    return $true
  }

  Write-Output "[missing] ${Label}: $Path"
  return $false
}

function Check-Contains {
  param(
    [string]$Path,
    [string]$Pattern,
    [string]$Label
  )

  if (Select-String -LiteralPath $Path -Pattern $Pattern -SimpleMatch -Quiet) {
    Write-Output "[ok] $Label"
    return $true
  }

  Write-Output "[missing] $Label"
  return $false
}

function Check-NoLegacyDiscoveryConflicts {
  param(
    [string]$Root,
    [string]$Label
  )

  if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
    Write-Output "[ok] $Label clean"
    return $true
  }

  $conflicts = @(Get-ChildItem -LiteralPath $Root -Force | Where-Object { $_.Name -like '*.backup-*' } | Sort-Object Name)
  if ($conflicts.Count -gt 0) {
    Write-Output "[invalid] $Label contains legacy backup artifacts that may surface as duplicate entries"
    foreach ($conflict in $conflicts) {
      Write-Output $conflict.FullName
    }
    return $false
  }

  Write-Output "[ok] $Label clean"
  return $true
}

function Ensure-ProjectTrust {
  param(
    [string]$ConfigPath,
    [string]$ProjectPath
  )

  $header = "[projects.""$ProjectPath""]"
  if (Select-String -LiteralPath $ConfigPath -Pattern $header -SimpleMatch -Quiet) {
    Write-Output "Project trust entry already present: $ProjectPath"
    return
  }

  $content = [System.IO.File]::ReadAllText($ConfigPath)
  $content = $content + "`n$header`ntrust_level = ""trusted""`n"
  Write-Utf8File -Path $ConfigPath -Content $content
  Write-Output "Added trusted project: $ProjectPath"
}

function Install-AgentFiles {
  $sourceFiles = @(Get-ChildItem -LiteralPath $script:sourceRepoAgents -Filter '*.toml' -File | Sort-Object Name)
  foreach ($sourceFile in $sourceFiles) {
    $targetPath = Join-Path $script:targetAgentsDir $sourceFile.Name
    Backup-Path $targetPath
    Copy-Item -LiteralPath $sourceFile.FullName -Destination $targetPath -Force
  }
}

function Install-SkillDirs {
  $sourceDirs = @(Get-ChildItem -LiteralPath $script:sourceRepoSkills -Directory | Sort-Object Name)
  foreach ($sourceDir in $sourceDirs) {
    $targetDir = Join-Path $script:userSkillsHome $sourceDir.Name
    if (Test-Path -LiteralPath $targetDir -PathType Container) {
      Backup-Path $targetDir
    }

    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
    $children = @(Get-ChildItem -LiteralPath $sourceDir.FullName -Force)
    foreach ($child in $children) {
      Copy-Item -LiteralPath $child.FullName -Destination $targetDir -Recurse -Force
    }
  }
}

function Run-Check {
  $status = 0

  if (-not (Check-Path $script:targetAgents 'Global AGENTS')) { $status = 1 }
  if (-not (Check-Path $script:targetConfig 'Global config')) { $status = 1 }
  if (-not (Check-Path $script:targetAgentsDir 'Global agents dir')) { $status = 1 }
  if (-not (Check-Path $script:userSkillsHome 'User skills home')) { $status = 1 }
  if (-not (Check-Path $script:playwrightOutput 'Playwright output')) { $status = 1 }
  if (-not (Check-NoLegacyDiscoveryConflicts $script:targetAgentsDir 'Global agents dir')) { $status = 1 }
  if (-not (Check-NoLegacyDiscoveryConflicts $script:userSkillsHome 'User skills home')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'builder.toml') 'Global agent builder')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'researcher.toml') 'Global agent researcher')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'runtime_platform.toml') 'Global agent runtime_platform')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'workflow_design.toml') 'Global agent workflow_design')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'workspace_governance.toml') 'Global agent workspace_governance')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'quality_operations.toml') 'Global agent quality_operations')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'docs_dx.toml') 'Global agent docs_dx')) { $status = 1 }
  if (-not (Check-Path (Join-Path $script:targetAgentsDir 'ci_security_guardian.toml') 'Global agent ci_security_guardian')) { $status = 1 }
  if (-not (Check-Path (Join-Path (Join-Path $script:userSkillsHome 'godmode-workflow') 'SKILL.md') 'Global skill godmode-workflow')) { $status = 1 }
  if (-not (Check-Path (Join-Path (Join-Path $script:userSkillsHome 'godmode-departments') 'SKILL.md') 'Global skill godmode-departments')) { $status = 1 }
  if (-not (Check-Path (Join-Path (Join-Path $script:userSkillsHome 'godmode-debug') 'SKILL.md') 'Global skill godmode-debug')) { $status = 1 }
  if (-not (Check-Path (Join-Path (Join-Path $script:userSkillsHome 'godmode-review') 'SKILL.md') 'Global skill godmode-review')) { $status = 1 }
  if (-not (Check-Path (Join-Path (Join-Path $script:userSkillsHome 'greenfield-bootstrap') 'SKILL.md') 'Global skill greenfield-bootstrap')) { $status = 1 }
  if (-not (Check-Path (Join-Path (Join-Path $script:userSkillsHome 'web-platforms') 'SKILL.md') 'Global skill web-platforms')) { $status = 1 }

  if (Test-Path -LiteralPath $script:targetConfig -PathType Leaf) {
    if (-not (Check-Contains $script:targetConfig '[profiles.swiftui]' 'config profile swiftui')) { $status = 1 }
    if (-not (Check-Contains $script:targetConfig '[profiles.web]' 'config profile web')) { $status = 1 }
    if (-not (Check-Contains $script:targetConfig '[profiles.flutter]' 'config profile flutter')) { $status = 1 }
    if (-not (Check-Contains $script:targetConfig '[profiles.review]' 'config profile review')) { $status = 1 }
    if ($script:trustProject) {
      if (-not (Check-Contains $script:targetConfig "[projects.""$($script:tomlRepoRoot)""]" 'trusted project entry')) { $status = 1 }
    }
  }

  if (Test-Path -LiteralPath $script:targetAgents -PathType Leaf) {
    if (-not (Check-Contains $script:targetAgents '## Profile intents' 'global AGENTS profile guidance')) { $status = 1 }
    if (-not (Check-Contains $script:targetAgents '## Global workflow' 'global AGENTS workflow guidance')) { $status = 1 }
  }

  $builderPath = Join-Path $script:targetAgentsDir 'builder.toml'
  if (Test-Path -LiteralPath $builderPath -PathType Leaf) {
    if (-not (Check-Contains $builderPath 'name = "builder"' 'installed builder agent name')) { $status = 1 }
  }

  $runtimePath = Join-Path $script:targetAgentsDir 'runtime_platform.toml'
  if (Test-Path -LiteralPath $runtimePath -PathType Leaf) {
    if (-not (Check-Contains $runtimePath 'name = "runtime_platform"' 'installed runtime_platform agent name')) { $status = 1 }
  }

  $guardianPath = Join-Path $script:targetAgentsDir 'ci_security_guardian.toml'
  if (Test-Path -LiteralPath $guardianPath -PathType Leaf) {
    if (-not (Check-Contains $guardianPath 'name = "ci_security_guardian"' 'installed ci_security_guardian agent name')) { $status = 1 }
  }

  $workflowSkill = Join-Path (Join-Path $script:userSkillsHome 'godmode-workflow') 'SKILL.md'
  if (Test-Path -LiteralPath $workflowSkill -PathType Leaf) {
    if (-not (Check-Contains $workflowSkill 'GodMode Workflow' 'installed godmode skill')) { $status = 1 }
  }

  $departmentsSkill = Join-Path (Join-Path $script:userSkillsHome 'godmode-departments') 'SKILL.md'
  if (Test-Path -LiteralPath $departmentsSkill -PathType Leaf) {
    if (-not (Check-Contains $departmentsSkill 'GodMode Departments' 'installed godmode departments skill')) { $status = 1 }
  }

  $debugSkill = Join-Path (Join-Path $script:userSkillsHome 'godmode-debug') 'SKILL.md'
  if (Test-Path -LiteralPath $debugSkill -PathType Leaf) {
    if (-not (Check-Contains $debugSkill 'GodMode Debug' 'installed godmode debug skill')) { $status = 1 }
  }

  $reviewSkill = Join-Path (Join-Path $script:userSkillsHome 'godmode-review') 'SKILL.md'
  if (Test-Path -LiteralPath $reviewSkill -PathType Leaf) {
    if (-not (Check-Contains $reviewSkill 'GodMode Review' 'installed godmode review skill')) { $status = 1 }
  }

  $greenfieldSkill = Join-Path (Join-Path $script:userSkillsHome 'greenfield-bootstrap') 'SKILL.md'
  if (Test-Path -LiteralPath $greenfieldSkill -PathType Leaf) {
    if (-not (Check-Contains $greenfieldSkill 'Greenfield Bootstrap' 'installed greenfield skill')) { $status = 1 }
  }

  if ($status -ne 0) {
    Write-Output ''
    Fail 'Global Codex setup check failed.' $status
  }

  Write-Output ''
  Write-Output 'Global Codex setup check passed.'
}

$script:repoRoot = Resolve-AbsolutePath (Join-Path $PSScriptRoot '..')
if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
  $defaultCodexHome = Join-Path $HOME '.codex'
}
else {
  $defaultCodexHome = $env:CODEX_HOME
}

$script:codexHome = Resolve-AbsolutePath $defaultCodexHome
$script:userSkillsHome = Resolve-AbsolutePath (Join-Path (Join-Path $HOME '.agents') 'skills')
$script:trustProject = $true
$script:checkOnly = $false

$index = 0
while ($index -lt $args.Count) {
  $argument = $args[$index]
  switch ($argument) {
    '--check' {
      $script:checkOnly = $true
      $index += 1
    }
    '-Check' {
      $script:checkOnly = $true
      $index += 1
    }
    '--codex-home' {
      if (($index + 1) -ge $args.Count) {
        Fail 'Missing value for option: --codex-home'
      }
      $script:codexHome = Resolve-AbsolutePath $args[$index + 1]
      $index += 2
    }
    '--user-skills-home' {
      if (($index + 1) -ge $args.Count) {
        Fail 'Missing value for option: --user-skills-home'
      }
      $script:userSkillsHome = Resolve-AbsolutePath $args[$index + 1]
      $index += 2
    }
    '--repo' {
      if (($index + 1) -ge $args.Count) {
        Fail 'Missing value for option: --repo'
      }
      $script:repoRoot = Resolve-AbsolutePath $args[$index + 1]
      $index += 2
    }
    '--no-trust-project' {
      $script:trustProject = $false
      $index += 1
    }
    '-h' {
      Show-Usage
      exit 0
    }
    '--help' {
      Show-Usage
      exit 0
    }
    default {
      [Console]::Error.WriteLine("Unknown option: $argument")
      [Console]::Error.WriteLine((Show-Usage))
      exit 1
    }
  }
}

$templateRoot = Join-Path $script:repoRoot 'templates/global-codex'
$script:sourceAgents = Join-Path $templateRoot 'AGENTS.md'
$script:sourceConfig = Join-Path $templateRoot 'config.toml'
$script:sourceRepoAgents = Join-Path (Join-Path $script:repoRoot '.codex') 'agents'
$script:sourceRepoSkills = Join-Path (Join-Path $script:repoRoot '.agents') 'skills'
$script:targetAgents = Join-Path $script:codexHome 'AGENTS.md'
$script:targetConfig = Join-Path $script:codexHome 'config.toml'
$script:targetAgentsDir = Join-Path $script:codexHome 'agents'
$script:playwrightOutput = Join-Path (Join-Path $script:codexHome 'playwright-output') 'isolated'
$timestamp = Get-Date -Format 'yyyy-MM-ddTHH-mm-ss'
$script:backupRoot = Join-Path (Join-Path (Join-Path $script:codexHome 'backups') 'install-archives') $timestamp
$script:tomlCodexHome = Convert-ToTomlPath $script:codexHome
$script:tomlRepoRoot = Convert-ToTomlPath $script:repoRoot

Require-File $script:sourceAgents
Require-File $script:sourceConfig
Require-Directory $script:sourceRepoAgents
Require-Directory $script:sourceRepoSkills

if ($script:checkOnly) {
  Run-Check
  exit 0
}

New-Item -ItemType Directory -Force -Path $script:codexHome | Out-Null
New-Item -ItemType Directory -Force -Path $script:userSkillsHome | Out-Null
New-Item -ItemType Directory -Force -Path $script:playwrightOutput | Out-Null
New-Item -ItemType Directory -Force -Path $script:targetAgentsDir | Out-Null

Archive-LegacyDiscoveryConflicts

Backup-Path $script:targetAgents
Backup-Path $script:targetConfig

Copy-Item -LiteralPath $script:sourceAgents -Destination $script:targetAgents -Force
Render-ConfigTemplate
Install-AgentFiles
Install-SkillDirs

if ($script:trustProject) {
  Ensure-ProjectTrust -ConfigPath $script:targetConfig -ProjectPath $script:tomlRepoRoot
}

Write-Output ''
Write-Output "Installed global Codex setup to $($script:codexHome)"
Write-Output "Installed global agents to $($script:targetAgentsDir)"
Write-Output "Installed user skill root at $($script:userSkillsHome)"
Write-Output "Prepared Playwright output directory at $($script:playwrightOutput)"

Run-Check
