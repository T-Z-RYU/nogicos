# 任务：创建浏览器专项测试集

> 状态：待执行  
> 优先级：P1  
> 创建日期：2026-01-05  
> 来源：Browser 功能诊断对话

---

## 背景

### 问题现象
用户让 NogicOS 执行 "帮我看一下 YC 官网" 任务时：
1. ❌ 没有展示浏览器操作过程
2. ❌ 返回的信息是错误的（疑似 hallucination）
3. ❌ 没有生成截图

### 诊断结果

| 组件 | 状态 | 验证方式 |
|------|------|----------|
| Playwright | ✅ 正常 | `test_browser_quick.py` |
| BrowserSession | ✅ 正常 | 导航、提取、截图全部成功 |
| 截图功能 | ✅ 正常 | 生成 348KB 截图 |
| **Agent 调用链路** | ❓ 待查 | 需要专项测试 |

**结论**：Browser 底层正常，问题在 Agent 层。

---

## 现有评估体系

### 评估器（已有）
```
规则评估器（4个）：latency, token_count, tool_call_count, error_rate
UX 评估器（3个）：ttft, follow_up, content_richness  
LLM 评估器（5个）：task_completion, tool_selection, correctness, hallucination, conciseness
```

### 测试集（不足）
- `COMPREHENSIVE_EXAMPLES`：54 个用例
- 浏览器相关：仅 **6 个**，且都是基础操作
- **缺失**：无 anti-hallucination 验证用例

---

## 解决方案

### 创建浏览器专项测试集

**目标**：验证 Browser 功能端到端正确性，特别是 anti-hallucination

**测试用例设计原则**：
1. **强制真实数据** - 答案必须从网页获取，不能用训练数据
2. **验证工具调用** - trajectory 必须包含正确的 browser tools
3. **验证数据完整性** - 截图必须有真实 base64 数据

### 建议测试用例（20个）

```python
BROWSER_TEST_CASES = [
    # === 1. 导航验证（4个）===
    {
        "id": "browser_nav_001",
        "input": "打开 https://www.ycombinator.com 告诉我页面标题",
        "expected_trajectory": ["browser_navigate"],
        "validation": {
            "type": "exact_match",
            "expected": "Y Combinator",  # 必须是真实标题
            "anti_hallucination": True,
        }
    },
    {
        "id": "browser_nav_002",
        "input": "访问 https://news.ycombinator.com 第一条新闻标题是什么",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "realtime_data",  # 必须是实时数据
            "min_length": 10,
        }
    },
    {
        "id": "browser_nav_003",
        "input": "打开 example.com 页面上写了什么",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "must_include",
            "patterns": ["Example Domain", "illustrative examples"],
        }
    },
    {
        "id": "browser_nav_004",
        "input": "访问 github.com/trending 今天排名第一的仓库是什么",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "realtime_data",
            "anti_hallucination": True,
        }
    },

    # === 2. 截图验证（3个）===
    {
        "id": "browser_screenshot_001",
        "input": "打开 google.com 截个图给我看",
        "expected_trajectory": ["browser_navigate", "browser_screenshot"],
        "validation": {
            "type": "has_screenshot",
            "min_size_bytes": 10000,  # 至少 10KB
        }
    },
    {
        "id": "browser_screenshot_002",
        "input": "帮我截取 YC 官网首页",
        "expected_trajectory": ["browser_navigate", "browser_screenshot"],
        "validation": {
            "type": "has_screenshot",
            "min_size_bytes": 50000,
        }
    },
    {
        "id": "browser_screenshot_003",
        "input": "访问 https://www.anthropic.com 截图保存",
        "expected_trajectory": ["browser_navigate", "browser_screenshot"],
        "validation": {
            "type": "has_screenshot",
        }
    },

    # === 3. 内容提取验证（4个）===
    {
        "id": "browser_extract_001",
        "input": "提取 YC 官网首页的 tagline",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "must_include",
            "patterns": ["Make something people want"],  # YC 的真实 tagline
        }
    },
    {
        "id": "browser_extract_002",
        "input": "从 https://example.com 提取所有链接",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "must_include",
            "patterns": ["iana.org"],
        }
    },
    {
        "id": "browser_extract_003",
        "input": "查看 Hacker News 首页有多少条新闻",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "contains_number",
            "range": [20, 40],  # HN 首页通常 30 条左右
        }
    },
    {
        "id": "browser_extract_004",
        "input": "提取 https://httpbin.org/html 页面的标题",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "must_include",
            "patterns": ["Herman Melville"],  # httpbin 的固定内容
        }
    },

    # === 4. Anti-Hallucination 专项（5个）===
    {
        "id": "browser_anti_hal_001",
        "input": "YC 的申请截止日期是什么时候？去官网看一下",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "anti_hallucination",
            "forbidden_patterns": ["2024", "2023"],  # 不能用旧数据
            "must_call_browser": True,
        }
    },
    {
        "id": "browser_anti_hal_002",
        "input": "OpenAI 官网现在首页展示的是什么产品",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "realtime_data",
            "must_call_browser": True,
        }
    },
    {
        "id": "browser_anti_hal_003",
        "input": "GitHub 今天的 trending 仓库列表",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "realtime_data",
            "must_call_browser": True,
        }
    },
    {
        "id": "browser_anti_hal_004",
        "input": "查一下 Claude 3.5 的最新定价",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "realtime_data",
            "anti_hallucination": True,
        }
    },
    {
        "id": "browser_anti_hal_005",
        "input": "Anthropic 官网的 careers 页面有多少个职位",
        "expected_trajectory": ["browser_navigate", "browser_extract"],
        "validation": {
            "type": "realtime_data",
            "must_call_browser": True,
        }
    },

    # === 5. 多步骤任务（2个）===
    {
        "id": "browser_multi_001",
        "input": "打开 HN，提取前 3 条新闻标题，保存到 hn_news.txt",
        "expected_trajectory": ["browser_navigate", "browser_extract", "write_file"],
        "validation": {
            "type": "file_created",
            "path": "hn_news.txt",
        }
    },
    {
        "id": "browser_multi_002",
        "input": "截取 YC 官网首页，分析页面主要内容",
        "expected_trajectory": ["browser_navigate", "browser_screenshot", "browser_extract"],
        "validation": {
            "type": "has_screenshot_and_analysis",
        }
    },

    # === 6. 错误处理（2个）===
    {
        "id": "browser_error_001",
        "input": "打开 https://this-domain-does-not-exist-xyz.com",
        "expected_trajectory": ["browser_navigate"],
        "validation": {
            "type": "graceful_error",
            "must_include": ["无法", "错误", "失败", "error"],
        }
    },
    {
        "id": "browser_error_002",
        "input": "在没打开任何网页的情况下截图",
        "expected_trajectory": ["browser_screenshot"],
        "validation": {
            "type": "graceful_error",
        }
    },
]
```

---

## 实施步骤

### Phase 1: 创建测试集
1. [ ] 在 `dataset_manager.py` 添加 `BROWSER_TEST_CASES`
2. [ ] 创建 `create_browser_test_dataset()` 函数
3. [ ] 添加新的验证类型（`realtime_data`, `has_screenshot`, `anti_hallucination`）

### Phase 2: 扩展评估器
1. [ ] 增强 `hallucination_evaluator` 针对浏览器任务
2. [ ] 添加 `screenshot_validator` 评估器
3. [ ] 添加 `browser_tool_usage_evaluator` 评估器

### Phase 3: 运行测试
1. [ ] 本地运行测试集
2. [ ] 上传到 LangSmith
3. [ ] 分析结果，定位 Agent 层问题

---

## 预期产出

1. **20 个浏览器专项测试用例**
2. **3 个新评估器**
3. **Agent 层问题根因定位**

---

## 相关文件

- `nogicos/test_browser_quick.py` - Browser 底层测试（已通过）
- `nogicos/engine/evaluation/evaluators.py` - 评估器定义
- `nogicos/engine/evaluation/dataset_manager.py` - 测试集管理
- `nogicos/engine/browser/session.py` - BrowserSession 实现
- `nogicos/engine/agent/react_agent.py` - Agent 实现

---

## 执行命令

```bash
# 运行 Browser 底层测试
cd "C:/Users/WIN/Desktop/Cursor Project/nogicos"
python test_browser_quick.py

# 创建测试集（待实现）
python -c "from engine.evaluation.dataset_manager import create_browser_test_dataset; create_browser_test_dataset()"

# 运行评估（待实现）
python -m engine.evaluation.run_evaluation --dataset nogicos_browser_tests
```

