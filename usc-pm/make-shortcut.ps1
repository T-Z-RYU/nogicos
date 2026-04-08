$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$lnkPath = Join-Path $desktop 'USC PM.lnk'
$lnk = $ws.CreateShortcut($lnkPath)
$lnk.TargetPath = 'C:\Users\lutie\Desktop\nogicos\.claude\worktrees\eager-archimedes\usc-pm\start-usc-pm.bat'
$lnk.WorkingDirectory = 'C:\Users\lutie\Desktop\nogicos\.claude\worktrees\eager-archimedes\usc-pm'
$lnk.WindowStyle = 7
$lnk.Description = 'USC PM Assistant'
$lnk.Save()
Write-Host "Created: $lnkPath"
