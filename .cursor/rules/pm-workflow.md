# PM 工作流程与项目结构

## 核心能力
1. **截图采集** - 从 screensdesign.com / mobbin.com 下载产品截图，支持会员登录
2. **流程分类** - 三层分类：Stage（阶段）/ Module（模块）/ Feature（功能）
3. **命名规范** - Screen_001.png, Screen_002.png... 绝对编号格式
4. **排序工具** - 可视化拖拽排序，支持手动校正截图顺序
5. **文档生成** - 生成流程分析、设计亮点、截图清单等文档

---

## 工作流程

### 截图分析流程
1. 下载截图 → 2. 手动排序校正 → 3. 应用排序（重命名文件） → 4. AI分类分析 → 5. 整合交付

### 竞品 Onboarding 分析流程
1. **实机验证**（人工）：确认截图顺序正确、无缺失
2. **标记 Onboarding**：在 PM_Screenshot_Tool Web 界面标记
3. **提取 Taxonomy**（AI）：从所有验证数据中提取统一页面类型分类
4. **批量标注**（AI）：用 Taxonomy 对所有 App 页面分类
5. **统计分析**（AI）：覆盖率、顺序模式、设计洞察
6. **输出设计**：VitaFlow Onboarding 逻辑设计

---

## 三层分类体系

### Stage（阶段）
- Onboarding - 新用户引导
- Core - 核心功能  
- Monetization - 变现相关

### Module（模块）
- 登录注册、权限请求、个性化设置、Paywall、首页、记录、统计等

### Feature（功能点）
- 具体的功能描述

---

## 重点模块分析维度

### Onboarding
- 步骤数量和类型（信息收集/激励/结果）
- 激励穿插设计
- 个性化程度
- Paywall位置

### 付费流程
- 免费试用设计
- 价格展示
- 套餐对比
- 促销策略

---

## 项目文件结构
```
PM_Screenshot_Tool/
├── app.py                    # Flask 主应用
├── templates/
│   ├── index.html            # 主展示页面
│   └── sort_screens.html     # 排序工具页面
├── config/
│   ├── page_types.json       # 页面类型配置（含中英文、图标）
│   ├── taxonomy.json         # 分类体系
│   └── tags_library.json     # 标签库
├── projects/
│   └── [项目名]Analysis/
│       ├── Screens/          # 截图文件夹
│       ├── ai_analysis.json  # AI分类结果
│       ├── descriptions.json # 截图描述
│       └── custom_order.json # 自定义排序
└── data/
    ├── competitors.json      # Sensor Tower竞品数据
    └── top30_must_study.csv  # Top30必研究列表
```

---

## API 端点
- `GET /api/projects` - 获取项目列表
- `GET /api/screenshots/<project>` - 获取截图列表
- `GET /api/sort-order/<project>` - 获取排序
- `POST /api/sort-order/<project>` - 保存排序
- `POST /api/apply-sort-order/<project>` - 应用排序（重命名文件）

---

## Notion 工作空间

### 私人区文件夹
- 📊 VitaFlow - 数据体系
- 🧪 VitaFlow - QA 测试
- 💻 VitaFlow - 开发技术
- 📱 VitaFlow - 产品设计
- 📈 VitaFlow - 运营增长

### 常用页面
- 📋 Zino 任务管理：https://www.notion.so/2833dd1c67fb4aafa2f11fb09d842f82
- 🔬 竞品 Onboarding 分析计划：https://www.notion.so/2cb0b38dce1681e1a6fcc3828a64b3ad

---

## 工作模式
- **全局优先**：先建立整体框架，再深入细节
- **数据驱动**：不拍脑袋定转化率，用数据说话
- **参考导向**：任何设计都找具体竞品参考
- **人机协作**：人做判断和验证，AI 做批量处理和统计

