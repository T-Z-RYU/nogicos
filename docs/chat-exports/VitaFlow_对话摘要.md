# VitaFlow 对话摘要

> 整理日期：2024-12-26  
> 相关对话文件：11 个  
> 时间范围：2024-12-17 ~ 2024-12-24

---

## 一、项目概述

### 1.1 产品定位
- **产品名称**：VitaFlow
- **产品类型**：iOS AI 卡路里追踪 App
- **付费模式**：Hard Paywall（Onboarding 结束必须开始 Trial 才能进入主页）
- **目标上线**：Q1

### 1.2 竞品
- Cal AI
- Noom
- MyFitnessPal
- Yazio

---

## 二、Onboarding 设计

### 2.1 竞品分析流程
1. 下载竞品截图
2. 在 PM_Screenshot_Tool Web 界面标记 Onboarding
3. AI 分析截图内容
4. 生成分析报告
5. 团队讨论
6. 输出 VitaFlow Onboarding 逻辑设计

### 2.2 设计基准
- 以 `onboarding.html` 为设计基准
- V2 A/B Test 版本包含 40 页

---

## 三、埋点事件列表

### 3.1 Notion 数据库
- **名称**：Vitaflow 事件埋点列表
- **位置**：VitaFlow 客户端相关文档
- **字段**：事件名、触发时机、状态、页面

### 3.2 关键埋点事件
| 事件 | 页面 | 状态 |
|------|------|------|
| Start onboarding | Demo-Onboarding | TBD |
| 进入 scan onboarding（4-steps） | Scan | TBD |
| 结束 scan onboarding | Scan | TBD |
| complete_onboarding | - | TBD |

---

## 四、Notion 文档结构

### 4.1 VitaFlow 相关页面
- 📊 VitaFlow - 数据体系
- 🧪 VitaFlow - QA 测试
- 💻 VitaFlow - 开发技术
- 📱 VitaFlow - 产品设计
- 📈 VitaFlow - 运营增长

### 4.2 竞品分析
- 🔬 竞品 Onboarding 分析计划
- Notion 链接：https://www.notion.so/2cb0b38dce1681e1a6fcc3828a64b3ad

---

## 五、Figma 集成

### 5.1 MCP 功能
- 获取设计上下文 - 生成 UI 代码
- 获取变量定义 - 颜色、字体、间距
- 获取截图 - 节点截图
- 获取元数据 - XML 格式结构
- 创建设计系统规则

### 5.2 UI 元素
- 食物营养信息展示（如 "Hunter's Fried Chicken"）
- 卡路里信息（如 "389 Calories"）

---

## 六、对话文件清单

| 日期 | 文件 | 大小 | 主题 |
|------|------|------|------|
| 12/24 | `FigmaMCP_VitaFlow_1224.txt` | 6.2MB | Figma MCP + 埋点 |
| 12/22 | `VitaFlow_Onboarding_1222.txt` | 2.4MB | Onboarding 设计 |
| 12/20 | `VitaFlow_CRISPE_1220.txt` | 994KB | CRISPE 框架 |
| 12/19 | 产品调研项目 | 1.8MB | 竞品分析 |
| 12/17~18 | 多个文件 | ~700KB | 各项功能开发 |

---

## 七、待办事项

### 7.1 Action Items（从对话中提取）
- [ ] 商标注册
- [ ] UGC 创作者联系
- [ ] Onboarding 竞品分析
- [ ] PostHog 分析框架

### 7.2 开发任务
- [ ] Demo-Onboarding 页面
- [ ] Scan 功能
- [ ] Dashboard
- [ ] MealDetail
- [ ] FoodDatabase

---

## 附录：原始对话文件

完整对话内容见 `docs/chat-exports/` 目录：
- `FigmaMCP_VitaFlow_1224.txt`
- `VitaFlow_Onboarding_1222.txt`
- `VitaFlow_CRISPE_1220.txt`




