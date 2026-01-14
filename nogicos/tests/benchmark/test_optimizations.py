# -*- coding: utf-8 -*-
"""
Quick Test for Agent Optimizations

Tests the new Reflection, Loop Detection, and Verification mechanisms
without running the full AgentBench suite.

Usage:
    python -m tests.benchmark.test_optimizations
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from engine.agent.react_agent import ReActAgent, ReflectionResult


class OptimizationTester:
    """Tests the new optimization mechanisms"""
    
    def __init__(self):
        self.agent = None
        self.passed = 0
        self.failed = 0
    
    def test_should_reflect(self):
        """Test _should_reflect() method"""
        print("\n=== Testing _should_reflect() ===")
        
        # Create a minimal agent for testing
        agent = ReActAgent.__new__(ReActAgent)
        agent.max_iterations = 20
        
        # Bind the method
        from types import MethodType
        agent._should_reflect = MethodType(ReActAgent._should_reflect, agent)
        
        test_cases = [
            # (text_content, task, expected_result)
            ("42", "How many files are in /etc?", True),
            ("220", "Count the number of lines", True),
            ("ok", "Delete the file", False),
            ("done", "Move files to folder", False),
            ("The answer is 5", "What is 2+3?", True),
            ("", "Any task", False),
            ("Successfully moved", "Move file.txt to backup/", False),
            ("3", "Statistics .txt FileCount", True),
        ]
        
        for text, task, expected in test_cases:
            result = agent._should_reflect(text, task)
            status = "PASS" if result == expected else "FAIL"
            if result == expected:
                self.passed += 1
            else:
                self.failed += 1
            print(f"  [{status}] _should_reflect('{text[:20]}...', '{task[:30]}...') = {result} (expected {expected})")
    
    def test_detect_loop(self):
        """Test _detect_loop() method"""
        print("\n=== Testing _detect_loop() ===")
        
        agent = ReActAgent.__new__(ReActAgent)
        from types import MethodType
        agent._detect_loop = MethodType(ReActAgent._detect_loop, agent)
        
        test_cases = [
            # (tool_calls, expected_result)
            ([], False),
            ([{"name": "ls", "args": {"path": "/"}}], False),
            ([
                {"name": "ls", "args": {"path": "/"}},
                {"name": "ls", "args": {"path": "/"}},
            ], False),  # Only 2 calls, need 3
            ([
                {"name": "ls", "args": {"path": "/"}},
                {"name": "ls", "args": {"path": "/"}},
                {"name": "ls", "args": {"path": "/"}},
            ], True),  # 3 identical calls
            ([
                {"name": "ls", "args": {"path": "/home"}},
                {"name": "ls", "args": {"path": "/"}},
                {"name": "ls", "args": {"path": "/"}},
            ], False),  # Different args in first call
            ([
                {"name": "cat", "args": {"path": "/etc/passwd"}},
                {"name": "ls", "args": {"path": "/"}},
                {"name": "ls", "args": {"path": "/"}},
                {"name": "ls", "args": {"path": "/"}},
            ], True),  # Last 3 are identical
        ]
        
        for calls, expected in test_cases:
            result = agent._detect_loop(calls)
            status = "PASS" if result == expected else "FAIL"
            if result == expected:
                self.passed += 1
            else:
                self.failed += 1
            desc = f"{len(calls)} calls"
            print(f"  [{status}] _detect_loop({desc}) = {result} (expected {expected})")
    
    async def test_reflect_before_submit(self):
        """Test _reflect_before_submit() method"""
        print("\n=== Testing _reflect_before_submit() ===")
        
        agent = ReActAgent.__new__(ReActAgent)
        from types import MethodType
        agent._reflect_before_submit = MethodType(ReActAgent._reflect_before_submit, agent)
        
        test_cases = [
            # (task, answer, tool_calls, expected_needs_revision)
            (
                "How many files are in /etc?",
                "220",
                [{"success": True, "output": "220"}],
                False  # Answer matches output
            ),
            (
                "How many files are in /etc?",
                "There are 220 files",
                [{"success": True, "output": "220"}],
                True  # Not clean numeric format
            ),
            (
                "Count the lines",
                "The total is five",
                [{"success": True, "output": "5"}],
                True  # No number in answer
            ),
            (
                "Count files",
                "42",
                [{"success": True, "output": "100"}],
                True  # Answer not in output
            ),
        ]
        
        for task, answer, tool_calls, expected in test_cases:
            result = await agent._reflect_before_submit(task, answer, tool_calls)
            status = "PASS" if result.needs_revision == expected else "FAIL"
            if result.needs_revision == expected:
                self.passed += 1
            else:
                self.failed += 1
            print(f"  [{status}] reflect('{task[:25]}...', '{answer[:15]}...') needs_revision={result.needs_revision} (expected {expected})")
            if result.issues:
                print(f"      Issues: {result.issues}")
    
    def test_verification_module(self):
        """Test the verification module"""
        print("\n=== Testing AnswerVerifier ===")
        
        try:
            from engine.agent.verification import AnswerVerifier, verify_answer
            verifier = AnswerVerifier()
            
            test_cases = [
                # (answer, task, tool_outputs, expected_valid)
                ("42", "How many files?", ["Found 42 files"], True),
                ("not a number", "How many files?", None, False),
                ("/etc/passwd", "Which file contains users?", None, True),
                ("", "Count something", None, False),
                ("yes", "Does file exist?", None, True),
            ]
            
            for answer, task, outputs, expected in test_cases:
                result = verifier.verify(answer, task, outputs)
                is_valid = result.is_valid
                status = "PASS" if is_valid == expected else "FAIL"
                if is_valid == expected:
                    self.passed += 1
                else:
                    self.failed += 1
                print(f"  [{status}] verify('{answer}', '{task[:20]}...') = {result.status.value} (expected {'valid' if expected else 'invalid'})")
                
        except ImportError as e:
            print(f"  ⚠ Skipped: verification module not available ({e})")
    
    async def run_all_tests(self):
        """Run all optimization tests"""
        print("=" * 60)
        print("NogicOS Agent Optimization Tests")
        print("=" * 60)
        
        self.test_should_reflect()
        self.test_detect_loop()
        await self.test_reflect_before_submit()
        self.test_verification_module()
        
        print("\n" + "=" * 60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        
        return self.failed == 0


async def main():
    tester = OptimizationTester()
    success = await tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

