"""
批量截取 VitaFlow Onboarding Demo V2 - 高质量版本
- 只截取手机框架内部
- 自动填写表单数据
- 高分辨率输出
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


async def fill_form_data(page, current_page: int):
    """根据当前页面填写表单数据"""
    
    # P3: 姓名输入
    if current_page == 3:
        input_field = page.locator('input[placeholder="Enter your name"]')
        if await input_field.count():
            await input_field.fill("Alex")
            await asyncio.sleep(0.2)
            # 点击 Continue
            continue_btn = page.get_by_role('button', name='Continue')
            if await continue_btn.count() and await continue_btn.is_enabled():
                await continue_btn.click()
                return True
    
    # P5: 目标选择 - 选择 Lose Weight
    elif current_page == 5:
        option = page.locator('text=Lose Weight').first
        if await option.count():
            await option.click()
            return True
    
    # P6: 性别选择 - 选择 Female
    elif current_page == 6:
        option = page.locator('text=Female').first
        if await option.count():
            await option.click()
            return True
    
    # P8: 活动水平 - 选择 Moderately Active
    elif current_page == 8:
        option = page.locator('text=Moderately Active').first
        if await option.count():
            await option.click()
            return True
    
    # P9: 运动频率 - 选择 Regularly
    elif current_page == 9:
        option = page.locator('text=Regularly').first
        if await option.count():
            await option.click()
            return True
    
    # P11: 年龄输入 - 默认值已设置，直接点击 Continue
    elif current_page == 11:
        continue_btn = page.get_by_role('button', name='Continue')
        if await continue_btn.count():
            await continue_btn.click()
            return True
    
    # P12: 身高输入 - 默认值已设置，直接点击 Continue
    elif current_page == 12:
        continue_btn = page.get_by_role('button', name='Continue')
        if await continue_btn.count():
            await continue_btn.click()
            return True
    
    # P13: 体重输入 - 默认值已设置，直接点击 Continue
    elif current_page == 13:
        continue_btn = page.get_by_role('button', name='Continue')
        if await continue_btn.count():
            await continue_btn.click()
            return True
    
    # P15: 目标体重 - 默认值已设置，直接点击 Continue
    elif current_page == 15:
        continue_btn = page.get_by_role('button', name='Continue')
        if await continue_btn.count():
            await continue_btn.click()
            return True
    
    # P16: 减重速度 - 选择 Recommended
    elif current_page == 16:
        option = page.locator('text=Recommended').first
        if await option.count():
            await option.click()
            return True
    
    # P19: 渠道来源 - 选择 Social Media
    elif current_page == 19:
        option = page.locator('text=Social Media').first
        if await option.count():
            await option.click()
            return True
    
    # P20: 之前经验 - 选择 Yes
    elif current_page == 20:
        option = page.locator('text=Yes, I have').first
        if await option.count():
            await option.click()
            return True
    
    return False


async def main():
    # 清空并重建输出目录
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        # 启动浏览器 - 高DPI设置
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            device_scale_factor=2  # 2x 高清截图
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
        
        for i in range(1, TOTAL_PAGES + 1):
            page_type = PAGE_TYPES.get(i, f"page_{i}")
            filename = f"Screen_{i:03d}_{page_type}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 等待页面稳定
            await asyncio.sleep(0.4)
            
            # 定位手机框架内部内容区域
            # 找到包含 9:41 的手机屏幕区域
            phone_screen = page.locator('div').filter(has_text='9:41').first
            
            try:
                # 获取手机框架的边界
                # 手机框架的父容器应该有圆角
                phone_container = page.locator('div[class*="rounded-"]').filter(
                    has=page.locator('text=9:41')
                ).first
                
                if await phone_container.count():
                    # 截取手机框架
                    await phone_container.screenshot(path=filepath, scale='css')
                else:
                    # 备用方案：使用固定裁剪区域
                    await page.screenshot(
                        path=filepath,
                        clip={
                            'x': 168,   # 手机框架左边位置
                            'y': 108,   # 手机框架顶部位置
                            'width': 393,  # iPhone 14 宽度
                            'height': 852  # iPhone 14 高度
                        }
                    )
                
                print(f"[OK] [{i:2d}/{TOTAL_PAGES}] {filename}")
                
            except Exception as e:
                print(f"[ERR] [{i:2d}/{TOTAL_PAGES}] {filename} - {str(e)[:50]}")
                # 错误时截取整个视口作为备份
                await page.screenshot(path=filepath)
            
            # 处理当前页面的表单填写
            if i < TOTAL_PAGES:
                form_handled = await fill_form_data(page, i)
                
                if not form_handled:
                    # 如果没有特殊表单处理，使用键盘导航到下一页
                    await page.keyboard.press('ArrowRight')
                
                await asyncio.sleep(0.3)
        
        print(f"\n[DONE] All {TOTAL_PAGES} screenshots saved to:\n{OUTPUT_DIR}")
        print("\nScreenshot quality: 2x Retina resolution")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

