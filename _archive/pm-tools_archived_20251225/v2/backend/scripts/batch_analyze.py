"""
Batch Screenshot Analyzer - 批量分析截图
使用 Claude API 分析所有 Onboarding 截图

运行方法:
1. 设置环境变量: export ANTHROPIC_API_KEY=your_key
2. 运行: python batch_analyze.py

注意: 此脚本将分析 828 张截图，预计需要 3-5 小时
"""

import os
import json
import base64
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import anthropic

# 配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads_2024"
ANALYSIS_DIR = DATA_DIR / "analysis"
OUTPUT_DIR = ANALYSIS_DIR / "analysis_opus"

# 加载分析队列
def load_queue() -> dict:
    queue_path = ANALYSIS_DIR / "analysis_queue.json"
    with open(queue_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 图像转 base64
def image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

SYSTEM_PROMPT = """你是一个专业的移动应用UX分析师。请分析这张健康App的Onboarding截图。

输出JSON格式（严格遵守）：
{
  "classification": {
    "functional_purpose": {
      "primary_category": "Value|Identity|Goal|Preference|Plan|Permission|Paywall|Registration|Growth",
      "secondary_type": "具体类型",
      "confidence": 0.0-1.0
    },
    "funnel_stage": {
      "stage": "Awareness|Consideration|Commitment|Activation|Conversion",
      "position_in_funnel": "top|middle|bottom"
    },
    "psychological_tactic": {
      "primary_tactic": "SocialProof|CommitmentConsistency|Scarcity|LossAversion|Personalization|ProgressAchievement|Authority|Reciprocity|None",
      "secondary_tactics": [],
      "tactic_strength": "strong|moderate|weak|none"
    },
    "interaction_pattern": {
      "primary_interaction": "PassiveRead|SingleChoice|MultipleChoice|TextInput|NumberInput|Slider|DatePicker|Toggle|SystemModal|Tap",
      "is_skippable": true|false,
      "input_effort": "none|low|medium|high"
    },
    "ui_pattern": {
      "layout_type": "FullScreenIllustration|Carousel|ListSelection|CardSelection|IconGrid|Form|Calculator|SummaryCard|PaywallScreen|SystemDialog|ChatBubble|ProgressDisplay",
      "has_progress_indicator": true|false,
      "has_illustration": true|false
    },
    "commitment_level": {
      "level": 1-5,
      "commitment_type": "time|information|permission|money|identity"
    }
  },
  "deep_analysis": {
    "design_intent": "设计意图",
    "conversion_impact": "positive|neutral|negative|uncertain"
  }
}

只输出JSON，不要其他文字。"""

def analyze_screenshot(client: anthropic.Anthropic, image_path: Path, app_name: str, index: int, total: int) -> dict:
    """分析单张截图"""
    image_base64 = image_to_base64(image_path)
    position_pct = round((index / total) * 100, 1)
    
    user_prompt = f"""分析这张 {app_name} App 的 Onboarding 截图。
截图序号：第 {index} 张（共 {total} 张）
流程位置：{position_pct}%"""
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",  # 使用 Claude Sonnet 4 进行批量分析
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    )
    
    result_text = response.content[0].text
    
    # 解析JSON
    if "```json" in result_text:
        result_text = result_text.split("```json")[1].split("```")[0]
    elif "```" in result_text:
        result_text = result_text.split("```")[1].split("```")[0]
    
    result = json.loads(result_text.strip())
    
    # 添加元数据
    result["app_name"] = app_name
    result["screenshot_index"] = index
    result["screenshot_filename"] = image_path.name
    result["total_onboarding_screens"] = total
    result["position_percentage"] = position_pct
    result["analysis_method"] = "claude_sonnet_4"
    result["analyzed_at"] = datetime.now().isoformat()
    
    return result

def analyze_app(client: anthropic.Anthropic, app_info: dict) -> List[dict]:
    """分析单个App的所有截图"""
    app_name = app_info["name"]
    start = app_info["onboarding_range"]["start"]
    end = app_info["onboarding_range"]["end"]
    total = end - start + 1
    
    print(f"\n{'='*50}")
    print(f"分析 {app_name}: {total} 张截图")
    print(f"{'='*50}")
    
    # 创建App输出目录
    app_output_dir = OUTPUT_DIR / app_name
    app_output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for i in range(start, end + 1):
        filename = f"{i+1:04d}.png"
        image_path = DOWNLOADS_DIR / app_name / filename
        
        if not image_path.exists():
            print(f"  [跳过] {filename} - 文件不存在")
            continue
        
        # 检查是否已分析
        result_file = app_output_dir / f"{i+1:04d}_analysis.json"
        if result_file.exists():
            print(f"  [已有] {filename}")
            with open(result_file, "r", encoding="utf-8") as f:
                results.append(json.load(f))
            continue
        
        try:
            print(f"  分析 {filename}...", end=" ", flush=True)
            result = analyze_screenshot(client, image_path, app_name, i + 1, total)
            results.append(result)
            
            # 保存单张分析结果
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("✓")
            
            # 避免API限流
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ 错误: {e}")
            continue
    
    # 保存App汇总
    summary_file = app_output_dir / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "app_name": app_name,
            "total_analyzed": len(results),
            "analyzed_at": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"  完成: {len(results)}/{total} 张")
    
    return results

def main():
    # 检查API Key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 请设置 ANTHROPIC_API_KEY 环境变量")
        return
    
    # 初始化客户端
    client = anthropic.Anthropic(api_key=api_key)
    
    # 加载队列
    queue = load_queue()
    
    print("="*60)
    print("Onboarding Screenshot Batch Analyzer")
    print("="*60)
    print(f"总计: {queue['total_apps']} 个App, {queue['total_screenshots']} 张截图")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 分析所有App
    all_results = {}
    total_analyzed = 0
    
    for app_info in queue["apps"]:
        results = analyze_app(client, app_info)
        all_results[app_info["name"]] = results
        total_analyzed += len(results)
    
    # 保存全部结果
    all_results_file = OUTPUT_DIR / "all_results.json"
    with open(all_results_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_apps": len(all_results),
            "total_screenshots": total_analyzed,
            "analyzed_at": datetime.now().isoformat(),
            "apps": all_results
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("分析完成!")
    print(f"总计分析: {total_analyzed} 张截图")
    print(f"结果保存到: {all_results_file}")
    print("="*60)

if __name__ == "__main__":
    main()
