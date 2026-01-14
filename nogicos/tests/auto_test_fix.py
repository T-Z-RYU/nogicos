# -*- coding: utf-8 -*-
"""
NogicOS Auto Test & Fix Loop
Auto生成Random任务 -> Test -> 检测问题 -> 尝试Repair -> Loop

Usage:
    python -m tests.auto_test_fix --rounds 10
    python -m tests.auto_test_fix --continuous
"""

import sys
import os
import asyncio
import argparse
import json
import random
import traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Task generation templates
TASK_TEMPLATES = [
    # File operations
    "Read {file}",
    "view {dir} Directory有什么",
    "SearchPackage含 {keyword} 的File",
    "Create一个File叫 {filename}",
    "Statistics {ext} File有多少个",
    
    # Project tasks  
    "这个项目的结构Yes什么",
    "Analyze {file} 的Inner容",
    "总结一Down README",
    "找到所有的 TODO 注释",
    
    # Shell commands
    "Running {cmd}",
    "view python 版本",
    "git status",
    
    # Natural language
    "帮我看看 {target}",
    "{target} 好乱，整理一Down",
    "你好",
    "1+1等于几",
    
    # Memory
    "记住我喜欢用 {tool}",
    "我之Before说过什么",
    
    # Edge cases
    "",  # Empty
    "   ",  # Whitespace
    "asdfghjkl",  # Gibberish
]

# Fill-in values
FILL_VALUES = {
    "file": ["requirements.txt", "README.md", "config.py", "package.json", "不存在.txt"],
    "dir": [".", "engine", "tests", "桌面", "/fake/path"],
    "keyword": ["import", "def", "class", "TODO", "error", "不存在的词"],
    "filename": ["test.txt", "Test.md", "temp.py"],
    "ext": [".py", ".js", ".md", ".xyz"],
    "cmd": ["echo hello", "python --version", "dir", "whoami"],
    "target": ["桌面", "这个项目", "代码", "Log"],
    "tool": ["vim", "pnpm", "vscode", "dark mode"],
}


class AutoTestFix:
    """Automatic test and fix loop"""
    
    def __init__(self, output_dir: str = "tests/auto_test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.agent = None
        self.llm_client = None
        self.issues_found = []
        self.fixes_applied = []
        
    def generate_random_task(self) -> str:
        """Generate a random task using templates"""
        template = random.choice(TASK_TEMPLATES)
        
        # Fill in placeholders
        for key, values in FILL_VALUES.items():
            placeholder = "{" + key + "}"
            if placeholder in template:
                template = template.replace(placeholder, random.choice(values))
        
        return template
    
    async def init_agent(self):
        """Initialize agent"""
        if self.agent is None:
            from engine.agent.react_agent import ReActAgent
            self.agent = ReActAgent()
        return self.agent
    
    def init_llm(self):
        """Initialize LLM client for analysis"""
        if self.llm_client is None:
            try:
                import anthropic
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    # Try to load from api_keys.py
                    try:
                        import api_keys
                        api_keys.setup_env()
                        api_key = os.environ.get("ANTHROPIC_API_KEY")
                    except:
                        pass
                
                if api_key:
                    self.llm_client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                pass
        return self.llm_client
    
    async def run_task(self, task: str, timeout: int = 30) -> dict:
        """Run a single task and capture results"""
        agent = await self.init_agent()
        
        result = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "response": None,
            "error": None,
            "issues": [],
        }
        
        try:
            agent_result = await asyncio.wait_for(
                agent.run(task=task if task.strip() else "(empty input)", session_id="autotest"),
                timeout=timeout
            )
            
            result["success"] = agent_result.success
            result["response"] = agent_result.response
            
            # Detect issues
            result["issues"] = self.detect_issues(task, agent_result)
            
        except asyncio.TimeoutError:
            result["error"] = "TIMEOUT"
            result["issues"].append({
                "type": "timeout",
                "severity": "high",
                "message": f"Task timed out after {timeout}s"
            })
        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            result["issues"].append({
                "type": "crash",
                "severity": "critical", 
                "message": str(e)[:500]
            })
        
        return result
    
    def detect_issues(self, task: str, agent_result) -> list:
        """Detect issues in agent response"""
        issues = []
        response = agent_result.response or ""
        
        # Traceback leaked
        if "Traceback (most recent call last)" in response:
            issues.append({
                "type": "traceback_leaked",
                "severity": "high",
                "message": "Python traceback in user response"
            })
        
        # Empty response for non-trivial task
        if not response.strip() and task.strip():
            issues.append({
                "type": "empty_response",
                "severity": "medium",
                "message": "Empty response for non-empty task"
            })
        
        # Encoding issues
        if "\\x" in response or "锟斤拷" in response or "烫烫烫" in response:
            issues.append({
                "type": "encoding_error",
                "severity": "medium",
                "message": "Encoding corruption in response"
            })
        
        # Unhandled error patterns
        error_patterns = [
            ("KeyError:", "key_error"),
            ("AttributeError:", "attribute_error"),
            ("TypeError:", "type_error"),
            ("IndexError:", "index_error"),
            ("FileNotFoundError:", "file_not_found"),
        ]
        for pattern, issue_type in error_patterns:
            if pattern in response and "sorry" not in response.lower():
                issues.append({
                    "type": issue_type,
                    "severity": "medium",
                    "message": f"Unhandled {pattern} in response"
                })
        
        # Tool call malformed
        if ("<tool_call>" in response or "<function_calls>" in response):
            if response.count("<") != response.count(">"):
                issues.append({
                    "type": "malformed_xml",
                    "severity": "high",
                    "message": "Malformed XML in tool calls"
                })
        
        return issues
    
    async def analyze_and_fix(self, issue: dict, context: dict) -> dict:
        """Use LLM to analyze issue and suggest fix"""
        client = self.init_llm()
        if not client:
            return {"analysis": "LLM not available", "fix": None}
        
        prompt = f"""你Yes NogicOS 的On发者。Analyze以Down问题并建议Repair方案。

## Issue
Class型: {issue['type']}
严重程度: {issue['severity']}
描述: {issue['message']}

## UpDowntext
任务: {context.get('task', 'N/A')}
Error: {context.get('error', 'N/A')}
Traceback: {context.get('traceback', 'N/A')[:1000]}

## needrequest
1. Analyze问题Root本原因
2. 如果能Repair，提供具体的代码Modify（FilePath + ModifyInner容）
3. 如果无法AutoRepair，说明需要人工介入的原因

以 JSON 格式Return:
{{"analysis": "问题Analyze", "can_auto_fix": true/false, "fix": {{"file": "path", "old": "old code", "new": "new code"}} 或 null}}
"""
        
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            text = response.content[0].text
            
            # Try to extract JSON
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end]
            
            return json.loads(text)
            
        except Exception as e:
            return {"analysis": f"Analysis failed: {e}", "fix": None}
    
    def apply_fix(self, fix: dict) -> bool:
        """Apply a code fix"""
        if not fix or "file" not in fix:
            return False
        
        try:
            file_path = Path(fix["file"])
            if not file_path.exists():
                print(f"  [!] File not found: {file_path}")
                return False
            
            content = file_path.read_text(encoding="utf-8")
            
            if fix.get("old") and fix.get("new"):
                if fix["old"] in content:
                    new_content = content.replace(fix["old"], fix["new"], 1)
                    
                    # Backup
                    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                    backup_path.write_text(content, encoding="utf-8")
                    
                    # Apply
                    file_path.write_text(new_content, encoding="utf-8")
                    
                    print(f"  [OK] Applied fix to {file_path}")
                    self.fixes_applied.append({
                        "file": str(file_path),
                        "backup": str(backup_path),
                        "timestamp": datetime.now().isoformat()
                    })
                    return True
                else:
                    print(f"  [!] Old code not found in {file_path}")
            
            return False
            
        except Exception as e:
            print(f"  [!] Fix failed: {e}")
            return False
    
    async def run_loop(self, rounds: int = 10, auto_fix: bool = True):
        """Run the test-fix loop"""
        print("="*60)
        print("NogicOS Auto Test & Fix Loop")
        print("="*60)
        print(f"Rounds: {rounds}")
        print(f"Auto-fix: {auto_fix}")
        print()
        
        results = []
        
        for i in range(rounds):
            # Generate random task
            task = self.generate_random_task()
            print(f"\n[Round {i+1}/{rounds}]")
            print(f"Task: {task[:60]}{'...' if len(task) > 60 else ''}")
            
            # Run task
            result = await self.run_task(task)
            results.append(result)
            
            # Report
            if result["success"] and not result["issues"]:
                print("  [PASS]")
            else:
                status = "FAIL" if result["issues"] else ("ERROR" if result["error"] else "?")
                print(f"  [X] {status}")
                
                if result["error"]:
                    print(f"    Error: {result['error'][:100]}")
                
                for issue in result["issues"]:
                    print(f"    [{issue['severity']}] {issue['type']}: {issue['message'][:80]}")
                    self.issues_found.append(issue)
                    
                    # Try to auto-fix
                    if auto_fix and issue["severity"] in ["high", "critical"]:
                        print("    Analyzing for auto-fix...")
                        fix_result = await self.analyze_and_fix(issue, result)
                        
                        if fix_result.get("can_auto_fix") and fix_result.get("fix"):
                            print(f"    Analysis: {fix_result['analysis'][:100]}")
                            if self.apply_fix(fix_result["fix"]):
                                print("    Fix applied! Will verify in next round.")
                        else:
                            print(f"    Cannot auto-fix: {fix_result.get('analysis', 'Unknown')[:100]}")
        
        # Summary
        self._print_summary(results)
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _print_summary(self, results: list):
        """Print summary"""
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        total = len(results)
        passed = sum(1 for r in results if r["success"] and not r["issues"])
        failed = total - passed
        
        print(f"Total rounds: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Pass rate: {passed/total*100:.1f}%")
        print(f"Issues found: {len(self.issues_found)}")
        print(f"Fixes applied: {len(self.fixes_applied)}")
        
        if self.issues_found:
            print("\nIssue types:")
            types = {}
            for issue in self.issues_found:
                t = issue["type"]
                types[t] = types.get(t, 0) + 1
            for t, count in sorted(types.items(), key=lambda x: -x[1]):
                print(f"  {t}: {count}")
    
    def _save_results(self, results: list):
        """Save results to file"""
        output_file = self.output_dir / f"autotest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_rounds": len(results),
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "results": results,
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\nResults saved to: {output_file}")


async def main():
    parser = argparse.ArgumentParser(description="NogicOS Auto Test & Fix")
    parser.add_argument("--rounds", type=int, default=5, help="Number of test rounds")
    parser.add_argument("--no-fix", action="store_true", help="Disable auto-fix")
    parser.add_argument("--timeout", type=int, default=30, help="Task timeout in seconds")
    args = parser.parse_args()
    
    tester = AutoTestFix()
    await tester.run_loop(rounds=args.rounds, auto_fix=not args.no_fix)


if __name__ == "__main__":
    asyncio.run(main())

