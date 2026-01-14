"""
Onboarding 相关 API
- 获取/设置 Onboarding 范围
- 获取/设置检查状态
"""
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..config import settings

router = APIRouter()


class OnboardingRange(BaseModel):
    """Onboarding 范围"""
    start: int = -1
    end: int = -1
    updated_at: Optional[str] = None


class CheckStatus(BaseModel):
    """检查状态"""
    checked: bool = False
    checked_at: Optional[str] = None
    screen_count: int = 0


class OnboardingRangeUpdate(BaseModel):
    """更新 Onboarding 范围请求"""
    start: int
    end: int


class CheckStatusUpdate(BaseModel):
    """更新检查状态请求"""
    checked: bool


def get_project_path(project_name: str) -> str:
    """获取项目路径"""
    if project_name.startswith("downloads_2024/"):
        return os.path.join(settings.downloads_2024_dir, project_name.replace("downloads_2024/", ""))
    return os.path.join(settings.projects_dir, project_name)


@router.get("/onboarding-range/{project_name:path}", response_model=OnboardingRange)
async def get_onboarding_range(project_name: str):
    """获取项目的 Onboarding 范围"""
    project_path = get_project_path(project_name)
    range_file = os.path.join(project_path, "onboarding_range.json")
    
    if os.path.exists(range_file):
        with open(range_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return OnboardingRange(**data)
    
    return OnboardingRange(start=-1, end=-1)


@router.post("/onboarding-range/{project_name:path}")
async def save_onboarding_range(project_name: str, data: OnboardingRangeUpdate):
    """保存项目的 Onboarding 范围"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    range_file = os.path.join(project_path, "onboarding_range.json")
    backup_dir = os.path.join(project_path, "backups")
    
    try:
        # 1. 如果旧文件存在，先备份
        if os.path.exists(range_file):
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(
                backup_dir, 
                f"onboarding_range_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            import shutil
            shutil.copy(range_file, backup_file)
            
            # 只保留最近 10 个备份
            backups = sorted([
                f for f in os.listdir(backup_dir) 
                if f.startswith("onboarding_range_")
            ], reverse=True)
            for old_backup in backups[10:]:
                os.remove(os.path.join(backup_dir, old_backup))
        
        # 2. 保存新数据
        range_data = {
            "start": data.start,
            "end": data.end,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(range_file, "w", encoding="utf-8") as f:
            json.dump(range_data, f, ensure_ascii=False, indent=2)
        
        # 3. 验证写入成功
        with open(range_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        
        if saved_data.get("start") != data.start or saved_data.get("end") != data.end:
            raise Exception("数据验证失败：写入的数据与预期不符")
        
        return {"success": True, "data": range_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-status/{project_name:path}", response_model=CheckStatus)
async def get_check_status(project_name: str):
    """获取项目的检查状态"""
    project_path = get_project_path(project_name)
    status_file = os.path.join(project_path, "check_status.json")
    
    if os.path.exists(status_file):
        with open(status_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CheckStatus(**data)
    
    return CheckStatus(checked=False)


@router.post("/check-status/{project_name:path}")
async def set_check_status(project_name: str, data: CheckStatusUpdate):
    """设置项目的检查状态"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    status_file = os.path.join(project_path, "check_status.json")
    
    # 获取当前截图数量
    is_downloads_2024 = project_name.startswith("downloads_2024/")
    if is_downloads_2024:
        screens_path = project_path
    else:
        screens_path = os.path.join(project_path, "Screens")
    
    screen_count = 0
    if os.path.exists(screens_path):
        screen_count = len([f for f in os.listdir(screens_path) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
    
    try:
        status_data = {
            "checked": data.checked,
            "checked_at": datetime.now().isoformat() if data.checked else None,
            "screen_count": screen_count
        }
        
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "data": status_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-onboarding")
async def get_all_onboarding():
    """获取所有项目的 Onboarding 数据"""
    results = []
    
    # 遍历 projects 目录
    if os.path.exists(settings.projects_dir):
        for project_name in os.listdir(settings.projects_dir):
            project_path = os.path.join(settings.projects_dir, project_name)
            if os.path.isdir(project_path):
                range_file = os.path.join(project_path, "onboarding_range.json")
                if os.path.exists(range_file):
                    with open(range_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("start", -1) >= 0:
                        results.append({
                            "project": project_name,
                            "source": "projects",
                            **data
                        })
    
    # 遍历 downloads_2024 目录
    if os.path.exists(settings.downloads_2024_dir):
        for app_name in os.listdir(settings.downloads_2024_dir):
            app_path = os.path.join(settings.downloads_2024_dir, app_name)
            if os.path.isdir(app_path):
                screens_path = os.path.join(app_path, "screenshots")
                if os.path.exists(screens_path):
                    range_file = os.path.join(screens_path, "onboarding_range.json")
                    if os.path.exists(range_file):
                        with open(range_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if data.get("start", -1) >= 0:
                            results.append({
                                "project": f"downloads_2024/{app_name}/screenshots",
                                "source": "downloads_2024",
                                **data
                            })
    
    return {"total": len(results), "items": results}






