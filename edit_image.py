"""
Nano Banana 3.0 Pro - 图片数字修改脚本
"""
import requests
import base64
import os
from pathlib import Path

# 配置
API_KEY = 'AIzaSyBa9e1MJD_VmzJ2do6q4nxYKjp4jsran00'

# Google Gemini API - 使用 imagen-3.0-generate-002 模型（精确编辑）
API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}'

# 文件路径
INPUT_IMAGE = r'C:\Users\WIN\Desktop\Cursor Project\input_image.png'
OUTPUT_IMAGE = r'C:\Users\WIN\Desktop\Cursor Project\output_image.png'

# 修改指令 - 精确描述，强调保持原样
EDIT_INSTRUCTION = """
You are an expert image editor. Your task is to make a MINIMAL edit to this screenshot.

TASK: Replace the text "$230,233.53" with "$394,669.45"

CRITICAL RULES:
1. ONLY change the digits in the main balance number
2. Keep the EXACT same font family, font weight, font size, and font color
3. Keep ALL other text EXACTLY as it appears (buttons, labels, percentages)
4. Do NOT modify any backgrounds, buttons, or UI elements
5. The result should look like an IDENTICAL screenshot with just the number changed

Output a high-quality image with this single change.
"""

def edit_image():
    print("[1/3] Reading image...")
    
    # 检查输入图片是否存在
    if not os.path.exists(INPUT_IMAGE):
        print(f"[ERROR] Image not found: {INPUT_IMAGE}")
        print("Please save the image as input_image.png in the project root")
        return False
    
    # 读取并编码图片
    with open(INPUT_IMAGE, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # 判断图片类型
    ext = Path(INPUT_IMAGE).suffix.lower()
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp'
    }.get(ext, 'image/png')
    
    print(f"[2/3] Calling Nano Banana Pro API...")
    
    # 设置请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 设置请求体 - Gemini API 格式
    payload = {
        'contents': [
            {
                'parts': [
                    {'inlineData': {'mimeType': mime_type, 'data': image_data}},
                    {'text': EDIT_INSTRUCTION}
                ]
            }
        ],
        'generationConfig': {
            'responseModalities': ['Text', 'Image'],
            'temperature': 0.2
        }
    }
    
    # 发送请求
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        result = response.json()
        
        print(f"[3/3] Response received, status: {response.status_code}")
        
        # 处理响应
        if 'candidates' in result:
            for part in result['candidates'][0]['content']['parts']:
                # 支持两种格式: inline_data 和 inlineData
                inline_data = part.get('inline_data') or part.get('inlineData')
                if inline_data:
                    output_image_data = base64.b64decode(inline_data['data'])
                    with open(OUTPUT_IMAGE, 'wb') as f:
                        f.write(output_image_data)
                    print(f"[SUCCESS] Image saved to: {OUTPUT_IMAGE}")
                    return True
        
        # 如果没有图片结果，打印完整响应用于调试
        print("[FAILED] Could not generate modified image")
        print(f"API Response: {result}")
        return False
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout, please try again")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == '__main__':
    edit_image()

