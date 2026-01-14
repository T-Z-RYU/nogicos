Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "cmd /c cd /d ""C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\backend"" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001", 0, False

WScript.Sleep 2000

WshShell.Run "cmd /c cd /d ""C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\frontend"" && npm run dev", 0, False

MsgBox "PM Tool v2 Started!" & vbCrLf & vbCrLf & "Frontend: http://localhost:3001" & vbCrLf & "Backend: http://localhost:8001", vbInformation, "PM Tool v2"
