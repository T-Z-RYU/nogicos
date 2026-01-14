"""
Onboarding Screenshot Analyzer
三方案并行分析：GPT-5.2 Pro / Claude Opus 4.5 / 双模型协作

使用方法：
1. 设置环境变量：
   - OPENAI_API_KEY: OpenAI API Key
   - ANTHROPIC_API_KEY: Anthropic API Key

2. 运行分析：
   python onboarding_analyzer.py --plan A  # GPT-5.2 Pro
   python onboarding_analyzer.py --plan B  # Claude Opus 4.5
   python onboarding_analyzer.py --plan C  # 双模型协作
   python onboarding_analyzer.py --plan ALL  # 三种方案都运行
"""

import os
import json
import base64
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import time

# API clients
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None


# 配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOWNLOADS_DIR = DATA_DIR / "downloads_2024"
ANALYSIS_DIR = DATA_DIR / "analysis"

# 加载 Taxonomy Schema
def load_taxonomy_schema() -> dict:
    schema_path = ANALYSIS_DIR / "taxonomy_schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 加载分析队列
def load_analysis_queue() -> dict:
    queue_path = ANALYSIS_DIR / "analysis_queue.json"
    with open(queue_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 图像转 base64
def image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

# 获取截图路径
def get_screenshot_path(app_name: str, index: int) -> Path:
    filename = f"{index:04d}.png"
    return DOWNLOADS_DIR / app_name / filename


SYSTEM_PROMPT = """你是一个专业的移动应用UX分析师，专门分析健康健身类App的Onboarding流程。

你需要对每张截图进行6维度分类分析：

1. **功能目的 (functional_purpose)**：页面做什么
   - Value: 价值传递（Splash, ValueProp, FeatureHighlight, Testimonial）
   - Identity: 身份采集（Gender, Age, Height, Weight, BodyMetrics）
   - Goal: 目标设定（DirectionSelect, TargetValue, Timeline, Motivation）
   - Preference: 偏好收集（DietType, ActivityLevel, ExerciseType, Lifestyle）
   - Plan: 计划生成（Loading, Calculating, PlanSummary, PersonalizedResult）
   - Permission: 权限请求（Notification, Location, Camera, Health, Tracking）
   - Paywall: 付费转化（ValueReminder, PlanSelect, PriceDisplay, TrialOffer）
   - Registration: 账户注册（MethodSelect, Email, Password, OAuth, Verification）
   - Growth: 增长运营（ChannelSurvey, ReferralCode, RateRequest）

2. **漏斗阶段 (funnel_stage)**：在用户决策旅程中的位置
   - Awareness: 让用户了解产品价值
   - Consideration: 让用户评估是否适合自己
   - Commitment: 让用户做出小承诺（填信息、设目标）
   - Activation: 让用户完成首次价值体验
   - Conversion: 让用户付费或注册

3. **心理策略 (psychological_tactic)**：使用了什么说服技巧
   - SocialProof: 社会认同（用户数、评价、名人背书）
   - CommitmentConsistency: 承诺一致性（小承诺 → 大承诺）
   - Scarcity: 稀缺性（限时优惠、名额有限）
   - LossAversion: 损失厌恶（错过什么、不行动的代价）
   - Personalization: 个性化（为你定制、专属计划）
   - ProgressAchievement: 进度成就（完成度、里程碑）
   - Authority: 权威性（专家、科学、认证）
   - Reciprocity: 互惠（先给价值再要求）
   - None: 无明显心理策略

4. **交互模式 (interaction_pattern)**：用户如何与页面交互
   - PassiveRead: 纯展示阅读
   - SingleChoice: 单选
   - MultipleChoice: 多选
   - TextInput: 文本输入
   - NumberInput: 数字输入
   - Slider: 滑块
   - DatePicker: 日期选择
   - Toggle: 开关
   - SystemModal: 系统弹窗
   - Tap: 点击继续

5. **UI模式 (ui_pattern)**：页面的视觉呈现方式
   - FullScreenIllustration: 全屏插画
   - Carousel: 轮播图
   - ListSelection: 列表选择
   - CardSelection: 卡片选择
   - IconGrid: 图标网格
   - Form: 表单
   - Calculator: 计算/加载动画
   - SummaryCard: 摘要卡片
   - PaywallScreen: 付费墙
   - SystemDialog: 系统对话框
   - ChatBubble: 对话气泡
   - ProgressDisplay: 进度展示

6. **承诺梯度 (commitment_level)**：用户需要付出多少（1-5）
   - 1: 无承诺（纯阅读或点击继续）
   - 2: 低承诺（简单选择）
   - 3: 中承诺（输入个人信息）
   - 4: 高承诺（连接账户、授予权限）
   - 5: 最高承诺（付费、注册）

请严格按照以下JSON格式输出分析结果：
"""

USER_PROMPT_TEMPLATE = """分析这张来自 {app_name} App 的 Onboarding 截图。

截图信息：
- App名称：{app_name}
- 截图序号：第 {index} 张（共 {total} 张 Onboarding 截图）
- 流程位置：{position_pct}%

请按照以下JSON格式输出分析结果（严格遵守格式）：

```json
{{
  "app_name": "{app_name}",
  "screenshot_index": {index},
  "screenshot_filename": "{filename}",
  "total_onboarding_screens": {total},
  "position_percentage": {position_pct},
  
  "classification": {{
    "functional_purpose": {{
      "primary_category": "选择: Value/Identity/Goal/Preference/Plan/Permission/Paywall/Registration/Growth",
      "secondary_type": "具体页面类型描述",
      "confidence": 0.0到1.0之间的数字
    }},
    "funnel_stage": {{
      "stage": "选择: Awareness/Consideration/Commitment/Activation/Conversion",
      "position_in_funnel": "选择: top/middle/bottom"
    }},
    "psychological_tactic": {{
      "primary_tactic": "选择: SocialProof/CommitmentConsistency/Scarcity/LossAversion/Personalization/ProgressAchievement/Authority/Reciprocity/None",
      "secondary_tactics": ["可选的次要策略数组"],
      "tactic_strength": "选择: strong/moderate/weak/none"
    }},
    "interaction_pattern": {{
      "primary_interaction": "选择: PassiveRead/SingleChoice/MultipleChoice/TextInput/NumberInput/Slider/DatePicker/Toggle/SystemModal/Tap",
      "is_skippable": true或false,
      "input_effort": "选择: none/low/medium/high"
    }},
    "ui_pattern": {{
      "layout_type": "选择: FullScreenIllustration/Carousel/ListSelection/CardSelection/IconGrid/Form/Calculator/SummaryCard/PaywallScreen/SystemDialog/ChatBubble/ProgressDisplay",
      "has_progress_indicator": true或false,
      "has_illustration": true或false,
      "has_animation": true或false,
      "color_scheme": "选择: light/dark/branded/mixed"
    }},
    "commitment_level": {{
      "level": 1到5之间的整数,
      "commitment_type": "选择: time/information/permission/money/identity",
      "reversibility": "选择: reversible/partially_reversible/irreversible"
    }}
  }},
  
  "deep_analysis": {{
    "design_intent": "分析这个页面的设计意图",
    "ux_observation": "用户体验观察",
    "conversion_impact": "选择: positive/neutral/negative/uncertain",
    "potential_issues": ["潜在问题列表"],
    "best_practice_alignment": "与行业最佳实践的对齐程度分析"
  }},
  
  "raw_observation": {{
    "visible_text": ["页面上可见的主要文字"],
    "ui_elements": ["主要UI元素描述"],
    "brand_elements": ["品牌元素描述"]
  }}
}}
```

只输出JSON，不要添加任何其他文字说明。
"""


class OnboardingAnalyzer:
    def __init__(self, plan: str = "A"):
        self.plan = plan
        self.taxonomy = load_taxonomy_schema()
        self.queue = load_analysis_queue()
        self.results = {}
        
        # 初始化API客户端
        if plan in ["A", "C", "ALL"]:
            if OpenAI is None:
                raise ImportError("请安装 openai: pip install openai")
            self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        if plan in ["B", "C", "ALL"]:
            if anthropic is None:
                raise ImportError("请安装 anthropic: pip install anthropic")
            self.anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    def analyze_with_gpt52(self, image_path: Path, app_name: str, index: int, total: int) -> dict:
        """使用 GPT-5.2 Pro 分析截图"""
        image_base64 = image_to_base64(image_path)
        filename = image_path.name
        position_pct = round((index / total) * 100, 1)
        
        user_prompt = USER_PROMPT_TEMPLATE.format(
            app_name=app_name,
            index=index,
            total=total,
            filename=filename,
            position_pct=position_pct
        )
        
        response = self.openai_client.chat.completions.create(
            model="gpt-5.2",  # 或者 "gpt-5.2-pro" 取决于实际API
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        return json.loads(result_text)
    
    def analyze_with_opus(self, image_path: Path, app_name: str, index: int, total: int) -> dict:
        """使用 Claude Opus 4.5 分析截图"""
        image_base64 = image_to_base64(image_path)
        filename = image_path.name
        position_pct = round((index / total) * 100, 1)
        
        user_prompt = USER_PROMPT_TEMPLATE.format(
            app_name=app_name,
            index=index,
            total=total,
            filename=filename,
            position_pct=position_pct
        )
        
        response = self.anthropic_client.messages.create(
            model="claude-opus-4-5-20251124",  # 或实际模型名
            max_tokens=2000,
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
        # 提取JSON部分
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        return json.loads(result_text.strip())
    
    def analyze_combined(self, image_path: Path, app_name: str, index: int, total: int) -> dict:
        """双模型协作分析"""
        # 第一层：GPT-5.2 深度分析
        gpt_result = self.analyze_with_gpt52(image_path, app_name, index, total)
        
        # 第二层：Claude 结构化分类（带上GPT的分析结果作为参考）
        opus_result = self.analyze_with_opus(image_path, app_name, index, total)
        
        # 合并结果
        combined = {
            **opus_result,  # 以 Claude 的结构化输出为主
            "gpt52_analysis": gpt_result.get("deep_analysis", {}),
            "analysis_method": "combined_gpt52_opus45"
        }
        
        return combined
    
    def analyze_app(self, app_info: dict, output_dir: Path, method: str = "gpt52"):
        """分析单个App的所有Onboarding截图"""
        app_name = app_info["name"]
        start = app_info["onboarding_range"]["start"]
        end = app_info["onboarding_range"]["end"]
        total = end - start + 1
        
        print(f"\n{'='*60}")
        print(f"分析 {app_name}: {total} 张截图")
        print(f"{'='*60}")
        
        app_results = []
        
        for i in range(start, end + 1):
            screenshot_path = get_screenshot_path(app_name, i + 1)  # 文件名从1开始
            
            if not screenshot_path.exists():
                print(f"  [跳过] {screenshot_path.name} - 文件不存在")
                continue
            
            try:
                print(f"  分析 {screenshot_path.name}...", end=" ")
                
                if method == "gpt52":
                    result = self.analyze_with_gpt52(screenshot_path, app_name, i + 1, total)
                elif method == "opus":
                    result = self.analyze_with_opus(screenshot_path, app_name, i + 1, total)
                elif method == "combined":
                    result = self.analyze_combined(screenshot_path, app_name, i + 1, total)
                
                app_results.append(result)
                print("✓")
                
                # 避免API限流
                time.sleep(0.5)
                
            except Exception as e:
                print(f"✗ 错误: {e}")
                continue
        
        # 保存App结果
        app_output_dir = output_dir / app_name
        app_output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = app_output_dir / "analysis.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "app_name": app_name,
                "total_screenshots": len(app_results),
                "analysis_method": method,
                "analyzed_at": datetime.now().isoformat(),
                "results": app_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  保存到: {output_file}")
        
        return app_results
    
    def run(self):
        """运行分析"""
        plans_to_run = []
        
        if self.plan == "ALL":
            plans_to_run = [("A", "gpt52"), ("B", "opus"), ("C", "combined")]
        elif self.plan == "A":
            plans_to_run = [("A", "gpt52")]
        elif self.plan == "B":
            plans_to_run = [("B", "opus")]
        elif self.plan == "C":
            plans_to_run = [("C", "combined")]
        
        for plan_name, method in plans_to_run:
            print(f"\n{'#'*60}")
            print(f"# 执行方案 {plan_name}: {method}")
            print(f"{'#'*60}")
            
            if method == "gpt52":
                output_dir = ANALYSIS_DIR / "analysis_gpt52"
            elif method == "opus":
                output_dir = ANALYSIS_DIR / "analysis_opus"
            else:
                output_dir = ANALYSIS_DIR / "analysis_combined"
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            all_results = {}
            
            for app_info in self.queue["apps"]:
                results = self.analyze_app(app_info, output_dir, method)
                all_results[app_info["name"]] = results
            
            # 保存汇总结果
            summary_file = output_dir / "all_results.json"
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump({
                    "plan": plan_name,
                    "method": method,
                    "total_apps": len(all_results),
                    "total_screenshots": sum(len(r) for r in all_results.values()),
                    "analyzed_at": datetime.now().isoformat(),
                    "apps": all_results
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n方案 {plan_name} 完成，结果保存到: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description="Onboarding Screenshot Analyzer")
    parser.add_argument(
        "--plan", 
        choices=["A", "B", "C", "ALL"], 
        default="ALL",
        help="分析方案: A=GPT-5.2, B=Claude Opus, C=双模型, ALL=全部"
    )
    parser.add_argument(
        "--app",
        type=str,
        default=None,
        help="只分析指定App（可选）"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Onboarding Screenshot Analyzer")
    print("="*60)
    print(f"分析方案: {args.plan}")
    print(f"数据目录: {DOWNLOADS_DIR}")
    print(f"输出目录: {ANALYSIS_DIR}")
    
    analyzer = OnboardingAnalyzer(plan=args.plan)
    analyzer.run()


if __name__ == "__main__":
    main()
