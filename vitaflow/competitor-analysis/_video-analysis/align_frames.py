# -*- coding: utf-8 -*-
"""
视频帧与静态截图对齐脚本
使用AI语义匹配将视频帧与高质量静态截图进行对齐
"""

import os
import sys
import json
import base64
from pathlib import Path
from anthropic import Anthropic
from typing import List, Dict, Optional, Tuple

# 配置
VIDEO_FRAMES_DIR = Path("calai_keyframes")
SCREENSHOTS_DIR = Path("C:/Users/WIN/Desktop/Cursor Project/PM_Screenshot_Tool/projects/Cal_AI_-_Calorie_Tracker_Analysis")
OUTPUT_FILE = Path("alignment_results.json")
ANALYSIS_FILE = Path("calai_analysis.json")

# 加载API密钥
def load_api_key():
    config_path = Path("C:/Users/WIN/Desktop/Cursor Project/PM_Screenshot_Tool/config/api_keys.json")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get("ANTHROPIC_API_KEY")
    
    return os.environ.get("ANTHROPIC_API_KEY")


def encode_image(filepath):
    """将图片编码为base64"""
    with open(filepath, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def get_media_type(filepath):
    """获取图片的media type"""
    ext = Path(filepath).suffix.lower()
    if ext in ['.jpg', '.jpeg']:
        return "image/jpeg"
    elif ext == '.png':
        return "image/png"
    elif ext == '.webp':
        return "image/webp"
    return "image/jpeg"


def load_video_analysis() -> Dict:
    """加载视频帧分析结果"""
    if ANALYSIS_FILE.exists():
        with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_unique_pages(video_analysis: Dict) -> List[Dict]:
    """从视频分析中提取唯一页面（去掉重复帧）"""
    frames = video_analysis.get('frames', [])
    unique_pages = []
    
    for frame in frames:
        if frame.get('is_new_page', True):
            unique_pages.append(frame)
    
    return unique_pages


def get_screenshots() -> List[Path]:
    """获取静态截图列表"""
    if not SCREENSHOTS_DIR.exists():
        return []
    
    screenshots = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        screenshots.extend(SCREENSHOTS_DIR.glob(ext))
    
    # 按文件名排序
    return sorted(screenshots, key=lambda x: x.name)


def align_single_frame(client, frame_path: Path, frame_info: Dict, 
                       screenshots: List[Path], batch_size: int = 10) -> Dict:
    """对齐单个视频帧与最匹配的静态截图"""
    
    # 构建prompt
    prompt = f"""你是一位产品分析专家，请帮我找出与参考图片最匹配的静态截图。

## 参考图片信息
- 来源: 视频帧
- Stage: {frame_info.get('stage', 'Unknown')}
- Module: {frame_info.get('module', 'Unknown')}
- Feature: {frame_info.get('feature', 'Unknown')}
- 描述: {frame_info.get('description', '')}

## 任务
1. 比较参考图片与候选截图
2. 找出内容最相似的截图
3. 如果没有匹配的，返回null

## 匹配标准（按优先级）
1. 页面完全相同（标题、内容、布局）
2. 页面类型相同但状态不同（如不同的选项被选中）
3. 相似但有明显差异

## 输出格式
```json
{{
  "best_match": {{
    "index": 3,
    "confidence": 0.95,
    "match_type": "exact",
    "reason": "页面完全相同，显示相同的性别选择界面"
  }},
  "alternatives": [
    {{
      "index": 5,
      "confidence": 0.7,
      "reason": "类似页面但选中状态不同"
    }}
  ]
}}
```

如果没有匹配：
```json
{{
  "best_match": null,
  "reason": "没有找到相似的截图"
}}
```

请分析以下图片，只输出JSON："""

    # 构建消息
    content = [
        {"type": "text", "text": prompt},
        {"type": "text", "text": "\n--- 参考图片（视频帧）---"},
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": get_media_type(frame_path),
                "data": encode_image(frame_path)
            }
        },
        {"type": "text", "text": "\n--- 候选截图 ---"}
    ]
    
    # 添加候选截图
    for i, screenshot in enumerate(screenshots[:batch_size]):
        content.append({"type": "text", "text": f"\n候选 {i + 1}: {screenshot.name}"})
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": get_media_type(screenshot),
                "data": encode_image(screenshot)
            }
        })
    
    # 调用API
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": content}]
    )
    
    # 解析结果
    result_text = response.content[0].text
    
    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        return json.loads(result_text)
    except:
        return {"error": "parse_failed", "raw": result_text}


def align_frames_batch(client, frame_paths: List[Path], frame_infos: List[Dict],
                       screenshots: List[Path]) -> List[Dict]:
    """批量对齐视频帧"""
    results = []
    
    for i, (frame_path, frame_info) in enumerate(zip(frame_paths, frame_infos)):
        print(f"\n  [{i+1}/{len(frame_paths)}] Aligning frame {frame_info.get('index', i+1)}...")
        
        result = align_single_frame(client, frame_path, frame_info, screenshots)
        
        alignment = {
            "frame_index": frame_info.get('index', i + 1),
            "frame_file": frame_path.name,
            "frame_info": frame_info,
            "alignment": result
        }
        
        # 解析匹配结果
        best_match = result.get('best_match')
        if best_match and best_match.get('index'):
            match_idx = best_match['index'] - 1  # 转换为0-based索引
            if 0 <= match_idx < len(screenshots):
                alignment['matched_screenshot'] = screenshots[match_idx].name
                alignment['confidence'] = best_match.get('confidence', 0)
                print(f"    -> Matched: {screenshots[match_idx].name} (confidence: {best_match.get('confidence', 0):.2f})")
            else:
                alignment['matched_screenshot'] = None
                alignment['confidence'] = 0
                print(f"    -> No match (index out of range)")
        else:
            alignment['matched_screenshot'] = None
            alignment['confidence'] = 0
            print(f"    -> No match found")
        
        results.append(alignment)
    
    return results


def main():
    print("=" * 60)
    print("  VIDEO FRAME ALIGNMENT")
    print("=" * 60)
    
    # 初始化
    api_key = load_api_key()
    if not api_key:
        print("Error: No API key found!")
        return
    
    client = Anthropic(api_key=api_key)
    
    # 加载视频分析结果
    video_analysis = load_video_analysis()
    if not video_analysis:
        print("Error: No video analysis found! Run analyze_keyframes.py first.")
        return
    
    # 获取唯一页面
    unique_pages = get_unique_pages(video_analysis)
    print(f"\nUnique pages from video: {len(unique_pages)}")
    
    # 获取静态截图
    screenshots = get_screenshots()
    print(f"Static screenshots available: {len(screenshots)}")
    
    if len(screenshots) == 0:
        print("Error: No screenshots found!")
        return
    
    # 获取视频帧文件
    frame_files = sorted(VIDEO_FRAMES_DIR.glob("*.jpg"))
    print(f"Video frame files: {len(frame_files)}")
    
    # 只处理唯一页面
    pages_to_align = []
    for page in unique_pages:
        idx = page.get('index', 0) - 1
        if 0 <= idx < len(frame_files):
            pages_to_align.append((frame_files[idx], page))
    
    print(f"\nPages to align: {len(pages_to_align)}")
    
    if len(pages_to_align) == 0:
        print("Error: No pages to align!")
        return
    
    # 执行对齐（限制数量以节省API调用）
    max_pages = min(len(pages_to_align), 50)  # 最多处理50个页面
    print(f"Processing first {max_pages} unique pages...")
    
    frame_paths = [p[0] for p in pages_to_align[:max_pages]]
    frame_infos = [p[1] for p in pages_to_align[:max_pages]]
    
    results = align_frames_batch(client, frame_paths, frame_infos, screenshots)
    
    # 保存结果
    output = {
        "product": video_analysis.get('product', 'Unknown'),
        "total_unique_pages": len(unique_pages),
        "aligned_pages": len(results),
        "screenshots_available": len(screenshots),
        "alignments": results
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\nAlignment results saved to: {OUTPUT_FILE}")
    
    # 统计
    print("\n" + "=" * 60)
    print("  ALIGNMENT SUMMARY")
    print("=" * 60)
    
    matched = sum(1 for r in results if r.get('matched_screenshot'))
    unmatched = len(results) - matched
    
    print(f"\nTotal aligned: {len(results)}")
    print(f"Matched: {matched}")
    print(f"Unmatched: {unmatched}")
    
    if matched > 0:
        avg_confidence = sum(r.get('confidence', 0) for r in results if r.get('matched_screenshot')) / matched
        print(f"Average confidence: {avg_confidence:.2f}")
    
    # 按Module统计匹配率
    module_stats = {}
    for r in results:
        module = r.get('frame_info', {}).get('module', 'Unknown')
        if module not in module_stats:
            module_stats[module] = {'matched': 0, 'total': 0}
        module_stats[module]['total'] += 1
        if r.get('matched_screenshot'):
            module_stats[module]['matched'] += 1
    
    print("\nMatch rate by Module:")
    for module, stats in sorted(module_stats.items(), key=lambda x: -x[1]['total']):
        rate = stats['matched'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"  {module}: {stats['matched']}/{stats['total']} ({rate:.0f}%)")


if __name__ == "__main__":
    main()
































































