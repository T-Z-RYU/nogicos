"""
最终基准测试 - 验证核心假设：AI 学习后执行速度提升 10x+

核心对比：
- 无知识库：AI 需要理解页面 + 生成代码 + 多次 LLM 调用
- 有知识库：直接执行预学习的技能代码（0 次 LLM 调用）
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
import openai

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


class FinalBenchmark:
    """最终基准测试"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.results: List[BenchmarkResult] = []
        
        # 预学习的技能（模拟 SkillWeaver 知识库）
        self.skill_codes = {
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
    # Wikipedia 首页搜索框使用 id="searchInput"
    search_input = page.locator('#searchInput')
    await search_input.fill(query)
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('domcontentloaded', timeout=15000)
    title = await page.title()
    return f"Searched: {title}"
''',
            "google_search": '''
async def act(page, query):
    await page.locator('textarea[name="q"]').fill(query)
    await page.keyboard.press('Enter')
    await page.wait_for_load_state('networkidle', timeout=10000)
    return "Search completed"
''',
        }
    
    async def execute_without_knowledge_base(self, url: str, task: str) -> Dict[str, Any]:
        """无知识库执行：AI 从头分析页面并生成代码"""
        result = {
            "success": False,
            "time": 0.0,
            "llm_calls": 0,
            "output": None,
            "error": None,
        }
        
        start_time = time.time()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state('domcontentloaded')
                await page.wait_for_timeout(1000)
                
                # 获取页面信息 (模拟 SkillWeaver 的 observe)
                title = await page.title()
                
                # 获取可点击元素 (简化版)
                elements = await page.evaluate('''() => {
                    const items = [];
                    const selectors = ['a', 'button', 'input', 'textarea'];
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach((el, i) => {
                            if (i < 10) {
                                items.push({
                                    tag: el.tagName,
                                    text: el.textContent?.substring(0, 50) || '',
                                    type: el.getAttribute('type') || '',
                                    name: el.getAttribute('name') || '',
                                    placeholder: el.getAttribute('placeholder') || '',
                                });
                            }
                        });
                    });
                    return items.slice(0, 30);
                }''')
                
                # 调用 LLM 生成代码
                result["llm_calls"] += 1
                
                prompt = f"""你是一个 Web 自动化助手。

当前页面信息:
- URL: {url}
- 标题: {title}
- 可用元素: {json.dumps(elements[:15], ensure_ascii=False)}

任务: {task}

请生成 Playwright Python 代码来完成这个任务。
只输出代码，不要解释。
代码应该是一个异步函数 `async def act(page):` 并返回结果。"""

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0,
                )
                
                generated_code = response.choices[0].message.content
                
                # 清理代码
                if "```python" in generated_code:
                    generated_code = generated_code.split("```python")[1].split("```")[0]
                elif "```" in generated_code:
                    generated_code = generated_code.split("```")[1].split("```")[0]
                
                print(f"   生成代码: {generated_code[:100]}...")
                
                # 执行生成的代码
                local_vars = {"page": page}
                exec(generated_code, {"__builtins__": __builtins__}, local_vars)
                
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
    
    async def execute_with_knowledge_base(
        self, url: str, task: str, skill_key: str, query: str = ""
    ) -> Dict[str, Any]:
        """有知识库执行：直接执行预学习的代码"""
        result = {
            "success": False,
            "time": 0.0,
            "llm_calls": 0,  # 不需要 LLM
            "output": None,
            "error": None,
        }
        
        start_time = time.time()
        skill_code = self.skill_codes.get(skill_key, "")
        
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
    
    async def run_benchmark(self, task_name: str, url: str, task: str,
                           skill_key: str, query: str = "") -> BenchmarkResult:
        print(f"\n{'='*60}")
        print(f"测试: {task_name}")
        print(f"URL: {url}")
        print(f"任务: {task}")
        print(f"{'='*60}")
        
        result = BenchmarkResult(task_name=task_name, url=url, task=task)
        
        # 1. 无知识库执行
        print("\n📍 无知识库执行 (AI 从头分析并生成代码)...")
        try:
            without_kb = await self.execute_without_knowledge_base(url, task)
            result.without_kb_time = without_kb["time"]
            result.without_kb_llm_calls = without_kb["llm_calls"]
            result.without_kb_success = without_kb["success"]
            result.without_kb_output = str(without_kb.get("output", ""))[:80]
        except Exception as e:
            result.without_kb_output = f"Error: {str(e)[:60]}"
        
        print(f"   时间: {result.without_kb_time:.2f}s")
        print(f"   LLM调用: {result.without_kb_llm_calls}")
        print(f"   成功: {'✅' if result.without_kb_success else '❌'}")
        if result.without_kb_output:
            print(f"   输出: {result.without_kb_output[:50]}...")
        
        # 2. 有知识库执行
        print("\n📍 有知识库执行 (直接执行预学习技能)...")
        try:
            with_kb = await self.execute_with_knowledge_base(url, task, skill_key, query)
            result.with_kb_time = with_kb["time"]
            result.with_kb_llm_calls = with_kb["llm_calls"]
            result.with_kb_success = with_kb["success"]
            result.with_kb_output = str(with_kb.get("output", ""))[:80]
        except Exception as e:
            result.with_kb_output = f"Error: {str(e)[:60]}"
        
        print(f"   时间: {result.with_kb_time:.2f}s")
        print(f"   LLM调用: {result.with_kb_llm_calls}")
        print(f"   成功: {'✅' if result.with_kb_success else '❌'}")
        if result.with_kb_output:
            print(f"   输出: {result.with_kb_output[:50]}...")
        
        # 计算速度提升
        result.calculate_speedup()
        if result.speedup > 0:
            print(f"\n📊 速度提升: {result.speedup:.1f}x")
        
        self.results.append(result)
        return result
    
    async def run_all_benchmarks(self):
        print("=" * 70)
        print("    核心假设验证: AI 学习后执行速度提升 10x+")
        print("=" * 70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"模型: {self.model_name}")
        
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
            {
                "name": "Wikipedia 搜索",
                "url": "https://www.wikipedia.org",
                "task": "搜索 'Artificial Intelligence'",
                "skill_key": "wikipedia_search",
                "query": "Artificial Intelligence",
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
        
        self.generate_report()
    
    def generate_report(self):
        print("\n" + "=" * 70)
        print("    验证报告")
        print("=" * 70)
        
        total = len(self.results)
        if total == 0:
            print("❌ 没有测试结果")
            return
        
        success_without = sum(1 for r in self.results if r.without_kb_success)
        success_with = sum(1 for r in self.results if r.with_kb_success)
        
        valid_speedups = [r.speedup for r in self.results if r.speedup > 0]
        avg_speedup = sum(valid_speedups) / max(1, len(valid_speedups))
        
        avg_without_time = sum(r.without_kb_time for r in self.results) / total
        avg_with_time = sum(r.with_kb_time for r in self.results) / total
        
        print(f"\n总测试数: {total}")
        print(f"无知识库成功率: {success_without}/{total}")
        print(f"有知识库成功率: {success_with}/{total}")
        print(f"平均无知识库时间: {avg_without_time:.2f}s")
        print(f"平均有知识库时间: {avg_with_time:.2f}s")
        print(f"平均速度提升: {avg_speedup:.1f}x")
        
        print("\n详细结果:")
        print("-" * 70)
        print(f"{'任务':<20} {'无KB(s)':<10} {'有KB(s)':<10} {'LLM调用':<8} {'提升':<10}")
        print("-" * 70)
        
        for r in self.results:
            speedup_str = f"{r.speedup:.1f}x" if r.speedup > 0 else "N/A"
            print(f"{r.task_name:<20} {r.without_kb_time:<10.2f} {r.with_kb_time:<10.2f} {r.without_kb_llm_calls:<8} {speedup_str}")
        
        print("-" * 70)
        
        print("\n🎯 核心假设验证结论:")
        if avg_speedup >= 10:
            print("   ✅ 假设验证通过! 平均速度提升达到 10x+")
            print(f"   📌 关键发现: 预学习技能节省了 LLM 调用时间约 {avg_without_time - avg_with_time:.1f}s")
        elif avg_speedup >= 5:
            print(f"   ⚠️ 部分验证，平均速度提升 {avg_speedup:.1f}x")
        else:
            print("   ❌ 需要进一步验证")
        
        # 保存报告
        os.makedirs("results", exist_ok=True)
        report = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "summary": {
                "total": total,
                "success_without_kb": success_without,
                "success_with_kb": success_with,
                "avg_speedup": avg_speedup,
                "avg_without_kb_time": avg_without_time,
                "avg_with_kb_time": avg_with_time,
            },
            "results": [asdict(r) for r in self.results],
        }
        
        with open("results/final_benchmark.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n报告已保存到: results/final_benchmark.json")


async def main():
    benchmark = FinalBenchmark(model_name="gpt-4o")
    await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())
