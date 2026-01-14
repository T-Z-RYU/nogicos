"""
Computer Use vs SkillWeaver 对比测试

核心问题：我们的方法真的比 Computer Use 更快吗？

测试逻辑：
- Computer Use 模式：每步都要 LLM 推理（无知识库）
- SkillWeaver 模式：有知识库，可以直接调用技能

关键指标：
- 执行时间
- LLM 调用次数
- 步骤数
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
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "computer_use_comparison_results")

# 模型配置
MODEL_NAME = "gpt-5.2"

# 测试任务 - 选择能体现知识库价值的任务
TEST_TASKS = [
    {
        "id": "search_task",
        "name": "搜索任务",
        "site_url": "https://news.ycombinator.com",
        "task": "Search for 'rust programming' using the search feature on this website",
        "expected_skill": "hn_search_from_footer",
    },
    {
        "id": "comments_task", 
        "name": "评论任务",
        "site_url": "https://news.ycombinator.com",
        "task": "Open the comments page for the 5th story on this page",
        "expected_skill": "open_hn_comments_thread_by_rank",
    },
]


def print_header(text: str):
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)


async def run_task(task: dict, use_knowledge_base: bool, mode_name: str):
    """运行单个任务"""
    import nest_asyncio
    nest_asyncio.apply()
    
    from playwright.async_api import async_playwright
    from skillweaver.environment import make_browser
    from skillweaver.attempt_task import attempt_task
    from skillweaver.knowledge_base.knowledge_base import KnowledgeBase, load_knowledge_base
    from skillweaver.lm import LM
    
    # 准备输出目录
    task_output_dir = os.path.join(OUTPUT_DIR, mode_name, task["id"])
    if os.path.exists(task_output_dir):
        shutil.rmtree(task_output_dir)
    os.makedirs(task_output_dir, exist_ok=True)
    
    # 加载或创建知识库
    if use_knowledge_base:
        kb = load_knowledge_base(KB_PREFIX)
        kb.hide_unverified = False
    else:
        kb = KnowledgeBase()  # 空知识库 = Computer Use 模式
    
    lm = LM(MODEL_NAME)
    
    # 记录详细时间
    start_time = time.time()
    llm_call_times = []
    
    result = {
        "task_id": task["id"],
        "task_name": task["name"],
        "mode": mode_name,
        "use_knowledge_base": use_knowledge_base,
    }
    
    try:
        async with async_playwright() as p:
            browser = await make_browser(p, task["site_url"], headless=False)
            
            task_obj = {"type": "prod", "task": task["task"]}
            
            # 记录每步的时间
            step_times = []
            step_start = time.time()
            
            states, actions = await attempt_task(
                browser,
                lm,
                task_obj,
                max_steps=10,
                knowledge_base=kb,
                store_dir=task_output_dir,
            )
            
            await browser.close()
            
            end_time = time.time()
            
            # 分析结果
            num_steps = len(actions)
            has_exception = any(
                a.get("result", {}).get("exception") is not None 
                for a in actions if a.get("result")
            )
            
            # 检查是否使用了知识库技能
            used_kb_skill = False
            for a in actions:
                code = a.get("python_code", "")
                if task["expected_skill"] in code:
                    used_kb_skill = True
                    break
            
            result.update({
                "success": not has_exception,
                "num_steps": num_steps,
                "total_time_seconds": round(end_time - start_time, 2),
                "used_kb_skill": used_kb_skill,
                "llm_calls": num_steps,  # 每步一次 LLM 调用
            })
            
    except Exception as e:
        result.update({
            "success": False,
            "error": str(e),
            "total_time_seconds": round(time.time() - start_time, 2),
        })
    
    # 保存结果
    with open(os.path.join(task_output_dir, "result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result


def print_comparison_table(computer_use_results: list, skillweaver_results: list):
    """打印对比表格"""
    print()
    print("┌" + "─" * 90 + "┐")
    print("│" + " Computer Use vs SkillWeaver 对比结果 ".center(82) + "│")
    print("├" + "─" * 90 + "┤")
    print(f"│ {'任务':<15} │ {'模式':<20} │ {'步骤':<6} │ {'时间(s)':<10} │ {'成功':<6} │ {'用KB技能':<10} │")
    print("├" + "─" * 90 + "┤")
    
    for cu, sw in zip(computer_use_results, skillweaver_results):
        # Computer Use 行
        task_name = cu.get("task_name", "")[:12]
        mode = "Computer Use"
        steps = str(cu.get("num_steps", "N/A"))
        time_s = str(cu.get("total_time_seconds", "N/A"))
        success = "✓" if cu.get("success") else "✗"
        kb_skill = "N/A"
        print(f"│ {task_name:<15} │ {mode:<20} │ {steps:<6} │ {time_s:<10} │ {success:<6} │ {kb_skill:<10} │")
        
        # SkillWeaver 行
        mode = "SkillWeaver (有KB)"
        steps = str(sw.get("num_steps", "N/A"))
        time_s = str(sw.get("total_time_seconds", "N/A"))
        success = "✓" if sw.get("success") else "✗"
        kb_skill = "✓" if sw.get("used_kb_skill") else "✗"
        print(f"│ {'└─':<15} │ {mode:<20} │ {steps:<6} │ {time_s:<10} │ {success:<6} │ {kb_skill:<10} │")
        
        # 计算提升
        cu_time = cu.get("total_time_seconds", 0)
        sw_time = sw.get("total_time_seconds", 0)
        if cu_time > 0 and sw_time > 0:
            speedup = round((cu_time - sw_time) / cu_time * 100, 1)
            cu_steps = cu.get("num_steps", 0)
            sw_steps = sw.get("num_steps", 0)
            step_reduction = round((cu_steps - sw_steps) / cu_steps * 100, 1) if cu_steps > 0 else 0
            print(f"│ {'   提升:':<15} │ {'时间: ' + str(speedup) + '%':<20} │ {'步骤: ' + str(step_reduction) + '%':<6} │ {'':<10} │ {'':<6} │ {'':<10} │")
        
        print("├" + "─" * 90 + "┤")
    
    print("└" + "─" * 90 + "┘")


def calculate_summary(computer_use_results: list, skillweaver_results: list) -> dict:
    """计算汇总数据"""
    cu_total_time = sum(r.get("total_time_seconds", 0) for r in computer_use_results)
    sw_total_time = sum(r.get("total_time_seconds", 0) for r in skillweaver_results)
    
    cu_total_steps = sum(r.get("num_steps", 0) for r in computer_use_results)
    sw_total_steps = sum(r.get("num_steps", 0) for r in skillweaver_results)
    
    cu_success = sum(1 for r in computer_use_results if r.get("success"))
    sw_success = sum(1 for r in skillweaver_results if r.get("success"))
    
    sw_kb_used = sum(1 for r in skillweaver_results if r.get("used_kb_skill"))
    
    return {
        "computer_use": {
            "total_time": cu_total_time,
            "total_steps": cu_total_steps,
            "success_count": cu_success,
            "avg_time_per_task": round(cu_total_time / len(computer_use_results), 2) if computer_use_results else 0,
        },
        "skillweaver": {
            "total_time": sw_total_time,
            "total_steps": sw_total_steps,
            "success_count": sw_success,
            "kb_skills_used": sw_kb_used,
            "avg_time_per_task": round(sw_total_time / len(skillweaver_results), 2) if skillweaver_results else 0,
        },
        "improvement": {
            "time_saved_percent": round((cu_total_time - sw_total_time) / cu_total_time * 100, 1) if cu_total_time > 0 else 0,
            "steps_saved_percent": round((cu_total_steps - sw_total_steps) / cu_total_steps * 100, 1) if cu_total_steps > 0 else 0,
            "time_saved_seconds": round(cu_total_time - sw_total_time, 2),
        }
    }


async def main():
    """主函数"""
    print_header("Computer Use vs SkillWeaver 对比测试")
    print(f"模型: {MODEL_NAME}")
    print(f"知识库路径: {KB_PREFIX}")
    print(f"测试任务数: {len(TEST_TASKS)}")
    
    print("\n测试逻辑:")
    print("  • Computer Use 模式 = 无知识库（每步都要 LLM 推理）")
    print("  • SkillWeaver 模式 = 有知识库（可以直接调用学过的技能）")
    
    # 清理输出目录
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    computer_use_results = []
    skillweaver_results = []
    
    # 运行 Computer Use 模式（无知识库）
    print_header("阶段 1: Computer Use 模式（无知识库）")
    for task in TEST_TASKS:
        print(f"\n任务: {task['name']}")
        print(f"  描述: {task['task'][:50]}...")
        result = await run_task(task, use_knowledge_base=False, mode_name="computer_use")
        computer_use_results.append(result)
        print(f"  结果: 步骤={result.get('num_steps', 'N/A')}, 时间={result.get('total_time_seconds', 'N/A')}s, 成功={result.get('success', False)}")
    
    # 运行 SkillWeaver 模式（有知识库）
    print_header("阶段 2: SkillWeaver 模式（有知识库）")
    for task in TEST_TASKS:
        print(f"\n任务: {task['name']}")
        print(f"  描述: {task['task'][:50]}...")
        result = await run_task(task, use_knowledge_base=True, mode_name="skillweaver")
        skillweaver_results.append(result)
        print(f"  结果: 步骤={result.get('num_steps', 'N/A')}, 时间={result.get('total_time_seconds', 'N/A')}s, 成功={result.get('success', False)}, 用KB={result.get('used_kb_skill', False)}")
    
    # 打印对比结果
    print_header("对比结果")
    print_comparison_table(computer_use_results, skillweaver_results)
    
    # 计算汇总
    summary = calculate_summary(computer_use_results, skillweaver_results)
    
    print_header("汇总")
    print(f"""
┌─────────────────────────────────────────────────────────────┐
│                       性能对比汇总                          │
├─────────────────────────────────────────────────────────────┤
│  Computer Use 模式:                                         │
│    • 总时间: {summary['computer_use']['total_time']:.2f} 秒
│    • 总步骤: {summary['computer_use']['total_steps']}
│    • 成功率: {summary['computer_use']['success_count']}/{len(TEST_TASKS)}
├─────────────────────────────────────────────────────────────┤
│  SkillWeaver 模式:                                          │
│    • 总时间: {summary['skillweaver']['total_time']:.2f} 秒
│    • 总步骤: {summary['skillweaver']['total_steps']}
│    • 成功率: {summary['skillweaver']['success_count']}/{len(TEST_TASKS)}
│    • 使用KB技能: {summary['skillweaver']['kb_skills_used']}/{len(TEST_TASKS)}
├─────────────────────────────────────────────────────────────┤
│  提升效果:                                                  │
│    • 时间节省: {summary['improvement']['time_saved_percent']}% ({summary['improvement']['time_saved_seconds']}秒)
│    • 步骤减少: {summary['improvement']['steps_saved_percent']}%
└─────────────────────────────────────────────────────────────┘
""")
    
    # 保存完整报告
    report = {
        "test_date": datetime.now().isoformat(),
        "model": MODEL_NAME,
        "knowledge_base_path": KB_PREFIX,
        "test_tasks": TEST_TASKS,
        "computer_use_results": computer_use_results,
        "skillweaver_results": skillweaver_results,
        "summary": summary,
    }
    
    report_path = os.path.join(OUTPUT_DIR, "comparison_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"完整报告已保存到: {report_path}")
    
    # 生成结论
    print_header("结论")
    if summary['improvement']['time_saved_percent'] > 20:
        print("✅ SkillWeaver 比 Computer Use 显著更快！")
        print(f"   时间节省 {summary['improvement']['time_saved_percent']}%，步骤减少 {summary['improvement']['steps_saved_percent']}%")
        print("   核心价值：学过的任务可以直接调用，跳过 LLM 推理")
    elif summary['improvement']['time_saved_percent'] > 0:
        print("⚠️ SkillWeaver 略快于 Computer Use")
        print(f"   时间节省 {summary['improvement']['time_saved_percent']}%")
        print("   可能需要更复杂的任务来体现优势")
    else:
        print("❓ 本次测试未能体现 SkillWeaver 的速度优势")
        print("   可能原因：任务太简单，或知识库未被有效使用")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())
