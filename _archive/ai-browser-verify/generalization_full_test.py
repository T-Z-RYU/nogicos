"""
完整泛化验证测试
1. 在 Lobsters 上学习技能
2. 测试技能迁移到 HN/Reddit
3. 对比分析
"""
import asyncio
import json
import os
import shutil
import sys
import time
from datetime import datetime

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

# 模型配置
MODEL_NAME = "gpt-5.2"

# 输出目录
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "generalization_full_results")


def print_header(text: str):
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)


async def run_explore_on_site(site_url: str, site_name: str, num_iterations: int = 2):
    """在指定网站上运行 explore 学习技能"""
    import nest_asyncio
    nest_asyncio.apply()
    
    from playwright.async_api import async_playwright
    from skillweaver.environment import make_browser
    from skillweaver.explore import explore
    from skillweaver.knowledge_base.knowledge_base import KnowledgeBase
    from skillweaver.lm import LM
    
    output_dir = os.path.join(OUTPUT_DIR, f"{site_name}_explore")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    kb = KnowledgeBase()
    lm = LM(MODEL_NAME)
    
    print(f"\n开始在 {site_name} 上学习技能...")
    print(f"迭代次数: {num_iterations}")
    
    try:
        async with async_playwright() as p:
            browser = await make_browser(p, site_url, headless=False)
            
            await explore(
                browser,
                lm,
                knowledge_base=kb,
                num_iterations=num_iterations,
                store_dir=output_dir,
            )
            
            await browser.close()
        
        # 保存知识库
        kb_path = os.path.join(output_dir, f"iter_{num_iterations-1}", "kb_post")
        print(f"\n知识库保存到: {kb_path}")
        
        return kb_path
        
    except Exception as e:
        print(f"Explore 失败: {e}")
        return None


async def run_task_with_kb(site_url: str, site_name: str, task: str, kb_path: str):
    """使用指定知识库执行任务"""
    import nest_asyncio
    nest_asyncio.apply()
    
    from playwright.async_api import async_playwright
    from skillweaver.environment import make_browser
    from skillweaver.attempt_task import attempt_task
    from skillweaver.knowledge_base.knowledge_base import load_knowledge_base
    from skillweaver.lm import LM
    
    output_dir = os.path.join(OUTPUT_DIR, "migration_tests", f"{site_name}_{int(time.time())}")
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载知识库
    kb = load_knowledge_base(kb_path)
    kb.hide_unverified = False
    lm = LM(MODEL_NAME)
    
    start_time = time.time()
    result = {
        "site": site_name,
        "site_url": site_url,
        "task": task,
        "kb_source": kb_path,
    }
    
    try:
        async with async_playwright() as p:
            browser = await make_browser(p, site_url, headless=False)
            
            task_obj = {"type": "prod", "task": task}
            
            states, actions = await attempt_task(
                browser,
                lm,
                task_obj,
                max_steps=8,
                knowledge_base=kb,
                store_dir=output_dir,
            )
            
            await browser.close()
            
            # 分析结果
            num_steps = len(actions)
            has_exception = any(
                a.get("result", {}).get("exception") is not None 
                for a in actions if a.get("result")
            )
            
            # 检查是否使用了知识库技能
            skills_used = []
            for a in actions:
                code = a.get("python_code", "")
                if "search" in code.lower() and "async def" not in code:
                    skills_used.append("search_skill")
                if "comment" in code.lower() and "async def" not in code:
                    skills_used.append("comments_skill")
            
            result.update({
                "success": not has_exception,
                "num_steps": num_steps,
                "time_seconds": round(time.time() - start_time, 2),
                "skills_used": list(set(skills_used)),
            })
            
    except Exception as e:
        result.update({
            "success": False,
            "error": str(e),
            "time_seconds": round(time.time() - start_time, 2),
        })
    
    return result


async def quick_generalization_test():
    """快速泛化测试 - 使用已有的 HN 知识库测试"""
    print_header("快速泛化测试")
    
    # 使用已有的 HN 知识库
    hn_kb_path = os.path.join(SCRIPT_DIR, "debug_explore_output", "iter_1", "kb_post")
    
    if not os.path.exists(hn_kb_path + "_code.py"):
        print(f"找不到 HN 知识库: {hn_kb_path}")
        return None
    
    print(f"使用 HN 知识库: {hn_kb_path}")
    
    # 测试任务
    test_cases = [
        {
            "site": "Hacker News",
            "url": "https://news.ycombinator.com",
            "task": "Search for 'python' using the search feature",
        },
        {
            "site": "Reddit",
            "url": "https://old.reddit.com/r/programming",
            "task": "Search for 'python' using the search feature",
        },
        {
            "site": "Lobsters",
            "url": "https://lobste.rs",
            "task": "Search for 'python' using the search feature",
        },
    ]
    
    results = []
    
    for tc in test_cases:
        print(f"\n--- 测试: {tc['site']} ---")
        print(f"任务: {tc['task']}")
        
        result = await run_task_with_kb(
            tc["url"],
            tc["site"],
            tc["task"],
            hn_kb_path
        )
        
        results.append(result)
        print(f"结果: 步骤={result.get('num_steps', 'N/A')}, 成功={result.get('success', False)}")
    
    return results


async def main():
    """主函数"""
    print_header("SkillWeaver 泛化能力完整测试")
    print(f"模型: {MODEL_NAME}")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 清理输出目录
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 运行快速泛化测试
    results = await quick_generalization_test()
    
    if results:
        # 生成报告
        print_header("测试结果摘要")
        
        print("\n┌" + "─" * 70 + "┐")
        print("│" + "泛化测试结果".center(62) + "│")
        print("├" + "─" * 70 + "┤")
        print(f"│ {'网站':<20} │ {'步骤':<8} │ {'成功':<8} │ {'时间(s)':<10} │")
        print("├" + "─" * 70 + "┤")
        
        for r in results:
            site = r.get("site", "")[:18]
            steps = str(r.get("num_steps", "N/A"))
            success = "✓" if r.get("success") else "✗"
            time_s = str(r.get("time_seconds", "N/A"))
            print(f"│ {site:<20} │ {steps:<8} │ {success:<8} │ {time_s:<10} │")
        
        print("└" + "─" * 70 + "┘")
        
        # 保存结果
        report = {
            "test_date": datetime.now().isoformat(),
            "model": MODEL_NAME,
            "results": results,
        }
        
        report_path = os.path.join(OUTPUT_DIR, "generalization_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n报告已保存到: {report_path}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
