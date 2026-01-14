"""
AI Browser 技术验证 - 配置文件
"""
import os
from dataclasses import dataclass
from typing import Optional

# 尝试从 api_keys.py 加载 API Keys
try:
    from api_keys import GOOGLE_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY, setup_env
    setup_env()  # 设置环境变量
except ImportError:
    GOOGLE_API_KEY = ""
    ANTHROPIC_API_KEY = ""
    OPENAI_API_KEY = ""

@dataclass
class Config:
    """配置类"""
    # API Keys (优先从 api_keys.py 读取，否则从环境变量)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "") or OPENAI_API_KEY
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "") or ANTHROPIC_API_KEY
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "") or GOOGLE_API_KEY
    
    # 模型配置
    main_model: str = "claude-opus-4-5-20251124"  # Claude Opus 4.5 - Computer Use 最强
    fast_model: str = "gemini-3-flash"           # Gemini 3 Flash - 速度最快
    fallback_model: str = "gpt-5.2-extra-high"   # GPT-5.2 - 备选
    
    # 路径配置
    base_dir: str = os.path.dirname(os.path.abspath(__file__))
    knowledge_base_dir: str = os.path.join(base_dir, "knowledge_base")
    results_dir: str = os.path.join(base_dir, "results")
    logs_dir: str = os.path.join(base_dir, "logs")
    
    # SkillWeaver 配置
    skillweaver_dir: str = os.path.join(base_dir, "SkillWeaver")
    
    # 测试配置
    max_steps: int = 15
    explore_iterations: int = 20
    timeout: int = 120  # 秒
    
    def validate(self) -> bool:
        """验证配置是否完整"""
        missing = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        if not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        
        if missing:
            print(f"警告: 缺少以下 API Keys: {', '.join(missing)}")
            return False
        return True


# 全局配置实例
config = Config()


# 测试场景配置
TEST_SCENARIOS = {
    "reddit": {
        "url": "https://www.reddit.com",
        "tasks": [
            "Find the top post on r/technology",
            "Search for 'AI browser' and find relevant posts",
            "Navigate to r/programming and find the most upvoted post today"
        ]
    },
    "github": {
        "url": "https://github.com",
        "tasks": [
            "Search for 'skillweaver' repository",
            "Navigate to trending repositories",
            "Find the most starred Python repository today"
        ]
    },
    "uniswap": {
        "url": "https://app.uniswap.org",
        "tasks": [
            "Navigate to the swap interface",
            "Select ETH as input token",
            "View token list and search for USDC"
        ]
    }
}


if __name__ == "__main__":
    # 测试配置
    print("=== AI Browser 技术验证配置 ===")
    print(f"主模型: {config.main_model}")
    print(f"快速模型: {config.fast_model}")
    print(f"备选模型: {config.fallback_model}")
    print(f"知识库目录: {config.knowledge_base_dir}")
    print(f"结果目录: {config.results_dir}")
    print()
    config.validate()
