"""
PM Tool v2 - FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import projects, screenshots, onboarding, sort, classify, store, export, pending, branch, analysis, vision, builder


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="PM 截图分析工具 v2 - 现代化重构版本",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
# 注意：screenshots 路由必须先注册，因为它的路由更具体
# /projects/{name}/screenshots 必须在 /projects/{name} 之前匹配
app.include_router(screenshots.router, prefix="/api", tags=["Screenshots"])
app.include_router(onboarding.router, prefix="/api", tags=["Onboarding"])
app.include_router(sort.router, prefix="/api", tags=["Sort"])
app.include_router(classify.router, prefix="/api", tags=["Classification"])
app.include_router(store.router, prefix="/api", tags=["Store"])
app.include_router(export.router, prefix="/api", tags=["Export"])
app.include_router(pending.router, prefix="/api", tags=["Pending"])
app.include_router(branch.router, prefix="/api", tags=["Branch"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(vision.router, prefix="/api", tags=["Vision Analysis"])
app.include_router(builder.router, prefix="/api", tags=["Builder"])
app.include_router(projects.router, prefix="/api", tags=["Projects"])


@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
