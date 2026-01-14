"""
从 App Store 下载应用 Logo
使用 iTunes Search API
"""
import os
import sys
import json
import requests
from pathlib import Path
from time import sleep

# 应用名称到 App Store 搜索词的映射
APP_SEARCH_TERMS = {
    "Fitbit": "Fitbit",
    "Yazio": "Yazio Calorie Counter",
    "LoseIt": "Lose It! Calorie Counter",
    "MacroFactor": "MacroFactor",
    "MyFitnessPal": "MyFitnessPal",
    "Noom": "Noom Weight",
    "Peloton": "Peloton Fitness",
    "Runna": "Runna Running",
    "Strava": "Strava Run Ride",
    "AllTrails": "AllTrails Hike Bike Run",
    "Flo": "Flo Period Pregnancy",
    "Cal_AI": "Cal AI Calorie Counter",
    "WeightWatchers": "WeightWatchers Weight Loss",
    "Headspace": "Headspace Meditation",
    "Calm": "Calm Sleep Meditation",
    "LADDER": "LADDER Workout",
}

def search_app(app_name: str) -> dict | None:
    """通过 iTunes Search API 搜索应用"""
    search_term = APP_SEARCH_TERMS.get(app_name, app_name)
    url = f"https://itunes.apple.com/search?term={search_term}&entity=software&country=us&limit=5"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("resultCount", 0) > 0:
            # 返回第一个结果
            return data["results"][0]
    except Exception as e:
        print(f"  [ERROR] Search failed: {e}")
    
    return None

def download_logo(url: str, save_path: Path) -> bool:
    """下载 logo 图片"""
    try:
        # 获取高分辨率图标 (512x512)
        high_res_url = url.replace("100x100", "512x512")
        
        response = requests.get(high_res_url, timeout=15)
        response.raise_for_status()
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"  [ERROR] Download failed: {e}")
        return False

def main():
    # Logo 保存目录
    script_dir = Path(__file__).parent
    logos_dir = script_dir.parent / "data" / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("  App Store Logo Downloader")
    print("=" * 50)
    print(f"Save directory: {logos_dir}")
    print("")
    
    # 获取项目列表
    apps = list(APP_SEARCH_TERMS.keys())
    
    success_count = 0
    fail_count = 0
    
    for i, app_name in enumerate(apps, 1):
        print(f"[{i}/{len(apps)}] {app_name}...")
        
        logo_path = logos_dir / f"{app_name}.png"
        
        # 检查是否已存在
        if logo_path.exists():
            print(f"  [SKIP] Already exists")
            success_count += 1
            continue
        
        # 搜索应用
        app_info = search_app(app_name)
        
        if not app_info:
            print(f"  [FAIL] App not found")
            fail_count += 1
            continue
        
        # 获取图标 URL
        icon_url = app_info.get("artworkUrl100")
        if not icon_url:
            print(f"  [FAIL] No icon URL")
            fail_count += 1
            continue
        
        # 下载图标
        if download_logo(icon_url, logo_path):
            print(f"  [OK] Saved to {logo_path.name}")
            success_count += 1
        else:
            fail_count += 1
        
        # 避免请求过快
        sleep(0.5)
    
    print("")
    print("=" * 50)
    print(f"  Done! Success: {success_count}, Failed: {fail_count}")
    print(f"  Logos saved to: {logos_dir}")
    print("=" * 50)

if __name__ == "__main__":
    main()
