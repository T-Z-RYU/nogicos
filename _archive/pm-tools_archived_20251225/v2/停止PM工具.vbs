Set WshShell = CreateObject("WScript.Shell")

' 停止占用 8001 端口的进程
WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -ano ^| findstr "":8001.*LISTENING""') do taskkill /F /PID %a", 0, True

' 停止占用 3001 端口的进程
WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -ano ^| findstr "":3001.*LISTENING""') do taskkill /F /PID %a", 0, True

MsgBox "PM Tool v2 服务已停止！", vbInformation, "PM Tool v2"
