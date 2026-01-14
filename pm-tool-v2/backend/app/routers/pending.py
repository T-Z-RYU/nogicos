"""
待处理截图 API 路由 - 傲软投屏导入功能
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings


router = APIRouter()


# 配置路径
PENDING_DIR = settings.data_dir / "pending_screenshots"
CONFIG_DIR = settings.data_dir / "config"
APOWERSOFT_CONFIG_FILE = CONFIG_DIR / "apowersoft.json"

# 确保目录存在
PENDING_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


# ==================== 数据模型 ====================

class PendingScreenshot(BaseModel):
    """待处理截图"""
    filename: str
    path: str
    size: int
    created_at: str
    thumbnail_url: str


class PendingListResponse(BaseModel):
    """待处理截图列表响应"""
    screenshots: List[PendingScreenshot]
    total: int
    source_path: Optional[str] = None


class ApowersoftConfig(BaseModel):
    """傲软配置"""
    path: str
    auto_import: bool = False
    updated_at: Optional[str] = None


class ImportRequest(BaseModel):
    """导入请求"""
    project: str
    filename: str
    position: int = -1  # -1 表示添加到末尾


class ImportResponse(BaseModel):
    """导入响应"""
    success: bool
    message: str
    new_filename: Optional[str] = None
    position: Optional[int] = None


# ==================== 工具函数 ====================

def get_apowersoft_paths() -> List[str]:
    """获取可能的傲软投屏截图路径"""
    username = os.environ.get('USERNAME') or os.environ.get('USER') or 'User'
    user_profile = os.environ.get('USERPROFILE', f'C:\\Users\\{username}')
    
    possible_paths = [
        os.path.join(user_profile, 'Pictures', 'Apowersoft'),
        os.path.join(user_profile, 'Documents', 'Apowersoft'),
        os.path.join(user_profile, 'Pictures', 'ApowerMirror'),
        os.path.join(user_profile, 'Documents', 'ApowerMirror'),
        os.path.join(user_profile, 'Pictures', 'Screenshots'),
    ]
    return possible_paths


def detect_apowersoft_folder() -> Optional[str]:
    """自动检测傲软投屏截图文件夹"""
    # 先检查配置文件
    if APOWERSOFT_CONFIG_FILE.exists():
        with open(APOWERSOFT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if config.get('path') and os.path.exists(config['path']):
                return config['path']
    
    # 自动检测
    for path in get_apowersoft_paths():
        if os.path.exists(path):
            save_apowersoft_config(path)
            return path
    
    return None


def save_apowersoft_config(path: str, auto_import: bool = False):
    """保存傲软配置"""
    config = {
        'path': path,
        'auto_import': auto_import,
        'updated_at': datetime.now().isoformat()
    }
    with open(APOWERSOFT_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_pending_screenshots_from_apowersoft() -> List[dict]:
    """从傲软目录获取截图列表"""
    source_path = detect_apowersoft_folder()
    if not source_path or not os.path.exists(source_path):
        return []
    
    screenshots = []
    for filename in os.listdir(source_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(source_path, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                screenshots.append({
                    'filename': filename,
                    'path': file_path,
                    'size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'thumbnail_url': f'/api/pending-thumbnail/{filename}'
                })
    
    # 按创建时间排序（最新的在前）
    screenshots.sort(key=lambda x: x['created_at'], reverse=True)
    return screenshots


def get_project_screens_dir(project_name: str) -> Optional[Path]:
    """获取项目截图目录"""
    if project_name.startswith('downloads_2024/'):
        project_path = settings.downloads_dir / project_name.replace('downloads_2024/', '')
    else:
        project_path = settings.projects_dir / project_name
    
    # 检查可能的截图目录
    for subdir in ['', 'screens', 'Screens', 'screenshots']:
        screens_dir = project_path / subdir if subdir else project_path
        if screens_dir.exists():
            # 检查是否有图片文件（支持多种格式）
            has_images = (
                list(screens_dir.glob('*.png')) or
                list(screens_dir.glob('*.jpg')) or
                list(screens_dir.glob('*.jpeg')) or
                list(screens_dir.glob('*.webp'))
            )
            if has_images:
                return screens_dir
    
    # 如果没有找到带图片的目录，但项目目录存在，返回项目目录本身
    if project_path.exists():
        return project_path
    
    return None


def get_next_filename(screens_dir: Path, position: int = -1) -> tuple:
    """
    获取下一个可用的文件名
    返回: (新文件名, 实际插入位置)
    """
    import re
    
    # 获取现有文件（支持多种格式，不限制开头字符）
    existing = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
        existing.extend([
            f.name for f in screens_dir.glob(ext)
            if not f.name.startswith(('thumb', '_temp'))
        ])
    existing = sorted(existing)
    
    if not existing:
        return ('0001.png', 0)
    
    # 解析现有文件的数字
    numbers = []
    for f in existing:
        try:
            # 使用正则提取文件名中的所有数字
            name_without_ext = f.rsplit('.', 1)[0]
            # 查找最后出现的连续数字（如 screenshot_01 -> 01, 0001 -> 0001）
            matches = re.findall(r'\d+', name_without_ext)
            if matches:
                # 取最后一个数字序列
                num = int(matches[-1])
                numbers.append(num)
        except ValueError:
            pass
    
    total_files = len(existing)
    
    if position < 0 or position >= total_files:
        # 添加到末尾
        new_num = max(numbers) + 1 if numbers else 1
        return (f'{new_num:04d}.png', total_files)
    
    # 插入到指定位置
    new_num = max(numbers) + 1 if numbers else 1
    return (f'{new_num:04d}.png', position)


# ==================== API 路由 ====================

@router.get("/pending-screenshots", response_model=PendingListResponse)
async def list_pending_screenshots():
    """获取待处理截图列表"""
    screenshots = get_pending_screenshots_from_apowersoft()
    source_path = detect_apowersoft_folder()
    
    return PendingListResponse(
        screenshots=[PendingScreenshot(**s) for s in screenshots],
        total=len(screenshots),
        source_path=source_path
    )


@router.get("/pending-thumbnail/{filename}")
async def get_pending_thumbnail(filename: str):
    """获取待处理截图的缩略图"""
    source_path = detect_apowersoft_folder()
    if not source_path:
        raise HTTPException(status_code=404, detail="傲软目录未配置")
    
    file_path = os.path.join(source_path, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=60"}
    )


@router.post("/import-screenshot", response_model=ImportResponse)
async def import_screenshot(req: ImportRequest):
    """导入截图到项目"""
    source_path = detect_apowersoft_folder()
    if not source_path:
        raise HTTPException(status_code=400, detail="傲软目录未配置")
    
    # 源文件
    src_file = os.path.join(source_path, req.filename)
    if not os.path.exists(src_file):
        raise HTTPException(status_code=404, detail=f"文件不存在: {req.filename}")
    
    # 目标目录
    screens_dir = get_project_screens_dir(req.project)
    if not screens_dir:
        raise HTTPException(status_code=404, detail=f"项目不存在: {req.project}")
    
    try:
        # 获取新文件名
        new_filename, position = get_next_filename(screens_dir, req.position)
        dst_file = screens_dir / new_filename
        
        # 复制文件（保留原文件）
        shutil.copy2(src_file, dst_file)
        
        # 清理缩略图缓存
        thumb_dir = screens_dir / "thumbs_small"
        if thumb_dir.exists():
            shutil.rmtree(thumb_dir, ignore_errors=True)
        
        return ImportResponse(
            success=True,
            message=f"已导入到 {req.project}",
            new_filename=new_filename,
            position=position
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apowersoft-config")
async def get_config():
    """获取傲软配置"""
    if APOWERSOFT_CONFIG_FILE.exists():
        with open(APOWERSOFT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    
    # 尝试自动检测
    detected = detect_apowersoft_folder()
    return {
        'path': detected or '',
        'auto_import': False,
        'detected': detected is not None
    }


@router.post("/apowersoft-config")
async def save_config(config: ApowersoftConfig):
    """保存傲软配置"""
    if not os.path.exists(config.path):
        raise HTTPException(status_code=400, detail=f"路径不存在: {config.path}")
    
    save_apowersoft_config(config.path, config.auto_import)
    
    return {"success": True, "message": "配置已保存"}


@router.post("/clear-pending-screenshots")
async def clear_pending_screenshots():
    """清除傲软目录中的所有截图"""
    source_path = detect_apowersoft_folder()
    
    if not source_path or not os.path.exists(source_path):
        raise HTTPException(status_code=400, detail="傲软目录未配置或不存在")

    deleted = 0
    errors = []
    for filename in os.listdir(source_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(source_path, filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    deleted += 1
                except Exception as e:
                    errors.append(str(e))
                    print(f"删除文件失败: {file_path}, 错误: {e}")
    
    return {"success": True, "deleted": deleted, "message": f"已清除 {deleted} 张截图"}


@router.post("/import-from-apowersoft")
async def import_all_from_apowersoft():
    """从傲软目录导入所有截图到待处理区"""
    source_path = detect_apowersoft_folder()
    if not source_path:
        raise HTTPException(status_code=400, detail="傲软目录未配置")
    
    imported = 0
    for filename in os.listdir(source_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            src = os.path.join(source_path, filename)
            dst = PENDING_DIR / filename
            if os.path.isfile(src) and not dst.exists():
                shutil.copy2(src, dst)
                imported += 1
    
    return {"success": True, "imported": imported}


@router.post("/upload-screenshot")
async def upload_screenshot(
    project: str = Form(...),
    file: UploadFile = File(...)
):
    """
    上传截图到项目（支持从文件管理器拖入）
    """
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="无效的文件")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.webp']:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")
    
    # 获取项目目录
    screens_dir = get_project_screens_dir(project)
    if not screens_dir:
        # 如果项目目录不存在，尝试创建
        if project.startswith('downloads_2024/'):
            screens_dir = settings.downloads_dir / project.replace('downloads_2024/', '')
        else:
            screens_dir = settings.projects_dir / project
        screens_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 获取新文件名
        new_filename, position = get_next_filename(screens_dir, -1)
        # 保持原始扩展名
        new_filename = f"{new_filename.rsplit('.', 1)[0]}{ext}"
        dst_file = screens_dir / new_filename
        
        # 保存文件
        content = await file.read()
        with open(dst_file, 'wb') as f:
            f.write(content)
        
        # 清理缩略图缓存
        thumb_dir = screens_dir / "thumbs_small"
        if thumb_dir.exists():
            shutil.rmtree(thumb_dir, ignore_errors=True)
        
        return {
            "success": True,
            "message": f"已上传到 {project}",
            "new_filename": new_filename,
            "position": position
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

