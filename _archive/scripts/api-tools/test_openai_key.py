"""
OpenAI API Key 测试脚本
使用方法：设置环境变量 OPENAI_API_KEY 或在下方填入你的 API Key
"""

import urllib.request
import urllib.error
import json
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# 从环境变量获取 API Key，或手动填入（测试完后记得清除）
API_KEY = os.environ.get("OPENAI_API_KEY", "your-api-key-here")

def test_api_key():
    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print("✅ API Key 有效！")
            print(f"📋 可用模型数量: {len(data.get('data', []))}")
            
            # 显示一些常用模型
            models = [m['id'] for m in data.get('data', [])]
            popular = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini']
            available_popular = [m for m in models if any(p in m for p in popular)][:5]
            if available_popular:
                print(f"🔥 常用模型: {', '.join(available_popular)}")
            return True
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("❌ API Key 无效或已过期")
        elif e.code == 429:
            print("⚠️ API Key 有效，但已达到速率限制")
        else:
            print(f"❌ 请求失败: HTTP {e.code}")
        return False
        
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return False

if __name__ == "__main__":
    if API_KEY == "your-api-key-here":
        print("⚠️ 请先设置环境变量 OPENAI_API_KEY 或在脚本中填入你的 API Key")
    else:
        test_api_key()
        print("\n💡 提示：建议使用环境变量存储 API Key，避免泄露")
