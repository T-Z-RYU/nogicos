# -*- coding: utf-8 -*-
import ast
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from typing import Optional

# Windows UTF-8 environmentvariable
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

import nest_asyncio
from aioconsole import aprint
from playwright.async_api import async_playwright

from skillweaver.agent import codegen_do, codegen_generate, codegen_trajectory_to_string
from skillweaver.create_skill_library_prompt import (
    create_skill_library_prompt,
    get_task_string,
)
from skillweaver.environment import Browser, State, make_browser
from skillweaver.knowledge_base.knowledge_base import KnowledgeBase, load_knowledge_base
from skillweaver.lm import LM

nest_asyncio.apply()


def _is_function_called_in_act_function(code: str, function_name: str):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == function_name:
                return True
    return False


def fix_code_formatting(generated_code: str) -> str:
    # Convert literal "\n" sequences to actual newlines.
    code = generated_code.replace("\\n", "\n")

    # Remove trailing semicolons from each line.
    lines = code.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.rstrip()
        if line.endswith(";"):
            line = line[:-1]
        cleaned_lines.append(line)

    code = "\n".join(cleaned_lines)

    # Wrap the code in the required async function if it's not already wrapped.
    if "async def act(page):" not in code:
        # Indent each non-empty line by 4 spaces.
        indented_code = "\n".join(
            "    " + line for line in code.splitlines() if line.strip() != ""
        )
        code = f"async def act(page):\n{indented_code}"

    # Split code into lines for further processing.
    code_lines: list[str] = code.splitlines()  # type: ignore

    # Extract the inner code (lines inside the function)
    inner_code = code_lines[1:]

    # Check if there is any line with a return statement.
    has_return = any(line.strip().startswith("return ") for line in inner_code)

    # If no return statement exists, check for an awaited assignment.
    if not has_return:
        assignment_pattern = re.compile(r"^\s*(\w+)\s*=\s*await\s+.*$")
        last_assigned_variable = None
        for line in inner_code:
            m = assignment_pattern.match(line)
            if m:
                last_assigned_variable = m.group(1)
        # If we found an awaited assignment, add a return statement for that variable.
        if last_assigned_variable:
            # Retrieve indentation from the last assignment line (or default to 4 spaces).
            indent = "    "
            for line in reversed(inner_code):
                m = assignment_pattern.match(line)
                if m:
                    indent = re.match(r"^\s*", line).group(0)  # type: ignore
                    break
            inner_code.append(f"{indent}return {last_assigned_variable}")
            code = code_lines[0] + "\n" + "\n".join(inner_code)

    return code


UNIQUE_FILENAME_COUNTER = 0
UNIQUE_FILENAME_COUNTER_LOCK = asyncio.Lock()


async def attempt_task(
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
    global UNIQUE_FILENAME_COUNTER

    if not os.path.exists(store_dir):
        os.makedirs(store_dir)

    # Note: Knowledge base does not get modified.
    with open(f"{store_dir}/task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2)

    states: list[State] = []
    actions: list[dict] = []
    disabled_function_names: list[str] = []

    states.append(await browser.observe())
    states[0].save(store_dir, "000_state")

    task_string = get_task_string(task)
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
        "[FOUND] Retrieved Task-Relevant Functions: "
        + ", ".join([function["name"] for function in visible_functions])
    )

    with open(store_dir + "/relevant_function_prediction.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "reasoning": visible_functions_reason,
                "functions_formatted": visible_functions_string,
                "functions": visible_functions,
            },
            f,
            indent=2,
        )

    for step in range(max_steps):
        break_early = False

        await aprint(f"{datetime.now().isoformat()} Step {step}")

        # Generate action.
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
            await aprint("[REASON] Step-by-step reasoning:")
            await aprint(action["step_by_step_reasoning"])
            await aprint("[CODE] Generated code:")
            await aprint(action["python_code"])

            # #region agent log - Hypothesis B: Generated code content
            import json as _json, time as _time
            _log_path = r"c:\Users\WIN\Desktop\Cursor Project\.cursor\debug.log"
            _has_placeholder = "QUERY" in action["python_code"] or "PUT_" in action["python_code"] or "TODO" in action["python_code"] or "placeholder" in action["python_code"].lower()
            with open(_log_path, "a", encoding="utf-8") as _f:
                _f.write(_json.dumps({"hypothesisId": "B", "location": "attempt_task.py:codegen", "message": "Generated code analysis", "data": {"step": step, "has_placeholder": _has_placeholder, "code_snippet": action["python_code"][:300]}, "timestamp": int(_time.time()*1000)}) + "\n")
            # #endregion

            # now we make a __UNIQUE__ filename for the py_{step}.py
            async with UNIQUE_FILENAME_COUNTER_LOCK:
                suffix = UNIQUE_FILENAME_COUNTER
                UNIQUE_FILENAME_COUNTER += 1

            formatted_code = fix_code_formatting(action["python_code"])
            action["formatted_code"] = formatted_code
            action["result"] = await codegen_do(
                browser=browser,
                knowledge_base=knowledge_base,
                code=formatted_code,
                filename=f"{store_dir}/py_{step}_{suffix}.py",
                disabled_function_names=disabled_function_names,
                allow_recovery=allow_recovery,
                recovery_lm=lm,
                as_reference_only=as_reference_only,
            )
            has_recovery_attempts = (
                # Has a recovery, this should be put into the knowledge base.
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
        else:
            assert (
                action["terminate_with_result"] != ""
            ), "Not a terminal action, but no code was provided."

        actions.append(action)
        with open(f"{store_dir}/{step:03d}_action.json", "w", encoding="utf-8") as f:
            json.dump(action, f, indent=2)

        # Give one retry, in case of redirections.
        try:
            await browser.active_page.wait_for_load_state("networkidle", timeout=10000)
            await browser.active_page.wait_for_load_state("load")
        except Exception as e:
            pass
        states.append(await browser.observe())

        states[-1].save(store_dir, f"{step+1:03d}_state")

        # If we forced this action, and there was no Exception, consider it tested.
        # Break out of this loop. We can detect this case by checking if len(actions) == 1
        # and the mode is "test".
        # was_forced = step == 0 and task["type"] == "test"
        # if was_forced and action["result"]["exception"] is None:
        #     break
        if break_early:
            break

        if action["terminate_with_result"] != "":
            await aprint("Received `terminate` action.")
            break

    with open(f"{store_dir}/trajectory_pretty.txt", "w", encoding="utf-8") as f:
        string = codegen_trajectory_to_string(
            states,
            actions,
            only_initial=False,
            include_recoveries=True,
        )
        f.write(string)

    return (states, actions)


async def cli(
    start_url: str,
    task: str,
    agent_lm_name: str = "gpt-4o",
    knowledge_base_path_prefix: Optional[str] = None,
    max_steps: int = 10,
    headless: bool = False,
):
    from contextlib import nullcontext

    from skillweaver.containerization.containers import containers
    from skillweaver.environment.patches import apply_patches
    from skillweaver.evaluation.webarena_config import SITES
    from skillweaver.evaluation.webarena_login import login_subprocess

    # required to be able to use JSON schema
    lm = LM(agent_lm_name)

    if knowledge_base_path_prefix is None:
        knowledge_base = KnowledgeBase()
    else:
        knowledge_base = load_knowledge_base(knowledge_base_path_prefix)
        knowledge_base.hide_unverified = False

    log_dir = os.path.join(
        "logs", datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + agent_lm_name
    )

    setup_site: str | None = None
    for site in SITES:
        start_string = f"__{site}__"
        if start_url.startswith(start_string):
            setup_site = site.lower()
            start_url = start_url[len(start_string) :]
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
                    # Updates the process-level configuration for hostname resolution.
                    SITES.update(
                        {
                            k.upper(): "http://" + v
                            for k, v in container_hostnames.items()
                        }
                    )
                    # shopping_admin start page is '/admin', not '/'.
                    if "shopping_admin" in container_hostnames:
                        SITES["SHOPPING_ADMIN"] = SITES["SHOPPING_ADMIN"] + "/admin"
                else:
                    container_hostnames = {setup_site: SITES[setup_site.upper()]}

                storage_state_file = login_subprocess(container_hostnames)

                # Replace the start_url with the container hostname.
                start_url = SITES[setup_site.upper()] + start_url
                print("Start URL:", start_url)
            else:
                storage_state_file = None

            async with async_playwright() as p:
                os.makedirs(log_dir, exist_ok=True)
                browser = await make_browser(
                    p,
                    start_url,
                    headless=headless,
                    storage_state=storage_state_file,
                )
                await attempt_task(
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
