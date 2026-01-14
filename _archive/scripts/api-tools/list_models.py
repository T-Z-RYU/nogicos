import urllib.request
import json
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

# 从环境变量获取 API Key
API_KEY = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
url = "https://api.openai.com/v1/models"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})

with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    models = sorted([m["id"] for m in data["data"]])
    
    # 分类
    gpt4 = [m for m in models if "gpt-4" in m]
    gpt35 = [m for m in models if "gpt-3.5" in m]
    dalle = [m for m in models if "dall-e" in m]
    whisper = [m for m in models if "whisper" in m]
    tts = [m for m in models if "tts" in m]
    embed = [m for m in models if "embedding" in m]
    other = [m for m in models if m not in gpt4+gpt35+dalle+whisper+tts+embed]
    
    print("=== GPT-4 系列 ===")
    for m in gpt4: print(f"  {m}")
    
    print("\n=== GPT-3.5 系列 ===")
    for m in gpt35: print(f"  {m}")
    
    print("\n=== DALL-E 图像生成 ===")
    for m in dalle: print(f"  {m}")
    
    print("\n=== Whisper 语音识别 ===")
    for m in whisper: print(f"  {m}")
    
    print("\n=== TTS 语音合成 ===")
    for m in tts: print(f"  {m}")
    
    print("\n=== Embedding 向量 ===")
    for m in embed: print(f"  {m}")
    
    print(f"\n=== 其他模型 ({len(other)}个) ===")
    for m in other: print(f"  {m}")
