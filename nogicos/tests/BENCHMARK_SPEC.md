# NogicOS Benchmark Specification

> 基于 WebArena、OSWorld、AgentBench 等权威基准的测试标准

## 一、参考基准

| 基准 | 来源 | 评估领域 |
|------|------|----------|
| **WebArena** | CMU | 浏览器自动化 |
| **OSWorld** | CMU/PKU | 桌面操作系统自动化 |
| **SWE-bench** | Princeton | 软件工程任务 |
| **AgentBench** | Tsinghua | 综合 Agent 能力 |
| **Anthropic Computer Use** | Anthropic | 计算机控制 |

---

## 二、评估维度

### 2.1 核心指标 (基于 WebArena/OSWorld)

| 指标 | 定义 | 计算方式 | 目标 |
|------|------|----------|------|
| **Success Rate (SR)** | 任务成功率 | 成功任务数 / 总任务数 | > 70% |
| **Step Efficiency (SE)** | 步骤效率 | 最优步骤数 / 实际步骤数 | > 50% |
| **Error Recovery (ER)** | 错误恢复率 | 恢复成功数 / 错误发生数 | > 60% |
| **Time to Complete (TTC)** | 完成时间 | 任务开始到结束的秒数 | 类型依赖 |

### 2.2 成功判定标准 (基于 WebArena Evaluator)

| 评估器类型 | 说明 | 适用场景 |
|------------|------|----------|
| **StringEvaluator** | 字符串匹配 | 内容提取、答案验证 |
| | - exact_match | 完全匹配 |
| | - must_include | 必须包含 |
| | - fuzzy_match | 模糊匹配 (LLM 判定) |
| **URLEvaluator** | URL 验证 | 导航任务 |
| **HTMLContentEvaluator** | 页面内容验证 | DOM 操作任务 |
| **FileEvaluator** | 文件验证 | 文件系统任务 |
| | - literal_match | 内容完全匹配 |
| | - check_json | JSON 结构验证 |
| | - check_csv | CSV 记录验证 |

---

## 三、任务分类 (基于 OSWorld)

### 3.1 Browser Tasks (浏览器任务)

| ID | 任务 | 难度 | 评估器 | 成功标准 |
|----|------|------|--------|----------|
| B001 | 导航到指定 URL | Easy | URLEvaluator | URL 匹配 |
| B002 | 在 Google 搜索关键词 | Easy | URLEvaluator + String | URL 含 query，结果显示 |
| B003 | 点击页面元素 | Medium | HTMLContentEvaluator | 目标元素状态变化 |
| B004 | 填写表单 | Medium | HTMLContentEvaluator | 表单值正确 |
| B005 | 提取页面数据 | Medium | StringEvaluator | 数据正确提取 |
| B006 | 多页面遍历 | Hard | StringEvaluator | 所有数据收集完成 |
| B007 | 登录认证 | Hard | URLEvaluator + HTML | 登录成功，跳转正确 |

### 3.2 Local Tasks (本地任务)

| ID | 任务 | 难度 | 评估器 | 成功标准 |
|----|------|------|--------|----------|
| L001 | 列出目录内容 | Easy | StringEvaluator | 返回文件列表 |
| L002 | 读取文件 | Easy | StringEvaluator | 返回正确内容 |
| L003 | 创建文件 | Easy | FileEvaluator | 文件存在且内容正确 |
| L004 | 搜索文件 | Medium | StringEvaluator | 返回匹配结果 |
| L005 | 移动/重命名文件 | Medium | FileEvaluator | 源不存在，目标存在 |
| L006 | 执行 Shell 命令 | Medium | StringEvaluator | 命令输出正确 |
| L007 | 文件内容搜索 (grep) | Medium | StringEvaluator | 返回匹配行 |
| L008 | 复杂文件整理 | Hard | FileEvaluator | 目录结构符合预期 |

### 3.3 Mixed Tasks (混合任务)

| ID | 任务 | 难度 | 评估器 | 成功标准 |
|----|------|------|--------|----------|
| M001 | 下载网页内容到本地 | Medium | FileEvaluator | 文件存在且内容正确 |
| M002 | 从网页提取数据保存为 JSON | Medium | FileEvaluator (check_json) | JSON 格式和内容正确 |
| M003 | 遍历网站生成报告 | Hard | FileEvaluator + String | 报告完整且准确 |
| M004 | Web 数据分析 + 本地输出 | Hard | FileEvaluator + String | 分析结果正确 |

---

## 四、测试用例定义格式

```json
{
  "task_id": "B001",
  "category": "browser",
  "difficulty": "easy",
  "task": "Navigate to https://example.com",
  "evaluator": {
    "type": "url",
    "expected": "https://example.com",
    "match_mode": "contains"
  },
  "timeout_seconds": 30,
  "max_steps": 5
}
```

```json
{
  "task_id": "M002",
  "category": "mixed",
  "difficulty": "medium",
  "task": "Go to https://example.com and save the page title and first paragraph to ~/test_output.json",
  "evaluator": {
    "type": "file",
    "path": "~/test_output.json",
    "checks": [
      {"type": "exists"},
      {"type": "json_valid"},
      {"type": "json_has_key", "key": "title"},
      {"type": "json_has_key", "key": "paragraph"}
    ]
  },
  "timeout_seconds": 60,
  "max_steps": 10
}
```

---

## 五、评分公式

### 5.1 单任务评分

```
Score = Evaluator_Score × Efficiency_Bonus × Time_Bonus

where:
- Evaluator_Score ∈ [0, 1]  # 评估器返回
- Efficiency_Bonus = min(1.0, optimal_steps / actual_steps)
- Time_Bonus = min(1.0, timeout / actual_time) if success else 0
```

### 5.2 综合评分

```
Overall_Score = Σ(Category_Weight × Category_Score)

Category_Score = Σ(Task_Score) / Task_Count

Weights:
- Browser: 0.35
- Local: 0.35
- Mixed: 0.30
```

---

## 六、成熟度等级映射

| Success Rate | Level | 描述 |
|--------------|-------|------|
| < 30% | L1 Prototype | 概念验证 |
| 30-50% | L2 Alpha | 基础功能 |
| 50-70% | L3 Beta | 稳定可用 |
| 70-85% | L4 Launch | 可发布 |
| > 85% | L5 Growth | 成熟产品 |

---

## 七、测试执行

### 7.1 测试环境

```
- OS: Windows 10/11 或 macOS
- Python: 3.10+
- Playwright: 已安装浏览器
- 网络: 可访问公网
```

### 7.2 运行命令

```bash
# 运行完整基准测试
python -m pytest tests/benchmark/ -v --benchmark

# 运行特定类别
python -m pytest tests/benchmark/test_browser.py -v
python -m pytest tests/benchmark/test_local.py -v
python -m pytest tests/benchmark/test_mixed.py -v

# 生成报告
python tests/benchmark/run_benchmark.py --output results/
```

### 7.3 输出格式

```json
{
  "timestamp": "2024-12-30T12:00:00Z",
  "version": "2.0.0",
  "overall_score": 0.72,
  "level": "L4",
  "categories": {
    "browser": {"score": 0.75, "passed": 6, "total": 7},
    "local": {"score": 0.88, "passed": 7, "total": 8},
    "mixed": {"score": 0.50, "passed": 2, "total": 4}
  },
  "metrics": {
    "success_rate": 0.79,
    "avg_steps": 4.2,
    "avg_time_seconds": 23.5,
    "error_recovery_rate": 0.60
  },
  "tasks": [...]
}
```

---

## 八、参考资料

- WebArena: https://github.com/web-arena-x/webarena
- OSWorld: https://github.com/xlang-ai/OSWorld
- AgentBench: https://github.com/THUDM/AgentBench
- SWE-bench: https://github.com/princeton-nlp/SWE-bench
- Anthropic Computer Use: https://github.com/anthropics/anthropic-quickstarts

---

*文档版本: 1.0*
*基于: WebArena Evaluator + OSWorld Metrics*


