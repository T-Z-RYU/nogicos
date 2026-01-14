# -*- coding: utf-8 -*-
"""
NogicOS Evaluators for LangSmith - 最佳实践版本

Evaluate器设计原则：
1. RuleEvaluate器只用于客观可量化的指标（Delayed、Token数、Tool调用次数、Error率）
2. 语义Judge交给 LLM Evaluate器（任务Complete度、ToolSelect合理性、正确性、幻觉、简洁性）
3. UX Evaluate器用于感知Iterate变化（TTFT、追问建议、Inner容丰富度）

Usage:
    from engine.evaluation.evaluators import (
        # RuleEvaluateer（objective metrics）
        latency_evaluator,
        token_count_evaluator,
        tool_call_count_evaluator,
        error_rate_evaluator,
        
        # UX Evaluateer（Userexperience）
        ttft_evaluator,
        follow_up_evaluator,
        content_richness_evaluator,
        
        # LLM Evaluateer（semantic understanding）
        task_completion_llm_evaluator,
        tool_selection_llm_evaluator,
        correctness_evaluator,
        hallucination_evaluator,
        conciseness_evaluator,
        
        # EvaluateerList
        get_rule_evaluators,
        get_llm_evaluators,
        get_ux_evaluators,  # Newincrease：UX Evaluateer
        get_all_evaluators,
    )
"""

import re
import time
from typing import Dict, Any, Optional, List, Callable

from engine.observability import get_logger
logger = get_logger("evaluators")

# Centralized keyword list for tool-required task detection
TOOL_REQUIRED_KEYWORDS = [
    "File", "Directory", "Open", "Create", "Delete", "浏览器", "Search",
    "file", "directory", "open", "create", "delete", "browser", "search",
    "桌面", "Window", "截Graph", "desktop", "window", "screenshot",
]

# Try to import LangSmith
try:
    from langsmith.evaluation.evaluator import run_evaluator
    from langsmith.schemas import Run, Example
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    run_evaluator = lambda f: f
    Run = Any
    Example = Any
    logger.warning("[Evaluators] LangSmith not available")

# Try to import openevals for LLM-as-judge
try:
    from openevals.llm import create_llm_as_judge
    from openevals.prompts import (
        CORRECTNESS_PROMPT,
        HALLUCINATION_PROMPT,
        CONCISENESS_PROMPT,
    )
    OPENEVALS_AVAILABLE = True
    logger.info("[Evaluators] openevals available - LLM-as-judge enabled")
except ImportError:
    OPENEVALS_AVAILABLE = False
    logger.warning("[Evaluators] openevals not available - install with: pip install openevals")


# ===========================================
# RuleEvaluateer - objective quantifiablemetric
# ===========================================

@run_evaluator
def latency_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    DelayedEvaluate器 - 客观指标
    
    评分标准：
    - 1.0: < 3s (excellent)
    - 0.8: 3-5s (good)
    - 0.6: 5-10s (acceptable)
    - 0.4: 10-20s (slow)
    - 0.2: 20-30s (very slow)
    - 0.0: > 30s (timeout)
    """
    try:
        outputs = run.outputs or {}
        latency_ms = None
        
        # from run elementDataGet
        if run.end_time and run.start_time:
            latency_ms = (run.end_time - run.start_time).total_seconds() * 1000
        
        # from outputs Get
        if latency_ms is None and outputs:
            latency_ms = outputs.get("total_time_ms")
        
        if latency_ms is None:
            return {"key": "latency", "score": 0.5, "comment": "Latency data not available"}
        
        latency_s = latency_ms / 1000
        
        if latency_s < 3:
            score, rating = 1.0, "excellent"
        elif latency_s < 5:
            score, rating = 0.8, "good"
        elif latency_s < 10:
            score, rating = 0.6, "acceptable"
        elif latency_s < 20:
            score, rating = 0.4, "slow"
        elif latency_s < 30:
            score, rating = 0.2, "very slow"
        else:
            score, rating = 0.0, "timeout"
        
        return {"key": "latency", "score": score, "comment": f"{latency_s:.1f}s ({rating})"}
        
    except Exception as e:
        logger.error(f"[latency_evaluator] Error: {e}")
        return {"key": "latency", "score": 0.5, "comment": f"Error: {str(e)[:100]}"}


@run_evaluator
def token_count_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    Token Usage量Evaluate器 - 客观指标
    
    评分标准（基于单次任务）：
    - 1.0: < 1000 tokens (efficient)
    - 0.8: 1000-3000 tokens (good)
    - 0.6: 3000-5000 tokens (acceptable)
    - 0.4: 5000-10000 tokens (high)
    - 0.2: > 10000 tokens (very high)
    """
    try:
        outputs = run.outputs or {}
        
        # tryneversamefromSourceGet token number
        total_tokens = None
        
        # from outputs Get
        if outputs:
            total_tokens = outputs.get("total_tokens") or outputs.get("token_count")
        
        # from run 's  feedback orOtherelementDataGet
        if total_tokens is None and hasattr(run, 'extra') and run.extra:
            total_tokens = run.extra.get("total_tokens")
        
        if total_tokens is None:
            return {"key": "token_count", "score": 0.5, "comment": "Token count not available"}
        
        if total_tokens < 1000:
            score, rating = 1.0, "efficient"
        elif total_tokens < 3000:
            score, rating = 0.8, "good"
        elif total_tokens < 5000:
            score, rating = 0.6, "acceptable"
        elif total_tokens < 10000:
            score, rating = 0.4, "high"
        else:
            score, rating = 0.2, "very high"
        
        return {"key": "token_count", "score": score, "comment": f"{total_tokens} tokens ({rating})"}
        
    except Exception as e:
        logger.error(f"[token_count_evaluator] Error: {e}")
        return {"key": "token_count", "score": 0.5, "comment": f"Error: {str(e)[:100]}"}


@run_evaluator
def tool_call_count_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    Tool调用次数Evaluate器 - 客观指标
    
    评分标准：
    - 1.0: 0-2 calls (efficient)
    - 0.8: 3-4 calls (good)
    - 0.6: 5-6 calls (acceptable)
    - 0.4: 7-10 calls (many)
    - 0.2: > 10 calls (excessive)
    
    注意：简单对话任务 0 次调用也Yes 1.0 分
    """
    try:
        outputs = run.outputs or {}
        inputs = run.inputs or {}
        
        tool_calls = outputs.get("tool_calls", []) or []
        num_calls = len(tool_calls)
        
        # simpleDialogNot NeedTool
        task = inputs.get("task", "") or ""
        is_simple_chat = not any(kw in task.lower() for kw in TOOL_REQUIRED_KEYWORDS)
        
        if is_simple_chat and num_calls == 0:
            return {"key": "tool_call_count", "score": 1.0, "comment": "Simple chat, no tools needed"}
        
        if num_calls <= 2:
            score, rating = 1.0, "efficient"
        elif num_calls <= 4:
            score, rating = 0.8, "good"
        elif num_calls <= 6:
            score, rating = 0.6, "acceptable"
        elif num_calls <= 10:
            score, rating = 0.4, "many"
        else:
            score, rating = 0.2, "excessive"
        
        return {"key": "tool_call_count", "score": score, "comment": f"{num_calls} calls ({rating})"}
        
    except Exception as e:
        logger.error(f"[tool_call_count_evaluator] Error: {e}")
        return {"key": "tool_call_count", "score": 0.5, "comment": f"Error: {str(e)[:100]}"}


@run_evaluator
def error_rate_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    Error率Evaluate器 - 客观指标
    
    CheckToolExecuteYesNo有Error，以及FinalResultYesNoSuccess
    
    评分标准：
    - 1.0: 无Error
    - 0.7: 有小Error但FinalSuccess
    - 0.3: 有Error且影响Result
    - 0.0: 完全Failed
    """
    try:
        outputs = run.outputs or {}
        
        success = outputs.get("success", False)
        error = outputs.get("error", "") or ""
        tool_calls = outputs.get("tool_calls", []) or []
        
        # StatisticsToolError
        tool_errors = 0
        for tc in tool_calls:
            if isinstance(tc, dict):
                if not tc.get("success", True) or tc.get("error"):
                    tool_errors += 1
        
        tool_error_rate = tool_errors / len(tool_calls) if tool_calls else 0
        
        # comprehensiveRating
        if success and tool_error_rate == 0:
            score = 1.0
            comment = "No errors"
        elif success and tool_error_rate < 0.3:
            score = 0.7
            comment = f"Success with {tool_errors} tool errors"
        elif success:
            score = 0.5
            comment = f"Success but high error rate: {tool_error_rate:.0%}"
        elif error:
            score = 0.0
            comment = f"Failed: {error[:100]}"
        else:
            score = 0.3
            comment = "Partial failure"
        
        return {"key": "error_rate", "score": score, "comment": comment}
        
    except Exception as e:
        logger.error(f"[error_rate_evaluator] Error: {e}")
        return {"key": "error_rate", "score": 0.5, "comment": f"Error: {str(e)[:100]}"}


# ===========================================
# UX Evaluateer - Userexperiencemetric（perceptionIteratechange）
# ===========================================

@run_evaluator
def ttft_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    TTFT (Time To First Token) Evaluate器
    
    评分标准：
    - 1.0: < 1s (excellent - Target)
    - 0.7: 1-2s (good)
    - 0.5: 2-3s (acceptable)
    - 0.2: > 3s (slow)
    """
    try:
        outputs = run.outputs or {}
        
        # way1: from outputs Get（agent Output）
        ttft_ms = outputs.get("ttft_ms")
        
        # way2: from run 's  first_token_time calculate
        if ttft_ms is None and hasattr(run, 'first_token_time') and run.start_time:
            if run.first_token_time:
                ttft_ms = (run.first_token_time - run.start_time).total_seconds() * 1000
        
        # way3: Ifallno，usetotalDelayed's estimate（Falseset TTFT YestotalTime's  30%）
        if ttft_ms is None and run.end_time and run.start_time:
            total_ms = (run.end_time - run.start_time).total_seconds() * 1000
            ttft_ms = total_ms * 0.3  # estimate
        
        if ttft_ms is None:
            return {"key": "ttft", "score": 0.5, "comment": "TTFT not available"}
        
        # Rating
        if ttft_ms < 1000:
            score, rating = 1.0, "excellent"
        elif ttft_ms < 2000:
            score, rating = 0.7, "good"
        elif ttft_ms < 3000:
            score, rating = 0.5, "acceptable"
        else:
            score, rating = 0.2, "slow"
        
        return {"key": "ttft", "score": score, "comment": f"{ttft_ms:.0f}ms ({rating})"}
        
    except Exception as e:
        logger.error(f"[ttft_evaluator] Error: {e}")
        return {"key": "ttft", "score": 0.5, "comment": f"Error: {str(e)[:100]}"}


@run_evaluator
def follow_up_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    追问建议Evaluate器 - 检测ResponseYesNoPackage含追问建议
    
    评分标准：
    - 1.0: 有 2+ 个追问建议
    - 0.7: 有 1 个追问建议
    - 0.5: 有模糊的追问暗示
    - 0.0: 无追问建议
    
    检测模式：
    - JSON 格式: {"follow_ups": [...]}
    - List格式: "你可能还想：\n- xxx\n- yyy"
    - 问句格式: "需要我帮你xxx吗？"
    """
    try:
        outputs = run.outputs or {}
        inputs = run.inputs or {}
        
        response = outputs.get("response", "")
        task = inputs.get("task", "")
        
        # CheckYesNoYesNeedfollow-up's scene
        ambiguous_keywords = ["整理", "优化", "改进", "Handle", "帮我", "这个", "那个"]
        needs_follow_up = any(kw in task for kw in ambiguous_keywords) and len(task) < 20
        
        # IfnotYesNeedfollow-up's scene，directlyReturnFullminute
        if not needs_follow_up:
            return {"key": "follow_up", "score": 1.0, "comment": "No follow-up needed for this task"}
        
        follow_up_count = 0
        
        # Detectionway1: JSON Format
        if "follow_ups" in response or "follow_up" in response:
            follow_up_count += 2
        
        # Detectionway2: ListFormat
        list_patterns = [
            r"你可能还想[：:]\s*\n",
            r"你YesNo需要[：:]",
            r"建议[：:]\s*\n\s*[-•]",
            r"可以考虑[：:]",
        ]
        for pattern in list_patterns:
            if re.search(pattern, response):
                follow_up_count += 1
                break
        
        # Detectionway3: questionFormat
        question_patterns = [
            r"需要我.*吗[？?]",
            r"要不要.*[？?]",
            r"YesNo需要.*[？?]",
            r"还有什么.*[？?]",
            r"请问.*[？?]",
            r"想要.*吗[？?]",
        ]
        for pattern in question_patterns:
            if re.search(pattern, response):
                follow_up_count += 1
                break
        
        # Rating
        if follow_up_count >= 2:
            score, rating = 1.0, "excellent"
        elif follow_up_count == 1:
            score, rating = 0.7, "good"
        elif "?" in response or "？" in response:
            score, rating = 0.5, "has question"
        else:
            score, rating = 0.0, "no follow-up"
        
        return {"key": "follow_up", "score": score, "comment": f"{follow_up_count} suggestions ({rating})"}
        
    except Exception as e:
        logger.error(f"[follow_up_evaluator] Error: {e}")
        return {"key": "follow_up", "score": 0.5, "comment": f"Error: {str(e)[:100]}"}


@run_evaluator
def content_richness_evaluator(run: Run, example: Example) -> Dict[str, Any]:
    """
    Inner容丰富度Evaluate器 - 检测Response的结构化程度
    
    检测Inner容Class型：
    - 代码块 (```code```)
    - List (- item 或 1. item)
    - title (# / ## / ###)
    - Table格 (| col |)
    - 链接 ([text](url))
    
    评分标准：
    - 1.0: 3+ 种Inner容Class型
    - 0.8: 2 种Inner容Class型
    - 0.6: 1 种Inner容Class型
    - 0.4: 只有纯文本
    """
    try:
        outputs = run.outputs or {}
        inputs = run.inputs or {}
        
        response = outputs.get("response", "")
        task = inputs.get("task", "")
        
        # CheckYesNoYesNeedrichInnercontent's scene
        rich_content_keywords = [
            "Write", "代码", "Function", "Script", "List", "步骤", "对比", "Compare",
            "解释", "说明", "Analyze", "Report", "总结", "整理",
        ]
        needs_rich_content = any(kw in task for kw in rich_content_keywords)
        
        # IfYessimpleDialog，Not NeedrichInnercontent
        simple_chat_patterns = ["你好", "谢谢", "再见", "好的", "明白"]
        if any(p in task for p in simple_chat_patterns) and len(task) < 10:
            return {"key": "content_richness", "score": 1.0, "comment": "Simple chat, no rich content needed"}
        
        content_types = []
        
        # Detectioncodeblock
        if re.search(r"```[\s\S]*?```", response):
            content_types.append("code")
        
        # DetectionList
        if re.search(r"^\s*[-•*]\s+", response, re.MULTILINE) or re.search(r"^\s*\d+[.、]\s+", response, re.MULTILINE):
            content_types.append("list")
        
        # Detectiontitle
        if re.search(r"^#{1,3}\s+", response, re.MULTILINE):
            content_types.append("heading")
        
        # DetectionTablegrid
        if re.search(r"\|.*\|.*\|", response):
            content_types.append("table")
        
        # Detectionlink
        if re.search(r"\[.+?\]\(.+?\)", response):
            content_types.append("link")
        
        # Detectionemphasize
        if re.search(r"\*\*.+?\*\*|__.+?__", response):
            content_types.append("emphasis")
        
        num_types = len(content_types)
        
        # Rating
        if num_types >= 3:
            score, rating = 1.0, "rich"
        elif num_types == 2:
            score, rating = 0.8, "good"
        elif num_types == 1:
            score, rating = 0.6, "basic"
        else:
            # if need richInnercontentbut none, deduct points
            if needs_rich_content:
                score, rating = 0.4, "plain text"
            else:
                score, rating = 0.7, "acceptable plain"
        
        types_str = ", ".join(content_types) if content_types else "none"
        return {"key": "content_richness", "score": score, "comment": f"{num_types} types: {types_str} ({rating})"}
        
    except Exception as e:
        logger.error(f"[content_richness_evaluator] Error: {e}")
        return {"key": "content_richness", "score": 0.5, "comment": f"Error: {str(e)[:100]}"}


# ===========================================
# LLM Evaluateer - semantic understanding
# ===========================================

# Custom prompt forTaskCompletedegreeEvaluate
# NOTE: openevals Usage {inputs} and {outputs} asforVariablename
TASK_COMPLETION_PROMPT = """You are evaluating whether an AI agent successfully completed a user's task.

User's Task: {inputs}

Agent's Response: {outputs}

Evaluate based on:
1. Did the agent understand the task correctly?
2. Did the agent provide a relevant and helpful response?
3. If the task required actions (file operations, web browsing, etc.), were they completed?

Score:
- 1.0: Task fully completed with correct and helpful response
- 0.7: Task mostly completed, minor issues
- 0.5: Task partially completed
- 0.3: Task poorly completed, significant issues
- 0.0: Task not completed or completely wrong

Respond with a JSON object: {{"score": <number>, "reasoning": "<explanation>"}}"""


# Custom prompt forToolSelectEvaluate
# NOTE: hereUsage {inputs} PackagecontainTaskandToolInfo
TOOL_SELECTION_PROMPT = """You are evaluating whether an AI agent selected appropriate tools for a task.

Task and Tools Info:
{inputs}

Agent's Response:
{outputs}

Evaluate based on:
1. Were the tools appropriate for the task?
2. Was the number of tools reasonable (not excessive)?
3. Were there any unnecessary tool calls?
4. Were there any missing tool calls that should have been made?

Score:
- 1.0: Optimal tool selection
- 0.7: Good selection with minor inefficiencies
- 0.5: Acceptable but not optimal
- 0.3: Poor selection, wrong or excessive tools
- 0.0: No tools used when needed, or completely wrong tools

Respond with a JSON object: {{"score": <number>, "reasoning": "<explanation>"}}"""


# Evaluator modetypeConfigConstant
# Optional:
#   - "anthropic:claude-opus-4-5-20251101" (Claude Opus 4.5 - newest and strongest)
#   - "anthropic:claude-3-5-sonnet-20241022" (Claude 3.5 Sonnet - price-performance ratio)
#   - "openai:gpt-4o-mini" (GPT-4o-mini - most affordable)
EVALUATOR_MODEL_OPUS = "anthropic:claude-opus-4-5-20251101"
EVALUATOR_MODEL_SONNET = "anthropic:claude-3-5-sonnet-20241022"
EVALUATOR_MODEL_GPT4O_MINI = "openai:gpt-4o-mini"

# Default model
EVALUATOR_MODEL = EVALUATOR_MODEL_OPUS  # Claude Opus 4.5 (2025Year11Month)


def _create_llm_evaluators():
    """Create LLM-as-judge Evaluate器（Usage Claude Opus 4.5）
    
    IMPORTANT: 这个Function必须在 setup_env() 之After调用，No则没有 API Key
    """
    if not OPENEVALS_AVAILABLE:
        logger.warning("[Evaluators] openevals not available, LLM evaluators disabled")
        return {}
    
    # ensure API Key alreadySet
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("[Evaluators] ANTHROPIC_API_KEY not set, trying to load from api_keys...")
        try:
            from api_keys import setup_env
            setup_env()
        except Exception as e:
            logger.error(f"[Evaluators] Failed to load API keys: {e}")
            return {}
    
    try:
        evaluators = {}
        model = EVALUATOR_MODEL
        logger.info(f"[Evaluators] Using model: {model}")
        
        # correctpropertyEvaluateer
        evaluators['correctness'] = create_llm_as_judge(
            prompt=CORRECTNESS_PROMPT,
            model=model,
            feedback_key="correctness",
        )
        
        # hallucinationDetectionEvaluateer
        evaluators['hallucination'] = create_llm_as_judge(
            prompt=HALLUCINATION_PROMPT,
            model=model,
            feedback_key="hallucination",
        )
        
        # simple and cleanEvaluateer
        evaluators['conciseness'] = create_llm_as_judge(
            prompt=CONCISENESS_PROMPT,
            model=model,
            feedback_key="conciseness",
        )
        
        # TaskCompletedegreeEvaluateer
        evaluators['task_completion'] = create_llm_as_judge(
            prompt=TASK_COMPLETION_PROMPT,
            model=model,
            feedback_key="task_completion_llm",
        )
        
        # ToolSelectEvaluateer
        evaluators['tool_selection'] = create_llm_as_judge(
            prompt=TOOL_SELECTION_PROMPT,
            model=model,
            feedback_key="tool_selection_llm",
        )
        
        logger.info("[Evaluators] LLM-as-judge evaluators created successfully (Claude Opus 4.5)")
        return evaluators
        
    except Exception as e:
        logger.error(f"[Evaluators] Failed to create LLM evaluators: {e}")
        return {}


# lazy load LLM Evaluateer（avoidinImporttimethenNeed API Key）
_llm_evaluators = None

def _get_llm_evaluators():
    """lazy loadGet LLM Evaluate器"""
    global _llm_evaluators
    if _llm_evaluators is None:
        _llm_evaluators = _create_llm_evaluators()
    return _llm_evaluators


def _wrap_llm_evaluator(evaluator_key: str, feedback_key: str):
    """
    Package装 LLM Evaluate器，HandleFieldConvert和Error
    
    Return一个Usage @run_evaluator 装饰器格式的Evaluate器Function，
    这样 LangSmith 可以正确调用它。
    
    IMPORTANT: openevals 期望 inputs/outputs YesCharacter串，不YesDict！
    """
    
    @run_evaluator
    def evaluator_fn(run: Run, example: Example) -> Dict[str, Any]:
        evaluators = _get_llm_evaluators()
        llm_eval = evaluators.get(evaluator_key)
        if llm_eval is None:
            return {"key": feedback_key, "score": 0.5, "comment": "LLM evaluator not available"}
        
        try:
            # from run Get inputs and outputs
            run_inputs = run.inputs or {}
            run_outputs = run.outputs or {}
            
            # openevals expectCharacterstringArgument，notYesDict！
            task_str = run_inputs.get("task", "")
            response_str = run_outputs.get("response", "")
            
            # forToolSelectEvaluateer，AddToolInfoto inputs
            if evaluator_key == "tool_selection":
                tool_calls = run_outputs.get("tool_calls", [])
                tools_str = ", ".join(
                    tc.get("name", "unknown") for tc in tool_calls if isinstance(tc, dict)
                ) if tool_calls else "None"
                task_str = f"Task: {task_str}\nTools used: {tools_str}"
            
            # Get reference outputs（Ifhave）
            ref_str = ""
            if example and hasattr(example, 'outputs') and example.outputs:
                ref_outputs = example.outputs
                ref_str = str(ref_outputs.get("trajectory", ref_outputs.get("response_pattern", "")))
            
            # CallEvaluateer - UsageCharacterstringArgument
            if evaluator_key == "hallucination":
                # hallucinationDetectionNeed context Argument
                result = llm_eval(
                    inputs=task_str,
                    outputs=response_str,
                    context=response_str,  # use response itselfasfor context
                    reference_outputs=ref_str,
                )
            else:
                result = llm_eval(
                    inputs=task_str,
                    outputs=response_str,
                    reference_outputs=ref_str,
                )
            
            # openevals maybeReturn dict or object
            if isinstance(result, dict):
                raw_score = result.get('score', 0.5)
                comment = result.get('comment', "LLM evaluation completed")
            else:
                raw_score = result.score if hasattr(result, 'score') else 0.5
                comment = result.comment if hasattr(result, 'comment') else "LLM evaluation completed"
            
            # openevals ReturnBooleanValueorCharacterstring，NeedConvertforFloatnumber
            if isinstance(raw_score, bool):
                score = 1.0 if raw_score else 0.0
            elif isinstance(raw_score, str):
                try:
                    score = float(raw_score)
                except ValueError:
                    score = 0.5  # NonemethodParsetimeUsageDefaultValue
            elif isinstance(raw_score, (int, float)):
                score = float(raw_score)
            else:
                score = 0.5  # DefaultValue
            
            return {"key": feedback_key, "score": score, "comment": comment}
            
        except Exception as e:
            logger.error(f"[{feedback_key}] Error: {e}")
            return {"key": feedback_key, "score": 0.5, "comment": f"Error: {str(e)[:100]}"}
    
    return evaluator_fn


# Create LLM EvaluateerFunction
correctness_evaluator = _wrap_llm_evaluator("correctness", "correctness")
hallucination_evaluator = _wrap_llm_evaluator("hallucination", "hallucination")
conciseness_evaluator = _wrap_llm_evaluator("conciseness", "conciseness")
task_completion_llm_evaluator = _wrap_llm_evaluator("task_completion", "task_completion_llm")
tool_selection_llm_evaluator = _wrap_llm_evaluator("tool_selection", "tool_selection_llm")


# ===========================================
# EvaluateerSetFunction
# ===========================================

def get_rule_evaluators() -> List[Callable]:
    """
    GetRuleEvaluate器List（客观指标，Fast、免费）
    
    Package含：
    - latency: Delayed
    - token_count: Token Usage量
    - tool_call_count: Tool调用次数
    - error_rate: Error率
    """
    return [
        latency_evaluator,
        token_count_evaluator,
        tool_call_count_evaluator,
        error_rate_evaluator,
    ]


def get_llm_evaluators() -> List[Callable]:
    """
    Get LLM-as-judge Evaluate器List（语义理解，准确但收费）
    
    Package含：
    - task_completion_llm: 任务Complete度
    - tool_selection_llm: ToolSelect合理性
    - correctness: 正确性
    - hallucination: 幻觉检测
    - conciseness: 简洁性
    
    注意：需要 OpenAI API Key
    """
    if not OPENEVALS_AVAILABLE:
        logger.warning("[Evaluators] LLM evaluators not available")
        return []
    
    return [
        task_completion_llm_evaluator,
        tool_selection_llm_evaluator,
        correctness_evaluator,
        hallucination_evaluator,
        conciseness_evaluator,
    ]


def get_all_evaluators() -> List[Callable]:
    """
    Get所有Evaluate器（Rule + UX + LLM）
    
    Package含全部 11 个Evaluate器：
    - Rule: latency, token_count, tool_call_count, error_rate
    - UX: ttft, follow_up, content_richness
    - LLM: task_completion, hallucination, correctness, conciseness, tool_selection
    
    推荐用于全面Evaluate
    """
    evaluators = get_rule_evaluators()  # 4 aRuleEvaluateer
    
    # Add UX Evaluateer（notDuplicateAdd latency）
    evaluators.extend([
        ttft_evaluator,
        follow_up_evaluator,
        content_richness_evaluator,
    ])
    
    # Add LLM Evaluateer
    evaluators.extend(get_llm_evaluators())
    
    return evaluators


def get_fast_evaluators() -> List[Callable]:
    """
    GetFastEvaluate器（只有RuleEvaluate器）
    
    推荐用于FastIterateTest
    """
    return get_rule_evaluators()


def get_quality_evaluators() -> List[Callable]:
    """
    Get质量Evaluate器（Rule + 幻觉检测 + 任务Complete度）
    
    balanced成本和质量检测
    """
    evaluators = get_rule_evaluators()
    
    if OPENEVALS_AVAILABLE:
        evaluators.extend([
            task_completion_llm_evaluator,
            hallucination_evaluator,
        ])
    
    return evaluators


def get_essential_evaluators() -> List[Callable]:
    """
    GetCoreEvaluate器（最Important的指标）
    
    Package含：Delayed、Error率、任务Complete度、幻觉检测
    """
    evaluators = [
        latency_evaluator,
        error_rate_evaluator,
    ]
    
    if OPENEVALS_AVAILABLE:
        evaluators.extend([
            task_completion_llm_evaluator,
            hallucination_evaluator,
        ])
    
    return evaluators


def get_ux_evaluators() -> List[Callable]:
    """
    Get UX Evaluate器（User体验指标，感知Iterate变化）
    
    Package含：
    - ttft: First Token Time（Target < 1s）
    - follow_up: 追问建议检测
    - content_richness: Inner容丰富度
    - latency: 总Delayed
    - task_completion_llm: 任务Complete度
    
    推荐用于Iterate对比Evaluate
    """
    evaluators = [
        ttft_evaluator,
        follow_up_evaluator,
        content_richness_evaluator,
        latency_evaluator,
    ]
    
    if OPENEVALS_AVAILABLE:
        evaluators.append(task_completion_llm_evaluator)
    
    return evaluators


# ===========================================
# Compatpropertyothername（keeptowardAfterCompat）
# ===========================================

# Old's EvaluateernamepointertowardNew's Implement
task_completion_evaluator = task_completion_llm_evaluator
tool_selection_evaluator = tool_selection_llm_evaluator
response_quality_evaluator = conciseness_evaluator  # response_quality be conciseness replaces
