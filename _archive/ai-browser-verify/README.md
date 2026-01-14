# AI Browser 技术验证

验证核心假设：**AI 能自动学习网站操作，学一次后执行速度提升 10x+**

## 项目结构

```
ai-browser-verify/
├── SkillWeaver/           # 克隆的 SkillWeaver 仓库
├── electron-browser/      # Electron 浏览器原型
│   ├── main.js           # 主进程
│   ├── preload.js        # 预加载脚本
│   └── renderer/         # 渲染进程
├── tests/                 # 测试脚本
│   ├── basic_test.py     # 基础测试
│   ├── reddit_test.py    # Reddit 场景
│   ├── github_test.py    # GitHub 场景
│   └── uniswap_test.py   # Uniswap 场景
├── knowledge_base/        # 学到的技能存储
├── results/              # 测试结果
├── config.py             # 配置文件
├── run_verify.py         # 主验证脚本
├── llm_adapter.py        # LLM 适配器
└── quick_test.py         # 快速环境检查
```

## 快速开始

### 1. 环境搭建

**Windows:**
```bash
# 运行环境搭建脚本
setup_env.bat
```

**Linux/Mac:**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

### 2. 配置 API Keys

编辑 `set_api_keys.bat` (Windows) 或设置环境变量:

```bash
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
export GOOGLE_API_KEY=your_key
```

### 3. 运行快速测试

```bash
python quick_test.py
```

### 4. 运行完整验证

```bash
python run_verify.py
```

## 测试场景

| 场景 | URL | 任务示例 |
|------|-----|---------|
| Reddit | reddit.com | 搜索帖子、查看热门 |
| GitHub | github.com | 搜索仓库、查看趋势 |
| Uniswap | app.uniswap.org | Swap 界面导航 |

## 模型配置

支持 2025 年最新模型：

| 模型 | 用途 | 特点 |
|------|------|------|
| Claude Opus 4.5 | 主模型/学习 | Computer Use 最强 |
| Gemini 3 Flash | 快速测试 | 速度最快 |
| GPT-5.2 | 备选 | 推理能力强 |

## Electron 浏览器原型

```bash
cd electron-browser
npm install
npm start
```

## 验证指标

| 指标 | 目标 | 必须达到 |
|------|------|---------|
| 学习时间 | < 60s | < 120s |
| 执行加速比 | > 10x | > 5x |
| 成功率 | > 80% | > 60% |

## 技术栈

- **框架**: SkillWeaver (OSU-NLP-Group)
- **浏览器自动化**: Playwright
- **LLM 统一接口**: LiteLLM
- **桌面应用**: Electron

## 参考资料

- [SkillWeaver 论文](https://arxiv.org/abs/2504.07079)
- [WebArena Benchmark](https://webarena.dev/)
- [Playwright 文档](https://playwright.dev/)

## License

MIT
