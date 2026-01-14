"""
单网站快速验证测试
测试 SkillWeaver explore + attempt_task 完整流程
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

# API Keys
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLWEAVER_PATH = os.path.join(SCRIPT_DIR, "SkillWeaver")
PYRIGHT_PATH = r"C:\Users\WIN\AppData\Local\Python\pythoncore-3.14-64\Scripts"
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_single_output")

MODEL = "gpt-5.2"


def get_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = SKILLWEAVER_PATH + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = PYRIGHT_PATH + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_explore(domain: str, out_dir: str, iterations: int = 2):
    """运行 explore，超时 5 分钟"""
    print(f"\n[1/3] EXPLORE: {domain}")
    print(f"  迭代: {iterations}")
    
    # 清理目录
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
        result = subprocess.run(
            cmd, cwd=SKILLWEAVER_PATH, env=get_env(),
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace"
        )
        elapsed = time.time() - start
        print(f"  完成: {elapsed:.1f}s | 返回码: {result.returncode}")
        return {"success": result.returncode == 0, "time": elapsed, "output": result.stdout}
    except subprocess.TimeoutExpired:
        print(f"  超时 (300s)")
        return {"success": False, "time": 300, "output": "Timeout"}
    except Exception as e:
        print(f"  错误: {e}")
        return {"success": False, "time": 0, "output": str(e)}


def find_kb(out_dir: str):
    """查找知识库"""
    if not os.path.exists(out_dir):
        return None
    for item in sorted(os.listdir(out_dir), reverse=True):
        path = os.path.join(out_dir, item)
        if os.path.isdir(path) and item.startswith("iter_"):
            kb_file = os.path.join(path, "kb_post_code.py")
            if os.path.exists(kb_file):
                with open(kb_file, "r", encoding="utf-8", errors="replace") as f:
                    if len(f.read().strip()) > 50:
                        return path
    return None


def run_task(url: str, task: str, kb_path=None, timeout=60):
    """运行 attempt_task"""
    label = "有KB" if kb_path else "无KB"
    print(f"  {label}...", end=" ", flush=True)
    
    cmd = [
        sys.executable, "-m", "skillweaver.attempt_task",
        url, task,
        "--max-steps", "5",
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
        print(f"{'OK' if success else 'FAIL'} ({elapsed:.1f}s)")
        return {"success": success, "time": elapsed}
    except subprocess.TimeoutExpired:
        print(f"超时 ({timeout}s)")
        return {"success": False, "time": timeout}
    except Exception as e:
        print(f"错误: {e}")
        return {"success": False, "time": 0}


def main():
    print("=" * 60)
    print("  单网站验证测试")
    print("=" * 60)
    print(f"时间: {datetime.now()}")
    print(f"模型: {MODEL}")
    
    # 测试配置
    domain = "news.ycombinator.com"
    url = "https://news.ycombinator.com"
    task = "获取排名第一的新闻标题"
    
    # Phase 1: Explore
    explore_result = run_explore(domain, OUTPUT_DIR, iterations=2)
    
    # 查找知识库
    kb_path = find_kb(OUTPUT_DIR)
    print(f"\n  知识库: {'找到 ' + kb_path if kb_path else '未生成'}")
    
    # Phase 2: 无知识库测试
    print(f"\n[2/3] 无知识库测试")
    results_without = []
    for i in range(2):
        r = run_task(url, task, None, timeout=60)
        results_without.append(r)
    
    # Phase 3: 有知识库测试（如果存在）
    results_with = []
    if kb_path:
        print(f"\n[3/3] 有知识库测试")
        for i in range(2):
            r = run_task(url, task, kb_path, timeout=60)
            results_with.append(r)
    
    # 结果
    print("\n" + "=" * 60)
    print("  结果")
    print("=" * 60)
    
    avg_without = sum(r["time"] for r in results_without) / len(results_without)
    success_without = sum(1 for r in results_without if r["success"]) / len(results_without)
    
    print(f"探索时间: {explore_result['time']:.1f}s")
    print(f"无KB平均: {avg_without:.1f}s | 成功率: {success_without*100:.0f}%")
    
    if results_with:
        avg_with = sum(r["time"] for r in results_with) / len(results_with)
        success_with = sum(1 for r in results_with if r["success"]) / len(results_with)
        print(f"有KB平均: {avg_with:.1f}s | 成功率: {success_with*100:.0f}%")
        if avg_with > 0:
            speedup = avg_without / avg_with
            print(f"加速比: {speedup:.2f}x")
    
    # 保存结果
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "explore_time": explore_result["time"],
        "kb_generated": kb_path is not None,
        "without_kb": {"avg_time": avg_without, "success_rate": success_without},
        "with_kb": {"avg_time": avg_with, "success_rate": success_with} if results_with else None,
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/single_site_test.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n报告: results/single_site_test.json")
    print("\n完成!")


if __name__ == "__main__":
    main()
