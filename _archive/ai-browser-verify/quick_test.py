"""
快速测试脚本 - 验证环境和 API 配置是否正确
"""
import asyncio
import os
import sys
from pathlib import Path

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def check_environment():
    """检查环境配置"""
    print("=" * 60)
    print("AI Browser 技术验证 - 环境检查")
    print("=" * 60)
    
    results = []
    
    # 1. Python 版本
    py_version = sys.version_info
    py_ok = py_version.major == 3 and py_version.minor >= 10
    results.append(("Python 版本", f"{py_version.major}.{py_version.minor}", py_ok))
    
    # 2. 必要目录
    dirs = ["SkillWeaver", "knowledge_base", "results", "tests"]
    for d in dirs:
        path = Path(__file__).parent / d
        results.append((f"目录 {d}", str(path.exists()), path.exists()))
    
    # 3. API Keys (从 config.py 读取，它会自动加载 api_keys.py)
    try:
        from config import config
        api_keys = {
            "OPENAI_API_KEY": config.openai_api_key,
            "ANTHROPIC_API_KEY": config.anthropic_api_key,
            "GOOGLE_API_KEY": config.google_api_key,
        }
    except ImportError:
        api_keys = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY", ""),
        }
    
    for key, value in api_keys.items():
        has_key = bool(value) and value != "xxx" and len(value) > 10
        display = f"{value[:15]}..." if has_key else "未设置"
        results.append((key, display, has_key))
    
    # 4. 依赖库
    deps = [
        ("playwright", "playwright"),
        ("litellm", "litellm"),
        ("anthropic", "anthropic"),
        ("openai", "openai"),
    ]
    
    for name, module in deps:
        try:
            __import__(module)
            results.append((f"依赖 {name}", "已安装", True))
        except ImportError:
            results.append((f"依赖 {name}", "未安装", False))
    
    # 打印结果
    print("\n检查结果:")
    print("-" * 60)
    all_ok = True
    for name, status, ok in results:
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}: {status}")
        if not ok:
            all_ok = False
    
    print("-" * 60)
    if all_ok:
        print("✅ 所有检查通过！可以开始测试")
    else:
        print("⚠️ 部分检查未通过，请查看上方详情")
    
    return all_ok


async def quick_llm_test():
    """快速 LLM 测试"""
    print("\n" + "=" * 60)
    print("快速 LLM 测试")
    print("=" * 60)
    
    try:
        from llm_adapter import get_llm, LLMAdapter
        
        print(f"\n可用模型: {LLMAdapter.list_available_models()}")
        
        # 测试 Gemini (通常最快最便宜)
        print("\n测试 Gemini 3 Flash...")
        llm = get_llm("gemini-3-flash")
        response = await llm.chat([
            {"role": "user", "content": "Reply with exactly: 'AI Browser Test OK'"}
        ])
        print(f"  响应: {response}")
        
        if "模拟" not in response:
            print("✅ LLM 测试通过!")
            return True
        else:
            print("⚠️ 使用模拟模式（可能是 API Key 未配置）")
            return False
            
    except Exception as e:
        print(f"❌ LLM 测试失败: {e}")
        return False


async def quick_playwright_test():
    """快速 Playwright 测试"""
    print("\n" + "=" * 60)
    print("快速 Playwright 测试")
    print("=" * 60)
    
    try:
        from playwright.async_api import async_playwright
        
        print("\n启动浏览器...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print("访问 Google...")
            await page.goto("https://www.google.com", timeout=30000)
            title = await page.title()
            print(f"  页面标题: {title}")
            
            await browser.close()
        
        print("✅ Playwright 测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ Playwright 测试失败: {e}")
        print("  提示: 运行 'playwright install chromium' 安装浏览器")
        return False


async def main():
    """主函数"""
    env_ok = check_environment()
    
    if env_ok:
        llm_ok = await quick_llm_test()
        pw_ok = await quick_playwright_test()
        
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"  环境配置: {'✅' if env_ok else '❌'}")
        print(f"  LLM 连接: {'✅' if llm_ok else '⚠️ 模拟模式'}")
        print(f"  Playwright: {'✅' if pw_ok else '❌'}")
        
        if env_ok and pw_ok:
            print("\n🚀 环境准备就绪！运行 'python run_verify.py' 开始测试")
        else:
            print("\n⚠️ 请先解决上述问题")
    else:
        print("\n请先完成环境配置:")
        print("  1. 运行 setup_env.bat (Windows) 或 ./setup_env.sh (Linux/Mac)")
        print("  2. 设置 API Keys: 编辑 set_api_keys.bat 并运行")


if __name__ == "__main__":
    asyncio.run(main())
