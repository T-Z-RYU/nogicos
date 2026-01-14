# NogicOS 产品文档

> 最后更新：2026/01/13

---

## 🎯 一句话定位

> **Workspace AI connects your tabs, files, and apps**
> 
> 连接你的标签页、文件和应用的工作环境 AI

---

## 📋 核心叙事

### 问题
知识工作者（PM、分析师、研究员）的工作分散在浏览器标签页、本地文件、各种应用里。现有 AI 只能看到一个窗口，用户需要不断复制粘贴上下文。

### 洞察
这不是 AI 能力的问题，是**上下文连接**的问题。Cursor 解决了程序员的这个问题——它能连接整个代码仓库。但对于非程序员的知识工作者呢？

### 解决方案
NogicOS 是一个 **Workspace AI**，能连接你的 tabs、files 和 apps。它不只是聊天，它能直接在你的工作环境里行动。

### 护城河
统一上下文 = 更准确的执行。不需要反复解释背景，AI 直接连接你所有的工作信息。

### 愿景
让每一个知识工作者都有一个 AI 伙伴，它能连接你的完整工作环境，直接帮你行动。

---

## 🔑 关键差异化

| 竞品 | 他们做什么 | 我们的差异 |
|------|-----------|-----------|
| **ChatGPT/Claude** | 纯聊天，看不到你的工作环境 | 我们能连接 tabs, files, apps |
| **Cursor** | 代码仓库 AI | 我们面向所有知识工作者 |
| **ramAIn** | 通讯自动化（WhatsApp/Email）| 我们做研究/分析/文档整合 |
| **Zapier/Make** | Workflow automation | 我们是 AI agent，不是 if-then 规则 |

---

## 🛠️ 核心能力

### 1. Connecting（连接）
- **Tabs**：内嵌浏览器，直接浏览网页（Playwright CDP）
- **Files**：本地文件访问，用户授权的文件夹
- **Apps**：桌面应用感知，窗口管理

### 2. Understanding（理解）
- AI 理解你的工作环境
- 不需要复制粘贴上下文
- 跨 tabs, files, apps 的统一理解

### 3. Acting（行动）
- 不只是建议，而是直接执行
- 自动填表、自动提取数据、自动整理文件
- 跨应用工作流
- **桌面自动化**：pyautogui + pywinauto

### 4. 技术实现
- **Browser Tools**: Playwright CDP 控制
- **Local Tools**: 读写文件、搜索、执行命令
- **Desktop Tools**: 截屏、点击、窗口管理
- **LangSmith 集成**：完整的 Agent 执行追踪

---

## 👥 目标用户

- **产品经理**：竞品分析、用户研究、文档整理
- **分析师**：数据提取、报告生成、信息汇总
- **研究员**：文献管理、笔记整理、资料收集
- **创业者**：市场调研、申请材料准备

---

## 🏗️ 技术架构

```
用户说话 → ReAct Agent 思考 → 调用工具 → 执行任务 → 返回结果
                                    ↓
                            Knowledge Store（学习）
```

**六类工具：**
- **Browser Tools**: Playwright CDP 控制、快照、点击、输入
- **Local Tools**: 读写文件、搜索、创建文件夹、执行命令
- **Desktop Tools**: 截屏、点击、输入、快捷键、窗口管理
- **Messaging Tools**: WhatsApp 消息发送
- **System Tools**: 系统信息、任务状态、用户确认
- **Vision Tools**: 图像理解、屏幕分析

---

## 📊 市场验证

**YC 2024-2026 数据分析（1,265 家公司）：**
- AI Agent 公司占比已超过 51%
- 同时具备「浏览器+本地+学习」能力的只有 19 家（1.5%）
- 「本地优先/隐私」定位只有 17 家 → **稀缺赛道**

---

## 🎬 典型使用场景

### 场景 1：竞品分析
> "帮我分析 Notion AI 的功能，和我们的差异是什么"

NogicOS 会：打开 Notion 官网 → 提取功能列表 → 对比本地文档 → 生成分析报告

### 场景 2：YC 申请
> "帮我填写 YC 申请表"

NogicOS 会：读取产品文档 → 理解表单问题 → 生成答案 → 填写表单

### 场景 3：信息整合
> "把这个网页的数据整理到我的 Excel 里"

NogicOS 会：提取网页数据 → 打开 Excel → 按格式填入 → 保存文件

### 场景 4：消息通知
> "给 ZinoT 发个 WhatsApp 消息，说会议改到下午 3 点"

NogicOS 会：打开 WhatsApp → 找到联系人 → 输入消息 → 发送

---

## 📈 当前状态

**L3 Beta**

| 能力 | 状态 |
|------|------|
| Local Tools | ✅ 全部工作 |
| Browser Tools | ✅ Playwright CDP |
| Desktop Tools | ✅ pyautogui + pywinauto |
| Messaging Tools | ✅ WhatsApp |
| Knowledge Store | ✅ 工作 |
| LangSmith 追踪 | ✅ 集成 |
| DSPy 优化 | ✅ 集成 |

---

## ⚠️ 注意事项

1. **叙事一致性**：围绕「Workspace AI」这个品类定位
2. **强调差异化**：跟 ramAIn（通讯自动化）不同，我们做研究/分析
3. **核心动词**：connects（连接），不是 sees（看到）
4. **三个关键词**：tabs, files, apps

---

*NogicOS - Workspace AI connects your tabs, files, and apps*
