"""
Generate Store Statistics
汇总所有 App 的商店截图分析数据，生成统计报告
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 数据目录
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads_2024"
REPORTS_DIR = DATA_DIR / "reports"
CSV_DATA_DIR = DATA_DIR / "csv_data"

# 确保目录存在
REPORTS_DIR.mkdir(exist_ok=True)

# 目标 Apps
TARGET_APPS = [
    "AllTrails", "Cal_AI", "Calm", "Fitbit", "Flo", 
    "Headspace", "LADDER", "LoseIt", "MacroFactor", "MyFitnessPal",
    "Noom", "Peloton", "Runna", "Strava", "WeightWatchers", "Yazio"
]


def load_business_data() -> dict:
    """加载业务数据（收入、增长等）"""
    competitors_file = CSV_DATA_DIR / "competitors.json"
    if competitors_file.exists():
        with open(competitors_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_all_analyses() -> list:
    """加载所有 App 的 v2 分析数据"""
    analyses = []
    
    for app_name in TARGET_APPS:
        v2_file = DOWNLOADS_DIR / app_name / "store_analysis_v2.json"
        if v2_file.exists():
            with open(v2_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                analyses.append(data)
    
    return analyses


def generate_statistics(analyses: list) -> dict:
    """生成统计数据"""
    total_apps = len(analyses)
    total_screenshots = sum(a["total_screenshots"] for a in analyses)
    
    # ==========================================
    # 1. 类型分布统计
    # ==========================================
    type_counter = Counter()
    type_by_position = defaultdict(Counter)
    
    for app in analyses:
        for s in app["screenshots"]:
            page_type = s.get("L2_understanding", {}).get("page_type", {}).get("primary", "OTHER")
            position = s.get("position", "P1")
            type_counter[page_type] += 1
            type_by_position[position][page_type] += 1
    
    type_distribution = {}
    for t, count in type_counter.most_common():
        positions = []
        for pos in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]:
            if type_by_position[pos][t] > 0:
                positions.append(pos)
        type_distribution[t] = {
            "count": count,
            "percentage": f"{count / total_screenshots * 100:.1f}%",
            "positions": positions
        }
    
    # ==========================================
    # 2. Position-Type 矩阵
    # ==========================================
    position_type_matrix = {}
    for pos in ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]:
        pos_total = sum(type_by_position[pos].values())
        if pos_total > 0:
            position_type_matrix[pos] = {}
            for t in type_counter.keys():
                count = type_by_position[pos][t]
                pct = count / pos_total * 100 if pos_total > 0 else 0
                position_type_matrix[pos][t] = {
                    "count": count,
                    "percentage": f"{pct:.0f}%"
                }
    
    # ==========================================
    # 3. 设计元素频率
    # ==========================================
    element_counter = Counter()
    
    for app in analyses:
        for s in app["screenshots"]:
            ve = s.get("L1_extraction", {}).get("visual_extraction", {})
            if ve.get("device_mockup", {}).get("present"):
                element_counter["Device_Mockup"] += 1
            if ve.get("food_images", {}).get("present"):
                element_counter["Food_Image"] += 1
            if ve.get("data_visualization", {}).get("present"):
                element_counter["Data_Visualization"] += 1
            if ve.get("human_presence", {}).get("present"):
                element_counter["Human_Presence"] += 1
            bg = ve.get("background_style", "")
            if bg == "gradient":
                element_counter["Gradient_Background"] += 1
            for be in ve.get("brand_elements", []):
                element_counter[f"Brand_{be}"] += 1
    
    element_frequency = {}
    for elem, count in element_counter.most_common(20):
        element_frequency[elem] = {
            "count": count,
            "percentage": f"{count / total_screenshots * 100:.1f}%"
        }
    
    # ==========================================
    # 4. 心理策略覆盖
    # ==========================================
    cialdini_counter = Counter()
    bias_counter = Counter()
    
    for app in analyses:
        for s in app["screenshots"]:
            pt = s.get("L2_understanding", {}).get("psychology_tactics", {})
            for c in pt.get("cialdini_principles", []):
                cialdini_counter[c] += 1
            for b in pt.get("cognitive_biases", []):
                bias_counter[b] += 1
    
    psychology_coverage = {
        "cialdini_principles": {
            k: {"count": v, "percentage": f"{v / total_screenshots * 100:.1f}%"}
            for k, v in cialdini_counter.most_common()
        },
        "cognitive_biases": {
            k: {"count": v, "percentage": f"{v / total_screenshots * 100:.1f}%"}
            for k, v in bias_counter.most_common()
        }
    }
    
    # ==========================================
    # 5. 元素共现分析
    # ==========================================
    cooccurrence = defaultdict(int)
    element_pairs = [
        ("Device_Mockup", "Gradient_Background"),
        ("Data_Visualization", "Device_Mockup"),
        ("Food_Image", "Device_Mockup"),
        ("Human_Presence", "Device_Mockup")
    ]
    
    for app in analyses:
        for s in app["screenshots"]:
            ve = s.get("L1_extraction", {}).get("visual_extraction", {})
            has_device = ve.get("device_mockup", {}).get("present", False)
            has_gradient = ve.get("background_style") == "gradient"
            has_data = ve.get("data_visualization", {}).get("present", False)
            has_food = ve.get("food_images", {}).get("present", False)
            has_human = ve.get("human_presence", {}).get("present", False)
            
            elements = {
                "Device_Mockup": has_device,
                "Gradient_Background": has_gradient,
                "Data_Visualization": has_data,
                "Food_Image": has_food,
                "Human_Presence": has_human
            }
            
            for (e1, e2) in element_pairs:
                if elements.get(e1) and elements.get(e2):
                    cooccurrence[f"{e1}+{e2}"] += 1
    
    element_cooccurrence = {}
    for pair, count in sorted(cooccurrence.items(), key=lambda x: -x[1]):
        element_cooccurrence[pair] = {
            "count": count,
            "percentage": f"{count / total_screenshots * 100:.1f}%"
        }
    
    # ==========================================
    # 6. 序列模式聚类
    # ==========================================
    cluster_counter = Counter()
    cluster_apps = defaultdict(list)
    
    for app in analyses:
        cluster = app.get("overall_analysis", {}).get("sequence_cluster", "unique")
        cluster_counter[cluster] += 1
        cluster_apps[cluster].append(app["app_name"])
    
    sequence_clusters = {}
    for cluster, count in cluster_counter.most_common():
        sequence_clusters[cluster] = {
            "count": count,
            "percentage": f"{count / total_apps * 100:.1f}%",
            "apps": cluster_apps[cluster]
        }
    
    # ==========================================
    # 7. 文案词频分析
    # ==========================================
    headline_words = Counter()
    
    for app in analyses:
        for s in app["screenshots"]:
            headline = s.get("L1_extraction", {}).get("text_extraction", {}).get("headline", "")
            if headline:
                # 简单分词
                words = headline.replace(",", " ").replace(".", " ").replace("!", " ").split()
                for word in words:
                    if len(word) > 2:  # 忽略短词
                        headline_words[word.lower()] += 1
    
    word_frequency = {
        "headlines": {
            k: v for k, v in headline_words.most_common(30)
        }
    }
    
    # ==========================================
    # 8. 设计评分统计
    # ==========================================
    score_sums = defaultdict(float)
    score_counts = defaultdict(int)
    
    for app in analyses:
        for s in app["screenshots"]:
            scores = s.get("L3_design", {}).get("design_scores", {})
            for key, value in scores.items():
                if isinstance(value, (int, float)):
                    score_sums[key] += value
                    score_counts[key] += 1
    
    design_score_averages = {}
    for key in score_sums:
        if score_counts[key] > 0:
            design_score_averages[key] = round(score_sums[key] / score_counts[key], 2)
    
    # ==========================================
    # 9. App 级别汇总
    # ==========================================
    app_summaries = []
    for app in analyses:
        types = [s.get("L2_understanding", {}).get("page_type", {}).get("primary", "OTHER") 
                 for s in app["screenshots"]]
        
        app_summaries.append({
            "app_name": app["app_name"],
            "total_screenshots": app["total_screenshots"],
            "sequence_pattern": app.get("overall_analysis", {}).get("sequence_pattern", ""),
            "sequence_cluster": app.get("overall_analysis", {}).get("sequence_cluster", ""),
            "type_distribution": dict(Counter(types)),
            "avg_design_score": app.get("statistics", {}).get("design_score_averages", {}).get("visual_appeal", 0)
        })
    
    # ==========================================
    # 10. 颜色分析
    # ==========================================
    color_moods = Counter()
    
    for app in analyses:
        for s in app["screenshots"]:
            mood = s.get("L1_extraction", {}).get("visual_extraction", {}).get("color_mood", "")
            if mood:
                color_moods[mood] += 1
    
    color_distribution = {
        k: {"count": v, "percentage": f"{v / total_screenshots * 100:.1f}%"}
        for k, v in color_moods.most_common()
    }
    
    # ==========================================
    # 汇总结果
    # ==========================================
    return {
        "generated_at": datetime.now().isoformat(),
        "sample_size": total_apps,
        "total_screenshots": total_screenshots,
        "type_distribution": type_distribution,
        "position_type_matrix": position_type_matrix,
        "element_frequency": element_frequency,
        "psychology_coverage": psychology_coverage,
        "element_cooccurrence": element_cooccurrence,
        "sequence_clusters": sequence_clusters,
        "word_frequency": word_frequency,
        "design_score_averages": design_score_averages,
        "color_distribution": color_distribution,
        "app_summaries": app_summaries
    }


def generate_design_patterns(analyses: list) -> dict:
    """生成设计模式库"""
    
    # 文案模式
    headline_patterns = []
    for app in analyses:
        for s in app["screenshots"]:
            headline = s.get("L1_extraction", {}).get("text_extraction", {}).get("headline", "")
            page_type = s.get("L2_understanding", {}).get("page_type", {}).get("primary", "")
            if headline:
                headline_patterns.append({
                    "text": headline,
                    "app": app["app_name"],
                    "position": s.get("position", ""),
                    "type": page_type
                })
    
    # 布局模式
    layout_patterns = Counter()
    for app in analyses:
        for s in app["screenshots"]:
            layout = s.get("L3_design", {}).get("layout_pattern", {}).get("template_type", "")
            if layout:
                layout_patterns[layout] += 1
    
    # 颜色方案
    color_schemes = []
    for app in analyses:
        for s in app["screenshots"][:1]:  # 只取第一张
            colors = s.get("L1_extraction", {}).get("visual_extraction", {}).get("dominant_colors", [])
            if colors:
                color_schemes.append({
                    "app": app["app_name"],
                    "colors": colors,
                    "mood": s.get("L1_extraction", {}).get("visual_extraction", {}).get("color_mood", "")
                })
    
    return {
        "generated_at": datetime.now().isoformat(),
        "headline_patterns": headline_patterns,
        "layout_patterns": {
            k: {"count": v, "percentage": f"{v / sum(layout_patterns.values()) * 100:.1f}%"}
            for k, v in layout_patterns.most_common()
        },
        "color_schemes": color_schemes
    }


def generate_vitaflow_recommendations(analyses: list, statistics: dict) -> dict:
    """生成 VitaFlow 设计推荐"""
    
    # 基于统计数据推荐序列
    position_recommendations = {}
    matrix = statistics.get("position_type_matrix", {})
    
    for pos in ["P1", "P2", "P3", "P4", "P5", "P6"]:
        if pos in matrix:
            # 找出该位置最常用的类型
            types_at_pos = matrix[pos]
            sorted_types = sorted(
                [(t, d["count"]) for t, d in types_at_pos.items()],
                key=lambda x: -x[1]
            )
            if sorted_types:
                recommended_type = sorted_types[0][0]
                position_recommendations[pos] = {
                    "recommended_type": recommended_type,
                    "confidence": sorted_types[0][1] / statistics["sample_size"],
                    "alternatives": [t for t, _ in sorted_types[1:3]]
                }
    
    # 推荐的序列模式
    clusters = statistics.get("sequence_clusters", {})
    recommended_cluster = max(clusters.items(), key=lambda x: x[1]["count"])[0] if clusters else "traditional"
    
    # 必备元素
    elements = statistics.get("element_frequency", {})
    must_have_elements = [
        elem for elem, data in elements.items()
        if float(data["percentage"].replace("%", "")) > 50
    ]
    
    # 推荐的心理策略
    psychology = statistics.get("psychology_coverage", {})
    recommended_cialdini = list(psychology.get("cialdini_principles", {}).keys())[:5]
    
    return {
        "generated_at": datetime.now().isoformat(),
        "recommended_sequence": {
            "cluster": recommended_cluster,
            "positions": position_recommendations
        },
        "must_have_elements": must_have_elements,
        "recommended_psychology": recommended_cialdini,
        "design_guidelines": {
            "P1": "Use VP (Value Proposition) - 100% of apps do this",
            "P2": "AI_DEMO or CORE_FUNC - show your key feature",
            "P3": "RESULT_PREVIEW or PERSONALIZATION",
            "P4": "SOCIAL_PROOF - build trust",
            "P5": "Additional features or AUTHORITY",
            "P6": "FREE_TRIAL - conversion CTA"
        }
    }


def main():
    """主函数"""
    print("=" * 60)
    print("[STATS] Generate Store Statistics")
    print("=" * 60)
    print()
    
    # 加载所有分析数据
    print("[1/4] Loading analysis data...")
    analyses = load_all_analyses()
    print(f"  Loaded {len(analyses)} apps")
    
    # 生成统计数据
    print("[2/4] Generating statistics...")
    statistics = generate_statistics(analyses)
    
    stats_file = REPORTS_DIR / "store_statistics.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(statistics, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {stats_file}")
    
    # 生成设计模式库
    print("[3/4] Generating design patterns...")
    patterns = generate_design_patterns(analyses)
    
    patterns_file = REPORTS_DIR / "design_patterns.json"
    with open(patterns_file, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {patterns_file}")
    
    # 生成 VitaFlow 推荐
    print("[4/4] Generating VitaFlow recommendations...")
    recommendations = generate_vitaflow_recommendations(analyses, statistics)
    
    rec_file = REPORTS_DIR / "vitaflow_recommendations.json"
    with open(rec_file, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)
    print(f"  Saved to {rec_file}")
    
    # 打印摘要
    print()
    print("=" * 60)
    print("[SUMMARY]")
    print(f"  Total Apps: {statistics['sample_size']}")
    print(f"  Total Screenshots: {statistics['total_screenshots']}")
    print(f"  Top 3 Page Types:")
    for i, (t, data) in enumerate(list(statistics['type_distribution'].items())[:3], 1):
        print(f"    {i}. {t}: {data['percentage']}")
    print(f"  Recommended Sequence Cluster: {recommendations['recommended_sequence']['cluster']}")
    print("=" * 60)


if __name__ == "__main__":
    main()


