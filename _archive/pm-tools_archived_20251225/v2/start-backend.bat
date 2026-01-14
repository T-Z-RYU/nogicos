@echo off
cd /d "C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
