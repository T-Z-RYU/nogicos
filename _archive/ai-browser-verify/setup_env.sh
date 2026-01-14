#!/bin/bash
echo "========================================"
echo "AI Browser 技术验证 - 环境搭建"
echo "========================================"

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到 conda，请先安装 Anaconda 或 Miniconda"
    exit 1
fi

echo ""
echo "[1/5] 创建 Conda 环境..."
conda create -n ai-browser python=3.10 -y

echo ""
echo "[2/5] 激活环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ai-browser

echo ""
echo "[3/5] 克隆 SkillWeaver..."
if [ ! -d "SkillWeaver" ]; then
    git clone https://github.com/OSU-NLP-Group/SkillWeaver.git
else
    echo "SkillWeaver 已存在，跳过克隆"
fi

echo ""
echo "[4/5] 安装依赖..."
cd SkillWeaver
pip install -r requirements.txt
cd ..

# 安装额外依赖
pip install litellm anthropic google-generativeai

echo ""
echo "[5/5] 安装 Playwright 浏览器..."
playwright install chromium

echo ""
echo "========================================"
echo "环境搭建完成！"
echo "========================================"
echo ""
echo "请设置以下环境变量:"
echo "  export OPENAI_API_KEY=your_key"
echo "  export ANTHROPIC_API_KEY=your_key"
echo "  export GOOGLE_API_KEY=your_key"
echo ""
echo "然后运行: python run_verify.py"
echo "========================================"
