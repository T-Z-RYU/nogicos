@echo off
echo ========================================
echo AI Browser 技术验证 - 环境搭建
echo ========================================

REM 检查 conda 是否安装
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 conda，请先安装 Anaconda 或 Miniconda
    exit /b 1
)

echo.
echo [1/5] 创建 Conda 环境...
call conda create -n ai-browser python=3.10 -y

echo.
echo [2/5] 激活环境...
call conda activate ai-browser

echo.
echo [3/5] 克隆 SkillWeaver...
if not exist "SkillWeaver" (
    git clone https://github.com/OSU-NLP-Group/SkillWeaver.git
) else (
    echo SkillWeaver 已存在，跳过克隆
)

echo.
echo [4/5] 安装依赖...
cd SkillWeaver
pip install -r requirements.txt
cd ..

REM 安装额外依赖
pip install litellm anthropic google-generativeai

echo.
echo [5/5] 安装 Playwright 浏览器...
playwright install chromium

echo.
echo ========================================
echo 环境搭建完成！
echo ========================================
echo.
echo 请设置以下环境变量:
echo   set OPENAI_API_KEY=your_key
echo   set ANTHROPIC_API_KEY=your_key
echo   set GOOGLE_API_KEY=your_key
echo.
echo 然后运行: python run_verify.py
echo ========================================
