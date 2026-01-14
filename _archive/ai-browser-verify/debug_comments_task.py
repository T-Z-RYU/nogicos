"""
调试评论任务的循环问题
"""
import asyncio
import os
import sys
import shutil

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 设置 API keys
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# 设置路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLWEAVER_PATH = os.path.join(SCRIPT_DIR, "SkillWeaver")
sys.path.insert(0, SKILLWEAVER_PATH)

PYRIGHT_PATH = r"C:\Users\WIN\AppData\Local\Python\pythoncore-3.14-64\Scripts"
os.environ["PATH"] = PYRIGHT_PATH + os.pathsep + os.environ.get("PATH", "")

# 知识库路径
KB_PREFIX = os.path.join(SCRIPT_DIR, "debug_explore_output", "iter_1", "kb_post")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "debug_comments_output")

MODEL_NAME = "gpt-5.2"


async def main():
    import nest_asyncio
    nest_asyncio.apply()
    
    from playwright.async_api import async_playwright
    from skillweaver.environment import make_browser
    from skillweaver.attempt_task import attempt_task
    from skillweaver.knowledge_base.knowledge_base import load_knowledge_base
    from skillweaver.lm import LM
    
    # 清理输出目录
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 加载知识库
    kb = load_knowledge_base(KB_PREFIX)
    kb.hide_unverified = False
    
    lm = LM(MODEL_NAME)
    
    task = {
        "type": "prod",
        "task": "Open the comments page for the 5th story on this page"
    }
    
    print("=" * 60)
    print("调试评论任务 - 使用知识库")
    print("=" * 60)
    print(f"模型: {MODEL_NAME}")
    print(f"任务: {task['task']}")
    print(f"知识库: {KB_PREFIX}")
    print()
    
    async with async_playwright() as p:
        browser = await make_browser(p, "https://news.ycombinator.com", headless=False)
        
        states, actions = await attempt_task(
            browser,
            lm,
            task,
            max_steps=5,  # 限制步骤数以便调试
            knowledge_base=kb,
            store_dir=OUTPUT_DIR,
        )
        
        await browser.close()
    
    print()
    print("=" * 60)
    print("结果")
    print("=" * 60)
    print(f"总步骤数: {len(actions)}")
    for i, action in enumerate(actions):
        print(f"\n步骤 {i}:")
        print(f"  代码: {action.get('python_code', '')[:100]}...")
        print(f"  terminate_with_result: {action.get('terminate_with_result', '')}")
        if action.get('result'):
            print(f"  result: {action['result'].get('exception', 'None')}")


if __name__ == "__main__":
    asyncio.run(main())
