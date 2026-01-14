import pandas as pd
import typer
import yaml

from skillweaver.evaluation.evaluate_benchmark import (
    evaluate_benchmark as evaluate_benchmark,
)


def run_experiment(experiment_filename: str, select_configs: str):
    if ".yaml" not in experiment_filename:
        experiment_filename += ".yaml"

    experiments: dict = yaml.safe_load(
        open(f"webrover/experiments/{experiment_filename}")
    )  # type: ignore
    shared_config = experiments.pop("__shared__", {})

    if select_configs:
        experiment_names = select_configs.split(",")
    else:
        experiment_names = list(experiments.keys())

    df_data = []
    for experiment_name in experiment_names:
        experiment = experiments[experiment_name]
        print("--- Running Experiment: " + experiment_name + " ---")
        print({**shared_config, **experiment})
        result = evaluate_benchmark(**shared_config, **experiment)
        df_data.append(
            {
                "name": experiment_name,
                **result,
                "s_pct": f"{result['success']/result['cost_available']*100:.1f}",
                "success_steps_avg": f"{result['success_steps'] / result['success']:.2f}",
            }
        )

    print(pd.DataFrame(df_data))
    print("---")
    print(pd.DataFrame(df_data).sort_values("name"))


if __name__ == "__main__":
    typer.run(run_experiment)
