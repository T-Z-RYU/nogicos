"""
独立运行 SkillWeaver 的 Worker 脚本
避免与主进程的异步上下文冲突
"""
import asyncio
import sys
import os
import time
import json
import tempfile

# 修复 Windows 控制台 UTF-8 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 添加 SkillWeaver 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SkillWeaver"))

from playwright.async_api import async_playwright

# 导入 API Keys
from api_keys import OPENAI_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 导入 SkillWeaver 组件
from skillweaver.lm import LM
from skillweaver.environment import make_browser
from skillweaver.agent import codegen_generate, codegen_do
from skillweaver.knowledge_base.knowledge_base import KnowledgeBase
from skillweaver.create_skill_library_prompt import create_skill_library_prompt


async def run_without_knowledge_base(url: str, task: str, max_steps: int = 3):
    """无知识库执行"""
    result = {
        "success": False,
        "time": 0.0,
        "steps": 0,
        "llm_calls": 0,
        "output": None,
        "error": None,
    }
    
    start_time = time.time()
    store_dir = tempfile.mkdtemp(prefix="sw_worker_")
    lm = LM("gpt-4o")
    
    async with async_playwright() as p:
        browser = None
        try:
            browser = await make_browser(
                p, url, 
                headless=True,
                navigation_timeout=30000,
                timeout=10000
            )
            
            states = []
            actions = []
            knowledge_base = KnowledgeBase()
            
            task_obj = {"type": "prod", "task": task}
            
            # 获取初始状态
            print("  正在获取页面状态...")
            initial_state = await browser.observe()
            states.append(initial_state)
            
            # 获取可见函数
            visible_functions, visible_functions_string, _ = (
                await create_skill_library_prompt(
                    task_obj,
                    knowledge_base,
                    lm,
                    as_reference_only=False,
                    enable_retrieval_module_for_exploration=False,
                )
            )
            
            for step in range(max_steps):
                print(f"  步骤 {step + 1}...")
                result["llm_calls"] += 1
                
                # 生成动作
                action = await codegen_generate(
                    lm=lm,
                    states=states,
                    actions=actions,
                    knowledge_base=knowledge_base,
                    task=task,
                    is_eval_task=True,
                    visible_functions_string=visible_functions_string,
                    disabled_function_names=[],
                    as_reference_only=False,
                )
                
                print(f"    推理: {action.get('step_by_step_reasoning', '')[:100]}...")
                
                if action.get("terminate_with_result"):
                    result["output"] = action["terminate_with_result"]
                    result["success"] = True
                    print(f"    终止结果: {result['output'][:100]}")
                    break
                
                if action.get("python_code"):
                    print(f"    生成代码: {action['python_code'][:100]}...")
                    
                    exec_result = await codegen_do(
                        browser=browser,
                        knowledge_base=knowledge_base,
                        code=action["python_code"],
                        filename=os.path.join(store_dir, f"step_{step}.py"),
                        disabled_function_names=[],
                        allow_recovery=False,
                    )
                    
                    actions.append(action)
                    result["steps"] += 1
                    
                    if exec_result.get("output"):
                        result["output"] = str(exec_result["output"])
                    
                    if exec_result.get("exception"):
                        result["error"] = str(exec_result["exception"])
                        print(f"    执行错误: {result['error'][:100]}")
                    
                    # 获取新状态
                    new_state = await browser.observe()
                    states.append(new_state)
                else:
                    break
            
            result["success"] = result["output"] is not None or result["steps"] > 0
            
        except Exception as e:
            result["error"] = str(e)
            import traceback
            traceback.print_exc()
        finally:
            if browser:
                try:
                    await browser.close()
                except:
                    pass
    
    result["time"] = time.time() - start_time
    return result


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--max-steps", type=int, default=3)
    args = parser.parse_args()
    
    print(f"URL: {args.url}")
    print(f"任务: {args.task}")
    print(f"最大步骤: {args.max_steps}")
    print()
    
    result = await run_without_knowledge_base(args.url, args.task, args.max_steps)
    
    print()
    print("=" * 50)
    print("结果:")
    print(f"  成功: {result['success']}")
    print(f"  时间: {result['time']:.2f}s")
    print(f"  步骤: {result['steps']}")
    print(f"  LLM调用: {result['llm_calls']}")
    if result['output']:
        print(f"  输出: {result['output'][:200]}")
    if result['error']:
        print(f"  错误: {result['error'][:200]}")
    
    # 输出 JSON 结果供主进程读取
    print()
    print("JSON_RESULT_START")
    print(json.dumps(result, ensure_ascii=False))
    print("JSON_RESULT_END")


if __name__ == "__main__":
    asyncio.run(main())
