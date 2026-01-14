# -*- coding: utf-8 -*-
"""
Cursor vs NogicOS 对比Test

Test维度：
1. Response速度 (Time to First Token)
2. 任务理解准确性
3. Tool调用合理性
4. 回复质量
"""

import asyncio
import httpx
import time
import json
import sys
import os

# ensureUTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Testuse case
TEST_CASES = [
    {
        "id": "simple_chat",
        "category": "简单对话",
        "prompt": "你好，介绍一Down你自己",
        "expected_behavior": "简短自我介绍，不需要调用Tool"
    },
    {
        "id": "file_list",
        "category": "File操作",
        "prompt": "Column出当BeforeDirectory有什么File",
        "expected_behavior": "调用 list_directory Tool，ReturnFileList"
    },
    {
        "id": "file_read",
        "category": "FileRead",
        "prompt": "Read README.md 的Inner容",
        "expected_behavior": "调用 read_file Tool，ReturnFileInner容"
    },
    {
        "id": "web_search",
        "category": "NetworkSearch",
        "prompt": "Search一Down Claude 3.5 的最NewMessage",
        "expected_behavior": "调用SearchTool，Return相OffInfo"
    },
    {
        "id": "multi_step",
        "category": "多步骤任务",
        "prompt": "帮我看看桌面有什么File，然After告诉我Max的那个FileYes什么",
        "expected_behavior": "先Column出Directory，AnalyzeFileSize，给出答案"
    },
    {
        "id": "ambiguous",
        "category": "模糊意Graph",
        "prompt": "帮我整理一Down",
        "expected_behavior": "应该询问具体整理什么，或者做出合理False设"
    },
    {
        "id": "code_task",
        "category": "代码任务",
        "prompt": "帮我Write一个 Python Function，计算斐波那契数Column",
        "expected_behavior": "直接给出代码，不需要过多解释"
    }
]


async def test_nogicos(prompt: str) -> dict:
    """Test NogicOS Response"""
    url = "http://localhost:8080/api/chat"
    
    start_time = time.time()
    first_token_time = None
    full_response = ""
    tool_calls = []
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                url,
                json={"text": prompt},
                headers={"Accept": "text/event-stream"}
            ) as response:
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    # RecordFirst token Time
                    if first_token_time is None and line:
                        first_token_time = time.time() - start_time
                    
                    # Parse SSE Data
                    if line.startswith("0:"):  # textInnercontent
                        try:
                            text = json.loads(line[2:])
                            full_response += text
                        except:
                            pass
                    elif line.startswith("9:"):  # ToolCall
                        try:
                            tool_data = json.loads(line[2:])
                            tool_calls.append(tool_data)
                        except:
                            pass
        
        total_time = time.time() - start_time
        
        return {
            "success": True,
            "ttft": first_token_time,
            "total_time": total_time,
            "response": full_response[:500],  # Truncate
            "tool_calls": tool_calls,
            "response_length": len(full_response)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ttft": None,
            "total_time": time.time() - start_time
        }


def print_result(test_case: dict, result: dict):
    """打印TestResult"""
    print(f"\n{'='*60}")
    print(f"Test: {test_case['category']} - {test_case['id']}")
    print(f"Prompt: {test_case['prompt']}")
    print(f"期望Row为: {test_case['expected_behavior']}")
    print(f"-"*60)
    
    if result["success"]:
        print(f"TTFT: {result['ttft']:.2f}s" if result['ttft'] else "TTFT: N/A")
        print(f"总耗时: {result['total_time']:.2f}s")
        print(f"ResponseLength: {result['response_length']} Character")
        
        if result.get("tool_calls"):
            print(f"Tool调用: {len(result['tool_calls'])} 次")
            for tc in result["tool_calls"][:3]:  # onlyDisplayBefore3a
                print(f"  - {tc.get('toolName', 'unknown')}")
        
        print(f"\nResponse预览:")
        print(f"{result['response'][:300]}...")
    else:
        print(f"Failed: {result.get('error', 'Unknown error')}")


async def run_comparison():
    """Running对比Test"""
    print("=" * 60)
    print("NogicOS 功能Test")
    print("=" * 60)
    
    # firstCheckServiceYesNoAvailable
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("http://localhost:8080/health")
            if resp.status_code != 200:
                print("NogicOS Service未Start或不Healthy")
                return
    except:
        print("无法Connect NogicOS Service (localhost:8080)")
        print("请先Start: python hive_server.py")
        return
    
    print("NogicOS Service已Connect\n")
    
    results = []
    
    for test_case in TEST_CASES:
        print(f"\n正在Test: {test_case['id']}...")
        result = await test_nogicos(test_case["prompt"])
        results.append({
            "test_case": test_case,
            "result": result
        })
        print_result(test_case, result)
    
    # collecttotal
    print("\n" + "=" * 60)
    print("Test汇总")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r["result"]["success"])
    ttft_sum = sum(r["result"]["ttft"] for r in results if r["result"].get("ttft"))
    ttft_count = sum(1 for r in results if r["result"].get("ttft"))
    time_sum = sum(r["result"]["total_time"] for r in results if r["result"]["success"])

    avg_ttft = ttft_sum / ttft_count if ttft_count > 0 else 0
    avg_time = time_sum / success_count if success_count > 0 else 0
    
    print(f"Success率: {success_count}/{len(TEST_CASES)}")
    print(f"Average TTFT: {avg_ttft:.2f}s")
    print(f"Average总耗时: {avg_time:.2f}s")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_comparison())


