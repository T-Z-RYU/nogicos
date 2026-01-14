"""
精确修改图片中的数字 - 使用 PIL 直接绘制
不依赖 AI，保证 100% 精确
"""
from PIL import Image, ImageDraw, ImageFont
import os

# 配置
INPUT_IMAGE = r'C:\Users\WIN\Desktop\Cursor Project\input_image.png'
OUTPUT_IMAGE = r'C:\Users\WIN\Desktop\Cursor Project\output_precise.png'

# 新数字
NEW_NUMBER = "$394,669.45"

def edit_number():
    print("[1/3] Loading image...")
    
    if not os.path.exists(INPUT_IMAGE):
        print(f"[ERROR] Image not found: {INPUT_IMAGE}")
        return False
    
    # 打开图片
    img = Image.open(INPUT_IMAGE)
    draw = ImageDraw.Draw(img)
    
    print("[2/3] Drawing new number...")
    
    # 图片实际尺寸：7868 x 2036
    # 原数字位置和大小（扩大覆盖区域，确保无残留）
    x = 120  # 左边距
    y = 440  # 上边距（往上扩一点）
    box_width = 1900  # 覆盖区域宽度
    box_height = 400  # 覆盖区域高度（往下扩一点）
    
    # 用原图背景色覆盖 - 从原图提取的精确颜色
    background_color = (28, 28, 28)  # 原图背景色
    draw.rectangle([x, y, x + box_width, y + box_height], fill=background_color)
    
    # 使用 Inter Bold 字体
    font_size = 280
    inter_bold_path = r"C:\Users\WIN\Desktop\Cursor Project\inter-font\extras\ttf\Inter-Bold.ttf"
    try:
        font = ImageFont.truetype(inter_bold_path, font_size)
        print(f"[INFO] Using Inter Bold font")
    except Exception as e:
        print(f"[WARNING] Could not load Inter Bold: {e}")
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()
            print("[WARNING] Using default font")
    
    # 绘制新数字 - 白色文字
    text_color = (255, 255, 255)  # 白色文字
    draw.text((x + 20, y + 30), NEW_NUMBER, font=font, fill=text_color)
    
    print("[3/3] Saving image...")
    img.save(OUTPUT_IMAGE)
    print(f"[SUCCESS] Image saved to: {OUTPUT_IMAGE}")
    
    return True

if __name__ == '__main__':
    edit_number()
    print("\n[TIP] If position/font doesn't match, adjust x, y, font_size in the script")

