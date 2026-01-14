"""
导出和历史记录相关 API
- 导出项目数据
- 获取操作历史
"""
import os
import json
import zipfile
from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, Any, List, Optional

from ..config import settings

router = APIRouter()

# 历史记录存储
HISTORY_FILE = os.path.join(settings.base_dir, "history.json")


def get_project_path(project_name: str) -> str:
    """获取项目路径"""
    if project_name.startswith("downloads_2024/"):
        return os.path.join(settings.downloads_2024_dir, project_name.replace("downloads_2024/", ""))
    return os.path.join(settings.projects_dir, project_name)


def load_history() -> List[Dict[str, Any]]:
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_history(history: List[Dict[str, Any]]):
    """保存历史记录"""
    # 只保留最近 100 条
    history = history[-100:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_history(action: str, description: str, project: Optional[str] = None):
    """添加历史记录"""
    history = load_history()
    history.append({
        "action": action,
        "description": description,
        "project": project,
        "timestamp": datetime.now().isoformat()
    })
    save_history(history)


@router.get("/history")
async def get_history(limit: int = 50):
    """获取操作历史"""
    history = load_history()
    return {
        "total": len(history),
        "items": list(reversed(history[-limit:]))
    }


@router.get("/export/{project_name:path}/{format_type}")
async def export_project(project_name: str, format_type: str):
    """导出项目数据"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    if format_type == "json":
        # 导出为 JSON
        return await export_json(project_name, project_path)
    elif format_type == "zip":
        # 导出为 ZIP（包含截图）
        return await export_zip(project_name, project_path)
    else:
        raise HTTPException(status_code=400, detail=f"不支持的格式: {format_type}")


async def export_json(project_name: str, project_path: str) -> JSONResponse:
    """导出为 JSON 格式"""
    data = {
        "project": project_name,
        "exported_at": datetime.now().isoformat(),
        "screenshots": [],
        "onboarding_range": None,
        "classification": {},
    }
    
    # 获取截图列表
    is_downloads_2024 = project_name.startswith("downloads_2024/")
    if is_downloads_2024:
        screens_dir = project_path
    else:
        screens_dir = os.path.join(project_path, "Screens")
        if not os.path.exists(screens_dir):
            screens_dir = os.path.join(project_path, "screens")
    
    if os.path.exists(screens_dir):
        screenshots = sorted([
            f for f in os.listdir(screens_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        ])
        data["screenshots"] = screenshots
    
    # 获取 Onboarding 范围
    range_file = os.path.join(project_path, "onboarding_range.json")
    if os.path.exists(range_file):
        with open(range_file, "r", encoding="utf-8") as f:
            data["onboarding_range"] = json.load(f)
    
    # 获取分类数据
    classification_file = os.path.join(project_path, "classification.json")
    ai_file = os.path.join(project_path, "ai_analysis.json")
    
    if os.path.exists(classification_file):
        with open(classification_file, "r", encoding="utf-8") as f:
            data["classification"] = json.load(f)
    elif os.path.exists(ai_file):
        with open(ai_file, "r", encoding="utf-8") as f:
            ai_data = json.load(f)
            data["classification"] = ai_data.get("results", {})
    
    # 添加历史记录
    add_history("export", f"导出 {project_name} 为 JSON", project_name)
    
    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": f'attachment; filename="{project_name.replace("/", "_")}_export.json"'
        }
    )


async def export_zip(project_name: str, project_path: str) -> StreamingResponse:
    """导出为 ZIP 格式（包含截图）"""
    is_downloads_2024 = project_name.startswith("downloads_2024/")
    if is_downloads_2024:
        screens_dir = project_path
    else:
        screens_dir = os.path.join(project_path, "Screens")
        if not os.path.exists(screens_dir):
            screens_dir = os.path.join(project_path, "screens")
    
    # 创建内存中的 ZIP
    buffer = BytesIO()
    
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 添加截图
        if os.path.exists(screens_dir):
            for filename in os.listdir(screens_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    file_path = os.path.join(screens_dir, filename)
                    zf.write(file_path, f"screenshots/{filename}")
        
        # 添加元数据文件
        metadata_files = [
            "onboarding_range.json",
            "classification.json",
            "ai_analysis.json",
            "check_status.json",
            "sort_order.json",
        ]
        
        for meta_file in metadata_files:
            meta_path = os.path.join(project_path, meta_file)
            if os.path.exists(meta_path):
                zf.write(meta_path, f"metadata/{meta_file}")
        
        # 添加导出信息
        export_info = {
            "project": project_name,
            "exported_at": datetime.now().isoformat(),
            "source": "PM Tool v2"
        }
        zf.writestr("export_info.json", json.dumps(export_info, indent=2))
    
    buffer.seek(0)
    
    # 添加历史记录
    add_history("export", f"导出 {project_name} 为 ZIP", project_name)
    
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{project_name.replace("/", "_")}_export.zip"'
        }
    )


@router.post("/history/clear")
async def clear_history():
    """清空历史记录"""
    save_history([])
    return {"success": True, "message": "历史记录已清空"}
