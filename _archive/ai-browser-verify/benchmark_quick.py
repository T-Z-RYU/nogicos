"""
SkillWeaver 快速泛化测试 (3 个网站)

测试目标：快速验证有/无知识库的效果差异
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

# 设置环境变量
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 路径配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLWEAVER_PATH = os.path.join(SCRIPT_DIR, "SkillWeaver")
PYRIGHT_PATH = r"C:\Users\WIN\AppData\Local\Python\pythoncore-3.14-64\Scripts"
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
EXPLORE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "explore_quick")

# 模型配置
DEFAULT_MODEL = "gpt-5.2"

# ============================================================================
# 快速测试: 3 个代表性网站
# ============================================================================
TEST_WEBSITES = [
    {
        "name": "HackerNews",
        "type": "news",
        "url": "https://news.ycombinator.com",
        "domain": "news.ycombinator.com",
        "task": "获取当前排名第一的新闻标题",
        "explore_iterations": 3,  # 减少迭代次数
    },
    {
        "name": "DuckDuckGo",
        "type": "search",
        "url": "https://duckduckgo.com",
        "domain": "duckduckgo.com",
        "task": "搜索 'Python' 并获取第一个搜索结果的标题",
        "explore_iterations": 3,
    },
    {
        "name": "CoinGecko",
        "type": "finance",
        "url": "https://www.coingecko.com",
        "domain": "www.coingecko.com",
        "task": "获取 Bitcoin 的当前价格",
        "explore_iterations": 3,
    },
]

@dataclass
class RunResult:
    success: bool
    time_seconds: float
    steps_count: int
    api_calls: int
    error: Optional[str] = None
    output: str = ""

@dataclass
class BenchmarkResult:
    website_name: str
    website_type: str
    explore_time: float
    explore_success: bool
    kb_generated: bool
    without_kb_runs: List[RunResult] = field(default_factory=list)
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


def get_env() -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = SKILLWEAVER_PATH + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = PYRIGHT_PATH + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_explore(website: dict, out_dir: str) -> Dict[str, Any]:
    print(f"\n{'='*60}")
    print(f"  EXPLORE: {website['name']} ({website['type']})")
    print(f"{'='*60}")
    
    # 强制清理旧目录
    if os.path.exists(out_dir):
        for retry in range(3):
            try:
                shutil.rmtree(out_dir)
                break
            except PermissionError:
                print(f"  目录被占用，等待重试 ({retry+1}/3)...")
                time.sleep(2)
    
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
            print(f"  {line.rstrip()}")
            output_lines.append(line)
        
        process.wait()
        elapsed = time.time() - start_time
        
        return {
            "success": process.returncode == 0,
            "time": elapsed,
            "output": "".join(output_lines),
        }
    
    except Exception as e:
        return {
            "success": False,
            "time": time.time() - start_time,
            "output": str(e),
        }


def find_knowledge_base(out_dir: str) -> Optional[str]:
    if not os.path.exists(out_dir):
        return None
    
    for item in sorted(os.listdir(out_dir), reverse=True):
        item_path = os.path.join(out_dir, item)
        if os.path.isdir(item_path) and item.startswith("iter_"):
            kb_post_code = os.path.join(item_path, "kb_post_code.py")
            if os.path.exists(kb_post_code):
                with open(kb_post_code, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                    if content and len(content) > 50:
                        return item_path
    return None


def count_steps_from_output(output: str) -> int:
    steps = re.findall(r'Step (\d+)', output)
    return max(int(s) for s in steps) + 1 if steps else 0


def run_attempt_task(url: str, task: str, knowledge_base_path: Optional[str] = None) -> RunResult:
    cmd = [
        sys.executable, "-m", "skillweaver.attempt_task",
        url,
        task,
        "--max-steps", "8",
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
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
        
        elapsed = time.time() - start_time
        output = result.stdout + result.stderr
        
        return RunResult(
            success=result.returncode == 0,
            time_seconds=elapsed,
            steps_count=count_steps_from_output(output),
            api_calls=1,
            output=output,
        )
    
    except subprocess.TimeoutExpired:
        return RunResult(success=False, time_seconds=120, steps_count=0, api_calls=0, error="Timeout")
    except Exception as e:
        return RunResult(success=False, time_seconds=0, steps_count=0, api_calls=0, error=str(e))


def benchmark_website(website: dict) -> BenchmarkResult:
    print(f"\n{'#'*70}")
    print(f"  测试: {website['name']}")
    print(f"{'#'*70}")
    
    out_dir = os.path.join(EXPLORE_OUTPUT_DIR, website['name'].lower())
    
    # Explore
    explore_result = run_explore(website, out_dir)
    kb_path = find_knowledge_base(out_dir)
    kb_generated = kb_path is not None
    
    print(f"\n  探索完成: {explore_result['time']:.1f}s | KB: {'是' if kb_generated else '否'}")
    
    result = BenchmarkResult(
        website_name=website['name'],
        website_type=website['type'],
        explore_time=explore_result['time'],
        explore_success=explore_result['success'],
        kb_generated=kb_generated,
    )
    
    # Benchmark: 无知识库 (2 次)
    print(f"\n  [无KB测试]")
    for i in range(2):
        print(f"    运行 {i+1}/2...", end=" ", flush=True)
        run_result = run_attempt_task(website['url'], website['task'], None)
        result.without_kb_runs.append(run_result)
        print(f"{'OK' if run_result.success else 'FAIL'} ({run_result.time_seconds:.1f}s)")
    
    # Benchmark: 有知识库 (2 次)
    if kb_generated:
        print(f"\n  [有KB测试]")
        for i in range(2):
            print(f"    运行 {i+1}/2...", end=" ", flush=True)
            run_result = run_attempt_task(website['url'], website['task'], kb_path)
            result.with_kb_runs.append(run_result)
            print(f"{'OK' if run_result.success else 'FAIL'} ({run_result.time_seconds:.1f}s)")
    
    # 摘要
    print(f"\n  --- 结果 ---")
    print(f"  无KB: {result.avg_time_without_kb():.1f}s | {result.success_rate_without_kb()*100:.0f}%")
    if kb_generated:
        print(f"  有KB: {result.avg_time_with_kb():.1f}s | {result.success_rate_with_kb()*100:.0f}%")
        if result.speedup():
            print(f"  加速: {result.speedup():.2f}x")
    
    return result


def generate_report(results: List[BenchmarkResult]) -> Dict[str, Any]:
    speedups = [r.speedup() for r in results if r.speedup() is not None]
    avg_speedup = sum(speedups) / len(speedups) if speedups else None
    
    all_without_kb_success = [run.success for r in results for run in r.without_kb_runs]
    all_with_kb_success = [run.success for r in results for run in r.with_kb_runs]
    
    return {
        "meta": {
            "timestamp": datetime.now().isoformat(),
            "model": DEFAULT_MODEL,
            "total_websites": len(results),
        },
        "summary": {
            "avg_speedup": avg_speedup,
            "success_rate_without_kb": sum(all_without_kb_success) / len(all_without_kb_success) if all_without_kb_success else 0,
            "success_rate_with_kb": sum(all_with_kb_success) / len(all_with_kb_success) if all_with_kb_success else 0,
        },
        "per_website": {
            r.website_name: {
                "type": r.website_type,
                "explore_time": r.explore_time,
                "kb_generated": r.kb_generated,
                "without_kb_avg_time": r.avg_time_without_kb(),
                "with_kb_avg_time": r.avg_time_with_kb(),
                "speedup": r.speedup(),
            }
            for r in results
        }
    }


def main():
    print("=" * 70)
    print("  SkillWeaver 快速泛化测试 (3 网站)")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模型: {DEFAULT_MODEL}")
    print()
    
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(EXPLORE_OUTPUT_DIR, exist_ok=True)
    
    results: List[BenchmarkResult] = []
    
    for i, website in enumerate(TEST_WEBSITES):
        print(f"\n[{i+1}/{len(TEST_WEBSITES)}] {website['name']}")
        try:
            result = benchmark_website(website)
            results.append(result)
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 生成报告
    report = generate_report(results)
    
    json_path = os.path.join(RESULTS_DIR, "quick_benchmark.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 打印最终结果
    print("\n" + "=" * 70)
    print("  最终结果")
    print("=" * 70)
    
    print(f"\n| 网站 | 无KB时间 | 有KB时间 | 加速比 |")
    print(f"|------|----------|----------|--------|")
    for name, data in report['per_website'].items():
        without_t = f"{data['without_kb_avg_time']:.1f}s"
        with_t = f"{data['with_kb_avg_time']:.1f}s" if data['with_kb_avg_time'] > 0 else "N/A"
        speedup = f"{data['speedup']:.2f}x" if data['speedup'] else "N/A"
        print(f"| {name} | {without_t} | {with_t} | {speedup} |")
    
    if report['summary']['avg_speedup']:
        print(f"\n平均加速比: {report['summary']['avg_speedup']:.2f}x")
    
    print(f"\n报告已保存: {json_path}")
    print("\n测试完成!")


if __name__ == "__main__":
    main()
