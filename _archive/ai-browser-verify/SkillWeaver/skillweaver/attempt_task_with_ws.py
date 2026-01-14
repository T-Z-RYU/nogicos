# -*- coding: utf-8 -*-
"""
SkillFlow taskexecute
 WebSocket statusbroadcast
"""
import ast
import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Optional

import nest_asyncio
from aioconsole import aprint
from playwright.async_api import async_playwright

from skillweaver.agent import codegen_do, codegen_generate, codegen_trajectory_to_string
from skillweaver.create_skill_library_prompt import (
    create_skill_library_prompt,
    get_task_string,
)
from skillweaver.environment import Browser, State, make_browser
from skillweaver.environment.browser import make_browser_cdp
from skillweaver.knowledge_base.knowledge_base import KnowledgeBase, load_knowledge_base
from skillweaver.lm import LM

# import WebSocket broadcast
from skillweaver.websocket_server import (
    start_server,
    broadcast_task_start,
    broadcast_task_complete,
    broadcast_task_error,
    broadcast_step_start,
    broadcast_step_thinking,
    broadcast_step_action,
    broadcast_step_result,
    broadcast_step_complete,
    broadcast_skill_matched,
    broadcast_skill_executing,
    broadcast_skill_result,
    broadcast_kb_loaded,
)

nest_asyncio.apply()


def _is_function_called_in_act_function(code: str, function_name: str):
    """checkfunction"""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == function_name:
                return True
    return False


def _extract_skill_call_info(code: str, visible_functions: list) -> dict:
    """extractskill"""
    skill_info = {
        "skill_used": False,
        "skill_name": None,
        "skill_params": {}
    }
    
    if not visible_functions:
        return skill_info
    
    function_names = [f["name"] for f in visible_functions]
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                
                if func_name and func_name in function_names:
                    skill_info["skill_used"] = True
                    skill_info["skill_name"] = func_name
                    
                    # extractparameter
                    for i, arg in enumerate(node.args):
                        if isinstance(arg, ast.Constant):
                            skill_info["skill_params"][f"arg{i}"] = arg.value
                    for kw in node.keywords:
                        if isinstance(kw.value, ast.Constant):
                            skill_info["skill_params"][kw.arg] = kw.value.value
                    
                    break
    except:
        pass
    
    return skill_info


def fix_code_formatting(generated_code: str) -> str:
    """format"""
    code = generated_code.replace("\\n", "\n")

    lines = code.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.rstrip()
        if line.endswith(";"):
            line = line[:-1]
        cleaned_lines.append(line)

    code = "\n".join(cleaned_lines)

    if "async def act(page):" not in code:
        indented_code = "\n".join(
            "    " + line for line in code.splitlines() if line.strip() != ""
        )
        code = f"async def act(page):\n{indented_code}"

    code_lines: list[str] = code.splitlines()
    inner_code = code_lines[1:]
    has_return = any(line.strip().startswith("return ") for line in inner_code)

    if not has_return:
        assignment_pattern = re.compile(r"^\s*(\w+)\s*=\s*await\s+.*$")
        last_assigned_variable = None
        for line in inner_code:
            m = assignment_pattern.match(line)
            if m:
                last_assigned_variable = m.group(1)
        if last_assigned_variable:
            indent = "    "
            for line in reversed(inner_code):
                m = assignment_pattern.match(line)
                if m:
                    indent = re.match(r"^\s*", line).group(0)
                    break
            inner_code.append(f"{indent}return {last_assigned_variable}")
            code = code_lines[0] + "\n" + "\n".join(inner_code)

    return code


UNIQUE_FILENAME_COUNTER = 0
UNIQUE_FILENAME_COUNTER_LOCK = asyncio.Lock()


async def attempt_task_with_ws(
    browser: Browser,
    lm: LM,
    task: dict,
    max_steps: int,
    knowledge_base: KnowledgeBase,
    store_dir: str,
    allow_recovery=False,
    as_reference_only=False,
    enable_retrieval_module_for_exploration=True,
):
    """executetask WebSocket broadcaststatus"""
    global UNIQUE_FILENAME_COUNTER
    
    task_start_time = time.time()
    task_string = get_task_string(task)
    url = browser.active_page.url if browser.active_page else "unknown"
    
    # broadcasttaskstart
    has_kb = len(knowledge_base.metadata.get("functions", {})) > 0
    broadcast_task_start(task_string, url, has_kb)

    if not os.path.exists(store_dir):
        os.makedirs(store_dir)

    with open(os.path.join(store_dir, "task.json"), "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2)

    states: list[State] = []
    actions: list[dict] = []
    disabled_function_names: list[str] = []

    states.append(await browser.observe())
    states[0].save(store_dir, "000_state")

    visible_functions, visible_functions_string, visible_functions_reason = (
        await create_skill_library_prompt(
            task,
            knowledge_base,
            lm,
            as_reference_only,
            enable_retrieval_module_for_exploration,
        )
    )
    
    await aprint(
        " Retrieved Task-Relevant Functions: "
        + ", ".join([function["name"] for function in visible_functions])
    )
    
    # broadcastskill
    if visible_functions:
        for func in visible_functions[:3]:
            broadcast_skill_matched(
                func["name"],
                func.get("description", ""),
                confidence=0.9
            )

    with open(os.path.join(store_dir, "relevant_function_prediction.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "reasoning": visible_functions_reason,
                "functions_formatted": visible_functions_string,
                "functions": visible_functions,
            },
            f,
            indent=2,
        )

    total_steps_executed = 0
    task_success = False

    try:
        for step in range(max_steps):
            step_start_time = time.time()
            break_early = False
            total_steps_executed = step + 1

            await aprint(f"{datetime.now().isoformat()} Step {step}")
            
            # broadcaststepstart
            broadcast_step_start(step, max_steps)

            action = await codegen_generate(
                lm,
                states,
                actions,
                knowledge_base,
                task_string,
                is_eval_task=task["type"] == "prod",
                visible_functions_string=visible_functions_string,
                disabled_function_names=disabled_function_names,
                as_reference_only=as_reference_only,
            )

            if action["python_code"]:
                await aprint("[EXEC] Executing", step)
                await aprint(" Step-by-step reasoning:")
                await aprint(action["step_by_step_reasoning"])
                
                # broadcast
                broadcast_step_thinking(step, action["step_by_step_reasoning"])
                
                await aprint(" Generated code:")
                await aprint(action["python_code"])
                
                # checkskill
                skill_info = _extract_skill_call_info(action["python_code"], visible_functions)
                
                if skill_info["skill_used"]:
                    broadcast_skill_executing(skill_info["skill_name"], skill_info["skill_params"])
                
                # broadcastexecute
                action_type = "skill_call" if skill_info["skill_used"] else "code_execution"
                action_detail = skill_info["skill_name"] if skill_info["skill_used"] else "Playwright automation"
                broadcast_step_action(step, action_type, action_detail, action["python_code"][:200])

                async with UNIQUE_FILENAME_COUNTER_LOCK:
                    suffix = UNIQUE_FILENAME_COUNTER
                    UNIQUE_FILENAME_COUNTER += 1

                formatted_code = fix_code_formatting(action["python_code"])
                action["formatted_code"] = formatted_code
                
                exec_start = time.time()
                action["result"] = await codegen_do(
                    browser=browser,
                    knowledge_base=knowledge_base,
                    code=formatted_code,
                    filename=os.path.join(store_dir, f"py_{step}_{suffix}.py"),
                    disabled_function_names=disabled_function_names,
                    allow_recovery=allow_recovery,
                    recovery_lm=lm,
                    as_reference_only=as_reference_only,
                )
                exec_duration = time.time() - exec_start
                
                # broadcaststepresult
                step_success = action["result"]["exception"] is None
                broadcast_step_result(
                    step, 
                    step_success,
                    result=str(action["result"].get("return_value", ""))[:100] if step_success else None,
                    error=str(action["result"]["exception"])[:200] if not step_success else None
                )
                
                if skill_info["skill_used"]:
                    broadcast_skill_result(skill_info["skill_name"], step_success)

                has_recovery_attempts = (
                    action["result"]["recovery_results"] is not None
                    and len(action["result"]["recovery_results"]) > 0
                )
                
                if (
                    task["type"] == "test"
                    and action["result"]["exception"] is None
                    and _is_function_called_in_act_function(
                        action["python_code"], task["function_name"]
                    )
                    and not has_recovery_attempts
                ):
                    break_early = True
                    task_success = True
            else:
                assert (
                    action["terminate_with_result"] != ""
                ), "Not a terminal action, but no code was provided."
                task_success = True

            actions.append(action)
            with open(os.path.join(store_dir, f"{step:03d}_action.json"), "w", encoding="utf-8") as f:
                json.dump(action, f, indent=2)

            try:
                await browser.active_page.wait_for_load_state("networkidle", timeout=10000)
                await browser.active_page.wait_for_load_state("load")
            except Exception as e:
                pass
            
            states.append(await browser.observe())
            states[-1].save(store_dir, f"{step+1:03d}_state")
            
            # broadcaststepcompleted
            step_duration = time.time() - step_start_time
            broadcast_step_complete(step, step_duration)

            if break_early:
                break

            if action["terminate_with_result"] != "":
                await aprint("Received `terminate` action.")
                task_success = True
                break

        with open(os.path.join(store_dir, "trajectory_pretty.txt"), "w", encoding="utf-8") as f:
            string = codegen_trajectory_to_string(
                states,
                actions,
                only_initial=False,
                include_recoveries=True,
            )
            f.write(string)

        # broadcasttaskcompleted
        task_duration = time.time() - task_start_time
        broadcast_task_complete(task_string, task_success, task_duration, total_steps_executed)
        
        return (states, actions)

    except Exception as e:
        broadcast_task_error(task_string, str(e))
        raise


def cli(
    start_url: str,
    task: str,
    agent_lm_name: str = "gpt-4o",
    knowledge_base_path_prefix: Optional[str] = None,
    max_steps: int = 10,
    headless: bool = True,
):
    """
    
    
    Args:
        start_url:  URL
        task: executetask
        agent_lm_name:  LLM model
        knowledge_base_path_prefix: knowledge basepath
        max_steps: 
        headless: modedefault True WebSocket syncstatus NogicOS
    """
    from contextlib import nullcontext

    from skillweaver.containerization.containers import containers
    from skillweaver.environment.patches import apply_patches
    from skillweaver.evaluation.webarena_config import SITES
    from skillweaver.evaluation.webarena_login import login_subprocess

    #  WebSocket server
    print("[SkillFlow] Starting WebSocket server...")
    start_server()
    
    import time
    time.sleep(1)

    lm = LM(agent_lm_name)

    if knowledge_base_path_prefix is None:
        knowledge_base = KnowledgeBase()
    else:
        knowledge_base = load_knowledge_base(knowledge_base_path_prefix)
        knowledge_base.hide_unverified = False
        broadcast_kb_loaded(knowledge_base_path_prefix, len(knowledge_base.functions))

    log_dir = os.path.join(
        "logs", datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + agent_lm_name
    )

    setup_site: str | None = None
    for site in SITES:
        start_string = f"__{site}__"
        if start_url.startswith(start_string):
            setup_site = site.lower()
            start_url = start_url[len(start_string):]
            break

    apply_patches()

    async def impl():
        nonlocal start_url

        use_manual_containers = os.getenv("CONTAINER_SETUP", "auto").lower() == "manual"
        async with (
            containers([setup_site])
            if setup_site is not None and not use_manual_containers
            else nullcontext({})
        ) as container_hostnames:
            if setup_site is not None:
                if not use_manual_containers:
                    SITES.update(
                        {
                            k.upper(): "http://" + v
                            for k, v in container_hostnames.items()
                        }
                    )
                    if "shopping_admin" in container_hostnames:
                        SITES["SHOPPING_ADMIN"] = SITES["SHOPPING_ADMIN"] + "/admin"
                else:
                    container_hostnames = {setup_site: SITES[setup_site.upper()]}

                storage_state_file = login_subprocess(container_hostnames)
                start_url = SITES[setup_site.upper()] + start_url
                print("Start URL:", start_url)
            else:
                storage_state_file = None

            async with async_playwright() as p:
                os.makedirs(log_dir, exist_ok=True)
                
                # 2025  headless browser + WebSocket sync
                # Playwright run Electron  webview
                #  headless modeexecute WebSocket broadcast NogicOS
                print(f"[NogicOS] Starting headless browser for task execution...")
                print(f"[NogicOS] Target URL: {start_url}")
                print(f"[NogicOS] Operations will be synced to NogicOS via WebSocket")
                
                browser = await make_browser(
                    p,
                    start_url,
                    headless=True,  # headless modeexecute
                    storage_state=storage_state_file,
                )
                
                await attempt_task_with_ws(
                    browser,
                    lm,
                    {"type": "prod", "task": task},
                    max_steps=max_steps,
                    knowledge_base=knowledge_base,
                    store_dir=log_dir,
                )
                await browser.close()

    asyncio.run(impl())


if __name__ == "__main__":
    import typer

    typer.run(cli)
