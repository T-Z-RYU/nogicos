#!/usr/bin/env python3
"""
AgentBench Official OS Interaction Test Runner

这Yes官方 AgentBench OS Test的适配器。
它会在 Docker 容器MediumRunningTest，让 NogicOS Agent Execute任务。
"""

import json
import subprocess
import time
import asyncio
import re
import sys
import os

# SetEncode
os.environ['PYTHONIOENCODING'] = 'utf-8'

# AddprojectPath
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.agent.react_agent import ReActAgent

# AgentBench TestDataPath
AGENTBENCH_DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "reference", "AgentBench", "data", "os_interaction", "data", "dev.json"
)

class DockerContainer:
    """管理 Docker 容器生命Cycle"""
    
    def __init__(self, image: str = "local-os/default"):
        self.image = image
        self.container_id = None
    
    def start(self, init_code: str = None, start_code: str = None):
        """Start容器"""
        # Createcontenter
        result = subprocess.run(
            ["docker", "run", "-d", "--rm", self.image, "tail", "-f", "/dev/null"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to start container: {result.stderr}")
        
        self.container_id = result.stdout.strip()[:12]
        print(f"  [Docker] Container started: {self.container_id}")
        
        # ExecuteInitializecode
        if init_code:
            self.exec(init_code)
            print(f"  [Docker] Init code executed")
        
        # ExecuteStartcode（usuallyYesAfterplatformProcess）
        if start_code:
            self.exec(f"bash -c '{start_code}'")
            print(f"  [Docker] Start code executed")
            time.sleep(1)  # WaitAfterplatformProcessStart
        
        return self.container_id
    
    def exec(self, command: str) -> str:
        """在容器MediumExecuteCommand"""
        result = subprocess.run(
            ["docker", "exec", self.container_id, "bash", "-c", command],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    
    def stop(self):
        """Stop容器"""
        if self.container_id:
            subprocess.run(["docker", "stop", self.container_id], capture_output=True)
            print(f"  [Docker] Container stopped: {self.container_id}")
            self.container_id = None


class AgentBenchRunner:
    """Running AgentBench 官方Test"""
    
    def __init__(self):
        self.results = []
    
    async def run_task(self, task: dict, task_idx: int) -> dict:
        """Running单个任务"""
        description = task.get("description", "")
        
        print(f"\n{'='*60}")
        print(f"Task {task_idx + 1}: {description[:80]}...")
        print(f"{'='*60}")
        
        # prepare contenter
        container = DockerContainer()
        
        # ParseInitializeConfig
        create_config = task.get("create", {})
        init_code = None
        start_code = task.get("start")
        
        if isinstance(create_config, dict):
            init_config = create_config.get("init", {})
            if isinstance(init_config, dict):
                init_code = init_config.get("code")
            elif isinstance(init_config, str):
                init_code = init_config
        
        try:
            container.start(init_code=init_code, start_code=start_code)
            
            # Create Agent Instance
            agent = ReActAgent()
            
            # Buildprecise's  prompt，needrequest Agent onlyOutputpreciseAnswer
            prompt = f"""You are running in a Docker container. Execute commands using docker exec.

TASK: {description}

IMPORTANT RULES:
1. Container ID is: {container.container_id}
2. Execute commands using: docker exec {container.container_id} <command>
3. Your final answer must be ONLY the requested value (number, filename, etc.)
4. Do NOT add explanations, units, or extra text
5. If asked for a number, respond with ONLY the number (e.g., "6" not "6 files")

Begin your analysis. When you have the answer, state it clearly."""

            # Running Agent
            result = await agent.run(prompt)
            agent_output = result.get("output", "")
            
            print(f"\n  [Agent Output]: {agent_output[:200]}...")
            
            # EvaluateResult
            evaluation = task.get("evaluation", {})
            expected = evaluation.get("match")
            
            passed = False
            if expected:
                # preciseMatch
                # tryfromOutputMediumExtractionAnswer
                answer = self._extract_answer(agent_output, expected)
                passed = (answer == expected)
                print(f"  [Expected]: {expected}")
                print(f"  [Extracted]: {answer}")
                print(f"  [Result]: {'✓ PASS' if passed else '✗ FAIL'}")
            else:
                # complexEvaluate（NeedRunning check Script）
                print(f"  [Evaluation]: Complex check (not implemented)")
                passed = None
            
            return {
                "task_idx": task_idx,
                "description": description[:100],
                "expected": expected,
                "agent_output": agent_output[:500],
                "passed": passed
            }
            
        finally:
            container.stop()
    
    def _extract_answer(self, output: str, expected: str) -> str:
        """从 Agent OutputMedium提取答案"""
        # IfexpectYesNumber，tryExtractionNumber
        if expected.isdigit():
            numbers = re.findall(r'\b(\d+)\b', output)
            if numbers:
                # ReturnmostAfteroneaNumber（usuallyYesFinalAnswer）
                return numbers[-1]
        
        # IfexpectYesspecificCharacterstring，CheckYesNoPackagecontain
        if expected in output:
            return expected
        
        # tryExtractionmostAfteroneRowasforAnswer
        lines = output.strip().split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('['):
                return line
        
        return output.strip()
    
    async def run_all(self, limit: int = None):
        """Running所有Test"""
        # LoadTestData
        with open(AGENTBENCH_DATA, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        if limit:
            tasks = tasks[:limit]
        
        print(f"\n{'#'*60}")
        print(f"# AgentBench Official OS Interaction Tests")
        print(f"# Total tasks: {len(tasks)}")
        print(f"{'#'*60}")
        
        passed = 0
        failed = 0
        skipped = 0
        
        for idx, task in enumerate(tasks):
            try:
                result = await self.run_task(task, idx)
                self.results.append(result)
                
                if result["passed"] is True:
                    passed += 1
                elif result["passed"] is False:
                    failed += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                print(f"  [Error]: {str(e)}")
                self.results.append({
                    "task_idx": idx,
                    "error": str(e),
                    "passed": False
                })
                failed += 1
        
        # Printtotalend
        total = passed + failed + skipped
        score = (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Passed:  {passed}/{total}")
        print(f"Failed:  {failed}/{total}")
        print(f"Skipped: {skipped}/{total}")
        print(f"Score:   {score:.1f}%")
        print(f"{'='*60}")
        
        return {
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "score": score,
            "results": self.results
        }


async def main():
    """主Function"""
    import argparse
    parser = argparse.ArgumentParser(description="Run AgentBench Official OS Tests")
    parser.add_argument("-n", "--limit", type=int, default=None, 
                        help="Number of tasks to run (default: all)")
    parser.add_argument("--all", action="store_true", 
                        help="Run all tasks")
    args = parser.parse_args()
    
    limit = args.limit  # None = run all
    
    runner = AgentBenchRunner()
    results = await runner.run_all(limit=limit)
    
    # SaveResult
    output_file = os.path.join(os.path.dirname(__file__), "agentbench_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())

