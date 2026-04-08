$cacheDir = "$env:LOCALAPPDATA\electron-builder\Cache\winCodeSign"
$archive = Get-ChildItem -Path $cacheDir -Filter '*.7z' -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $archive) {
  Write-Host "No winCodeSign archive found in $cacheDir; nothing to fix."
  exit 0
}
$extractDir = Join-Path $cacheDir $archive.BaseName
Write-Host "Archive: $($archive.FullName)"
Write-Host "Extract dir: $extractDir"

# Use 7zip-bin shipped with electron-builder
$sevenZip = "C:\Users\lutie\Desktop\nogicos\.claude\worktrees\eager-archimedes\usc-pm\desktop\node_modules\7zip-bin\win\x64\7za.exe"
if (-not (Test-Path $sevenZip)) {
  Write-Host "7za.exe not found at $sevenZip"
  exit 1
}

# Remove broken extraction
if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Path $extractDir -Force | Out-Null

# Extract: -y (yes), no symlink storage (-snld)
& $sevenZip x $archive.FullName "-o$extractDir" -y -snld 2>&1 | Out-Null

# Whatever symlinks failed: create empty placeholder files at their expected paths
$macLib = Join-Path $extractDir 'darwin\10.12\lib'
if (Test-Path (Split-Path $macLib -Parent)) {
  New-Item -ItemType Directory -Path $macLib -Force | Out-Null
  foreach ($f in 'libcrypto.dylib','libssl.dylib') {
    $p = Join-Path $macLib $f
    if (-not (Test-Path $p)) {
      New-Item -ItemType File -Path $p -Force | Out-Null
      Write-Host "Created placeholder: $p"
    }
  }
}

Write-Host "Done. Extracted to: $extractDir"
