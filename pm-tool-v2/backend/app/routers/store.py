"""
App Store 商店对比相关 API
- 获取商店对比数据
- 获取单个应用商店信息
- 获取商店截图
"""
import os
import json
import csv
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional

from ..config import settings

router = APIRouter()


def get_project_path(project_name: str) -> str:
    """获取项目路径"""
    if project_name.startswith("downloads_2024/"):
        return os.path.join(str(settings.downloads_2024_dir), project_name.replace("downloads_2024/", ""))
    return os.path.join(str(settings.projects_dir), project_name)


@router.get("/store-comparison")
async def get_store_comparison():
    """获取所有 APP 的商城对比数据"""
    downloads_dir = str(settings.downloads_2024_dir)
    csv_data_dir = str(settings.csv_data_dir)
    comparison_file = os.path.join(downloads_dir, "store_comparison.json")
    csv_file = os.path.join(csv_data_dir, "top30_must_study.csv")
    
    if not os.path.exists(comparison_file):
        # 如果没有预生成的数据，则扫描目录生成
        apps = []
        
        if os.path.exists(downloads_dir):
            for name in sorted(os.listdir(downloads_dir)):
                app_path = os.path.join(downloads_dir, name)
                if not os.path.isdir(app_path):
                    continue
                
                # 读取 store_info.json
                info_file = os.path.join(app_path, "store_info.json")
                if os.path.exists(info_file):
                    with open(info_file, "r", encoding="utf-8") as f:
                        info = json.load(f)
                    info["folder_name"] = name
                    apps.append(info)
                else:
                    # 基础信息
                    apps.append({
                        "folder_name": name,
                        "name": name.replace("_", " ").title(),
                        "track_name": name.replace("_", " ").title(),
                    })
        
        return {"apps": apps, "total": len(apps)}
    
    try:
        with open(comparison_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 读取竞品 CSV 数据进行合并
        csv_data = {}
        if os.path.exists(csv_file):
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    app_name = row.get("app_name", "")
                    csv_data[app_name.lower()] = {
                        "revenue": int(float(row.get("revenue", 0) or 0)),
                        "downloads": int(float(row.get("downloads", 0) or 0)),
                        "arpu": float(row.get("arpu", 0) or 0),
                        "growth_rate": float(row.get("growth_rate", 0) or 0),
                        "dau": int(float(row.get("dau", 0) or 0)),
                        "priority": row.get("priority", "P1"),
                        "csv_rank": int(row.get("rank", 99) or 99),
                        "developer": row.get("publisher", "")
                    }
        
        # 合并数据
        for app in data.get("apps", []):
            # 添加 folder_name（前端需要）
            if "folder_name" not in app:
                app["folder_name"] = app.get("name", "")
            
            track_name = (app.get("track_name") or "").lower()
            app_name = (app.get("name") or "").lower()
            
            matched_data = None
            for csv_key, csv_val in csv_data.items():
                csv_key_clean = csv_key.lower()
                if (csv_key_clean == track_name or 
                    csv_key_clean in track_name or 
                    track_name in csv_key_clean):
                    matched_data = csv_val
                    break
            
            if matched_data:
                app.update(matched_data)
            else:
                app.setdefault("revenue", 0)
                app.setdefault("downloads", 0)
        
        # 按收入排序
        data["apps"].sort(key=lambda x: x.get("revenue", 0), reverse=True)
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/store-info/{project_name:path}")
async def get_store_info(project_name: str):
    """获取单个 APP 的商城详细信息"""
    downloads_2024 = str(settings.downloads_2024_dir)
    if project_name.startswith("downloads_2024/"):
        app_name = project_name.replace("downloads_2024/", "")
        project_path = os.path.join(downloads_2024, app_name)
    else:
        project_path = os.path.join(downloads_2024, project_name)
    
    info_file = os.path.join(project_path, "store_info.json")
    store_dir = os.path.join(project_path, "store")
    
    if not os.path.exists(info_file):
        # 返回基础信息
        return {
            "name": project_name.replace("_", " ").title(),
            "folder_name": project_name,
            "screenshots": [],
        }
    
    try:
        with open(info_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 添加商城截图列表
        if os.path.exists(store_dir):
            screenshots = sorted([f for f in os.listdir(store_dir) if f.startswith("screenshot_")])
            data["store_screenshots"] = screenshots
        else:
            data["store_screenshots"] = []
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/store-screenshot/{project_name:path}/{filename}")
async def get_store_screenshot(project_name: str, filename: str):
    """获取商店截图"""
    downloads_2024 = str(settings.downloads_2024_dir)
    if project_name.startswith("downloads_2024/"):
        app_name = project_name.replace("downloads_2024/", "")
        project_path = os.path.join(downloads_2024, app_name)
    else:
        project_path = os.path.join(downloads_2024, project_name)
    
    store_dir = os.path.join(project_path, "store")
    file_path = os.path.join(store_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="截图不存在")
    
    return FileResponse(file_path)


@router.get("/store-icon/{project_name:path}")
async def get_store_icon(project_name: str):
    """获取应用图标"""
    downloads_2024 = str(settings.downloads_2024_dir)
    if project_name.startswith("downloads_2024/"):
        app_name = project_name.replace("downloads_2024/", "")
        project_path = os.path.join(downloads_2024, app_name)
    else:
        project_path = os.path.join(downloads_2024, project_name)
    
    # 尝试多个可能的图标文件名
    icon_names = ["icon.png", "icon.jpg", "app_icon.png", "store_icon.png"]
    
    for icon_name in icon_names:
        icon_path = os.path.join(project_path, icon_name)
        if os.path.exists(icon_path):
            return FileResponse(icon_path)
    
    # 尝试在 store 目录中查找
    store_dir = os.path.join(project_path, "store")
    if os.path.exists(store_dir):
        for icon_name in icon_names:
            icon_path = os.path.join(store_dir, icon_name)
            if os.path.exists(icon_path):
                return FileResponse(icon_path)
    
    raise HTTPException(status_code=404, detail="图标不存在")
