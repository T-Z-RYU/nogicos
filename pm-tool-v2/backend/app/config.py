"""
PM Tool v2 - 配置文件
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


# 获取当前文件所在目录，推导出 backend 目录
_BACKEND_DIR = Path(__file__).parent.parent

# 数据目录 - 使用本地 data 文件夹（已包含完整截图）
_DATA_DIR = _BACKEND_DIR / "data"


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    app_name: str = "PM Tool v2"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8004
    
    # AI API Keys (支持多种环境变量名称)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果 PM_TOOL_ 前缀的变量为空，尝试读取标准环境变量
        import os
        if not self.openai_api_key or self.openai_api_key == "your_openai_api_key_here":
            self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        if not self.anthropic_api_key or self.anthropic_api_key == "your_anthropic_api_key_here":
            self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    
    # 数据目录 - 使用独立的数据副本（不再依赖老版本）
    data_dir: Path = _DATA_DIR
    
    @property
    def base_dir(self) -> Path:
        """基础目录"""
        return self.data_dir
    
    @property
    def projects_dir(self) -> Path:
        """projects 目录"""
        return self.data_dir / "projects"
    
    @property
    def downloads_dir(self) -> Path:
        """downloads_2024 目录"""
        return self.data_dir / "downloads_2024"
    
    @property
    def downloads_2024_dir(self) -> Path:
        """downloads_2024 目录 (alias)"""
        return self.data_dir / "downloads_2024"
    
    @property
    def config_dir(self) -> Path:
        """config 目录"""
        return self.data_dir / "config"
    
    @property
    def csv_data_dir(self) -> Path:
        """CSV 数据目录"""
        return self.data_dir / "csv_data"
    
    # 缩略图配置
    thumb_sizes: dict = {
        "small": 120,
        "medium": 240,
        "large": 480
    }
    
    # CORS 配置
    cors_origins: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ]
    
    class Config:
        env_prefix = "PM_TOOL_"


# 全局配置实例
settings = Settings()

# 启动时验证数据目录
def validate_data_directories():
    """验证数据目录是否正确配置"""
    import sys
    
    errors = []
    
    # 检查 downloads_2024 目录
    if not settings.downloads_2024_dir.exists():
        errors.append(f"❌ downloads_2024 目录不存在: {settings.downloads_2024_dir}")
    else:
        # 检查是否有实际的截图文件（不只是 JSON）
        has_images = any(
            f.suffix.lower() in ['.png', '.jpg', '.jpeg']
            for d in settings.downloads_2024_dir.iterdir() if d.is_dir()
            for f in d.iterdir() if f.is_file()
        )
        if not has_images:
            errors.append(f"⚠️ downloads_2024 目录没有图片文件，只有 JSON 配置")
            errors.append(f"   当前路径: {settings.downloads_2024_dir}")
            errors.append(f"   请检查数据目录配置是否正确")
    
    # 检查 config 目录
    if not settings.config_dir.exists():
        errors.append(f"❌ config 目录不存在: {settings.config_dir}")
    
    if errors:
        print("\n" + "="*60)
        print("🚨 数据目录配置警告")
        print("="*60)
        for err in errors:
            print(err)
        print("="*60 + "\n")

# 在模块加载时执行验证
validate_data_directories()
