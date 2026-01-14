"""
分支流程 API
- 获取/保存分支数据
- 标记分支点、汇合点
- 管理分支路径

重要：所有路由都把操作类型放在 project_name 之前，避免 :path 的贪婪匹配问题
"""
import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..config import settings

router = APIRouter()


# ============ 数据模型 ============

class ForkPoint(BaseModel):
    """分支点"""
    index: int                    # 截图索引
    name: str = ""                # 分支点名称，如"选择目标"


class Branch(BaseModel):
    """分支路径"""
    id: str                       # 唯一标识
    name: str                     # 分支名称，如"减重路径"
    color: str                    # 颜色标识，如"#22c55e"
    fork_from: int                # 从哪个截图分叉
    screens: List[int]            # 包含的截图索引列表
    merge_to: Optional[int] = None  # 汇合到哪个截图（可选）


class BranchData(BaseModel):
    """分支数据"""
    version: str = "1.0"
    fork_points: List[ForkPoint] = []
    merge_points: List[int] = []
    branches: List[Branch] = []
    updated_at: Optional[str] = None


class BranchDataUpdate(BaseModel):
    """更新分支数据请求"""
    fork_points: List[ForkPoint] = []
    merge_points: List[int] = []
    branches: List[Branch] = []


class AddForkPointRequest(BaseModel):
    """添加分支点请求"""
    index: int
    name: str = ""


class AddMergePointRequest(BaseModel):
    """添加汇合点请求"""
    index: int


class AddBranchRequest(BaseModel):
    """添加分支请求"""
    name: str
    color: str
    fork_from: int
    screens: List[int]
    merge_to: Optional[int] = None


# ============ 工具函数 ============

def get_project_path(project_name: str) -> str:
    """获取项目路径"""
    if project_name.startswith("downloads_2024/"):
        return os.path.join(settings.downloads_2024_dir, project_name.replace("downloads_2024/", ""))
    return os.path.join(settings.projects_dir, project_name)


def get_branch_file(project_path: str) -> str:
    """获取分支数据文件路径"""
    return os.path.join(project_path, "branch_data.json")


def load_branch_data(project_path: str) -> BranchData:
    """加载分支数据"""
    branch_file = get_branch_file(project_path)
    
    if os.path.exists(branch_file):
        with open(branch_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return BranchData(**data)
    
    return BranchData()


def save_branch_data(project_path: str, data: BranchData) -> None:
    """保存分支数据"""
    branch_file = get_branch_file(project_path)
    
    # 备份旧文件
    backup_dir = os.path.join(project_path, "backups")
    if os.path.exists(branch_file):
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(
            backup_dir,
            f"branch_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        import shutil
        shutil.copy(branch_file, backup_file)
        
        # 只保留最近10个备份
        backups = sorted([
            f for f in os.listdir(backup_dir)
            if f.startswith("branch_data_")
        ], reverse=True)
        for old_backup in backups[10:]:
            os.remove(os.path.join(backup_dir, old_backup))
    
    # 更新时间戳
    data.updated_at = datetime.now().isoformat()
    
    # 保存数据
    with open(branch_file, "w", encoding="utf-8") as f:
        json.dump(data.model_dump(), f, ensure_ascii=False, indent=2)


# ============ API 路由 ============
# 重要：把操作类型放在 project_name 之前，避免 :path 贪婪匹配


# --- 分支数据 CRUD ---

@router.get("/branch/data/{project_name:path}", response_model=BranchData)
async def get_branch_data(project_name: str):
    """获取项目的分支数据"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    return load_branch_data(project_path)


@router.post("/branch/data/{project_name:path}")
async def save_branch_data_api(project_name: str, data: BranchDataUpdate):
    """保存项目的分支数据"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = BranchData(
        fork_points=data.fork_points,
        merge_points=data.merge_points,
        branches=data.branches
    )
    
    save_branch_data(project_path, branch_data)
    
    return {"success": True, "data": branch_data.model_dump()}


# --- 分支点操作 ---

@router.post("/branch/fork-point/{project_name:path}")
async def add_fork_point(project_name: str, request: AddForkPointRequest):
    """添加分支点"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = load_branch_data(project_path)
    
    # 检查是否已存在
    existing = next((fp for fp in branch_data.fork_points if fp.index == request.index), None)
    if existing:
        existing.name = request.name
    else:
        branch_data.fork_points.append(ForkPoint(index=request.index, name=request.name))
    
    # 排序
    branch_data.fork_points.sort(key=lambda x: x.index)
    
    save_branch_data(project_path, branch_data)
    
    return {"success": True, "fork_points": [fp.model_dump() for fp in branch_data.fork_points]}


@router.delete("/branch/fork-point/{index}/{project_name:path}")
async def remove_fork_point(index: int, project_name: str):
    """移除分支点"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = load_branch_data(project_path)
    branch_data.fork_points = [fp for fp in branch_data.fork_points if fp.index != index]
    
    save_branch_data(project_path, branch_data)
    
    return {"success": True, "fork_points": [fp.model_dump() for fp in branch_data.fork_points]}


# --- 汇合点操作 ---

@router.post("/branch/merge-point/{project_name:path}")
async def add_merge_point(project_name: str, request: AddMergePointRequest):
    """添加汇合点"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = load_branch_data(project_path)
    
    if request.index not in branch_data.merge_points:
        branch_data.merge_points.append(request.index)
        branch_data.merge_points.sort()
    
    save_branch_data(project_path, branch_data)
    
    return {"success": True, "merge_points": branch_data.merge_points}


@router.delete("/branch/merge-point/{index}/{project_name:path}")
async def remove_merge_point(index: int, project_name: str):
    """移除汇合点"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = load_branch_data(project_path)
    branch_data.merge_points = [mp for mp in branch_data.merge_points if mp != index]
    
    save_branch_data(project_path, branch_data)
    
    return {"success": True, "merge_points": branch_data.merge_points}


# --- 分支路径操作 ---

@router.post("/branch/path/{project_name:path}")
async def add_branch(project_name: str, request: AddBranchRequest):
    """添加分支路径"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = load_branch_data(project_path)
    
    # 生成唯一ID
    branch_id = f"branch_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(branch_data.branches)}"
    
    new_branch = Branch(
        id=branch_id,
        name=request.name,
        color=request.color,
        fork_from=request.fork_from,
        screens=request.screens,
        merge_to=request.merge_to
    )
    
    branch_data.branches.append(new_branch)
    save_branch_data(project_path, branch_data)
    
    return {"success": True, "branch": new_branch.model_dump()}


@router.put("/branch/path/{branch_id}/{project_name:path}")
async def update_branch(branch_id: str, project_name: str, request: AddBranchRequest):
    """更新分支路径"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = load_branch_data(project_path)
    
    # 找到并更新分支
    for i, branch in enumerate(branch_data.branches):
        if branch.id == branch_id:
            branch_data.branches[i] = Branch(
                id=branch_id,
                name=request.name,
                color=request.color,
                fork_from=request.fork_from,
                screens=request.screens,
                merge_to=request.merge_to
            )
            break
    else:
        raise HTTPException(status_code=404, detail=f"分支不存在: {branch_id}")
    
    save_branch_data(project_path, branch_data)
    
    return {"success": True, "branch": branch_data.branches[i].model_dump()}


@router.delete("/branch/path/{branch_id}/{project_name:path}")
async def delete_branch(branch_id: str, project_name: str):
    """删除分支路径"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    branch_data = load_branch_data(project_path)
    branch_data.branches = [b for b in branch_data.branches if b.id != branch_id]
    
    save_branch_data(project_path, branch_data)
    
    return {"success": True}


# --- 清空操作 ---

@router.delete("/branch/clear/{project_name:path}")
async def clear_branch_data(project_name: str):
    """清空项目的所有分支数据"""
    project_path = get_project_path(project_name)
    
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
    
    # 保存空数据（会自动备份旧数据）
    save_branch_data(project_path, BranchData())
    
    return {"success": True}
