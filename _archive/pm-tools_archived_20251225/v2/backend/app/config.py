"""
PM Tool v2 - 配置文件
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


# 获取当前文件所在目录，推导出 backend 目录
_BACKEND_DIR = Path(__file__).parent.parent
_DATA_DIR = _BACKEND_DIR / "data"


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    app_name: str = "PM Tool v2"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8001
    
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
