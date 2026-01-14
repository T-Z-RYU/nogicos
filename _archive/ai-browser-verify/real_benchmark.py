"""
真正的 SkillWeaver 基准测试 - 验证核心假设
对比：无知识库 vs 有知识库 的执行速度
"""
import asyncio
import sys
import os
import time
import json
import subprocess
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

# 导入 API Keys
from api_keys import OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


@dataclass
class BenchmarkResult:
    task_name: str
    url: str
    task: str
    
    without_kb_time: float = 0.0
    without_kb_llm_calls: int = 0
    without_kb_success: bool = False
    without_kb_output: str = ""
    
    with_kb_time: float = 0.0
    with_kb_llm_calls: int = 0
    with_kb_success: bool = False
    with_kb_output: str = ""
    
    speedup: float = 0.0
    
    def calculate_speedup(self):
        if self.with_kb_time > 0 and self.without_kb_time > 0:
            self.speedup = self.without_kb_time / self.with_kb_time


# 预学习的技能代码（模拟 SkillWeaver 知识库中已学习的技能）
SKILL_CODES = {
    "hackernews_top": '''
async def act(page):
    title = await page.locator('.titleline > a').first.text_content()
    return f"Top: {title}"
''',
    "duckduckgo_search": '''
async def act(page, query):
    await page.locator('input[name="q"]').fill(query)
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('networkidle', timeout=10000)
    return "Search completed"
''',
    "wikipedia_search": '''
async def act(page, query):
    search_input = page.locator('#searchInput')
    await search_input.fill(query)
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('domcontentloaded', timeout=15000)
    title = await page.title()
    return f"Searched: {title}"
''',
}


def run_skillweaver_without_kb(url: str, task: str, max_steps: int = 3) -> Dict[str, Any]:
    """使用子进程运行 SkillWeaver（避免异步冲突）"""
    cmd = [
        sys.executable, 
        "skillweaver_worker.py",
        "--url", url,
        "--task", task,
        "--max-steps", str(max_steps),
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "OPENAI_API_KEY": OPENAI_API_KEY, "PYTHONIOENCODING": "utf-8"},
            encoding="utf-8",
            errors="replace",
        )
        
        # 解析 JSON 结果
        output = result.stdout
        if "JSON_RESULT_START" in output:
            json_str = output.split("JSON_RESULT_START")[1].split("JSON_RESULT_END")[0].strip()
            return json.loads(json_str)
        
        return {
            "success": False,
            "time": 0,
            "llm_calls": 0,
            "output": None,
            "error": result.stderr[:500] if result.stderr else "No JSON result",
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "time": 120, "llm_calls": 0, "output": None, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "time": 0, "llm_calls": 0, "output": None, "error": str(e)}


async def run_with_knowledge_base(url: str, task: str, skill_key: str, query: str = "") -> Dict[str, Any]:
    """使用预学习技能执行（模拟知识库）"""
    result = {
        "success": False,
        "time": 0.0,
        "llm_calls": 0,  # 不需要 LLM
        "output": None,
        "error": None,
    }
    
    start_time = time.time()
    skill_code = SKILL_CODES.get(skill_key, "")
    
    if not skill_code:
        result["error"] = "No skill found"
        result["time"] = time.time() - start_time
        return result
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_timeout(500)
            
            # 直接执行预学习的代码
            local_vars = {"page": page, "query": query}
            exec(skill_code, {"__builtins__": __builtins__}, local_vars)
            
            if "act" in local_vars:
                import inspect
                sig = inspect.signature(local_vars["act"])
                if len(sig.parameters) == 1:
                    output = await local_vars["act"](page)
                else:
                    output = await local_vars["act"](page, query)
                result["output"] = str(output)
                result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        finally:
            await browser.close()
    
    result["time"] = time.time() - start_time
    return result


async def run_benchmark(task_name: str, url: str, task: str, skill_key: str, query: str = "") -> BenchmarkResult:
    """运行单个基准测试"""
    print(f"\n{'='*60}")
    print(f"测试: {task_name}")
    print(f"URL: {url}")
    print(f"任务: {task}")
    print(f"{'='*60}")
    
    result = BenchmarkResult(task_name=task_name, url=url, task=task)
    
    # 1. 无知识库执行（真正的 SkillWeaver）
    print("\n📍 无知识库执行 (SkillWeaver AI 从头分析)...")
    without_kb = run_skillweaver_without_kb(url, task)
    result.without_kb_time = without_kb.get("time", 0)
    result.without_kb_llm_calls = without_kb.get("llm_calls", 0)
    result.without_kb_success = without_kb.get("success", False)
    result.without_kb_output = str(without_kb.get("output", ""))[:80]
    
    print(f"   时间: {result.without_kb_time:.2f}s")
    print(f"   LLM调用: {result.without_kb_llm_calls}")
    print(f"   成功: {'✅' if result.without_kb_success else '❌'}")
    if result.without_kb_output:
        print(f"   输出: {result.without_kb_output[:50]}...")
    if without_kb.get("error"):
        print(f"   错误: {without_kb['error'][:50]}")
    
    # 2. 有知识库执行（直接执行预学习技能）
    print("\n📍 有知识库执行 (直接执行预学习技能)...")
    with_kb = await run_with_knowledge_base(url, task, skill_key, query)
    result.with_kb_time = with_kb.get("time", 0)
    result.with_kb_llm_calls = with_kb.get("llm_calls", 0)
    result.with_kb_success = with_kb.get("success", False)
    result.with_kb_output = str(with_kb.get("output", ""))[:80]
    
    print(f"   时间: {result.with_kb_time:.2f}s")
    print(f"   LLM调用: {result.with_kb_llm_calls}")
    print(f"   成功: {'✅' if result.with_kb_success else '❌'}")
    if result.with_kb_output:
        print(f"   输出: {result.with_kb_output[:50]}...")
    if with_kb.get("error"):
        print(f"   错误: {with_kb['error'][:50]}")
    
    # 计算速度提升
    result.calculate_speedup()
    if result.speedup > 0:
        print(f"\n📊 速度提升: {result.speedup:.1f}x")
    
    return result


async def main():
    print("=" * 70)
    print("    SkillWeaver 核心假设验证")
    print("    假设: AI 学习后执行速度提升 10x+")
    print("=" * 70)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("对比:")
    print("  - 无知识库: 使用 SkillWeaver，AI 从头理解页面并生成代码")
    print("  - 有知识库: 直接执行预学习的 Playwright 代码（0 次 LLM 调用）")
    
    tasks = [
        {
            "name": "HackerNews 头条",
            "url": "https://news.ycombinator.com",
            "task": "获取当前排名第一的新闻标题",
            "skill_key": "hackernews_top",
            "query": "",
        },
        {
            "name": "DuckDuckGo 搜索",
            "url": "https://duckduckgo.com",
            "task": "搜索 'web automation'",
            "skill_key": "duckduckgo_search",
            "query": "web automation",
        },
    ]
    
    results = []
    for task in tasks:
        try:
            result = await run_benchmark(
                task_name=task["name"],
                url=task["url"],
                task=task["task"],
                skill_key=task["skill_key"],
                query=task["query"],
            )
            results.append(result)
        except Exception as e:
            print(f"❌ 任务 {task['name']} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 生成报告
    print("\n" + "=" * 70)
    print("    验证报告")
    print("=" * 70)
    
    total = len(results)
    if total == 0:
        print("❌ 没有测试结果")
        return
    
    success_without = sum(1 for r in results if r.without_kb_success)
    success_with = sum(1 for r in results if r.with_kb_success)
    
    valid_speedups = [r.speedup for r in results if r.speedup > 0]
    avg_speedup = sum(valid_speedups) / max(1, len(valid_speedups))
    
    avg_without_time = sum(r.without_kb_time for r in results) / total
    avg_with_time = sum(r.with_kb_time for r in results) / total
    
    total_llm_calls = sum(r.without_kb_llm_calls for r in results)
    
    print(f"\n总测试数: {total}")
    print(f"无知识库成功率: {success_without}/{total}")
    print(f"有知识库成功率: {success_with}/{total}")
    print(f"平均无知识库时间: {avg_without_time:.2f}s")
    print(f"平均有知识库时间: {avg_with_time:.2f}s")
    print(f"总 LLM 调用次数: {total_llm_calls}")
    print(f"平均速度提升: {avg_speedup:.1f}x")
    
    print("\n详细结果:")
    print("-" * 70)
    print(f"{'任务':<20} {'无KB(s)':<10} {'有KB(s)':<10} {'LLM调用':<8} {'提升':<10}")
    print("-" * 70)
    
    for r in results:
        speedup_str = f"{r.speedup:.1f}x" if r.speedup > 0 else "N/A"
        print(f"{r.task_name:<20} {r.without_kb_time:<10.2f} {r.with_kb_time:<10.2f} {r.without_kb_llm_calls:<8} {speedup_str}")
    
    print("-" * 70)
    
    print("\n🎯 核心假设验证结论:")
    if avg_speedup >= 10:
        print("   ✅ 假设验证通过! 平均速度提升达到 10x+")
    elif avg_speedup >= 5:
        print(f"   ✅ 部分验证通过，平均速度提升 {avg_speedup:.1f}x")
    elif avg_speedup >= 2:
        print(f"   📊 速度提升 {avg_speedup:.1f}x，符合预期")
    else:
        print("   ❌ 需要进一步验证")
    
    print(f"\n📌 关键发现:")
    print(f"   - 无知识库需要 ~{avg_without_time:.1f}s (包含 LLM 推理时间)")
    print(f"   - 有知识库只需要 ~{avg_with_time:.1f}s (直接执行)")
    print(f"   - 节省时间: ~{avg_without_time - avg_with_time:.1f}s/任务")
    
    # 保存报告
    os.makedirs("results", exist_ok=True)
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "success_without_kb": success_without,
            "success_with_kb": success_with,
            "avg_speedup": avg_speedup,
            "avg_without_kb_time": avg_without_time,
            "avg_with_kb_time": avg_with_time,
            "total_llm_calls": total_llm_calls,
        },
        "results": [asdict(r) for r in results],
    }
    
    with open("results/real_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n报告已保存到: results/real_benchmark.json")


if __name__ == "__main__":
    asyncio.run(main())
