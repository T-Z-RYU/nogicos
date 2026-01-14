"""
项目 API 路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.project import Project, ProjectListResponse
from app.services.project_service import get_all_projects


router = APIRouter()


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    source: Optional[str] = Query(None, description="过滤来源: projects 或 downloads_2024"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    checked: Optional[bool] = Query(None, description="过滤已检查/未检查"),
) -> ProjectListResponse:
    """
    获取项目列表
    
    - **source**: 过滤项目来源
    - **search**: 按名称搜索
    - **checked**: 过滤检查状态
    """
    # #region agent log
    import json as _json
    with open(r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log", "a", encoding="utf-8") as _f:
        _f.write(_json.dumps({"location":"projects.py:list_projects","message":"API_CALLED","data":{"source":source,"search":search},"timestamp":__import__("time").time()*1000,"hypothesisId":"A"}) + "\n")
    # #endregion
    
    projects = get_all_projects()
    
    # #region agent log
    with open(r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log", "a", encoding="utf-8") as _f:
        _f.write(_json.dumps({"location":"projects.py:list_projects","message":"PROJECTS_LOADED","data":{"count":len(projects)},"timestamp":__import__("time").time()*1000,"hypothesisId":"A"}) + "\n")
    # #endregion
    
    # 过滤
    if source:
        projects = [p for p in projects if p.source == source]
    
    if search:
        search_lower = search.lower()
        projects = [p for p in projects if search_lower in p.display_name.lower()]
    
    if checked is not None:
        projects = [p for p in projects if p.checked == checked]
    
    # 统计
    total_screens = sum(p.screen_count for p in projects)
    checked_count = sum(1 for p in projects if p.checked)
    onboarding_count = sum(1 for p in projects if p.onboarding_start > 0)
    
    return ProjectListResponse(
        projects=projects,
        total=len(projects),
        stats={
            "total_screens": total_screens,
            "checked": checked_count,
            "onboarding_marked": onboarding_count,
        }
    )


@router.get("/projects/{project_name:path}", response_model=Project)
async def get_project(project_name: str) -> Project:
    """
    获取单个项目信息
    """
    projects = get_all_projects()
    
    for p in projects:
        if p.name == project_name:
            return p
    
    raise HTTPException(status_code=404, detail=f"项目不存在: {project_name}")
