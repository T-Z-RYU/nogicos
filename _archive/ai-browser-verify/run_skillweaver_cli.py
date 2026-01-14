"""
使用 SkillWeaver 官方命令行方式运行测试
"""
import subprocess
import sys
import os
import time
import json
from datetime import datetime

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 设置环境变量
from api_keys import OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

SKILLWEAVER_PATH = os.path.join(os.path.dirname(__file__), "SkillWeaver")


def run_skillweaver_task(url: str, task: str, knowledge_base_path: str = None, max_steps: int = 5):
    """使用子进程运行 SkillWeaver attempt_task"""
    
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
    
    print(f"运行命令: {' '.join(cmd)}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SKILLWEAVER_PATH,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,  # 2分钟超时
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
        return {
            "success": False,
            "time": 120,
            "stdout": "",
            "stderr": "Timeout",
            "returncode": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "time": time.time() - start_time,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
        }


def main():
    print("=" * 70)
    print("    SkillWeaver CLI 测试")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"SkillWeaver 路径: {SKILLWEAVER_PATH}")
    
    # 测试 1: 无知识库 - HackerNews
    print("\n" + "=" * 60)
    print("测试 1: HackerNews 头条 (无知识库)")
    print("=" * 60)
    
    result1 = run_skillweaver_task(
        url="https://news.ycombinator.com",
        task="获取当前排名第一的新闻标题",
        knowledge_base_path=None,
        max_steps=3,
    )
    
    print(f"\n结果:")
    print(f"  成功: {'✅' if result1['success'] else '❌'}")
    print(f"  时间: {result1['time']:.2f}s")
    print(f"  返回码: {result1['returncode']}")
    
    if result1['stdout']:
        print(f"\n  输出 (前500字符):")
        print("  " + result1['stdout'][:500].replace('\n', '\n  '))
    
    if result1['stderr']:
        print(f"\n  错误 (前500字符):")
        print("  " + result1['stderr'][:500].replace('\n', '\n  '))
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
