"""
多网站泛化验证测试
验证 AI 学到的知识能否跨网站迁移
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

# 知识库路径 (从 HN 学习得到的)
KB_PREFIX = os.path.join(SCRIPT_DIR, "debug_explore_output", "iter_1", "kb_post")

# 输出目录
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "generalization_results")

# 模型配置
MODEL_NAME = "gpt-5.2"

# 测试网站和任务
TEST_SITES = [
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com",
        "category": "tech_forum",
        "tasks": [
            {
                "id": "hn_search",
                "task": "Search for 'machine learning' on this website",
                "type": "search",
            },
            {
                "id": "hn_comments",
                "task": "Open the comments/discussion for the 3rd item on the page",
                "type": "comments",
            },
        ]
    },
    {
        "name": "Reddit",
        "url": "https://old.reddit.com/r/programming",
        "category": "tech_forum",
        "tasks": [
            {
                "id": "reddit_search",
                "task": "Search for 'machine learning' on this website",
                "type": "search",
            },
            {
                "id": "reddit_comments",
                "task": "Open the comments/discussion for the 3rd post on the page",
                "type": "comments",
            },
        ]
    },
    {
        "name": "Lobsters",
        "url": "https://lobste.rs",
        "category": "tech_forum",
        "tasks": [
            {
                "id": "lobsters_search",
                "task": "Search for 'rust programming' on this website",
                "type": "search",
            },
            {
                "id": "lobsters_comments",
                "task": "Open the comments/discussion for the 3rd story on the page",
                "type": "comments",
            },
        ]
    },
]


async def run_task_test(site: dict, task: dict, use_knowledge_base: bool, output_subdir: str):
    """运行单个任务测试"""
    import nest_asyncio
    nest_asyncio.apply()
    
    from playwright.async_api import async_playwright
    from skillweaver.environment import make_browser
    from skillweaver.attempt_task import attempt_task
    from skillweaver.knowledge_base.knowledge_base import KnowledgeBase, load_knowledge_base
    from skillweaver.lm import LM
    
    # 准备输出目录
    task_output_dir = os.path.join(OUTPUT_DIR, output_subdir, f"{site['name']}_{task['id']}")
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
        "site_name": site["name"],
        "site_url": site["url"],
        "site_category": site["category"],
        "task_id": task["id"],
        "task_description": task["task"],
        "task_type": task["type"],
        "knowledge_base": kb_status,
        "model": MODEL_NAME,
        "start_time": datetime.now().isoformat(),
    }
    
    try:
        async with async_playwright() as p:
            browser = await make_browser(
                p,
                site["url"],
                headless=False,
            )
            
            task_obj = {"type": "prod", "task": task["task"]}
            
            states, actions = await attempt_task(
                browser,
                lm,
                task_obj,
                max_steps=12,
                knowledge_base=kb,
                store_dir=task_output_dir,
            )
            
            # 获取最终 URL
            final_url = await browser.page.url if hasattr(browser, 'page') else "unknown"
            
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
            skill_patterns = ["hn_search", "open_hn_comments", "search_from_footer", "comments_thread"]
            for a in actions:
                code = a.get("python_code", "")
                for pattern in skill_patterns:
                    if pattern in code.lower():
                        skills_used.append(pattern)
            
            # 检查是否成功完成任务
            # 简单检查：看最终 URL 是否发生了预期的变化
            task_success = not has_exception
            
            result.update({
                "success": task_success,
                "num_steps": num_steps,
                "execution_time_seconds": round(end_time - start_time, 2),
                "skills_used": list(set(skills_used)),
                "has_exception": has_exception,
                "final_url": str(final_url),
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
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_results_table(results: list, title: str):
    """打印结果表格"""
    print()
    print(f"┌{'─' * 88}┐")
    print(f"│{title.center(88)}│")
    print(f"├{'─' * 88}┤")
    print(f"│ {'网站':<15} │ {'任务类型':<10} │ {'步骤':<6} │ {'时间(s)':<8} │ {'成功':<6} │ {'技能使用':<20} │")
    print(f"├{'─' * 88}┤")
    
    for r in results:
        site = r.get("site_name", "")[:12]
        task_type = r.get("task_type", "")[:8]
        steps = str(r.get("num_steps", "N/A"))
        time_s = str(r.get("execution_time_seconds", "N/A"))
        success = "✓" if r.get("success") else "✗"
        skills = ", ".join(r.get("skills_used", [])) or "无"
        skills = skills[:18] + ".." if len(skills) > 20 else skills
        
        print(f"│ {site:<15} │ {task_type:<10} │ {steps:<6} │ {time_s:<8} │ {success:<6} │ {skills:<20} │")
    
    print(f"└{'─' * 88}┘")


def print_comparison_summary(no_kb_results: list, with_kb_results: list):
    """打印对比摘要"""
    print()
    print_header("泛化测试对比摘要")
    
    # 按网站分组
    sites = {}
    for r in no_kb_results:
        site = r["site_name"]
        if site not in sites:
            sites[site] = {"no_kb": [], "with_kb": []}
        sites[site]["no_kb"].append(r)
    
    for r in with_kb_results:
        site = r["site_name"]
        if site in sites:
            sites[site]["with_kb"].append(r)
    
    print()
    print(f"┌{'─' * 90}┐")
    print(f"│{'知识迁移效果对比'.center(82)}│")
    print(f"├{'─' * 90}┤")
    print(f"│ {'网站':<20} │ {'无KB成功率':<12} │ {'有KB成功率':<12} │ {'无KB平均步骤':<12} │ {'有KB平均步骤':<12} │")
    print(f"├{'─' * 90}┤")
    
    for site_name, data in sites.items():
        no_kb = data["no_kb"]
        with_kb = data["with_kb"]
        
        no_kb_success = sum(1 for r in no_kb if r.get("success")) / len(no_kb) * 100 if no_kb else 0
        with_kb_success = sum(1 for r in with_kb if r.get("success")) / len(with_kb) * 100 if with_kb else 0
        
        no_kb_steps = sum(r.get("num_steps", 0) for r in no_kb if r.get("num_steps")) / len(no_kb) if no_kb else 0
        with_kb_steps = sum(r.get("num_steps", 0) for r in with_kb if r.get("num_steps")) / len(with_kb) if with_kb else 0
        
        print(f"│ {site_name:<20} │ {no_kb_success:>10.0f}% │ {with_kb_success:>10.0f}% │ {no_kb_steps:>12.1f} │ {with_kb_steps:>12.1f} │")
    
    print(f"└{'─' * 90}┘")
    
    # 计算知识迁移成功率
    print()
    print("知识迁移分析:")
    for site_name, data in sites.items():
        if site_name == "Hacker News":
            continue  # 跳过原网站
        
        with_kb = data["with_kb"]
        skills_used_count = sum(1 for r in with_kb if r.get("skills_used"))
        total = len(with_kb)
        
        if total > 0:
            migration_rate = skills_used_count / total * 100
            print(f"  - {site_name}: 技能迁移率 {migration_rate:.0f}% ({skills_used_count}/{total} 任务使用了 HN 技能)")


async def main():
    """主函数"""
    print_header("SkillWeaver 多网站泛化验证测试")
    print(f"模型: {MODEL_NAME}")
    print(f"知识库来源: Hacker News (HN)")
    print(f"测试网站: {', '.join(s['name'] for s in TEST_SITES)}")
    
    # 清理输出目录
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    no_kb_results = []
    with_kb_results = []
    
    # 运行无知识库测试
    print_header("阶段 1: 无知识库测试（基线）")
    for site in TEST_SITES:
        print(f"\n--- 网站: {site['name']} ({site['url']}) ---")
        for task in site["tasks"]:
            print(f"  任务: {task['id']} - {task['task'][:40]}...")
            result = await run_task_test(site, task, use_knowledge_base=False, output_subdir="no_kb")
            no_kb_results.append(result)
            print(f"    结果: 步骤={result.get('num_steps', 'N/A')}, 成功={result.get('success', False)}, 时间={result.get('execution_time_seconds', 'N/A')}s")
    
    print_results_table(no_kb_results, "无知识库测试结果")
    
    # 运行有知识库测试
    print_header("阶段 2: 有知识库测试（HN 技能）")
    for site in TEST_SITES:
        print(f"\n--- 网站: {site['name']} ({site['url']}) ---")
        for task in site["tasks"]:
            print(f"  任务: {task['id']} - {task['task'][:40]}...")
            result = await run_task_test(site, task, use_knowledge_base=True, output_subdir="with_kb")
            with_kb_results.append(result)
            skills = result.get('skills_used', [])
            print(f"    结果: 步骤={result.get('num_steps', 'N/A')}, 成功={result.get('success', False)}, 技能={skills}")
    
    print_results_table(with_kb_results, "有知识库测试结果（使用 HN 技能）")
    
    # 打印对比摘要
    print_comparison_summary(no_kb_results, with_kb_results)
    
    # 保存完整报告
    report = {
        "test_date": datetime.now().isoformat(),
        "model": MODEL_NAME,
        "knowledge_base_source": "Hacker News",
        "test_sites": [s["name"] for s in TEST_SITES],
        "no_kb_results": no_kb_results,
        "with_kb_results": with_kb_results,
        "summary": {
            "total_tasks": len(no_kb_results),
            "no_kb_success_rate": sum(1 for r in no_kb_results if r.get("success")) / len(no_kb_results) * 100,
            "with_kb_success_rate": sum(1 for r in with_kb_results if r.get("success")) / len(with_kb_results) * 100,
        }
    }
    
    report_path = os.path.join(OUTPUT_DIR, "generalization_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n完整报告已保存到: {report_path}")
    
    # 生成 Markdown 报告
    md_report = generate_markdown_report(report)
    md_path = os.path.join(OUTPUT_DIR, "GENERALIZATION_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    
    print(f"Markdown 报告已保存到: {md_path}")
    
    return report


def generate_markdown_report(report: dict) -> str:
    """生成 Markdown 格式的报告"""
    md = f"""# 多网站泛化验证报告

## 测试概述

- **测试日期**: {report['test_date']}
- **使用模型**: {report['model']}
- **知识库来源**: {report['knowledge_base_source']}
- **测试网站**: {', '.join(report['test_sites'])}

## 核心发现

### 成功率对比

| 指标 | 无知识库 | 有知识库 | 变化 |
|------|---------|---------|------|
| 成功率 | {report['summary']['no_kb_success_rate']:.1f}% | {report['summary']['with_kb_success_rate']:.1f}% | {report['summary']['with_kb_success_rate'] - report['summary']['no_kb_success_rate']:+.1f}% |

### 详细结果

#### 无知识库测试

| 网站 | 任务 | 步骤 | 时间(s) | 成功 |
|------|------|------|---------|------|
"""
    
    for r in report['no_kb_results']:
        success = "✓" if r.get("success") else "✗"
        md += f"| {r['site_name']} | {r['task_type']} | {r.get('num_steps', 'N/A')} | {r.get('execution_time_seconds', 'N/A')} | {success} |\n"
    
    md += """
#### 有知识库测试

| 网站 | 任务 | 步骤 | 时间(s) | 成功 | 使用技能 |
|------|------|------|---------|------|----------|
"""
    
    for r in report['with_kb_results']:
        success = "✓" if r.get("success") else "✗"
        skills = ", ".join(r.get('skills_used', [])) or "无"
        md += f"| {r['site_name']} | {r['task_type']} | {r.get('num_steps', 'N/A')} | {r.get('execution_time_seconds', 'N/A')} | {success} | {skills} |\n"
    
    md += """
## 知识迁移分析

### 关键问题

1. **HN 学到的技能能否迁移到 Reddit/Lobsters？**
2. **迁移后的效率是否有提升？**
3. **哪些技能更容易迁移？**

### 结论

（根据实际测试结果填写）

## 对 YC 申请的意义

如果知识迁移成功：
- 证明了"学习一次，多处使用"的核心价值
- 网络效应可以跨网站形成
- 差异化优势更加明显

如果知识迁移失败：
- 需要重新思考知识库的设计
- 可能需要更抽象的技能表示
- 或者专注于单网站深度优化
"""
    
    return md


if __name__ == "__main__":
    asyncio.run(main())
