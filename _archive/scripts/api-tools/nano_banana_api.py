"""
Google Nano Banana 图像生成 API 调用脚本
使用方法：设置环境变量 GOOGLE_API_KEY 或在下方填入你的 API Key

Nano Banana 模型：
- gemini-2.5-flash-preview-05-20 (Nano Banana - 快速版)
- gemini-2.0-flash-exp-image-generation (实验版图像生成)
"""

import urllib.request
import urllib.error
import json
import sys
import os
import base64
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 从环境变量获取 API Key
API_KEY = os.environ.get("GOOGLE_API_KEY", "your-google-api-key-here")

# 可用的模型
MODELS = {
    "nano_banana_pro": "nano-banana-pro-preview",           # Nano Banana Pro (默认)
    "nano_banana": "gemini-2.0-flash-exp-image-generation", # Nano Banana 标准版
    "gemini_3_pro": "gemini-3-pro-image-preview",           # Gemini 3 Pro Image
    "gemini_2.5_flash": "gemini-2.5-flash-image",           # Gemini 2.5 Flash Image
    "imagen_4": "imagen-4.0-generate-001",                  # Imagen 4.0
    "imagen_4_ultra": "imagen-4.0-ultra-generate-001",      # Imagen 4.0 Ultra
}

# 默认模型
DEFAULT_MODEL = "nano_banana_pro"

def generate_image(prompt: str, model: str = None, output_path: str = None) -> dict:
    """
    使用 Nano Banana 生成图像
    
    Args:
        prompt: 图像描述文本
        model: 模型选择 ("nano_banana" 或 "flash")
        output_path: 保存图像的路径（可选）
    
    Returns:
        dict: API 响应结果
    """
    if model is None:
        model = DEFAULT_MODEL
    model_id = MODELS.get(model, MODELS[DEFAULT_MODEL])
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        print(f"🎨 正在生成图像...")
        print(f"📝 提示词: {prompt}")
        print(f"🤖 模型: {model_id}")
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())
            
            # 解析响应
            if "candidates" in result:
                for candidate in result["candidates"]:
                    if "content" in candidate:
                        for part in candidate["content"].get("parts", []):
                            # 处理图像数据
                            if "inlineData" in part:
                                image_data = part["inlineData"]
                                mime_type = image_data.get("mimeType", "image/png")
                                base64_data = image_data.get("data", "")
                                
                                # 保存图像
                                if output_path is None:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    ext = mime_type.split("/")[-1]
                                    output_path = f"nano_banana_{timestamp}.{ext}"
                                
                                image_bytes = base64.b64decode(base64_data)
                                with open(output_path, "wb") as f:
                                    f.write(image_bytes)
                                
                                print(f"✅ 图像已保存: {output_path}")
                                print(f"📦 文件大小: {len(image_bytes) / 1024:.1f} KB")
                                return {"success": True, "path": output_path, "size": len(image_bytes)}
                            
                            # 处理文本响应
                            if "text" in part:
                                print(f"💬 文本响应: {part['text']}")
            
            print("⚠️ 响应中没有找到图像数据")
            print(f"📋 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return {"success": False, "response": result}
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"❌ HTTP 错误 {e.code}: {e.reason}")
        if error_body:
            try:
                error_json = json.loads(error_body)
                print(f"📋 错误详情: {json.dumps(error_json, indent=2, ensure_ascii=False)}")
            except:
                print(f"📋 错误详情: {error_body}")
        return {"success": False, "error": str(e)}
        
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return {"success": False, "error": str(e)}


def edit_image(image_path: str, edit_prompt: str, output_path: str = None) -> dict:
    """
    使用 Nano Banana 编辑图像
    
    Args:
        image_path: 输入图像路径
        edit_prompt: 编辑指令
        output_path: 保存编辑后图像的路径（可选）
    
    Returns:
        dict: API 响应结果
    """
    # 读取图像并转换为 base64
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    # 检测 MIME 类型
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", 
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp"
    }
    mime_type = mime_types.get(ext, "image/png")
    
    model_id = MODELS[DEFAULT_MODEL]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64_image
                        }
                    },
                    {"text": edit_prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        print(f"✏️ 正在编辑图像...")
        print(f"📁 输入图像: {image_path}")
        print(f"📝 编辑指令: {edit_prompt}")
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())
            
            if "candidates" in result:
                for candidate in result["candidates"]:
                    if "content" in candidate:
                        for part in candidate["content"].get("parts", []):
                            if "inlineData" in part:
                                image_data = part["inlineData"]
                                result_mime = image_data.get("mimeType", "image/png")
                                base64_data = image_data.get("data", "")
                                
                                if output_path is None:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    result_ext = result_mime.split("/")[-1]
                                    output_path = f"nano_banana_edit_{timestamp}.{result_ext}"
                                
                                result_bytes = base64.b64decode(base64_data)
                                with open(output_path, "wb") as f:
                                    f.write(result_bytes)
                                
                                print(f"✅ 编辑后图像已保存: {output_path}")
                                return {"success": True, "path": output_path}
                            
                            if "text" in part:
                                print(f"💬 文本响应: {part['text']}")
            
            print("⚠️ 响应中没有找到图像数据")
            return {"success": False, "response": result}
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"❌ HTTP 错误 {e.code}: {e.reason}")
        if error_body:
            try:
                error_json = json.loads(error_body)
                print(f"📋 错误详情: {json.dumps(error_json, indent=2, ensure_ascii=False)}")
            except:
                print(f"📋 错误详情: {error_body}")
        return {"success": False, "error": str(e)}
        
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return {"success": False, "error": str(e)}


def test_api_key():
    """测试 Google API Key 是否有效"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            models = data.get("models", [])
            print("✅ Google API Key 有效！")
            print(f"📋 可用模型数量: {len(models)}")
            
            # 显示图像相关模型
            image_models = [m["name"] for m in models if "image" in m["name"].lower() or "flash" in m["name"].lower()]
            if image_models:
                print(f"🎨 图像相关模型:")
                for m in image_models[:5]:
                    print(f"   - {m}")
            return True
            
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print("❌ API Key 无效")
        else:
            print(f"❌ 请求失败: HTTP {e.code}")
        return False
        
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return False


def main():
    """主函数 - 交互式使用"""
    print("=" * 50)
    print("🍌 Google Nano Banana 图像生成工具")
    print("=" * 50)
    
    if API_KEY == "your-google-api-key-here":
        print("\n⚠️ 请先设置环境变量 GOOGLE_API_KEY")
        print("   Windows: set GOOGLE_API_KEY=你的API密钥")
        print("   Linux/Mac: export GOOGLE_API_KEY=你的API密钥")
        print("\n💡 获取 API Key: https://aistudio.google.com/apikey")
        return
    
    print("\n🔑 正在验证 API Key...")
    if not test_api_key():
        return
    
    print("\n" + "-" * 50)
    print("功能选择:")
    print("  1. 文本生成图像")
    print("  2. 编辑图像")
    print("  3. 退出")
    print("-" * 50)
    
    choice = input("\n请选择功能 (1/2/3): ").strip()
    
    if choice == "1":
        prompt = input("\n📝 请输入图像描述: ").strip()
        if prompt:
            generate_image(prompt)
        else:
            print("❌ 描述不能为空")
            
    elif choice == "2":
        image_path = input("\n📁 请输入图像路径: ").strip()
        if os.path.exists(image_path):
            edit_prompt = input("📝 请输入编辑指令: ").strip()
            if edit_prompt:
                edit_image(image_path, edit_prompt)
            else:
                print("❌ 编辑指令不能为空")
        else:
            print(f"❌ 文件不存在: {image_path}")
            
    elif choice == "3":
        print("👋 再见！")
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
