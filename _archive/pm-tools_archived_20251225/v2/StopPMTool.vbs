Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -ano ^| findstr "":8001.*LISTENING""') do taskkill /F /PID %a", 0, True

WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -ano ^| findstr "":3001.*LISTENING""') do taskkill /F /PID %a", 0, True

MsgBox "PM Tool v2 Stopped!", vbInformation, "PM Tool v2"
