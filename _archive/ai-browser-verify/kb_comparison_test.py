"""
知识库对比验证测试
比较有知识库和无知识库情况下执行任务的效率差异
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

# 知识库路径
KB_PREFIX = os.path.join(SCRIPT_DIR, "debug_explore_output", "iter_1", "kb_post")

# 输出目录
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "comparison_results")

# 测试任务
TEST_TASKS = [
    {
        "id": "task1_search",
        "task": "Search Hacker News for 'rust programming' using the footer search box",
        "related_skill": "hn_search_from_footer",
    },
    {
        "id": "task2_comments",
        "task": "Open the comments page for the 5th story on the Hacker News front page",
        "related_skill": "open_hn_comments_thread_by_rank",
    },
    {
        "id": "task3_combined",
        "task": "Search Hacker News for 'AI startup' and then navigate to view results",
        "related_skill": "hn_search_from_footer (combined)",
    },
]

# 模型配置
MODEL_NAME = "gpt-5.2"


async def run_attempt_task(task_info: dict, use_knowledge_base: bool, output_subdir: str):
    """运行单个任务测试"""
    import nest_asyncio
    nest_asyncio.apply()
    
    from playwright.async_api import async_playwright
    from skillweaver.environment import make_browser
    from skillweaver.attempt_task import attempt_task
    from skillweaver.knowledge_base.knowledge_base import KnowledgeBase, load_knowledge_base
    from skillweaver.lm import LM
    
    # 准备输出目录
    task_output_dir = os.path.join(OUTPUT_DIR, output_subdir, task_info["id"])
    if os.path.exists(task_output_dir):
        shutil.rmtree(task_output_dir)
    os.makedirs(task_output_dir, exist_ok=True)
    
    # 加载或创建知识库
    if use_knowledge_base:
        kb = load_knowledge_base(KB_PREFIX)
        kb.hide_unverified = False
        kb_status = "with_kb"
    else:
        kb = KnowledgeBase()
        kb_status = "no_kb"
    
    # 创建 LM
    lm = LM(MODEL_NAME)
    
    # 记录开始时间
    start_time = time.time()
    
    result = {
        "task_id": task_info["id"],
        "task_description": task_info["task"],
        "knowledge_base": kb_status,
        "model": MODEL_NAME,
        "start_time": datetime.now().isoformat(),
    }
    
    try:
        async with async_playwright() as p:
            browser = await make_browser(
                p,
                "https://news.ycombinator.com",
                headless=False,
            )
            
            task = {"type": "prod", "task": task_info["task"]}
            
            states, actions = await attempt_task(
                browser,
                lm,
                task,
                max_steps=10,
                knowledge_base=kb,
                store_dir=task_output_dir,
            )
            
            await browser.close()
            
            # 计算指标
            end_time = time.time()
            
            # 分析轨迹
            num_steps = len(actions)
            has_exception = any(
                a.get("result", {}).get("exception") is not None 
                for a in actions if a.get("result")
            )
            
            # 检查是否使用了知识库技能
            skills_used = []
            for a in actions:
                code = a.get("python_code", "")
                if "hn_search_from_footer" in code:
                    skills_used.append("hn_search_from_footer")
                if "open_hn_comments_thread_by_rank" in code:
                    skills_used.append("open_hn_comments_thread_by_rank")
            
            result.update({
                "success": not has_exception,
                "num_steps": num_steps,
                "execution_time_seconds": round(end_time - start_time, 2),
                "skills_used": list(set(skills_used)),
                "has_exception": has_exception,
            })
            
    except Exception as e:
        result.update({
            "success": False,
            "error": str(e),
            "execution_time_seconds": round(time.time() - start_time, 2),
        })
    
    # 保存结果
    with open(os.path.join(task_output_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result


def print_header(text: str):
    """打印标题"""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_comparison_table(no_kb_results: list, with_kb_results: list):
    """打印对比表格"""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + "知识库对比测试结果".center(70) + "║")
    print("╠" + "═" * 78 + "╣")
    print("║ {:30} │ {:10} │ {:10} │ {:10} │ {:10} ║".format(
        "任务", "无KB步骤", "有KB步骤", "提升", "技能使用"
    ))
    print("╠" + "─" * 78 + "╣")
    
    for no_kb, with_kb in zip(no_kb_results, with_kb_results):
        task_name = no_kb["task_id"][:28]
        no_kb_steps = no_kb.get("num_steps", "N/A")
        with_kb_steps = with_kb.get("num_steps", "N/A")
        
        if isinstance(no_kb_steps, int) and isinstance(with_kb_steps, int) and no_kb_steps > 0:
            improvement = f"{round((1 - with_kb_steps/no_kb_steps) * 100)}% ↓"
        else:
            improvement = "N/A"
        
        skills = ", ".join(with_kb.get("skills_used", [])) or "无"
        skills = skills[:8] + ".." if len(skills) > 10 else skills
        
        print("║ {:30} │ {:^10} │ {:^10} │ {:^10} │ {:10} ║".format(
            task_name, str(no_kb_steps), str(with_kb_steps), improvement, skills
        ))
    
    print("╚" + "═" * 78 + "╝")


async def main():
    """主函数"""
    print_header("SkillWeaver 知识库对比验证测试")
    print(f"模型: {MODEL_NAME}")
    print(f"知识库路径: {KB_PREFIX}")
    print(f"测试任务数: {len(TEST_TASKS)}")
    
    # 清理输出目录
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    no_kb_results = []
    with_kb_results = []
    
    # 运行无知识库测试
    print_header("阶段 1: 无知识库测试")
    for i, task in enumerate(TEST_TASKS):
        print(f"\n[{i+1}/{len(TEST_TASKS)}] 任务: {task['id']}")
        print(f"    描述: {task['task'][:50]}...")
        result = await run_attempt_task(task, use_knowledge_base=False, output_subdir="no_kb")
        no_kb_results.append(result)
        print(f"    结果: 步骤={result.get('num_steps', 'N/A')}, 成功={result.get('success', False)}")
    
    # 运行有知识库测试
    print_header("阶段 2: 有知识库测试")
    for i, task in enumerate(TEST_TASKS):
        print(f"\n[{i+1}/{len(TEST_TASKS)}] 任务: {task['id']}")
        print(f"    描述: {task['task'][:50]}...")
        result = await run_attempt_task(task, use_knowledge_base=True, output_subdir="with_kb")
        with_kb_results.append(result)
        print(f"    结果: 步骤={result.get('num_steps', 'N/A')}, 成功={result.get('success', False)}, 技能={result.get('skills_used', [])}")
    
    # 打印对比结果
    print_header("测试完成 - 对比结果")
    print_comparison_table(no_kb_results, with_kb_results)
    
    # 保存完整报告
    report = {
        "test_date": datetime.now().isoformat(),
        "model": MODEL_NAME,
        "knowledge_base_path": KB_PREFIX,
        "no_kb_results": no_kb_results,
        "with_kb_results": with_kb_results,
    }
    
    report_path = os.path.join(OUTPUT_DIR, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n完整报告已保存到: {report_path}")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())
