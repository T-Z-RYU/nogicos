# AI Browser 技术验证 - 快速开始

## 🚀 5 分钟快速验证

### Step 1: 进入项目目录

```bash
cd "c:/Users/WIN/Desktop/Cursor Project/ai-browser-verify"
```

### Step 2: 安装依赖

```bash
# 安装 Python 依赖
pip install playwright litellm anthropic openai google-generativeai rich

# 安装 Playwright 浏览器
playwright install chromium
```

### Step 3: 运行快速测试

```bash
python quick_test.py
```

这会检查：
- Python 版本
- 必要目录
- API Keys 配置
- Playwright 功能

### Step 4: 设置 API Keys（可选）

如果要使用真实 AI 模型：

```bash
# Windows
set GOOGLE_API_KEY=your_key
set ANTHROPIC_API_KEY=your_key

# Linux/Mac
export GOOGLE_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

### Step 5: 运行完整验证

```bash
python run_verify.py
```

---

## 📁 项目结构概览

```
ai-browser-verify/
├── quick_test.py      # 快速环境检查 ⬅️ 先运行这个
├── run_verify.py      # 完整验证脚本
├── config.py          # 配置文件
├── llm_adapter.py     # LLM 适配器（支持最新模型）
├── tests/
│   ├── basic_test.py  # 基础测试
│   ├── reddit_test.py # Reddit 场景
│   └── uniswap_test.py# Web3 场景
├── electron-browser/  # Electron 浏览器原型
│   └── npm start      # 启动浏览器
├── SkillWeaver/       # 核心 AI 框架
└── results/           # 测试结果
```

---

## 🎯 验证目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 执行加速比 | > 10x | 有知识库 vs 无知识库 |
| 学习时间 | < 60s | 学习一个网站 |
| 成功率 | > 80% | 任务完成率 |

---

## 🖥️ Electron 浏览器原型

```bash
cd electron-browser
npm install
npm start
```

这是一个完整的 AI 浏览器原型，具有：
- 现代化 UI（深色主题）
- AI 助手面板
- 学习/执行功能
- 状态指示器

---

## 🔧 支持的模型

| 模型 | 适用场景 | 特点 |
|------|---------|------|
| **Claude Opus 4.5** | 学习/复杂任务 | Computer Use 最强 |
| **Gemini 3 Flash** | 快速测试 | 速度最快，成本最低 |
| **GPT-5.2** | 备选 | 推理能力强 |

---

## ❓ 常见问题

**Q: 没有 API Key 能测试吗？**
A: 可以！会使用模拟模式，能验证整体流程。

**Q: Playwright 安装失败？**
A: 运行 `playwright install chromium --with-deps`

**Q: SkillWeaver 报错？**
A: 确保在 SkillWeaver 目录下运行 `pip install -r requirements.txt`

---

## 📊 预期结果

运行 `run_verify.py` 后，你会在 `results/` 目录看到：
- `report_YYYYMMDD_HHMMSS.md` - 测试报告
- `data_YYYYMMDD_HHMMSS.json` - 原始数据
- `test_screenshot.png` - 测试截图

---

## 🎬 下一步

1. 配置真实 API Keys 运行完整测试
2. 在 Electron 浏览器中体验 AI 功能
3. 根据报告调整参数
4. 录制 Demo 视频
