@echo off
REM AI Browser 技术验证 - 设置 API Keys
REM 请将下面的 xxx 替换为你的实际 API Key

REM OpenAI API Key (GPT-5.2)
set OPENAI_API_KEY=xxx

REM Anthropic API Key (Claude Opus 4.5)
set ANTHROPIC_API_KEY=xxx

REM Google API Key (Gemini 3)
set GOOGLE_API_KEY=xxx

echo API Keys 已设置!
echo.
echo 验证:
echo   OPENAI_API_KEY: %OPENAI_API_KEY:~0,10%...
echo   ANTHROPIC_API_KEY: %ANTHROPIC_API_KEY:~0,10%...
echo   GOOGLE_API_KEY: %GOOGLE_API_KEY:~0,10%...
echo.
echo 现在可以运行: python run_verify.py
