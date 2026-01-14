"""
Onboarding 构建器 API
交互式构建 VitaFlow Onboarding 方案
"""

from fastapi import APIRouter, Query
from typing import Optional
from ..services.builder_engine import get_engine, reset_engine

router = APIRouter(prefix="/builder", tags=["Builder"])


@router.get("/start")
async def start_builder(session_id: str = Query(default="default")):
    """开始/重置构建器"""
    reset_engine(session_id)
    engine = get_engine(session_id)
    return {
        "message": "构建器已启动",
        "session_id": session_id,
        "next": engine.get_next_options(),
    }


@router.get("/options")
async def get_options(session_id: str = Query(default="default")):
    """获取下一步的选项"""
    engine = get_engine(session_id)
    return engine.get_next_options()


@router.post("/select/{option_id}")
async def select_option(option_id: str, session_id: str = Query(default="default")):
    """选择一个选项"""
    engine = get_engine(session_id)
    result = engine.select_option(option_id)
    
    if "error" in result:
        return {"success": False, "error": result["error"]}
    
    return {
        **result,
        "next": engine.get_next_options(),
    }


@router.post("/undo")
async def undo_selection(session_id: str = Query(default="default")):
    """撤销最后一个选择"""
    engine = get_engine(session_id)
    result = engine.remove_last()
    
    if "error" in result:
        return {"success": False, "error": result["error"]}
    
    return {
        **result,
        "next": engine.get_next_options(),
    }


@router.get("/summary")
async def get_summary(session_id: str = Query(default="default")):
    """获取当前方案摘要"""
    engine = get_engine(session_id)
    return engine.get_summary()


@router.get("/export")
async def export_plan(session_id: str = Query(default="default")):
    """导出完整方案"""
    engine = get_engine(session_id)
    return engine.export_plan()


@router.get("/health")
async def get_health(session_id: str = Query(default="default")):
    """获取健康度评分"""
    engine = get_engine(session_id)
    return engine._calculate_health()

