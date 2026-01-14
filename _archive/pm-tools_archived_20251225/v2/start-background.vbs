' PM Tool v2 - 后台启动脚本
' 双击运行，不会弹出命令行窗口

Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' 后台启动 (0 = 隐藏窗口)
WshShell.Run "cmd /c cd /d """ & strPath & """ && python start.py", 0, False

' 显示通知
MsgBox "PM Tool v2 已在后台启动!" & vbCrLf & vbCrLf & _
       "后端: http://localhost:8000" & vbCrLf & _
       "前端: http://localhost:3001" & vbCrLf & vbCrLf & _
       "要停止服务，请打开任务管理器结束 Python 和 Node 进程", _
       vbInformation, "PM Tool v2"


