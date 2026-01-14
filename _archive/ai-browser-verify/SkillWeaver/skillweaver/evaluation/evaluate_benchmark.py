# -*- coding: utf-8 -*-
import json
import os
import subprocess
from multiprocessing import Pool
from typing import Annotated, Literal

import click
import tqdm
import typer
from pydantic import BaseModel

from skillweaver.evaluation.load_test_cases import (
    load_test_cases_webarena,
    load_test_cases_vwa,
)
from skillweaver.knowledge_base.knowledge_base import load_knowledge_base


class SingleTaskEvaluationResult(BaseModel):
    cost: float | None
    status: Literal["success", "failure", "runtime_error", "none"]
    length: int


def _determine_single_task_evaluation_outcome(
    out_dir: str,
) -> SingleTaskEvaluationResult:
    result = SingleTaskEvaluationResult(cost=None, status="none", length=-1)

    if os.path.exists(out_dir + "/perfmon.json"):
        with open(out_dir + "/perfmon.json") as f:
            perfmon = json.load(f)

            result.cost = sum(row["price"] or 0.0 for row in perfmon["token_usages"])

    if os.path.exists(out_dir + "/eval.json"):
        with open(out_dir + "/eval.json") as f:
            result_ = json.load(f)
            success = bool(result_["score"])
            result.status = "success" if success else "failure"
    else:
        result.status = "runtime_error"

    i = 0
    while os.path.exists(f"{out_dir}/{i:03d}_action.json"):
        i += 1

    result.length = i

    return result


def _evaluate_task_subprocess(args: dict) -> SingleTaskEvaluationResult:
    out_dir = args["out_dir"]
    # Skip if the path already exists.
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        with open(out_dir + "/stdout.txt", "w") as fout:
            with open(out_dir + "/stderr.txt", "w") as ferr:
                subprocess.run(
                    [
                        "python3",
                        "-m",
                        "skillweaver.evaluation.evaluate_single_task",
                        *[
                            f"--{k}={v}" if not isinstance(v, bool) else f"--{k}"
                            for k, v in args.items()
                            if v is not None and (not isinstance(v, bool) or v)
                        ],
                    ],
                    stdout=fout,
                    stderr=ferr,
                )
    return _determine_single_task_evaluation_outcome(out_dir)


def evaluate_benchmark(
    site: Annotated[
        str,
        typer.Argument(
            click_type=click.Choice(
                ["reddit", "webarena", "map", "shopping", "shopping_admin", "gitlab"]
            )
        ),
    ],
    out_dir: str,
    time_limit: int = 10,
    knowledge_base_path_prefix: str | None = None,
    lm_name: str = "gpt-4o",
    pool_size: int = 8,
    use_debugger_eval: Annotated[
        bool,
        typer.Option(
            help="Whether to use the modified WebArena debugger which adds additional information about why a test case failed."
        ),
    ] = True,
    allow_recovery: bool = True,
    allow_unverified_apis: bool = False,
    selected_tasks: Annotated[
        str | None,
        typer.Option(
            help="Which tasks to run. If not provided, runs all tasks. If 'reduced_set' is provided, only one of each intent_template_id will be tested. If a comma-separated list of task IDs is provided (e.g., '1,2,3'), then those task_ids will be run."
        ),
    ] = None,
    set_name: Annotated[
        str,
        typer.Option(
            click_type=click.Choice(
                ["webarena", "vwa_reddit", "vwa_shopping", "vwa_classifieds"]
            ),
            help="The name of the test case set. Can either be WebArena, or any of the VisualWebArena site-specific evaluation sets (must be one of: 'webarena', 'vwa_reddit', 'vwa_shopping', or 'vwa_classifieds').",
        ),
    ] = "webarena",
    agent_type: Annotated[
        str,
        typer.Option(
            click_type=click.Choice(
                [
                    "skillweaver",
                    "webarena",
                ]
            ),
            help="The type of agent to use. Can be one of 'skillweaver' or 'webarena'. Defaults to 'skillweaver'.",
        ),
    ] = "skillweaver",
):
    print(
        "Running benchmark evaluation with parameters:", json.dumps(locals(), indent=2)
    )
    reduced_set = selected_tasks == "reduced_set"
    if set_name == "webarena":
        test_cases = load_test_cases_webarena()
    elif set_name == "vwa_reddit":
        test_cases = load_test_cases_vwa("reddit")
    elif set_name == "vwa_shopping":
        test_cases = load_test_cases_vwa("shopping")
    elif set_name == "vwa_classifieds":
        test_cases = load_test_cases_vwa("classifieds")

    if selected_tasks is not None and selected_tasks != "reduced_set":
        task_ids = [int(x) for x in selected_tasks.split(",")]
        test_cases = [tc for tc in test_cases if tc["task_id"] in task_ids]

    out_dir = os.path.join(out_dir, site)

    if site == "map" and not os.getenv("MAP_ADDR"):
        raise ValueError("MAP_ADDR environment variable must be set for the map site.")

    os.makedirs(out_dir, exist_ok=True)

    eval_info = {
        "site": site,
        "knowledge_base_path_prefix": knowledge_base_path_prefix,
        "time_limit": time_limit,
        "use_debugger_eval": use_debugger_eval,
        "lm_name": lm_name,
        "full_set": not reduced_set,
        "enable_unverified": allow_unverified_apis,
        "set_name": set_name,
        "agent_type": agent_type,
    }
    if os.path.exists(out_dir + "/eval_info.json"):
        with open(out_dir + "/eval_info.json", "r") as f:
            existing_eval_info = json.load(f)
            if existing_eval_info != eval_info:
                print("Current eval_info:", eval_info)
                raise ValueError(
                    "The evaluation info file already exists and does not match the current parameters. Please use a different output directory."
                )

    with open(out_dir + "/eval_info.json", "w") as f:
        json.dump(eval_info, f)

    # Copy the knowledge base into the correct folder.
    if knowledge_base_path_prefix is not None:
        # BUG print the path
        kb = load_knowledge_base(knowledge_base_path_prefix)
        kb.save(out_dir + "/kb")

        if len(kb.get_functions()) == 0:
            if allow_unverified_apis:
                raise ValueError("No APIs could be parsed from this knowledge base.")

            raise ValueError(
                "There are no unverified APIs in the knowledge base. Please pass --allow-unverified-apis if you wish to use this knowledge base without explicit verification."
            )

    seen_intent_ids = set()
    single_task_cmd_args = []

    for i in range(len(test_cases)):
        if test_cases[i]["sites"][0] == site and len(test_cases[i]["sites"]) == 1:
            intent_id = test_cases[i]["intent_template_id"]
            if reduced_set and intent_id in seen_intent_ids:
                continue

            seen_intent_ids.add(intent_id)
            single_task_cmd_args.append(
                {
                    "task_id": test_cases[i]["task_id"],
                    "out_dir": f"{out_dir}/task_{test_cases[i]['task_id']}",
                    "knowledge_base_path_prefix": knowledge_base_path_prefix,
                    "time_limit": time_limit,
                    "use_debugger_eval": use_debugger_eval,
                    "lm_name": lm_name,
                    "allow_recovery": allow_recovery,
                    "enable_unverified": allow_unverified_apis,
                    "set_name": set_name,
                    "agent_type": agent_type,
                }
            )

    # Create a progress bar.
    running_total = {
        "finished": 0,
        "cost": 0.0,
        "cost_available": 0,
        "success": 0,
        "fail": 0,
        "error": 0,
        "success_steps": 0,
    }

    # Run the tasks with a pool.
    with Pool(pool_size) as pool:
        with tqdm.tqdm(total=len(single_task_cmd_args)) as pbar:

            for result in pool.imap_unordered(
                _evaluate_task_subprocess, single_task_cmd_args
            ):
                running_total["finished"] += 1
                if result.cost is not None:
                    running_total["cost"] += result.cost
                    running_total["cost_available"] += 1

                match result.status:
                    case "success":
                        running_total["success"] += 1
                        running_total["success_steps"] += result.length
                    case "failure":
                        running_total["fail"] += 1
                    case _:
                        running_total["error"] += 1

                remaining = len(single_task_cmd_args) - running_total["finished"]
                string = "[EVAL] Evaluating.  {}/{};  {};  ${:.2f}  {:.2f} (n={}) (remaining={})".format(
                    running_total["success"],
                    running_total["fail"] + running_total["success"],
                    running_total["error"],
                    running_total["cost"],
                    (
                        running_total["success_steps"] / running_total["success"]
                        if running_total["success"] > 0
                        else 0
                    ),
                    running_total["cost_available"],
                    remaining,
                )
                pbar.update(1)
                pbar.set_postfix_str(string)

    return running_total


if __name__ == "__main__":
    typer.run(evaluate_benchmark)
