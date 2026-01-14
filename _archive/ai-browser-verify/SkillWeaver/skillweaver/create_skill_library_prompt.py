import json
from skillweaver.knowledge_base.knowledge_base import Function, KnowledgeBase
from skillweaver.lm import LM


def get_task_string(task: dict):
    match task["type"]:
        case "test":
            return f"Test {task['function_name']} with {json.dumps(task['function_args'])}. If you are not at a screen where you can call the function, get there first."
        case "explore":
            return task["task"]
        case "prod":
            return task["task"]

    raise ValueError(f"Unknown task type: {task['type']}")


async def create_skill_library_prompt(
    task: dict,
    knowledge_base: KnowledgeBase,
    lm: LM,
    as_reference_only: bool,
    enable_retrieval_module_for_exploration: bool,
) -> tuple[list[Function], str, str]:
    task_string = get_task_string(task)

    if (
        task["type"] in ["test", "explore"] and enable_retrieval_module_for_exploration
    ) or task["type"] == "prod":
        return await knowledge_base.retrieve(task_string, lm)

    if task["type"] == "test":
        fns, fns_string = knowledge_base.get_functions_string(
            "code" if as_reference_only else "pretty",
            only_verified=True,
            extra_functions=[task["function_name"]],
        )
        return fns, fns_string, "verified"
    else:
        fns, fns_string = knowledge_base.get_functions_string(
            "code" if as_reference_only else "pretty"
        )
        return fns, fns_string, "all_for_explore"
