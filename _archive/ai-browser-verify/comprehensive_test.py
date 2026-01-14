"""
综合测试脚本 - 更大样本量测试 AI Browser 能力
"""
import asyncio
import sys
import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY

import openai
import anthropic
import google.generativeai as genai


@dataclass
class TestResult:
    """测试结果"""
    name: str
    category: str
    success: bool
    time_seconds: float
    model_used: str
    details: str = ""
    error: str = ""


class ComprehensiveTest:
    """综合测试类"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        genai.configure(api_key=GOOGLE_API_KEY)
        
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("    AI Browser 综合测试 - 大样本量")
        print("=" * 70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 1. 模型性能测试
        await self.test_model_performance()
        
        # 2. 多网站浏览测试
        await self.test_multiple_websites()
        
        # 3. 复杂任务测试
        await self.test_complex_tasks()
        
        # 4. Web3 场景测试
        await self.test_web3_scenarios()
        
        # 5. 并发测试
        await self.test_concurrent_requests()
        
        # 生成报告
        self.generate_report()
        
    async def test_model_performance(self):
        """测试各模型性能"""
        print("\n" + "=" * 70)
        print("📊 Phase 1: 模型性能测试")
        print("=" * 70)
        
        test_prompts = [
            ("简单问答", "What is 2+2?"),
            ("代码生成", "Write a Python function to calculate fibonacci(n)"),
            ("分析任务", "Analyze the pros and cons of React vs Vue in 50 words"),
            ("创意写作", "Write a haiku about AI"),
            ("推理任务", "If all A are B, and all B are C, what can we conclude about A and C?"),
        ]
        
        models = [
            ("GPT-5.2", "openai", "gpt-5.2"),
            ("GPT-4o", "openai", "gpt-4o"),
            ("Claude Opus 4.5", "anthropic", "claude-opus-4-5-20251101"),
            ("Gemini 3 Flash", "google", "gemini-3-flash-preview"),
        ]
        
        for model_name, provider, model_id in models:
            print(f"\n  测试 {model_name}:")
            total_time = 0
            success_count = 0
            
            for task_name, prompt in test_prompts:
                try:
                    start = time.time()
                    
                    if provider == "openai":
                        if "gpt-5" in model_id:
                            response = self.openai_client.chat.completions.create(
                                model=model_id,
                                messages=[{"role": "user", "content": prompt}],
                                max_completion_tokens=100
                            )
                        else:
                            response = self.openai_client.chat.completions.create(
                                model=model_id,
                                messages=[{"role": "user", "content": prompt}],
                                max_tokens=100
                            )
                        result = response.choices[0].message.content
                        
                    elif provider == "anthropic":
                        response = self.anthropic_client.messages.create(
                            model=model_id,
                            max_tokens=100,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        result = response.content[0].text
                        
                    elif provider == "google":
                        model = genai.GenerativeModel(model_id)
                        response = model.generate_content(prompt)
                        result = response.text
                    
                    elapsed = time.time() - start
                    total_time += elapsed
                    success_count += 1
                    print(f"    ✅ {task_name}: {elapsed:.2f}s")
                    
                    self.results.append(TestResult(
                        name=f"{model_name} - {task_name}",
                        category="模型性能",
                        success=True,
                        time_seconds=elapsed,
                        model_used=model_id,
                        details=result[:100]
                    ))
                    
                except Exception as e:
                    print(f"    ❌ {task_name}: {str(e)[:50]}")
                    self.results.append(TestResult(
                        name=f"{model_name} - {task_name}",
                        category="模型性能",
                        success=False,
                        time_seconds=0,
                        model_used=model_id,
                        error=str(e)[:100]
                    ))
            
            avg_time = total_time / max(success_count, 1)
            print(f"    📈 平均响应: {avg_time:.2f}s ({success_count}/{len(test_prompts)} 成功)")

    async def test_multiple_websites(self):
        """测试多个网站"""
        print("\n" + "=" * 70)
        print("🌐 Phase 2: 多网站浏览测试")
        print("=" * 70)
        
        websites = [
            # 常规网站
            ("GitHub", "https://github.com", "技术平台"),
            ("Google", "https://www.google.com", "搜索引擎"),
            ("Wikipedia", "https://www.wikipedia.org", "百科全书"),
            ("Reddit", "https://www.reddit.com", "社区论坛"),
            ("Stack Overflow", "https://stackoverflow.com", "技术问答"),
            ("HackerNews", "https://news.ycombinator.com", "技术新闻"),
            ("Product Hunt", "https://www.producthunt.com", "产品发现"),
            ("Medium", "https://medium.com", "内容平台"),
            # 电商
            ("Amazon", "https://www.amazon.com", "电商平台"),
            ("eBay", "https://www.ebay.com", "拍卖平台"),
            # 社交
            ("Twitter/X", "https://x.com", "社交媒体"),
            ("LinkedIn", "https://www.linkedin.com", "职业社交"),
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            for name, url, category in websites:
                try:
                    page = await browser.new_page()
                    print(f"\n  测试 {name} ({url})...")
                    
                    start = time.time()
                    await page.goto(url, timeout=30000)
                    await page.wait_for_timeout(1000)
                    
                    title = await page.title()
                    content = await page.inner_text("body")
                    load_time = time.time() - start
                    
                    # AI 分析
                    ai_start = time.time()
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": f"Describe this website in 20 words: {content[:500]}"}],
                        max_tokens=50
                    )
                    ai_time = time.time() - ai_start
                    analysis = response.choices[0].message.content
                    
                    total_time = time.time() - start
                    print(f"    ✅ 加载: {load_time:.2f}s | AI: {ai_time:.2f}s | 总计: {total_time:.2f}s")
                    print(f"    📝 {analysis[:80]}...")
                    
                    self.results.append(TestResult(
                        name=name,
                        category=f"网站-{category}",
                        success=True,
                        time_seconds=total_time,
                        model_used="gpt-4o-mini",
                        details=f"Title: {title[:50]}, Analysis: {analysis[:100]}"
                    ))
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"    ❌ {name} 失败: {str(e)[:60]}")
                    self.results.append(TestResult(
                        name=name,
                        category=f"网站-{category}",
                        success=False,
                        time_seconds=0,
                        model_used="",
                        error=str(e)[:100]
                    ))
            
            await browser.close()

    async def test_complex_tasks(self):
        """测试复杂任务"""
        print("\n" + "=" * 70)
        print("🧠 Phase 3: 复杂任务测试")
        print("=" * 70)
        
        tasks = [
            {
                "name": "GitHub 仓库搜索分析",
                "url": "https://github.com/search?q=ai+browser&type=repositories",
                "prompt": "List the top 3 repository names and their star counts from this search result",
            },
            {
                "name": "HackerNews 热门话题",
                "url": "https://news.ycombinator.com",
                "prompt": "What are the top 3 stories on HackerNews right now? Give titles only.",
            },
            {
                "name": "Stack Overflow 问题分析",
                "url": "https://stackoverflow.com/questions?tab=Votes",
                "prompt": "What programming topics appear most frequently in the top questions?",
            },
            {
                "name": "Product Hunt 今日产品",
                "url": "https://www.producthunt.com",
                "prompt": "What type of products are trending today? Summarize in 30 words.",
            },
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            for task in tasks:
                try:
                    page = await browser.new_page()
                    print(f"\n  任务: {task['name']}...")
                    
                    start = time.time()
                    await page.goto(task["url"], timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    content = await page.inner_text("body")
                    
                    # 使用 GPT-5.2 进行复杂分析
                    ai_start = time.time()
                    response = self.openai_client.chat.completions.create(
                        model="gpt-5.2",
                        messages=[{
                            "role": "user", 
                            "content": f"{task['prompt']}\n\nPage content:\n{content[:2000]}"
                        }],
                        max_completion_tokens=200
                    )
                    ai_time = time.time() - ai_start
                    result = response.choices[0].message.content
                    
                    total_time = time.time() - start
                    print(f"    ✅ 完成 ({total_time:.2f}s, AI: {ai_time:.2f}s)")
                    print(f"    📝 {result[:150]}...")
                    
                    self.results.append(TestResult(
                        name=task["name"],
                        category="复杂任务",
                        success=True,
                        time_seconds=total_time,
                        model_used="gpt-5.2",
                        details=result[:200]
                    ))
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"    ❌ 失败: {str(e)[:60]}")
                    self.results.append(TestResult(
                        name=task["name"],
                        category="复杂任务",
                        success=False,
                        time_seconds=0,
                        model_used="gpt-5.2",
                        error=str(e)[:100]
                    ))
            
            await browser.close()

    async def test_web3_scenarios(self):
        """测试 Web3 场景"""
        print("\n" + "=" * 70)
        print("🔗 Phase 4: Web3 场景测试")
        print("=" * 70)
        
        web3_sites = [
            ("OpenSea", "https://opensea.io", "NFT 市场"),
            ("DexScreener", "https://dexscreener.com", "DEX 分析"),
            ("CoinGecko", "https://www.coingecko.com", "加密货币数据"),
            ("Etherscan", "https://etherscan.io", "区块链浏览器"),
            ("DefiLlama", "https://defillama.com", "DeFi 数据"),
            ("Aave", "https://aave.com", "借贷协议"),
            ("Compound", "https://compound.finance", "借贷协议"),
            ("Blur", "https://blur.io", "NFT 市场"),
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            for name, url, category in web3_sites:
                try:
                    page = await browser.new_page()
                    print(f"\n  测试 {name} ({category})...")
                    
                    start = time.time()
                    await page.goto(url, timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    title = await page.title()
                    content = await page.inner_text("body")
                    load_time = time.time() - start
                    
                    # AI 分析 Web3 功能
                    ai_start = time.time()
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "user", 
                            "content": f"What Web3 features does this site offer? (30 words max): {content[:800]}"
                        }],
                        max_tokens=60
                    )
                    ai_time = time.time() - ai_start
                    analysis = response.choices[0].message.content
                    
                    total_time = time.time() - start
                    print(f"    ✅ 加载: {load_time:.2f}s | AI: {ai_time:.2f}s")
                    print(f"    📝 {analysis[:100]}...")
                    
                    self.results.append(TestResult(
                        name=f"Web3-{name}",
                        category=f"Web3-{category}",
                        success=True,
                        time_seconds=total_time,
                        model_used="gpt-4o-mini",
                        details=analysis[:150]
                    ))
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"    ❌ {name} 失败: {str(e)[:60]}")
                    self.results.append(TestResult(
                        name=f"Web3-{name}",
                        category=f"Web3-{category}",
                        success=False,
                        time_seconds=0,
                        model_used="",
                        error=str(e)[:100]
                    ))
            
            await browser.close()

    async def test_concurrent_requests(self):
        """测试并发请求"""
        print("\n" + "=" * 70)
        print("⚡ Phase 5: 并发测试")
        print("=" * 70)
        
        async def single_request(prompt: str, model: str) -> tuple:
            start = time.time()
            try:
                if "gpt" in model:
                    if "gpt-5" in model:
                        response = self.openai_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            max_completion_tokens=50
                        )
                    else:
                        response = self.openai_client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=50
                        )
                    return True, time.time() - start
                elif "claude" in model:
                    response = self.anthropic_client.messages.create(
                        model=model,
                        max_tokens=50,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return True, time.time() - start
                elif "gemini" in model:
                    m = genai.GenerativeModel(model)
                    response = m.generate_content(prompt)
                    return True, time.time() - start
            except Exception as e:
                return False, 0
        
        # 测试 5 个并发请求
        print("\n  测试 5 个并发请求...")
        prompts = [f"Count to {i}" for i in range(1, 6)]
        
        for model_name, model_id in [
            ("GPT-5.2", "gpt-5.2"),
            ("GPT-4o-mini", "gpt-4o-mini"),
            ("Claude Opus 4.5", "claude-opus-4-5-20251101"),
            ("Gemini 3 Flash", "gemini-3-flash-preview"),
        ]:
            start = time.time()
            tasks = [single_request(p, model_id) for p in prompts]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start
            
            success_count = sum(1 for r in results if r[0])
            avg_time = sum(r[1] for r in results if r[0]) / max(success_count, 1)
            
            print(f"    {model_name}: {success_count}/5 成功, 总时间: {total_time:.2f}s, 平均: {avg_time:.2f}s")
            
            self.results.append(TestResult(
                name=f"并发测试-{model_name}",
                category="并发性能",
                success=success_count == 5,
                time_seconds=total_time,
                model_used=model_id,
                details=f"{success_count}/5 成功, 平均响应: {avg_time:.2f}s"
            ))

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 70)
        print("📊 测试报告")
        print("=" * 70)
        
        # 统计
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        
        # 按类别统计
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = {"total": 0, "success": 0, "time": []}
            categories[r.category]["total"] += 1
            if r.success:
                categories[r.category]["success"] += 1
                categories[r.category]["time"].append(r.time_seconds)
        
        print(f"\n总计: {success}/{total} 测试通过 ({success/total*100:.1f}%)")
        print("\n按类别统计:")
        print("-" * 50)
        
        for cat, stats in sorted(categories.items()):
            avg_time = sum(stats["time"]) / max(len(stats["time"]), 1)
            print(f"  {cat}: {stats['success']}/{stats['total']} 通过, 平均耗时: {avg_time:.2f}s")
        
        # 保存详细结果
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "success": success,
                "success_rate": success / total * 100,
            },
            "by_category": {
                cat: {
                    "total": stats["total"],
                    "success": stats["success"],
                    "avg_time": sum(stats["time"]) / max(len(stats["time"]), 1)
                }
                for cat, stats in categories.items()
            },
            "details": [asdict(r) for r in self.results]
        }
        
        with open("results/comprehensive_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细报告已保存到: results/comprehensive_test_report.json")
        print("=" * 70)


async def main():
    test = ComprehensiveTest()
    await test.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
