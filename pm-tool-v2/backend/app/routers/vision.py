"""
Vision Analysis API Router
提供截图分析和 API 配置功能
"""
import asyncio
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.config import settings
from app.services.vision_analysis_service import vision_service, VisionAnalysisService

router = APIRouter()


# ============================================================================
# 数据模型
# ============================================================================

class APIKeysConfig(BaseModel):
    """API Keys 配置"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


class AnalysisRequest(BaseModel):
    """分析请求"""
    app_id: str
    start_index: int = 1
    end_index: Optional[int] = None


class AnalysisStatus(BaseModel):
    """分析状态"""
    app_id: str
    status: str  # pending, running, completed, failed
    progress: int = 0
    total: int = 0
    current_screen: Optional[str] = None
    error: Optional[str] = None


# 全局状态存储
_analysis_status: dict[str, AnalysisStatus] = {}


# ============================================================================
# API 端点
# ============================================================================

@router.get("/vision/status")
async def get_api_status():
    """获取 API 配置状态"""
    openai_ok, anthropic_ok = vision_service.is_configured()
    return {
        "openai_configured": openai_ok,
        "anthropic_configured": anthropic_ok,
        "ready": openai_ok or anthropic_ok,
        "dual_model_ready": openai_ok and anthropic_ok
    }


@router.post("/vision/configure")
async def configure_api_keys(config: APIKeysConfig):
    """配置 API Keys"""
    global vision_service
    
    # 更新 settings
    if config.openai_api_key:
        settings.openai_api_key = config.openai_api_key
    if config.anthropic_api_key:
        settings.anthropic_api_key = config.anthropic_api_key
    
    # 重新初始化服务
    vision_service = VisionAnalysisService()
    
    openai_ok, anthropic_ok = vision_service.is_configured()
    return {
        "success": True,
        "openai_configured": openai_ok,
        "anthropic_configured": anthropic_ok
    }


@router.get("/vision/analysis/{app_id}/status")
async def get_analysis_status(app_id: str):
    """获取分析状态"""
    if app_id not in _analysis_status:
        return AnalysisStatus(app_id=app_id, status="not_started")
    return _analysis_status[app_id]


@router.post("/vision/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """启动截图分析任务"""
    app_id = request.app_id
    
    # 检查 API 配置
    openai_ok, anthropic_ok = vision_service.is_configured()
    if not openai_ok and not anthropic_ok:
        raise HTTPException(
            status_code=400,
            detail="API Keys not configured. Please configure via /api/vision/configure"
        )
    
    # 检查是否已在运行
    if app_id in _analysis_status and _analysis_status[app_id].status == "running":
        raise HTTPException(
            status_code=409,
            detail=f"Analysis for {app_id} is already running"
        )
    
    # 初始化状态
    _analysis_status[app_id] = AnalysisStatus(
        app_id=app_id,
        status="pending",
        progress=0,
        total=0
    )
    
    # 在后台执行分析
    background_tasks.add_task(
        run_analysis_task,
        app_id,
        request.start_index,
        request.end_index
    )
    
    return {"message": f"Analysis started for {app_id}", "status": "pending"}


async def run_analysis_task(app_id: str, start_index: int, end_index: Optional[int]):
    """后台分析任务"""
    import json
    from datetime import datetime
    
    # App 配置
    APPS = {
        "flo": {"name": "Flo", "dir": "Flo"},
        "yazio": {"name": "Yazio", "dir": "Yazio"},
        "cal_ai": {"name": "Cal AI", "dir": "Cal_AI"},
        "noom": {"name": "Noom", "dir": "Noom"},
    }
    
    if app_id not in APPS:
        _analysis_status[app_id] = AnalysisStatus(
            app_id=app_id,
            status="failed",
            error=f"Unknown app: {app_id}"
        )
        return
    
    app_config = APPS[app_id]
    screenshots_dir = settings.downloads_dir / app_config["dir"]
    
    # 获取截图文件列表
    screenshot_files = sorted([
        f for f in screenshots_dir.iterdir()
        if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]
    ])
    
    if end_index:
        screenshot_files = screenshot_files[:end_index]
    if start_index > 1:
        screenshot_files = screenshot_files[start_index - 1:]
    
    total = len(screenshot_files)
    _analysis_status[app_id] = AnalysisStatus(
        app_id=app_id,
        status="running",
        progress=0,
        total=total
    )
    
    try:
        results = []
        
        for i, file in enumerate(screenshot_files):
            _analysis_status[app_id].progress = i
            _analysis_status[app_id].current_screen = file.name
            
            # 分析单张截图
            result = await vision_service.analyze_screenshot(
                image_path=file,
                index=i + start_index,
                use_dual_model=True
            )
            results.append(result)
            
            # 短暂延迟避免 rate limit
            await asyncio.sleep(0.5)
        
        # 保存结果
        output_dir = settings.data_dir / "analysis" / "swimlane"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{app_id}.json"
        
        # 构建输出数据
        output_data = {
            "app": app_config["name"],
            "appId": app_id,
            "total_screens": len(results),
            "analyzed_at": datetime.now().isoformat(),
            "taxonomy_version": "3.0",
            "analysis_method": "gpt-5.2 + claude-opus-4-5",
            "phases": [],
            "patterns": [],
            "summary": {
                "total_pages": len(results),
                "by_type": {}
            },
            "screens": [
                {
                    "index": r.index,
                    "filename": r.filename,
                    "primary_type": r.primary_type,
                    "secondary_type": r.secondary_type,
                    "phase": r.phase,
                    "psychology": r.psychology,
                    "ui_pattern": r.ui_pattern,
                    "copy": {
                        "headline": r.copy.headline,
                        "subheadline": r.copy.subheadline,
                        "cta": r.copy.cta
                    },
                    "insight": r.insight,
                    "confidence": r.confidence,
                    "analyzed_by": r.analyzed_by
                }
                for r in results
            ],
            "flow_patterns": {},
            "design_insights": {}
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        _analysis_status[app_id] = AnalysisStatus(
            app_id=app_id,
            status="completed",
            progress=total,
            total=total
        )
    
    except Exception as e:
        _analysis_status[app_id] = AnalysisStatus(
            app_id=app_id,
            status="failed",
            error=str(e)
        )


@router.get("/vision/apps")
async def list_available_apps():
    """列出可分析的 App"""
    apps = []
    
    APPS = {
        "flo": {"name": "Flo", "dir": "Flo", "expected": 100},
        "yazio": {"name": "Yazio", "dir": "Yazio", "expected": 98},
        "cal_ai": {"name": "Cal AI", "dir": "Cal_AI", "expected": 37},
        "noom": {"name": "Noom", "dir": "Noom", "expected": 114},
    }
    
    for app_id, config in APPS.items():
        screenshots_dir = settings.downloads_dir / config["dir"]
        
        # 统计截图数量
        screenshot_count = 0
        if screenshots_dir.exists():
            screenshot_count = len([
                f for f in screenshots_dir.iterdir()
                if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]
            ])
        
        # 检查是否已分析
        analysis_path = settings.data_dir / "analysis" / "swimlane" / f"{app_id}.json"
        
        apps.append({
            "id": app_id,
            "name": config["name"],
            "screenshot_count": screenshot_count,
            "expected_count": config["expected"],
            "analyzed": analysis_path.exists(),
            "status": _analysis_status.get(app_id, AnalysisStatus(app_id=app_id, status="not_started"))
        })
    
    return apps
