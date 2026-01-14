"""
测试 SkillWeaver 对多模型的支持
"""
import asyncio
import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 设置 API Keys
from api_keys import GOOGLE_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 添加 SkillWeaver 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SkillWeaver"))

from skillweaver.lm import LM


async def test_model(model_name: str, display_name: str):
    """测试单个模型"""
    print(f"\n{'='*50}")
    print(f"测试: {display_name}")
    print(f"模型: {model_name}")
    print(f"{'='*50}")
    
    try:
        lm = LM(model_name)
        print(f"✅ 客户端创建成功")
        print(f"   类型: {'OpenAI' if lm.is_openai() else 'Anthropic' if lm.is_anthropic() else 'Gemini' if lm.is_gemini() else '未知'}")
        
        # 简单测试
        response = await lm(
            [{"role": "user", "content": "Say 'Hello' in exactly one word."}],
            json_mode=False,
        )
        
        print(f"✅ API 调用成功")
        print(f"   响应: {response[:100] if isinstance(response, str) else response}")
        
        # 测试 JSON 模式
        json_response = await lm(
            [{"role": "user", "content": "Return a JSON object with key 'greeting' and value 'hello'"}],
            json_mode=True,
        )
        
        print(f"✅ JSON 模式成功")
        print(f"   响应: {json_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("    SkillWeaver 多模型支持测试")
    print("=" * 60)
    
    models = [
        ("gpt-5.2", "GPT-5.2 (OpenAI)"),
        ("claude-opus-4-5-20251101", "Claude Opus 4.5 (Anthropic)"),
        ("gemini-3-flash-preview", "Gemini 3 Flash (Google)"),
    ]
    
    results = {}
    for model_name, display_name in models:
        results[display_name] = await test_model(model_name, display_name)
    
    print("\n" + "=" * 60)
    print("    测试结果")
    print("=" * 60)
    
    for name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
