"""
项目数据模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Project(BaseModel):
    """项目信息"""
    
    name: str = Field(..., description="项目名称（目录名）")
    display_name: str = Field(..., description="显示名称")
    screen_count: int = Field(0, description="截图数量")
    source: str = Field("projects", description="来源: projects 或 downloads_2024")
    data_source: Optional[str] = Field(None, description="数据来源: SD 或 Mobbin")
    
    # 可选字段
    color: str = Field("#5E6AD2", description="项目颜色")
    initial: str = Field("?", description="首字母")
    category: Optional[str] = Field(None, description="分类")
    description_cn: Optional[str] = Field(None, description="中文描述")
    description_en: Optional[str] = Field(None, description="英文描述")
    created: Optional[str] = Field(None, description="创建时间")
    
    # 状态字段
    checked: bool = Field(False, description="是否已检查")
    checked_at: Optional[str] = Field(None, description="检查时间")
    onboarding_start: int = Field(-1, description="Onboarding 开始位置")
    onboarding_end: int = Field(-1, description="Onboarding 结束位置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Cal_AI",
                "display_name": "Cal_AI",
                "screen_count": 42,
                "source": "downloads_2024",
                "data_source": "Mobbin",
                "color": "#10B981",
                "initial": "C",
            }
        }


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    
    projects: list[Project] = Field(default_factory=list)
    total: int = Field(0, description="项目总数")
    
    # 统计信息
    stats: Optional[dict] = Field(None, description="统计数据")
