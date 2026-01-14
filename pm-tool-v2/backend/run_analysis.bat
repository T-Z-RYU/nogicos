@echo off
cd /d "c:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\backend"
REM Set your API keys as environment variables before running
REM set ANTHROPIC_API_KEY=your-api-key-here
REM set OPENAI_API_KEY=your-api-key-here
echo Starting analysis at %date% %time%
echo ============================================================
python scripts/analyze_screenshots.py --app all
echo ============================================================
echo Analysis completed at %date% %time%
pause
