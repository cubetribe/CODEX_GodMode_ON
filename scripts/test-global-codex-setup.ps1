Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$script:installer = Join-Path $PSScriptRoot 'apply-global-codex-setup.ps1'
$script:sourceAgents = Join-Path $script:repoRoot 'templates/global-codex/AGENTS.md'
$script:sourceProfiles = Join-Path $script:repoRoot 'templates/global-codex/profiles'
$script:sourceAgentsDir = Join-Path $script:repoRoot 'templates/global-codex/agents'
$script:tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('godmode-powershell-installer-tests-' + [guid]::NewGuid().ToString('N'))
$script:fakeCodex = Join-Path (Join-Path $script:tempRoot 'bin') 'codex.cmd'
$script:testCount = 0
$script:powerShellExe = (Get-Process -Id $PID).Path

function Write-Utf8File {
  param(
    [string]$Path,
    [string]$Content
  )

  $encoding = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Fail-Test {
  param([string]$Message)

  throw "[FAIL] $Message"
}

function Pass-Test {
  param([string]$Name)

  $script:testCount += 1
  Write-Output "[PASS] $Name"
}

function Assert-True {
  param(
    [bool]$Condition,
    [string]$Message
  )

  if (-not $Condition) {
    Fail-Test $Message
  }
}

function Assert-File {
  param([string]$Path)

  Assert-True (Test-Path -LiteralPath $Path -PathType Leaf) "expected file: $Path"
}

function Assert-Absent {
  param([string]$Path)

  Assert-True (-not (Test-Path -LiteralPath $Path)) "expected path to be absent: $Path"
}

function Assert-FilesEqual {
  param(
    [string]$Expected,
    [string]$Actual,
    [string]$Message
  )

  Assert-File $Expected
  Assert-File $Actual
  $expectedInfo = Get-Item -LiteralPath $Expected
  $actualInfo = Get-Item -LiteralPath $Actual
  $same = $expectedInfo.Length -eq $actualInfo.Length
  if ($same) {
    $same = (Get-FileHash -LiteralPath $Expected -Algorithm SHA256).Hash -eq
      (Get-FileHash -LiteralPath $Actual -Algorithm SHA256).Hash
  }
  Assert-True $same $Message
}

function New-TestCase {
  param([string]$Name)

  $root = Join-Path $script:tempRoot $Name
  New-Item -ItemType Directory -Force -Path $root | Out-Null
  [pscustomobject]@{
    Name = $Name
    Root = $root
    CodexHome = Join-Path $root 'codex-home'
    SkillsHome = Join-Path $root 'user-skills'
  }
}

function Invoke-Installer {
  param(
    [pscustomobject]$Case,
    [string[]]$ExtraArgs = @()
  )

  $arguments = @(
    '-NoLogo',
    '-NoProfile',
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    $script:installer,
    '--repo',
    $script:repoRoot,
    '--codex-home',
    $Case.CodexHome,
    '--user-skills-home',
    $Case.SkillsHome
  ) + $ExtraArgs

  $previousCodexBin = $env:CODEX_BIN
  try {
    $env:CODEX_BIN = $script:fakeCodex
    $output = @(& $script:powerShellExe @arguments 2>&1)
    $exitCode = $LASTEXITCODE
  }
  finally {
    $env:CODEX_BIN = $previousCodexBin
  }

  [pscustomobject]@{
    ExitCode = $exitCode
    Output = ($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
  }
}

function Assert-InstallerExit {
  param(
    [pscustomobject]$Result,
    [int]$Expected,
    [string]$Context
  )

  if ($Result.ExitCode -ne $Expected) {
    Fail-Test "$Context expected exit $Expected, got $($Result.ExitCode). Output:`n$($Result.Output)"
  }
}

function Get-ManagedManifest {
  param([pscustomobject]$Case)

  $entries = New-Object System.Collections.Generic.List[string]
  foreach ($rootSpec in @(
      [pscustomobject]@{ Label = 'codex'; Path = $Case.CodexHome },
      [pscustomobject]@{ Label = 'skills'; Path = $Case.SkillsHome }
    )) {
    if (-not (Test-Path -LiteralPath $rootSpec.Path -PathType Container)) {
      continue
    }
    $prefix = $rootSpec.Path.TrimEnd([char[]]@('\', '/')) + [System.IO.Path]::DirectorySeparatorChar
    foreach ($file in @(Get-ChildItem -LiteralPath $rootSpec.Path -File -Force -Recurse | Sort-Object FullName)) {
      $relative = $file.FullName.Substring($prefix.Length).Replace('\', '/')
      $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
      $entries.Add("$($rootSpec.Label):${relative}:$hash")
    }
  }
  ($entries | Sort-Object) -join "`n"
}

function Get-UnmarkedV11AgentsContent {
  $result = @()
  foreach ($line in [System.IO.File]::ReadAllLines($script:sourceAgents)) {
    if ($line -eq '<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->' -or
        $line -eq '<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->' -or
        $line.Contains('Use bounded proactive subagents') -or
        $line.Contains('Parallelize independent read-only discovery') -or
        $line.Contains('Let custom agents inherit the parent session')) {
      continue
    }
    $updatedLine = $line.Replace('`godmode-swiftui`:', '`swiftui`:')
    $updatedLine = $updatedLine.Replace('`godmode-web`:', '`web`:')
    $updatedLine = $updatedLine.Replace('`godmode-flutter`:', '`flutter`:')
    $updatedLine = $updatedLine.Replace('`godmode-review`:', '`review`:')
    $result += $updatedLine
  }
  ($result -join "`n") + "`n"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $script:fakeCodex) | Out-Null
$fakeCodexContent = @'
@echo off
if "%~1"=="--version" (
  echo codex-cli 0.144.1
  exit /b 0
)
if "%~1"=="help" if "%~2"=="doctor" exit /b 0
exit /b 1
'@
$fakeCodexContent = $fakeCodexContent -replace "(?<!`r)`n", "`r`n"
Write-Utf8File -Path $script:fakeCodex -Content $fakeCodexContent

try {
  # Clean install plus both supported check spellings.
  $case = New-TestCase 'clean'
  $result = Invoke-Installer $case
  Assert-InstallerExit $result 0 'clean install'
  Assert-File (Join-Path $case.CodexHome 'config.toml')
  Assert-File (Join-Path $case.CodexHome 'AGENTS.md')
  Assert-File (Join-Path $case.CodexHome 'godmode-web.config.toml')
  Assert-File (Join-Path (Join-Path (Join-Path $case.SkillsHome 'godmode-workflow') 'agents') 'openai.yaml')
  Assert-InstallerExit (Invoke-Installer $case @('-Check')) 0 'clean -Check'
  Assert-InstallerExit (Invoke-Installer $case @('--check')) 0 'clean --check'
  Pass-Test 'clean install and exact checks'

  # Existing config must survive byte-for-byte, including syntax forms that
  # cannot be preserved safely by a line-oriented TOML merger.
  $case = New-TestCase 'preserve-config'
  New-Item -ItemType Directory -Force -Path $case.CodexHome | Out-Null
  $configPath = Join-Path $case.CodexHome 'config.toml'
  $configContent = @'
"quoted.root" = "keep = exact"
dotted.root = "also exact"
message = """
first line
[not.a.section]
last line
"""

[custom]
value = "untouched"
'@
  Write-Utf8File -Path $configPath -Content $configContent
  $beforeHash = (Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash
  $beforeLength = (Get-Item -LiteralPath $configPath).Length
  Assert-InstallerExit (Invoke-Installer $case) 0 'existing config install'
  $afterHash = (Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash
  $afterLength = (Get-Item -LiteralPath $configPath).Length
  Assert-True ($beforeHash -eq $afterHash -and $beforeLength -eq $afterLength) 'existing config changed'
  Assert-InstallerExit (Invoke-Installer $case @('-Check')) 0 'existing config check'
  Pass-Test 'existing config byte preservation'

  # The known v1.1 guidance must migrate without duplication even when it was
  # written by a Windows checkout with CRLF line endings.
  $case = New-TestCase 'agents-v1-1-crlf'
  New-Item -ItemType Directory -Force -Path $case.CodexHome | Out-Null
  $legacyAgents = (Get-UnmarkedV11AgentsContent) -replace "(?<!`r)`n", "`r`n"
  $agentsPath = Join-Path $case.CodexHome 'AGENTS.md'
  Write-Utf8File -Path $agentsPath -Content $legacyAgents
  Assert-InstallerExit (Invoke-Installer $case) 0 'CRLF v1.1 AGENTS migration'
  Assert-FilesEqual $script:sourceAgents $agentsPath 'CRLF v1.1 AGENTS did not migrate exactly'
  $migratedAgents = [System.IO.File]::ReadAllText($agentsPath)
  Assert-True (-not $migratedAgents.Contains('## Preserved User Guidance')) 'v1.1 guidance was duplicated as custom content'
  Pass-Test 'CRLF v1.1 AGENTS migration'

  # Genuinely custom unmarked guidance is retained exactly once and remains
  # byte-stable on a second apply.
  $case = New-TestCase 'custom-agents'
  New-Item -ItemType Directory -Force -Path $case.CodexHome | Out-Null
  $agentsPath = Join-Path $case.CodexHome 'AGENTS.md'
  $customGuidance = "# My custom global rule`n`n- Keep this exact guidance.`n"
  Write-Utf8File -Path $agentsPath -Content $customGuidance
  Assert-InstallerExit (Invoke-Installer $case) 0 'custom AGENTS install'
  $firstCustomInstall = [System.IO.File]::ReadAllText($agentsPath)
  Assert-True ($firstCustomInstall.Contains('## Preserved User Guidance')) 'custom guidance section is missing'
  $customCount = [regex]::Matches($firstCustomInstall, [regex]::Escape('- Keep this exact guidance.')).Count
  Assert-True ($customCount -eq 1) 'custom guidance was duplicated'
  Assert-InstallerExit (Invoke-Installer $case) 0 'custom AGENTS reinstall'
  $secondCustomInstall = [System.IO.File]::ReadAllText($agentsPath)
  Assert-True ($firstCustomInstall -ceq $secondCustomInstall) 'custom AGENTS changed on reinstall'
  Pass-Test 'custom AGENTS preservation and idempotence'

  # A conflicting managed profile must stop before writes with exit 4. The
  # explicit reset path then backs it up and installs the exact package file.
  $case = New-TestCase 'profile-conflict'
  New-Item -ItemType Directory -Force -Path $case.CodexHome | Out-Null
  $profileName = 'godmode-web.config.toml'
  $targetProfile = Join-Path $case.CodexHome $profileName
  Write-Utf8File -Path $targetProfile -Content "# user-modified managed profile`n"
  Assert-InstallerExit (Invoke-Installer $case) 4 'managed profile conflict'
  Assert-Absent (Join-Path $case.CodexHome 'AGENTS.md')
  Assert-Absent (Join-Path $case.CodexHome 'config.toml')
  Assert-Absent $case.SkillsHome
  Assert-InstallerExit (Invoke-Installer $case @('--reset-config')) 0 'managed profile reset'
  Assert-FilesEqual (Join-Path $script:sourceProfiles $profileName) $targetProfile 'managed profile reset was not exact'
  $profileBackups = @(Get-ChildItem -LiteralPath (Join-Path $case.CodexHome 'backups') -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq $profileName })
  Assert-True ($profileBackups.Count -gt 0) 'managed profile reset backup is missing'
  Pass-Test 'managed profile conflict and reset'

  # Separate reset processes must never overwrite one another's backups.
  $case = New-TestCase 'unique-backups'
  Assert-InstallerExit (Invoke-Installer $case) 0 'backup baseline install'
  $configPath = Join-Path $case.CodexHome 'config.toml'
  Write-Utf8File -Path $configPath -Content "custom_reset = ""first""`n"
  Assert-InstallerExit (Invoke-Installer $case @('--reset-config')) 0 'first config reset'
  Write-Utf8File -Path $configPath -Content "custom_reset = ""second""`n"
  Assert-InstallerExit (Invoke-Installer $case @('--reset-config')) 0 'second config reset'
  $configBackups = @(Get-ChildItem -LiteralPath (Join-Path $case.CodexHome 'backups') -File -Recurse | Where-Object { $_.Name -eq 'config.toml' })
  Assert-True ($configBackups.Count -ge 2) 'reset runs reused one backup target'
  Pass-Test 'unique backup archives'

  # Malformed markers must fail before config, agents, profiles, or skills are written.
  $case = New-TestCase 'malformed-markers'
  New-Item -ItemType Directory -Force -Path $case.CodexHome | Out-Null
  $malformed = @'
<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->
<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->
<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->
'@
  Write-Utf8File -Path (Join-Path $case.CodexHome 'AGENTS.md') -Content $malformed
  Assert-InstallerExit (Invoke-Installer $case) 1 'malformed AGENTS markers'
  Assert-Absent (Join-Path $case.CodexHome 'config.toml')
  Assert-Absent (Join-Path $case.CodexHome 'agents')
  Assert-Absent (Join-Path $case.CodexHome 'godmode-web.config.toml')
  Assert-Absent $case.SkillsHome
  Pass-Test 'malformed marker preflight'

  # Marker text embedded in user guidance is not a managed marker line. It
  # must stay outside the exact managed block boundaries during replacement.
  $case = New-TestCase 'inline-marker-guidance'
  Assert-InstallerExit (Invoke-Installer $case) 0 'inline marker baseline install'
  $agentsPath = Join-Path $case.CodexHome 'AGENTS.md'
  $managedAgents = [System.IO.File]::ReadAllText($agentsPath)
  $inlineGuidance = 'Do not type <!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN --> manually.' + "`n"
  Write-Utf8File -Path $agentsPath -Content ($inlineGuidance + $managedAgents)
  Assert-InstallerExit (Invoke-Installer $case) 0 'inline marker reinstall'
  $updatedAgents = [System.IO.File]::ReadAllText($agentsPath)
  Assert-True ($updatedAgents.StartsWith($inlineGuidance, [System.StringComparison]::Ordinal)) 'inline marker guidance changed'
  Assert-True ($updatedAgents.Contains('# ~/.codex/AGENTS.md')) 'managed AGENTS block is missing after inline marker reinstall'
  Pass-Test 'inline marker guidance preservation'

  # Exact checks detect changed agents and stale files in owned skills. Apply
  # must restore exact package content without relying on substring checks.
  $case = New-TestCase 'exact-drift'
  Assert-InstallerExit (Invoke-Installer $case) 0 'drift baseline install'
  $targetAgent = Join-Path (Join-Path $case.CodexHome 'agents') 'researcher.toml'
  [System.IO.File]::AppendAllText($targetAgent, "# drift`n")
  $staleSkillFile = Join-Path (Join-Path $case.SkillsHome 'godmode-workflow') 'stale.txt'
  Write-Utf8File -Path $staleSkillFile -Content "stale`n"
  Assert-InstallerExit (Invoke-Installer $case @('-Check')) 1 'exact drift check'
  Assert-InstallerExit (Invoke-Installer $case) 0 'exact drift repair'
  Assert-FilesEqual (Join-Path $script:sourceAgentsDir 'researcher.toml') $targetAgent 'agent drift was not repaired'
  Assert-Absent $staleSkillFile
  Assert-InstallerExit (Invoke-Installer $case @('--check')) 0 'repaired exact check'
  Pass-Test 'exact drift detection and repair'

  # A repeated apply with no source or target drift must leave all managed file
  # bytes unchanged.
  $case = New-TestCase 'idempotence'
  Assert-InstallerExit (Invoke-Installer $case) 0 'idempotence first install'
  $beforeManifest = Get-ManagedManifest $case
  Assert-InstallerExit (Invoke-Installer $case) 0 'idempotence second install'
  $afterManifest = Get-ManagedManifest $case
  Assert-True ($beforeManifest -ceq $afterManifest) 'second install changed managed runtime bytes'
  Pass-Test 'idempotent repeated install'

  Write-Output "`nAll $($script:testCount) PowerShell installer regression groups passed."
}
finally {
  if (Test-Path -LiteralPath $script:tempRoot) {
    Remove-Item -LiteralPath $script:tempRoot -Recurse -Force
  }
}
