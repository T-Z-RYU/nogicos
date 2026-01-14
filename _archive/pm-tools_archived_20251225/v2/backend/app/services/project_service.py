"""
项目服务 - 业务逻辑
"""
import json
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.project import Project


# Mobbin 来源的 App 列表
MOBBIN_APPS = {"Cal_AI", "Fitbit"}


def get_all_projects() -> list[Project]:
    """获取所有项目（仅从 downloads_2024 目录加载）"""
    projects: list[Project] = []
    
    # 仅扫描 downloads_2024 目录（新数据）
    if settings.downloads_dir.exists():
        for item in settings.downloads_dir.iterdir():
            if item.is_dir() and "_backup" not in item.name:
                project = _load_project_from_downloads_dir(item)
                if project:
                    # 显示所有项目，包括空项目（screen_count = 0）
                    projects.append(project)
    
    # 按截图数量排序（空项目排在最后）
    projects.sort(key=lambda x: (-x.screen_count if x.screen_count > 0 else float('inf')))
    
    return projects


def _load_project_from_downloads_dir(path: Path) -> Optional[Project]:
    """从 downloads_2024 目录加载项目"""
    name = path.name
    
    # 计算截图数量（支持多种格式和 screenshots 子目录）
    screen_count = 0
    # 根目录的截图
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
        screen_count += len(list(path.glob(ext)))
    # screenshots 子目录的截图
    screenshots_dir = path / "screenshots"
    if screenshots_dir.exists():
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
            screen_count += len(list(screenshots_dir.glob(ext)))
    
    # 根据来源设置数据来源和颜色（显示名只用项目名，不带前缀）
    if name in MOBBIN_APPS:
        data_source = "Mobbin"
        color = "#8B5CF6"
    else:
        data_source = "SD"
        color = "#10B981"
    
    # 显示名只用项目名，不带 [SD] 或 [Mobbin] 前缀
    display_name = name
    
    # 读取检查状态
    checked, checked_at = _load_check_status(path)
    
    # 读取 Onboarding 范围
    ob_start, ob_end = _load_onboarding_range(path)
    
    return Project(
        name=f"downloads_2024/{name}",
        display_name=display_name,
        screen_count=screen_count,
        source="downloads_2024",
        data_source=data_source,
        color=color,
        initial=name[0].upper() if name else "?",
        category="Health & Fitness",
        checked=checked,
        checked_at=checked_at,
        onboarding_start=ob_start,
        onboarding_end=ob_end,
    )


def _load_check_status(path: Path) -> tuple[bool, Optional[str]]:
    """加载检查状态"""
    check_file = path / "check_status.json"
    if check_file.exists():
        try:
            with open(check_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("checked", False), data.get("checked_at")
        except:
            pass
    return False, None


def _load_onboarding_range(path: Path) -> tuple[int, int]:
    """加载 Onboarding 范围"""
    ob_file = path / "onboarding_range.json"
    if ob_file.exists():
        try:
            with open(ob_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("start", -1), data.get("end", -1)
        except:
            pass
    return -1, -1


def get_project_path(project_name: str) -> Path:
    """获取项目路径"""
    if project_name.startswith("downloads_2024/"):
        app_name = project_name.replace("downloads_2024/", "")
        return settings.downloads_dir / app_name
    return settings.projects_dir / project_name
