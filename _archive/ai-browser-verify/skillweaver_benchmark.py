"""
使用 SkillWeaver 验证核心假设：AI 学习后执行速度提升 10x+
"""
import asyncio
import sys
import os
import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加 SkillWeaver 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SkillWeaver"))

import nest_asyncio
nest_asyncio.apply()

from playwright.async_api import async_playwright

# 导入 API Keys
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 导入 SkillWeaver 组件
from skillweaver.lm import LM
from skillweaver.environment import make_browser
from skillweaver.agent import codegen_do, codegen_generate


@dataclass
class BenchmarkResult:
    """测试结果"""
    task_name: str
    url: str
    task: str
    
    # 无知识库结果
    without_kb_time: float = 0.0
    without_kb_steps: int = 0
    without_kb_llm_calls: int = 0
    without_kb_success: bool = False
    without_kb_output: str = ""
    
    # 有知识库结果
    with_kb_time: float = 0.0
    with_kb_steps: int = 0
    with_kb_llm_calls: int = 0
    with_kb_success: bool = False
    with_kb_output: str = ""
    
    # 速度提升
    speedup: float = 0.0
    
    def calculate_speedup(self):
        if self.with_kb_time > 0 and self.without_kb_time > 0:
            self.speedup = self.without_kb_time / self.with_kb_time
        return self.speedup


class SkillWeaverBenchmark:
    """使用 SkillWeaver 进行基准测试"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name
        self.lm = LM(model_name)
        self.results: List[BenchmarkResult] = []
        
        # 预定义的知识库（预学习的技能代码）
        self.knowledge_base = self._create_knowledge_base()
    
    def _create_knowledge_base(self) -> Dict[str, str]:
        """创建知识库（预定义的 Playwright 代码）"""
        return {
            "github_search": '''
async def act(page):
    """在 GitHub 上搜索仓库"""
    search_button = page.locator('button[data-target="qbsearch-input.inputButton"]')
    await search_button.click()
    await page.wait_for_timeout(500)
    search_input = page.locator('input[name="query-builder-test"]')
    await search_input.fill('{query}')
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('networkidle')
    return "搜索完成"
''',
            "google_search": '''
async def act(page):
    """在 Google 上搜索"""
    search_input = page.locator('textarea[name="q"]')
    await search_input.fill('{query}')
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('networkidle')
    return "搜索完成"
''',
            "hackernews_top": '''
async def act(page):
    """获取 HackerNews 头条"""
    title_element = page.locator('.titleline > a').first
    title = await title_element.text_content()
    return f"头条: {title}"
''',
            "wikipedia_search": '''
async def act(page):
    """在 Wikipedia 搜索"""
    search_input = page.locator('input[name="search"]')
    await search_input.fill('{query}')
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('networkidle')
    return "搜索完成"
''',
            "duckduckgo_search": '''
async def act(page):
    """在 DuckDuckGo 搜索"""
    search_input = page.locator('input[name="q"]')
    await search_input.fill('{query}')
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('networkidle')
    return "搜索完成"
''',
        }
    
    async def execute_without_knowledge_base(
        self, 
        url: str, 
        task: str,
        max_steps: int = 5
    ) -> Dict[str, Any]:
        """无知识库执行：让 AI 从头分析并执行（使用 SkillWeaver）"""
        result = {
            "success": False,
            "time": 0.0,
            "steps": 0,
            "llm_calls": 0,
            "output": None,
            "error": None,
        }
        
        start_time = time.time()
        
        async with async_playwright() as p:
            try:
                # 使用 SkillWeaver 的 make_browser
                browser = await make_browser(
                    p, 
                    url, 
                    headless=True,
                    navigation_timeout=30000,
                    timeout=10000
                )
                
                trajectory = []
                
                for step in range(max_steps):
                    # 获取当前状态（使用 browser.observe()）
                    state = await browser.observe()
                    
                    # 让 AI 生成下一步操作
                    result["llm_calls"] += 1
                    
                    action = await codegen_generate(
                        lm=self.lm,
                        state=state,
                        task=task,
                        trajectory=trajectory,
                        knowledge_base=None,  # 无知识库
                    )
                    
                    if action.get("terminate_with_result"):
                        result["output"] = action["terminate_with_result"]
                        result["success"] = True
                        break
                    
                    # 执行操作
                    exec_result = await codegen_do(
                        browser=browser,
                        action=action,
                        knowledge_base=None,
                    )
                    
                    trajectory.append(action)
                    result["steps"] += 1
                    
                    if exec_result.get("output"):
                        result["output"] = str(exec_result["output"])
                        result["success"] = True
                        break
                
                await browser.close()
                
            except Exception as e:
                result["error"] = str(e)
        
        result["time"] = time.time() - start_time
        return result
    
    async def execute_with_knowledge_base(
        self,
        url: str,
        task: str,
        skill_code: str,
        query: str = ""
    ) -> Dict[str, Any]:
        """有知识库执行：直接执行预定义的代码（跳过 AI 分析）"""
        result = {
            "success": False,
            "time": 0.0,
            "steps": 1,  # 预定义技能通常是一步
            "llm_calls": 0,  # 不需要 LLM 调用
            "output": None,
            "error": None,
        }
        
        start_time = time.time()
        
        # 替换查询参数
        code = skill_code.replace("{query}", query)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 访问页面
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state('domcontentloaded')
                await page.wait_for_timeout(1000)
                
                # 直接执行预定义代码
                local_vars = {"page": page}
                exec(code, {"__builtins__": __builtins__}, local_vars)
                
                if "act" in local_vars:
                    output = await local_vars["act"](page)
                    result["output"] = str(output)
                    result["success"] = True
                
            except Exception as e:
                result["error"] = str(e)
            finally:
                await browser.close()
        
        result["time"] = time.time() - start_time
        return result
    
    async def run_benchmark(self, task_name: str, url: str, task: str, 
                           skill_key: str, query: str = "") -> BenchmarkResult:
        """运行单个基准测试"""
        print(f"\n{'='*60}")
        print(f"测试: {task_name}")
        print(f"URL: {url}")
        print(f"任务: {task}")
        print(f"{'='*60}")
        
        result = BenchmarkResult(
            task_name=task_name,
            url=url,
            task=task,
        )
        
        # 1. 无知识库执行
        print("\n📍 无知识库执行 (AI 从头分析 - SkillWeaver)...")
        without_kb = await self.execute_without_knowledge_base(url, task)
        result.without_kb_time = without_kb["time"]
        result.without_kb_steps = without_kb["steps"]
        result.without_kb_llm_calls = without_kb["llm_calls"]
        result.without_kb_success = without_kb["success"]
        result.without_kb_output = str(without_kb.get("output", ""))[:100]
        print(f"   时间: {without_kb['time']:.2f}s")
        print(f"   步骤: {without_kb['steps']}")
        print(f"   LLM调用: {without_kb['llm_calls']}")
        print(f"   成功: {'✅' if without_kb['success'] else '❌'}")
        if without_kb.get("output"):
            print(f"   输出: {str(without_kb['output'])[:80]}...")
        if without_kb.get("error"):
            print(f"   错误: {without_kb['error'][:80]}")
        
        # 2. 有知识库执行
        print("\n📍 有知识库执行 (直接执行预学习技能)...")
        skill_code = self.knowledge_base.get(skill_key, "")
        if skill_code:
            with_kb = await self.execute_with_knowledge_base(url, task, skill_code, query)
            result.with_kb_time = with_kb["time"]
            result.with_kb_steps = with_kb["steps"]
            result.with_kb_llm_calls = with_kb["llm_calls"]
            result.with_kb_success = with_kb["success"]
            result.with_kb_output = str(with_kb.get("output", ""))[:100]
            print(f"   时间: {with_kb['time']:.2f}s")
            print(f"   步骤: {with_kb['steps']}")
            print(f"   LLM调用: {with_kb['llm_calls']}")
            print(f"   成功: {'✅' if with_kb['success'] else '❌'}")
            if with_kb.get("output"):
                print(f"   输出: {str(with_kb['output'])[:80]}...")
            if with_kb.get("error"):
                print(f"   错误: {with_kb['error'][:80]}")
        else:
            print("   ⚠️ 无对应知识库技能")
        
        # 3. 计算速度提升
        result.calculate_speedup()
        if result.speedup > 0:
            print(f"\n📊 速度提升: {result.speedup:.1f}x")
        
        self.results.append(result)
        return result
    
    async def run_all_benchmarks(self):
        """运行所有基准测试"""
        print("=" * 70)
        print("    SkillWeaver 核心假设验证")
        print("    假设: AI 学习后执行速度提升 10x+")
        print("=" * 70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"模型: {self.model_name}")
        
        # 定义测试任务（选择稳定可靠的网站）
        tasks = [
            {
                "name": "HackerNews 头条",
                "url": "https://news.ycombinator.com",
                "task": "获取当前排名第一的新闻标题",
                "skill_key": "hackernews_top",
                "query": "",
            },
            {
                "name": "Google 搜索",
                "url": "https://www.google.com",
                "task": "搜索 'SkillWeaver AI agent'",
                "skill_key": "google_search",
                "query": "SkillWeaver AI agent",
            },
            {
                "name": "Wikipedia 搜索",
                "url": "https://www.wikipedia.org",
                "task": "搜索 'Artificial Intelligence'",
                "skill_key": "wikipedia_search",
                "query": "Artificial Intelligence",
            },
            {
                "name": "DuckDuckGo 搜索",
                "url": "https://duckduckgo.com",
                "task": "搜索 'web automation'",
                "skill_key": "duckduckgo_search",
                "query": "web automation",
            },
            {
                "name": "GitHub 搜索",
                "url": "https://github.com",
                "task": "搜索 'ai browser' 相关的仓库",
                "skill_key": "github_search",
                "query": "ai browser",
            },
        ]
        
        for task in tasks:
            try:
                await self.run_benchmark(
                    task_name=task["name"],
                    url=task["url"],
                    task=task["task"],
                    skill_key=task["skill_key"],
                    query=task["query"],
                )
            except Exception as e:
                print(f"❌ 任务 {task['name']} 失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 70)
        print("    验证报告")
        print("=" * 70)
        
        # 统计
        total = len(self.results)
        success_without_kb = sum(1 for r in self.results if r.without_kb_success)
        success_with_kb = sum(1 for r in self.results if r.with_kb_success)
        
        valid_speedups = [r.speedup for r in self.results if r.speedup > 0]
        avg_speedup = sum(valid_speedups) / max(1, len(valid_speedups))
        
        speedup_10x_count = sum(1 for r in self.results if r.speedup >= 10)
        speedup_5x_count = sum(1 for r in self.results if r.speedup >= 5)
        
        print(f"\n总测试数: {total}")
        print(f"无知识库成功率: {success_without_kb}/{total}")
        print(f"有知识库成功率: {success_with_kb}/{total}")
        print(f"平均速度提升: {avg_speedup:.1f}x")
        print(f"达到 10x+ 提升: {speedup_10x_count}/{total}")
        print(f"达到 5x+ 提升: {speedup_5x_count}/{total}")
        
        print("\n详细结果:")
        print("-" * 70)
        print(f"{'任务':<20} {'无KB(s)':<10} {'有KB(s)':<10} {'LLM调用':<8} {'提升':<10}")
        print("-" * 70)
        
        for r in self.results:
            speedup_str = f"{r.speedup:.1f}x" if r.speedup > 0 else "N/A"
            print(f"{r.task_name:<20} {r.without_kb_time:<10.2f} {r.with_kb_time:<10.2f} {r.without_kb_llm_calls:<8} {speedup_str}")
        
        print("-" * 70)
        
        # 核心假设验证结论
        print("\n🎯 核心假设验证结论:")
        if speedup_10x_count >= 3:
            print("   ✅ 假设验证通过! 至少 3 个任务达到 10x+ 速度提升")
        elif speedup_5x_count >= 3:
            print("   ⚠️ 部分验证通过，至少 3 个任务达到 5x+ 速度提升")
        else:
            print("   ❌ 假设未验证，需要优化")
        
        # 保存结果
        report = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "summary": {
                "total_tasks": total,
                "success_without_kb": success_without_kb,
                "success_with_kb": success_with_kb,
                "avg_speedup": avg_speedup,
                "tasks_with_10x_speedup": speedup_10x_count,
                "tasks_with_5x_speedup": speedup_5x_count,
            },
            "results": [asdict(r) for r in self.results],
        }
        
        os.makedirs("results", exist_ok=True)
        with open("results/skillweaver_benchmark_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存到: results/skillweaver_benchmark_report.json")


async def main():
    benchmark = SkillWeaverBenchmark(model_name="gpt-4o")
    await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())
