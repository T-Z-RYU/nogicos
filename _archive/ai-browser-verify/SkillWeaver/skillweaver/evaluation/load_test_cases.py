import json
import os
from typing import Literal


def _split_test_cases(test_cases: list, out_dir_name: str = "split"):
    os.makedirs(
        os.path.join(os.path.dirname(__file__), "test_cases", out_dir_name),
        exist_ok=True,
    )
    for test_case in test_cases:
        with open(
            os.path.join(
                os.path.dirname(__file__),
                "test_cases",
                out_dir_name,
                f"{test_case['task_id']}.json",
            ),
            "w",
        ) as f:
            json.dump(test_case, f, indent=2)


def load_test_cases_webarena(selected_tasks: list[int] | None = None):
    test_case_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "test_cases/test.webarena.raw.json")
    )
    with open(test_case_path) as f:
        test_cases = json.load(f)

    if selected_tasks is not None:
        test_cases = [test_cases[i] for i in selected_tasks if i < len(test_cases)]

    if not os.path.exists(os.path.dirname(test_case_path) + "/split/0.json"):
        _split_test_cases(test_cases, "split")

    return test_cases


def get_test_case_config_file_path_webarena(task_id: int):
    test_case_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"test_cases/split/{task_id}.json")
    )
    if not os.path.exists(test_case_path):
        # Trigger splitting of test cases
        load_test_cases_webarena()

    return test_case_path


def get_test_case_config_file_path_vwa(
    subset: Literal["classifieds", "reddit", "shopping"], task_id: int
):
    test_case_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), f"test_cases/split_vwa_{subset}/{task_id}.json"
        )
    )
    if not os.path.exists(test_case_path):
        # Trigger splitting of test cases
        load_test_cases_vwa(subset)

    return test_case_path


def load_test_cases_vwa(
    subset: Literal["classifieds", "reddit", "shopping"],
    selected_tasks: list[int] | None = None,
):
    test_case_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "test_cases", f"test.vwa_{subset}.raw.json"
        )
    )
    with open(test_case_path) as f:
        test_cases = json.load(f)

    if selected_tasks is not None:
        test_cases = [test_cases[i] for i in selected_tasks if i < len(test_cases)]

    if not os.path.exists(
        os.path.join(os.path.dirname(test_case_path), f"split_vwa_{subset}", "0.json")
    ):
        _split_test_cases(test_cases, f"split_vwa_{subset}")

    return test_cases
