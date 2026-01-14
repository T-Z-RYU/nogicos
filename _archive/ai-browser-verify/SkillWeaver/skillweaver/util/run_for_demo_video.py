import os
import typer


def run(task_id: int, site: str, with_tools: bool = False):
    if with_tools:
        os.system(
            f"python -m skillweaver.evaluation.evaluate_single_task --headed --task_id {task_id} --out_dir logs/{task_id}_kb --enable_unverified --knowledge_base_path_prefix skillweaver/knowledge_base/collected/{site}_160"
        )
    else:
        os.system(
            f"python -m skillweaver.evaluation.evaluate_single_task --headed --task_id {task_id} --out_dir logs/{task_id}_no_kb --knowledge_base_path_prefix skillweaver/knowledge_base/collected/{site}_160"
        )


if __name__ == "__main__":
    typer.run(run)
