"""
批量截取 VitaFlow Onboarding Demo 的所有页面
使用 Playwright 自动化
"""
import asyncio
import os
from playwright.async_api import async_playwright

# 配置
DEMO_URL = "http://localhost:3001/onboarding-demo"
OUTPUT_DIR = r"C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\exports\onboarding-screens-v2"
TOTAL_PAGES = 40

# 页面类型映射（根据 V2 配置）
PAGE_TYPES = {
    1: "launch",
    2: "welcome", 
    3: "name_input",
    4: "transition_greeting",
    5: "goal_selection",
    6: "gender_selection",
    7: "transition_goal",
    8: "activity_level",
    9: "workout_frequency",
    10: "transition_habits",
    11: "age_input",
    12: "height_input",
    13: "weight_input",
    14: "transition_almost",
    15: "target_weight",
    16: "loss_rate",
    17: "transition_motivation",
    18: "permission_health",
    19: "acquisition_channel",
    20: "previous_experience",
    21: "previous_barriers",
    22: "transition_empathy",
    23: "dietary_preferences",
    24: "value_notifications",
    25: "permission_notification",
    26: "secondary_goals",
    27: "referral_code",
    28: "loading",
    29: "result",
    30: "value_ai_scan",
    31: "soft_commit",
    32: "game_scan",
    33: "value_personalized",
    34: "permission_att",
    35: "transition_ready",
    36: "paywall",
    37: "game_spin",
    38: "paywall_discount",
    39: "celebration",
    40: "account"
}


async def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900}
        )
        page = await context.new_page()
        
        # 导航到 demo 页面
        print(f"Loading: {DEMO_URL}")
        await page.goto(DEMO_URL)
        await page.wait_for_load_state('networkidle')
        
        # 确保是 V2 版本
        v2_button = page.get_by_role('button', name='V2 (40p)')
        await v2_button.click()
        await asyncio.sleep(0.5)
        
        # 重置到第 1 页
        reset_button = page.get_by_role('button', name='Reset')
        await reset_button.click()
        await asyncio.sleep(0.5)
        
        # 获取手机框架元素的选择器
        phone_frame = page.locator('[class*="PhoneFrame"]').first
        if not await phone_frame.count():
            # 备用选择器：找到包含 9:41 的容器
            phone_frame = page.locator('text=9:41').locator('xpath=ancestor::div[contains(@class, "rounded")]').first
        
        print(f"\nStarting to capture {TOTAL_PAGES} screenshots...\n")
        
        for i in range(1, TOTAL_PAGES + 1):
            page_type = PAGE_TYPES.get(i, f"page_{i}")
            filename = f"Screen_{i:03d}_{page_type}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 等待页面稳定
            await asyncio.sleep(0.3)
            
            # 截取手机框架内容
            try:
                # 尝试找到手机内容区域
                phone_content = page.locator('div').filter(has_text='9:41').first
                await phone_content.screenshot(path=filepath)
            except Exception:
                # 如果失败，截取整个视口
                await page.screenshot(path=filepath, clip={
                    'x': 160,  # 手机框架大约位置
                    'y': 100,
                    'width': 375,
                    'height': 812
                })
            
            print(f"[OK] [{i:2d}/{TOTAL_PAGES}] {filename}")
            
            # 如果不是最后一页，点击下一页
            if i < TOTAL_PAGES:
                # 使用键盘导航（更可靠）
                await page.keyboard.press('ArrowRight')
                await asyncio.sleep(0.4)
        
        print(f"\n[DONE] All screenshots saved to:\n{OUTPUT_DIR}")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

