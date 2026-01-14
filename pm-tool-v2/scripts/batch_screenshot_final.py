"""
批量截取 VitaFlow Onboarding Demo - 最终稳定版
使用页码按钮直接导航，避免页面偏移问题
"""
import asyncio
import os
from playwright.async_api import async_playwright

# 配置
DEMO_URL = "http://localhost:3001/onboarding-demo"
OUTPUT_DIR = r"C:\Users\WIN\Desktop\Cursor Project\pm-tool-v2\exports\onboarding-screens-v2"
TOTAL_PAGES = 40

# 页面类型映射
PAGE_TYPES = {
    1: "launch", 2: "welcome", 3: "name_input", 4: "transition_greeting",
    5: "goal_selection", 6: "gender_selection", 7: "transition_goal",
    8: "activity_level", 9: "workout_frequency", 10: "transition_habits",
    11: "age_input", 12: "height_input", 13: "weight_input", 14: "transition_almost",
    15: "target_weight", 16: "loss_rate", 17: "transition_motivation",
    18: "permission_health", 19: "acquisition_channel", 20: "previous_experience",
    21: "previous_barriers", 22: "transition_empathy", 23: "dietary_preferences",
    24: "value_notifications", 25: "permission_notification", 26: "secondary_goals",
    27: "referral_code", 28: "loading", 29: "result", 30: "value_ai_scan",
    31: "soft_commit", 32: "game_scan", 33: "value_personalized",
    34: "permission_att", 35: "transition_ready", 36: "paywall",
    37: "game_spin", 38: "paywall_discount", 39: "celebration", 40: "account"
}


async def setup_user_data(page):
    """通过 localStorage 预设用户数据，确保 Result 页面有数据"""
    # 设置用户数据到 sessionStorage
    await page.evaluate("""
        const userData = {
            name: 'Alex',
            goal: 'lose_weight',
            gender: 'female',
            age: 28,
            currentWeight: 70,
            targetWeight: 60,
            height: 165,
            weeklyLossRate: 1,
            activityLevel: 'moderate',
            workoutFrequency: 'often',
            acquisitionChannel: 'social',
            previousAppExperience: 'yes',
            previousBarriers: ['motivation'],
            dietaryPreferences: ['none'],
            secondaryGoals: ['energy'],
            healthKitConnected: true,
            notificationsEnabled: true,
            trackingAllowed: true,
            referralCode: null
        };
        
        const results = {
            dailyCalories: 1650,
            targetDate: 'Mar 15, 2026',
            weeklyLoss: 0.5,
            bmi: 25.7,
            tdee: 2200
        };
        
        // 更新 Zustand store 的 sessionStorage
        const storeData = {
            state: {
                currentStep: 1,
                totalSteps: 40,
                userData: userData,
                results: results,
                scanGameCompleted: false,
                spinAttempts: 0,
                discountWon: null,
                paymentCompleted: false,
                selectedPlan: null
            },
            version: 0
        };
        
        sessionStorage.setItem('vitaflow-onboarding-demo', JSON.stringify(storeData));
    """)


async def take_phone_screenshot(page, filepath: str):
    """截取手机框架内部截图"""
    try:
        phone_container = page.locator('div[class*="rounded-"]').filter(
            has=page.locator('text=9:41')
        ).first
        
        if await phone_container.count():
            await phone_container.screenshot(path=filepath, scale='css')
            return True
    except:
        pass
    
    # 备用方案
    await page.screenshot(
        path=filepath,
        clip={'x': 168, 'y': 108, 'width': 393, 'height': 852}
    )
    return True


async def go_to_page(page, target_page: int):
    """通过点击页码按钮直接跳转到指定页面"""
    # 找到 Flow Overview 中的页码按钮
    page_button = page.locator(f'button:has-text("{target_page}")').filter(
        has_text=str(target_page)
    ).first
    
    # 尝试更精确的选择器
    buttons = page.locator('button')
    count = await buttons.count()
    
    for i in range(count):
        btn = buttons.nth(i)
        text = await btn.inner_text()
        if text.strip() == str(target_page):
            await btn.click()
            await asyncio.sleep(0.4)
            return True
    
    return False


async def main():
    # 清空并重建输出目录
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            device_scale_factor=2
        )
        page = await context.new_page()
        
        print(f"Loading: {DEMO_URL}")
        await page.goto(DEMO_URL)
        await page.wait_for_load_state('networkidle')
        
        # 确保是 V2 版本
        v2_button = page.get_by_role('button', name='V2 (40p)')
        await v2_button.click()
        await asyncio.sleep(0.3)
        
        # 预设用户数据
        print("Setting up user data...")
        await setup_user_data(page)
        
        # 刷新页面使数据生效
        await page.reload()
        await page.wait_for_load_state('networkidle')
        
        # 再次确保是 V2 版本
        v2_button = page.get_by_role('button', name='V2 (40p)')
        await v2_button.click()
        await asyncio.sleep(0.3)
        
        print(f"\nCapturing {TOTAL_PAGES} high-quality screenshots...\n")
        
        for target_page in range(1, TOTAL_PAGES + 1):
            page_type = PAGE_TYPES.get(target_page, f"page_{target_page}")
            filename = f"Screen_{target_page:03d}_{page_type}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 直接跳转到目标页面
            jumped = await go_to_page(page, target_page)
            if not jumped:
                print(f"[WARN] Could not jump to page {target_page}, using keyboard")
            
            await asyncio.sleep(0.5)
            
            # 特殊处理：Loading 页面需要等待一下看到动画
            if target_page == 28:
                await asyncio.sleep(0.3)
            
            # 截图
            await take_phone_screenshot(page, filepath)
            print(f"[OK] [{target_page:2d}/{TOTAL_PAGES}] {filename}")
        
        print(f"\n[DONE] All {TOTAL_PAGES} screenshots saved to:\n{OUTPUT_DIR}")
        print("\nScreenshot quality: 2x Retina resolution")
        print("User data: Pre-filled (Name: Alex, Goal: Lose Weight)")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

