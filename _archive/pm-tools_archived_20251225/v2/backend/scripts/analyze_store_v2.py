"""
Store Screenshot Analysis v2
使用 Claude Opus 4.5 + GPT-5.2 双模型分析商店截图
5层分析框架：真实识别 → 语义理解 → 设计分析 → 竞争洞察 → 设计建议
"""
import os
import sys
import json
import base64
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI
from anthropic import Anthropic

# ============================================================================
# 配置
# ============================================================================

# 数据目录
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads_2024"
REPORTS_DIR = DATA_DIR / "reports"
CONFIG_DIR = DATA_DIR / "config"

# 确保目录存在
REPORTS_DIR.mkdir(exist_ok=True)

# 15个要分析的 App（排除 backup 目录）
TARGET_APPS = [
    "AllTrails", "Cal_AI", "Calm", "Fitbit", "Flo", 
    "Headspace", "LADDER", "LoseIt", "MacroFactor", "MyFitnessPal",
    "Noom", "Peloton", "Runna", "Strava", "WeightWatchers", "Yazio"
]

# ============================================================================
# Prompts
# ============================================================================

STORE_ANALYSIS_PROMPT = """你是一位资深的 App Store 优化(ASO)专家和 UI/UX 研究员，专门分析健康健身类 App 的商店截图设计策略。

## 任务

请仔细观察这张 App Store 商店截图（位置 {position}），进行全面的 5 层分析。

## 重要原则

1. **准确抄录原则**：所有文案必须准确抄录截图中的原文，不要翻译、改写或猜测
2. **完整性原则**：识别所有可见文字，包括小字、水印、数据数字
3. **客观性原则**：基于实际看到的内容分析，不要臆测

## 输出要求

请严格按照以下 JSON 格式输出分析结果：

```json
{{
  "L1_extraction": {{
    "text_extraction": {{
      "headline": "主标题原文",
      "subheadline": "副标题原文（如果有）",
      "body_copy": ["正文内容1", "正文内容2"],
      "cta_button": "按钮文字（如果有）",
      "small_print": ["小字说明1", "小字说明2"],
      "data_numbers": ["出现的数字，如 4.8★, 10M+, 7天"],
      "language": "en/zh/mixed"
    }},
    "visual_extraction": {{
      "dominant_colors": ["#主色1", "#主色2"],
      "color_mood": "warm/cool/neutral/vibrant/muted",
      "layout_type": "centered/split_horizontal/split_vertical/full_bleed/card_based/grid",
      "device_mockup": {{
        "present": true,
        "type": "iphone/android/tablet/none",
        "position": "center/left/right/tilted/multiple"
      }},
      "human_presence": {{
        "present": false,
        "type": "photo/illustration/hands_only/silhouette/none"
      }},
      "food_images": {{
        "present": true,
        "style": "photo/illustration/icon/none"
      }},
      "data_visualization": {{
        "present": true,
        "types": ["pie_chart", "bar_chart", "progress_ring", "number_stat"]
      }},
      "brand_elements": ["logo", "icon", "app_name"],
      "background_style": "solid/gradient/image/pattern/transparent"
    }}
  }},
  "L2_understanding": {{
    "page_type": {{
      "primary": "VP/AI_DEMO/CORE_FUNC/RESULT_PREVIEW/PERSONALIZATION/SOCIAL_PROOF/AUTHORITY/DATA_PROOF/USP/HOW_IT_WORKS/INTEGRATION/CONTENT_PREVIEW/FREE_TRIAL/OTHER",
      "primary_cn": "中文类型名",
      "secondary": "次要类型（可选）"
    }},
    "message_strategy": {{
      "primary_message": "这张图想传达的核心信息",
      "supporting_evidence": "用什么来支撑这个信息",
      "emotional_appeal": "trust/excitement/curiosity/urgency/belonging/achievement/security/simplicity",
      "value_proposition": "传递的价值主张"
    }},
    "psychology_tactics": {{
      "cialdini_principles": ["reciprocity", "commitment", "social_proof", "authority", "liking", "scarcity", "unity"],
      "cognitive_biases": ["primacy_effect", "anchoring", "bandwagon", "loss_aversion", "cognitive_fluency", "novelty"],
      "persuasion_technique": "具体说服技巧描述"
    }}
  }},
  "L3_design": {{
    "visual_hierarchy": {{
      "eye_flow": "top_down/z_pattern/f_pattern/center_out/left_right",
      "focal_point": "视觉焦点位置和元素",
      "information_density": "low/medium/high",
      "hierarchy_score": 4.5
    }},
    "typography": {{
      "headline_style": "bold/light/condensed/regular/italic",
      "headline_size": "extra_large/large/medium/small",
      "text_alignment": "center/left/right/mixed",
      "text_contrast": "high/medium/low"
    }},
    "color_strategy": {{
      "primary_color": "#主色HEX",
      "color_scheme": "monochromatic/complementary/analogous/triadic/neutral",
      "contrast_level": "high/medium/low",
      "brand_color_dominance": "dominant/accent/subtle/absent"
    }},
    "layout_pattern": {{
      "template_type": "device_centered/device_offset/full_bleed/split_screen/floating_elements/editorial",
      "whitespace_usage": "tight/balanced/generous",
      "element_count": 5,
      "symmetry": "symmetric/asymmetric/balanced_asymmetric"
    }},
    "design_scores": {{
      "visual_appeal": 4.5,
      "clarity": 4.5,
      "brand_consistency": 5.0,
      "uniqueness": 3.5
    }}
  }},
  "L4_insights": {{
    "differentiation": {{
      "unique_elements": ["该App独有的元素"],
      "category_conventions": ["遵循的行业惯例"],
      "innovations": ["突破惯例的创新"]
    }},
    "competitive_positioning": "premium/value/specialist/mainstream/disruptor",
    "target_audience_signals": ["目标用户信号"]
  }},
  "L5_recommendations": {{
    "vitaflow_applicability": "highly_relevant/somewhat_relevant/not_relevant",
    "reusable_elements": ["可复用的元素"],
    "avoid_elements": ["应避免的元素"],
    "adaptation_notes": "如何适配到 VitaFlow"
  }}
}}
```

## 页面类型定义

- **VP (Value Proposition)**: 价值主张，核心卖点展示，App 主功能一句话概括
- **AI_DEMO**: AI 功能演示，展示 AI 扫描、识别、分析等智能功能
- **CORE_FUNC**: 核心功能展示，主要功能的详细说明
- **RESULT_PREVIEW**: 效果预览，使用后的结果/成果展示
- **PERSONALIZATION**: 个性化展示，定制计划、个人设置
- **SOCIAL_PROOF**: 社会证明，用户评价、下载量、评分
- **AUTHORITY**: 权威背书，专家推荐、媒体报道、奖项
- **DATA_PROOF**: 数据证明，统计数据、成功率、用户数据
- **USP**: 独特卖点，差异化功能强调
- **HOW_IT_WORKS**: 使用流程，如何使用的步骤说明
- **INTEGRATION**: 生态整合，与其他服务/设备的连接
- **CONTENT_PREVIEW**: 内容预览，课程/文章/食谱等内容展示
- **FREE_TRIAL**: 免费试用提示，试用期说明、入门引导

请基于你看到的截图内容进行分析，确保所有文案都是准确抄录的原文。
"""


# ============================================================================
# 分析服务
# ============================================================================

class StoreAnalysisService:
    """商店截图分析服务"""
    
    def __init__(self):
        self.openai_client: Optional[OpenAI] = None
        self.anthropic_client: Optional[Anthropic] = None
        self._init_clients()
    
    def _init_clients(self):
        """初始化 API 客户端"""
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            print("[OK] OpenAI API configured")
        else:
            print("[--] OpenAI API not configured")
        
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
            print("[OK] Anthropic API configured")
        else:
            print("[--] Anthropic API not configured")
    
    def _load_image_base64(self, image_path: Path) -> str:
        """加载图片并转换为 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _get_media_type(self, filename: str) -> str:
        """根据文件名获取媒体类型"""
        ext = filename.lower().split(".")[-1]
        return {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }.get(ext, "image/png")
    
    def _parse_json_response(self, content: str) -> dict:
        """解析 AI 返回的 JSON 响应"""
        # 尝试提取 JSON
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON parse failed: {e}")
            # 返回空结构
            return self._get_empty_analysis()
    
    def _get_empty_analysis(self) -> dict:
        """返回空分析结构"""
        return {
            "L1_extraction": {
                "text_extraction": {
                    "headline": "",
                    "subheadline": "",
                    "body_copy": [],
                    "cta_button": "",
                    "small_print": [],
                    "data_numbers": [],
                    "language": "en"
                },
                "visual_extraction": {
                    "dominant_colors": [],
                    "color_mood": "neutral",
                    "layout_type": "centered",
                    "device_mockup": {"present": False, "type": "none", "position": "center"},
                    "human_presence": {"present": False, "type": "none"},
                    "food_images": {"present": False, "style": "none"},
                    "data_visualization": {"present": False, "types": []},
                    "brand_elements": [],
                    "background_style": "solid"
                }
            },
            "L2_understanding": {
                "page_type": {"primary": "OTHER", "primary_cn": "其他", "secondary": None},
                "message_strategy": {
                    "primary_message": "",
                    "supporting_evidence": "",
                    "emotional_appeal": "trust",
                    "value_proposition": ""
                },
                "psychology_tactics": {
                    "cialdini_principles": [],
                    "cognitive_biases": [],
                    "persuasion_technique": ""
                }
            },
            "L3_design": {
                "visual_hierarchy": {
                    "eye_flow": "top_down",
                    "focal_point": "",
                    "information_density": "medium",
                    "hierarchy_score": 3.0
                },
                "typography": {
                    "headline_style": "regular",
                    "headline_size": "medium",
                    "text_alignment": "center",
                    "text_contrast": "medium"
                },
                "color_strategy": {
                    "primary_color": "#000000",
                    "color_scheme": "neutral",
                    "contrast_level": "medium",
                    "brand_color_dominance": "subtle"
                },
                "layout_pattern": {
                    "template_type": "device_centered",
                    "whitespace_usage": "balanced",
                    "element_count": 3,
                    "symmetry": "symmetric"
                },
                "design_scores": {
                    "visual_appeal": 3.0,
                    "clarity": 3.0,
                    "brand_consistency": 3.0,
                    "uniqueness": 3.0
                }
            },
            "L4_insights": {
                "differentiation": {
                    "unique_elements": [],
                    "category_conventions": [],
                    "innovations": []
                },
                "competitive_positioning": "mainstream",
                "target_audience_signals": []
            },
            "L5_recommendations": {
                "vitaflow_applicability": "somewhat_relevant",
                "reusable_elements": [],
                "avoid_elements": [],
                "adaptation_notes": ""
            }
        }
    
    async def analyze_with_opus(self, image_base64: str, position: str, media_type: str = "image/png") -> dict:
        """使用 Claude Opus 4.5 进行 5 层分析"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        prompt = STORE_ANALYSIS_PROMPT.format(position=position)
        
        response = self.anthropic_client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        content = response.content[0].text
        return self._parse_json_response(content)
    
    async def analyze_with_gpt52(self, image_base64: str, position: str, media_type: str = "image/png") -> dict:
        """使用 GPT-5.2 进行 5 层分析"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        prompt = STORE_ANALYSIS_PROMPT.format(position=position)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=4000,
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        return self._parse_json_response(content)
    
    async def analyze_screenshot(self, image_path: Path, index: int) -> dict:
        """
        分析单张商店截图
        优先使用 Opus 4.5，如果失败则使用 GPT-5.2
        """
        position = f"P{index}"
        media_type = self._get_media_type(image_path.name)
        image_base64 = self._load_image_base64(image_path)
        
        analysis = None
        model_used = None
        
        # 优先使用 Opus 4.5
        if self.anthropic_client:
            try:
                analysis = await self.analyze_with_opus(image_base64, position, media_type)
                model_used = "claude-opus-4-5-20251101"
            except Exception as e:
                print(f"  [WARN] Opus failed: {e}")
        
        # 备选 GPT-5.2
        if analysis is None and self.openai_client:
            try:
                analysis = await self.analyze_with_gpt52(image_base64, position, media_type)
                model_used = "gpt-5.2"
            except Exception as e:
                print(f"  [WARN] GPT-5.2 failed: {e}")
        
        if analysis is None:
            analysis = self._get_empty_analysis()
            model_used = "fallback"
        
        # 添加元数据
        result = {
            "index": index,
            "filename": image_path.name,
            "position": position,
            "model_used": model_used,
            **analysis
        }
        
        return result
    
    async def analyze_app(self, app_name: str) -> dict:
        """分析单个 App 的所有商店截图"""
        app_dir = DOWNLOADS_DIR / app_name
        store_dir = app_dir / "store"
        
        if not store_dir.exists():
            print(f"  [WARN] {app_name} has no store dir")
            return None
        
        # 获取所有截图
        screenshots = sorted([
            f for f in store_dir.iterdir()
            if f.suffix.lower() == ".png" and f.name.startswith("screenshot_")
        ])
        
        if not screenshots:
            print(f"  [WARN] {app_name} has no store screenshots")
            return None
        
        print(f"  [INFO] Found {len(screenshots)} screenshots")
        
        # 逐张分析
        analyses = []
        for i, screenshot in enumerate(screenshots, 1):
            print(f"    [{i}/{len(screenshots)}] Analyzing {screenshot.name}...")
            try:
                result = await self.analyze_screenshot(screenshot, i)
                analyses.append(result)
                print(f"    [OK] Type: {result.get('L2_understanding', {}).get('page_type', {}).get('primary', 'N/A')}")
            except Exception as e:
                print(f"    [FAIL] {e}")
                analyses.append({
                    "index": i,
                    "filename": screenshot.name,
                    "position": f"P{i}",
                    "error": str(e),
                    **self._get_empty_analysis()
                })
            
            # 避免 rate limit
            await asyncio.sleep(2)
        
        # 生成整体分析
        overall = self._generate_overall_analysis(analyses)
        statistics = self._generate_statistics(analyses)
        
        # 组装结果
        result = {
            "app_name": app_name,
            "total_screenshots": len(screenshots),
            "analyzed_at": datetime.now().isoformat(),
            "model": "claude-opus-4-5-20251101 / gpt-5.2",
            "schema_version": "v2",
            "screenshots": analyses,
            "overall_analysis": overall,
            "statistics": statistics
        }
        
        return result
    
    def _generate_overall_analysis(self, analyses: list) -> dict:
        """生成整体分析"""
        # 提取序列模式
        types = [a.get("L2_understanding", {}).get("page_type", {}).get("primary", "OTHER") for a in analyses]
        sequence_pattern = " → ".join(types)
        
        # 判断序列聚类
        if "AI_DEMO" in types[:3]:
            cluster = "ai_driven"
        elif "AUTHORITY" in types[:3]:
            cluster = "authority_led"
        elif "SOCIAL_PROOF" in types[:3]:
            cluster = "social_first"
        elif types[0] == "VP":
            cluster = "traditional"
        else:
            cluster = "unique"
        
        # 收集优缺点
        strengths = []
        weaknesses = []
        
        # 分析设计得分
        scores = []
        for a in analyses:
            ds = a.get("L3_design", {}).get("design_scores", {})
            if ds:
                scores.append(ds)
        
        if scores:
            avg_appeal = sum(s.get("visual_appeal", 0) for s in scores) / len(scores)
            avg_clarity = sum(s.get("clarity", 0) for s in scores) / len(scores)
            
            if avg_appeal >= 4.0:
                strengths.append(f"视觉吸引力高 ({avg_appeal:.1f}/5)")
            if avg_clarity >= 4.0:
                strengths.append(f"信息传达清晰 ({avg_clarity:.1f}/5)")
            if avg_appeal < 3.5:
                weaknesses.append(f"视觉吸引力待提升 ({avg_appeal:.1f}/5)")
        
        # 收集关键启示
        takeaways = []
        for a in analyses:
            rec = a.get("L5_recommendations", {})
            if rec.get("vitaflow_applicability") == "highly_relevant":
                elements = rec.get("reusable_elements", [])
                if elements:
                    takeaways.extend(elements[:2])
        
        return {
            "sequence_pattern": sequence_pattern,
            "sequence_cluster": cluster,
            "narrative_arc": f"从{types[0]}开始，以{types[-1]}结束" if types else "",
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "key_takeaways": list(set(takeaways))[:5]
        }
    
    def _generate_statistics(self, analyses: list) -> dict:
        """生成统计数据"""
        # 类型分布
        type_dist = {}
        for a in analyses:
            t = a.get("L2_understanding", {}).get("page_type", {}).get("primary", "OTHER")
            type_dist[t] = type_dist.get(t, 0) + 1
        
        # 元素频率
        element_freq = {}
        for a in analyses:
            ve = a.get("L1_extraction", {}).get("visual_extraction", {})
            if ve.get("device_mockup", {}).get("present"):
                element_freq["Device_Mockup"] = element_freq.get("Device_Mockup", 0) + 1
            if ve.get("food_images", {}).get("present"):
                element_freq["Food_Image"] = element_freq.get("Food_Image", 0) + 1
            if ve.get("data_visualization", {}).get("present"):
                element_freq["Data_Viz"] = element_freq.get("Data_Viz", 0) + 1
            if ve.get("human_presence", {}).get("present"):
                element_freq["Human"] = element_freq.get("Human", 0) + 1
            for be in ve.get("brand_elements", []):
                element_freq[be] = element_freq.get(be, 0) + 1
        
        # 心理策略覆盖
        cialdini_set = set()
        biases_set = set()
        for a in analyses:
            pt = a.get("L2_understanding", {}).get("psychology_tactics", {})
            cialdini_set.update(pt.get("cialdini_principles", []))
            biases_set.update(pt.get("cognitive_biases", []))
        
        # 设计得分平均
        score_sums = {"visual_appeal": 0, "clarity": 0, "brand_consistency": 0, "uniqueness": 0}
        count = 0
        for a in analyses:
            ds = a.get("L3_design", {}).get("design_scores", {})
            if ds:
                count += 1
                for k in score_sums:
                    score_sums[k] += ds.get(k, 0)
        
        score_avgs = {k: round(v / count, 2) if count > 0 else 0 for k, v in score_sums.items()}
        
        return {
            "type_distribution": type_dist,
            "element_frequency": element_freq,
            "psychology_coverage": {
                "cialdini": list(cialdini_set),
                "cognitive_biases": list(biases_set)
            },
            "design_score_averages": score_avgs
        }


# ============================================================================
# 主函数
# ============================================================================

async def main():
    """主函数"""
    print("=" * 60)
    print("[STORE] Store Screenshot Analysis v2")
    print("=" * 60)
    print()
    
    service = StoreAnalysisService()
    
    # 检查 API 配置
    if not service.anthropic_client and not service.openai_client:
        print("[ERROR] No API key configured")
        print("Please set env: ANTHROPIC_API_KEY or OPENAI_API_KEY")
        return
    
    # 统计需要分析的 App
    apps_to_analyze = []
    for app_name in TARGET_APPS:
        app_dir = DOWNLOADS_DIR / app_name
        store_dir = app_dir / "store"
        output_file = app_dir / "store_analysis_v2.json"
        
        if not store_dir.exists():
            continue
        
        # 检查是否已有 v2 分析
        if output_file.exists():
            print(f"[SKIP] {app_name} - v2 analysis exists")
            continue
        
        apps_to_analyze.append(app_name)
    
    if not apps_to_analyze:
        print("\n[OK] All apps have v2 analysis")
        return
    
    print(f"\n[TODO] {len(apps_to_analyze)} apps to analyze")
    print("-" * 40)
    
    # 逐个分析
    for i, app_name in enumerate(apps_to_analyze, 1):
        print(f"\n[{i}/{len(apps_to_analyze)}] Analyzing {app_name}...")
        
        try:
            result = await service.analyze_app(app_name)
            
            if result:
                # 保存结果
                output_file = DOWNLOADS_DIR / app_name / "store_analysis_v2.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"  [OK] Saved to {output_file}")
        except Exception as e:
            print(f"  [FAIL] {e}")
        
        # 避免 rate limit
        if i < len(apps_to_analyze):
            print("  [WAIT] 5 seconds...")
            await asyncio.sleep(5)
    
    print("\n" + "=" * 60)
    print("[DONE] Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

