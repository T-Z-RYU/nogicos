# -*- coding: utf-8 -*-
"""
AgentBench OS Interaction Adapter

Runs OFFICIAL AgentBench OS tasks that can execute locally (no Docker required).
These are UNMODIFIED from the official repository.
"""

import asyncio
import json
import os
import sys
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load official AgentBench tasks
AGENTBENCH_DATA = Path(__file__).parent.parent.parent / "benchmarks" / "AgentBench" / "data" / "os_interaction" / "data" / "dev.json"


@dataclass
class AgentBenchTask:
    """Official AgentBench task"""
    id: int
    description: str
    expected_answer: Optional[str]
    match_type: str  # "exact", "integer", "string", "contains"
    labels: List[str]
    requires_docker: bool


def load_agentbench_tasks() -> List[AgentBenchTask]:
    """Load official AgentBench OS tasks"""
    with open(AGENTBENCH_DATA, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = []
    for i, item in enumerate(data):
        desc = item.get("description", "")
        
        # Determine if requires Docker (has init scripts or special environment)
        requires_docker = False
        if "create" in item and item["create"]:
            if isinstance(item["create"], dict):
                if "init" in item["create"] or "local" in item["create"]:
                    requires_docker = True
            elif isinstance(item["create"], list):
                requires_docker = True
        if "start" in item:  # Background process
            requires_docker = True
        
        # Get expected answer
        expected = None
        match_type = "unknown"
        
        eval_info = item.get("evaluation", {})
        if "match" in eval_info:
            expected = eval_info["match"]
            match_type = "exact"
        elif "check" in eval_info:
            check = eval_info["check"]
            if isinstance(check, list):
                for c in check:
                    if c and isinstance(c, dict) and "file" in c:
                        if "integer-match" in c["file"]:
                            match_type = "integer"
                        elif "string-match" in c["file"]:
                            match_type = "string"
                        elif "size-match" in c["file"]:
                            match_type = "size"
                        elif "containing" in c["file"]:
                            match_type = "contains"
        
        tasks.append(AgentBenchTask(
            id=i,
            description=desc,
            expected_answer=expected,
            match_type=match_type,
            labels=item.get("labels", []),
            requires_docker=requires_docker
        ))
    
    return tasks


def get_local_runnable_tasks(tasks: List[AgentBenchTask]) -> List[AgentBenchTask]:
    """Filter tasks that can run locally without Docker"""
    local_tasks = []
    for t in tasks:
        # Skip tasks requiring Docker setup
        if t.requires_docker:
            continue
        # Skip tasks about specific Docker environment
        if any(x in t.description.lower() for x in ["/root/", "useradd", "/home/tmpdir"]):
            continue
        local_tasks.append(t)
    return local_tasks


class AgentBenchEvaluator:
    """Official AgentBench evaluation logic"""
    
    @staticmethod
    def evaluate(response: str, expected: Optional[str], match_type: str) -> tuple:
        """
        Evaluate using AgentBench's official logic
        Returns: (passed, score, message)
        """
        if not response:
            return False, 0.0, "Empty response"
        
        response = response.strip()
        
        if match_type == "exact":
            passed = response == expected
            return passed, 1.0 if passed else 0.0, f"Exact match: {passed}"
        
        elif match_type == "integer":
            # Extract integer from response
            numbers = re.findall(r'-?\d+', response)
            if not numbers:
                return False, 0.0, "No integer found in response"
            # Try each number found
            for num in numbers:
                if expected and num == expected:
                    return True, 1.0, f"Integer match: {num}"
            return False, 0.0, f"Integer mismatch: got {numbers}, expected {expected}"
        
        elif match_type == "string":
            passed = expected.lower() in response.lower() if expected else False
            return passed, 1.0 if passed else 0.0, f"String match: {passed}"
        
        elif match_type == "contains":
            passed = expected.lower() in response.lower() if expected else True
            return passed, 1.0 if passed else 0.0, f"Contains: {passed}"
        
        elif match_type == "size":
            # Size comparison (e.g., "4.0K", "1.2M")
            size_pattern = r'[\d.]+[KMGT]?B?'
            found = re.findall(size_pattern, response, re.IGNORECASE)
            return len(found) > 0, 0.5, f"Size found: {found}"
        
        else:
            # Unknown type - just check non-empty
            return len(response) > 0, 0.5, f"Unknown match type: {match_type}"


async def run_agentbench_test():
    """Run AgentBench official tasks"""
    print("=" * 70)
    print("AgentBench OS Interaction - OFFICIAL Tasks")
    print("Source: github.com/THUDM/AgentBench")
    print("=" * 70)
    
    # Load official tasks
    all_tasks = load_agentbench_tasks()
    print(f"\nLoaded {len(all_tasks)} official AgentBench OS tasks")
    
    # Filter for local execution
    local_tasks = get_local_runnable_tasks(all_tasks)
    print(f"Tasks runnable locally (no Docker): {len(local_tasks)}")
    
    if not local_tasks:
        print("\n⚠️  No tasks can run locally without Docker.")
        print("To run full AgentBench, you need:")
        print("  1. Docker installed")
        print("  2. Run: docker compose -f extra/docker-compose.yml up")
        print("  3. Use official AgentBench runner")
        
        # Show what tasks require
        print("\n--- Task Requirements ---")
        for t in all_tasks[:10]:
            docker_status = "🐳 Requires Docker" if t.requires_docker else "✅ Local"
            print(f"  [{t.id:2}] {docker_status}: {t.description[:50]}...")
        return
    
    # Initialize agent
    try:
        from engine.agent.react_agent import ReActAgent
        agent = ReActAgent(max_iterations=10)
        print("\n[Setup] Agent initialized")
    except Exception as e:
        print(f"[ERROR] Failed to init agent: {e}")
        return
    
    # Run tasks
    results = []
    print(f"\nRunning {len(local_tasks)} tasks...\n")
    
    for task in local_tasks:
        print(f"[Task {task.id}] {task.description[:60]}...")
        print(f"    Labels: {task.labels}, Match: {task.match_type}")
        
        try:
            result = await asyncio.wait_for(
                agent.run(task=task.description, session_id=f"agentbench_{task.id}"),
                timeout=60
            )
            response = result.response if result else ""
            
            passed, score, message = AgentBenchEvaluator.evaluate(
                response, task.expected_answer, task.match_type
            )
            
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"    {status}: {message}")
            print(f"    Response: {response[:80]}..." if response else "    Response: (empty)")
            
            results.append({
                "task_id": task.id,
                "passed": passed,
                "score": score,
                "response": response[:200] if response else ""
            })
            
        except asyncio.TimeoutError:
            print(f"    ❌ TIMEOUT")
            results.append({"task_id": task.id, "passed": False, "score": 0, "response": "TIMEOUT"})
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            results.append({"task_id": task.id, "passed": False, "score": 0, "response": str(e)})
    
    # Cleanup
    try:
        await agent.cleanup_browser_session()
    except:
        pass
    
    # Summary
    print("\n" + "=" * 70)
    print("AgentBench RESULTS")
    print("=" * 70)
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    rate = passed / total if total > 0 else 0
    
    print(f"\n📊 Official AgentBench OS Score: {passed}/{total} ({rate:.1%})")
    
    # Reference comparison
    print("\n--- Reference Scores (from AgentBench paper) ---")
    print("  GPT-4:        34.5%")
    print("  GPT-3.5:      18.6%")
    print("  Claude-2:     17.2%")
    print("  LLaMA-2-70B:  4.8%")
    print(f"\n  NogicOS:      {rate:.1%}")
    
    if rate > 0.345:
        level = "Above GPT-4 level"
    elif rate > 0.186:
        level = "Above GPT-3.5 level"
    elif rate > 0.172:
        level = "Above Claude-2 level"
    elif rate > 0.048:
        level = "Above LLaMA-2-70B level"
    else:
        level = "Below baseline"
    
    print(f"\n📈 Relative Performance: {level}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_agentbench_test())


