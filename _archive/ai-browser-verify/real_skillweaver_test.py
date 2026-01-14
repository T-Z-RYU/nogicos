"""
真正的 SkillWeaver 完整验证流程

流程：
1. 先运行 explore - 让 AI 探索网站并学习技能
2. 使用学习到的知识库执行任务
3. 对比有无知识库的执行时间
"""
import subprocess
import sys
import os
import time
import json
import shutil
from datetime import datetime

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 设置环境变量 - 最新模型 API Keys
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 2025年12月最新模型配置
LATEST_MODELS = {
    "openai": "gpt-5.2",
    "anthropic": "claude-opus-4-5-20251101",
    "google": "gemini-3-flash-preview",
}

# 默认使用 GPT-5.2
DEFAULT_MODEL = LATEST_MODELS["openai"]

SKILLWEAVER_PATH = os.path.join(os.path.dirname(__file__), "SkillWeaver")
PYRIGHT_PATH = r"C:\Users\WIN\AppData\Local\Python\pythoncore-3.14-64\Scripts"


def run_explore(website: str, out_dir: str, iterations: int = 3):
    """
    运行 SkillWeaver explore - 让 AI 自动探索网站并学习技能
    """
    print(f"\n{'='*60}")
    print(f"🔍 开始探索网站: {website}")
    print(f"📁 输出目录: {out_dir}")
    print(f"🔄 迭代次数: {iterations}")
    print(f"{'='*60}\n")
    
    # 清理旧目录
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    
    # 使用 2025年12月最新模型 GPT-5.2
    cmd = [
        sys.executable, "-m", "skillweaver.explore",
        website,
        out_dir,
        "--iterations", str(iterations),
        "--agent-lm-name", DEFAULT_MODEL,
        "--api-synthesis-lm-name", DEFAULT_MODEL,
        "--success-check-lm-name", DEFAULT_MODEL,
        "--explore-schedule", "test_probability:0.3",
    ]
    
    env = os.environ.copy()
    env["PYTHONPATH"] = SKILLWEAVER_PATH + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = PYRIGHT_PATH + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    
    print(f"运行命令: {' '.join(cmd)}\n")
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=SKILLWEAVER_PATH,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        
        output_lines = []
        for line in process.stdout:
            print(line, end='')
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


def find_knowledge_base(out_dir: str) -> str:
    """查找生成的知识库路径"""
    if not os.path.exists(out_dir):
        return None
        
    for item in sorted(os.listdir(out_dir), reverse=True):
        item_path = os.path.join(out_dir, item)
        if os.path.isdir(item_path) and item.startswith("iter_"):
            kb_code = os.path.join(item_path, "kb_code.py")
            kb_metadata = os.path.join(item_path, "kb_metadata.json")
            if os.path.exists(kb_code) or os.path.exists(kb_metadata):
                return os.path.join(item_path, "kb")
    return None


def run_attempt_task(url: str, task: str, knowledge_base_path: str = None, max_steps: int = 5):
    """运行 SkillWeaver attempt_task"""
    cmd = [
        sys.executable, "-m", "skillweaver.attempt_task",
        url,
        task,
        "--max-steps", str(max_steps),
        "--headless",
    ]
    
    if knowledge_base_path:
        cmd.extend(["--knowledge-base-path-prefix", knowledge_base_path])
    
    env = os.environ.copy()
    env["PYTHONPATH"] = SKILLWEAVER_PATH + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = PYRIGHT_PATH + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SKILLWEAVER_PATH,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace",
        )
        
        elapsed = time.time() - start_time
        
        return {
            "success": result.returncode == 0,
            "time": elapsed,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "time": 120, "stdout": "", "stderr": "Timeout", "returncode": -1}
    except Exception as e:
        return {"success": False, "time": 0, "stdout": "", "stderr": str(e), "returncode": -1}


def main():
    print("=" * 70)
    print("    SkillWeaver 完整验证流程")
    print("    Explore → Learn → Execute")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    website = "news.ycombinator.com"
    task = "获取当前排名第一的新闻标题"
    out_dir = os.path.join(os.path.dirname(__file__), "explore_output", "hackernews")
    
    # 阶段 1: 探索
    print("\n" + "=" * 70)
    print("    阶段 1: 探索 (Explore) - AI 自动学习网站")
    print("=" * 70)
    
    explore_result = run_explore(website=website, out_dir=out_dir, iterations=3)
    
    print(f"\n探索完成! 耗时: {explore_result['time']:.2f}s")
    
    kb_path = find_knowledge_base(out_dir)
    if kb_path:
        print(f"✅ 知识库已生成: {kb_path}")
    else:
        print("⚠️ 未找到知识库")
    
    # 阶段 2: 对比测试
    print("\n" + "=" * 70)
    print("    阶段 2: 对比测试")
    print("=" * 70)
    
    url = f"https://{website}"
    
    print(f"\n📍 测试 1: 无知识库")
    result_without = run_attempt_task(url, task, None, 5)
    print(f"   时间: {result_without['time']:.2f}s | 成功: {'✅' if result_without['success'] else '❌'}")
    
    result_with = None
    if kb_path:
        print(f"\n📍 测试 2: 有知识库")
        result_with = run_attempt_task(url, task, kb_path, 5)
        print(f"   时间: {result_with['time']:.2f}s | 成功: {'✅' if result_with['success'] else '❌'}")
        
        if result_with['time'] > 0 and result_without['time'] > 0:
            speedup = result_without['time'] / result_with['time']
            print(f"\n📊 速度提升: {speedup:.1f}x")
    
    # 保存报告
    os.makedirs("results", exist_ok=True)
    report = {
        "timestamp": datetime.now().isoformat(),
        "website": website,
        "explore_time": explore_result['time'],
        "without_kb_time": result_without['time'],
        "with_kb_time": result_with['time'] if result_with else None,
        "speedup": (result_without['time'] / result_with['time']) if result_with and result_with['time'] > 0 else None,
    }
    
    with open("results/real_skillweaver_test.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n报告已保存: results/real_skillweaver_test.json")


if __name__ == "__main__":
    main()
