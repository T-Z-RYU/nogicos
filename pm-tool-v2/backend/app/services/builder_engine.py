"""
Onboarding 构建器规则引擎
基于 8 款竞品分析 + 心理学研究，动态推荐下一步选项
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class PageType(str, Enum):
    W = "W"  # Welcome
    A = "A"  # Authority
    S = "S"  # Social Proof
    Q = "Q"  # Question
    V = "V"  # Value
    C = "C"  # Commit
    G = "G"  # Gamified
    L = "L"  # Loading
    R = "R"  # Result
    X = "X"  # Permission
    D = "D"  # Demo
    P = "P"  # Paywall


class Phase(str, Enum):
    TRUST = "trust"           # 信任建立
    GOAL = "goal"             # 目标设定
    DATA = "data"             # 数据收集
    VALUE = "value"           # 价值展示
    COMMIT = "commit"         # 承诺阶段
    RESULT = "result"         # 结果展示
    PERMISSION = "permission" # 权限请求
    CONVERT = "convert"       # 转化阶段


@dataclass
class PageOption:
    """单个页面选项"""
    id: str
    type: PageType
    name: str
    purpose: str
    psychology: List[str]
    ui_pattern: str
    copy: Dict[str, Optional[str]]
    competitor_refs: List[str]  # 竞品参考
    confidence: str  # "极高", "高", "中"
    research_source: Optional[str] = None


@dataclass
class BuilderState:
    """构建器状态"""
    selected_pages: List[Dict] = field(default_factory=list)
    current_phase: Phase = Phase.TRUST
    consecutive_q_count: int = 0
    has_value_shown: bool = False
    has_social_proof: bool = False
    has_result: bool = False
    has_loading: bool = False
    has_commit: bool = False
    total_q_count: int = 0


# ============================================================================
# 页面模板库
# ============================================================================

PAGE_TEMPLATES: Dict[PageType, List[Dict]] = {
    PageType.W: [
        {
            "id": "w_splash",
            "name": "品牌启动页",
            "purpose": "建立第一印象，传达品牌调性",
            "psychology": ["Brand Recognition", "First Impression"],
            "ui_pattern": "Splash Screen with Logo",
            "copy": {"headline": "欢迎来到 VitaFlow", "subheadline": None, "cta": None},
            "competitor_refs": ["Flo #1", "Noom #1", "MyFitnessPal #1"],
            "confidence": "极高",
            "research": "8/8 竞品使用"
        },
        {
            "id": "w_value_prop",
            "name": "价值主张",
            "purpose": "快速传达核心价值",
            "psychology": ["Value Proposition", "Curiosity"],
            "ui_pattern": "Hero with Benefits List",
            "copy": {"headline": "智能追踪，轻松健康", "subheadline": "AI 驱动的个性化健康管理", "cta": "开始体验"},
            "competitor_refs": ["Cal.AI #2", "Yazio #2"],
            "confidence": "高",
            "research": "6/8 竞品使用"
        },
        {
            "id": "w_how_it_works",
            "name": "流程说明",
            "purpose": "设定预期，减少不确定性",
            "psychology": ["Expectation Setting", "Cognitive Load Reduction"],
            "ui_pattern": "3-Step Preview",
            "copy": {"headline": "3 分钟定制你的专属计划", "subheadline": "回答几个问题，我们来帮你", "cta": "开始"},
            "competitor_refs": ["Noom #3", "WeightWatchers #2"],
            "confidence": "高",
            "research": "Laws of UX - 减少认知负荷"
        },
    ],
    PageType.A: [
        {
            "id": "a_expert",
            "name": "专家背书",
            "purpose": "建立专业信任",
            "psychology": ["Authority", "Trust Building"],
            "ui_pattern": "Expert Testimonial Card",
            "copy": {"headline": "#1 营养师推荐应用", "subheadline": "基于 1000+ 位专业营养师调研", "cta": "继续"},
            "competitor_refs": ["Noom #5", "WeightWatchers #4"],
            "confidence": "高",
            "research": "Cialdini 权威原则"
        },
        {
            "id": "a_media",
            "name": "媒体报道",
            "purpose": "第三方信任背书",
            "psychology": ["Authority", "Social Proof"],
            "ui_pattern": "Media Logo Wall",
            "copy": {"headline": "被顶级媒体报道", "subheadline": "Forbes / TechCrunch / Healthline", "cta": "继续"},
            "competitor_refs": ["Flo #4", "Cal.AI #3"],
            "confidence": "中",
            "research": "5/8 竞品使用"
        },
    ],
    PageType.S: [
        {
            "id": "s_user_count",
            "name": "用户规模",
            "purpose": "展示社会认同",
            "psychology": ["Social Proof", "Bandwagon Effect"],
            "ui_pattern": "Big Number Display",
            "copy": {"headline": "加入 500 万+ 用户", "subheadline": "他们已经成功改变了生活", "cta": "继续"},
            "competitor_refs": ["Cal.AI #5", "Flo #3", "Noom #4"],
            "confidence": "极高",
            "research": "+34% 转化率 (testimonialstar 2024)"
        },
        {
            "id": "s_testimonial",
            "name": "用户评价",
            "purpose": "真实用户证言",
            "psychology": ["Social Proof", "Trust Building"],
            "ui_pattern": "Testimonial Cards",
            "copy": {"headline": "看看他们怎么说", "subheadline": None, "cta": "继续"},
            "competitor_refs": ["Flo #6", "MacroFactor #4"],
            "confidence": "高",
            "research": "视频证言 +34% 转化 (testimonialstar 2024)"
        },
        {
            "id": "s_rating",
            "name": "App Store 评分",
            "purpose": "展示用户满意度",
            "psychology": ["Social Proof", "Authority"],
            "ui_pattern": "Rating Display with Stars",
            "copy": {"headline": "4.8 ★ 评分", "subheadline": "来自 10 万+ 用户评价", "cta": "继续"},
            "competitor_refs": ["Cal.AI #4", "Yazio #3"],
            "confidence": "高",
            "research": "7/8 竞品使用"
        },
    ],
    PageType.Q: [
        {
            "id": "q_goal",
            "name": "主要目标",
            "purpose": "了解核心目标，开始个性化",
            "psychology": ["Goal Setting", "Personalization", "Commitment"],
            "ui_pattern": "Single Select Cards",
            "copy": {"headline": "你的主要目标是什么？", "subheadline": "选择最符合你的选项", "cta": "继续"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "承诺一致性原则 (Cialdini)"
        },
        {
            "id": "q_gender",
            "name": "性别选择",
            "purpose": "收集基础生理数据",
            "psychology": ["Personalization"],
            "ui_pattern": "Binary Choice",
            "copy": {"headline": "你的生理性别是？", "subheadline": "用于计算基础代谢率", "cta": "继续"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "个性化 +20% 参与度 (moldstud 2025)"
        },
        {
            "id": "q_birthday",
            "name": "出生日期",
            "purpose": "计算年龄相关代谢",
            "psychology": ["Personalization"],
            "ui_pattern": "Date Picker",
            "copy": {"headline": "你的出生日期？", "subheadline": None, "cta": "继续"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "8/8 竞品收集"
        },
        {
            "id": "q_height",
            "name": "身高输入",
            "purpose": "收集身体数据",
            "psychology": ["Personalization"],
            "ui_pattern": "Scroll Picker",
            "copy": {"headline": "你的身高是？", "subheadline": None, "cta": "继续"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "8/8 竞品收集"
        },
        {
            "id": "q_weight",
            "name": "当前体重",
            "purpose": "收集身体数据",
            "psychology": ["Personalization"],
            "ui_pattern": "Scroll Picker",
            "copy": {"headline": "你的当前体重是？", "subheadline": None, "cta": "继续"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "8/8 竞品收集"
        },
        {
            "id": "q_target_weight",
            "name": "目标体重",
            "purpose": "设定具体目标",
            "psychology": ["Goal Setting", "Commitment"],
            "ui_pattern": "Slider Input",
            "copy": {"headline": "你的目标体重是？", "subheadline": "我们会帮你制定计划", "cta": "设定目标"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "承诺一致性原则"
        },
        {
            "id": "q_activity",
            "name": "活动水平",
            "purpose": "评估日常活动量",
            "psychology": ["Personalization"],
            "ui_pattern": "Single Select List",
            "copy": {"headline": "你的日常活动水平？", "subheadline": "这会影响你的热量目标", "cta": "继续"},
            "competitor_refs": ["7/8 竞品"],
            "confidence": "高",
            "research": "7/8 竞品收集"
        },
        {
            "id": "q_diet_type",
            "name": "饮食偏好",
            "purpose": "了解饮食习惯",
            "psychology": ["Personalization"],
            "ui_pattern": "Single Select Cards",
            "copy": {"headline": "你的饮食方式？", "subheadline": None, "cta": "继续"},
            "competitor_refs": ["Yazio #15", "Noom #20"],
            "confidence": "高",
            "research": "6/8 竞品收集"
        },
        {
            "id": "q_diet_restriction",
            "name": "饮食限制",
            "purpose": "了解过敏/禁忌",
            "psychology": ["Personalization", "Safety"],
            "ui_pattern": "Multi Select Tags",
            "copy": {"headline": "有什么饮食限制吗？", "subheadline": "可多选，没有就跳过", "cta": "继续"},
            "competitor_refs": ["Yazio #16", "MyFitnessPal #12"],
            "confidence": "中",
            "research": "5/8 竞品收集"
        },
        {
            "id": "q_challenge",
            "name": "减重挑战",
            "purpose": "了解痛点",
            "psychology": ["Pain Point Discovery", "Empathy"],
            "ui_pattern": "Multi Select Cards",
            "copy": {"headline": "减重最大的挑战是什么？", "subheadline": "可多选", "cta": "继续"},
            "competitor_refs": ["Noom #25", "WeightWatchers #18"],
            "confidence": "高",
            "research": "Noom 心理学驱动方法"
        },
        {
            "id": "q_motivation",
            "name": "动力来源",
            "purpose": "了解深层动机",
            "psychology": ["Motivation Discovery", "Emotional Connection"],
            "ui_pattern": "Multi Select Cards",
            "copy": {"headline": "是什么让你想要改变？", "subheadline": "可多选", "cta": "继续"},
            "competitor_refs": ["Noom #28", "Flo #20"],
            "confidence": "高",
            "research": "Noom 心理学方法"
        },
        {
            "id": "q_timeline",
            "name": "时间框架",
            "purpose": "设定预期",
            "psychology": ["Goal Setting", "Expectation Management"],
            "ui_pattern": "Single Select Cards",
            "copy": {"headline": "你希望多久达成目标？", "subheadline": None, "cta": "继续"},
            "competitor_refs": ["Noom #30", "Cal.AI #25"],
            "confidence": "高",
            "research": "6/8 竞品收集"
        },
        {
            "id": "q_name",
            "name": "名字输入",
            "purpose": "个性化称呼",
            "psychology": ["Personalization", "Rapport Building"],
            "ui_pattern": "Text Input",
            "copy": {"headline": "我们该怎么称呼你？", "subheadline": None, "cta": "继续"},
            "competitor_refs": ["Flo #8", "Noom #10"],
            "confidence": "中",
            "research": "5/8 竞品收集"
        },
    ],
    PageType.V: [
        {
            "id": "v_ai_scan",
            "name": "AI 扫描功能",
            "purpose": "展示核心功能价值",
            "psychology": ["Value Proposition", "Wow Factor"],
            "ui_pattern": "Feature Card with Animation",
            "copy": {"headline": "AI 智能识别食物", "subheadline": "拍照即可记录卡路里", "cta": "继续"},
            "competitor_refs": ["Cal.AI #10", "Yazio #12"],
            "confidence": "极高",
            "research": "Q→Q→Q→V 模式 (6/8 竞品)"
        },
        {
            "id": "v_personalized",
            "name": "个性化计划",
            "purpose": "强调定制化价值",
            "psychology": ["Personalization", "Value Proposition"],
            "ui_pattern": "Feature Preview",
            "copy": {"headline": "专为你定制的计划", "subheadline": "根据你的目标和生活方式量身打造", "cta": "继续"},
            "competitor_refs": ["Noom #15", "WeightWatchers #12"],
            "confidence": "高",
            "research": "个性化 +20% 参与度"
        },
        {
            "id": "v_progress",
            "name": "进度追踪",
            "purpose": "展示追踪能力",
            "psychology": ["Progress Achievement", "Value Proposition"],
            "ui_pattern": "Chart Preview",
            "copy": {"headline": "可视化你的进度", "subheadline": "图表和报告让你清晰了解进展", "cta": "继续"},
            "competitor_refs": ["MyFitnessPal #18", "LoseIt #15"],
            "confidence": "高",
            "research": "7/8 竞品展示"
        },
        {
            "id": "v_recipe",
            "name": "食谱推荐",
            "purpose": "展示内容价值",
            "psychology": ["Value Proposition", "Practical Value"],
            "ui_pattern": "Content Preview Grid",
            "copy": {"headline": "海量健康食谱", "subheadline": "每天为你推荐美味又健康的选择", "cta": "继续"},
            "competitor_refs": ["Yazio #20", "MyFitnessPal #22"],
            "confidence": "中",
            "research": "5/8 竞品展示"
        },
    ],
    PageType.C: [
        {
            "id": "c_goal_confirm",
            "name": "目标确认",
            "purpose": "强化承诺",
            "psychology": ["Commitment & Consistency", "Goal Setting"],
            "ui_pattern": "Goal Summary Card",
            "copy": {"headline": "确认你的目标", "subheadline": "减重 5kg，8 周内达成", "cta": "这是我的目标"},
            "competitor_refs": ["Noom #35", "Cal.AI #30"],
            "confidence": "高",
            "research": "承诺一致性原则 (Cialdini)"
        },
        {
            "id": "c_pledge",
            "name": "承诺宣言",
            "purpose": "心理承诺",
            "psychology": ["Commitment & Consistency", "Public Commitment"],
            "ui_pattern": "Long Press Button",
            "copy": {"headline": "我承诺会坚持", "subheadline": "长按确认你的决心", "cta": "长按承诺"},
            "competitor_refs": ["Noom #38"],
            "confidence": "中",
            "research": "Noom 独特做法"
        },
    ],
    PageType.G: [
        {
            "id": "g_progress_celebrate",
            "name": "进度庆祝",
            "purpose": "强化积极情绪",
            "psychology": ["Progress Achievement", "Positive Reinforcement"],
            "ui_pattern": "Celebration Animation",
            "copy": {"headline": "太棒了！你已完成一半", "subheadline": "继续加油！", "cta": "继续"},
            "competitor_refs": ["Flo #15", "Noom #20"],
            "confidence": "高",
            "research": "5/8 竞品使用中途激励"
        },
        {
            "id": "g_badge",
            "name": "里程碑徽章",
            "purpose": "增加成就感",
            "psychology": ["Achievement Unlocking", "Gamification"],
            "ui_pattern": "Badge Unlock Animation",
            "copy": {"headline": "获得「新手」徽章", "subheadline": "你迈出了第一步！", "cta": "继续"},
            "competitor_refs": ["MyFitnessPal #25"],
            "confidence": "中",
            "research": "3/8 竞品使用"
        },
    ],
    PageType.L: [
        {
            "id": "l_analyzing",
            "name": "分析加载",
            "purpose": "创造期待感",
            "psychology": ["Labor Illusion", "Anticipation"],
            "ui_pattern": "Progress Animation",
            "copy": {"headline": "正在分析你的数据...", "subheadline": None, "cta": None},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "Labor Illusion 增加满意度 (sciencedirect 2024)"
        },
        {
            "id": "l_generating",
            "name": "计划生成",
            "purpose": "展示个性化处理",
            "psychology": ["Labor Illusion", "Value Perception"],
            "ui_pattern": "Step Progress Animation",
            "copy": {"headline": "正在生成你的专属计划...", "subheadline": "计算最佳热量 → 分析营养需求 → 定制计划", "cta": None},
            "competitor_refs": ["Cal.AI #35", "Noom #40"],
            "confidence": "极高",
            "research": "L→R 出现在 8/8 竞品"
        },
    ],
    PageType.R: [
        {
            "id": "r_plan_overview",
            "name": "计划概览",
            "purpose": "展示个性化结果",
            "psychology": ["Personalization", "Value Proposition"],
            "ui_pattern": "Result Summary Card",
            "copy": {"headline": "你的专属计划已生成", "subheadline": None, "cta": "查看详情"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "8/8 竞品展示结果"
        },
        {
            "id": "r_calorie_goal",
            "name": "热量目标",
            "purpose": "展示关键指标",
            "psychology": ["Goal Setting", "Specificity"],
            "ui_pattern": "Big Number with Context",
            "copy": {"headline": "每日目标：1,800 卡路里", "subheadline": "基于你的身体数据和目标计算", "cta": "继续"},
            "competitor_refs": ["MyFitnessPal #35", "LoseIt #30"],
            "confidence": "高",
            "research": "7/8 竞品展示"
        },
        {
            "id": "r_timeline",
            "name": "预期时间线",
            "purpose": "设定预期",
            "psychology": ["Goal Setting", "Expectation Management"],
            "ui_pattern": "Timeline Chart",
            "copy": {"headline": "预计 8 周达成目标", "subheadline": "按计划执行，每周减少 0.5kg", "cta": "继续"},
            "competitor_refs": ["Noom #45", "Cal.AI #40"],
            "confidence": "高",
            "research": "6/8 竞品展示"
        },
    ],
    PageType.X: [
        {
            "id": "x_notification",
            "name": "通知权限",
            "purpose": "获取推送权限",
            "psychology": ["Permission Pre-priming"],
            "ui_pattern": "Permission Request with Value",
            "copy": {"headline": "开启提醒，不错过任何记录", "subheadline": "我们会在用餐时间提醒你", "cta": "开启通知"},
            "competitor_refs": ["7/8 竞品"],
            "confidence": "极高",
            "research": "+34% 同意率使用预权限页 (moldstud 2024)"
        },
        {
            "id": "x_health",
            "name": "健康权限",
            "purpose": "获取健康数据权限",
            "psychology": ["Permission Pre-priming", "Value Exchange"],
            "ui_pattern": "Permission Request with Benefits",
            "copy": {"headline": "连接 Apple Health", "subheadline": "同步步数和运动数据，获得更准确的建议", "cta": "连接"},
            "competitor_refs": ["MyFitnessPal #40", "LoseIt #35"],
            "confidence": "高",
            "research": "6/8 竞品请求"
        },
    ],
    PageType.D: [
        {
            "id": "d_home_preview",
            "name": "首页预览",
            "purpose": "展示产品界面",
            "psychology": ["Progressive Disclosure", "Expectation Setting"],
            "ui_pattern": "App Screenshot Tour",
            "copy": {"headline": "这是你的主页", "subheadline": "一目了然查看今日进度", "cta": "继续"},
            "competitor_refs": ["Yazio #35", "MyFitnessPal #38"],
            "confidence": "高",
            "research": "6/8 竞品展示"
        },
        {
            "id": "d_scan_demo",
            "name": "扫描演示",
            "purpose": "展示核心功能",
            "psychology": ["Feature Education", "Aha Moment"],
            "ui_pattern": "Interactive Demo",
            "copy": {"headline": "试试 AI 扫描", "subheadline": "对准食物，点击拍照", "cta": "试一试"},
            "competitor_refs": ["Cal.AI #38"],
            "confidence": "中",
            "research": "Cal.AI 独特做法"
        },
    ],
    PageType.P: [
        {
            "id": "p_comparison",
            "name": "免费 vs Pro",
            "purpose": "展示付费价值",
            "psychology": ["Value Proposition", "Loss Aversion"],
            "ui_pattern": "Feature Comparison Table",
            "copy": {"headline": "解锁完整功能", "subheadline": None, "cta": "了解 Pro"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "高",
            "research": "战略性放置 +234% 转化 (AppAgent 2024)"
        },
        {
            "id": "p_pricing",
            "name": "定价页",
            "purpose": "展示价格方案",
            "psychology": ["Pricing Psychology", "Anchoring"],
            "ui_pattern": "Pricing Cards",
            "copy": {"headline": "选择你的计划", "subheadline": "7 天免费试用，随时取消", "cta": "开始免费试用"},
            "competitor_refs": ["所有 8 款竞品"],
            "confidence": "极高",
            "research": "周订阅占 55% 市场 (Adapty 2025)"
        },
        {
            "id": "p_urgency",
            "name": "限时优惠",
            "purpose": "最终转化",
            "psychology": ["Scarcity", "Loss Aversion", "Urgency"],
            "ui_pattern": "Special Offer Modal",
            "copy": {"headline": "限时优惠 50% OFF", "subheadline": "仅限今天，错过不再", "cta": "立即开通"},
            "competitor_refs": ["Cal.AI #45", "Flo #40"],
            "confidence": "中",
            "research": "4/8 竞品使用"
        },
    ],
}


# ============================================================================
# 规则引擎
# ============================================================================

class BuilderEngine:
    """Onboarding 构建器规则引擎"""
    
    # 规则：每个阶段推荐的页面类型
    PHASE_RECOMMENDATIONS = {
        Phase.TRUST: [PageType.W, PageType.A, PageType.S],
        Phase.GOAL: [PageType.Q],  # 目标相关问题
        Phase.DATA: [PageType.Q, PageType.V],  # 数据收集 + 价值穿插
        Phase.VALUE: [PageType.V],
        Phase.COMMIT: [PageType.C],
        Phase.RESULT: [PageType.L, PageType.R],
        Phase.PERMISSION: [PageType.X, PageType.D],
        Phase.CONVERT: [PageType.P],
    }
    
    # 问题页面分类
    GOAL_QUESTIONS = ["q_goal", "q_target_weight", "q_timeline", "q_motivation"]
    DATA_QUESTIONS = ["q_gender", "q_birthday", "q_height", "q_weight", "q_activity", 
                      "q_diet_type", "q_diet_restriction", "q_challenge", "q_name"]
    
    def __init__(self):
        self.state = BuilderState()
    
    def reset(self):
        """重置状态"""
        self.state = BuilderState()
    
    def get_next_options(self) -> Dict[str, Any]:
        """获取下一步的 3 个选项"""
        current_index = len(self.state.selected_pages)
        
        # 确定当前阶段
        phase = self._determine_phase()
        
        # 获取推荐选项
        options = self._get_options_for_phase(phase)
        
        # 计算健康度
        health = self._calculate_health()
        
        return {
            "current_index": current_index + 1,
            "current_phase": phase.value,
            "phase_name": self._get_phase_name(phase),
            "options": options,
            "health": health,
            "can_finish": self._can_finish(),
            "recommendation": self._get_recommendation(options),
        }
    
    def select_option(self, option_id: str) -> Dict[str, Any]:
        """选择一个选项"""
        # 找到选项
        option = self._find_option(option_id)
        if not option:
            return {"error": f"Option not found: {option_id}"}
        
        # 添加到已选列表
        selected = {
            "index": len(self.state.selected_pages) + 1,
            **option
        }
        self.state.selected_pages.append(selected)
        
        # 更新状态
        self._update_state(option)
        
        return {
            "success": True,
            "selected": selected,
            "total_pages": len(self.state.selected_pages),
        }
    
    def remove_last(self) -> Dict[str, Any]:
        """移除最后一个选择"""
        if not self.state.selected_pages:
            return {"error": "No pages to remove"}
        
        removed = self.state.selected_pages.pop()
        # 重新计算状态
        self._recalculate_state()
        
        return {
            "success": True,
            "removed": removed,
            "total_pages": len(self.state.selected_pages),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取当前方案摘要"""
        type_counts = {}
        for page in self.state.selected_pages:
            t = page.get("type", "?")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            "total_pages": len(self.state.selected_pages),
            "pages": self.state.selected_pages,
            "type_distribution": type_counts,
            "health": self._calculate_health(),
            "phases_covered": self._get_covered_phases(),
        }
    
    def export_plan(self) -> Dict[str, Any]:
        """导出完整方案"""
        return {
            "title": "VitaFlow Onboarding 方案",
            "generated_at": "2024-12-17",
            "source": "基于 8 款竞品分析 + 心理学研究",
            "total_pages": len(self.state.selected_pages),
            "pages": self.state.selected_pages,
            "health_score": self._calculate_health(),
            "notes": self._generate_notes(),
        }
    
    # ========== 私有方法 ==========
    
    def _determine_phase(self) -> Phase:
        """确定当前应该处于的阶段"""
        total = len(self.state.selected_pages)
        
        # 阶段判断逻辑
        if total < 3:
            return Phase.TRUST
        elif total < 6:
            return Phase.GOAL
        elif total < 20:
            # 数据收集阶段，但需要穿插价值
            if self.state.consecutive_q_count >= 3 and not self.state.has_value_shown:
                return Phase.VALUE
            return Phase.DATA
        elif total < 25:
            if not self.state.has_commit:
                return Phase.COMMIT
            return Phase.DATA
        elif total < 30:
            return Phase.RESULT
        elif total < 35:
            return Phase.PERMISSION
        else:
            return Phase.CONVERT
    
    def _get_options_for_phase(self, phase: Phase) -> List[Dict]:
        """获取指定阶段的选项"""
        options = []
        
        # 特殊规则：连续 3+ 个 Q 后，强制推荐 V
        if self.state.consecutive_q_count >= 3:
            options.append(self._create_option_from_template(
                PageType.V, "v_ai_scan", recommended=True,
                reason="连续 3 个问题后建议插入价值展示，缓解问卷疲劳 (Q→Q→Q→V 模式)"
            ))
            # 但也允许继续问
            q_templates = [t for t in PAGE_TEMPLATES[PageType.Q] 
                         if t["id"] not in [p.get("id") for p in self.state.selected_pages]]
            if q_templates:
                options.append(self._create_option_from_template(
                    PageType.Q, q_templates[0]["id"], recommended=False,
                    reason="可以继续问问题，但建议先插入价值页面"
                ))
        
        # 根据阶段获取推荐类型
        recommended_types = self.PHASE_RECOMMENDATIONS.get(phase, [])
        
        for page_type in recommended_types:
            templates = PAGE_TEMPLATES.get(page_type, [])
            # 过滤已选的
            available = [t for t in templates 
                        if t["id"] not in [p.get("id") for p in self.state.selected_pages]]
            
            for template in available[:2]:  # 每种类型最多 2 个
                if len(options) >= 3:
                    break
                options.append(self._create_option_from_template(
                    page_type, template["id"], 
                    recommended=(len(options) == 0),
                    reason=self._get_reason_for_type(page_type, phase)
                ))
        
        # 确保有 3 个选项
        if len(options) < 3:
            # 补充其他可选类型
            all_types = [PageType.Q, PageType.V, PageType.S, PageType.G]
            for page_type in all_types:
                if len(options) >= 3:
                    break
                templates = PAGE_TEMPLATES.get(page_type, [])
                available = [t for t in templates 
                            if t["id"] not in [p.get("id") for p in self.state.selected_pages]]
                for template in available[:1]:
                    if len(options) >= 3:
                        break
                    options.append(self._create_option_from_template(
                        page_type, template["id"], 
                        recommended=False,
                        reason="可选项"
                    ))
        
        return options[:3]
    
    def _create_option_from_template(self, page_type: PageType, template_id: str, 
                                      recommended: bool, reason: str) -> Dict:
        """从模板创建选项"""
        templates = PAGE_TEMPLATES.get(page_type, [])
        template = next((t for t in templates if t["id"] == template_id), None)
        
        if not template:
            return {}
        
        return {
            "id": template["id"],
            "type": page_type.value,
            "name": template["name"],
            "purpose": template["purpose"],
            "psychology": template["psychology"],
            "ui_pattern": template["ui_pattern"],
            "copy": template["copy"],
            "competitor_refs": template["competitor_refs"],
            "confidence": template["confidence"],
            "research": template.get("research", ""),
            "recommended": recommended,
            "reason": reason,
        }
    
    def _find_option(self, option_id: str) -> Optional[Dict]:
        """查找选项"""
        for page_type, templates in PAGE_TEMPLATES.items():
            for template in templates:
                if template["id"] == option_id:
                    return {
                        "id": template["id"],
                        "type": page_type.value,
                        "name": template["name"],
                        "purpose": template["purpose"],
                        "psychology": template["psychology"],
                        "ui_pattern": template["ui_pattern"],
                        "copy": template["copy"],
                        "competitor_refs": template["competitor_refs"],
                        "confidence": template["confidence"],
                    }
        return None
    
    def _update_state(self, option: Dict):
        """更新状态"""
        page_type = option.get("type", "")
        
        if page_type == "Q":
            self.state.consecutive_q_count += 1
            self.state.total_q_count += 1
        else:
            self.state.consecutive_q_count = 0
        
        if page_type == "V":
            self.state.has_value_shown = True
        elif page_type == "S":
            self.state.has_social_proof = True
        elif page_type == "R":
            self.state.has_result = True
        elif page_type == "L":
            self.state.has_loading = True
        elif page_type == "C":
            self.state.has_commit = True
    
    def _recalculate_state(self):
        """重新计算状态"""
        self.state.consecutive_q_count = 0
        self.state.total_q_count = 0
        self.state.has_value_shown = False
        self.state.has_social_proof = False
        self.state.has_result = False
        self.state.has_loading = False
        self.state.has_commit = False
        
        for page in self.state.selected_pages:
            page_type = page.get("type", "")
            if page_type == "Q":
                self.state.consecutive_q_count += 1
                self.state.total_q_count += 1
            else:
                self.state.consecutive_q_count = 0
            
            if page_type == "V":
                self.state.has_value_shown = True
            elif page_type == "S":
                self.state.has_social_proof = True
            elif page_type == "R":
                self.state.has_result = True
            elif page_type == "L":
                self.state.has_loading = True
            elif page_type == "C":
                self.state.has_commit = True
    
    def _calculate_health(self) -> Dict[str, Any]:
        """计算健康度"""
        total = len(self.state.selected_pages)
        issues = []
        warnings = []
        
        # 检查规则
        if self.state.consecutive_q_count > 4:
            issues.append("连续问题过多 (>4)，建议插入价值页面")
        elif self.state.consecutive_q_count > 3:
            warnings.append("连续问题较多 (>3)，考虑插入价值页面")
        
        if total > 10 and not self.state.has_value_shown:
            issues.append("缺少价值展示页面")
        
        if total > 5 and not self.state.has_social_proof:
            warnings.append("建议添加社会认同页面")
        
        # 计算分数
        score = 100
        score -= len(issues) * 15
        score -= len(warnings) * 5
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "level": "良好" if score >= 80 else ("一般" if score >= 60 else "需改进"),
            "issues": issues,
            "warnings": warnings,
        }
    
    def _can_finish(self) -> bool:
        """是否可以结束"""
        total = len(self.state.selected_pages)
        return total >= 10  # 至少 10 页
    
    def _get_recommendation(self, options: List[Dict]) -> str:
        """获取推荐说明"""
        if not options:
            return ""
        
        recommended = next((o for o in options if o.get("recommended")), options[0])
        return f"推荐选择「{recommended.get('name', '')}」：{recommended.get('reason', '')}"
    
    def _get_phase_name(self, phase: Phase) -> str:
        """获取阶段名称"""
        names = {
            Phase.TRUST: "信任建立",
            Phase.GOAL: "目标设定",
            Phase.DATA: "数据收集",
            Phase.VALUE: "价值展示",
            Phase.COMMIT: "承诺阶段",
            Phase.RESULT: "结果展示",
            Phase.PERMISSION: "权限请求",
            Phase.CONVERT: "转化阶段",
        }
        return names.get(phase, "")
    
    def _get_reason_for_type(self, page_type: PageType, phase: Phase) -> str:
        """获取推荐理由"""
        reasons = {
            PageType.W: "建立品牌第一印象",
            PageType.A: "通过专家背书建立信任",
            PageType.S: "社会认同提升转化 +34%",
            PageType.Q: "收集用户数据进行个性化",
            PageType.V: "展示产品价值，缓解问卷疲劳",
            PageType.C: "强化用户承诺，提升完成率",
            PageType.G: "中途激励，维持用户动力",
            PageType.L: "Labor Illusion 增加期待感",
            PageType.R: "展示个性化结果，强化价值感知",
            PageType.X: "获取权限，预权限页 +34% 同意率",
            PageType.D: "展示产品界面，设定使用预期",
            PageType.P: "战略性放置可提升 +234% 转化",
        }
        return reasons.get(page_type, "")
    
    def _get_covered_phases(self) -> List[str]:
        """获取已覆盖的阶段"""
        phases = set()
        for page in self.state.selected_pages:
            page_type = page.get("type", "")
            if page_type in ["W", "A", "S"]:
                phases.add("信任建立")
            elif page_type == "Q":
                phases.add("数据收集")
            elif page_type == "V":
                phases.add("价值展示")
            elif page_type == "C":
                phases.add("承诺阶段")
            elif page_type in ["L", "R"]:
                phases.add("结果展示")
            elif page_type in ["X", "D"]:
                phases.add("权限/演示")
            elif page_type == "P":
                phases.add("转化阶段")
        return list(phases)
    
    def _generate_notes(self) -> List[str]:
        """生成方案说明"""
        notes = [
            "此方案基于 8 款竞品分析 + 2024-2025 行业研究生成",
            "建议作为 A/B 测试的 Control 组",
            "根据实际数据迭代优化",
        ]
        
        health = self._calculate_health()
        if health["issues"]:
            notes.extend([f"⚠️ {issue}" for issue in health["issues"]])
        
        return notes


# 全局引擎实例
_engine_instances: Dict[str, BuilderEngine] = {}


def get_engine(session_id: str = "default") -> BuilderEngine:
    """获取引擎实例"""
    if session_id not in _engine_instances:
        _engine_instances[session_id] = BuilderEngine()
    return _engine_instances[session_id]


def reset_engine(session_id: str = "default"):
    """重置引擎"""
    if session_id in _engine_instances:
        _engine_instances[session_id].reset()
    else:
        _engine_instances[session_id] = BuilderEngine()

