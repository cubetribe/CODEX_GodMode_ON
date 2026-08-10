Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$script:installer = Join-Path $PSScriptRoot 'apply-global-codex-setup.ps1'
$script:sourceAgents = Join-Path $script:repoRoot 'templates/global-codex/AGENTS.md'
$script:sourceProfiles = Join-Path $script:repoRoot 'templates/global-codex/profiles'
$script:sourceAgentsDir = Join-Path $script:repoRoot 'templates/global-codex/agents'
$script:sourceInventory = Join-Path $script:repoRoot 'templates/global-codex/managed-assets.tsv'
$script:legacyV1Agents = Join-Path $script:repoRoot 'tests/fixtures/global-codex-1.1/AGENTS.md'
$script:legacyV2 = Join-Path $script:repoRoot 'tests/fixtures/global-codex-2.0'
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
  $previousErrorActionPreference = $ErrorActionPreference
  try {
    $env:CODEX_BIN = $script:fakeCodex
    # Windows PowerShell 5.1 promotes redirected native stderr to a
    # NativeCommandError when the caller uses Stop. Installer warnings are
    # expected output, so capture them and assert the child process exit code.
    $ErrorActionPreference = 'Continue'
    $output = @(& $script:powerShellExe @arguments 2>&1)
    $exitCode = $LASTEXITCODE
  }
  finally {
    $env:CODEX_BIN = $previousCodexBin
    $ErrorActionPreference = $previousErrorActionPreference
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
  [System.IO.File]::ReadAllText($script:legacyV1Agents)
}

function Get-LegacyV2ConfigContent {
  param([string]$CodexHome)

  $tomlHome = (($CodexHome -replace '\\', '/') -replace '"', '\"')
  [System.IO.File]::ReadAllText((Join-Path $script:legacyV2 'config.toml')).Replace('__CODEX_HOME__', $tomlHome)
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
  Assert-FilesEqual $script:sourceInventory (Join-Path (Join-Path $case.CodexHome 'godmode') 'managed-assets.tsv') 'managed inventory was not installed exactly'
  Assert-File (Join-Path (Join-Path (Join-Path $case.SkillsHome 'godmode-workflow') 'agents') 'openai.yaml')
  $agentCount = @(Get-ChildItem -LiteralPath (Join-Path $case.CodexHome 'agents') -Filter '*.toml' -File).Count
  $skillCount = @(Get-ChildItem -LiteralPath $case.SkillsHome -Directory).Count
  Assert-True ($agentCount -eq 7) "expected 7 managed agents, got $agentCount"
  Assert-True ($skillCount -eq 9) "expected 9 managed skills, got $skillCount"
  Assert-Absent (Join-Path (Join-Path $case.CodexHome 'agents') 'researcher.toml')
  Assert-Absent (Join-Path $case.SkillsHome 'godmode-departments')
  Assert-InstallerExit (Invoke-Installer $case @('-Check')) 0 'clean -Check'
  Assert-InstallerExit (Invoke-Installer $case @('--check')) 0 'clean --check'
  Pass-Test 'clean install and exact checks'

  # Exact 2.0 assets are backed up and retired; normalized CRLF is accepted and
  # custom agents or skills are left alone.
  $case = New-TestCase 'upgrade-v2'
  $targetAgents = Join-Path $case.CodexHome 'agents'
  New-Item -ItemType Directory -Force -Path $targetAgents | Out-Null
  New-Item -ItemType Directory -Force -Path $case.SkillsHome | Out-Null
  foreach ($legacyAgent in @(Get-ChildItem -LiteralPath (Join-Path $script:legacyV2 'agents') -Filter '*.toml' -File)) {
    Copy-Item -LiteralPath $legacyAgent.FullName -Destination $targetAgents
  }
  Copy-Item -LiteralPath (Join-Path (Join-Path $script:legacyV2 'skills') 'godmode-departments') -Destination $case.SkillsHome -Recurse
  $legacyConfigPath = Join-Path $case.CodexHome 'config.toml'
  $repoTrustPath = (($script:repoRoot -replace '\\', '/') -replace '"', '\"')
  $legacyConfigContent = (Get-LegacyV2ConfigContent $case.CodexHome) + "`n[projects.""$repoTrustPath""]`ntrust_level = ""trusted""`n"
  Write-Utf8File -Path $legacyConfigPath -Content $legacyConfigContent
  $legacyConfigHash = (Get-FileHash -LiteralPath $legacyConfigPath -Algorithm SHA256).Hash
  $researcherFixture = Join-Path (Join-Path $script:legacyV2 'agents') 'researcher.toml'
  $researcherTarget = Join-Path $targetAgents 'researcher.toml'
  $crlfResearcher = ([System.IO.File]::ReadAllText($researcherFixture) -replace "(?<!`r)`n", "`r`n")
  Write-Utf8File -Path $researcherTarget -Content $crlfResearcher
  Write-Utf8File -Path (Join-Path $targetAgents 'custom.toml') -Content "name = ""custom""`n"
  $customSkill = Join-Path $case.SkillsHome 'custom-skill'
  New-Item -ItemType Directory -Force -Path $customSkill | Out-Null
  Write-Utf8File -Path (Join-Path $customSkill 'keep.txt') -Content "custom`n"
  Assert-InstallerExit (Invoke-Installer $case) 0 'exact 2.0 upgrade'
  foreach ($retired in @('architect', 'builder', 'github_manager', 'quality_operations', 'researcher', 'scribe', 'workspace_governance')) {
    Assert-Absent (Join-Path $targetAgents ($retired + '.toml'))
    $backups = @(Get-ChildItem -LiteralPath (Join-Path $case.CodexHome 'backups') -File -Recurse | Where-Object { $_.Name -eq ($retired + '.toml') })
    Assert-True ($backups.Count -gt 0) "retired agent backup missing: $retired"
  }
  Assert-Absent (Join-Path $case.SkillsHome 'godmode-departments')
  Assert-File (Join-Path $targetAgents 'custom.toml')
  Assert-File (Join-Path $customSkill 'keep.txt')
  $migratedConfig = [System.IO.File]::ReadAllText($legacyConfigPath)
  Assert-True ($migratedConfig.Contains('max_threads = 2')) 'legacy config did not receive the Lean thread cap'
  Assert-True (-not $migratedConfig.Contains('max_depth')) 'legacy max_depth survived migration'
  Assert-True (-not $migratedConfig.Contains('[mcp_servers.playwright]')) 'legacy Playwright MCP survived migration'
  $configBackups = @(Get-ChildItem -LiteralPath (Join-Path $case.CodexHome 'backups') -File -Recurse | Where-Object { $_.Name -eq 'config.toml' })
  Assert-True ($configBackups.Count -eq 1) 'legacy 2.0 config backup is missing or ambiguous'
  Assert-True ((Get-FileHash -LiteralPath $configBackups[0].FullName -Algorithm SHA256).Hash -eq $legacyConfigHash) 'legacy 2.0 config backup changed'
  Assert-InstallerExit (Invoke-Installer $case @('--check')) 0 'exact 2.0 upgrade check'
  Pass-Test 'exact 2.0 retirement and Lean config migration with backup'

  # A modified retired asset conflicts before any package write.
  $case = New-TestCase 'modified-retired'
  $targetAgents = Join-Path $case.CodexHome 'agents'
  New-Item -ItemType Directory -Force -Path $targetAgents | Out-Null
  $researcherTarget = Join-Path $targetAgents 'researcher.toml'
  Copy-Item -LiteralPath $researcherFixture -Destination $researcherTarget
  [System.IO.File]::AppendAllText($researcherTarget, "# user modification`n")
  Assert-InstallerExit (Invoke-Installer $case) 5 'modified retired conflict'
  Assert-Absent (Join-Path $case.CodexHome 'AGENTS.md')
  Assert-Absent (Join-Path $case.CodexHome 'config.toml')
  Assert-Absent $case.SkillsHome
  Assert-True ([System.IO.File]::ReadAllText($researcherTarget).Contains('# user modification')) 'modified retired agent was changed'
  Pass-Test 'modified retired asset no-write conflict'

  # Unsafe retired paths and an unusable inventory parent all fail before writes.
  $case = New-TestCase 'modified-retired-skill'
  New-Item -ItemType Directory -Force -Path $case.SkillsHome | Out-Null
  $retiredSkill = Join-Path $case.SkillsHome 'godmode-departments'
  Copy-Item -LiteralPath (Join-Path (Join-Path $script:legacyV2 'skills') 'godmode-departments') -Destination $retiredSkill -Recurse
  Write-Utf8File -Path (Join-Path $retiredSkill 'extra.txt') -Content "user content`n"
  Assert-InstallerExit (Invoke-Installer $case) 5 'modified retired skill conflict'
  Assert-Absent $case.CodexHome
  Assert-File (Join-Path $retiredSkill 'extra.txt')

  $case = New-TestCase 'retired-wrong-type'
  $wrongType = Join-Path (Join-Path $case.CodexHome 'agents') 'researcher.toml'
  New-Item -ItemType Directory -Force -Path $wrongType | Out-Null
  Assert-InstallerExit (Invoke-Installer $case) 5 'retired wrong-type conflict'
  Assert-Absent (Join-Path $case.CodexHome 'AGENTS.md')
  Assert-Absent (Join-Path $case.CodexHome 'config.toml')

  $case = New-TestCase 'retired-dangling-link'
  $targetAgents = Join-Path $case.CodexHome 'agents'
  New-Item -ItemType Directory -Force -Path $targetAgents | Out-Null
  $danglingLink = Join-Path $targetAgents 'researcher.toml'
  New-Item -ItemType SymbolicLink -Path $danglingLink -Target (Join-Path $case.Root 'missing-researcher') -Force | Out-Null
  Assert-InstallerExit (Invoke-Installer $case) 5 'retired dangling-link conflict'
  $linkItems = @(Get-ChildItem -LiteralPath $targetAgents -Force | Where-Object { $_.Name -ceq 'researcher.toml' })
  Assert-True ($linkItems.Count -eq 1 -and ($linkItems[0].Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) 'dangling retired link was changed'
  Assert-Absent (Join-Path $case.CodexHome 'AGENTS.md')
  Assert-Absent (Join-Path $case.CodexHome 'config.toml')

  $case = New-TestCase 'inventory-parent-conflict'
  New-Item -ItemType Directory -Force -Path $case.CodexHome | Out-Null
  Write-Utf8File -Path (Join-Path $case.CodexHome 'godmode') -Content "not a directory`n"
  Assert-InstallerExit (Invoke-Installer $case) 5 'inventory parent conflict'
  Assert-Absent (Join-Path $case.CodexHome 'AGENTS.md')
  Assert-Absent (Join-Path $case.CodexHome 'config.toml')
  Assert-Absent (Join-Path $case.CodexHome 'agents')
  Assert-Absent $case.SkillsHome
  Pass-Test 'unsafe migration targets fail before writes'

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

  # A 2.0-looking config with any user modification remains user-owned and exact.
  $case = New-TestCase 'modified-v2-config'
  New-Item -ItemType Directory -Force -Path $case.CodexHome | Out-Null
  $configPath = Join-Path $case.CodexHome 'config.toml'
  $modifiedLegacyConfig = (Get-LegacyV2ConfigContent $case.CodexHome) + "`n[projects.""C:/manually/changed/source""]`ntrust_level = ""trusted""`n"
  Write-Utf8File -Path $configPath -Content $modifiedLegacyConfig
  $beforeHash = (Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash
  $beforeLength = (Get-Item -LiteralPath $configPath).Length
  Assert-InstallerExit (Invoke-Installer $case) 0 'modified 2.0 config install'
  Assert-True ((Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash -eq $beforeHash -and (Get-Item -LiteralPath $configPath).Length -eq $beforeLength) 'modified 2.0 config changed'
  Assert-InstallerExit (Invoke-Installer $case @('--check')) 0 'modified 2.0 config check'
  Pass-Test 'modified 2.0 config preservation'

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
  $targetAgent = Join-Path (Join-Path $case.CodexHome 'agents') 'api_guardian.toml'
  [System.IO.File]::AppendAllText($targetAgent, "# drift`n")
  $staleSkillFile = Join-Path (Join-Path $case.SkillsHome 'godmode-workflow') 'stale.txt'
  Write-Utf8File -Path $staleSkillFile -Content "stale`n"
  Assert-InstallerExit (Invoke-Installer $case @('-Check')) 1 'exact drift check'
  Assert-InstallerExit (Invoke-Installer $case) 0 'exact drift repair'
  Assert-FilesEqual (Join-Path $script:sourceAgentsDir 'api_guardian.toml') $targetAgent 'agent drift was not repaired'
  Assert-Absent $staleSkillFile
  Assert-InstallerExit (Invoke-Installer $case @('--check')) 0 'repaired exact check'
  Pass-Test 'exact drift detection and repair'

  # Invalid arguments and an incompatible CLI fail with stable preflight codes.
  $case = New-TestCase 'cli-preflight'
  Assert-InstallerExit (Invoke-Installer $case @('--unknown-option')) 2 'unknown argument preflight'
  Assert-InstallerExit (Invoke-Installer $case @('--codex-home')) 2 'missing argument value preflight'
  $oldFakeCodexContent = $fakeCodexContent -replace '0\.144\.1', '0.143.9'
  Write-Utf8File -Path $script:fakeCodex -Content $oldFakeCodexContent
  Assert-InstallerExit (Invoke-Installer $case) 3 'incompatible CLI preflight'
  Write-Utf8File -Path $script:fakeCodex -Content $fakeCodexContent
  Pass-Test 'argument and CLI preflight exit codes'

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
