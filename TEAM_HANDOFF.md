# NogicOS 团队交接文档

> 最后更新：2025/01/03
> 准备发给团队的项目概览

---

## 📦 项目包含内容

### 核心项目：nogicos/

```
nogicos/
├── 📄 README.md              ← 项目说明（已更新）
├── 📄 PRODUCT_SPEC.md        ← 产品规范（开发必读）
├── 📄 ARCHITECTURE.md        ← 技术架构
├── 📄 PITCH_CONTEXT.md       ← Pitch 协作上下文（新增）
├── 📄 CHANGELOG.md           ← 更新日志
│
├── 🐍 hive_server.py         ← 后端入口
├── 📁 engine/                ← 核心引擎代码
├── 📁 client/                ← Electron 客户端
├── 📁 nogicos-ui/            ← React 前端
│
├── 📄 api_keys.example.py    ← API Key 模板
├── 📄 requirements.txt       ← Python 依赖
└── 📁 tests/                 ← 测试代码
```

### YC 申请材料：docs/yc/

```
docs/yc/
├── 📄 NogicOS_Product_Analysis.md    ← 产品分析（纯产品视角）
├── 📄 NogicOS_YC_Application.md      ← YC 申请材料
├── 📄 yc_founders_2024_2026.json     ← YC 公司数据（1,265家）
└── 📄 YC_Founder_Analysis_2024_2026.md ← 创始人分析报告
```

---

## 🎯 核心叙事

### One-liner
> **"NogicOS: The AI that works where you work"**

### 30秒 Pitch
1. 知识工作者的工作分散在浏览器、本地文件、各种应用里
2. 现有 AI 只能看到一个窗口
3. NogicOS 是第一个能同时看到浏览器、文件和桌面的 AI
4. 而且它会学习——第一次 30 秒，第二次 1 秒
5. 用的人越多，所有人越快

---

## 🔑 关键差异化

| 维度 | NogicOS | 竞品 |
|------|---------|------|
| **上下文** | 浏览器 + 文件 + 桌面 | 单一窗口 |
| **学习** | 越用越快 | 每次从零开始 |
| **网络效应** | 集体学习 | 无 |
| **隐私** | 本地优先 | 云端依赖 |

---

## 👥 团队分工建议

### Deck 制作
- 阅读 `nogicos/PITCH_CONTEXT.md`
- 参考 `docs/yc/NogicOS_Product_Analysis.md`
- 用 Cursor 问："帮我写 Problem slide 的文案"

### Script 撰写
- 阅读 `docs/yc/NogicOS_YC_Application.md` 的叙事部分
- 用 Cursor 问："帮我扩展 1 分钟 Pitch 到 3 分钟"

### Demo 准备
- 启动后端：`python hive_server.py`
- 推荐场景：帮助分析 YC 公司数据

---

## 🚀 快速启动

```bash
# 1. 进入项目目录
cd nogicos

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 配置 API Key
cp api_keys.example.py api_keys.py
# 编辑 api_keys.py 填入 Anthropic API Key

# 4. 启动后端
python hive_server.py

# 5. 启动前端（另一个终端）
cd nogicos-ui
npm install
npm run dev
```

---

## 📁 可以忽略的文件/文件夹

以下是开发过程中的临时文件，团队成员不需要关注：

```
nogicos/
├── __pycache__/           ← Python 缓存
├── node_modules/          ← NPM 依赖（自动安装）
├── benchmarks/            ← 测试基准（开发用）
├── reference/             ← 参考代码（开发用）
├── logs/                  ← 日志文件
├── data/                  ← 运行时数据
├── tests/screenshots/     ← 测试截图
├── *.txt (测试文件)       ← 各种测试临时文件
└── novnc-client/          ← VNC 客户端（备用）
```

---

## 📞 联系方式

有问题找 Zino

---

## ✅ Checklist

团队成员收到后：

- [ ] 阅读 `nogicos/PITCH_CONTEXT.md`
- [ ] 阅读 `docs/yc/NogicOS_Product_Analysis.md`
- [ ] 阅读 `docs/yc/NogicOS_YC_Application.md`
- [ ] 用 Cursor 打开项目，开始协作

---

*准备好就开始吧！*

