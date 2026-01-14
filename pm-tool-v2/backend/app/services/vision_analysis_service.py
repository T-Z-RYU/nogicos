"""
Vision Analysis Service
使用 GPT-5.2 和 Claude Opus 4.5 双模型分析 Onboarding 截图
"""
import base64
import asyncio
import json
import re
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from anthropic import Anthropic

from app.config import settings


# ============================================================================
# 数据模型
# ============================================================================

class ScreenCopy(BaseModel):
    """截图文案内容"""
    headline: Optional[str] = None
    subheadline: Optional[str] = None
    cta: Optional[str] = None


class ScreenAnalysis(BaseModel):
    """单个截图的分析结果"""
    index: int
    filename: str
    primary_type: str = Field(description="主类型: W/Q/V/S/A/R/D/C/G/L/X/P")
    secondary_type: Optional[str] = None
    phase: Optional[str] = None
    psychology: list[str] = Field(default_factory=list)
    ui_pattern: str = ""
    copy: ScreenCopy = Field(default_factory=ScreenCopy)
    insight: str = ""
    confidence: float = Field(ge=0, le=1, default=0.8)
    analyzed_by: str = "gpt-5.2 + claude-opus-4-5"


# ============================================================================
# Prompts
# ============================================================================

DEEP_ANALYSIS_PROMPT = """你是一位专业的移动应用 UX 研究员，专门分析健康/健身类 App 的 Onboarding 流程。

请仔细观察这张截图，分析以下内容：

1. **页面主要功能**：这个页面在做什么？（收集信息？展示价值？请求权限？）
2. **文案内容**：页面上的标题、副标题、按钮文字是什么？（请准确抄录）
3. **设计意图**：为什么在这个位置放这个页面？对用户心理有什么影响？
4. **心理策略**：使用了哪些说服技巧？（如：社会认同、权威背书、稀缺性、承诺一致性等）
5. **UI 模式**：这是什么类型的 UI 设计？（如：选择题、滑块、全屏品牌展示、价格卡片等）

请用中文详细分析，帮助我理解这个页面的设计意图。"""

CLASSIFICATION_PROMPT = """基于 GPT-5.2 的深度分析和原始截图，请将此页面分类为以下 12 种类型之一：

## 页面类型定义

- **W (Welcome)**: 品牌展示、欢迎语、App 启动屏、"Hello, I'm [App]" 类型
- **Q (Question)**: 收集用户信息的问题页（选择题、输入题、滑块、日期选择）
- **V (Value)**: 展示功能价值、利益点、功能预览、"With [App] you can..." 类型
- **S (Social)**: 用户证言、用户数统计、社区内容、"Join X million users" 类型
- **A (Authority)**: 专家背书、医生推荐、媒体报道、奖项认证、"#1 recommended by..." 类型
- **R (Result)**: 个性化结果展示、计算结果、分析报告、"Your plan is ready" 类型
- **D (Demo)**: 功能演示、交互式体验、产品预览、"Try it now" 类型
- **C (Commit)**: 目标承诺、用户协议、确认页、"I commit to..." 类型
- **G (Gamified)**: 游戏化元素、进度奖励、成就徽章、里程碑庆祝
- **L (Loading)**: 加载动画、处理中状态、Labor Illusion、"Analyzing your data..." 类型
- **X (Permission)**: 系统权限请求、通知/位置/健康授权、"Allow notifications" 类型
- **P (Paywall)**: 付费墙、订阅方案、价格展示、试用提示、"Start free trial" 类型

## 心理策略列表

请从以下策略中选择适用的：
- Brand Recognition (品牌认知)
- First Impression (第一印象)
- Value Proposition (价值主张)
- Social Proof (社会认同)
- Authority (权威背书)
- Personalization (个性化)
- Progressive Disclosure (渐进式披露)
- Commitment & Consistency (承诺一致性)
- Loss Aversion (损失厌恶)
- Scarcity (稀缺性)
- Reciprocity (互惠)
- Goal Setting (目标设定)
- Gender Data (性别数据)
- Body Data (身体数据)
- Activity Level (活动水平)
- Labor Illusion (努力错觉)
- Permission Pre-priming (权限预铺垫)
- Trust Building (信任建立)
- Privacy Assurance (隐私保障)

## 输出格式

请严格按以下 JSON 格式输出，不要添加任何其他内容：

```json
{
  "primary_type": "Q",
  "secondary_type": null,
  "psychology": ["Gender Data", "Personalization"],
  "ui_pattern": "Binary Choice",
  "copy": {
    "headline": "What's your biological sex?",
    "subheadline": "This helps us calculate your needs",
    "cta": "Continue"
  },
  "insight": "性别选择页，用于计算基础代谢率和个性化推荐",
  "confidence": 0.95
}
```"""


# ============================================================================
# Vision Analysis Service
# ============================================================================

class VisionAnalysisService:
    """双模型视觉分析服务"""
    
    def __init__(self):
        self.openai_client: Optional[OpenAI] = None
        self.anthropic_client: Optional[Anthropic] = None
        self._init_clients()
    
    def _init_clients(self):
        """初始化 API 客户端"""
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        
        if settings.anthropic_api_key and settings.anthropic_api_key != "your_anthropic_api_key_here":
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
    
    def is_configured(self) -> tuple[bool, bool]:
        """检查 API 是否已配置"""
        return (self.openai_client is not None, self.anthropic_client is not None)
    
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
    
    async def analyze_with_gpt52(self, image_base64: str, media_type: str = "image/png") -> str:
        """使用 GPT-5.2 进行深度视觉分析"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        response = self.openai_client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": DEEP_ANALYSIS_PROMPT},
                {
                    "role": "user",
                    "content": [
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
            max_completion_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content
    
    async def classify_with_opus(
        self, 
        image_base64: str, 
        gpt52_analysis: str,
        media_type: str = "image/png"
    ) -> dict:
        """使用 Opus 4.5 进行结构化分类"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        response = self.anthropic_client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=1000,
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
                            "text": f"GPT-5.2 深度分析结果:\n{gpt52_analysis}\n\n{CLASSIFICATION_PROMPT}"
                        }
                    ]
                }
            ]
        )
        
        # 解析 JSON 响应
        content = response.content[0].text
        
        # 尝试提取 JSON
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        # 尝试解析 JSON，如果失败则尝试修复常见问题
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError:
            # 尝试修复：替换嵌套引号问题
            fixed_json = re.sub(r'("headline":\s*)"([^"]*)"([^"]*)"([^"]*)"', r'\1"\2\3\4"', json_str)
            fixed_json = re.sub(r'("subheadline":\s*)"([^"]*)"([^"]*)"([^"]*)"', r'\1"\2\3\4"', fixed_json)
            fixed_json = re.sub(r'("cta":\s*)"([^"]*)"([^"]*)"([^"]*)"', r'\1"\2\3\4"', fixed_json)
            try:
                result = json.loads(fixed_json)
            except json.JSONDecodeError:
                # 如果还是失败，使用正则提取关键字段
                primary_match = re.search(r'"primary_type":\s*"([WQVSARDCGLXP])"', json_str)
                result = {
                    "primary_type": primary_match.group(1) if primary_match else "Q",
                    "secondary_type": None,
                    "psychology": [],
                    "ui_pattern": "Unknown",
                    "copy": {"headline": None, "subheadline": None, "cta": None},
                    "insight": "JSON parsing failed, using extracted type",
                    "confidence": 0.5
                }
        
        return result
    
    async def analyze_screenshot(
        self, 
        image_path: Path,
        index: int,
        use_dual_model: bool = True
    ) -> ScreenAnalysis:
        """
        分析单张截图
        
        Args:
            image_path: 截图文件路径
            index: 截图序号
            use_dual_model: 是否使用双模型（GPT-5.2 + Opus 4.5）
        
        Returns:
            ScreenAnalysis: 分析结果
        """
        filename = image_path.name
        media_type = self._get_media_type(filename)
        image_base64 = self._load_image_base64(image_path)
        
        if use_dual_model and self.openai_client and self.anthropic_client:
            # 双模型协作
            # Step 1: GPT-5.2 深度分析
            gpt52_analysis = await self.analyze_with_gpt52(image_base64, media_type)
            
            # Step 2: Opus 4.5 结构化分类
            classification = await self.classify_with_opus(image_base64, gpt52_analysis, media_type)
            
            analyzed_by = "gpt-5.2 + claude-opus-4-5"
        
        elif self.anthropic_client:
            # 仅使用 Opus 4.5
            classification = await self.classify_with_opus(
                image_base64, 
                "无 GPT-5.2 分析结果，请直接分析截图",
                media_type
            )
            analyzed_by = "claude-opus-4-5"
        
        elif self.openai_client:
            # 仅使用 GPT-5.2（需要修改 prompt 输出 JSON）
            gpt52_analysis = await self.analyze_with_gpt52(image_base64, media_type)
            # 简单解析
            classification = {
                "primary_type": "Q",
                "secondary_type": None,
                "psychology": [],
                "ui_pattern": "Unknown",
                "copy": {"headline": None, "subheadline": None, "cta": None},
                "insight": gpt52_analysis[:200],
                "confidence": 0.7
            }
            analyzed_by = "gpt-5.2"
        
        else:
            raise ValueError("No API keys configured")
        
        # 处理 copy 字段，确保 cta 是字符串而非列表
        copy_data = classification.get("copy", {})
        if isinstance(copy_data.get("cta"), list):
            copy_data["cta"] = ", ".join(copy_data["cta"])
        if isinstance(copy_data.get("headline"), list):
            copy_data["headline"] = ", ".join(copy_data["headline"])
        if isinstance(copy_data.get("subheadline"), list):
            copy_data["subheadline"] = ", ".join(copy_data["subheadline"])
        
        return ScreenAnalysis(
            index=index,
            filename=filename,
            primary_type=classification.get("primary_type", "Q"),
            secondary_type=classification.get("secondary_type"),
            psychology=classification.get("psychology", []),
            ui_pattern=classification.get("ui_pattern", ""),
            copy=ScreenCopy(**copy_data),
            insight=classification.get("insight", ""),
            confidence=classification.get("confidence", 0.8),
            analyzed_by=analyzed_by
        )
    
    async def analyze_app_screenshots(
        self,
        app_name: str,
        screenshots_dir: Path,
        start_index: int = 1,
        end_index: Optional[int] = None,
        concurrency: int = 3,
        progress_callback: Optional[callable] = None
    ) -> list[ScreenAnalysis]:
        """
        批量分析某个 App 的所有截图
        
        Args:
            app_name: App 名称
            screenshots_dir: 截图目录
            start_index: 起始序号
            end_index: 结束序号
            concurrency: 并发数
            progress_callback: 进度回调
        
        Returns:
            list[ScreenAnalysis]: 分析结果列表
        """
        # 获取所有截图文件
        screenshot_files = sorted([
            f for f in screenshots_dir.iterdir()
            if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]
        ])
        
        if end_index:
            screenshot_files = screenshot_files[:end_index]
        if start_index > 1:
            screenshot_files = screenshot_files[start_index - 1:]
        
        results = []
        semaphore = asyncio.Semaphore(concurrency)
        
        async def analyze_with_semaphore(file: Path, idx: int) -> ScreenAnalysis:
            async with semaphore:
                # Rate limit 重试逻辑
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        result = await self.analyze_screenshot(file, idx)
                        if progress_callback:
                            progress_callback(idx, len(screenshot_files), result)
                        return result
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "rate" in error_msg or "limit" in error_msg or "429" in error_msg:
                            wait_time = (attempt + 1) * 30  # 30s, 60s, 90s
                            print(f"    [RATE LIMIT] {file.name} - 等待 {wait_time}s 后重试...")
                            await asyncio.sleep(wait_time)
                        else:
                            if attempt == max_retries - 1:
                                raise
                            await asyncio.sleep(5)
                raise Exception(f"Failed after {max_retries} retries")
        
        tasks = [
            analyze_with_semaphore(f, i + start_index)
            for i, f in enumerate(screenshot_files)
        ]
        
        results = await asyncio.gather(*tasks)
        return list(results)


# 全局服务实例
vision_service = VisionAnalysisService()

