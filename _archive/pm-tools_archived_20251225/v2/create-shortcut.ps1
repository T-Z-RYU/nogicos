$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = [Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupFolder "PM Tool v2.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\start-background.vbs"
$Shortcut.WorkingDirectory = "C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2"
$Shortcut.Description = "PM Tool v2 Auto Start"
$Shortcut.Save()

Write-Host "Done! Shortcut created at: $ShortcutPath"


