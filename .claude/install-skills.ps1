# Skill paketini %USERPROFILE%\.claude\skills altina kurar (Windows).
# Kurulum:     powershell -ExecutionPolicy Bypass -File .claude\install-skills.ps1
# Guncelleme:  powershell -ExecutionPolicy Bypass -File .claude\install-skills.ps1 -Update
param([switch]$Update)

$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $Here

if ($Update) {
    Write-Host 'Depo guncelleniyor (git pull)...'
    git -C $RepoRoot pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'git pull basarisiz oldu.' }
}

$ClaudeHome = Join-Path $env:USERPROFILE '.claude'
$Dest = Join-Path $ClaudeHome 'skills'
foreach ($d in @($Dest, (Join-Path $ClaudeHome 'agents'), (Join-Path $ClaudeHome 'references'))) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

$count = 0
foreach ($item in Get-ChildItem -Path (Join-Path $Here 'skills')) {
    $name = $item.Name
    # 'watch' gibi depo kokundeki skill'leri dogrudan kaynaktan al: Windows'ta
    # git symlink'leri cogu zaman duz metin dosyasi olarak cikarir.
    $src = Join-Path $RepoRoot "skills\$name"
    if (-not (Test-Path (Join-Path $src 'SKILL.md'))) { $src = $item.FullName }
    if (-not (Test-Path (Join-Path $src 'SKILL.md'))) { continue }

    $target = Join-Path $Dest $name
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    Copy-Item -Recurse -Path $src -Destination $target
    $count++
}

Copy-Item -Force -Path (Join-Path $Here 'agents\*.md') -Destination (Join-Path $ClaudeHome 'agents')
Copy-Item -Force -Path (Join-Path $Here 'references\*.md') -Destination (Join-Path $ClaudeHome 'references')

Write-Host "$count skill kuruldu: $Dest"
Write-Host 'Claude Code''u yeniden baslat; /video-editing, /watch, /seo gibi isimlerle cagirabilirsin.'
