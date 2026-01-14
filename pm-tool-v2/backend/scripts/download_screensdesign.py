"""
ScreensDesign 截图下载脚本
从 screensdesign.com 下载应用截图

使用方法:
    python download_screensdesign.py --url "https://screensdesign.com/apps/yazio-calorie-counter-diet/?ts=0&vt=1&id=869" --output "Yazio"
    python download_screensdesign.py --app "yazio"  # 自动搜索并下载
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("请先安装 playwright: pip install playwright && playwright install chromium")
    sys.exit(1)


def get_data_dir():
    """获取数据目录"""
    return Path(__file__).parent.parent / "data"


def download_image(url: str, save_path: Path, headers: dict = None):
    """下载单张图片"""
    try:
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://screensdesign.com/",
            }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"  [ERROR] Download failed: {url} - {e}")
        return False


def download_from_screensdesign(url: str, output_name: str = None, output_dir: Path = None):
    """
    从 ScreensDesign 下载应用截图
    
    Args:
        url: ScreensDesign 应用页面 URL
        output_name: 输出文件夹名称（默认从 URL 提取）
        output_dir: 输出目录（默认为 data/downloads_2024）
    """
    
    # 确定输出目录
    if output_dir is None:
        output_dir = get_data_dir() / "downloads_2024"
    
    # 从 URL 提取应用名称
    if output_name is None:
        path_parts = urlparse(url).path.strip("/").split("/")
        if len(path_parts) >= 2:
            output_name = path_parts[1]  # apps/xxx -> xxx
        else:
            output_name = "unknown_app"
    
    # 创建输出目录
    app_dir = output_dir / output_name
    screenshots_dir = app_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[APP] Starting download: {output_name}")
    print(f"[DIR] Save to: {screenshots_dir}")
    print(f"[URL] Source: {url}")
    print()
    
    downloaded = []
    failed = []
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("[WEB] Loading page...")
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        # 等待页面完全加载
        time.sleep(3)
        
        # 滚动页面以加载所有图片
        print("[SCROLL] Loading all images...")
        for _ in range(10):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(0.5)
        
        # 滚动回顶部
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        
        # 查找所有截图图片
        # ScreensDesign 通常使用 img 标签展示截图
        image_urls = set()
        
        # 尝试多种选择器来找到截图
        selectors = [
            "img[src*='screenshot']",
            "img[src*='screens']",
            "img[data-src*='screenshot']",
            "img[data-src*='screens']",
            ".screenshot img",
            ".screens img",
            "[class*='screen'] img",
            "[class*='screenshot'] img",
            "main img",
            "article img",
            ".gallery img",
            "[class*='gallery'] img",
            "[class*='slider'] img",
            "[class*='carousel'] img",
        ]
        
        for selector in selectors:
            try:
                images = page.query_selector_all(selector)
                for img in images:
                    # 获取 src 或 data-src
                    src = img.get_attribute("src") or img.get_attribute("data-src")
                    if src:
                        # 过滤掉小图标和 placeholder
                        if any(x in src.lower() for x in ["icon", "logo", "avatar", "placeholder", "loading", "spinner"]):
                            continue
                        # 确保是完整 URL
                        if src.startswith("//"):
                            src = "https:" + src
                        elif src.startswith("/"):
                            src = urljoin(url, src)
                        elif not src.startswith("http"):
                            src = urljoin(url, src)
                        image_urls.add(src)
            except Exception as e:
                pass
        
        # 也尝试获取背景图片
        try:
            bg_images = page.evaluate("""
                () => {
                    const urls = [];
                    document.querySelectorAll('*').forEach(el => {
                        const bg = getComputedStyle(el).backgroundImage;
                        if (bg && bg !== 'none') {
                            const match = bg.match(/url\\(['"]?([^'"\\)]+)['"]?\\)/);
                            if (match) urls.push(match[1]);
                        }
                    });
                    return urls;
                }
            """)
            for bg_url in bg_images:
                if any(x in bg_url.lower() for x in ["screenshot", "screen", "mobile", "app"]):
                    if bg_url.startswith("//"):
                        bg_url = "https:" + bg_url
                    elif bg_url.startswith("/"):
                        bg_url = urljoin(url, bg_url)
                    image_urls.add(bg_url)
        except Exception:
            pass
        
        print(f"[FOUND] {len(image_urls)} images")
        
        if not image_urls:
            # 如果没找到，尝试获取页面上所有较大的图片
            print("[WARN] No screenshots found, trying to get all large images...")
            all_images = page.query_selector_all("img")
            for img in all_images:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src:
                    # 获取图片尺寸
                    try:
                        box = img.bounding_box()
                        if box and box["width"] > 100 and box["height"] > 100:
                            if src.startswith("//"):
                                src = "https:" + src
                            elif src.startswith("/"):
                                src = urljoin(url, src)
                            elif not src.startswith("http"):
                                src = urljoin(url, src)
                            image_urls.add(src)
                    except:
                        pass
            
            print(f"[FOUND] {len(image_urls)} large images")
        
        browser.close()
    
    # 下载所有图片
    print()
    print("[DOWNLOAD] Starting downloads...")
    
    for i, img_url in enumerate(sorted(image_urls), 1):
        # 生成文件名
        ext = Path(urlparse(img_url).path).suffix or ".png"
        if ext.lower() not in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
            ext = ".png"
        
        filename = f"screenshot_{i:02d}{ext}"
        save_path = screenshots_dir / filename
        
        print(f"  [{i}/{len(image_urls)}] 下载: {filename}")
        
        if download_image(img_url, save_path):
            downloaded.append(filename)
            print(f"       [OK] Success")
        else:
            failed.append(img_url)
    
    # 总结
    print()
    print("=" * 50)
    print(f"[DONE] Download complete!")
    print(f"   Success: {len(downloaded)}")
    print(f"   Failed: {len(failed)}")
    print(f"   Location: {screenshots_dir}")
    
    return {
        "app_name": output_name,
        "output_dir": str(screenshots_dir),
        "downloaded": downloaded,
        "failed": failed,
    }


def search_and_download(app_name: str, output_dir: Path = None):
    """
    搜索并下载应用截图
    
    Args:
        app_name: 应用名称（如 "yazio", "calm", "headspace"）
        output_dir: 输出目录
    """
    # 构建搜索 URL
    search_term = app_name.lower().replace(" ", "-")
    
    # 常见应用的直接 URL 映射
    known_apps = {
        "yazio": "https://screensdesign.com/apps/yazio-calorie-counter-diet/",
        "calm": "https://screensdesign.com/apps/calm/",
        "headspace": "https://screensdesign.com/apps/headspace-meditation-sleep/",
        "myfitnesspal": "https://screensdesign.com/apps/myfitnesspal-calorie-counter/",
        "strava": "https://screensdesign.com/apps/strava-run-ride-swim/",
        "peloton": "https://screensdesign.com/apps/peloton-fitness-workouts/",
        "fitbit": "https://screensdesign.com/apps/fitbit-health-fitness/",
        "noom": "https://screensdesign.com/apps/noom-healthy-weight-loss/",
        "loseit": "https://screensdesign.com/apps/lose-it-calorie-counter/",
        "flo": "https://screensdesign.com/apps/flo-period-ovulation-tracker/",
    }
    
    if search_term in known_apps:
        url = known_apps[search_term]
        print(f"[OK] Found known app: {app_name}")
    else:
        # 尝试构建 URL
        url = f"https://screensdesign.com/apps/{search_term}/"
        print(f"[TRY] Accessing: {url}")
    
    return download_from_screensdesign(url, app_name, output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="从 ScreensDesign 下载应用截图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 从 URL 下载
    python download_screensdesign.py --url "https://screensdesign.com/apps/yazio-calorie-counter-diet/"
    
    # 搜索并下载
    python download_screensdesign.py --app yazio
    
    # 指定输出目录
    python download_screensdesign.py --app calm --output ./my_screenshots
        """
    )
    
    parser.add_argument("--url", "-u", type=str, help="ScreensDesign 应用页面 URL")
    parser.add_argument("--app", "-a", type=str, help="应用名称（自动搜索）")
    parser.add_argument("--output", "-o", type=str, help="输出目录")
    parser.add_argument("--name", "-n", type=str, help="输出文件夹名称")
    
    args = parser.parse_args()
    
    # 确定输出目录
    output_dir = Path(args.output) if args.output else None
    
    if args.url:
        download_from_screensdesign(args.url, args.name, output_dir)
    elif args.app:
        search_and_download(args.app, output_dir)
    else:
        # 默认下载 Yazio
        print("[DEFAULT] Downloading Yazio screenshots...")
        url = "https://screensdesign.com/apps/yazio-calorie-counter-diet/?ts=0&vt=1&id=869"
        download_from_screensdesign(url, "Yazio", output_dir)


if __name__ == "__main__":
    main()


