# Notion 导入指南

## 📋 需要导入的文件

以下报告已生成，可以导入 Notion：

| 文件 | 位置 | 说明 |
|------|------|------|
| 分析报告 | `reports/onboarding_analysis_report.md` | 完整竞品分析报告 |
| VitaFlow 设计建议 | `reports/vitaflow_onboarding_design.md` | Onboarding 设计方案 |
| 统计数据 | `statistics.json` | 可转换为 Notion Database |
| 对比报告 | `comparison_report.json` | 三方案对比结果 |

---

## 🔧 导入方法

### 方法 1: 直接复制 Markdown

1. 打开 `onboarding_analysis_report.md` 或 `vitaflow_onboarding_design.md`
2. 复制全部内容
3. 在 Notion 中创建新页面
4. 粘贴内容（Notion 会自动解析 Markdown 格式）

### 方法 2: 使用 Notion Import

1. 在 Notion 中点击 Import
2. 选择 "Markdown & CSV"
3. 上传 `.md` 文件

### 方法 3: JSON 数据转 Database

对于 `statistics.json`，可以：

1. 使用 Python 脚本转换为 CSV：

```python
import json
import pandas as pd

with open('statistics.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 转换 onboarding 长度数据
apps_df = pd.DataFrame(data['onboarding_length_statistics']['by_app'])
apps_df.to_csv('apps_onboarding_length.csv', index=False)
```

2. 在 Notion 中 Import CSV 创建 Database

---

## 📊 建议的 Notion 结构

```
📁 VitaFlow 项目
├── 📄 竞品分析报告
│   ├── 执行摘要
│   ├── 研究范围
│   ├── 统计分析
│   └── 设计建议
├── 📊 App 数据库 (Database)
│   └── 15个App的Onboarding数据
├── 📋 设计假设 (Database)
│   └── 5个可测试假设
├── 📄 VitaFlow 设计方案
│   ├── 流程结构
│   ├── 页面设计
│   └── A/B测试计划
└── ✅ 执行清单
    └── 任务追踪
```

---

## 🔗 Notion API 自动同步（高级）

如需自动同步，可以使用 Notion API：

1. 创建 Notion Integration: https://www.notion.so/my-integrations
2. 获取 API Key
3. 运行以下脚本：

```python
# notion_sync.py
import json
import requests

NOTION_TOKEN = "your_notion_token"
DATABASE_ID = "your_database_id"

def create_page(title, content):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]}
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# 使用示例
with open('reports/onboarding_analysis_report.md', 'r', encoding='utf-8') as f:
    content = f.read()
    
create_page("Onboarding 竞品分析报告", content[:2000])  # Notion API 有长度限制
```

---

## ✅ 导入检查清单

- [ ] 创建 Notion 工作区结构
- [ ] 导入分析报告
- [ ] 导入 VitaFlow 设计方案
- [ ] 创建 App 数据库并导入数据
- [ ] 创建执行任务清单
- [ ] 分享给团队成员

---

*如需帮助，请联系项目负责人*
