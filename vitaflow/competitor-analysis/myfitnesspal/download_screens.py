# -*- coding: utf-8 -*-
"""
从 screensdesign.com 下载 App 截图
使用已登录会员的 Chrome 浏览器窗口
"""

import os
import time
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============ 配置区域 ============
# 目标URL
TARGET_URL = "https://screensdesign.com/apps/myfitnesspal-calorie-counter/?ts=0&vt=1&id=904"

# 输出文件夹名称
OUTPUT_FOLDER = "MFP_Screens_Downloaded"

# 图片处理参数
TARGET_WIDTH = 402  # 目标宽度（像素）
# =================================


def connect_to_chrome():
    """连接到已打开的 Chrome 调试窗口"""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("[OK] 成功连接到 Chrome 浏览器")
        return driver
    except Exception as e:
        print(f"[X] 无法连接到 Chrome: {e}")
        print("\n请确保已用以下命令启动 Chrome:")
        print('& "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        return None


def scroll_to_load_all_images(driver):
    """滚动页面以加载所有图片"""
    print("正在滚动页面加载所有图片...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 计算新的滚动高度
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            break
        last_height = new_height
    
    # 滚动回顶部
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    print("[OK] 页面加载完成")


def get_screenshot_urls(driver):
    """获取页面上所有截图的URL"""
    print("正在获取截图URL...")
    
    # 等待图片加载
    time.sleep(2)
    
    # 查找所有截图图片 - 尝试多种选择器
    image_urls = []
    
    # 常见的图片选择器
    selectors = [
        "img[src*='screen']",
        "img[src*='screenshot']", 
        "img[data-src]",
        ".screen-image img",
        ".screenshot img",
        "img[loading='lazy']",
        "picture source",
        "picture img",
        "img"
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                # 尝试获取图片URL
                url = elem.get_attribute("src") or elem.get_attribute("data-src") or elem.get_attribute("srcset")
                
                if url and url.startswith("http"):
                    # 过滤掉小图标和非截图图片
                    if any(skip in url.lower() for skip in ['logo', 'icon', 'avatar', 'profile', 'favicon']):
                        continue
                    if url not in image_urls:
                        image_urls.append(url)
        except:
            continue
    
    print(f"[OK] 找到 {len(image_urls)} 个图片URL")
    return image_urls


def download_and_process_image(url, output_path, index):
    """下载图片并处理（调整尺寸为402宽度，转换为PNG）"""
    try:
        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 打开图片
        img = Image.open(BytesIO(response.content))
        
        # 转换为RGB模式（如果是RGBA或其他模式）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # 计算新尺寸（保持宽高比）
        original_width, original_height = img.size
        ratio = TARGET_WIDTH / original_width
        new_height = int(original_height * ratio)
        
        # 调整尺寸
        img_resized = img.resize((TARGET_WIDTH, new_height), Image.Resampling.LANCZOS)
        
        # 保存为PNG
        filename = f"Screen_{index:03d}.png"
        filepath = os.path.join(output_path, filename)
        img_resized.save(filepath, 'PNG', optimize=True)
        
        print(f"  [OK] 已保存: {filename} ({TARGET_WIDTH}x{new_height})")
        return True
        
    except Exception as e:
        print(f"  [X] 下载失败: {e}")
        return False


def main():
    print("=" * 50)
    print("ScreensDesign 截图下载工具")
    print("=" * 50)
    
    # 创建输出文件夹
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, OUTPUT_FOLDER)
    os.makedirs(output_path, exist_ok=True)
    print(f"输出目录: {output_path}")
    
    # 连接到 Chrome
    driver = connect_to_chrome()
    if not driver:
        return
    
    try:
        # 检查当前页面
        current_url = driver.current_url
        print(f"当前页面: {current_url}")
        
        if "screensdesign.com" not in current_url:
            print(f"\n正在导航到目标页面...")
            driver.get(TARGET_URL)
            time.sleep(3)
        
        # 滚动加载所有图片
        scroll_to_load_all_images(driver)
        
        # 获取截图URL
        image_urls = get_screenshot_urls(driver)
        
        if not image_urls:
            print("未找到截图，请检查页面是否正确加载或会员是否已登录")
            
            # 打印页面源码以便调试
            print("\n正在保存页面源码以便调试...")
            with open(os.path.join(output_path, "page_source.html"), "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("已保存到 page_source.html")
            return
        
        # 下载并处理图片
        print(f"\n开始下载 {len(image_urls)} 张截图...")
        success_count = 0
        
        for i, url in enumerate(image_urls, 1):
            print(f"\n[{i}/{len(image_urls)}] 处理中...")
            if download_and_process_image(url, output_path, i):
                success_count += 1
        
        print("\n" + "=" * 50)
        print(f"完成！成功下载 {success_count}/{len(image_urls)} 张截图")
        print(f"保存位置: {output_path}")
        print("=" * 50)
        
    except Exception as e:
        print(f"发生错误: {e}")
    
    # 注意：不要关闭 driver，因为是用户的浏览器窗口


if __name__ == "__main__":
    main()
