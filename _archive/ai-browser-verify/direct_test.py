"""
直接 API 测试 - 跳过 SkillWeaver，直接测试 LLM + Playwright 能力
"""
import asyncio
import sys
import time
import json
from datetime import datetime

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

# 导入 API Keys
from api_keys import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY


async def test_openai():
    """测试 OpenAI API - GPT-5.2"""
    print("\n📡 测试 OpenAI API (GPT-5.2)...")
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # GPT-5.2 系列模型（需要特殊参数）
        gpt5_models = ["gpt-5.2", "gpt-5.2-chat-latest", "o3-mini"]
        # 回退模型
        fallback_models = ["gpt-4o", "gpt-4o-mini"]
        
        # 先测试 GPT-5.2 (使用 max_completion_tokens 而不是 max_tokens)
        for model_name in gpt5_models:
            try:
                start = time.time()
                # GPT-5.2 不支持 max_tokens，需要用 max_completion_tokens
                # 也不支持 temperature
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": "Say 'API Test OK' in exactly 3 words"}
                    ],
                    max_completion_tokens=20
                )
                elapsed = time.time() - start
                result = response.choices[0].message.content
                print(f"  ✅ 模型 {model_name}: {result} ({elapsed:.2f}s)")
                return True, elapsed, model_name
            except Exception as e:
                print(f"  ⚠️ 模型 {model_name} 失败: {str(e)[:80]}")
                continue
        
        # 回退到 GPT-4o
        for model_name in fallback_models:
            try:
                start = time.time()
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": "Say 'API Test OK' in exactly 3 words"}
                    ],
                    max_tokens=10
                )
                elapsed = time.time() - start
                result = response.choices[0].message.content
                print(f"  ✅ 模型 {model_name} (回退): {result} ({elapsed:.2f}s)")
                return True, elapsed, model_name
            except Exception as e:
                print(f"  ⚠️ 模型 {model_name} 失败: {str(e)[:60]}")
                continue
        
        return False, 0, None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False, 0, None


async def test_anthropic():
    """测试 Anthropic API - Claude Opus 4.5"""
    print("\n📡 测试 Anthropic API (Claude Opus 4.5)...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # 使用最新的 Claude Opus 4.5 模型
        models_to_try = [
            "claude-opus-4-5-20251101",   # Claude Opus 4.5 最新
            "claude-opus-4-5-20251124",   # 可能的另一个版本
            "claude-sonnet-4-20250514",   # Claude Sonnet 4 回退
            "claude-3-5-sonnet-latest",   # 回退
        ]
        
        for model_name in models_to_try:
            try:
                start = time.time()
                response = client.messages.create(
                    model=model_name,
                    max_tokens=20,
                    messages=[
                        {"role": "user", "content": "Say 'API Test OK' in exactly 3 words"}
                    ]
                )
                elapsed = time.time() - start
                result = response.content[0].text
                print(f"  ✅ 模型 {model_name}: {result} ({elapsed:.2f}s)")
                return True, elapsed, model_name
            except Exception as e:
                print(f"  ⚠️ 模型 {model_name} 失败: {str(e)[:60]}")
                continue
        
        return False, 0, None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False, 0, None


async def test_google():
    """测试 Google API - Gemini 3 Flash"""
    print("\n📡 测试 Google API (Gemini 3 Flash)...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # 使用最新的 Gemini 3 Flash 模型
        models_to_try = [
            'gemini-3-flash-preview',     # Gemini 3 Flash 最新
            'gemini-3-flash',             # 可能的简称
            'gemini-2.5-flash-preview',   # Gemini 2.5 回退
            'gemini-2.0-flash',           # Gemini 2.0 回退
        ]
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                start = time.time()
                response = model.generate_content("Say 'API Test OK' in exactly 3 words")
                elapsed = time.time() - start
                result = response.text
                print(f"  ✅ 模型 {model_name}: {result.strip()} ({elapsed:.2f}s)")
                return True, elapsed, model_name
            except Exception as e:
                print(f"  ⚠️ 模型 {model_name} 失败: {str(e)[:60]}")
                continue
        
        return False, 0, None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False, 0, None


async def test_browser_with_ai():
    """测试 AI + 浏览器集成"""
    print("\n🌐 测试 AI + Playwright 浏览器集成...")
    
    try:
        # 使用 OpenAI 因为它已经验证可用
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 1. 访问 GitHub
            print("  1. 访问 GitHub...")
            start = time.time()
            await page.goto("https://github.com", timeout=30000)
            title = await page.title()
            print(f"     页面: {title}")
            
            # 2. 获取页面内容摘要
            content = await page.inner_text("body")
            content_preview = content[:500].replace('\n', ' ')
            
            # 3. 让 AI 分析页面
            print("  2. AI 分析页面内容...")
            ai_start = time.time()
            prompt = f"""Analyze this webpage content briefly (2-3 sentences max):
            
{content_preview}

What is this page about? What can users do here?"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            ai_elapsed = time.time() - ai_start
            
            print(f"  3. AI 分析结果 ({ai_elapsed:.2f}s):")
            print(f"     {response.choices[0].message.content[:200]}...")
            
            total = time.time() - start
            await browser.close()
            
            print(f"  ✅ 完成! 总耗时: {total:.2f}s (AI: {ai_elapsed:.2f}s)")
            return True, total, ai_elapsed
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False, 0, 0


async def test_web3_scenario():
    """测试 Web3 场景 - Uniswap"""
    print("\n🔗 测试 Web3 场景 (Uniswap)...")
    
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print("  1. 访问 Uniswap...")
            start = time.time()
            await page.goto("https://app.uniswap.org", timeout=60000)
            await page.wait_for_timeout(3000)  # 等待 JS 加载
            
            # 获取页面文本内容
            content = await page.inner_text("body")
            content_preview = content[:800].replace('\n', ' ')
            print(f"     已加载 ({time.time()-start:.2f}s)")
            
            # AI 分析操作步骤
            print("  2. AI 分析交互元素...")
            ai_start = time.time()
            prompt = f"""Based on this Uniswap interface content:

{content_preview}

Describe briefly:
1. What interactive elements are visible?
2. What are the main actions a user can take?
3. How would you automate "selecting ETH as input token"?

Keep response under 100 words."""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            ai_elapsed = time.time() - ai_start
            
            print(f"  3. AI 分析 ({ai_elapsed:.2f}s):")
            print(f"     {response.choices[0].message.content[:300]}...")
            
            total = time.time() - start
            await browser.close()
            
            print(f"  ✅ 完成! 总耗时: {total:.2f}s")
            return True, total
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


async def main():
    print("=" * 60)
    print("    AI Browser 直接 API 测试")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    # 测试各 API
    openai_result = await test_openai()
    openai_ok = openai_result[0]
    openai_time = openai_result[1]
    openai_model = openai_result[2] if len(openai_result) > 2 else None
    
    anthropic_result = await test_anthropic()
    anthropic_ok = anthropic_result[0]
    anthropic_time = anthropic_result[1]
    anthropic_model = anthropic_result[2] if len(anthropic_result) > 2 else None
    
    google_result = await test_google()
    google_ok = google_result[0]
    google_time = google_result[1]
    google_model = google_result[2] if len(google_result) > 2 else None
    
    results['api_tests'] = {
        'openai': {'success': openai_ok, 'time': openai_time, 'model': openai_model},
        'anthropic': {'success': anthropic_ok, 'time': anthropic_time, 'model': anthropic_model},
        'google': {'success': google_ok, 'time': google_time, 'model': google_model}
    }
    
    # 测试 AI + 浏览器
    browser_ok, browser_total, browser_ai = await test_browser_with_ai()
    results['browser_ai'] = {
        'success': browser_ok, 
        'total_time': browser_total,
        'ai_time': browser_ai
    }
    
    # 测试 Web3 场景
    web3_ok, web3_time = await test_web3_scenario()
    results['web3'] = {'success': web3_ok, 'time': web3_time}
    
    # 总结
    print("\n" + "=" * 60)
    print("    测试总结")
    print("=" * 60)
    print(f"  OpenAI API:    {'✅' if openai_ok else '❌'} ({openai_time:.2f}s)")
    print(f"  Anthropic API: {'✅' if anthropic_ok else '❌'} ({anthropic_time:.2f}s)")
    print(f"  Google API:    {'✅' if google_ok else '❌'} ({google_time:.2f}s)")
    print(f"  AI + Browser:  {'✅' if browser_ok else '❌'} ({browser_total:.2f}s)")
    print(f"  Web3 Uniswap:  {'✅' if web3_ok else '❌'} ({web3_time:.2f}s)")
    
    all_ok = all([openai_ok, anthropic_ok, google_ok, browser_ok, web3_ok])
    
    if all_ok:
        print("\n🎉 所有测试通过! API 和浏览器集成正常工作")
        print("\n下一步: 可以继续开发 AI 自动学习网站操作的功能")
    else:
        print("\n⚠️ 部分测试失败，请检查 API Keys 或网络连接")
    
    # 保存结果
    with open('results/direct_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存到: results/direct_test_result.json")


if __name__ == "__main__":
    asyncio.run(main())
