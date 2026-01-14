"""
截图数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field


class Classification(BaseModel):
    """三层分类信息"""
    
    stage: Optional[str] = Field(None, description="阶段: Onboarding, Core, Monetization")
    module: Optional[str] = Field(None, description="模块: Login, Permission, Paywall 等")
    feature: Optional[str] = Field(None, description="功能点描述")
    page_role: Optional[str] = Field(None, description="页面角色")
    screen_type: Optional[str] = Field(None, description="页面类型（旧格式兼容）")
    confidence: float = Field(0.0, description="分类置信度")
    manually_adjusted: bool = Field(False, description="是否手动调整过")


class Screenshot(BaseModel):
    """截图信息"""
    
    filename: str = Field(..., description="文件名")
    index: int = Field(0, description="排序索引")
    
    # 分类信息
    classification: Optional[Classification] = Field(None, description="分类信息")
    
    # 描述
    description: Optional[str] = Field(None, description="截图描述")
    
    # URL（由 API 填充）
    url: Optional[str] = Field(None, description="原图 URL")
    thumb_url: Optional[str] = Field(None, description="缩略图 URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "Screen_001.png",
                "index": 1,
                "classification": {
                    "stage": "Onboarding",
                    "module": "Welcome",
                    "feature": "欢迎页面",
                },
                "url": "/api/screenshots/Cal_AI/Screen_001.png",
                "thumb_url": "/api/thumbnails/Cal_AI/Screen_001.png",
            }
        }


class ScreenshotListResponse(BaseModel):
    """截图列表响应"""
    
    project: str = Field(..., description="项目名称")
    screenshots: list[Screenshot] = Field(default_factory=list)
    total: int = Field(0, description="截图总数")
    
    # 分类统计
    stages: Optional[dict[str, int]] = Field(None, description="Stage 统计")
    modules: Optional[dict[str, int]] = Field(None, description="Module 统计")
