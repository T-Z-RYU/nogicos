import ast
import asyncio
import traceback
from contextvars import ContextVar
from typing import Callable, Coroutine, Literal, Optional, TypedDict
from urllib.parse import urlparse

from aioconsole import aprint
from playwright.async_api import Locator, Page, async_playwright

from skillweaver.environment.a11y import (
    capture_accessibility_tree,
    filter_out_of_view_nodes,
    serialize_accessibility_tree,
)
from skillweaver.environment.browser import make_browser
from skillweaver.knowledge_base.knowledge_base import KnowledgeBase
from skillweaver.lm import LM
from skillweaver.templates import axtree_intro
from skillweaver.util import J

ActionNameLiteral = Literal[
    "click", "type", "fill", "hover", "select", "check", "uncheck"
]

# we can wrap each function with a boundary that modifies the current exception_handler in a recursive fashion
EXCEPTION_HANDLER: Optional[
    Callable[
        [
            ActionNameLiteral,
            Exception,
            str,  # filename
            int,  # lineno
            Locator,
            dict,  # locals
            tuple,  # args
            dict,  # kwargs
        ],
        Coroutine,
    ]
] = None
EXCEPTION_HANDLERS = {}
EXECUTION_CONTEXT = ContextVar("execution_context", default="<default>")


def _apply_relative_goto():
    original_goto = Page.goto

    async def relative_goto(self: Page, url: str, **kwargs):
        if url.startswith("/"):
            parsed = urlparse(self.url)
            url = parsed.scheme + "://" + parsed.netloc + url

        return await original_goto(self, url, **kwargs)

    Page.goto = relative_goto


def _make_wrapper(original_locator_fn):
    import inspect

    async def wrapper(self: Locator, *locator_args, **locator_kwargs):
        global EXCEPTION_HANDLERS, EXECUTION_CONTEXT

        # get line in parent function
        frame = inspect.currentframe()
        assert frame
        assert frame.f_back
        filename = frame.f_back.f_code.co_filename
        lineno = frame.f_back.f_lineno
        locals = frame.f_back.f_locals

        try:
            return await original_locator_fn(self, *locator_args, **locator_kwargs)
        except Exception as e:
            # if EXCEPTION_HANDLER is not None:
            handler = EXCEPTION_HANDLERS.get(EXECUTION_CONTEXT.get(), None)
            if handler:
                return await handler(
                    original_locator_fn.__name__,
                    e,
                    filename,
                    lineno,
                    self,
                    locals,
                    locator_args,
                    locator_kwargs,
                )
            else:
                raise

    wrapper.__name__ = original_locator_fn.__name__

    return wrapper


def _apply_exception_handlers():
    for action_name in [
        "click",
        "type",
        "fill",
        "hover",
        "select_option",
        "wait_for",
        "check",
        "uncheck",
    ]:
        original_locator_fn = getattr(Locator, action_name)
        wrapper = _make_wrapper(original_locator_fn)
        setattr(Locator, action_name, wrapper)
        wrapper.__name__ = action_name


def apply_patches():
    import re

    # patch for the playwright bug.
    orig_re_escape = re.escape

    def patched_escape(s: str):
        s = s.replace("/", "\\u002f")
        return orig_re_escape(s)

    re.escape = patched_escape
    _apply_relative_goto()
    _apply_exception_handlers()


def _is_not_ok_locator_expression(locator: str):
    try:
        code_tree = ast.parse(locator)
    except SyntaxError as e:
        return "SyntaxError: " + str(e)

    if not isinstance(code_tree.body[0], ast.Expr):
        return "Not an expression; instead: " + type(code_tree.body[0]).__name__

    if not isinstance(code_tree.body[0].value, ast.Call):
        return (
            "Value is not an ast.Call; instead: "
            + type(code_tree.body[0].value).__name__
        )

    if not locator.startswith("page."):
        return "Locator does not start with `page.`"

    if ".locator" in locator or ".query_selector" in locator:
        return "Please use Accessibility Tree-centric selectors, like `page.get_by_role()`, `.nth()`, instead of the CSS-style selectors like `.locator()` or `.query_selector()`."

    return False


class RecoveryResultException(TypedDict):
    type: str
    message: str


class RecoveryResultDebugInfo(TypedDict):
    error_function_name: str
    error_function_start_line: int
    error_function_end_line: int
    error_function_offset_line: int
    error_function_source: str


class RecoveryAttempt(TypedDict):
    choice: str
    locator_code: str
    error: str


class RecoveryResult(TypedDict):
    action_name: str
    filename: str
    lineno: int
    recovery_instructions: str
    attempts: list[dict[str, str]]
    outcome: Literal["success", "fail"]
    exception: RecoveryResultException | None
    debug: RecoveryResultDebugInfo


def create_locator_error_wrapper(
    knowledge_base: KnowledgeBase,
    source_mapping: dict[int, int],
    recovery_results: list[RecoveryResult],
    recovery_lm: LM,
    module_code: str,
    code: str,
    disabled_function_names: list[str],
    allow_act_function_recovery=True,
):
    visited_locators = {}

    async def handle_locator_error(
        action_name: str,
        exception: Exception,
        filename: str,
        lineno: int,
        locator: Locator,
        locals_: dict,
        locator_args,
        locator_kwargs,
    ):
        # Only handle locator errors.
        if (
            not ("Timeout " in str(exception) and "ms exceeded." in str(exception))
            and not ("Error: strict mode violation" in str(exception))
            and not ("invalidselector" in str(exception).lower().replace(" ", ""))
        ):
            raise exception

        key = filename + str(lineno)
        if key in visited_locators:
            raise exception

        visited_locators[key] = True

        await aprint(f"Exception at {filename}:{lineno}")

        error_function_name: str | None = None
        error_function_start_line = -1
        error_function_end_line = -1
        error_function_offset_line = -1
        if lineno not in source_mapping and allow_act_function_recovery:
            # occurred in `act` function.
            error_function_name = "act"

            # find the line where `act` is defined.
            # make sure we are inside the `act` function.
            parsed = ast.parse(module_code)
            for node in parsed.body:
                if isinstance(node, ast.AsyncFunctionDef) and node.name == "act":
                    act_start_line = node.lineno
                    act_end_line = node.end_lineno
                    assert (
                        act_end_line is not None
                    ), "AsyncFunctionDef must have an end_lineno"
                    if not (act_start_line <= lineno <= act_end_line):
                        await aprint("Expected to find act() function but did not.")
                        await aprint(exception)
                        await aprint(traceback.format_exc())
                        raise exception

                    error_function_offset_line = lineno - act_start_line
                    break
        else:
            # Highlight the line in the function where the error occurred.
            parsed = ast.parse(knowledge_base.code)
            for node in parsed.body:
                if isinstance(node, ast.AsyncFunctionDef):
                    start_line = node.lineno
                    end_line = node.end_lineno
                    assert (
                        end_line is not None
                    ), "AsyncFunctionDef must have an end_lineno"

                    if start_line <= source_mapping[lineno] <= end_line:
                        # We found the function where the error occurred.
                        error_function_name = node.name
                        error_function_start_line = start_line
                        error_function_end_line = end_line
                        error_function_offset_line = (
                            source_mapping[lineno] - error_function_start_line
                        )
                        break

        if error_function_name is None:
            # This error did not occur in any recoverable/modifiable function.
            await aprint("error_function_name was None. Ignoring this exception.")
            raise exception

        # Found the function. We can stringify this error.
        if error_function_name == "act":
            source = code
        else:
            # We disable a function after it errors the first time.
            # This is to prevent the agent from repeatedly calling it, and also because we do not apply recoveries mid-trajectory.
            disabled_function_names.append(error_function_name)
            error_function = [
                fn
                for fn in knowledge_base.get_functions(force_return_all=True)
                if fn["name"] == error_function_name
            ][0]

            source = error_function["source"]
        lines = source.split("\n")
        before = lines[:error_function_offset_line]
        during = lines[error_function_offset_line]
        after = lines[error_function_offset_line + 1 :]

        locals_str_filter = ""
        for k, v in locals_.items():
            v_type = type(v).__name__
            if type(v) in [str, int, float, bool, list, dict]:
                locals_str_filter += f" - {k}: {v_type} = {repr(v)}\n"
            else:
                locals_str_filter += f" - {k}: {v_type}\n"

        if len(locals_str_filter) > 900:
            locals_str_filter = locals_str_filter[:900] + "..."
        elif len(locals_str_filter) == 0:
            locals_str_filter = "None"

        error_string = f"Error occurred in function `{error_function_name}` at line {error_function_offset_line + 1}. Local variables: {locals_str_filter}.\n"
        i = 1
        for line in before:
            error_string += f"{i: 3d}: {line}\n"
            i += 1
        error_string += f"{i: 3d}: {during}\n"
        i += 1

        error_string += (
            f"   [ERROR: This locator was not found for operation: {action_name}]\n"
        )
        for line in after:
            error_string += f"{i: 3d}: {line}\n"
            i += 1

        axtree = filter_out_of_view_nodes(
            await capture_accessibility_tree(locator.page)
        )
        if axtree is None:
            await aprint("filter_out_of_view_nodes returned None for some reason.")
            raise exception
        mcq_string, mcq_choices = serialize_accessibility_tree(
            axtree,
            add_mcq=True,
            root_locator=locator.page.get_by_role("document"),
        )
        recovery_instructions = f"""
We were trying to execute a function but there was an error:
<error>
{error_string}
</error>

{axtree_intro}

Here is the webpage accessibility tree:
<tree>
{mcq_string}
</tree>

Please select the intended element (as the letter of the option). Additionally, write an expression that represents the correct locator (e.g. `page.locator("button").first()`). You can use the local variables. If you think there is no element
on the page that represents the intended element, you can write `None`.
""".strip()

        locator_code = ""
        past_attempts = []
        prompt_messages = [
            {"role": "system", "content": "You are interacting with a website."},
            {"role": "user", "content": recovery_instructions},
        ]
        R: RecoveryResult = {
            "action_name": action_name,
            "filename": filename,
            "lineno": lineno,
            "recovery_instructions": recovery_instructions,
            "attempts": [],
            "outcome": "fail",
            "exception": {"type": type(exception).__name__, "message": str(exception)},
            "debug": {
                "error_function_name": error_function_name,
                "error_function_start_line": error_function_start_line,
                "error_function_end_line": error_function_end_line,
                "error_function_offset_line": error_function_offset_line,
                "error_function_source": source,
            },
        }
        recovery_results.append(R)
        for attempt_ in range(5):
            if len(past_attempts) > 0:
                print(past_attempts[-1])
                (choice, locator_code, error) = past_attempts[-1]
                prompt_messages.append(
                    {
                        "role": "assistant",
                        "content": f"""
Choice: {choice}
Locator: {locator_code}
""".strip(),
                    }
                )
                prompt_messages.append(
                    {
                        "role": "user",
                        "content": "Your response failed. Here is an error message: "
                        + error,
                    }
                )

            result = await recovery_lm(
                prompt_messages,
                json_schema=J.struct(
                    step_by_step_reasoning=J.string(),
                    choice=J.string(),
                    locator_code=J.string(),
                ),
            )

            # Backtest the intended locator.
            locator_code: str = result["locator_code"].strip(" `")
            if locator_code.endswith("first()"):
                locator_code = locator_code[:-2]
            choice: str = result["choice"]

            R["attempts"].append(
                {
                    "choice": choice,
                    "locator_code": locator_code,
                    "error": "",
                }
            )

            if choice.lower().startswith("none"):
                await aprint("No relevant choice found for this locator.")

                R["attempts"][-1][
                    "error"
                ] = "No relevant choice found for this locator."
                break

            # Check whether the locator matches the target element.
            target_element = result["choice"].strip("[]")
            if target_element not in mcq_choices:
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"`choice` ({repr(target_element)}) must be a multiple-choice letter (e.g. 'A' alone)",
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue

            if msg := _is_not_ok_locator_expression(locator_code):
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"The locator code must be of the format `page.get_by_...()`. Don't use `page.locator(...)`. Instead use get_by_role(role, name=...) and filter(has_text=...). Message: "
                        + msg,
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue

            # Check if the generated locator attempts to perform an action.
            if any(
                "." + possible_action + "(" in locator_code
                for possible_action in [
                    "click",
                    "type",
                    "fill",
                    "hover",
                    "wait_for",
                    "select_option",
                ]
            ):
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"The locator code must not contain any actions (e.g. .click, .type, .fill, .hover, .select_option); you should only provide the locator (which is a Locator object, that the action is called upon).",
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue

            try:
                locator = eval(locator_code, None, locals_)
            except TypeError as _e:
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"Could not evaluate the locator code (TypeError): {str(_e)}",
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue
            except Exception as _e:
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"Could not evaluate the locator code: {str(_e)}",
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue

            if type(locator) != Locator:
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"The locator code must return a Locator object.",
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue

            count = await locator.count()
            if count != 1:
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"The locator must match exactly one element. Found {count} elements.",
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue

            _id, mcq_locator = mcq_choices[target_element]

            assert mcq_locator is not None, "mcq_locator must not be None."

            await mcq_locator.evaluate("L => window.__mcq_locator = L")
            match_check_result = await locator.evaluate(
                "L => ({is_match: (window.__mcq_locator == L), mcq_locator_result: window.__mcq_locator.toString(), code_locator_result: L.toString()})"
            )

            if not match_check_result["is_match"]:
                past_attempts.append(
                    (
                        choice,
                        locator_code,
                        f"The locator {locator_code} did not match the target element {result['choice']}",
                    )
                )
                R["attempts"][-1]["error"] = past_attempts[-1][2]
                continue

            # We passed all checks, the locator is probably OK.
            R["outcome"] = "success"
            await aprint("Created improved locator:", locator_code)
            if action_name == "wait_for_selector":
                action_name = "wait_for"

            if not hasattr(locator, action_name):
                await aprint(
                    "Locator does not have the attribute:",
                    action_name,
                    type(locator).__name__,
                )
                raise exception
            return await getattr(locator, action_name)(*locator_args, **locator_kwargs)

        await aprint("Could not find a suitable locator.")

        raise exception

    return handle_locator_error


async def test_out():
    apply_patches()
    async with async_playwright() as p:
        browser = await make_browser(p, "https://www.google.com")
        await browser.active_page.goto("/search?q=hello+world")
        await aprint(browser.active_page.url)


if __name__ == "__main__":
    asyncio.run(test_out())
