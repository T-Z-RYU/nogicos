"""
Migrate Store Analysis v1 to v2
将现有的 store_analysis.json 转换为 v2 格式
生成合理的默认值用于前端开发和演示
"""
import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 数据目录
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads_2024"

# 目标 Apps
TARGET_APPS = [
    "AllTrails", "Cal_AI", "Calm", "Fitbit", "Flo", 
    "Headspace", "LADDER", "LoseIt", "MacroFactor", "MyFitnessPal",
    "Noom", "Peloton", "Runna", "Strava", "WeightWatchers", "Yazio"
]

# 页面类型定义
PAGE_TYPE_MAP = {
    "VP": {"cn": "Value Proposition", "desc": "Price, features, benefits"},
    "AI_DEMO": {"cn": "AI Demo", "desc": "AI scanning, recognition"},
    "CORE_FUNC": {"cn": "Core Functions", "desc": "Main features"},
    "RESULT_PREVIEW": {"cn": "Result Preview", "desc": "Outcome display"},
    "PERSONALIZATION": {"cn": "Personalization", "desc": "Custom plans"},
    "SOCIAL_PROOF": {"cn": "Social Proof", "desc": "Reviews, ratings"},
    "AUTHORITY": {"cn": "Authority", "desc": "Expert endorsements"},
    "DATA_PROOF": {"cn": "Data Proof", "desc": "Statistics, numbers"},
    "USP": {"cn": "Unique Selling Point", "desc": "Differentiation"},
    "HOW_IT_WORKS": {"cn": "How It Works", "desc": "Process steps"},
    "INTEGRATION": {"cn": "Integration", "desc": "Ecosystem, connections"},
    "CONTENT_PREVIEW": {"cn": "Content Preview", "desc": "Courses, recipes"},
    "FREE_TRIAL": {"cn": "Free Trial", "desc": "Trial offer, CTA"},
    "OTHER": {"cn": "Other", "desc": "Miscellaneous"}
}

# 颜色调色板（根据 App 类型）
APP_COLORS = {
    "Cal_AI": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
    "Noom": ["#FF9500", "#00C853", "#FFFFFF"],
    "MyFitnessPal": ["#0077ED", "#00C853", "#FFFFFF"],
    "Yazio": ["#00BFA5", "#7C4DFF", "#FFFFFF"],
    "Flo": ["#FF6B9D", "#9C27B0", "#FFFFFF"],
    "Calm": ["#4A90D9", "#6B8DD6", "#1C3A5F"],
    "Headspace": ["#FF8F3F", "#F5C063", "#FFFFFF"],
    "Fitbit": ["#00B0B9", "#1A1A2E", "#FFFFFF"],
    "Strava": ["#FC4C02", "#1A1A1A", "#FFFFFF"],
    "Peloton": ["#DF1C2F", "#000000", "#FFFFFF"],
    "Runna": ["#00D4AA", "#1A1A1A", "#FFFFFF"],
    "AllTrails": ["#2F9E44", "#4B4B4B", "#FFFFFF"],
    "LADDER": ["#000000", "#F5B800", "#FFFFFF"],
    "LoseIt": ["#FF6B00", "#00A651", "#FFFFFF"],
    "MacroFactor": ["#6366F1", "#1E1B4B", "#FFFFFF"],
    "WeightWatchers": ["#0055A4", "#9747FF", "#FFFFFF"]
}

# 常见心理策略
CIALDINI_POOL = ["reciprocity", "commitment", "social_proof", "authority", "liking", "scarcity", "unity"]
BIAS_POOL = ["primacy_effect", "recency_effect", "anchoring", "bandwagon", "loss_aversion", 
             "endowment_effect", "cognitive_fluency", "novelty", "social_comparison", "authority_bias"]


def convert_v1_to_v2(v1_data: dict, app_name: str) -> dict:
    """将 v1 数据转换为 v2 格式"""
    screenshots_v2 = []
    colors = APP_COLORS.get(app_name, ["#6366F1", "#1E1B4B", "#FFFFFF"])
    
    for s in v1_data.get("screenshots", []):
        idx = s.get("index", 1)
        pos = s.get("position", f"P{idx}")
        
        # 获取 v1 数据
        v1_type = s.get("type", "OTHER")
        v1_copy = s.get("copywriting", {})
        v1_elements = s.get("elements", [])
        v1_psychology = s.get("psychology", {})
        v1_scores = s.get("design_scores", {})
        v1_analysis = s.get("analysis", "")
        
        # 转换为 v2 格式
        screenshot_v2 = {
            "index": idx,
            "filename": s.get("filename", f"screenshot_{idx:02d}.png"),
            "position": pos,
            "model_used": "migrated_from_v1",
            "L1_extraction": {
                "text_extraction": {
                    "headline": v1_copy.get("headline", ""),
                    "subheadline": v1_copy.get("subheadline", ""),
                    "body_copy": [],
                    "cta_button": "",
                    "small_print": [],
                    "data_numbers": [],
                    "language": "en"
                },
                "visual_extraction": {
                    "dominant_colors": colors,
                    "color_mood": random.choice(["warm", "cool", "vibrant"]),
                    "layout_type": "centered" if "Device_Mockup" in v1_elements else "full_bleed",
                    "device_mockup": {
                        "present": "Device_Mockup" in v1_elements,
                        "type": "iphone" if "Device_Mockup" in v1_elements else "none",
                        "position": "center"
                    },
                    "human_presence": {
                        "present": "Human" in v1_elements or "Person" in str(v1_elements),
                        "type": "photo" if "Human" in v1_elements else "none"
                    },
                    "food_images": {
                        "present": "Food_Image" in v1_elements or "food" in str(v1_elements).lower(),
                        "style": "photo" if "Food_Image" in v1_elements else "none"
                    },
                    "data_visualization": {
                        "present": any(x in v1_elements for x in ["Stat_Number", "Chart", "Graph", "Data"]),
                        "types": ["number_stat"] if "Stat_Number" in v1_elements else []
                    },
                    "brand_elements": ["app_name"] if "Headline" in v1_elements else [],
                    "background_style": "gradient" if "Gradient_BG" in v1_elements else "solid"
                }
            },
            "L2_understanding": {
                "page_type": {
                    "primary": v1_type,
                    "primary_cn": PAGE_TYPE_MAP.get(v1_type, {}).get("cn", v1_type),
                    "secondary": None
                },
                "message_strategy": {
                    "primary_message": v1_analysis[:100] if v1_analysis else PAGE_TYPE_MAP.get(v1_type, {}).get("desc", ""),
                    "supporting_evidence": "Visual elements and copywriting",
                    "emotional_appeal": random.choice(["trust", "excitement", "achievement", "simplicity"]),
                    "value_proposition": v1_copy.get("headline", "")
                },
                "psychology_tactics": {
                    "cialdini_principles": v1_psychology.get("cialdini", random.sample(CIALDINI_POOL, 2)),
                    "cognitive_biases": v1_psychology.get("cognitive_biases", random.sample(BIAS_POOL, 2)),
                    "persuasion_technique": v1_analysis[:150] if v1_analysis else ""
                }
            },
            "L3_design": {
                "visual_hierarchy": {
                    "eye_flow": "top_down",
                    "focal_point": "Headline and device mockup" if "Device_Mockup" in v1_elements else "Headline",
                    "information_density": "medium",
                    "hierarchy_score": v1_scores.get("visual_hierarchy", 4.0)
                },
                "typography": {
                    "headline_style": "bold",
                    "headline_size": "large",
                    "text_alignment": "center",
                    "text_contrast": "high"
                },
                "color_strategy": {
                    "primary_color": colors[0],
                    "color_scheme": "complementary",
                    "contrast_level": "high",
                    "brand_color_dominance": "dominant"
                },
                "layout_pattern": {
                    "template_type": "device_centered" if "Device_Mockup" in v1_elements else "full_bleed",
                    "whitespace_usage": "balanced",
                    "element_count": len(v1_elements),
                    "symmetry": "symmetric"
                },
                "design_scores": {
                    "visual_appeal": v1_scores.get("visual_hierarchy", 4.0),
                    "clarity": v1_scores.get("readability", 4.0),
                    "brand_consistency": v1_scores.get("brand_consistency", 4.5),
                    "uniqueness": 3.5
                }
            },
            "L4_insights": {
                "differentiation": {
                    "unique_elements": [],
                    "category_conventions": ["Device mockup", "Gradient background"] if "Device_Mockup" in v1_elements else [],
                    "innovations": []
                },
                "competitive_positioning": "mainstream",
                "target_audience_signals": []
            },
            "L5_recommendations": {
                "vitaflow_applicability": "highly_relevant" if v1_type in ["VP", "AI_DEMO", "RESULT_PREVIEW"] else "somewhat_relevant",
                "reusable_elements": v1_elements[:3] if v1_elements else [],
                "avoid_elements": [],
                "adaptation_notes": f"Reference for VitaFlow {pos}"
            }
        }
        
        screenshots_v2.append(screenshot_v2)
    
    # 生成整体分析
    types = [s["L2_understanding"]["page_type"]["primary"] for s in screenshots_v2]
    sequence_pattern = " -> ".join(types)
    
    # 判断序列聚类
    if "AI_DEMO" in types[:3]:
        cluster = "ai_driven"
    elif "AUTHORITY" in types[:3]:
        cluster = "authority_led"
    elif "SOCIAL_PROOF" in types[:3]:
        cluster = "social_first"
    elif types and types[0] == "VP":
        cluster = "traditional"
    else:
        cluster = "unique"
    
    # 类型分布
    type_dist = {}
    for t in types:
        type_dist[t] = type_dist.get(t, 0) + 1
    
    # 元素频率
    element_freq = {}
    for s in screenshots_v2:
        ve = s["L1_extraction"]["visual_extraction"]
        if ve["device_mockup"]["present"]:
            element_freq["Device_Mockup"] = element_freq.get("Device_Mockup", 0) + 1
        if ve["food_images"]["present"]:
            element_freq["Food_Image"] = element_freq.get("Food_Image", 0) + 1
        if ve["data_visualization"]["present"]:
            element_freq["Data_Viz"] = element_freq.get("Data_Viz", 0) + 1
        if ve["human_presence"]["present"]:
            element_freq["Human"] = element_freq.get("Human", 0) + 1
    
    # 心理策略覆盖
    cialdini_set = set()
    biases_set = set()
    for s in screenshots_v2:
        pt = s["L2_understanding"]["psychology_tactics"]
        cialdini_set.update(pt.get("cialdini_principles", []))
        biases_set.update(pt.get("cognitive_biases", []))
    
    # 设计得分平均
    score_avgs = {"visual_appeal": 0, "clarity": 0, "brand_consistency": 0, "uniqueness": 0}
    for s in screenshots_v2:
        ds = s["L3_design"]["design_scores"]
        for k in score_avgs:
            score_avgs[k] += ds.get(k, 0)
    for k in score_avgs:
        score_avgs[k] = round(score_avgs[k] / len(screenshots_v2), 2) if screenshots_v2 else 0
    
    result = {
        "app_name": app_name,
        "total_screenshots": len(screenshots_v2),
        "analyzed_at": datetime.now().isoformat(),
        "model": "migrated_from_v1",
        "schema_version": "v2",
        "screenshots": screenshots_v2,
        "overall_analysis": {
            "sequence_pattern": sequence_pattern,
            "sequence_cluster": cluster,
            "narrative_arc": f"From {types[0]} to {types[-1]}" if types else "",
            "strengths": v1_data.get("overall_analysis", {}).get("strengths", []),
            "weaknesses": v1_data.get("overall_analysis", {}).get("weaknesses", []),
            "key_takeaways": v1_data.get("overall_analysis", {}).get("recommendations", [])
        },
        "statistics": {
            "type_distribution": type_dist,
            "element_frequency": element_freq,
            "psychology_coverage": {
                "cialdini": list(cialdini_set),
                "cognitive_biases": list(biases_set)
            },
            "design_score_averages": score_avgs
        }
    }
    
    return result


def main():
    """主函数"""
    print("=" * 60)
    print("[MIGRATE] Store Analysis v1 -> v2")
    print("=" * 60)
    print()
    
    migrated = 0
    skipped = 0
    
    for app_name in TARGET_APPS:
        app_dir = DOWNLOADS_DIR / app_name
        v1_file = app_dir / "store_analysis.json"
        v2_file = app_dir / "store_analysis_v2.json"
        
        # 检查是否已有 v2
        if v2_file.exists():
            print(f"[SKIP] {app_name} - v2 already exists")
            skipped += 1
            continue
        
        # 检查是否有 v1
        if not v1_file.exists():
            print(f"[SKIP] {app_name} - no v1 data")
            skipped += 1
            continue
        
        # 读取 v1 数据
        try:
            with open(v1_file, "r", encoding="utf-8") as f:
                v1_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] {app_name} - failed to read v1: {e}")
            continue
        
        # 转换为 v2
        print(f"[MIGRATE] {app_name}...")
        v2_data = convert_v1_to_v2(v1_data, app_name)
        
        # 保存 v2
        with open(v2_file, "w", encoding="utf-8") as f:
            json.dump(v2_data, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] Saved {v2_file.name} ({v2_data['total_screenshots']} screenshots)")
        migrated += 1
    
    print()
    print("=" * 60)
    print(f"[DONE] Migrated: {migrated}, Skipped: {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()


