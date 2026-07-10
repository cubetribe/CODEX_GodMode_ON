Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Show-Usage {
  @'
Usage:
  ./scripts/apply-global-codex-setup.ps1 [options]

Options:
  --check, -Check        Verify managed files exactly without applying changes
  --codex-home PATH      Override the target Codex home directory
  --user-skills-home PATH
                         Override the target user skills directory
  --repo PATH            Override the repository root used for package sources and trust
  --no-trust-project     Do not add or check the repository trust entry
  --reset-config         Back up and replace config.toml and conflicting managed profiles
  --reset-agents         Back up and replace AGENTS.md instead of preserving user guidance
  -h, --help             Show this help text

Environment:
  CODEX_BIN              Codex executable name or path (default: resolved codex on PATH)
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

function Invalid-Argument {
  param([string]$Message)

  [Console]::Error.WriteLine($Message)
  [Console]::Error.WriteLine((Show-Usage))
  exit 2
}

function Resolve-AbsolutePath {
  param([string]$Path)

  $resolved = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
  [System.IO.Path]::GetFullPath($resolved)
}

function Convert-ToTomlPath {
  param([string]$Path)

  (($Path -replace '\\', '/') -replace '"', '\"')
}

function Same-Path {
  param(
    [string]$Left,
    [string]$Right
  )

  [string]::Equals(
    [System.IO.Path]::GetFullPath($Left).TrimEnd('\', '/'),
    [System.IO.Path]::GetFullPath($Right).TrimEnd('\', '/'),
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

function Test-FilesEqual {
  param(
    [string]$Left,
    [string]$Right
  )

  if (-not (Test-Path -LiteralPath $Left -PathType Leaf) -or -not (Test-Path -LiteralPath $Right -PathType Leaf)) {
    return $false
  }

  $leftInfo = Get-Item -LiteralPath $Left
  $rightInfo = Get-Item -LiteralPath $Right
  if ($leftInfo.Length -ne $rightInfo.Length) {
    return $false
  }

  (Get-FileHash -LiteralPath $Left -Algorithm SHA256).Hash -eq
    (Get-FileHash -LiteralPath $Right -Algorithm SHA256).Hash
}

function Get-NormalizedText {
  param([string]$Path)

  ([System.IO.File]::ReadAllText($Path) -replace "`r`n", "`n") -replace "`r", "`n"
}

function Get-NormalizedSha256 {
  param([string]$Path)

  $normalized = Get-NormalizedText $Path
  $encoding = New-Object System.Text.UTF8Encoding($false)
  $bytes = $encoding.GetBytes($normalized)
  $sha = [System.Security.Cryptography.SHA256]::Create()
  try {
    $hash = $sha.ComputeHash($bytes)
    ([System.BitConverter]::ToString($hash) -replace '-', '').ToLowerInvariant()
  }
  finally {
    $sha.Dispose()
  }
}

function Get-DirectoryManifest {
  param([string]$Root)

  if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
    return @()
  }

  $rootWithSeparator = $Root.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
  @(
    Get-ChildItem -LiteralPath $Root -Force -Recurse | ForEach-Object {
      $relative = $_.FullName.Substring($rootWithSeparator.Length).Replace('\', '/')
      if ($_.PSIsContainer) {
        "D:$relative"
      }
      else {
        $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        "F:${relative}:$hash"
      }
    } | Sort-Object
  )
}

function Test-DirectoriesEqual {
  param(
    [string]$Left,
    [string]$Right
  )

  if (-not (Test-Path -LiteralPath $Left -PathType Container) -or -not (Test-Path -LiteralPath $Right -PathType Container)) {
    return $false
  }

  $difference = @(Compare-Object (Get-DirectoryManifest $Left) (Get-DirectoryManifest $Right))
  $difference.Count -eq 0
}

function Get-AgentsMarkerState {
  param([string]$Path)

  $lines = @([System.IO.File]::ReadAllLines($Path))
  $beginIndexes = @()
  $endIndexes = @()
  for ($index = 0; $index -lt $lines.Count; $index += 1) {
    if ($lines[$index] -eq $script:agentsMarkerBegin) {
      $beginIndexes += $index
    }
    if ($lines[$index] -eq $script:agentsMarkerEnd) {
      $endIndexes += $index
    }
  }

  if ($beginIndexes.Count -eq 0 -and $endIndexes.Count -eq 0) {
    return 'none'
  }
  if ($beginIndexes.Count -eq 1 -and $endIndexes.Count -eq 1 -and $beginIndexes[0] -lt $endIndexes[0]) {
    return 'valid'
  }
  'invalid'
}

function Get-ManagedAgentsMatch {
  param([string]$Content)

  $pattern = '(?ms)^{0}\r?\n.*?^{1}(?:\r?\n|$)' -f
    [regex]::Escape($script:agentsMarkerBegin),
    [regex]::Escape($script:agentsMarkerEnd)
  [regex]::Match($Content, $pattern)
}

function Get-ManagedAgentsContent {
  param([string]$Path)

  $content = [System.IO.File]::ReadAllText($Path)
  $managedMatch = Get-ManagedAgentsMatch $content
  if (-not $managedMatch.Success) {
    return $null
  }
  $managedMatch.Value
}

function Get-SourceWithoutMarkers {
  $lines = @([System.IO.File]::ReadAllLines($script:sourceAgents) | Where-Object {
      $_ -ne $script:agentsMarkerBegin -and $_ -ne $script:agentsMarkerEnd
    })
  ($lines -join "`n") + "`n"
}

function Test-KnownUnmarkedAgents {
  param([string]$Path)

  $existing = Get-NormalizedText $Path
  if ($existing -eq (Get-SourceWithoutMarkers)) {
    return $true
  }
  (Get-NormalizedSha256 $Path) -eq $script:legacyV11AgentsSha256
}

function Get-ProjectTrustHeader {
  "[projects.""$($script:tomlRepoRoot)""]"
}

function Test-ProjectTrust {
  param([string]$ConfigPath)

  Select-String -LiteralPath $ConfigPath -Pattern (Get-ProjectTrustHeader) -SimpleMatch -Quiet
}

function Warn-LegacyInlineProfiles {
  param([string]$ConfigPath)

  if (Select-String -LiteralPath $ConfigPath -Pattern '^\s*\[profiles\.' -Quiet) {
    [Console]::Error.WriteLine("[warn] $ConfigPath contains legacy inline [profiles.*] tables; Codex >= 0.134.0 loads separate NAME.config.toml files instead.")
  }
}

function Resolve-CodexRuntime {
  $requested = if ([string]::IsNullOrWhiteSpace($env:CODEX_BIN)) { 'codex' } else { $env:CODEX_BIN }
  $candidate = $null

  if ($requested.IndexOfAny(@([char]'\', [char]'/')) -ge 0) {
    if (-not (Test-Path -LiteralPath $requested -PathType Leaf)) {
      Fail "Codex executable is missing: $requested" 3
    }
    $candidate = Resolve-AbsolutePath $requested
  }
  else {
    $commands = @(Get-Command $requested -All -CommandType Application -ErrorAction SilentlyContinue)
    if ($commands.Count -eq 0) {
      Fail "Codex CLI was not found. Install Codex >= $($script:minimumCodexVersion) or set CODEX_BIN." 3
    }
    $candidate = $commands[0].Source
  }

  $versionOutput = @(& $candidate --version 2>&1)
  $versionExit = $LASTEXITCODE
  $versionText = ($versionOutput -join ' ')
  if ($versionExit -ne 0) {
    Fail "Could not query Codex version from ${candidate}: $versionText" 3
  }
  $match = [regex]::Match($versionText, '(\d+)\.(\d+)\.(\d+)')
  if (-not $match.Success) {
    Fail "Could not parse Codex version from: $versionText" 3
  }
  $actualVersion = [version]$match.Value
  if ($actualVersion -lt [version]$script:minimumCodexVersion) {
    Fail "Incompatible Codex CLI $actualVersion at $candidate; version >= $($script:minimumCodexVersion) is required." 3
  }

  & $candidate help doctor *> $null
  if ($LASTEXITCODE -ne 0) {
    Fail "Codex CLI $actualVersion at $candidate does not support 'codex help doctor'." 3
  }

  $script:codexBin = $candidate
  Write-Output "Codex preflight: $candidate ($versionText)"
}

function Preflight-SourcesAndTargets {
  Require-File $script:sourceAgents
  Require-File $script:sourceConfig
  Require-Directory $script:sourceRepoAgents
  Require-Directory $script:sourceRepoProfiles
  Require-Directory $script:sourceRepoSkills
  foreach ($profileName in $script:profileNames) {
    Require-File (Join-Path $script:sourceRepoProfiles $profileName)
  }

  if ((Get-AgentsMarkerState $script:sourceAgents) -ne 'valid') {
    Fail "Packaged AGENTS.md must contain exactly one ordered managed marker pair: $($script:sourceAgents)"
  }
  if ((Test-Path -LiteralPath $script:targetConfig) -and -not (Test-Path -LiteralPath $script:targetConfig -PathType Leaf)) {
    Fail "Target config is not a regular file: $($script:targetConfig)"
  }
  if ((Test-Path -LiteralPath $script:targetAgents) -and -not (Test-Path -LiteralPath $script:targetAgents -PathType Leaf)) {
    Fail "Target AGENTS is not a regular file: $($script:targetAgents)"
  }
  if ((Test-Path -LiteralPath $script:targetAgents -PathType Leaf) -and (Get-AgentsMarkerState $script:targetAgents) -eq 'invalid') {
    Fail "Malformed managed markers in $($script:targetAgents); expected exactly one BEGIN followed by one END."
  }

  foreach ($profileName in $script:profileNames) {
    $sourceProfile = Join-Path $script:sourceRepoProfiles $profileName
    $targetProfile = Join-Path $script:codexHome $profileName
    if ((Test-Path -LiteralPath $targetProfile) -and -not (Test-Path -LiteralPath $targetProfile -PathType Leaf)) {
      Fail "Managed profile target is not a regular file: $targetProfile" 4
    }
    if ((Test-Path -LiteralPath $targetProfile -PathType Leaf) -and -not (Test-FilesEqual $sourceProfile $targetProfile) -and -not $script:resetConfig) {
      Fail "Managed profile conflict: $targetProfile. Re-run with --reset-config to back up and replace managed profiles." 4
    }
  }
}

function Backup-Path {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    return
  }

  $destination = $null
  if (Same-Path $Path $script:targetAgents) {
    $destination = Join-Path (Join-Path $script:backupRoot 'root') 'AGENTS.md'
  }
  elseif (Same-Path $Path $script:targetConfig) {
    $destination = Join-Path (Join-Path $script:backupRoot 'root') 'config.toml'
  }
  elseif (Same-Path (Split-Path -Parent $Path) $script:targetAgentsDir) {
    $destination = Join-Path (Join-Path $script:backupRoot 'agents') (Split-Path -Leaf $Path)
  }
  elseif (Same-Path (Split-Path -Parent $Path) $script:userSkillsHome) {
    $destination = Join-Path (Join-Path $script:backupRoot 'skills') (Split-Path -Leaf $Path)
  }
  elseif ((Same-Path (Split-Path -Parent $Path) $script:codexHome) -and $Path.EndsWith('.config.toml')) {
    $destination = Join-Path (Join-Path $script:backupRoot 'profiles') (Split-Path -Leaf $Path)
  }
  else {
    $destination = Join-Path (Join-Path $script:backupRoot 'misc') (Split-Path -Leaf $Path)
  }

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
  Copy-Item -LiteralPath $Path -Destination $destination -Recurse -Force
  Write-Output "Backed up $Path -> $destination"
}

function Install-FileAtomically {
  param(
    [string]$Source,
    [string]$Target
  )

  $targetDirectory = Split-Path -Parent $Target
  $temporary = Join-Path $targetDirectory ('.' + (Split-Path -Leaf $Target) + '.tmp.' + [guid]::NewGuid().ToString('N'))
  Copy-Item -LiteralPath $Source -Destination $temporary -Force
  Move-Item -LiteralPath $temporary -Destination $Target -Force
}

function Archive-LegacyDiscoveryConflicts {
  $found = $false
  $pairs = @(
    [pscustomobject]@{ Root = $script:targetAgentsDir; Category = 'agents' },
    [pscustomobject]@{ Root = $script:userSkillsHome; Category = 'skills' }
  )
  foreach ($pair in $pairs) {
    $root = $pair.Root
    $category = $pair.Category
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
      continue
    }
    $artifacts = @(Get-ChildItem -LiteralPath $root -Force | Where-Object { $_.Name -like '*.backup-*' } | Sort-Object Name)
    foreach ($artifact in $artifacts) {
      $found = $true
      $archivedPath = Join-Path (Join-Path (Join-Path $script:backupRoot 'legacy-discovery-conflicts') $category) $artifact.Name
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $archivedPath) | Out-Null
      Move-Item -LiteralPath $artifact.FullName -Destination $archivedPath -Force
      Write-Output "Archived legacy discovery conflict $($artifact.FullName) -> $archivedPath"
    }
  }
  if ($found) {
    Write-Output "Legacy discovery conflicts were moved under $($script:backupRoot)"
  }
}

function Add-ProjectTrust {
  param([string]$ConfigPath)

  if (Test-ProjectTrust $ConfigPath) {
    return
  }
  $content = [System.IO.File]::ReadAllText($ConfigPath)
  $content += "`n$(Get-ProjectTrustHeader)`ntrust_level = ""trusted""`n"
  Write-Utf8File -Path $ConfigPath -Content $content
  Write-Output "Added trusted project: $($script:repoRoot)"
}

function Install-Config {
  if ((Test-Path -LiteralPath $script:targetConfig -PathType Leaf) -and -not $script:resetConfig) {
    Write-Output "Preserved existing config byte-for-byte: $($script:targetConfig)"
    if ($script:trustProject -and -not (Test-ProjectTrust $script:targetConfig)) {
      [Console]::Error.WriteLine("[warn] Existing config is unchanged and has no trust entry for $($script:repoRoot). Add it manually or use --reset-config.")
    }
    Warn-LegacyInlineProfiles $script:targetConfig
    return
  }

  if (Test-Path -LiteralPath $script:targetConfig -PathType Leaf) {
    Backup-Path $script:targetConfig
  }
  $temporary = Join-Path $script:codexHome ('.config.toml.tmp.' + [guid]::NewGuid().ToString('N'))
  $content = [System.IO.File]::ReadAllText($script:sourceConfig).Replace('__CODEX_HOME__', $script:tomlCodexHome)
  Write-Utf8File -Path $temporary -Content $content
  if ($script:trustProject) {
    Add-ProjectTrust $temporary
  }
  Move-Item -LiteralPath $temporary -Destination $script:targetConfig -Force
  if ($script:resetConfig) {
    Write-Output "Reset global config from template: $($script:targetConfig)"
  }
  else {
    Write-Output "Installed global config from template: $($script:targetConfig)"
  }
}

function Install-AgentsTemplate {
  if (-not (Test-Path -LiteralPath $script:targetAgents -PathType Leaf)) {
    Install-FileAtomically $script:sourceAgents $script:targetAgents
    Write-Output "Installed global AGENTS template: $($script:targetAgents)"
    return
  }

  if ($script:resetAgents) {
    Backup-Path $script:targetAgents
    Install-FileAtomically $script:sourceAgents $script:targetAgents
    Write-Output "Reset global AGENTS from template: $($script:targetAgents)"
    return
  }

  $markerState = Get-AgentsMarkerState $script:targetAgents
  if ($markerState -eq 'valid') {
    $sourceContent = [System.IO.File]::ReadAllText($script:sourceAgents)
    if ((Get-ManagedAgentsContent $script:targetAgents) -ceq $sourceContent) {
      Write-Output "Managed global AGENTS block already exact: $($script:targetAgents)"
      return
    }

    Backup-Path $script:targetAgents
    $existing = [System.IO.File]::ReadAllText($script:targetAgents)
    $managedMatch = Get-ManagedAgentsMatch $existing
    if (-not $managedMatch.Success) {
      Fail "Validated managed AGENTS block could not be located: $($script:targetAgents)"
    }
    $updated = $existing.Substring(0, $managedMatch.Index) + $sourceContent +
      $existing.Substring($managedMatch.Index + $managedMatch.Length)
    $temporary = Join-Path $script:codexHome ('.AGENTS.md.tmp.' + [guid]::NewGuid().ToString('N'))
    Write-Utf8File -Path $temporary -Content $updated
    Move-Item -LiteralPath $temporary -Destination $script:targetAgents -Force
    Write-Output "Updated exact managed AGENTS block and preserved user guidance: $($script:targetAgents)"
    return
  }

  if ($markerState -ne 'none') {
    Fail "Malformed managed markers reached install unexpectedly: $($script:targetAgents)"
  }

  Backup-Path $script:targetAgents
  if (Test-KnownUnmarkedAgents $script:targetAgents) {
    Install-FileAtomically $script:sourceAgents $script:targetAgents
    Write-Output "Migrated unmarked GodMode v1.1 AGENTS guidance without duplication: $($script:targetAgents)"
    return
  }

  $sourceContent = [System.IO.File]::ReadAllText($script:sourceAgents)
  $existing = [System.IO.File]::ReadAllText($script:targetAgents)
  $preserved = $sourceContent + "`n## Preserved User Guidance`n`n" +
    "<!-- Preserved from the previous ~/.codex/AGENTS.md during the $($script:timestamp) install. -->`n`n" +
    $existing
  if (-not $preserved.EndsWith("`n")) {
    $preserved += "`n"
  }
  $temporary = Join-Path $script:codexHome ('.AGENTS.md.tmp.' + [guid]::NewGuid().ToString('N'))
  Write-Utf8File -Path $temporary -Content $preserved
  Move-Item -LiteralPath $temporary -Destination $script:targetAgents -Force
  Write-Output "Installed managed AGENTS block and preserved custom user guidance: $($script:targetAgents)"
}

function Install-Profiles {
  foreach ($profileName in $script:profileNames) {
    $sourcePath = Join-Path $script:sourceRepoProfiles $profileName
    $targetPath = Join-Path $script:codexHome $profileName
    if ((Test-Path -LiteralPath $targetPath -PathType Leaf) -and (Test-FilesEqual $sourcePath $targetPath)) {
      Write-Output "Managed profile already exact: $targetPath"
      continue
    }
    if (Test-Path -LiteralPath $targetPath) {
      Backup-Path $targetPath
      Remove-Item -LiteralPath $targetPath -Recurse -Force
    }
    Install-FileAtomically $sourcePath $targetPath
    Write-Output "Installed managed profile: $targetPath"
  }
}

function Install-AgentFiles {
  $sourceFiles = @(Get-ChildItem -LiteralPath $script:sourceRepoAgents -Filter '*.toml' -File | Sort-Object Name)
  foreach ($sourceFile in $sourceFiles) {
    $targetPath = Join-Path $script:targetAgentsDir $sourceFile.Name
    if ((Test-Path -LiteralPath $targetPath -PathType Leaf) -and (Test-FilesEqual $sourceFile.FullName $targetPath)) {
      continue
    }
    if (Test-Path -LiteralPath $targetPath) {
      Backup-Path $targetPath
      Remove-Item -LiteralPath $targetPath -Recurse -Force
    }
    Install-FileAtomically $sourceFile.FullName $targetPath
  }
}

function Install-SkillDirs {
  $sourceDirs = @(Get-ChildItem -LiteralPath $script:sourceRepoSkills -Directory | Sort-Object Name)
  foreach ($sourceDir in $sourceDirs) {
    $targetDir = Join-Path $script:userSkillsHome $sourceDir.Name
    if ((Test-Path -LiteralPath $targetDir -PathType Container) -and (Test-DirectoriesEqual $sourceDir.FullName $targetDir)) {
      continue
    }
    if (Test-Path -LiteralPath $targetDir) {
      Backup-Path $targetDir
    }
    $stageDir = Join-Path $script:userSkillsHome ('.' + $sourceDir.Name + '.tmp.' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stageDir | Out-Null
    foreach ($child in @(Get-ChildItem -LiteralPath $sourceDir.FullName -Force)) {
      Copy-Item -LiteralPath $child.FullName -Destination $stageDir -Recurse -Force
    }
    if (Test-Path -LiteralPath $targetDir) {
      Remove-Item -LiteralPath $targetDir -Recurse -Force
    }
    Move-Item -LiteralPath $stageDir -Destination $targetDir
  }
}

function Check-Path {
  param(
    [string]$Path,
    [string]$Label
  )

  if (Test-Path -LiteralPath $Path) {
    Write-Host "[ok] ${Label}: $Path"
    return $true
  }
  Write-Host "[missing] ${Label}: $Path"
  $false
}

function Check-ExactFile {
  param(
    [string]$Source,
    [string]$Target,
    [string]$Label
  )

  if (Test-FilesEqual $Source $Target) {
    Write-Host "[ok] $Label exact"
    return $true
  }
  Write-Host "[drift] ${Label}: $Target"
  $false
}

function Check-NoLegacyDiscoveryConflicts {
  param(
    [string]$Root,
    [string]$Label
  )

  if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
    Write-Host "[ok] $Label clean"
    return $true
  }
  $conflicts = @(Get-ChildItem -LiteralPath $Root -Force | Where-Object { $_.Name -like '*.backup-*' })
  if ($conflicts.Count -gt 0) {
    Write-Host "[invalid] $Label contains legacy backup artifacts"
    $conflicts.FullName | ForEach-Object { Write-Host $_ }
    return $false
  }
  Write-Host "[ok] $Label clean"
  $true
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

  if (Test-Path -LiteralPath $script:targetAgents -PathType Leaf) {
    $sourceContent = [System.IO.File]::ReadAllText($script:sourceAgents)
    if ((Get-AgentsMarkerState $script:targetAgents) -eq 'valid' -and (Get-ManagedAgentsContent $script:targetAgents) -ceq $sourceContent) {
      Write-Output '[ok] Global AGENTS managed block exact'
    }
    else {
      Write-Output '[drift] Global AGENTS managed block'
      $status = 1
    }
  }

  if (Test-Path -LiteralPath $script:targetConfig -PathType Leaf) {
    Warn-LegacyInlineProfiles $script:targetConfig
    if ($script:trustProject) {
      if (Test-ProjectTrust $script:targetConfig) {
        Write-Output '[ok] trusted project entry'
      }
      else {
        [Console]::Error.WriteLine("[warn] Existing config has no trust entry for $($script:repoRoot) and remains unchanged.")
      }
    }
  }

  foreach ($profileName in $script:profileNames) {
    if (-not (Check-ExactFile (Join-Path $script:sourceRepoProfiles $profileName) (Join-Path $script:codexHome $profileName) "Managed profile $profileName")) {
      $status = 1
    }
  }
  foreach ($sourceFile in @(Get-ChildItem -LiteralPath $script:sourceRepoAgents -Filter '*.toml' -File | Sort-Object Name)) {
    if (-not (Check-ExactFile $sourceFile.FullName (Join-Path $script:targetAgentsDir $sourceFile.Name) "Global agent $($sourceFile.BaseName)")) {
      $status = 1
    }
  }
  foreach ($sourceDir in @(Get-ChildItem -LiteralPath $script:sourceRepoSkills -Directory | Sort-Object Name)) {
    $targetDir = Join-Path $script:userSkillsHome $sourceDir.Name
    if (Test-DirectoriesEqual $sourceDir.FullName $targetDir) {
      Write-Output "[ok] Global skill $($sourceDir.Name) exact"
    }
    else {
      Write-Output "[drift] Global skill $($sourceDir.Name): $targetDir"
      $status = 1
    }
  }

  if ($status -ne 0) {
    Fail 'Global Codex setup check failed.' 1
  }
  Write-Output ''
  Write-Output 'Global Codex setup check passed.'
}

$script:minimumCodexVersion = '0.134.0'
$script:repoRoot = Resolve-AbsolutePath (Join-Path $PSScriptRoot '..')
$defaultCodexHome = if ([string]::IsNullOrWhiteSpace($env:CODEX_HOME)) { Join-Path $HOME '.codex' } else { $env:CODEX_HOME }
$script:codexHome = Resolve-AbsolutePath $defaultCodexHome
$script:userSkillsHome = Resolve-AbsolutePath (Join-Path (Join-Path $HOME '.agents') 'skills')
$script:trustProject = $true
$script:checkOnly = $false
$script:resetConfig = $false
$script:resetAgents = $false

$index = 0
while ($index -lt $args.Count) {
  $argument = $args[$index]
  switch ($argument) {
    '--check' { $script:checkOnly = $true; $index += 1 }
    '-Check' { $script:checkOnly = $true; $index += 1 }
    '--codex-home' {
      if (($index + 1) -ge $args.Count) { Invalid-Argument 'Missing value for option: --codex-home' }
      $script:codexHome = Resolve-AbsolutePath $args[$index + 1]
      $index += 2
    }
    '--user-skills-home' {
      if (($index + 1) -ge $args.Count) { Invalid-Argument 'Missing value for option: --user-skills-home' }
      $script:userSkillsHome = Resolve-AbsolutePath $args[$index + 1]
      $index += 2
    }
    '--repo' {
      if (($index + 1) -ge $args.Count) { Invalid-Argument 'Missing value for option: --repo' }
      $script:repoRoot = Resolve-AbsolutePath $args[$index + 1]
      $index += 2
    }
    '--no-trust-project' { $script:trustProject = $false; $index += 1 }
    '--reset-config' { $script:resetConfig = $true; $index += 1 }
    '-ResetConfig' { $script:resetConfig = $true; $index += 1 }
    '--reset-agents' { $script:resetAgents = $true; $index += 1 }
    '-ResetAgents' { $script:resetAgents = $true; $index += 1 }
    '-h' { Show-Usage; exit 0 }
    '--help' { Show-Usage; exit 0 }
    default { Invalid-Argument "Unknown option: $argument" }
  }
}

if ($script:checkOnly -and ($script:resetConfig -or $script:resetAgents)) {
  Invalid-Argument '--check cannot be combined with --reset-config or --reset-agents.'
}
if ([string]::IsNullOrWhiteSpace($script:codexHome) -or [string]::IsNullOrWhiteSpace($script:userSkillsHome) -or [string]::IsNullOrWhiteSpace($script:repoRoot)) {
  Invalid-Argument 'Path options must not be empty.'
}
if (-not (Test-Path -LiteralPath $script:repoRoot -PathType Container)) {
  Fail "Repository root is not a directory: $($script:repoRoot)"
}

$templateRoot = Join-Path $script:repoRoot 'templates/global-codex'
$script:sourceAgents = Join-Path $templateRoot 'AGENTS.md'
$script:sourceConfig = Join-Path $templateRoot 'config.toml'
$script:sourceRepoAgents = Join-Path $templateRoot 'agents'
$script:sourceRepoProfiles = Join-Path $templateRoot 'profiles'
$script:sourceRepoSkills = Join-Path $templateRoot 'skills'
$script:targetAgents = Join-Path $script:codexHome 'AGENTS.md'
$script:targetConfig = Join-Path $script:codexHome 'config.toml'
$script:targetAgentsDir = Join-Path $script:codexHome 'agents'
$script:playwrightOutput = Join-Path (Join-Path $script:codexHome 'playwright-output') 'isolated'
$script:timestamp = Get-Date -Format 'yyyy-MM-ddTHH-mm-ss'
$script:backupRunId = $script:timestamp + '-' + $PID + '-' + [guid]::NewGuid().ToString('N')
$script:backupRoot = Join-Path (Join-Path (Join-Path $script:codexHome 'backups') 'install-archives') $script:backupRunId
$script:tomlCodexHome = Convert-ToTomlPath $script:codexHome
$script:tomlRepoRoot = Convert-ToTomlPath $script:repoRoot
$script:agentsMarkerBegin = '<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->'
$script:agentsMarkerEnd = '<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->'
$script:legacyV11AgentsSha256 = 'b660e0f29ea87e1817b702c5a52d960fe7230f807ec8adb927c18f14ed101451'
$script:profileNames = @(
  'godmode-swiftui.config.toml',
  'godmode-web.config.toml',
  'godmode-flutter.config.toml',
  'godmode-review.config.toml'
)

# Nothing below this point mutates a target until every preflight gate is green.
Resolve-CodexRuntime
Preflight-SourcesAndTargets

if ($script:checkOnly) {
  Run-Check
  exit 0
}

New-Item -ItemType Directory -Force -Path $script:codexHome | Out-Null
New-Item -ItemType Directory -Force -Path $script:userSkillsHome | Out-Null
New-Item -ItemType Directory -Force -Path $script:playwrightOutput | Out-Null
New-Item -ItemType Directory -Force -Path $script:targetAgentsDir | Out-Null

Archive-LegacyDiscoveryConflicts
Install-AgentsTemplate
Install-Config
Install-Profiles
Install-AgentFiles
Install-SkillDirs

Write-Output ''
Write-Output "Installed global Codex setup to $($script:codexHome)"
Write-Output "Installed global agents to $($script:targetAgentsDir)"
Write-Output "Installed user skill root at $($script:userSkillsHome)"
Write-Output "Prepared Playwright output directory at $($script:playwrightOutput)"

Run-Check
