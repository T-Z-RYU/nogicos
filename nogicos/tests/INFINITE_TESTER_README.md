# NogicOS Infinite AI Tester

无限循环测试 NogicOS，直到 AI 认为产品稳定。

## 核心原理

```
┌─────────────────────────────────────────────────────────────┐
│                    Infinite Test Loop                        │
│                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│   │   AI     │───►│  Execute │───►│   AI     │              │
│   │ Generate │    │  Tests   │    │ Analyze  │              │
│   │  Cases   │    │          │    │ Results  │              │
│   └──────────┘    └──────────┘    └────┬─────┘              │
│                                        │                     │
│                    ┌───────────────────┴───────────────────┐│
│                    │                                       ││
│                    ▼                                       ▼│
│            ┌──────────────┐                    ┌──────────┐ │
│            │ Issues Found │───────────────────►│ Continue │ │
│            │              │                    │   Loop   │ │
│            └──────────────┘                    └──────────┘ │
│                                                     │       │
│            ┌──────────────┐                        │       │
│            │ N Rounds     │◄───────────────────────┘       │
│            │ Stable?      │                                 │
│            └──────┬───────┘                                 │
│                   │                                         │
│         Yes ──────┴────── No                               │
│          │                │                                 │
│          ▼                ▼                                 │
│    ┌──────────┐    ┌──────────┐                            │
│    │  STABLE  │    │ Continue │                            │
│    │   EXIT   │    │  Testing │                            │
│    └──────────┘    └──────────┘                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 方式一：PowerShell 脚本（推荐）

```powershell
cd nogicos
./scripts/run_infinite_test.ps1
```

自定义参数：

```powershell
./scripts/run_infinite_test.ps1 -MaxRounds 50 -StabilityThreshold 5 -TestsPerRound 15
```

### 方式二：直接运行 Python

```bash
cd nogicos
python -m tests.infinite_ai_tester
```

自定义参数：

```bash
python -m tests.infinite_ai_tester \
    --max-rounds 100 \
    --stability-threshold 3 \
    --tests-per-round 10 \
    --timeout 60
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--max-rounds` | 100 | 最大测试轮数 |
| `--stability-threshold` | 3 | 连续 N 轮无高危问题 = 稳定 |
| `--tests-per-round` | 10 | 每轮测试用例数 |
| `--timeout` | 60 | 单个测试超时时间（秒） |
| `--output` | tests/infinite_test_results | 输出目录 |

## 稳定性判断逻辑

系统通过以下标准判断产品是否稳定：

### 问题严重级别

| 级别 | 说明 | 对稳定性的影响 |
|------|------|----------------|
| `CRITICAL` | 崩溃、安全问题 | 立即判定为不稳定 |
| `HIGH` | Traceback 泄露、超时 | 判定为不稳定 |
| `MEDIUM` | 空响应、编码问题 | 需要 AI 综合判断 |
| `LOW` | 轻微警告 | 不影响稳定性 |

### 稳定条件

连续 N 轮（默认 3 轮）满足：
- 无 CRITICAL 级别问题
- 无 HIGH 级别问题
- AI 分析判定为稳定

## 输出文件

测试完成后，会在 `tests/infinite_test_results/` 生成：

```
infinite_test_results/
├── round_0001.json      # 第 1 轮详细结果
├── round_0002.json      # 第 2 轮详细结果
├── ...
├── final_report.txt     # 最终测试报告（人类可读）
└── full_results.json    # 完整数据（机器可读）
```

### final_report.txt 示例

```
============================================================
NogicOS INFINITE AI TESTER - FINAL REPORT
============================================================

Session: infinite_test_20250101_120000
Duration: 15.2 minutes

## Summary
- Total Rounds: 8
- Total Tests: 80
- Total Issues: 12
- Consecutive Stable Rounds: 3
- Final Status: ✓ STABLE

## Rounds Overview
  Round 1: 7/10 passed, 5 issues ✗
  Round 2: 8/10 passed, 3 issues ✗
  Round 3: 9/10 passed, 2 issues ✗
  Round 4: 9/10 passed, 1 issues ✗
  Round 5: 10/10 passed, 1 issues ✗
  Round 6: 10/10 passed, 0 issues ✓
  Round 7: 10/10 passed, 0 issues ✓
  Round 8: 10/10 passed, 0 issues ✓

## Issues by Type
  traceback_leaked: 5
  empty_response: 4
  timeout: 2
  encoding_error: 1

## Conclusion
Product is STABLE! ✓
```

## AI 测试用例生成

系统使用 Claude 动态生成测试用例，覆盖：

1. **文件操作** - 读写、搜索、整理
2. **Shell 命令** - 执行命令、查看结果
3. **中文处理** - 自然语言理解
4. **错误处理** - 边缘情况、异常输入
5. **复杂任务** - 多步骤任务

每轮测试后，AI 会：
- 分析失败的测试
- 生成针对已知问题的回归测试
- 探索新的边缘情况

## 问题检测

自动检测的问题类型：

| 类型 | 检测逻辑 |
|------|----------|
| `traceback_leaked` | 响应中包含 Python traceback |
| `empty_response` | 非空输入但响应为空 |
| `encoding_error` | 编码乱码（如 锟斤拷） |
| `unhandled_exception` | 未处理的异常泄露 |
| `malformed_tool_call` | 工具调用 XML 格式错误 |
| `timeout` | 测试超时 |
| `crash` | Agent 崩溃 |
| `safety_risk` | 危险命令（如 rm -rf） |

## 与其他测试的区别

| 特性 | `self_test_loop.py` | `auto_test_fix.py` | `infinite_ai_tester.py` |
|------|---------------------|---------------------|-------------------------|
| 测试用例 | 固定列表 | 模板随机 | **AI 动态生成** |
| 结果分析 | 规则检测 | 规则 + AI | **AI 深度分析** |
| 终止条件 | 固定轮数 | 固定轮数 | **AI 判断稳定** |
| 自动修复 | ❌ | ✓ | ❌（专注测试） |

## 最佳实践

### 开发中使用

```bash
# 快速验证（少量测试）
python -m tests.infinite_ai_tester --tests-per-round 5 --stability-threshold 2
```

### 发布前使用

```bash
# 全面测试（严格标准）
python -m tests.infinite_ai_tester --tests-per-round 20 --stability-threshold 5 --max-rounds 200
```

### CI/CD 集成

```yaml
# GitHub Actions 示例
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run Infinite AI Tester
      run: |
        cd nogicos
        python -m tests.infinite_ai_tester --max-rounds 50 --stability-threshold 3
```

## 注意事项

1. **API 消耗**：每轮测试会消耗 Anthropic API 额度，注意成本控制
2. **时间**：完整测试可能需要数小时，建议设置合理的 max-rounds
3. **后台运行**：长时间测试建议使用 `nohup` 或 tmux

```bash
# 后台运行示例
nohup python -m tests.infinite_ai_tester > test.log 2>&1 &
```

## FAQ

**Q: 如何中断测试？**
A: 按 Ctrl+C，系统会保存已完成的结果并生成报告

**Q: 测试总是通不过怎么办？**
A: 查看 `final_report.txt` 中的 Issues by Type，定位最常见的问题类型

**Q: 可以自定义测试用例吗？**
A: 可以修改 `_get_default_test_cases()` 方法添加自定义用例

**Q: 支持并行测试吗？**
A: 当前版本是串行执行，未来可能支持并行

