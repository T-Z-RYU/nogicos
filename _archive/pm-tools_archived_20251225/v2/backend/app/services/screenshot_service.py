"""
截图服务 - 业务逻辑
"""
import json
from pathlib import Path
from typing import Optional
from collections import Counter

from app.config import settings
from app.models.screenshot import Screenshot, Classification
from app.services.project_service import get_project_path


def get_project_screenshots(project_name: str) -> list[Screenshot]:
    """获取项目的所有截图"""
    project_path = get_project_path(project_name)
    
    if not project_path.exists():
        return []
    
    # 确定截图目录
    is_downloads = project_name.startswith("downloads_2024/")
    if is_downloads:
        screens_path = project_path
    else:
        screens_path = project_path / "Screens"
    
    if not screens_path.exists():
        return []
    
    # 加载分类数据
    classifications = _load_classifications(project_path)
    
    # 加载描述数据
    descriptions = _load_descriptions(project_path)
    
    # 获取截图列表（支持多种格式和 screenshots 子目录）
    image_files = []
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
    
    # 根目录截图
    for ext in extensions:
        image_files.extend(screens_path.glob(ext))
    
    # screenshots 子目录截图（仅对 downloads_2024）
    if is_downloads:
        screenshots_subdir = screens_path / "screenshots"
        if screenshots_subdir.exists():
            for ext in extensions:
                image_files.extend(screenshots_subdir.glob(ext))
    
    # 排序
    image_files = sorted(image_files, key=lambda x: x.name)
    
    screenshots: list[Screenshot] = []
    for idx, file_path in enumerate(image_files):
        filename = file_path.name
        # 标记来自 screenshots 子目录的文件
        is_subdir = "screenshots" in str(file_path.parent)
        actual_filename = f"screenshots/{filename}" if is_subdir else filename
        
        # 获取分类
        classification = None
        if filename in classifications:
            cls_data = classifications[filename]
            classification = Classification(
                stage=cls_data.get("stage"),
                module=cls_data.get("module"),
                feature=cls_data.get("feature"),
                page_role=cls_data.get("page_role"),
                screen_type=cls_data.get("screen_type"),
                confidence=cls_data.get("confidence", 0),
                manually_adjusted=cls_data.get("manually_adjusted", False),
            )
        
        screenshot = Screenshot(
            filename=actual_filename,
            index=idx + 1,
            classification=classification,
            description=descriptions.get(filename),
            url=f"/api/screenshots/{project_name}/{actual_filename}",
            thumb_url=f"/api/thumbnails/{project_name}/{actual_filename}",
        )
        screenshots.append(screenshot)
    
    return screenshots


def get_classification_stats(screenshots: list[Screenshot]) -> tuple[dict, dict]:
    """获取分类统计"""
    stages: Counter = Counter()
    modules: Counter = Counter()
    
    for s in screenshots:
        if s.classification:
            if s.classification.stage:
                stages[s.classification.stage] += 1
            if s.classification.module:
                modules[s.classification.module] += 1
    
    return dict(stages), dict(modules)


def _load_classifications(project_path: Path) -> dict:
    """加载分类数据"""
    ai_file = project_path / "ai_analysis.json"
    
    if ai_file.exists():
        try:
            with open(ai_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("results", {})
        except:
            pass
    
    return {}


def _load_descriptions(project_path: Path) -> dict:
    """加载描述数据"""
    desc_file = project_path / "descriptions.json"
    
    if desc_file.exists():
        try:
            with open(desc_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    
    return {}


def get_screenshot_path(project_name: str, filename: str) -> Optional[Path]:
    """获取截图文件路径"""
    project_path = get_project_path(project_name)
    
    is_downloads = project_name.startswith("downloads_2024/")
    if is_downloads:
        # 支持 screenshots 子目录路径（如 screenshots/xxx.webp）
        file_path = project_path / filename
    else:
        file_path = project_path / "Screens" / filename
    
    if file_path.exists():
        return file_path
    
    return None


def get_thumbnail_path(project_name: str, filename: str, size: str = "small") -> Optional[Path]:
    """获取缩略图路径，如果不存在则生成"""
    project_path = get_project_path(project_name)
    
    is_downloads = project_name.startswith("downloads_2024/")
    if is_downloads:
        # 支持 screenshots 子目录
        src_path = project_path / filename
        # 缩略图统一放在 thumbs_xxx 目录，使用扁平化文件名
        thumb_dir = project_path / f"thumbs_{size}"
        # 将路径中的 / 替换为 _ 以避免子目录问题
        thumb_filename = filename.replace("/", "_").replace("\\", "_")
        # 缩略图统一用 png 格式
        thumb_filename = Path(thumb_filename).stem + ".png"
    else:
        src_path = project_path / "Screens" / filename
        thumb_dir = project_path / f"Screens_thumbs_{size}"
        thumb_filename = Path(filename).stem + ".png"
    
    if not src_path.exists():
        return None
    
    # 确保缩略图目录存在
    thumb_dir.mkdir(exist_ok=True)
    
    thumb_path = thumb_dir / thumb_filename
    
    # 如果缩略图不存在或源文件更新，重新生成
    if not thumb_path.exists() or src_path.stat().st_mtime > thumb_path.stat().st_mtime:
        _generate_thumbnail(src_path, thumb_path, settings.thumb_sizes.get(size, 120))
    
    return thumb_path if thumb_path.exists() else None


def _generate_thumbnail(src_path: Path, thumb_path: Path, width: int):
    """生成缩略图"""
    try:
        from PIL import Image
        
        with Image.open(src_path) as img:
            ratio = width / img.width
            new_height = int(img.height * ratio)
            thumb = img.resize((width, new_height), Image.Resampling.LANCZOS)
            thumb.save(thumb_path, "PNG", optimize=True)
    except Exception as e:
        print(f"[ERROR] 生成缩略图失败: {e}")
