#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Full Evaluation Runner - 确保 100% Complete的EvaluateScript

特点：
- 逐个RunningTest用例，确保不Timeout
- 实时Save进度到File
- 支持断点continued跑
- Output详细Log
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path

# SetEncode
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AddPath
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load API Keys
try:
    import api_keys
    api_keys.setup_env()
except ImportError:
    print("[WARN] api_keys.py not found")

from engine.observability import get_logger, setup_logging
setup_logging()
logger = get_logger("full_eval")

# ImportEvaluateComponent
from engine.evaluation.dataset_manager import COMPREHENSIVE_EXAMPLES
from engine.agent.react_agent import ReActAgent


# progressFile
PROGRESS_FILE = Path(__file__).parent / "eval_progress.json"
RESULTS_FILE = Path(__file__).parent / "eval_results.json"


def load_progress():
    """Load已Complete的进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "results": []}


def save_progress(progress):
    """Save进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def save_results(results):
    """SaveFinalResult"""
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


async def run_single_case(agent, task: str, case_idx: int) -> dict:
    """Running单个Test用例"""
    start_time = time.time()
    ttft = None
    response_chunks = []
    error = None
    tool_calls = []
    
    # CallbackFunction
    async def on_text_delta(text: str):
        nonlocal ttft
        if ttft is None:
            ttft = time.time() - start_time
        response_chunks.append(text)
    
    async def on_tool_start(name: str, tool_id: str, args: dict):
        tool_calls.append(name)
    
    try:
        # Running agent (UsageCallback)
        result = await agent.run(
            task=task,
            session_id=f"eval_{case_idx}_{int(time.time())}",
            on_text_delta=on_text_delta,
            on_tool_start=on_tool_start,
        )
        
        # fromResultMediumGetResponse
        if isinstance(result, dict):
            if not response_chunks and result.get("response"):
                response_chunks.append(result.get("response", ""))
                
    except Exception as e:
        error = str(e)
        logger.error(f"Error running case {case_idx}: {e}")
    
    total_time = time.time() - start_time
    response = "".join(response_chunks)
    
    return {
        "task": task,
        "response": response[:500],  # Truncate
        "ttft_s": ttft,
        "total_time_s": total_time,
        "tool_calls": tool_calls,
        "error": error,
        "success": error is None and len(response) > 0,
    }


def evaluate_result(result: dict, expected: dict) -> dict:
    """Evaluate单个Result"""
    scores = {}
    
    # TTFT Rating
    ttft = result.get("ttft_s")
    if ttft is not None:
        if ttft < 1:
            scores["ttft"] = 1.0
        elif ttft < 2:
            scores["ttft"] = 0.7
        elif ttft < 3:
            scores["ttft"] = 0.5
        else:
            scores["ttft"] = 0.2
    else:
        scores["ttft"] = 0.0
    
    # DelayedRating
    total = result.get("total_time_s") or 999
    if total < 3:
        scores["latency"] = 1.0
    elif total < 5:
        scores["latency"] = 0.8
    elif total < 10:
        scores["latency"] = 0.6
    elif total < 20:
        scores["latency"] = 0.4
    else:
        scores["latency"] = 0.2
    
    # SuccessrateRating
    scores["success"] = 1.0 if result.get("success") else 0.0
    
    # follow-upDetection
    response = result.get("response", "")
    follow_up_patterns = ['?', '？', '请告诉', '什么', '哪', '希望', '需要']
    has_follow_up = any(p in response for p in follow_up_patterns)
    scores["follow_up"] = 1.0 if has_follow_up else 0.0
    
    # Innercontentrichrichdegree
    richness_score = 0
    if '```' in response:
        richness_score += 0.3
    if any(response.count(p) >= 2 for p in ['- ', '* ', '1. ', '2. ']):
        richness_score += 0.3
    if any(h in response for h in ['# ', '## ', '### ']):
        richness_score += 0.2
    if len(response) > 100:
        richness_score += 0.2
    scores["content_richness"] = min(richness_score, 1.0)
    
    # ToolCallcount
    scores["tool_calls"] = len(result.get("tool_calls", []))
    
    return scores


async def main():
    print("=" * 60)
    print("NogicOS Full Evaluation")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Loadprogress
    progress = load_progress()
    completed_indices = set(progress.get("completed", []))
    
    print(f"\nTotal test cases: {len(COMPREHENSIVE_EXAMPLES)}")
    print(f"Already completed: {len(completed_indices)}")
    print(f"Remaining: {len(COMPREHENSIVE_EXAMPLES) - len(completed_indices)}")
    
    # Initialize Agent
    print("\nInitializing agent...")
    agent = ReActAgent()
    print("Agent ready!\n")
    
    # RunningEvaluate
    all_results = progress.get("results", [])
    
    for idx, example in enumerate(COMPREHENSIVE_EXAMPLES):
        if idx in completed_indices:
            print(f"[{idx+1}/{len(COMPREHENSIVE_EXAMPLES)}] Skipped (already done)")
            continue
        
        task = example["inputs"]["task"]
        print(f"\n[{idx+1}/{len(COMPREHENSIVE_EXAMPLES)}] Testing: {task[:40]}...")
        
        try:
            # RunningsingleTest
            result = await run_single_case(agent, task, idx)
            
            # EvaluateResult
            scores = evaluate_result(result, example.get("outputs", {}))
            
            # MergeResult
            result["scores"] = scores
            result["case_idx"] = idx
            all_results.append(result)
            
            # Saveprogress
            progress["completed"].append(idx)
            progress["results"] = all_results
            save_progress(progress)
            
            # PrintResult
            ttft_str = f"{result['ttft_s']:.2f}s" if result['ttft_s'] else "N/A"
            total_str = f"{result['total_time_s']:.2f}s" if result['total_time_s'] else "N/A"
            print(f"  TTFT: {ttft_str} | Total: {total_str} | Success: {result['success']}")
            print(f"  Scores: ttft={scores['ttft']:.1f}, latency={scores['latency']:.1f}, success={scores['success']:.1f}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            # RecordFailedbutcontinue
            all_results.append({
                "task": task,
                "case_idx": idx,
                "error": str(e),
                "success": False,
                "scores": {"ttft": 0, "latency": 0, "success": 0, "follow_up": 0, "content_richness": 0}
            })
            progress["completed"].append(idx)
            progress["results"] = all_results
            save_progress(progress)
    
    # calculatecollecttotal
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    
    total = len(all_results)
    if total > 0:
        avg_ttft = sum(r.get("scores", {}).get("ttft", 0) for r in all_results) / total
        avg_latency = sum(r.get("scores", {}).get("latency", 0) for r in all_results) / total
        avg_success = sum(r.get("scores", {}).get("success", 0) for r in all_results) / total
        avg_follow_up = sum(r.get("scores", {}).get("follow_up", 0) for r in all_results) / total
        avg_richness = sum(r.get("scores", {}).get("content_richness", 0) for r in all_results) / total
        
        summary = {
            "total_cases": total,
            "completed_at": datetime.now().isoformat(),
            "scores": {
                "ttft": {"avg": avg_ttft, "target": 1.0},
                "latency": {"avg": avg_latency, "target": 0.8},
                "success": {"avg": avg_success, "target": 1.0},
                "follow_up": {"avg": avg_follow_up},
                "content_richness": {"avg": avg_richness},
            }
        }
        
        print(f"\nTotal cases: {total}")
        print(f"\nScores (0-1 scale):")
        print(f"  TTFT:             {avg_ttft:.2f} (target: 1.0 = <1s)")
        print(f"  Latency:          {avg_latency:.2f} (target: 0.8 = <5s)")
        print(f"  Success Rate:     {avg_success:.2f} (target: 1.0)")
        print(f"  Follow-up:        {avg_follow_up:.2f}")
        print(f"  Content Richness: {avg_richness:.2f}")
        
        # SaveFinalResult
        save_results({"summary": summary, "details": all_results})
        print(f"\nResults saved to: {RESULTS_FILE}")
    
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
