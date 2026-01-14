"""
Phase 2: 基础测试
验证 SkillWeaver 基础功能和浏览器自动化能力
"""
import asyncio
import time
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "SkillWeaver"))

from config import config


@dataclass
class TestMetrics:
    """测试指标"""
    name: str
    success: bool
    time_seconds: float
    steps: int = 0
    error: Optional[str] = None


async def test_playwright_basic():
    """测试 Playwright 基础功能"""
    print("\n[测试 1] Playwright 基础功能")
    print("-" * 40)
    
    start = time.time()
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            print("  启动浏览器...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 测试 1: 访问 Google
            print("  访问 Google...")
            await page.goto("https://www.google.com", timeout=30000)
            title = await page.title()
            print(f"    页面标题: {title}")
            
            # 测试 2: 搜索框交互
            print("  测试搜索框交互...")
            search_box = page.locator('textarea[name="q"], input[name="q"]')
            await search_box.fill("AI browser automation")
            
            # 测试 3: 截图
            print("  截图...")
            screenshot_path = Path(__file__).parent.parent / "results" / "test_screenshot.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path))
            print(f"    截图保存到: {screenshot_path}")
            
            await browser.close()
        
        elapsed = time.time() - start
        print(f"  ✅ 测试通过 (耗时: {elapsed:.2f}s)")
        return TestMetrics("playwright_basic", True, elapsed, steps=3)
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ 测试失败: {e}")
        return TestMetrics("playwright_basic", False, elapsed, error=str(e))


async def test_accessibility_tree():
    """测试 Accessibility Tree 获取"""
    print("\n[测试 2] Accessibility Tree 获取")
    print("-" * 40)
    
    start = time.time()
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print("  访问 Reddit...")
            await page.goto("https://www.reddit.com", timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # 获取 Accessibility Tree
            print("  获取 Accessibility Tree...")
            snapshot = await page.accessibility.snapshot()
            
            if snapshot:
                print(f"    根节点角色: {snapshot.get('role', 'unknown')}")
                children = snapshot.get('children', [])
                print(f"    子节点数量: {len(children)}")
                
                # 统计可交互元素
                def count_interactive(node, count=0):
                    role = node.get('role', '')
                    if role in ['button', 'link', 'textbox', 'checkbox']:
                        count += 1
                    for child in node.get('children', []):
                        count = count_interactive(child, count)
                    return count
                
                interactive_count = count_interactive(snapshot)
                print(f"    可交互元素: {interactive_count}")
            
            await browser.close()
        
        elapsed = time.time() - start
        print(f"  ✅ 测试通过 (耗时: {elapsed:.2f}s)")
        return TestMetrics("accessibility_tree", True, elapsed, steps=2)
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ 测试失败: {e}")
        return TestMetrics("accessibility_tree", False, elapsed, error=str(e))


async def test_web3_page():
    """测试 Web3 页面访问 (Uniswap)"""
    print("\n[测试 3] Web3 页面访问 (Uniswap)")
    print("-" * 40)
    
    start = time.time()
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print("  访问 Uniswap...")
            await page.goto("https://app.uniswap.org", timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # 检查页面加载
            print("  检查页面元素...")
            title = await page.title()
            print(f"    页面标题: {title}")
            
            # 查找 Swap 相关元素
            swap_text = await page.locator("text=Swap").count()
            print(f"    找到 'Swap' 文本: {swap_text} 处")
            
            # 截图
            screenshot_path = Path(__file__).parent.parent / "results" / "uniswap_screenshot.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"    截图保存到: {screenshot_path}")
            
            await browser.close()
        
        elapsed = time.time() - start
        print(f"  ✅ 测试通过 (耗时: {elapsed:.2f}s)")
        return TestMetrics("web3_page", True, elapsed, steps=3)
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ 测试失败: {e}")
        return TestMetrics("web3_page", False, elapsed, error=str(e))


async def test_skillweaver_import():
    """测试 SkillWeaver 导入"""
    print("\n[测试 4] SkillWeaver 导入")
    print("-" * 40)
    
    start = time.time()
    
    try:
        print("  导入 SkillWeaver 模块...")
        
        # 尝试导入核心模块
        from skillweaver import agent
        print("    ✓ skillweaver.agent")
        
        from skillweaver import attempt_task
        print("    ✓ skillweaver.attempt_task")
        
        from skillweaver import explore
        print("    ✓ skillweaver.explore")
        
        from skillweaver.environment import browser
        print("    ✓ skillweaver.environment.browser")
        
        from skillweaver.knowledge_base import knowledge_base
        print("    ✓ skillweaver.knowledge_base")
        
        elapsed = time.time() - start
        print(f"  ✅ 测试通过 (耗时: {elapsed:.2f}s)")
        return TestMetrics("skillweaver_import", True, elapsed)
        
    except ImportError as e:
        elapsed = time.time() - start
        print(f"  ⚠️ 部分模块导入失败: {e}")
        print("    这是预期的，需要先安装 SkillWeaver 依赖")
        return TestMetrics("skillweaver_import", False, elapsed, error=str(e))
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ 测试失败: {e}")
        return TestMetrics("skillweaver_import", False, elapsed, error=str(e))


async def main():
    """主测试函数"""
    print("=" * 60)
    print("Phase 2: 基础测试")
    print("=" * 60)
    print(f"使用模型: {config.fast_model}")
    
    results = []
    
    # 运行测试
    results.append(await test_playwright_basic())
    results.append(await test_accessibility_tree())
    results.append(await test_web3_page())
    results.append(await test_skillweaver_import())
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.success)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    print("\n详细结果:")
    for r in results:
        status = "✅" if r.success else "❌"
        print(f"  {status} {r.name}: {r.time_seconds:.2f}s")
        if r.error:
            print(f"      错误: {r.error[:80]}")
    
    # 保存结果
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    import json
    from datetime import datetime
    
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "passed": passed,
        "total": total,
        "tests": [
            {
                "name": r.name,
                "success": r.success,
                "time": r.time_seconds,
                "error": r.error
            }
            for r in results
        ]
    }
    
    results_path = results_dir / f"basic_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_path, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\n结果保存到: {results_path}")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
