"""
截图 API 路由
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional

from app.config import settings
from app.models.screenshot import ScreenshotListResponse
from app.services.screenshot_service import (
    get_project_screenshots,
    get_classification_stats,
    get_screenshot_path,
    get_thumbnail_path,
)


router = APIRouter()


@router.get("/project-screenshots/{project_name:path}", response_model=ScreenshotListResponse)
async def list_screenshots(
    project_name: str,
    stage: Optional[str] = Query(None, description="过滤 Stage"),
    module: Optional[str] = Query(None, description="过滤 Module"),
) -> ScreenshotListResponse:
    """
    获取项目的截图列表
    
    - **project_name**: 项目名称
    - **stage**: 过滤 Stage (Onboarding, Core, Monetization)
    - **module**: 过滤 Module
    """
    screenshots = get_project_screenshots(project_name)
    
    if not screenshots:
        raise HTTPException(status_code=404, detail=f"项目不存在或没有截图: {project_name}")
    
    # 过滤
    if stage:
        screenshots = [
            s for s in screenshots 
            if s.classification and s.classification.stage == stage
        ]
    
    if module:
        screenshots = [
            s for s in screenshots 
            if s.classification and s.classification.module == module
        ]
    
    # 获取统计
    all_screenshots = get_project_screenshots(project_name)
    stages, modules = get_classification_stats(all_screenshots)
    
    return ScreenshotListResponse(
        project=project_name,
        screenshots=screenshots,
        total=len(screenshots),
        stages=stages,
        modules=modules,
    )


@router.get("/screenshots/{project_name:path}/{filename}")
async def get_screenshot(project_name: str, filename: str):
    """
    获取截图原图
    """
    file_path = get_screenshot_path(project_name, filename)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="截图不存在")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
        }
    )


@router.get("/thumbnails/{project_name:path}/{filename}")
async def get_thumbnail(
    project_name: str, 
    filename: str,
    size: str = Query("small", description="缩略图尺寸: small, medium, large"),
):
    """
    获取截图缩略图
    
    - **size**: small (120px), medium (240px), large (480px)
    """
    if size not in ["small", "medium", "large"]:
        size = "small"
    
    file_path = get_thumbnail_path(project_name, filename, size)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="缩略图不存在")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=3600",
        }
    )


@router.get("/logo/{app_name}")
async def get_app_logo(app_name: str):
    """
    获取应用 Logo
    
    - **app_name**: 应用名称（如 Fitbit, Yazio 等）
    """
    logos_dir = settings.data_dir / "logos"
    logo_path = logos_dir / f"{app_name}.png"
    
    if not logo_path.exists():
        raise HTTPException(status_code=404, detail=f"Logo not found: {app_name}")
    
    return FileResponse(
        logo_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=604800",  # 缓存 7 天
        }
    )
