Set WshShell = CreateObject("WScript.Shell")

' 启动后端
WshShell.Run "cmd /c cd /d ""C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\backend"" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001", 0, False

' 等待2秒
WScript.Sleep 2000

' 启动前端
WshShell.Run "cmd /c cd /d ""C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\frontend"" && npm run dev", 0, False

' 显示提示
MsgBox "PM Tool v2 服务已在后台启动！" & vbCrLf & vbCrLf & "前端: http://localhost:3001" & vbCrLf & "后端: http://localhost:8001", vbInformation, "PM Tool v2"
