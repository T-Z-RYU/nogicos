import argparse
from contextlib import nullcontext

import skillweaver.environment.playwright_regex_patch

skillweaver.environment.playwright_regex_patch.apply()

import asyncio
import json
import os
import traceback
from typing import Literal, Optional

import dotenv
from aioconsole import aprint
from playwright.async_api import async_playwright

import skillweaver.evaluation.get_access_tokens as get_access_tokens
from skillweaver.attempt_task import attempt_task
from skillweaver.containerization.containers import containers
from skillweaver.environment import State, apply_patches, make_browser
from skillweaver.evaluation.load_test_cases import (
    get_test_case_config_file_path_vwa,
    get_test_case_config_file_path_webarena,
)
from skillweaver.evaluation.vwa_evaluators import (
    evaluator_router as evaluator_router_vwa,
)
from skillweaver.evaluation.webarena_config import SITES, _resolve_start_url
from skillweaver.evaluation.webarena_evaluators import (
    evaluator_router as evaluator_router_webarena,
)
from skillweaver.evaluation.webarena_evaluators_with_debug_info import (
    evaluator_router as evaluator_router_debug_webarena,
)
from skillweaver.evaluation.webarena_login import login_subprocess
from skillweaver.knowledge_base.knowledge_base import KnowledgeBase, load_knowledge_base
from skillweaver.lm import LM
from skillweaver.openai_cua.attempt_task import attempt_task as attempt_task_cua
from skillweaver.util.perfmon import monitor

dotenv.load_dotenv()


def _attempt_login(container_hostnames):
    # attempt to login 3 times
    for _ in range(3):
        if storage_state_path := login_subprocess(container_hostnames):
            return storage_state_path

    raise Exception("Failed to login to the website after 3 attempts.")


async def run_test_case_with_webrover(
    playwright,
    start_url: str,
    storage_state_path: str,
    out_dir: str,
    lm: LM,
    task_string: str,
    knowledge_base: KnowledgeBase,
    time_limit: int,
    allow_recovery: bool,
    as_reference_only: bool,
    headless: bool,
):
    # Initialize browser.
    browser = await make_browser(
        playwright,
        start_url,
        storage_state_path,
        video_dir=out_dir + "/video",
        headless=headless,
    )

    if not headless:
        # Give time to resize the window
        await aprint("Starting in 10 seconds...")
        await asyncio.sleep(5.0)
        await aprint("Starting in 5 seconds...")
        await asyncio.sleep(5.0)
        await aprint("Starting now!")

    await browser.context.tracing.start(snapshots=True, screenshots=True)

    # Attempt the task.
    if lm.model == "computer-use-preview":
        function_retrieval_lm = LM("gpt-4o")
        (states, actions, outcome_type, outcome_value) = await attempt_task_cua(
            browser,
            agent_lm_name=lm.model,
            function_retrieval_lm=function_retrieval_lm,
            task={"type": "prod", "task": task_string},
            max_steps=time_limit,
            knowledge_base=knowledge_base,
            store_dir=out_dir,
            reasoning_effort="medium",
            auto_accept_safety_checks=True,
        )

        # Manually set the "terminate_with_result" attribute of the final action.
        # This is not stored anywhere, though. All states and actions will have already been persisted to the disk.
        actions[-1]["terminate_with_result"] = outcome_value or ""
    else:
        (states, actions) = await attempt_task(
            browser,
            lm,
            {"type": "prod", "task": task_string},
            time_limit,
            knowledge_base,
            out_dir,
            allow_recovery=allow_recovery,
            as_reference_only=as_reference_only,
        )  # type: ignore
        states: list[State]
        actions: list[dict]

    await browser.context.tracing.stop(path=f"{out_dir}/trace.zip")

    # Now, let's evaluate.
    page = browser.active_page

    if page not in browser.cdp_sessions:
        cdp_session = await browser.context.new_cdp_session(page)
    else:
        cdp_session = browser.cdp_sessions[page]

    async def close_func():
        await browser.context.close()
        await browser.close()

    return (states, actions, page, cdp_session, close_func)


def evaluate_single_task(
    task_id: int,
    out_dir: str,
    lm_name: str,
    set_name: Literal[
        "webarena",
        "vwa_reddit",
        "vwa_classifieds",
        "vwa_shopping",
    ] = "webarena",
    knowledge_base_path_prefix: Optional[str] = None,
    temperature: float = 0.3,
    allow_recovery: bool = False,
    enable_unverified: bool = False,
    as_reference_only: bool = False,
    disable_tool_filter: bool = False,
    use_debugger_eval: bool = True,
    time_limit: int = 10,
    setup_backend_apis: bool = False,
    headless: bool = True,
):
    # Load metadata about the task.
    if set_name == "webarena":
        config_file_path = get_test_case_config_file_path_webarena(task_id)
        with open(config_file_path) as f:
            config = json.load(f)
        sites = config["sites"]
        task_string = config["intent"]
    else:
        config_file_path = get_test_case_config_file_path_vwa(set_name[4:], task_id)  # type: ignore
        with open(config_file_path) as f:
            config = json.load(f)
        sites = config["sites"]
        task_string = config["intent"]

    if knowledge_base_path_prefix is not None:
        knowledge_base = load_knowledge_base(knowledge_base_path_prefix)
    else:
        knowledge_base = KnowledgeBase()

    knowledge_base.hide_unverified = not enable_unverified

    # Create output folder.
    os.makedirs(out_dir, exist_ok=True)
    with open(out_dir + "/eval_info.json", "w") as f:
        json.dump(
            {
                "test_case_config": config,
                "set_name": set_name,
                "task_id": task_id,
                "knowledge_base_path_prefix": knowledge_base_path_prefix,
                "time_limit": time_limit,
                "use_debugger_eval": use_debugger_eval,
                "lm_name": lm_name,
                "allow_recovery": allow_recovery,
                "enable_unverified": enable_unverified,
                "as_reference_only": as_reference_only,
                "disable_tool_filter": disable_tool_filter,
            },
            f,
        )

    # Apply Playwright patches.
    apply_patches()

    lm = LM(lm_name, default_kwargs={"temperature": temperature})

    # Run asynchronous code with a separate async function.
    async def inner():
        try:
            use_manual_containers = (
                os.getenv("CONTAINER_SETUP", "auto").lower() == "manual"
            )
            async with (
                containers(sites) if not use_manual_containers else nullcontext({})
            ) as container_hostnames:
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
                    container_hostnames = {
                        # Convention in our code is that there is no http:// in container_hostnames.
                        k: SITES[k.split(":")[0].upper()][7:]
                        for k in sites
                    }

                await aprint("container_hostnames:", container_hostnames)
                await aprint("sites:", sites)
                await aprint("SITES:", SITES)

                # Set up environment variables needed by Beyond Browsing.
                if setup_backend_apis:
                    # Hard-coded from `API-Based-Agent/evaluation/webarena/utils.py`
                    # Split so that we can commit to GitHub. This access token is only for the Docker container.
                    os.environ["GITLAB_TOKEN"] = "glp" + "at-KygcYjwtD2JfA6wU4wBd"
                    os.environ["WA_GITLAB_API"] = SITES["GITLAB"] + "/api/v4"
                    os.environ["WA_REDDIT"] = SITES["REDDIT"]
                    # TODO: Add NOMINATIM_URL and OSRM_ROUTE_URL. (or, note to README that they must be set manually).

                    used_sites = {site.split(":")[0].upper() for site in sites}

                    if "SHOPPING" in used_sites:
                        os.environ["WA_SHOPPING_API"] = SITES["SHOPPING"]
                        os.environ["SHOPPING_ADMIN_TOKEN"] = (
                            get_access_tokens.get_shopping_admin_auth_token()
                        )
                    if "SHOPPING_ADMIN" in used_sites:
                        # NOTE(Michael): SHOPPING_ADMIN uses the same environment variable as SHOPPING. This is how the APIs for Beyond Browsing are set up. This is OK because they are never hosted at the same time.
                        # Must get rid of the "/admin" at the end of the address, though.
                        os.environ["WA_SHOPPING_API"] = SITES["SHOPPING_ADMIN"][
                            : -len("/admin")
                        ]
                        os.environ["SHOPPING_ADMIN_TOKEN"] = (
                            get_access_tokens.get_shopping_admin_admin_auth_token()
                        )
                    if "MAP" in used_sites:
                        assert (
                            "NOMINATIM_URL" in os.environ
                        ), "NOMINATIM_URL must be set in the environment variables to evaluate on map with setup_backend_apis=True."
                        assert (
                            "OSRM_ROUTE_URL" in os.environ
                        ), "OSRM_ROUTE_URL must be set in the environment variables to evaluate on map with setup_backend_apis=True."

                storage_state_path = _attempt_login(container_hostnames)
                start_url = _resolve_start_url(config["start_url"])

                async with async_playwright() as playwright:
                    states, actions, page, cdp_session, close_func = (
                        await run_test_case_with_webrover(
                            playwright,
                            start_url,
                            storage_state_path,
                            out_dir,
                            lm,
                            task_string,
                            knowledge_base,
                            time_limit,
                            allow_recovery,
                            as_reference_only,
                            headless,
                        )
                    )

                    if set_name == "webarena":
                        if use_debugger_eval:
                            evaluator = evaluator_router_debug_webarena(
                                config_file_path
                            )
                            result = await evaluator(
                                (states, actions),  # type: ignore
                                config_file_path,
                                page,
                                cdp_session,
                            )
                        else:
                            evaluator = evaluator_router_webarena(config_file_path)
                            result = {
                                "score": await evaluator(
                                    (states, actions),  # type: ignore
                                    config_file_path,
                                    page,
                                    cdp_session,
                                ),
                                "checks": [],
                            }
                    else:
                        evaluator = evaluator_router_vwa(config_file_path)
                        result = {
                            "score": await evaluator(
                                (states, actions),  # type: ignore
                                config_file_path,
                                page,
                            ),
                            "checks": [],
                        }

                    await close_func()

                    with open(out_dir + "/eval.json", "w") as f:
                        json.dump(result, f)

                    # Store performance monitoring result.
                    with open(f"{out_dir}/perfmon.json", "w") as f:
                        json.dump(monitor.as_dict(), f)
        except Exception as e:
            exception_str = traceback.format_exc()
            await aprint("Error occurred:", e)
            await aprint(exception_str)

            with open(f"{out_dir}/error.txt", "w") as f:
                f.write(exception_str)

        finally:
            os._exit(0)

    asyncio.run(inner())


def main():
    parser = argparse.ArgumentParser(description="Evaluate a single task.")

    parser.add_argument("--task_id", type=int, help="Task ID", required=True)
    parser.add_argument("--out_dir", type=str, help="Output directory", required=True)
    parser.add_argument(
        "--lm_name", type=str, help="Language model name", default="gpt-4o"
    )

    parser.add_argument(
        "--knowledge_base_path_prefix",
        type=str,
        default=None,
        help="Path prefix for the knowledge base",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Temperature for the language model",
    )
    parser.add_argument(
        "--allow_recovery", action="store_true", help="Allow recovery if the task fails"
    )
    parser.add_argument(
        "--enable_unverified",
        action="store_true",
        help="Enable unverified knowledge base entries",
    )
    parser.add_argument(
        "--as_reference_only",
        action="store_true",
        help="Use the task as a reference only",
    )
    parser.add_argument(
        "--disable_tool_filter", action="store_true", help="Disable tool filtering"
    )
    parser.add_argument(
        "--use_debugger_eval",
        action="store_true",
        default=True,
        help="Use debugger-based evaluation",
    )
    parser.add_argument(
        "--time_limit", type=int, default=10, help="Time limit for the task"
    )
    parser.add_argument(
        "--set_name",
        type=str,
        default="webarena",
        help="Name of the task set. Must be one of 'webarena', 'vwa_reddit', 'vwa_classifieds', 'vwa_shopping'.",
    )
    parser.add_argument(
        "--setup_backend_apis",
        action="store_true",
        help="Creates requests for access tokens for use with backend APIs (default: False) (only used with Beyond Browsing)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Disables 'headless' mode for browser (default: False)",
    )

    args = parser.parse_args()

    assert args.set_name in [
        "webarena",
        "vwa_reddit",
        "vwa_classifieds",
        "vwa_shopping",
    ], f"Invalid set name: {args.set_name}. Must be one of 'webarena', 'vwa_reddit', 'vwa_classifieds', 'vwa_shopping'."
    headless = not args.headed

    evaluate_single_task(
        args.task_id,
        args.out_dir,
        args.lm_name,
        args.set_name,
        args.knowledge_base_path_prefix,
        args.temperature,
        args.allow_recovery,
        args.enable_unverified,
        args.as_reference_only,
        args.disable_tool_filter,
        args.use_debugger_eval,
        args.time_limit,
        args.setup_backend_apis,
        headless,
    )


if __name__ == "__main__":
    main()
