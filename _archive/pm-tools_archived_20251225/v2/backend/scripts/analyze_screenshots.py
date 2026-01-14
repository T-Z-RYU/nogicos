#!/usr/bin/env python3
"""
批量分析 Onboarding 截图脚本
使用 GPT-5.2 + Claude Opus 4.5 双模型分析

Usage:
    python scripts/analyze_screenshots.py --app flo
    python scripts/analyze_screenshots.py --app all
    python scripts/analyze_screenshots.py --app cal_ai --start 1 --end 10
"""
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.services.vision_analysis_service import vision_service, ScreenAnalysis


# ============================================================================
# 配置
# ============================================================================

# 要分析的 App 列表（会从 onboarding_range.json 读取实际范围）
APPS_TO_ANALYZE = {
    # 已分析
    "flo": {
        "name": "Flo",
        "dir": "Flo"
    },
    "yazio": {
        "name": "Yazio", 
        "dir": "Yazio"
    },
    "cal_ai": {
        "name": "Cal AI",
        "dir": "Cal_AI"
    },
    "noom": {
        "name": "Noom",
        "dir": "Noom"
    },
    # 新增 - 卡路里/饮食追踪类
    "myfitnesspal": {
        "name": "MyFitnessPal",
        "dir": "MyFitnessPal"
    },
    "loseit": {
        "name": "LoseIt",
        "dir": "LoseIt"
    },
    "macrofactor": {
        "name": "MacroFactor",
        "dir": "MacroFactor"
    },
    "weightwatchers": {
        "name": "WeightWatchers",
        "dir": "WeightWatchers"
    }
}


def get_onboarding_range(screenshots_dir: Path) -> tuple[int, int]:
    """从 onboarding_range.json 读取实际的 onboarding 范围"""
    range_file = screenshots_dir / "onboarding_range.json"
    if range_file.exists():
        with open(range_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("start", 0), data.get("end", 999)
    return 0, 999  # 默认分析全部

OUTPUT_DIR = settings.data_dir / "analysis" / "swimlane"


# ============================================================================
# 阶段划分逻辑
# ============================================================================

def assign_phase(screen: ScreenAnalysis, total_screens: int) -> str:
    """
    根据截图位置和类型自动分配阶段
    
    这是一个启发式算法，基于：
    1. 截图在流程中的位置（前10%、中间、后10%等）
    2. 截图的类型（W、Q、V、P 等）
    """
    position_ratio = screen.index / total_screens
    primary_type = screen.primary_type
    
    # 前 10% 通常是信任建立阶段
    if position_ratio <= 0.10:
        if primary_type in ["W", "A", "S"]:
            return "trust-building"
        elif primary_type == "X":
            return "trust-building"
        else:
            return "trust-building"
    
    # 10-30% 通常是目标设定或早期数据收集
    elif position_ratio <= 0.30:
        if primary_type in ["Q", "C"]:
            return "goal-setting"
        elif primary_type == "V":
            return "goal-setting"
        else:
            return "data-collection-a"
    
    # 30-60% 是主要数据收集阶段
    elif position_ratio <= 0.60:
        if primary_type in ["Q"]:
            return "data-collection"
        elif primary_type in ["V", "S"]:
            return "data-collection"
        elif primary_type == "D":
            return "feature-showcase"
        else:
            return "data-collection"
    
    # 60-80% 是功能展示或最终设置
    elif position_ratio <= 0.80:
        if primary_type in ["D", "V"]:
            return "feature-showcase"
        elif primary_type == "X":
            return "final-setup"
        elif primary_type in ["Q"]:
            return "final-setup"
        else:
            return "final-setup"
    
    # 后 20% 是转化阶段
    else:
        if primary_type in ["L", "R"]:
            return "results"
        elif primary_type == "P":
            return "conversion"
        elif primary_type in ["V", "W"]:
            return "conversion"
        else:
            return "conversion"


def detect_patterns(screens: list[ScreenAnalysis]) -> list[dict]:
    """检测序列模式"""
    patterns = []
    types = [s.primary_type for s in screens]
    
    # 检测 Q→Q→Q→V 模式
    qqqv_positions = []
    for i in range(len(types) - 3):
        if types[i:i+4] == ["Q", "Q", "Q", "V"]:
            qqqv_positions.append(i + 1)
    if qqqv_positions:
        patterns.append({
            "pattern": "Q→Q→Q→V",
            "name": "问题-价值穿插",
            "occurrences": len(qqqv_positions),
            "positions": qqqv_positions,
            "interpretation": "每3-4个问题后穿插1个价值页，缓解问卷疲劳"
        })
    
    # 检测 V→S 模式
    vs_positions = []
    for i in range(len(types) - 1):
        if types[i] == "V" and types[i+1] == "S":
            vs_positions.append(i + 1)
    if vs_positions:
        patterns.append({
            "pattern": "V→S",
            "name": "价值-社会认同",
            "occurrences": len(vs_positions),
            "positions": vs_positions,
            "interpretation": "价值展示后跟随社会认同强化可信度"
        })
    
    # 检测 L→R 模式
    lr_positions = []
    for i in range(len(types) - 1):
        if types[i] == "L" and types[i+1] == "R":
            lr_positions.append(i + 1)
    if lr_positions:
        patterns.append({
            "pattern": "L→R",
            "name": "加载-结果",
            "occurrences": len(lr_positions),
            "positions": lr_positions,
            "interpretation": "加载动画后展示结果，创造期待感"
        })
    
    # 检测 V→X 模式 (Permission Pre-priming)
    vx_positions = []
    for i in range(len(types) - 1):
        if types[i] == "V" and types[i+1] == "X":
            vx_positions.append(i + 1)
    if vx_positions:
        patterns.append({
            "pattern": "V→X",
            "name": "价值-权限",
            "occurrences": len(vx_positions),
            "positions": vx_positions,
            "interpretation": "展示价值后请求权限（Permission Pre-priming）"
        })
    
    return patterns


def generate_phases(screens: list[ScreenAnalysis]) -> list[dict]:
    """根据截图生成阶段划分"""
    # 按 phase 分组
    phase_groups = {}
    for s in screens:
        phase = s.phase or "unknown"
        if phase not in phase_groups:
            phase_groups[phase] = []
        phase_groups[phase].append(s)
    
    # 生成阶段列表
    phases = []
    phase_order = [
        "trust-building", "goal-setting", "data-collection-a", 
        "data-collection", "feature-showcase", "final-setup", 
        "results", "conversion"
    ]
    
    phase_names = {
        "trust-building": ("信任建立", "Trust Building"),
        "goal-setting": ("目标设定", "Goal Setting"),
        "data-collection-a": ("数据收集A", "Data Collection A"),
        "data-collection": ("数据收集", "Data Collection"),
        "feature-showcase": ("功能展示", "Feature Showcase"),
        "final-setup": ("最终设置", "Final Setup"),
        "results": ("结果展示", "Results"),
        "conversion": ("转化", "Conversion"),
    }
    
    for phase_id in phase_order:
        if phase_id not in phase_groups:
            continue
        
        group = phase_groups[phase_id]
        if not group:
            continue
        
        indices = [s.index for s in group]
        types = [s.primary_type for s in group]
        
        # 统计主要类型
        type_counts = {}
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1
        dominant_types = sorted(type_counts.keys(), key=lambda x: -type_counts[x])[:4]
        
        # 收集心理策略
        all_psychology = []
        for s in group:
            all_psychology.extend(s.psychology)
        unique_psychology = list(dict.fromkeys(all_psychology))[:5]
        
        name_cn, name_en = phase_names.get(phase_id, (phase_id, phase_id))
        
        phases.append({
            "id": phase_id,
            "name": name_cn,
            "nameEn": name_en,
            "purpose": f"包含 {len(group)} 个页面",
            "startIndex": min(indices),
            "endIndex": max(indices),
            "dominantTypes": dominant_types,
            "psychologyTactics": unique_psychology,
            "keyInsights": []
        })
    
    return phases


def calculate_summary(screens: list[ScreenAnalysis]) -> dict:
    """计算统计摘要"""
    total = len(screens)
    
    # 按类型统计
    type_counts = {}
    type_labels = {
        "W": "Welcome", "Q": "Question", "V": "Value", "S": "Social",
        "A": "Authority", "R": "Result", "D": "Demo", "C": "Commit",
        "G": "Gamified", "L": "Loading", "X": "Permission", "P": "Paywall"
    }
    type_colors = {
        "W": "#E5E5E5", "Q": "#3B82F6", "V": "#22C516", "S": "#EAB308",
        "A": "#6366F1", "R": "#A855F7", "D": "#F97316", "C": "#D97706",
        "G": "#14B8A6", "L": "#1F2937", "X": "#6B7280", "P": "#EF4444"
    }
    
    for s in screens:
        t = s.primary_type
        if t not in type_counts:
            type_counts[t] = {
                "count": 0,
                "label": type_labels.get(t, t),
                "color": type_colors.get(t, "#6B7280")
            }
        type_counts[t]["count"] += 1
    
    # 按阶段统计
    phase_counts = {}
    for s in screens:
        phase = s.phase or "unknown"
        if phase not in phase_counts:
            phase_counts[phase] = {"count": 0, "percentage": 0}
        phase_counts[phase]["count"] += 1
    
    for phase in phase_counts:
        phase_counts[phase]["percentage"] = round(phase_counts[phase]["count"] / total * 100)
    
    return {
        "total_pages": total,
        "phase_distribution": phase_counts,
        "by_type": type_counts
    }


# ============================================================================
# 主函数
# ============================================================================

async def analyze_app(app_id: str, start: int = 1, end: int = None, resume: bool = True):
    """分析单个 App"""
    if app_id not in APPS_TO_ANALYZE:
        print(f"Unknown app: {app_id}")
        return
    
    app_config = APPS_TO_ANALYZE[app_id]
    app_name = app_config["name"]
    screenshots_dir = settings.downloads_dir / app_config["dir"]
    output_path = OUTPUT_DIR / f"{app_id}.json"
    
    # 读取 onboarding 范围
    onboarding_start, onboarding_end = get_onboarding_range(screenshots_dir)
    total_onboarding = onboarding_end - onboarding_start + 1
    
    print(f"\n{'='*60}")
    print(f"开始分析: {app_name}")
    print(f"截图目录: {screenshots_dir}")
    print(f"Onboarding 范围: {onboarding_start}-{onboarding_end} ({total_onboarding} 张)")
    print(f"{'='*60}\n")
    
    # 如果没有指定 end，使用 onboarding 范围
    if end is None:
        end = onboarding_end + 1  # +1 因为 end 是 exclusive
    
    # 检查是否有已存在的分析结果（断点续传）
    existing_screens = []
    if resume and output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                existing_screens = existing_data.get("screens", [])
                if existing_screens:
                    last_index = max(s["index"] for s in existing_screens)
                    print(f"[RESUME] 发现已有分析结果: {len(existing_screens)} 张")
                    print(f"[RESUME] 将从第 {last_index + 1} 张继续分析")
                    start = last_index + 1
        except Exception as e:
            print(f"[WARN] 读取已有结果失败: {e}，将从头开始")
            existing_screens = []
    
    # 检查 API 配置
    openai_ok, anthropic_ok = vision_service.is_configured()
    if not openai_ok and not anthropic_ok:
        print("[ERROR] API Keys not configured")
        print("Please configure in backend/.env:")
        print("  PM_TOOL_OPENAI_API_KEY=your_key")
        print("  PM_TOOL_ANTHROPIC_API_KEY=your_key")
        return
    
    print(f"[OK] OpenAI API: {'configured' if openai_ok else 'not configured'}")
    print(f"[OK] Anthropic API: {'configured' if anthropic_ok else 'not configured'}")
    print()
    
    # 进度回调
    def progress_callback(current: int, total: int, result: ScreenAnalysis):
        print(f"  [{current}/{total}] {result.filename} → {result.primary_type} ({result.ui_pattern})")
    
    # 执行分析
    print("开始分析截图...")
    screens = await vision_service.analyze_app_screenshots(
        app_name=app_name,
        screenshots_dir=screenshots_dir,
        start_index=start,
        end_index=end,
        concurrency=5,  # 提高并发，有 rate limit 自动重试
        progress_callback=progress_callback
    )
    
    print(f"\n[DONE] 新分析完成: {len(screens)} 张截图")
    
    # 合并已有结果和新分析结果
    if existing_screens:
        # 将已有的 screens 转换为 ScreenAnalysis 对象
        from app.services.vision_analysis_service import ScreenCopy
        all_screens = []
        for s in existing_screens:
            all_screens.append(ScreenAnalysis(
                index=s["index"],
                filename=s["filename"],
                primary_type=s["primary_type"],
                secondary_type=s.get("secondary_type"),
                phase=s.get("phase"),
                psychology=s.get("psychology", []),
                ui_pattern=s.get("ui_pattern", ""),
                copy=ScreenCopy(**s.get("copy", {})),
                insight=s.get("insight", ""),
                confidence=s.get("confidence", 0.8),
                analyzed_by=s.get("analyzed_by", "unknown")
            ))
        all_screens.extend(screens)
        screens = sorted(all_screens, key=lambda x: x.index)
        print(f"[MERGED] 合并后总计: {len(screens)} 张截图")
    
    # 分配阶段
    total_screens = len(screens)
    for s in screens:
        s.phase = assign_phase(s, total_screens)
    
    # 检测模式
    patterns = detect_patterns(screens)
    
    # 生成阶段
    phases = generate_phases(screens)
    
    # 计算统计
    summary = calculate_summary(screens)
    
    # 构建输出数据
    output_data = {
        "app": app_name,
        "appId": app_id,
        "total_screens": len(screens),
        "analyzed_at": datetime.now().isoformat(),
        "taxonomy_version": "3.0",
        "analysis_method": "gpt-5.2 + claude-opus-4-5",
        "phases": phases,
        "patterns": patterns,
        "summary": summary,
        "screens": [
            {
                "index": s.index,
                "filename": s.filename,
                "primary_type": s.primary_type,
                "secondary_type": s.secondary_type,
                "phase": s.phase,
                "psychology": s.psychology,
                "ui_pattern": s.ui_pattern,
                "copy": {
                    "headline": s.copy.headline,
                    "subheadline": s.copy.subheadline,
                    "cta": s.copy.cta
                },
                "insight": s.insight,
                "confidence": s.confidence,
                "analyzed_by": s.analyzed_by
            }
            for s in screens
        ],
        "flow_patterns": {},
        "design_insights": {}
    }
    
    # 保存结果
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{app_id}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Results saved to: {output_path}")
    
    # 打印统计摘要
    print(f"\n{'='*60}")
    print(f"统计摘要")
    print(f"{'='*60}")
    print(f"总页面数: {summary['total_pages']}")
    print(f"阶段数: {len(phases)}")
    print(f"检测到的模式: {len(patterns)}")
    print(f"\n类型分布:")
    for t, data in sorted(summary['by_type'].items(), key=lambda x: -x[1]['count']):
        print(f"  {t} ({data['label']}): {data['count']}")


async def main():
    parser = argparse.ArgumentParser(description="分析 Onboarding 截图")
    parser.add_argument("--app", type=str, default="all", help="要分析的 App (flo/yazio/cal_ai/noom/all)")
    parser.add_argument("--start", type=int, default=1, help="起始序号")
    parser.add_argument("--end", type=int, default=None, help="结束序号")
    parser.add_argument("--no-resume", action="store_true", help="不使用断点续传，从头开始")
    args = parser.parse_args()
    
    resume = not args.no_resume
    
    if args.app == "all":
        for app_id in APPS_TO_ANALYZE:
            await analyze_app(app_id, args.start, args.end, resume=resume)
    else:
        await analyze_app(args.app, args.start, args.end, resume=resume)


if __name__ == "__main__":
    asyncio.run(main())
