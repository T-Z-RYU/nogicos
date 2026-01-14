import ast
import datetime
import importlib
import io
import json
import os
import sys
import traceback
from typing import Any, TypedDict

from aioconsole import aprint

from skillweaver.environment import Browser, State
from skillweaver.environment.patches import (
    EXCEPTION_HANDLERS,
    EXECUTION_CONTEXT,
    RecoveryResult,
    create_locator_error_wrapper,
)
from skillweaver.knowledge_base.knowledge_base import KnowledgeBase
from skillweaver.knowledge_base.type_checking import find_type_errors
from skillweaver.lm import LM
from skillweaver.sanity_check_code import sanity_check_codegen_code
from skillweaver.templates import codegen_templ
from skillweaver.util import J
from skillweaver.util.deep_await import deep_await
import re as _re


def sanitize_generated_code(code: str) -> str:
    """
    Clean up LLM-generated code to avoid common errors.
    
    Fixes:
    1. Non-ASCII characters (cause UTF-8 errors)
    2. Missing .first on selectors (cause strict mode violations)
    3. Missing timeout parameters (cause TimeoutError)
    """
    # 1. Remove non-ASCII characters (keep only ASCII)
    code = code.encode('ascii', 'ignore').decode('ascii')
    
    # 2. Auto-add .first to get_by_role().click/fill/press patterns
    # Pattern: .get_by_role(...).click() without .first
    pattern = r'(\.get_by_role\([^)]+\))(\.(click|fill|press|wait_for)\()'
    
    def add_first(match):
        selector = match.group(1)
        action = match.group(2)
        # Only add .first if it's not already there
        if '.first' not in selector and '.nth(' not in selector:
            return selector + '.first' + action
        return match.group(0)
    
    code = _re.sub(pattern, add_first, code)
    
    # 3. Add timeout to click/fill/press if not present
    for action in ['click', 'fill', 'press']:
        # Match action() without timeout parameter
        pattern = rf'\.{action}\(\s*\)'
        replacement = f'.{action}(timeout=15000)'
        code = _re.sub(pattern, replacement, code)
        
        # Match action("...") without timeout
        pattern = rf'\.{action}\(([^)]+)\)'
        def add_timeout(m):
            args = m.group(1)
            if 'timeout' not in args:
                return f'.{action}({args}, timeout=15000)'
            return m.group(0)
        code = _re.sub(pattern, add_timeout, code)
    
    return code


def annotate_source_with_recoveries(
    function_source: str, recoveries: list[dict]
) -> str:
    source_lines = function_source.split("\n")
    for recovery in recoveries:
        line = recovery["debug"]["error_function_offset_line"]
        locator = recovery["attempts"][-1]["locator_code"]
        source_lines[
            line
        ] += f" # RECOVERY. Locator should be replaced with (*exact string*): {locator}"
    return "\n".join(source_lines)


def codegen_action_to_string(action: dict, include_recoveries=False) -> str:
    if action["terminate_with_result"]:
        return (
            "<terminate_with_result>\n"
            + action["terminate_with_result"]
            + "\n</terminate_with_result>"
        )

    if include_recoveries and action["result"]["recovery_results"] is not None:
        recoveries = action["result"]["recovery_results"]
        action_recoveries = [
            recov
            for recov in recoveries
            if recov["debug"]["error_function_name"] == "act"
        ]
        knowledge_base_recoveries = [
            recov
            for recov in recoveries
            if recov["debug"]["error_function_name"] != "act"
        ]
        action_source = annotate_source_with_recoveries(
            action["python_code"],
            [recov for recov in action_recoveries if recov["outcome"] == "success"],
        )
    else:
        action_source = action["python_code"]
        action_recoveries = []
        knowledge_base_recoveries = []

    # Modify `act` code to include recovery messages.

    result = f"""
<reasoning>
{action['step_by_step_reasoning']}
</reasoning>

<code>
{action_source}
</code>"""

    if action["result"]["stdout"]:
        result += f"""

<stdout>
{action['result']['stdout']}
</stdout>"""

    if action["result"]["output"] is not None:
        result += f"""

<result>
{repr(action['result']['output'])}
</result>"""

    if "warnings" in action["result"] and action["result"]["warnings"]:
        warnings_str = "\n".join(" - " + warn for warn in action["result"]["warnings"])
        result += f"""

<warnings>
{warnings_str}
</warnings>"""

    if len(knowledge_base_recoveries) > 0:
        recovery_results = action["result"]["recovery_results"]
        recovery_annotated_sources: dict[str, str] = {}

        # group by function name
        function_names = set(
            recov["debug"]["error_function_name"]
            for recov in recovery_results
            if recov["outcome"] == "success"
        )
        for name in function_names:
            relevant_recoveries = [
                recov
                for recov in recovery_results
                if recov["debug"]["error_function_name"] == name
                and recov["outcome"] == "success"
            ]
            fn_source = relevant_recoveries[0]["debug"]["error_function_source"]
            recovery_annotated_sources[name] = annotate_source_with_recoveries(
                fn_source, relevant_recoveries
            )

        result += f"""
    
We found a bug in one of the APIs, and were able to make the following {'recovery' if len(recovery_annotated_sources) == 1 else 'recoveries'}. For each RECOVERY comment, follow the instructions."""

        for (
            fn_name,
            recovery_annotated_source,
        ) in recovery_annotated_sources.items():
            if fn_name == "act":
                continue

            result += f"""
<recovery>
{recovery_annotated_source}
</recovery>"""

    if action["result"]["exception"]:
        maybe_truncated_msg = "\n".join(
            action["result"]["exception"]["args"][0].split("\n")[:5]
        )
        result += f"""

<exception>
{repr(action['result']['exception']['type'])}: {maybe_truncated_msg}
</exception>"""

    return result.strip()


def state_to_string(state: State, include_axtree=True) -> str:
    return (
        f"URL: {state.relative_url}\nTitle: {state.title}"
        + f"\n\n{state.get_axtree_string()}"
        if include_axtree
        else ""
    )


def codegen_trajectory_to_string(
    states: list[State],
    actions: list[dict],
    only_initial=True,
    include_recoveries=False,
) -> str:
    trajectory_string = f"<state 0>\n{state_to_string(states[0])}\n</state 0>\n\n"

    for i in range(len(actions)):
        trajectory_string += (
            codegen_action_to_string(actions[i], include_recoveries=include_recoveries)
            + "\n\n---\n\n"
        )

        if not only_initial:
            trajectory_string += f"<state {i+1}>\n{state_to_string(states[i + 1], include_axtree=not only_initial)}\n</state {i+1}>\n\n"

    return trajectory_string


def codegen_trajectory_from_folder(folder: str, weak=False):
    states: list[State] = []
    actions: list[dict] = []
    i = 0
    while os.path.exists(os.path.join(folder, f"{i:03d}_action.json")):
        states.append(State.load(folder, f"{i:03d}_state", weak=weak))
        with open(f"{folder}/{i:03d}_action.json") as f:
            actions.append(json.load(f))

        i += 1

    states.append(State.load(folder, f"{i:03d}_state"))

    return (states, actions)


def _create_codegen_prompt(
    lm: LM,
    states: list[State],
    actions: list[dict],
    task: str,
    disabled_function_names: list[str],
    visible_functions_string: str,
    is_eval_task: bool,
    as_reference_only: bool,
    errors: str | None = None,
    previous_attempt_code: str | None = None,
):
    user_text_prompt = codegen_templ(
        ax_tree=states[-1].get_axtree_string(),
        procedural_knowledge=visible_functions_string
        + (
            (
                "\n\nNote: The following functions are hereby disabled:\n"
                + "\n".join(" - " + fn for fn in disabled_function_names)
            )
            if len(disabled_function_names) > 0
            else ""
        ),
        previous_actions="\n\n---\n\n".join(
            codegen_action_to_string(action) for action in actions
        ),
        task=task,
        title=states[-1].title,
        url=states[-1].url,
        is_first_step=len(actions) == 0,
        is_eval_task=is_eval_task,
        as_reference_only=as_reference_only,
    )

    if errors is not None:
        assert (
            previous_attempt_code is not None
        ), "previous_attempt_code must be set if errors are provided"
        user_text_prompt += f"\n\nA previous attempt had some errors. Your previous code:\n\n<code>\n{previous_attempt_code}\n</code>\n\nErrors:\n\n<errors>\n{errors}\n</errors>\n\nPlease update your response to fix these errors."

    return [
        {
            "role": "system",
            "content": "You interact with websites via Playwright scripting, written in Python. You reason step-by-step before returning code to execute your goal. You are very careful to follow the accessibility tree roles and names exactly, as incorrect roles will lead to timeout errors.",
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_text_prompt},
                lm.image_url_content_piece(states[-1].screenshot),
            ],
        },
    ]


async def codegen_generate(
    lm: LM,
    states: list[State],
    actions: list[dict],
    knowledge_base: KnowledgeBase,
    task: str,
    is_eval_task: bool,
    visible_functions_string: str,
    disabled_function_names: list[str],
    as_reference_only=False,
):
    errors: str | None = None
    previous_attempt_code: str | None = None
    for _ in range(5):
        prompt = _create_codegen_prompt(
            lm,
            states,
            actions,
            task,
            disabled_function_names,
            visible_functions_string,
            is_eval_task,
            as_reference_only,
            errors,
            previous_attempt_code,
        )

        response = await lm(
            prompt,
            json_schema=J.struct(
                step_by_step_reasoning=J.string(),
                python_code=J.string(),
                terminate_with_result=J.string(),
            ),
        )
        response["prompt"] = prompt[1]["content"][0]["text"]

        if response["python_code"]:
            response["terminate_with_result"] = ""

            error_list = sanity_check_codegen_code(
                response["python_code"],
                disabled_function_names,
                knowledge_base,
                as_reference_only,
            )

            if len(error_list) == 0:
                break

            errors = "\n".join([" - " + error for error in error_list])
            previous_attempt_code = response["python_code"]

            await aprint("Errors found in code generation:\n", errors)

        elif response["terminate_with_result"] != "":
            break
        else:
            errors = "You did not provide any Python code, but you also did not provide a result for `terminate_with_result`. Please provide one or the other."

    return response


class CodeExecutionException(TypedDict):
    type: str
    args: tuple[Any]
    traceback: str | None


class CodeExecutionOutcome(TypedDict):
    output: Any
    exception: CodeExecutionException | None
    warnings: list[str]
    stdout: str
    recovery_results: list[RecoveryResult] | None  # None if recovery is not enabled


# This variable is so that we can communicate information between the codegen_do function and the code that it runs.
vars = {}


async def codegen_do(
    browser: Browser,
    knowledge_base: KnowledgeBase,
    code: str,
    filename: str,
    disabled_function_names: list[str],
    allow_recovery: bool,
    recovery_lm: LM | None = None,
    as_reference_only=False,
) -> CodeExecutionOutcome:
    """
    `code` parameter must be formatted as an "act" function
    """

    page = browser.active_page
    stdout_capture = io.StringIO()
    recovery_results: list[RecoveryResult] = []

    def print_wrapper(*args, **kwargs):
        print(*args, **kwargs, file=stdout_capture)

    # MODIFIED: Sanitize generated code to fix common LLM errors
    code = sanitize_generated_code(code)
    
    with open(filename, "w", encoding="utf-8") as f:
        key = os.path.abspath(filename)
        vars[key] = [
            print_wrapper,
        ]
        kb_code = knowledge_base.code if not as_reference_only else ""
        module_code = f"""
# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars[{repr(key)}]

{kb_code}

{code}""".strip()

        f.write(module_code)

    if allow_recovery:
        assert (
            recovery_lm is not None
        ), "recovery_lm must be non-None if allow_recovery is True"

        # source line 6 -> kb line 1
        source_map = {l + 5: l for l in range(kb_code.count("\n") + 1)}
        contextvar_token = EXECUTION_CONTEXT.set(filename)
        EXCEPTION_HANDLERS[filename] = create_locator_error_wrapper(
            knowledge_base,
            source_map,
            recovery_results,
            recovery_lm,
            module_code,
            code,
            disabled_function_names,
            allow_act_function_recovery=True,
        )
    else:
        contextvar_token = None

    # A module from this timestep may have been loaded in previous runs.
    module_name = os.path.basename(filename)[:-3]
    if module_name in sys.modules:
        del sys.modules[module_name]

    d = os.path.dirname(filename)
    sys.path.append(d)

    warnings = []
    output = exception = traceback_ = None
    try:
        module = importlib.__import__(module_name)
        output = await module.act(page)

        awaits = []
        output = await deep_await(output, awaits)
        for await_path in awaits:
            warnings.append(
                f"Your function returned `retval`, and we needed to await `{await_path}`. Please await all coroutines that you return."
            )

    except Exception as e:
        exception = e
        output = None
        traceback_ = traceback.format_exc()
    finally:
        sys.path.remove(d)
        if contextvar_token:
            EXECUTION_CONTEXT.reset(contextvar_token)
            del EXCEPTION_HANDLERS[filename]

    if exception is not None:
        with open("error.log", "a") as f:
            firstline = exception.args[0].split("\n")[0]
            f.write(
                f"{datetime.datetime.now().isoformat()} Error in {filename}: {type(exception).__name__}: {firstline}"
            )

    return {
        "output": output,
        "exception": (
            {
                "type": type(exception).__name__,
                "args": exception.args,
                "traceback": traceback_,
            }
            if exception
            else None
        ),
        "warnings": warnings,
        "stdout": stdout_capture.getvalue(),
        # `recovery_results` will return a list of line numbers, etc.
        # we can avoid patching the same line multiple times in the same run (because this will only happen when we run a loop,
        # and we don't want to be stuck patching a lot)
        "recovery_results": recovery_results,
    }
