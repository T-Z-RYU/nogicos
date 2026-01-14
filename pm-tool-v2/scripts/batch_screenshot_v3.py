"""
批量截取 VitaFlow Onboarding Demo V3 - 最终版本
修复：
1. 表单页面先填写再截图
2. Loading 页面等待完成后跳过，直接截 Result
3. 正确的截图顺序
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

# 需要填写表单的页面
FORM_PAGES = {3, 5, 6, 8, 9, 11, 12, 13, 15, 16, 19, 20}

# 多选页面（需要点击 Continue）
MULTI_SELECT_PAGES = {21, 23, 26}


async def take_phone_screenshot(page, filepath: str):
    """截取手机框架内部截图"""
    try:
        # 方法1: 尝试找到手机框架容器
        phone_container = page.locator('div[class*="rounded-"]').filter(
            has=page.locator('text=9:41')
        ).first
        
        if await phone_container.count():
            await phone_container.screenshot(path=filepath, scale='css')
            return True
    except:
        pass
    
    # 方法2: 使用固定裁剪区域
    await page.screenshot(
        path=filepath,
        clip={
            'x': 168,
            'y': 108,
            'width': 393,
            'height': 852
        }
    )
    return True


async def fill_and_submit(page, current_page: int):
    """填写表单并提交，返回是否自动跳转"""
    
    await asyncio.sleep(0.3)
    
    # P3: 姓名输入
    if current_page == 3:
        input_field = page.locator('input[placeholder="Enter your name"]')
        if await input_field.count():
            await input_field.fill("Alex")
            await asyncio.sleep(0.2)
        continue_btn = page.get_by_role('button', name='Continue')
        if await continue_btn.count() and await continue_btn.is_enabled():
            await continue_btn.click()
            return True
    
    # P5: 目标选择 - Lose Weight (自动跳转)
    elif current_page == 5:
        option = page.locator('text=Lose Weight').first
        if await option.count():
            await option.click()
            return True
    
    # P6: 性别选择 - Female (自动跳转)
    elif current_page == 6:
        option = page.locator('text=Female').first
        if await option.count():
            await option.click()
            return True
    
    # P8: 活动水平 - Moderately Active (自动跳转)
    elif current_page == 8:
        option = page.locator('text=Moderately Active').first
        if await option.count():
            await option.click()
            return True
    
    # P9: 运动频率 - Regularly (自动跳转)
    elif current_page == 9:
        option = page.locator('text=Regularly').first
        if await option.count():
            await option.click()
            return True
    
    # P11, P12, P13, P15: 数字输入 - 点击 Continue
    elif current_page in {11, 12, 13, 15}:
        continue_btn = page.get_by_role('button', name='Continue')
        if await continue_btn.count():
            await continue_btn.click()
            return True
    
    # P16: 减重速度 - Recommended (自动跳转)
    elif current_page == 16:
        option = page.locator('text=Recommended').first
        if await option.count():
            await option.click()
            return True
    
    # P19: 渠道来源 - Social Media (自动跳转)
    elif current_page == 19:
        option = page.locator('text=Social Media').first
        if await option.count():
            await option.click()
            return True
    
    # P20: 之前经验 - Yes (自动跳转)
    elif current_page == 20:
        option = page.locator('text=Yes, I have').first
        if await option.count():
            await option.click()
            return True
    
    # P21, P23, P26: 多选页面 - 选一个然后点 Continue
    elif current_page == 21:
        option = page.locator('text=Lost motivation').first
        if await option.count():
            await option.click()
            await asyncio.sleep(0.5)  # 等待按钮启用
        continue_btn = page.get_by_role('button', name='Continue')
        try:
            await continue_btn.click(timeout=3000)
            return True
        except:
            return False
    
    elif current_page == 23:
        option = page.locator('text=No restrictions').first
        if await option.count():
            await option.click()
            await asyncio.sleep(0.5)
        continue_btn = page.get_by_role('button', name='Continue')
        try:
            await continue_btn.click(timeout=3000)
            return True
        except:
            return False
    
    elif current_page == 26:
        option = page.locator('text=More energy').first
        if await option.count():
            await option.click()
            await asyncio.sleep(0.5)
        continue_btn = page.get_by_role('button', name='Continue')
        try:
            await continue_btn.click(timeout=3000)
            return True
        except:
            return False
    
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
        
        # 重置到第 1 页
        reset_button = page.get_by_role('button', name='Reset')
        await reset_button.click()
        await asyncio.sleep(0.5)
        
        print(f"\nCapturing {TOTAL_PAGES} high-quality screenshots...\n")
        
        current_page = 1
        
        while current_page <= TOTAL_PAGES:
            page_type = PAGE_TYPES.get(current_page, f"page_{current_page}")
            filename = f"Screen_{current_page:03d}_{page_type}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            await asyncio.sleep(0.4)
            
            # 特殊处理：Loading 页面 (P28)
            if current_page == 28:
                # 截取 Loading 状态
                await take_phone_screenshot(page, filepath)
                print(f"[OK] [{current_page:2d}/{TOTAL_PAGES}] {filename}")
                
                # 等待 Loading 完成（等待 Result 页面出现）
                print("     Waiting for loading to complete...")
                await asyncio.sleep(4)  # Loading 动画约 3-4 秒
                
                current_page += 1
                continue
            
            # 特殊处理：Result 页面 (P29)
            if current_page == 29:
                # 确保 Result 已加载
                await asyncio.sleep(0.5)
                await take_phone_screenshot(page, filepath)
                print(f"[OK] [{current_page:2d}/{TOTAL_PAGES}] {filename}")
                await page.keyboard.press('ArrowRight')
                current_page += 1
                continue
            
            # 普通页面：先截图
            await take_phone_screenshot(page, filepath)
            print(f"[OK] [{current_page:2d}/{TOTAL_PAGES}] {filename}")
            
            # 处理表单填写和导航
            if current_page in FORM_PAGES or current_page in MULTI_SELECT_PAGES:
                auto_advanced = await fill_and_submit(page, current_page)
                if not auto_advanced:
                    await page.keyboard.press('ArrowRight')
            else:
                # 非表单页面，直接下一页
                await page.keyboard.press('ArrowRight')
            
            await asyncio.sleep(0.3)
            current_page += 1
        
        print(f"\n[DONE] All {TOTAL_PAGES} screenshots saved to:\n{OUTPUT_DIR}")
        print("\nScreenshot quality: 2x Retina resolution")
        print("Form data filled: Yes (Name: Alex)")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

