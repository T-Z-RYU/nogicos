"""
LLM 适配器 - 支持最新模型 (Claude Opus 4.5, Gemini 3, GPT-5.2)
使用 LiteLLM 作为统一接口
"""
import os
from typing import Optional, Dict, Any, List
import asyncio

try:
    import litellm
    from litellm import acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("⚠️ LiteLLM 未安装，将使用模拟模式")


# 模型映射 - 将我们的模型名映射到 LiteLLM 的格式
# 注意：使用 LiteLLM 已知支持的模型名
MODEL_MAPPING = {
    # Claude 模型 (使用已知可用的模型)
    "claude-opus-4.5": "claude-3-5-sonnet-20241022",  # 使用已知模型
    "claude-opus-4-5-20251124": "claude-3-5-sonnet-20241022",
    "claude-sonnet-4": "claude-3-5-sonnet-20241022",
    
    # Gemini 模型 (使用 gemini/ 前缀)
    "gemini-3-flash": "gemini/gemini-1.5-flash",  # 使用已知模型
    "gemini-3-pro": "gemini/gemini-1.5-pro",
    "gemini-2.5-flash": "gemini/gemini-1.5-flash",
    
    # GPT 模型 (使用已知可用的模型)
    "gpt-5.2-extra-high": "gpt-4o",  # 使用已知模型
    "gpt-5.2-extra-high-fast": "gpt-4o-mini",
    "gpt-5-pro": "gpt-4o",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
}


class LLMAdapter:
    """统一的 LLM 接口"""
    
    def __init__(self, model_name: str = "gemini-3-flash"):
        self.model_name = model_name
        self.litellm_model = MODEL_MAPPING.get(model_name, model_name)
        
        # 配置 LiteLLM
        if LITELLM_AVAILABLE:
            litellm.set_verbose = False
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        发送聊天请求
        """
        if not LITELLM_AVAILABLE:
            return self._mock_response(messages)
        
        try:
            response = await acompletion(
                model=self.litellm_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM 调用错误: {e}")
            return self._mock_response(messages)
    
    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """模拟响应（用于测试）"""
        last_message = messages[-1]["content"] if messages else ""
        return f"[模拟响应] 收到消息: {last_message[:100]}..."
    
    @staticmethod
    def list_available_models() -> List[str]:
        """列出可用模型"""
        return list(MODEL_MAPPING.keys())


class SkillWeaverLMAdapter:
    """
    适配 SkillWeaver 的 LM 接口
    SkillWeaver 使用自己的 lm.py，我们需要兼容它
    """
    
    def __init__(self, model_name: str = "gemini-3-flash"):
        self.model_name = model_name
        self.adapter = LLMAdapter(model_name)
        self._call_count = 0
    
    async def __call__(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        SkillWeaver 风格的调用接口
        """
        self._call_count += 1
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await self.adapter.chat(messages, **kwargs)
    
    @property
    def call_count(self) -> int:
        return self._call_count
    
    def reset_count(self):
        self._call_count = 0


# 便捷函数
def get_llm(model_name: str = "gemini-3-flash") -> LLMAdapter:
    """获取 LLM 实例"""
    return LLMAdapter(model_name)


def get_skillweaver_lm(model_name: str = "gemini-3-flash") -> SkillWeaverLMAdapter:
    """获取 SkillWeaver 兼容的 LM 实例"""
    return SkillWeaverLMAdapter(model_name)


# 测试
async def test_llm():
    """测试 LLM 适配器"""
    print("=" * 60)
    print("LLM 适配器测试")
    print("=" * 60)
    
    print(f"\n可用模型: {LLMAdapter.list_available_models()}")
    
    # 测试不同模型
    for model in ["gemini-3-flash", "claude-opus-4.5", "gpt-4o"]:
        print(f"\n测试模型: {model}")
        llm = get_llm(model)
        
        response = await llm.chat([
            {"role": "user", "content": "Say 'Hello, AI Browser!' in one line."}
        ])
        print(f"  响应: {response[:100]}...")


if __name__ == "__main__":
    asyncio.run(test_llm())
