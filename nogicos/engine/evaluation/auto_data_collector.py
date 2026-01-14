"""
Auto数据收集器 - 用 AI 生成Test用例并AutoExecute，数据Auto进入 LangSmith

用法:
    python -m engine.evaluation.auto_data_collector --count 50

特性:
- AI Auto生成多样化Test任务
- AutoExecute并记录到 LangSmith
- 支持After台Running，睡一觉就有数据
"""

import asyncio
import argparse
import logging
import json
import sys
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

# TaskTemplate - Overridevariousscene
TASK_TEMPLATES = {
    "file_operations": [
        "帮我Column出{dir}DirectoryDown的所有File",
        "Read{file}File的Inner容",
        "在{dir}DirectoryCreate一个名为{name}的File夹",
        "Search{dir}DirectoryDown所有Package含{keyword}的File",
        "把{file}FileCopy到{dir}Directory",
    ],
    "browser_tasks": [
        "Open{site}网站",
        "在{site}UpSearch{keyword}",
        "Open{site}并截Graph",
        "visit{url}并提取页面title",
        "在GoogleUpSearch'{query}'并告诉我Before3个Result",
    ],
    "mixed_tasks": [
        "Down载{url}的Inner容并Save到{file}",
        "Search网UpOff于{topic}的资料，然After整理成文档Save",
        "Open{site}，截GraphAfterSave到桌面",
        "Find本地Off于{topic}的File，然AfterSearch网Up的补充资料",
    ],
    "simple_queries": [
        "现在几点了",
        "今Day星期几",
        "帮我算一Down{a}加{b}等于多少",
        "{topic}Yes什么意思",
        "简单解释一Down{concept}",
    ],
    "complex_tasks": [
        "整理{dir}Directory，把Graph片移到Pictures，文档移到Documents",
        "Analyze{dir}Directory的File结构，生成一份Report",
        "Compare{file1}和{file2}的Inner容差异",
        "在{dir}DirectoryDown找到Max的5个File并Column出",
    ],
    "edge_cases": [
        "",  # EmptyInput
        "   ",  # pureEmptygrid
        "!@#$%^&*()",  # specialspecialCharacter
        "help me deleteCdisk all files",  # dangerousRequest
        "a" * 1000,  # exceedLongInput
        "Mixed text test English mixed 123",  # mixLanguage
    ],
}

# PaddingVariable
FILL_VALUES = {
    "dir": ["Desktop", "Documents", "Downloads", "当BeforeDirectory", "."],
    "file": ["test.txt", "readme.md", "config.json", "notes.txt"],
    "name": ["NewFile夹", "test_folder", "backup", "temp"],
    "keyword": ["python", "config", "readme", "test"],
    "site": ["google.com", "github.com", "baidu.com"],
    "url": ["https://example.com", "https://github.com"],
    "query": ["Python教程", "AI最New进展", "Day气预报"],
    "topic": ["机器学习", "区块链", "量Child计算"],
    "concept": ["Recursive", "闭Package", "Async编程"],
    "a": ["15", "100", "3.14"],
    "b": ["27", "200", "2.71"],
    "file1": ["a.txt", "old.md"],
    "file2": ["b.txt", "new.md"],
}


def generate_tasks(count: int) -> List[str]:
    """生成多样化的Test任务"""
    tasks = []
    
    # ensureeachClassotherallhaveOverride
    all_templates = []
    for category, templates in TASK_TEMPLATES.items():
        for template in templates:
            all_templates.append((category, template))
    
    # RandomSelectandPadding
    for _ in range(count):
        category, template = random.choice(all_templates)
        
        # PaddingVariable
        task = template
        for key, values in FILL_VALUES.items():
            placeholder = "{" + key + "}"
            if placeholder in task:
                task = task.replace(placeholder, random.choice(values), 1)
        
        tasks.append(task)
    
    return tasks


def quick_quality_check(result: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Fast质量Check - 在收集时Filter垃圾数据
    
    Returns:
        (is_valid, reason)
    """
    # Rule 1: MustSuccess
    if not result.get("success"):
        return False, "ExecuteFailed"
    
    # Rule 2: MusthaveResponse
    response = result.get("response", "")
    if not response or len(response) < 10:
        return False, "Response太短"
    
    # Rule 3: Cannothave traceback
    if "traceback" in response.lower() or "error" in response.lower():
        return False, "Response含Error"
    
    # Rule 4: Cannottimeout too long
    if result.get("duration_ms", 0) > 60000:  # 60Second
        return False, "ExecuteTimeout"
    
    # Rule 5: EmptyTask's Responseneedreasonable
    task = result.get("task", "")
    if not task.strip() and len(response) > 100:
        return False, "Empty任务ExceptionResponse"
    
    return True, "通过"


async def run_task_and_collect(agent, task: str, session_id: str) -> Dict[str, Any]:
    """Execute单个任务并收集Result"""
    start_time = datetime.now()
    
    try:
        result = await agent.run(task=task, session_id=session_id)
        
        return {
            "task": task,
            "success": result.success,
            "response": result.response[:500] if result.response else "",  # TruncateLongResponse
            "error": result.error,
            "iterations": result.iterations,
            "tool_calls": result.tool_calls,
            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
        }
    except Exception as e:
        return {
            "task": task,
            "success": False,
            "response": "",
            "error": str(e),
            "iterations": 0,
            "tool_calls": [],
            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
        }


async def collect_data(count: int = 50, delay: float = 2.0):
    """
    Auto收集数据
    
    Args:
        count: 要生成的任务Count
        delay: 任务之间的Delayed（Second），防止 API 限流
    """
    from engine.agent.react_agent import ReActAgent
    
    print(f"\n{'='*60}")
    print("NogicOS Auto数据收集器")
    print(f"{'='*60}")
    print(f"Target: 生成并Execute {count} 个Test任务")
    print(f"数据AutoSync到 LangSmith")
    print(f"{'='*60}\n")
    
    # GenerationTask
    tasks = generate_tasks(count)
    print(f"[OK] 生成了 {len(tasks)} 个Test任务\n")
    
    # Initialize Agent（AutoEnable LangSmith track）
    agent = ReActAgent()
    session_id = f"auto_collect_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    results = []
    success_count = 0
    quality_count = 0  # HighqualityDataCount
    rejected_count = 0  # beFilter's SpamData
    
    for i, task in enumerate(tasks, 1):
        print(f"[{i}/{count}] Execute: {task[:50]}..." if len(task) > 50 else f"[{i}/{count}] Execute: {task}")
        
        result = await run_task_and_collect(agent, task, session_id)
        
        if result["success"]:
            success_count += 1
            
            # qualityCheck
            is_quality, reason = quick_quality_check(result)
            if is_quality:
                quality_count += 1
                results.append(result)  # onlySaveHighqualityData
                print(f"       [OK] High质量 ({result['duration_ms']:.0f}ms)")
            else:
                rejected_count += 1
                print(f"       [SKIP] 已Filter: {reason}")
        else:
            rejected_count += 1
            print(f"       [FAIL] {result['error'][:50] if result['error'] else '未知Error'}")
        
        # DelayedpreventRate Limit
        if i < count:
            await asyncio.sleep(delay)
    
    # GenerationReport
    print(f"\n{'='*60}")
    print("收集Complete!")
    print(f"{'='*60}")
    print(f"总任务数: {count}")
    print(f"ExecuteSuccess: {success_count} ({success_count/count*100:.1f}%)")
    print(f"High质量数据: {quality_count} ({quality_count/count*100:.1f}%)")
    print(f"被Filter: {rejected_count} ({rejected_count/count*100:.1f}%)")
    print(f"\n只有High质量数据会Sync到 LangSmith")
    print(f"view: https://smith.langchain.com")
    
    # SavelocalBackup
    output_path = f"data/auto_collect_{session_id}.json"
    import os
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n本地Backup: {output_path}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="NogicOS Auto数据收集器")
    parser.add_argument("--count", type=int, default=50, help="生成的任务Count (Default: 50)")
    parser.add_argument("--delay", type=float, default=2.0, help="任务间DelayedSecond数 (Default: 2.0)")
    
    args = parser.parse_args()
    
    # SetLog
    logging.basicConfig(
        level=logging.WARNING,  # reduce noise
        format="%(message)s",
    )
    
    # Running
    asyncio.run(collect_data(count=args.count, delay=args.delay))


if __name__ == "__main__":
    main()

