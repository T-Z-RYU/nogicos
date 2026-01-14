"""
知识库对比测试

策略：增加 explore 迭代次数，提高任务成功率，从而生成知识库
然后对比有/无知识库的执行效率
"""
import subprocess
import sys
import os
import time
import json
import shutil
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLWEAVER_PATH = os.path.join(SCRIPT_DIR, "SkillWeaver")
PYRIGHT_PATH = r"C:\Users\WIN\AppData\Local\Python\pythoncore-3.14-64\Scripts"
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "kb_comparison_output")
MODEL = "gpt-5.2"


def get_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = SKILLWEAVER_PATH + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = PYRIGHT_PATH + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_explore(domain: str, out_dir: str, iterations: int):
    """运行 explore"""
    print(f"\n{'='*60}")
    print(f"  EXPLORE: {domain}")
    print(f"  迭代次数: {iterations} (更多迭代 = 更高成功率)")
    print(f"{'='*60}")
    
    if os.path.exists(out_dir):
        try:
            shutil.rmtree(out_dir)
        except:
            pass
    os.makedirs(out_dir, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "skillweaver.explore",
        domain, out_dir,
        "--iterations", str(iterations),
        "--agent-lm-name", MODEL,
        "--api-synthesis-lm-name", MODEL,
        "--success-check-lm-name", MODEL,
    ]
    
    start = time.time()
    try:
        process = subprocess.Popen(
            cmd, cwd=SKILLWEAVER_PATH, env=get_env(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1
        )
        
        for line in process.stdout:
            # 只打印关键信息
            if any(k in line for k in ["Iteration:", "Task proposal:", "success", "Error", "kb_"]):
                print(f"  {line.rstrip()}")
        
        process.wait()
        elapsed = time.time() - start
        return {"success": process.returncode == 0, "time": elapsed}
    except Exception as e:
        return {"success": False, "time": time.time() - start, "error": str(e)}


def find_kb_with_content(out_dir: str):
    """查找有实际内容的知识库"""
    if not os.path.exists(out_dir):
        return None
    
    # 检查所有迭代，找到有内容的知识库
    for item in sorted(os.listdir(out_dir), reverse=True):
        path = os.path.join(out_dir, item)
        if os.path.isdir(path) and item.startswith("iter_"):
            kb_file = os.path.join(path, "kb_post_code.py")
            if os.path.exists(kb_file):
                with open(kb_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().strip()
                    if content and len(content) > 100:  # 有实际代码
                        print(f"  找到知识库: {kb_file}")
                        print(f"  内容长度: {len(content)} 字符")
                        return path
            
            # 检查成功率
            success_file = os.path.join(path, "success_check.json")
            if os.path.exists(success_file):
                with open(success_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("success"):
                        print(f"  迭代 {item} 成功!")
    
    return None


def run_task(url: str, task: str, kb_path=None, timeout=90):
    """运行任务"""
    label = "有KB" if kb_path else "无KB"
    print(f"  {label}...", end=" ", flush=True)
    
    cmd = [
        sys.executable, "-m", "skillweaver.attempt_task",
        url, task,
        "--max-steps", "8",
        "--headless",
        "--agent-lm-name", MODEL,
    ]
    if kb_path:
        cmd.extend(["--knowledge-base-path-prefix", kb_path])
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd, cwd=SKILLWEAVER_PATH, env=get_env(),
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace"
        )
        elapsed = time.time() - start
        success = result.returncode == 0
        
        # 提取步骤数
        import re
        steps = re.findall(r'Step (\d+)', result.stdout)
        step_count = max(int(s) for s in steps) + 1 if steps else 0
        
        print(f"{'OK' if success else 'FAIL'} ({elapsed:.1f}s, {step_count} 步)")
        return {"success": success, "time": elapsed, "steps": step_count}
    except subprocess.TimeoutExpired:
        print(f"超时 ({timeout}s)")
        return {"success": False, "time": timeout, "steps": 0}
    except Exception as e:
        print(f"错误")
        return {"success": False, "time": 0, "steps": 0}


def main():
    print("=" * 70)
    print("  SkillWeaver 知识库对比测试")
    print("  目标: 量化证明有知识库 vs 无知识库的效果差异")
    print("=" * 70)
    print(f"时间: {datetime.now()}")
    print(f"模型: {MODEL}")
    
    # 测试配置 - 使用简单的搜索引擎任务
    domain = "duckduckgo.com"
    url = "https://duckduckgo.com"
    task = "搜索 'Python programming' 并点击第一个结果"
    
    # Phase 1: Explore (增加迭代次数)
    print("\n[Phase 1] 探索阶段")
    explore_result = run_explore(domain, OUTPUT_DIR, iterations=5)
    print(f"\n探索完成: {explore_result['time']:.1f}s")
    
    # 查找知识库
    kb_path = find_kb_with_content(OUTPUT_DIR)
    if not kb_path:
        print("\n⚠️ 知识库未生成（探索任务可能都没成功）")
        print("  这是正常的 - 不是所有探索都会成功")
    
    # Phase 2: 对比测试
    print("\n[Phase 2] 对比测试")
    
    # 无知识库测试
    print("\n无知识库执行 (3次):")
    results_without = []
    for i in range(3):
        r = run_task(url, task, None, timeout=90)
        results_without.append(r)
    
    # 有知识库测试
    results_with = []
    if kb_path:
        print("\n有知识库执行 (3次):")
        for i in range(3):
            r = run_task(url, task, kb_path, timeout=90)
            results_with.append(r)
    
    # 结果统计
    print("\n" + "=" * 70)
    print("  测试结果")
    print("=" * 70)
    
    def calc_stats(results):
        times = [r["time"] for r in results if r["success"]]
        steps = [r["steps"] for r in results if r["success"]]
        success_rate = sum(1 for r in results if r["success"]) / len(results) if results else 0
        return {
            "avg_time": sum(times) / len(times) if times else 0,
            "avg_steps": sum(steps) / len(steps) if steps else 0,
            "success_rate": success_rate,
        }
    
    stats_without = calc_stats(results_without)
    
    print(f"\n| 指标 | 无知识库 | 有知识库 |")
    print(f"|------|----------|----------|")
    print(f"| 平均时间 | {stats_without['avg_time']:.1f}s | ", end="")
    
    if results_with:
        stats_with = calc_stats(results_with)
        print(f"{stats_with['avg_time']:.1f}s |")
        print(f"| 平均步骤 | {stats_without['avg_steps']:.1f} | {stats_with['avg_steps']:.1f} |")
        print(f"| 成功率 | {stats_without['success_rate']*100:.0f}% | {stats_with['success_rate']*100:.0f}% |")
        
        if stats_with['avg_time'] > 0 and stats_without['avg_time'] > 0:
            speedup = stats_without['avg_time'] / stats_with['avg_time']
            print(f"\n📊 加速比: {speedup:.2f}x")
    else:
        print("N/A |")
        print(f"| 平均步骤 | {stats_without['avg_steps']:.1f} | N/A |")
        print(f"| 成功率 | {stats_without['success_rate']*100:.0f}% | N/A |")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "website": domain,
        "task": task,
        "explore_time": explore_result["time"],
        "kb_generated": kb_path is not None,
        "without_kb": stats_without,
        "with_kb": calc_stats(results_with) if results_with else None,
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/kb_comparison.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n报告: results/kb_comparison.json")
    print("\n测试完成!")


if __name__ == "__main__":
    main()
