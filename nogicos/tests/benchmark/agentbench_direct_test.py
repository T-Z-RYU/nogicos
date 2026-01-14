#!/usr/bin/env python3
"""
AgentBench 直接Test - 不通过 Agent，直接VerifyTestFramework
这样可以FastVerify Docker Environment和Evaluate逻辑YesNo正确
"""

import json
import subprocess
import time
import os
import re

# AgentBench TestDataPath
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTBENCH_DATA = os.path.join(
    os.path.dirname(os.path.dirname(SCRIPT_DIR)),
    "nogicos", "reference", "AgentBench", "data", "os_interaction", "data", "dev.json"
)

# IfPathnotto，tryanotherPath
if not os.path.exists(AGENTBENCH_DATA):
    AGENTBENCH_DATA = os.path.join(
        SCRIPT_DIR, "..", "..", "reference", "AgentBench", 
        "data", "os_interaction", "data", "dev.json"
    )


def docker_run(command: str, container_id: str) -> str:
    """在 Docker 容器MediumExecuteCommand"""
    result = subprocess.run(
        ["docker", "exec", container_id, "bash", "-c", command],
        capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def start_container(image: str = "local-os/default", init_code: str = None, start_code: str = None) -> str:
    """Start Docker 容器"""
    result = subprocess.run(
        ["docker", "run", "-d", "--rm", image, "tail", "-f", "/dev/null"],
        capture_output=True, text=True
    )
    container_id = result.stdout.strip()[:12]
    
    if init_code:
        docker_run(init_code, container_id)
    
    if start_code:
        docker_run(f"bash -c '{start_code}'", container_id)
        time.sleep(1)
    
    return container_id


def stop_container(container_id: str):
    """Stop容器"""
    subprocess.run(["docker", "stop", container_id], capture_output=True)


def run_test(task: dict, idx: int) -> dict:
    """Running单个Test，Usage官方的 example Command"""
    description = task.get("description", "")
    print(f"\n[Task {idx + 1}] {description[:70]}...")
    
    # ParseConfig
    create_config = task.get("create", {})
    init_code = None
    start_code = task.get("start")
    
    if isinstance(create_config, dict):
        init_config = create_config.get("init", {})
        if isinstance(init_config, dict):
            init_code = init_config.get("code")
        elif isinstance(init_config, str):
            init_code = init_config
    
    # Getexpect's Evaluate
    evaluation = task.get("evaluation", {})
    expected = evaluation.get("match")
    example = evaluation.get("example")
    
    if not expected and not example:
        print("  [SKIP] No match or example evaluation")
        return {"passed": None, "reason": "no evaluation"}
    
    try:
        container_id = start_container(init_code=init_code, start_code=start_code)
        print(f"  Container: {container_id}")
        
        # Ifhave example，ExecuteitGetcorrectAnswer
        if example:
            if isinstance(example, dict):
                example_cmd = example.get("code", "")
            else:
                example_cmd = example
            
            if example_cmd:
                actual = docker_run(example_cmd, container_id)
                print(f"  Example cmd: {example_cmd[:50]}...")
                print(f"  Actual result: {actual}")
                
                if expected:
                    passed = (actual.strip() == expected.strip())
                    print(f"  Expected: {expected}")
                    print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
                    return {"passed": passed, "actual": actual, "expected": expected}
                else:
                    print(f"  [INFO] Example executed, no exact match check")
                    return {"passed": True, "actual": actual, "reason": "example executed"}
        
        # Ifonlyhave expected match，Need Agent fromExecute
        if expected:
            print(f"  [NEED AGENT] Expected: {expected}")
            return {"passed": None, "expected": expected, "reason": "needs agent"}
        
        return {"passed": None, "reason": "unknown"}
        
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return {"passed": False, "error": str(e)}
    finally:
        try:
            stop_container(container_id)
        except:
            pass


def main():
    """主Function"""
    print("=" * 60)
    print("AgentBench Direct Test (VerifyTestFramework)")
    print("=" * 60)
    
    # CheckDataFile
    if not os.path.exists(AGENTBENCH_DATA):
        print(f"ERROR: Data file not found: {AGENTBENCH_DATA}")
        return
    
    with open(AGENTBENCH_DATA, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    
    print(f"Loaded {len(tasks)} tasks")
    
    # Testthe 7-15 a（thesehave example Command）
    results = []
    for idx, task in enumerate(tasks[6:15]):
        result = run_test(task, idx)
        results.append(result)
    
    # Statistics
    passed = sum(1 for r in results if r.get("passed") is True)
    failed = sum(1 for r in results if r.get("passed") is False)
    skipped = sum(1 for r in results if r.get("passed") is None)
    
    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)


if __name__ == "__main__":
    main()

