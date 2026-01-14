"""
调试 SkillWeaver explore 流程
只运行 2 次迭代来快速获取日志
"""
import subprocess
import sys
import os
import shutil

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLWEAVER_PATH = os.path.join(SCRIPT_DIR, "SkillWeaver")
PYRIGHT_PATH = r"C:\Users\WIN\AppData\Local\Python\pythoncore-3.14-64\Scripts"
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "debug_explore_output")

def get_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = SKILLWEAVER_PATH + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = PYRIGHT_PATH + os.pathsep + env.get("PATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return env

def main():
    print("=" * 60)
    print("  调试 SkillWeaver Explore")
    print("=" * 60)
    
    # 清理旧目录
    if os.path.exists(OUTPUT_DIR):
        try:
            shutil.rmtree(OUTPUT_DIR)
        except:
            pass
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 运行 explore - 只 2 次迭代
    cmd = [
        sys.executable, "-m", "skillweaver.explore",
        "news.ycombinator.com",
        OUTPUT_DIR,
        "--iterations", "2",
        "--agent-lm-name", "gpt-5.2",
        "--api-synthesis-lm-name", "gpt-5.2",
        "--success-check-lm-name", "gpt-5.2",
    ]
    
    print(f"运行命令: {' '.join(cmd[:5])}...")
    print()
    
    process = subprocess.Popen(
        cmd, cwd=SKILLWEAVER_PATH, env=get_env(),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", bufsize=1
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    print(f"\n完成! 返回码: {process.returncode}")
    print(f"\n请查看调试日志: .cursor/debug.log")

if __name__ == "__main__":
    main()
