"""
分类相关 API
- 获取分类法
- 更新截图分类
- 获取/更新标签库
"""
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from ..config import settings

router = APIRouter()


class ClassificationUpdate(BaseModel):
    """单个截图的分类更新"""
    stage: Optional[str] = None
    module: Optional[str] = None
    feature: Optional[str] = None
    page_role: Optional[str] = None


class UpdateClassificationRequest(BaseModel):
    """更新分类请求"""
    project: str
    changes: Dict[str, ClassificationUpdate]


def get_project_path(project_name: str) -> str:
    """获取项目路径"""
    if project_name.startswith("downloads_2024/"):
        return os.path.join(settings.downloads_2024_dir, project_name.replace("downloads_2024/", ""))
    return os.path.join(settings.projects_dir, project_name)


def load_taxonomy() -> Dict[str, Any]:
    """加载分类法"""
    taxonomy_file = os.path.join(settings.base_dir, "config", "taxonomy.json")
    if os.path.exists(taxonomy_file):
        with open(taxonomy_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # 默认分类法
    return {
        "stages": [
            "Onboarding",
            "Registration",
            "Home",
            "Browse",
            "Search",
            "Detail",
            "Profile",
            "Settings",
            "Paywall",
            "Checkout",
            "Other"
        ],
        "modules": [
            "Authentication",
            "Navigation",
            "Content",
            "Commerce",
            "Social",
            "Utility"
        ]
    }


def load_synonyms() -> Dict[str, Any]:
    """加载同义词映射"""
    synonyms_file = os.path.join(settings.base_dir, "config", "synonyms.json")
    if os.path.exists(synonyms_file):
        with open(synonyms_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mappings": {}}


@router.get("/taxonomy")
async def get_taxonomy():
    """获取标准分类词表"""
    taxonomy = load_taxonomy()
    synonyms = load_synonyms()
    
    return {
        "success": True,
        "taxonomy": taxonomy,
        "synonyms": synonyms.get("mappings", {})
    }


@router.get("/tag-library")
async def get_tag_library():
    """获取标签库"""
    tags_file = os.path.join(settings.base_dir, "config", "tags_library.json")
    
    if os.path.exists(tags_file):
        with open(tags_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {"categories": [], "tags": []}


@router.post("/update-classification")
async def update_classification(data: UpdateClassificationRequest):
    """更新截图的分类"""
    project_path = get_project_path(data.project)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {data.project}")
    
    # 查找分类文件
    classification_file = os.path.join(project_path, "classification.json")
    ai_file = os.path.join(project_path, "ai_analysis.json")
    
    try:
        # 尝试加载现有分类
        classifications = {}
        
        if os.path.exists(classification_file):
            with open(classification_file, "r", encoding="utf-8") as f:
                classifications = json.load(f)
        elif os.path.exists(ai_file):
            with open(ai_file, "r", encoding="utf-8") as f:
                ai_data = json.load(f)
                classifications = ai_data.get("results", {})
        
        # 应用更新
        updated = 0
        for filename, new_class in data.changes.items():
            if filename not in classifications:
                classifications[filename] = {}
            
            if new_class.stage is not None:
                classifications[filename]["stage"] = new_class.stage
            if new_class.module is not None:
                classifications[filename]["module"] = new_class.module
            if new_class.feature is not None:
                classifications[filename]["feature"] = new_class.feature
            if new_class.page_role is not None:
                classifications[filename]["page_role"] = new_class.page_role
            
            classifications[filename]["manually_adjusted"] = True
            classifications[filename]["adjusted_at"] = datetime.now().isoformat()
            updated += 1
        
        # 保存到 classification.json
        with open(classification_file, "w", encoding="utf-8") as f:
            json.dump(classifications, f, ensure_ascii=False, indent=2)
        
        # 如果有 ai_analysis.json，也更新它
        if os.path.exists(ai_file):
            with open(ai_file, "r", encoding="utf-8") as f:
                ai_data = json.load(f)
            ai_data["results"] = classifications
            with open(ai_file, "w", encoding="utf-8") as f:
                json.dump(ai_data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "count": updated}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classification/{project_name:path}")
async def get_classification(project_name: str):
    """获取项目的分类数据"""
    project_path = get_project_path(project_name)
    
    classification_file = os.path.join(project_path, "classification.json")
    ai_file = os.path.join(project_path, "ai_analysis.json")
    
    if os.path.exists(classification_file):
        with open(classification_file, "r", encoding="utf-8") as f:
            return {"project": project_name, "classifications": json.load(f)}
    elif os.path.exists(ai_file):
        with open(ai_file, "r", encoding="utf-8") as f:
            ai_data = json.load(f)
            return {"project": project_name, "classifications": ai_data.get("results", {})}
    
    return {"project": project_name, "classifications": {}}


@router.post("/batch-classify")
async def batch_classify(data: Dict[str, Any]):
    """批量分类（用于快速分类）"""
    project_name = data.get("project")
    files = data.get("files", [])
    classification = ClassificationUpdate(**data.get("classification", {}))
    
    if not project_name or not files:
        raise HTTPException(status_code=400, detail="缺少参数")
    
    # 构建 changes
    changes = {f: classification for f in files}
    
    # 复用 update_classification 逻辑
    request = UpdateClassificationRequest(project=project_name, changes=changes)
    return await update_classification(request)






