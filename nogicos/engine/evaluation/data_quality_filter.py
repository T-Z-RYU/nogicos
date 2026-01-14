"""
数据质量Filter器 - AutoFilter垃圾数据，只保留High质量Sample

Policy：
1. RuleFilter - Fast剔除明显的垃圾（EmptyResponse、Timeout、Error）
2. LLM 评分 - AI Judge数据质量（0-10分）
3. Auto标签 - Root据分数Auto打标签

用法:
    python -m engine.evaluation.data_quality_filter --project nogicos --threshold 6
"""

import os
import sys
import logging
import argparse
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from langsmith import Client
from anthropic import Anthropic

# Load API keys
try:
    from api_keys import setup_env
    setup_env()
except ImportError as e:
    logger.debug(f"api_keys Module未找到: {e}")

logger = logging.getLogger(__name__)

# qualityRule（moreloose，Adapt LangSmith DataFormat）
QUALITY_RULES = {
    # AutoReject（minutenumber=0）- onlyreject obvious's Spam
    "auto_reject": [
        lambda r: r.error is not None and "error" in str(r.error).lower(),  # haveexplicitError
        lambda r: r.outputs and "traceback" in str(r.outputs).lower(),  # Traceback leak
    ],
    # Autodecreaseminute（minutenumber-2）
    "auto_penalize": [
        lambda r: r.end_time and r.start_time and (r.end_time - r.start_time).total_seconds() > 60,  # Timeout >60s
        lambda r: not r.outputs,  # NoneOutput
        lambda r: r.outputs and len(str(r.outputs)) < 20,  # OutputtooShort
    ],
    # Autoaddminute（minutenumber+2）
    "auto_bonus": [
        lambda r: r.outputs and len(str(r.outputs)) > 100,  # have real quality output
        lambda r: r.end_time and r.start_time and (r.end_time - r.start_time).total_seconds() < 10,  # FastComplete
    ],
}


def apply_rule_filters(run) -> Tuple[float, List[str]]:
    """应用RuleFilter，Return基础分数和原因"""
    base_score = 6.0  # baseminute（DefaultMediumetcquality）
    reasons = []
    
    # CheckAutoReject
    for rule in QUALITY_RULES["auto_reject"]:
        try:
            if rule(run):
                return 0.0, ["auto_rejected"]
        except Exception:
            pass
    
    # Checkdecreaseminute
    for rule in QUALITY_RULES["auto_penalize"]:
        try:
            if rule(run):
                base_score -= 2
                reasons.append("penalized")
        except Exception:
            pass
    
    # Checkaddminute
    for rule in QUALITY_RULES["auto_bonus"]:
        try:
            if rule(run):
                base_score += 2
                reasons.append("bonus")
        except Exception:
            pass
    
    return max(1, min(10, base_score)), reasons  # mostLow 1 minute（exceptnonbeReject）


def llm_score_quality(task: str, response: str, client: Anthropic) -> Tuple[float, str]:
    """用 LLM Evaluate数据质量"""
    # IfInputtooShort，directlyReturnLowminute
    if not task or len(str(task)) < 5:
        return 3.0, "任务描述太短"
    if not response or len(str(response)) < 10:
        return 2.0, "Response太短"
    
    prompt = f"""Evaluate这条 AI Agent Execute数据的质量（用于训练/Evaluate）。

任务: {str(task)[:200]}
Response: {str(response)[:500]}

评分标准（0-10）:
- 10: 完美Execute，Response准确完整
- 7-9: ExecuteSuccess，Response合理
- 4-6: 部分Success，有改进Empty间
- 1-3: Execute有问题，但有学习价值
- 0: 垃圾数据，无价值

请回复格式:
分数: X
原因: 一句话解释

只回复Up面的格式，不要其他Inner容。"""

    try:
        llm_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = llm_response.content[0].text
        # Parseminutenumber
        score_lines = [l for l in text.split("\n") if "分数" in l]
        if not score_lines:
            return 5.0, "无法Parse分数"
        score = float(score_lines[0].split(":")[1].strip().split()[0])
        
        # Parseoriginalbecause
        reason_lines = [l for l in text.split("\n") if "原因" in l]
        reason = reason_lines[0].split(":", 1)[1].strip() if reason_lines else "无原因"
        
        return min(10, max(0, score)), reason
    except Exception as e:
        logger.warning(f"LLM 评分Failed: {e}")
        return 5.0, f"评分Failed: {str(e)[:30]}"


def filter_and_score_runs(
    project_name: str = "nogicos",
    hours: int = 24,
    threshold: float = 6.0,
    use_llm: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Filter和评分最近的 runs
    
    Args:
        project_name: LangSmith 项目名
        hours: view最近多少Hour的数据
        threshold: 质量Threshold（Low于此分数的标记为Low质量）
        use_llm: YesNoUsage LLM 评分（更准确但更慢）
        dry_run: 只Analyze不打标签
    
    Returns:
        StatisticsInfo
    """
    ls_client = Client()
    anthropic_client = Anthropic() if use_llm else None
    
    # Getmostnear's  runs
    start_time = datetime.now() - timedelta(hours=hours)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"NogicOS 数据质量Filter器")
    logger.info(f"{'='*60}")
    logger.info(f"项目: {project_name}")
    logger.info(f"TimeRange: 最近 {hours} Hour")
    logger.info(f"质量Threshold: {threshold}")
    logger.info(f"LLM 评分: {'Yes' if use_llm else 'No'}")
    logger.info(f"{'='*60}\n")
    
    runs = list(ls_client.list_runs(
        project_name=project_name,
        execution_order=1,  # only look at root runs
        start_time=start_time,
    ))
    
    logger.info(f"找到 {len(runs)} 条记录\n")
    
    stats = {
        "total": len(runs),
        "high_quality": 0,
        "medium_quality": 0,
        "low_quality": 0,
        "rejected": 0,
        "scores": [],
    }
    
    for i, run in enumerate(runs, 1):
        # trymultiplekindmaybe's InputFormat
        task = ""
        if run.inputs:
            task = run.inputs.get("task", "") or run.inputs.get("input", "") or run.inputs.get("query", "") or str(run.inputs)[:200]
        
        # trymultiplekindmaybe's OutputFormat
        response = ""
        if run.outputs:
            response = run.outputs.get("response", "") or run.outputs.get("output", "") or run.outputs.get("result", "") or str(run.outputs)[:500]
        
        # 1. RuleFilter
        rule_score, rule_reasons = apply_rule_filters(run)
        
        if rule_score == 0:
            final_score = 0
            reason = "RuleReject"
            stats["rejected"] += 1
        else:
            # 2. LLM Rating（Optional）
            if use_llm and rule_score >= 3:
                llm_score, llm_reason = llm_score_quality(task, response, anthropic_client)
                final_score = (rule_score + llm_score) / 2  # Average
                reason = llm_reason
            else:
                final_score = rule_score
                reason = "Rule评分"
            
            # Statistics
            if final_score >= 8:
                stats["high_quality"] += 1
            elif final_score >= threshold:
                stats["medium_quality"] += 1
            else:
                stats["low_quality"] += 1
        
        stats["scores"].append(final_score)
        
        # Printprogress
        quality_tag = "High" if final_score >= 8 else ("Medium" if final_score >= threshold else "Low")
        logger.info(f"[{i}/{len(runs)}] 分数: {final_score:.1f} ({quality_tag}) - {task[:40]}...")
        
        # 3. hitLabel
        if not dry_run:
            try:
                ls_client.create_feedback(
                    run.id,
                    key="quality_score",
                    score=final_score / 10,  # LangSmith use 0-1
                    comment=reason,
                )
                
                # qualityLabel
                quality_label = "high" if final_score >= 8 else ("medium" if final_score >= threshold else "low")
                ls_client.create_feedback(
                    run.id,
                    key="quality_label",
                    value=quality_label,
                )
            except Exception as e:
                logger.warning(f"打标签Failed: {e}")
    
    # PrintStatistics
    avg_score = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0
    total = stats["total"] if stats["total"] > 0 else 1  # prevent divide by zero
    
    logger.info(f"\n{'='*60}")
    logger.info("StatisticsResult")
    logger.info(f"{'='*60}")
    logger.info(f"总数: {stats['total']}")
    if stats['total'] > 0:
        logger.info(f"High质量 (>=8): {stats['high_quality']} ({stats['high_quality']/total*100:.1f}%)")
        logger.info(f"Medium等质量 ({threshold}-8): {stats['medium_quality']} ({stats['medium_quality']/total*100:.1f}%)")
        logger.info(f"Low质量 (<{threshold}): {stats['low_quality']} ({stats['low_quality']/total*100:.1f}%)")
        logger.info(f"被Reject: {stats['rejected']} ({stats['rejected']/total*100:.1f}%)")
        logger.info(f"Average分: {avg_score:.1f}")
    else:
        logger.info("没有找到数据，请扩大TimeRange (--hours)")
    logger.info(f"{'='*60}")
    
    return stats


def create_quality_dataset(
    project_name: str = "nogicos",
    dataset_name: str = "nogicos_quality",
    min_score: float = 7.0,
    limit: int = 100,
) -> None:
    """从High质量数据Create数据集"""
    ls_client = Client()
    
    logger.info(f"\nCreateHigh质量数据集: {dataset_name}")
    logger.info(f"最Low分数: {min_score}")
    
    # QueryHighminuteData
    runs = list(ls_client.list_runs(
        project_name=project_name,
        execution_order=1,
        filter=f'gte(feedback_score, {min_score/10})',  # 0-1 scale
        limit=limit,
    ))
    
    if not runs:
        logger.info("未找到High质量数据，尝试Query所有Success的 runs...")
        runs = list(ls_client.list_runs(
            project_name=project_name,
            execution_order=1,
            error=False,
            limit=limit,
        ))
    
    logger.info(f"找到 {len(runs)} 条符合Condition的数据")
    
    # CreateDataset
    try:
        dataset = ls_client.create_dataset(
            dataset_name=dataset_name,
            description=f"High质量数据集（分数>={min_score}）"
        )
    except Exception:
        dataset = ls_client.read_dataset(dataset_name=dataset_name)
    
    # AddExample
    added = 0
    for run in runs:
        if run.inputs and run.outputs:
            task = run.inputs.get("task")
            response = run.outputs.get("response")
            
            if task and response:
                try:
                    ls_client.create_example(
                        inputs={"task": task},
                        outputs={
                            "expected_response": response,
                            "expected_tools": [tc.get("name") for tc in run.outputs.get("tool_calls", []) if tc.get("name")],
                        },
                        dataset_id=dataset.id,
                        metadata={"source_run_id": str(run.id)}
                    )
                    added += 1
                except Exception as e:
                    logger.warning(f"AddExampleFailed: {e}")
    
    logger.info(f"SuccessAdd {added} 条High质量数据到 {dataset_name}")


def main():
    parser = argparse.ArgumentParser(description="NogicOS 数据质量Filter器")
    parser.add_argument("--project", type=str, default="nogicos", help="LangSmith 项目名")
    parser.add_argument("--hours", type=int, default=24, help="view最近多少Hour")
    parser.add_argument("--threshold", type=float, default=6.0, help="质量Threshold")
    parser.add_argument("--no-llm", action="store_true", help="不Usage LLM 评分（更快）")
    parser.add_argument("--dry-run", action="store_true", help="只Analyze不打标签")
    parser.add_argument("--create-dataset", type=str, help="CreateHigh质量数据集")
    parser.add_argument("--min-score", type=float, default=7.0, help="数据集最Low分数")
    
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    if args.create_dataset:
        create_quality_dataset(
            project_name=args.project,
            dataset_name=args.create_dataset,
            min_score=args.min_score,
        )
    else:
        filter_and_score_runs(
            project_name=args.project,
            hours=args.hours,
            threshold=args.threshold,
            use_llm=not args.no_llm,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()

