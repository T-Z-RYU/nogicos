try:
    from browser_use import Agent, Browser, BrowserConfig, BrowserContextConfig
except ImportError:
    print("Please install browser-use with `pip install browser-use`.")
    exit(1)

import dotenv

from skillweaver.environment.patches import apply_patches

apply_patches()

dotenv.load_dotenv()
import asyncio
import json
import os
import sys
import traceback
from contextlib import nullcontext
from datetime import datetime
from typing import Optional

import typer
from aioconsole import aprint
from langchain_openai import AzureChatOpenAI

from skillweaver.containerization.containers import containers
from skillweaver.evaluation.webarena_config import SITES
from skillweaver.evaluation.webarena_login import login_subprocess
from skillweaver.knowledge_base.knowledge_base import KnowledgeBase, load_knowledge_base
from skillweaver.lm import LM


def cli(
    start_url: str,
    task: str,
    agent_lm_name: str = "gpt-4o",
    knowledge_base_path_prefix: Optional[str] = None,
    headless: bool = False,
):
    retrieval_lm_name = "gpt-4o"

    if knowledge_base_path_prefix is None:
        knowledge_base = KnowledgeBase()
    else:
        knowledge_base = load_knowledge_base(knowledge_base_path_prefix)
        knowledge_base.hide_unverified = False

    log_dir = os.path.join(
        "logs",
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_browser-use_" + agent_lm_name,
    )
    os.makedirs(log_dir)

    setup_site: str | None = None
    for site in SITES:
        start_string = f"__{site}__"
        if start_url.startswith(start_string):
            setup_site = site.lower()
            start_url = start_url[len(start_string) :]
            break

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
                assert storage_state_file is not None, "Login failed for site " + site
                # browser-use expects a file with *just* the cookies
                cookies_file = storage_state_file[:-5] + "_cookies.json"

                with open(storage_state_file) as f:
                    auth_data = json.load(f)

                with open(cookies_file, "w") as f:
                    json.dump(auth_data["cookies"], f)

                # Replace the start_url with the container hostname.
                start_url = SITES[setup_site.upper()] + start_url
                print("Start URL:", start_url)
            else:
                cookies_file = None

            (functions, _, _) = await knowledge_base.retrieve(
                task, LM(retrieval_lm_name)
            )
            function_names = [function["name"] for function in functions]
            await aprint("Functions retrieved:", function_names)
            controller = knowledge_base.get_browser_use_controller(
                function_names, debug=True
            )
            browser = Browser(
                config=BrowserConfig(
                    new_context_config=BrowserContextConfig(cookies_file=cookies_file),
                    headless=headless,
                )
            )
            agent = Agent(
                task=task,
                controller=controller,
                llm=AzureChatOpenAI(
                    model=agent_lm_name,
                    base_url=os.getenv("AZURE_OPENAI_gpt_4o_ENDPOINT"),
                    api_key=os.getenv("AZURE_OPENAI_gpt_4o_API_KEY"),  # type: ignore
                    api_version="2025-01-01-preview",  # this is from the API endpoint url
                ),
                save_conversation_path=log_dir,
                browser=browser,
                tool_calling_method="function_calling",
            )
            await agent.browser_context.navigate_to(start_url)
            await agent.run()

    try:
        asyncio.run(impl())
    except Exception as e:
        os.set_blocking(sys.stdout.fileno(), True)
        with open("traceback.txt", "w") as f:
            f.write(traceback.format_exc())
        print(traceback.format_exc())


if __name__ == "__main__":
    import typer

    typer.run(cli)
