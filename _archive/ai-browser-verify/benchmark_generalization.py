"""
SkillWeaver 知识库对比与泛化能力测试

测试目标：
1. 量化证明有知识库 vs 无知识库的执行效率差异
2. 在 6 种不同类型网站上验证泛化能力

测试流程：
Phase 1: Explore - AI 自动探索网站生成知识库
Phase 2: Benchmark - 对比有/无知识库执行效率
Phase 3: Report - 生成量化报告
"""
import subprocess
import sys
import os
import time
import json
import shutil
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 设置环境变量 - 最新模型 API Keys
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLWEAVER_PATH = os.path.join(SCRIPT_DIR, "SkillWeaver")
PYRIGHT_PATH = r"C:\Users\WIN\AppData\Local\Python\pythoncore-3.14-64\Scripts"
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
EXPLORE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "explore_output_new")

# 2025年12月最新模型配置
LATEST_MODELS = {
    "openai": "gpt-5.2",
    "anthropic": "claude-opus-4-5-20251101",
    "google": "gemini-3-flash-preview",
}
DEFAULT_MODEL = LATEST_MODELS["openai"]

# ============================================================================
# 测试网站配置
# ============================================================================
TEST_WEBSITES = [
    {
        "name": "HackerNews",
        "type": "news",
        "url": "https://news.ycombinator.com",
        "domain": "news.ycombinator.com",
        "task": "获取当前排名第一的新闻标题",
        "explore_iterations": 5,
    },
    {
        "name": "GitHub",
        "type": "productivity",
        "url": "https://github.com",
        "domain": "github.com",
        "task": "搜索 'playwright' 仓库并获取第一个结果的 star 数",
        "explore_iterations": 5,
    },
    {
        "name": "Reddit",
        "type": "social",
        "url": "https://www.reddit.com",
        "domain": "www.reddit.com",
        "task": "进入 r/programming 并获取当前热门帖子的标题",
        "explore_iterations": 5,
    },
    {
        "name": "Amazon",
        "type": "ecommerce",
        "url": "https://www.amazon.com",
        "domain": "www.amazon.com",
        "task": "搜索 'wireless mouse' 并获取第一个商品的价格",
        "explore_iterations": 5,
    },
    {
        "name": "DuckDuckGo",
        "type": "search",
        "url": "https://duckduckgo.com",
        "domain": "duckduckgo.com",
        "task": "搜索 'Python programming' 并获取第一个搜索结果的标题",
        "explore_iterations": 5,
    },
    {
        "name": "CoinGecko",
        "type": "finance",
        "url": "https://www.coingecko.com",
        "domain": "www.coingecko.com",
        "task": "获取 Bitcoin 的当前价格",
        "explore_iterations": 5,
    },
]

# ============================================================================
# 数据结构
# ============================================================================
@dataclass
class RunResult:
    """单次执行结果"""
    success: bool
    time_seconds: float
    steps_count: int
    api_calls: int
    error: Optional[str] = None
    output: str = ""

@dataclass
class BenchmarkResult:
    """单个网站的基准测试结果"""
    website_name: str
    website_type: str
    explore_time: float
    explore_success: bool
    kb_generated: bool
    
    # 无知识库执行结果（多次运行）
    without_kb_runs: List[RunResult] = field(default_factory=list)
    
    # 有知识库执行结果（多次运行）
    with_kb_runs: List[RunResult] = field(default_factory=list)
    
    def avg_time_without_kb(self) -> float:
        times = [r.time_seconds for r in self.without_kb_runs if r.success]
        return sum(times) / len(times) if times else 0
    
    def avg_time_with_kb(self) -> float:
        times = [r.time_seconds for r in self.with_kb_runs if r.success]
        return sum(times) / len(times) if times else 0
    
    def success_rate_without_kb(self) -> float:
        if not self.without_kb_runs:
            return 0
        return sum(1 for r in self.without_kb_runs if r.success) / len(self.without_kb_runs)
    
    def success_rate_with_kb(self) -> float:
        if not self.with_kb_runs:
            return 0
        return sum(1 for r in self.with_kb_runs if r.success) / len(self.with_kb_runs)
    
    def speedup(self) -> Optional[float]:
        avg_without = self.avg_time_without_kb()
        avg_with = self.avg_time_with_kb()
        if avg_with > 0 and avg_without > 0:
            return avg_without / avg_with
        return None

# ============================================================================
# 核心函数
# ============================================================================
def get_env() -> dict:
    """获取运行环境变量"""
    env = os.environ.copy()
    env["PYTHONPATH"] = SKILLWEAVER_PATH + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = PYRIGHT_PATH + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_explore(website: dict, out_dir: str) -> Dict[str, Any]:
    """
    运行 SkillWeaver explore - 让 AI 自动探索网站并学习技能
    """
    print(f"\n{'='*60}")
    print(f"  EXPLORE: {website['name']} ({website['type']})")
    print(f"  URL: {website['url']}")
    print(f"  迭代次数: {website['explore_iterations']}")
    print(f"{'='*60}\n")
    
    # 清理旧目录
    if os.path.exists(out_dir):
        try:
            shutil.rmtree(out_dir)
        except PermissionError:
            print(f"警告: 无法删除旧目录 {out_dir}，继续...")
    os.makedirs(out_dir, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "skillweaver.explore",
        website["domain"],
        out_dir,
        "--iterations", str(website["explore_iterations"]),
        "--agent-lm-name", DEFAULT_MODEL,
        "--api-synthesis-lm-name", DEFAULT_MODEL,
        "--success-check-lm-name", DEFAULT_MODEL,
        "--explore-schedule", "test_probability:0.3",
    ]
    
    print(f"命令: {' '.join(cmd[:5])}...")
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=SKILLWEAVER_PATH,
            env=get_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        
        output_lines = []
        for line in process.stdout:
            print(f"  {line}", end='')
            output_lines.append(line)
        
        process.wait()
        elapsed = time.time() - start_time
        
        return {
            "success": process.returncode == 0,
            "time": elapsed,
            "output": "".join(output_lines),
            "returncode": process.returncode,
        }
    
    except Exception as e:
        return {
            "success": False,
            "time": time.time() - start_time,
            "output": str(e),
            "returncode": -1,
        }


def find_knowledge_base(out_dir: str) -> Optional[str]:
    """查找生成的知识库路径"""
    if not os.path.exists(out_dir):
        return None
    
    # 查找最新的迭代目录中的知识库
    for item in sorted(os.listdir(out_dir), reverse=True):
        item_path = os.path.join(out_dir, item)
        if os.path.isdir(item_path) and item.startswith("iter_"):
            # 检查是否有知识库代码文件
            kb_post_code = os.path.join(item_path, "kb_post_code.py")
            if os.path.exists(kb_post_code):
                # 检查文件是否非空
                with open(kb_post_code, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                    if content and len(content) > 50:  # 有实际内容
                        return item_path
    return None


def count_steps_from_output(output: str) -> int:
    """从输出中统计执行步骤数"""
    # 匹配 "Step X" 模式
    steps = re.findall(r'Step (\d+)', output)
    if steps:
        return max(int(s) for s in steps) + 1
    return 0


def count_api_calls_from_output(output: str) -> int:
    """从输出中统计 API 调用次数"""
    # 匹配常见的 API 调用模式
    patterns = [
        r'Executing \d+',
        r'Generated code',
        r'API 调用',
        r'completion_openai',
        r'completion_anthropic',
        r'completion_gemini',
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, output, re.IGNORECASE))
    return max(count, 1)  # 至少 1 次


def run_attempt_task(
    url: str, 
    task: str, 
    knowledge_base_path: Optional[str] = None, 
    max_steps: int = 10,
    timeout: int = 180,
) -> RunResult:
    """运行 SkillWeaver attempt_task 并收集指标"""
    cmd = [
        sys.executable, "-m", "skillweaver.attempt_task",
        url,
        task,
        "--max-steps", str(max_steps),
        "--headless",
        "--agent-lm-name", DEFAULT_MODEL,
    ]
    
    if knowledge_base_path:
        cmd.extend(["--knowledge-base-path-prefix", knowledge_base_path])
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SKILLWEAVER_PATH,
            env=get_env(),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        
        elapsed = time.time() - start_time
        output = result.stdout + result.stderr
        
        return RunResult(
            success=result.returncode == 0,
            time_seconds=elapsed,
            steps_count=count_steps_from_output(output),
            api_calls=count_api_calls_from_output(output),
            output=output,
        )
    
    except subprocess.TimeoutExpired:
        return RunResult(
            success=False,
            time_seconds=timeout,
            steps_count=0,
            api_calls=0,
            error="Timeout",
        )
    except Exception as e:
        return RunResult(
            success=False,
            time_seconds=time.time() - start_time,
            steps_count=0,
            api_calls=0,
            error=str(e),
        )


def benchmark_website(website: dict, runs_per_test: int = 3) -> BenchmarkResult:
    """对单个网站进行完整的基准测试"""
    print(f"\n{'#'*70}")
    print(f"  开始测试: {website['name']} ({website['type']})")
    print(f"{'#'*70}")
    
    out_dir = os.path.join(EXPLORE_OUTPUT_DIR, website['name'].lower())
    
    # Phase 1: Explore
    print("\n[Phase 1] 探索阶段 - AI 学习网站操作")
    explore_result = run_explore(website, out_dir)
    
    kb_path = find_knowledge_base(out_dir)
    kb_generated = kb_path is not None
    
    print(f"\n探索完成: 耗时 {explore_result['time']:.1f}s | 成功: {explore_result['success']}")
    print(f"知识库生成: {'是' if kb_generated else '否'}")
    if kb_path:
        print(f"知识库路径: {kb_path}")
    
    result = BenchmarkResult(
        website_name=website['name'],
        website_type=website['type'],
        explore_time=explore_result['time'],
        explore_success=explore_result['success'],
        kb_generated=kb_generated,
    )
    
    # Phase 2: Benchmark
    print(f"\n[Phase 2] 基准测试阶段 - 执行 {runs_per_test} 次对比")
    
    # 无知识库测试
    print(f"\n  测试 A: 无知识库")
    for i in range(runs_per_test):
        print(f"    运行 {i+1}/{runs_per_test}...", end=" ", flush=True)
        run_result = run_attempt_task(website['url'], website['task'], None)
        result.without_kb_runs.append(run_result)
        status = "成功" if run_result.success else "失败"
        print(f"{status} ({run_result.time_seconds:.1f}s, {run_result.steps_count} 步)")
    
    # 有知识库测试（如果知识库存在）
    if kb_generated:
        print(f"\n  测试 B: 有知识库")
        for i in range(runs_per_test):
            print(f"    运行 {i+1}/{runs_per_test}...", end=" ", flush=True)
            run_result = run_attempt_task(website['url'], website['task'], kb_path)
            result.with_kb_runs.append(run_result)
            status = "成功" if run_result.success else "失败"
            print(f"{status} ({run_result.time_seconds:.1f}s, {run_result.steps_count} 步)")
    else:
        print(f"\n  测试 B: 跳过（无知识库）")
    
    # 打印该网站的结果摘要
    print(f"\n  --- {website['name']} 结果摘要 ---")
    print(f"  无KB平均时间: {result.avg_time_without_kb():.1f}s | 成功率: {result.success_rate_without_kb()*100:.0f}%")
    if kb_generated:
        print(f"  有KB平均时间: {result.avg_time_with_kb():.1f}s | 成功率: {result.success_rate_with_kb()*100:.0f}%")
        speedup = result.speedup()
        if speedup:
            print(f"  加速比: {speedup:.2f}x")
    
    return result


def generate_report(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """生成综合报告"""
    
    # 计算汇总统计
    total_websites = len(results)
    kb_generated_count = sum(1 for r in results if r.kb_generated)
    
    # 计算平均加速比（仅统计有知识库的网站）
    speedups = [r.speedup() for r in results if r.speedup() is not None]
    avg_speedup = sum(speedups) / len(speedups) if speedups else None
    
    # 计算平均成功率
    all_without_kb_success = []
    all_with_kb_success = []
    for r in results:
        all_without_kb_success.extend([run.success for run in r.without_kb_runs])
        all_with_kb_success.extend([run.success for run in r.with_kb_runs])
    
    success_rate_without = sum(all_without_kb_success) / len(all_without_kb_success) if all_without_kb_success else 0
    success_rate_with = sum(all_with_kb_success) / len(all_with_kb_success) if all_with_kb_success else 0
    
    report = {
        "meta": {
            "timestamp": datetime.now().isoformat(),
            "model": DEFAULT_MODEL,
            "total_websites": total_websites,
            "kb_generated_count": kb_generated_count,
        },
        "summary": {
            "avg_speedup": avg_speedup,
            "success_rate_without_kb": success_rate_without,
            "success_rate_with_kb": success_rate_with,
            "success_rate_improvement": success_rate_with - success_rate_without if all_with_kb_success else None,
        },
        "per_website": {},
    }
    
    for r in results:
        report["per_website"][r.website_name] = {
            "type": r.website_type,
            "explore_time": r.explore_time,
            "explore_success": r.explore_success,
            "kb_generated": r.kb_generated,
            "without_kb": {
                "avg_time": r.avg_time_without_kb(),
                "success_rate": r.success_rate_without_kb(),
                "runs": [asdict(run) for run in r.without_kb_runs],
            },
            "with_kb": {
                "avg_time": r.avg_time_with_kb(),
                "success_rate": r.success_rate_with_kb(),
                "runs": [asdict(run) for run in r.with_kb_runs],
            } if r.kb_generated else None,
            "speedup": r.speedup(),
        }
    
    return report


def generate_markdown_report(report: Dict[str, Any]) -> str:
    """生成 Markdown 格式的报告"""
    md = []
    md.append("# SkillWeaver 知识库对比与泛化能力测试报告")
    md.append("")
    md.append(f"**测试时间**: {report['meta']['timestamp']}")
    md.append(f"**使用模型**: {report['meta']['model']}")
    md.append("")
    
    # 汇总统计
    md.append("## 汇总统计")
    md.append("")
    summary = report['summary']
    
    md.append("| 指标 | 数值 |")
    md.append("|------|------|")
    md.append(f"| 测试网站数 | {report['meta']['total_websites']} |")
    md.append(f"| 成功生成知识库 | {report['meta']['kb_generated_count']} |")
    
    if summary['avg_speedup']:
        md.append(f"| **平均加速比** | **{summary['avg_speedup']:.2f}x** |")
    
    md.append(f"| 无KB成功率 | {summary['success_rate_without_kb']*100:.1f}% |")
    md.append(f"| 有KB成功率 | {summary['success_rate_with_kb']*100:.1f}% |")
    
    if summary['success_rate_improvement'] is not None:
        improvement = summary['success_rate_improvement'] * 100
        sign = "+" if improvement >= 0 else ""
        md.append(f"| 成功率提升 | {sign}{improvement:.1f}% |")
    
    md.append("")
    
    # 各网站详细结果
    md.append("## 各网站测试结果")
    md.append("")
    md.append("| 网站 | 类型 | 探索时间 | 无KB时间 | 有KB时间 | 加速比 | 无KB成功率 | 有KB成功率 |")
    md.append("|------|------|----------|----------|----------|--------|------------|------------|")
    
    for name, data in report['per_website'].items():
        explore_time = f"{data['explore_time']:.0f}s"
        without_time = f"{data['without_kb']['avg_time']:.1f}s" if data['without_kb']['avg_time'] > 0 else "N/A"
        with_time = f"{data['with_kb']['avg_time']:.1f}s" if data['with_kb'] and data['with_kb']['avg_time'] > 0 else "N/A"
        speedup = f"{data['speedup']:.2f}x" if data['speedup'] else "N/A"
        without_rate = f"{data['without_kb']['success_rate']*100:.0f}%"
        with_rate = f"{data['with_kb']['success_rate']*100:.0f}%" if data['with_kb'] else "N/A"
        
        md.append(f"| {name} | {data['type']} | {explore_time} | {without_time} | {with_time} | {speedup} | {without_rate} | {with_rate} |")
    
    md.append("")
    
    # 结论
    md.append("## 结论")
    md.append("")
    
    if summary['avg_speedup'] and summary['avg_speedup'] > 1:
        md.append(f"- **知识库有效**: 平均加速比为 **{summary['avg_speedup']:.2f}x**，证明 AI 学习到的技能可以提升执行效率")
    else:
        md.append("- 知识库效果待验证，需要更多测试数据")
    
    if summary['success_rate_improvement'] and summary['success_rate_improvement'] > 0:
        md.append(f"- **成功率提升**: 有知识库时成功率提升 **{summary['success_rate_improvement']*100:.1f}%**")
    
    md.append(f"- **泛化能力**: 在 {report['meta']['total_websites']} 种不同类型网站上进行了测试")
    
    md.append("")
    md.append("---")
    md.append("*此报告由 benchmark_generalization.py 自动生成*")
    
    return "\n".join(md)


def main():
    """主函数"""
    print("=" * 70)
    print("  SkillWeaver 知识库对比与泛化能力测试")
    print("  Knowledge Base Comparison & Generalization Benchmark")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模型: {DEFAULT_MODEL}")
    print(f"测试网站数: {len(TEST_WEBSITES)}")
    print(f"每个测试运行次数: 3")
    print()
    
    # 创建输出目录
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(EXPLORE_OUTPUT_DIR, exist_ok=True)
    
    # 运行测试
    results: List[BenchmarkResult] = []
    
    for i, website in enumerate(TEST_WEBSITES):
        print(f"\n[{i+1}/{len(TEST_WEBSITES)}] 测试网站: {website['name']}")
        try:
            result = benchmark_website(website, runs_per_test=3)
            results.append(result)
        except Exception as e:
            print(f"错误: 测试 {website['name']} 失败 - {e}")
            import traceback
            traceback.print_exc()
    
    # 生成报告
    print("\n" + "=" * 70)
    print("  生成报告")
    print("=" * 70)
    
    report = generate_report(results)
    
    # 保存 JSON 报告
    json_path = os.path.join(RESULTS_DIR, "generalization_benchmark.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"JSON 报告: {json_path}")
    
    # 保存 Markdown 报告
    md_report = generate_markdown_report(report)
    md_path = os.path.join(RESULTS_DIR, "GENERALIZATION_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"Markdown 报告: {md_path}")
    
    # 打印最终摘要
    print("\n" + "=" * 70)
    print("  最终结果摘要")
    print("=" * 70)
    
    summary = report['summary']
    print(f"测试网站数: {report['meta']['total_websites']}")
    print(f"成功生成知识库: {report['meta']['kb_generated_count']}")
    
    if summary['avg_speedup']:
        print(f"平均加速比: {summary['avg_speedup']:.2f}x")
    
    print(f"无KB成功率: {summary['success_rate_without_kb']*100:.1f}%")
    print(f"有KB成功率: {summary['success_rate_with_kb']*100:.1f}%")
    
    print("\n测试完成！")


if __name__ == "__main__":
    main()
