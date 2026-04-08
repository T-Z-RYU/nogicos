$tmp = [System.IO.Path]::GetTempPath()
$target = Join-Path $tmp 'symlink-test-target.txt'
$link = Join-Path $tmp 'symlink-test-link.txt'
'hi' | Out-File $target
Remove-Item $link -ErrorAction SilentlyContinue
try {
  New-Item -ItemType SymbolicLink -Path $link -Target $target -ErrorAction Stop | Out-Null
  Write-Host 'SYMLINK OK'
  Remove-Item $link
} catch {
  Write-Host "SYMLINK FAIL: $_"
}
