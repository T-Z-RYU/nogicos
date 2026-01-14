"""
Swimlane Analysis Router - 泳道图分析 API
"""
import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter(prefix="/analysis")

# 泳道数据目录
SWIMLANE_DATA_DIR = settings.data_dir / "analysis" / "swimlane"


# ============================================================================
# 跨产品比较 API (放在前面避免路由冲突)
# ============================================================================

@router.get("/compare")
async def compare_all_apps():
    """
    跨产品比较：获取所有 App 的汇总对比数据
    """
    if not SWIMLANE_DATA_DIR.exists():
        return {"apps": [], "aggregate": {}}
    
    apps_data = []
    all_types = {}
    all_patterns = []
    total_screens = 0
    
    for json_file in SWIMLANE_DATA_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            app_id = json_file.stem
            screens = data.get("screens", [])
            summary = data.get("summary", {})
            by_type = summary.get("by_type", {})
            
            # 收集每个 App 的数据
            apps_data.append({
                "appId": app_id,
                "app": data.get("app", app_id),
                "total_screens": len(screens),
                "phases": data.get("phases", []),
                "patterns": data.get("patterns", []),
                "by_type": by_type
            })
            
            # 汇总类型统计
            for type_code, type_info in by_type.items():
                if type_code not in all_types:
                    all_types[type_code] = {
                        "label": type_info.get("label", type_code),
                        "color": type_info.get("color", "#6B7280"),
                        "count": 0,
                        "apps": []
                    }
                all_types[type_code]["count"] += type_info.get("count", 0)
                all_types[type_code]["apps"].append({
                    "appId": app_id,
                    "count": type_info.get("count", 0)
                })
            
            # 收集模式
            for pattern in data.get("patterns", []):
                all_patterns.append({
                    "appId": app_id,
                    **pattern
                })
            
            total_screens += len(screens)
            
        except (json.JSONDecodeError, IOError):
            continue
    
    # 计算类型占比
    for type_code in all_types:
        all_types[type_code]["percentage"] = round(
            all_types[type_code]["count"] / total_screens * 100, 1
        ) if total_screens > 0 else 0
    
    return {
        "apps": apps_data,
        "aggregate": {
            "total_apps": len(apps_data),
            "total_screens": total_screens,
            "type_distribution": all_types,
            "common_patterns": _extract_common_patterns(all_patterns)
        }
    }


@router.get("/compare/type-matrix")
async def get_type_matrix():
    """
    获取类型分布矩阵：每个 App 的每种类型数量
    """
    if not SWIMLANE_DATA_DIR.exists():
        return {"matrix": [], "apps": [], "types": []}
    
    apps = []
    matrix = []
    all_type_codes = set()
    
    for json_file in SWIMLANE_DATA_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            app_id = json_file.stem
            by_type = data.get("summary", {}).get("by_type", {})
            
            apps.append({
                "id": app_id,
                "name": data.get("app", app_id),
                "total": data.get("total_screens", 0)
            })
            
            row = {"appId": app_id, "app": data.get("app", app_id)}
            for type_code, type_info in by_type.items():
                row[type_code] = type_info.get("count", 0)
                all_type_codes.add(type_code)
            
            matrix.append(row)
        except (json.JSONDecodeError, IOError):
            continue
    
    # 类型定义
    type_labels = {
        "W": "Welcome", "Q": "Question", "V": "Value", "S": "Social",
        "A": "Authority", "R": "Result", "D": "Demo", "C": "Commit",
        "G": "Gamified", "L": "Loading", "X": "Permission", "P": "Paywall"
    }
    
    types = [
        {"code": t, "label": type_labels.get(t, t)}
        for t in sorted(all_type_codes)
    ]
    
    return {"matrix": matrix, "apps": apps, "types": types}


@router.get("/compare/phase-structure")
async def get_phase_structure():
    """
    获取阶段结构对比：每个 App 的阶段划分
    """
    if not SWIMLANE_DATA_DIR.exists():
        return {"apps": []}
    
    apps = []
    
    for json_file in SWIMLANE_DATA_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            apps.append({
                "appId": json_file.stem,
                "app": data.get("app", json_file.stem),
                "total_screens": data.get("total_screens", 0),
                "phases": data.get("phases", [])
            })
        except (json.JSONDecodeError, IOError):
            continue
    
    return {"apps": apps}


@router.get("/template/vitaflow")
async def generate_vitaflow_template():
    """
    基于竞品分析生成 VitaFlow onboarding 模板建议
    """
    if not SWIMLANE_DATA_DIR.exists():
        return {"error": "No analysis data found"}
    
    # 收集所有 App 的数据
    all_screens = []
    all_patterns = []
    type_stats = {}
    
    for json_file in SWIMLANE_DATA_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            app_id = json_file.stem
            for screen in data.get("screens", []):
                screen["source_app"] = app_id
                all_screens.append(screen)
            
            for pattern in data.get("patterns", []):
                pattern["source_app"] = app_id
                all_patterns.append(pattern)
            
            for type_code, type_info in data.get("summary", {}).get("by_type", {}).items():
                if type_code not in type_stats:
                    type_stats[type_code] = {"count": 0, "label": type_info.get("label", type_code)}
                type_stats[type_code]["count"] += type_info.get("count", 0)
        except (json.JSONDecodeError, IOError):
            continue
    
    total = sum(t["count"] for t in type_stats.values())
    
    # 计算行业平均配比
    industry_ratio = {}
    for type_code, info in type_stats.items():
        industry_ratio[type_code] = {
            "label": info["label"],
            "percentage": round(info["count"] / total * 100, 1) if total > 0 else 0,
            "count": info["count"]
        }
    
    # 生成推荐的页面序列
    recommended_sequence = _generate_recommended_sequence(all_screens, all_patterns, industry_ratio)
    
    # 提取最佳实践示例
    best_practices = _extract_best_practices(all_screens)
    
    return {
        "industry_ratio": industry_ratio,
        "common_patterns": _extract_common_patterns(all_patterns),
        "recommended_sequence": recommended_sequence,
        "best_practices": best_practices,
        "total_screens_analyzed": len(all_screens),
        "apps_analyzed": len(list(SWIMLANE_DATA_DIR.glob("*.json")))
    }


# ============================================================================
# Swimlane API
# ============================================================================

@router.get("/swimlane")
async def list_swimlane_analyses():
    """
    获取所有可用的泳道图分析列表
    """
    if not SWIMLANE_DATA_DIR.exists():
        return {"analyses": []}
    
    analyses = []
    for json_file in SWIMLANE_DATA_DIR.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                analyses.append({
                    "id": json_file.stem,
                    "app": data.get("app", json_file.stem),
                    "total_screens": data.get("total_screens", 0),
                    "analyzed_at": data.get("analyzed_at"),
                    "summary": {
                        "by_type": data.get("summary", {}).get("by_type", {}),
                        "key_patterns": data.get("summary", {}).get("key_patterns", [])
                    }
                })
        except (json.JSONDecodeError, IOError) as e:
            continue
    
    return {"analyses": analyses}


@router.get("/swimlane/{app_id}")
async def get_swimlane_analysis(app_id: str):
    """
    获取特定 app 的泳道图分析数据
    """
    json_file = SWIMLANE_DATA_DIR / f"{app_id}.json"
    
    if not json_file.exists():
        raise HTTPException(status_code=404, detail=f"Analysis for '{app_id}' not found")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/swimlane/{app_id}/screens")
async def get_swimlane_screens(
    app_id: str,
    start: int = 0,
    limit: int = 100,
    type_filter: Optional[str] = None
):
    """
    分页获取泳道图截图数据，支持按类型筛选
    """
    json_file = SWIMLANE_DATA_DIR / f"{app_id}.json"
    
    if not json_file.exists():
        raise HTTPException(status_code=404, detail=f"Analysis for '{app_id}' not found")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        screens = data.get("screens", [])
        
        # 按类型筛选
        if type_filter:
            screens = [s for s in screens if s.get("primary_type") == type_filter]
        
        # 分页
        total = len(screens)
        paginated = screens[start:start + limit]
        
        return {
            "screens": paginated,
            "total": total,
            "start": start,
            "limit": limit,
            "has_more": start + limit < total
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON data: {str(e)}")


@router.get("/swimlane/{app_id}/screen/{index}")
async def get_screen_detail(app_id: str, index: int):
    """
    获取单个截图的详细信息
    """
    json_file = SWIMLANE_DATA_DIR / f"{app_id}.json"
    
    if not json_file.exists():
        raise HTTPException(status_code=404, detail=f"Analysis for '{app_id}' not found")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        screens = data.get("screens", [])
        
        # 查找对应索引的截图
        for screen in screens:
            if screen.get("index") == index:
                return screen
        
        raise HTTPException(status_code=404, detail=f"Screen {index} not found")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON data: {str(e)}")


@router.get("/swimlane/{app_id}/summary")
async def get_swimlane_summary(app_id: str):
    """
    获取泳道图分析摘要统计
    """
    json_file = SWIMLANE_DATA_DIR / f"{app_id}.json"
    
    if not json_file.exists():
        raise HTTPException(status_code=404, detail=f"Analysis for '{app_id}' not found")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {
            "app": data.get("app"),
            "total_screens": data.get("total_screens"),
            "analyzed_at": data.get("analyzed_at"),
            "taxonomy_version": data.get("taxonomy_version"),
            "summary": data.get("summary", {}),
            "flow_patterns": data.get("flow_patterns", {}),
            "design_insights": data.get("design_insights", {})
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON data: {str(e)}")


@router.get("/swimlane/{app_id}/types")
async def get_screen_types(app_id: str):
    """
    获取页面类型统计
    """
    json_file = SWIMLANE_DATA_DIR / f"{app_id}.json"
    
    if not json_file.exists():
        raise HTTPException(status_code=404, detail=f"Analysis for '{app_id}' not found")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        by_type = data.get("summary", {}).get("by_type", {})
        
        return {
            "types": by_type,
            "type_list": [
                {"code": code, **info}
                for code, info in by_type.items()
            ]
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON data: {str(e)}")


# ============================================================================
# 帮助函数
# ============================================================================

def _extract_common_patterns(all_patterns: list) -> list:
    """提取多个 App 共有的模式"""
    pattern_counts = {}
    for p in all_patterns:
        pattern_name = p.get("pattern", "")
        if pattern_name not in pattern_counts:
            pattern_counts[pattern_name] = {
                "pattern": pattern_name,
                "name": p.get("name", ""),
                "interpretation": p.get("interpretation", ""),
                "apps": [],
                "total_occurrences": 0
            }
        pattern_counts[pattern_name]["apps"].append(p.get("appId") or p.get("source_app"))
        pattern_counts[pattern_name]["total_occurrences"] += p.get("occurrences", 1)
    
    # 按出现的 App 数量排序
    common = sorted(
        pattern_counts.values(),
        key=lambda x: len(x["apps"]),
        reverse=True
    )
    return common


def _generate_recommended_sequence(screens: list, patterns: list, ratio: dict) -> list:
    """基于行业数据动态生成推荐的 VitaFlow onboarding 页面序列"""
    
    # 目标总页数：基于行业平均（约 50-60 页是合理的精简版本）
    TARGET_PAGES = 55
    
    # 页面模板库 - 每种类型的可选页面
    PAGE_TEMPLATES = {
        "W": [  # Welcome (4.2% ≈ 2-3页)
            {"name": "品牌启动页", "purpose": "建立第一印象", "psychology": ["Brand Recognition", "First Impression"], "ui_pattern": "Splash Screen", "copy": {"headline": "欢迎来到 VitaFlow", "subheadline": None, "cta": None}},
            {"name": "价值主张", "purpose": "传达核心价值", "psychology": ["Value Proposition"], "ui_pattern": "Hero with Benefits", "copy": {"headline": "智能追踪，轻松健康", "subheadline": "AI 驱动的个性化健康管理", "cta": "开始体验"}},
            {"name": "用户引导", "purpose": "说明 Onboarding 流程", "psychology": ["Expectation Setting"], "ui_pattern": "Progress Preview", "copy": {"headline": "3 分钟定制你的专属计划", "subheadline": "回答几个问题，我们来帮你", "cta": "开始"}},
        ],
        "A": [  # Authority (0.5% ≈ 1页)
            {"name": "专家背书", "purpose": "建立专业信任", "psychology": ["Authority", "Trust Building"], "ui_pattern": "Expert Testimonial", "copy": {"headline": "#1 营养师推荐应用", "subheadline": "基于 1000+ 位专业营养师调研", "cta": "继续"}},
        ],
        "S": [  # Social (2.4% ≈ 2页)
            {"name": "用户规模展示", "purpose": "展示社会认同", "psychology": ["Social Proof", "Bandwagon Effect"], "ui_pattern": "Statistics Display", "copy": {"headline": "加入 500 万+ 用户", "subheadline": "他们已经成功改变了生活", "cta": "继续"}},
            {"name": "用户评价", "purpose": "真实用户证言", "psychology": ["Social Proof", "Trust Building"], "ui_pattern": "Testimonial Cards", "copy": {"headline": "看看他们怎么说", "subheadline": None, "cta": "继续"}},
        ],
        "Q": [  # Question (41.1% ≈ 22-25页)
            {"name": "主要目标", "purpose": "了解核心目标", "psychology": ["Goal Setting", "Personalization"], "ui_pattern": "Single Select Cards", "copy": {"headline": "你的主要目标是什么？", "subheadline": "选择最符合你的选项", "cta": "继续"}},
            {"name": "性别选择", "purpose": "收集基础生理数据", "psychology": ["Personalization"], "ui_pattern": "Binary Choice", "copy": {"headline": "你的生理性别是？", "subheadline": "用于计算基础代谢率", "cta": "继续"}},
            {"name": "出生日期", "purpose": "计算年龄相关代谢", "psychology": ["Personalization"], "ui_pattern": "Date Picker", "copy": {"headline": "你的出生日期？", "subheadline": None, "cta": "继续"}},
            {"name": "身高输入", "purpose": "收集身体数据", "psychology": ["Body Data"], "ui_pattern": "Scroll Picker", "copy": {"headline": "你的身高是？", "subheadline": None, "cta": "继续"}},
            {"name": "体重输入", "purpose": "收集身体数据", "psychology": ["Body Data"], "ui_pattern": "Scroll Picker", "copy": {"headline": "你的当前体重是？", "subheadline": None, "cta": "继续"}},
            {"name": "目标体重", "purpose": "设定具体目标", "psychology": ["Goal Setting", "Commitment"], "ui_pattern": "Slider Input", "copy": {"headline": "你的目标体重是？", "subheadline": "我们会帮你制定计划", "cta": "设定目标"}},
            {"name": "活动水平", "purpose": "评估日常活动量", "psychology": ["Activity Level"], "ui_pattern": "Single Select List", "copy": {"headline": "你的日常活动水平？", "subheadline": "这会影响你的热量目标", "cta": "继续"}},
            {"name": "运动频率", "purpose": "了解运动习惯", "psychology": ["Activity Level"], "ui_pattern": "Single Select Cards", "copy": {"headline": "你每周运动几次？", "subheadline": None, "cta": "继续"}},
            {"name": "运动类型", "purpose": "了解运动偏好", "psychology": ["Personalization"], "ui_pattern": "Multi Select Grid", "copy": {"headline": "你喜欢什么运动？", "subheadline": "可多选", "cta": "继续"}},
            {"name": "饮食偏好", "purpose": "了解饮食习惯", "psychology": ["Personalization"], "ui_pattern": "Single Select List", "copy": {"headline": "你的饮食方式？", "subheadline": None, "cta": "继续"}},
            {"name": "饮食限制", "purpose": "了解过敏/禁忌", "psychology": ["Personalization"], "ui_pattern": "Multi Select Tags", "copy": {"headline": "有什么饮食限制吗？", "subheadline": "可多选，没有就跳过", "cta": "继续"}},
            {"name": "用餐习惯", "purpose": "了解进餐模式", "psychology": ["Behavioral Data"], "ui_pattern": "Single Select Cards", "copy": {"headline": "你通常一天吃几餐？", "subheadline": None, "cta": "继续"}},
            {"name": "早餐时间", "purpose": "了解时间偏好", "psychology": ["Behavioral Data"], "ui_pattern": "Time Picker", "copy": {"headline": "你通常几点吃早餐？", "subheadline": None, "cta": "继续"}},
            {"name": "午餐时间", "purpose": "了解时间偏好", "psychology": ["Behavioral Data"], "ui_pattern": "Time Picker", "copy": {"headline": "你通常几点吃午餐？", "subheadline": None, "cta": "继续"}},
            {"name": "晚餐时间", "purpose": "了解时间偏好", "psychology": ["Behavioral Data"], "ui_pattern": "Time Picker", "copy": {"headline": "你通常几点吃晚餐？", "subheadline": None, "cta": "继续"}},
            {"name": "饮水习惯", "purpose": "了解水分摄入", "psychology": ["Behavioral Data"], "ui_pattern": "Single Select Cards", "copy": {"headline": "你每天喝多少水？", "subheadline": None, "cta": "继续"}},
            {"name": "睡眠时长", "purpose": "了解睡眠习惯", "psychology": ["Behavioral Data"], "ui_pattern": "Slider Input", "copy": {"headline": "你每晚睡几个小时？", "subheadline": None, "cta": "继续"}},
            {"name": "减重经历", "purpose": "了解历史尝试", "psychology": ["Personalization"], "ui_pattern": "Single Select List", "copy": {"headline": "你之前尝试过减重吗？", "subheadline": None, "cta": "继续"}},
            {"name": "减重挑战", "purpose": "了解痛点", "psychology": ["Pain Point Discovery"], "ui_pattern": "Multi Select Cards", "copy": {"headline": "减重最大的挑战是什么？", "subheadline": "可多选", "cta": "继续"}},
            {"name": "动力来源", "purpose": "了解深层动机", "psychology": ["Motivation Discovery"], "ui_pattern": "Multi Select Cards", "copy": {"headline": "是什么让你想要改变？", "subheadline": "可多选", "cta": "继续"}},
            {"name": "时间框架", "purpose": "设定预期", "psychology": ["Goal Setting"], "ui_pattern": "Single Select Cards", "copy": {"headline": "你希望多久达成目标？", "subheadline": None, "cta": "继续"}},
            {"name": "追踪偏好", "purpose": "了解使用习惯", "psychology": ["Personalization"], "ui_pattern": "Single Select List", "copy": {"headline": "你更喜欢怎么记录饮食？", "subheadline": None, "cta": "继续"}},
            {"name": "提醒偏好", "purpose": "了解通知偏好", "psychology": ["Personalization"], "ui_pattern": "Multi Select Cards", "copy": {"headline": "你希望我们什么时候提醒你？", "subheadline": "可多选", "cta": "继续"}},
            {"name": "名字输入", "purpose": "个性化称呼", "psychology": ["Personalization"], "ui_pattern": "Text Input", "copy": {"headline": "我们该怎么称呼你？", "subheadline": None, "cta": "继续"}},
        ],
        "V": [  # Value (13.6% ≈ 7-8页)
            {"name": "AI 扫描功能", "purpose": "展示核心功能", "psychology": ["Value Proposition"], "ui_pattern": "Feature Card with Illustration", "copy": {"headline": "AI 智能识别食物", "subheadline": "拍照即可记录卡路里", "cta": "继续"}},
            {"name": "营养分析", "purpose": "展示数据能力", "psychology": ["Value Proposition"], "ui_pattern": "Feature Demo", "copy": {"headline": "全面的营养分析", "subheadline": "追踪碳水、蛋白质、脂肪及微量元素", "cta": "继续"}},
            {"name": "个性化计划", "purpose": "强调定制化", "psychology": ["Personalization", "Value Proposition"], "ui_pattern": "Feature Card", "copy": {"headline": "专为你定制的计划", "subheadline": "根据你的目标和生活方式量身打造", "cta": "继续"}},
            {"name": "进度追踪", "purpose": "展示追踪能力", "psychology": ["Progress Achievement"], "ui_pattern": "Feature Preview", "copy": {"headline": "可视化你的进度", "subheadline": "图表和报告让你清晰了解进展", "cta": "继续"}},
            {"name": "社区支持", "purpose": "展示社交功能", "psychology": ["Social Support"], "ui_pattern": "Feature Card", "copy": {"headline": "加入健康社区", "subheadline": "与志同道合的人一起进步", "cta": "继续"}},
            {"name": "专家指导", "purpose": "展示专业支持", "psychology": ["Authority", "Value Proposition"], "ui_pattern": "Feature Card", "copy": {"headline": "获得专业指导", "subheadline": "营养师团队支持你的每一步", "cta": "继续"}},
            {"name": "食谱推荐", "purpose": "展示内容价值", "psychology": ["Value Proposition"], "ui_pattern": "Content Preview", "copy": {"headline": "海量健康食谱", "subheadline": "每天为你推荐美味又健康的选择", "cta": "继续"}},
            {"name": "成功案例", "purpose": "展示效果证明", "psychology": ["Social Proof", "Value Proposition"], "ui_pattern": "Before/After Comparison", "copy": {"headline": "看看他们的改变", "subheadline": None, "cta": "继续"}},
        ],
        "C": [  # Commit (2.9% ≈ 2页)
            {"name": "目标确认", "purpose": "强化承诺", "psychology": ["Commitment & Consistency"], "ui_pattern": "Goal Summary Card", "copy": {"headline": "确认你的目标", "subheadline": "减重 5kg，8 周内达成", "cta": "这是我的目标"}},
            {"name": "承诺宣言", "purpose": "心理承诺", "psychology": ["Commitment & Consistency", "Public Commitment"], "ui_pattern": "Long Press Commitment", "copy": {"headline": "我承诺会坚持", "subheadline": "长按确认你的决心", "cta": "长按承诺"}},
        ],
        "G": [  # Gamified (2.7% ≈ 2页)
            {"name": "进度庆祝", "purpose": "强化积极情绪", "psychology": ["Progress Achievement", "Positive Reinforcement"], "ui_pattern": "Celebration Animation", "copy": {"headline": "太棒了！你已完成一半", "subheadline": "继续加油！", "cta": "继续"}},
            {"name": "里程碑", "purpose": "增加成就感", "psychology": ["Achievement Unlocking"], "ui_pattern": "Badge Unlock", "copy": {"headline": "获得「新手」徽章", "subheadline": "你迈出了第一步！", "cta": "继续"}},
        ],
        "L": [  # Loading (5.4% ≈ 3页)
            {"name": "分析加载", "purpose": "创造期待感", "psychology": ["Labor Illusion", "Anticipation"], "ui_pattern": "Progress Animation", "copy": {"headline": "正在分析你的数据...", "subheadline": None, "cta": None}},
            {"name": "计划生成", "purpose": "展示个性化处理", "psychology": ["Labor Illusion", "Value Perception"], "ui_pattern": "Step Progress", "copy": {"headline": "正在生成你的专属计划...", "subheadline": "计算最佳热量 → 分析营养需求 → 定制计划", "cta": None}},
            {"name": "最终准备", "purpose": "转场过渡", "psychology": ["Anticipation"], "ui_pattern": "Loading Dots", "copy": {"headline": "一切就绪...", "subheadline": None, "cta": None}},
        ],
        "R": [  # Result (9.5% ≈ 5页)
            {"name": "计划概览", "purpose": "展示个性化结果", "psychology": ["Personalization", "Value Proposition"], "ui_pattern": "Result Summary Card", "copy": {"headline": "你的专属计划已生成", "subheadline": None, "cta": "查看详情"}},
            {"name": "热量目标", "purpose": "展示关键指标", "psychology": ["Goal Setting"], "ui_pattern": "Metric Display", "copy": {"headline": "每日目标：1,800 卡路里", "subheadline": "基于你的身体数据和目标计算", "cta": "继续"}},
            {"name": "营养配比", "purpose": "展示宏量分布", "psychology": ["Education", "Value Proposition"], "ui_pattern": "Pie Chart", "copy": {"headline": "你的营养配比", "subheadline": "碳水 45% / 蛋白质 30% / 脂肪 25%", "cta": "继续"}},
            {"name": "预期时间线", "purpose": "设定预期", "psychology": ["Goal Setting", "Expectation Management"], "ui_pattern": "Timeline Chart", "copy": {"headline": "预计 8 周达成目标", "subheadline": "按计划执行，每周减少 0.5kg", "cta": "继续"}},
            {"name": "计划详情", "purpose": "展示完整计划", "psychology": ["Value Proposition"], "ui_pattern": "Plan Overview", "copy": {"headline": "这是你的完整计划", "subheadline": None, "cta": "开始使用"}},
        ],
        "X": [  # Permission (3.9% ≈ 2页)
            {"name": "通知权限", "purpose": "获取推送权限", "psychology": ["Permission Pre-priming"], "ui_pattern": "Permission Request with Value", "copy": {"headline": "开启提醒，不错过任何记录", "subheadline": "我们会在用餐时间提醒你", "cta": "开启通知"}},
            {"name": "健康权限", "purpose": "获取健康数据权限", "psychology": ["Permission Pre-priming"], "ui_pattern": "Permission Request with Benefits", "copy": {"headline": "连接 Apple Health", "subheadline": "同步步数和运动数据，获得更准确的建议", "cta": "连接"}},
        ],
        "D": [  # Demo (8.3% ≈ 4-5页)
            {"name": "首页预览", "purpose": "展示产品界面", "psychology": ["Progressive Disclosure"], "ui_pattern": "App Screenshot", "copy": {"headline": "这是你的主页", "subheadline": "一目了然查看今日进度", "cta": "继续"}},
            {"name": "扫描演示", "purpose": "展示核心功能", "psychology": ["Feature Education"], "ui_pattern": "Interactive Demo", "copy": {"headline": "试试 AI 扫描", "subheadline": "对准食物，点击拍照", "cta": "试一试"}},
            {"name": "记录演示", "purpose": "展示使用方法", "psychology": ["Feature Education"], "ui_pattern": "Tutorial Steps", "copy": {"headline": "如何记录一餐", "subheadline": None, "cta": "下一步"}},
            {"name": "报告预览", "purpose": "展示数据价值", "psychology": ["Value Proposition"], "ui_pattern": "Report Preview", "copy": {"headline": "每周获得详细报告", "subheadline": "了解你的饮食模式和进步", "cta": "继续"}},
        ],
        "P": [  # Paywall (5.3% ≈ 3页)
            {"name": "免费 vs Pro", "purpose": "展示付费价值", "psychology": ["Value Proposition", "Loss Aversion"], "ui_pattern": "Feature Comparison", "copy": {"headline": "解锁完整功能", "subheadline": None, "cta": "了解 Pro"}},
            {"name": "定价页", "purpose": "展示价格方案", "psychology": ["Pricing Psychology", "Anchoring"], "ui_pattern": "Pricing Cards", "copy": {"headline": "选择你的计划", "subheadline": "7 天免费试用，随时取消", "cta": "开始免费试用"}},
            {"name": "最后机会", "purpose": "最终转化", "psychology": ["Scarcity", "Loss Aversion", "Urgency"], "ui_pattern": "Special Offer Modal", "copy": {"headline": "限时优惠 50% OFF", "subheadline": "仅限今天，错过不再", "cta": "立即开通"}},
        ],
    }
    
    # 根据行业比例计算每种类型的页数
    type_counts = {}
    for type_code, info in ratio.items():
        percentage = info.get("percentage", 0)
        count = max(1, round(TARGET_PAGES * percentage / 100))
        type_counts[type_code] = min(count, len(PAGE_TEMPLATES.get(type_code, [])))
    
    # 按推荐的流程顺序生成序列
    FLOW_ORDER = [
        ("W", 2),   # 信任建立阶段
        ("A", 1),
        ("S", 1),
        ("Q", 5),   # 目标设定阶段 - 第一批问题
        ("V", 2),   # 价值穿插
        ("Q", 6),   # 数据收集阶段 - 第二批问题
        ("V", 2),   # 价值穿插
        ("Q", 5),   # 数据收集阶段 - 第三批问题
        ("G", 1),   # 中途激励
        ("Q", 4),   # 继续问题
        ("V", 2),   # 价值穿插
        ("Q", 3),   # 最后问题
        ("C", 2),   # 承诺阶段
        ("L", 2),   # 加载/期待
        ("R", 4),   # 结果展示阶段
        ("D", 3),   # 功能演示
        ("X", 2),   # 权限请求
        ("G", 1),   # 庆祝
        ("L", 1),   # 最终加载
        ("P", 3),   # 转化阶段
    ]
    
    sequence = []
    used_templates = {t: 0 for t in PAGE_TEMPLATES}
    index = 1
    
    for type_code, count in FLOW_ORDER:
        templates = PAGE_TEMPLATES.get(type_code, [])
        for _ in range(count):
            if used_templates[type_code] < len(templates):
                template = templates[used_templates[type_code]]
                sequence.append({
                    "index": index,
                    "type": type_code,
                    "name": template["name"],
                    "purpose": template["purpose"],
                    "psychology": template["psychology"],
                    "ui_pattern": template["ui_pattern"],
                    "recommended_copy": template["copy"]
                })
                used_templates[type_code] += 1
                index += 1
    
    return sequence


def _extract_best_practices(screens: list) -> dict:
    """提取各类型页面的最佳实践示例"""
    best = {}
    
    # 按类型分组，选择高置信度的示例
    by_type = {}
    for s in screens:
        t = s.get("primary_type", "")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(s)
    
    for type_code, type_screens in by_type.items():
        # 按置信度排序，取前 3 个
        sorted_screens = sorted(
            type_screens,
            key=lambda x: x.get("confidence", 0),
            reverse=True
        )[:3]
        
        best[type_code] = [
            {
                "source_app": s.get("source_app"),
                "filename": s.get("filename"),
                "ui_pattern": s.get("ui_pattern"),
                "copy": s.get("copy", {}),
                "insight": s.get("insight"),
                "confidence": s.get("confidence")
            }
            for s in sorted_screens
        ]
    
    return best

