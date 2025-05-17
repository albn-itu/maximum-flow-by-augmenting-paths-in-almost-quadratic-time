from collections import defaultdict
import pathlib
import sys
import json
from typing import cast
import numpy as np
from preprocess import (
    BenchmarkData,
    BenchmarkResult,
    ProcessedKey,
    ProcessedRunList,
    preprocess,
)


type BenchmarkGroups = dict[str, dict[str, list[BenchmarkResult]]]

work_dir = pathlib.Path(__file__).parent.resolve()


def group_by(data: ProcessedRunList, key: str) -> dict[ProcessedKey, ProcessedRunList]:
    grouped: dict[ProcessedKey, ProcessedRunList] = defaultdict(list)
    for run in data:
        grouped[run[key]].append(run)
    return grouped


def no_correct_flow(data: ProcessedRunList) -> ProcessedRunList:
    return [
        run for run in data if run["function_name"] != "test_correct_flow_algorithms"
    ]


def find_in_h6(
    h6_data: ProcessedRunList,
    metric: str,
    class_name: str,
    param_id: str,
    function_name: str,
) -> float:
    for run in h6_data:
        if (
            run["class_name"] == class_name
            and run["param_id"] == param_id
            and run["function_name"] == function_name
        ):
            return cast(float, run[metric])
    return 0.0


def cmp_weight_functions(h9_data: ProcessedRunList, h6_data: ProcessedRunList):
    metrics: list[str] = [
        # "avg_updates",
        "average_w_length",
        "duration_s",
        "marked_admissible",
        "marked_dead",
        "marked_inadmissible",
        "before_kill.marked_admissible",
        "before_kill.marked_inadmissible",
        "before_kill.relabels",
        "relabels",
        # "iterations",
        # "edge_updates",
        # "highest_level",
    ]
    print("metric;class_name;function_name;param_id;h9;h6;percentage")
    for metric in metrics:
        prefixed_metric = f"blik.{metric}"

        by_class = group_by(h9_data, "class_name")
        for class_name, class_runs in by_class.items():
            if class_name is None:
                continue

            by_param_id = group_by(class_runs, "param_id")
            functions: dict[str, list[float]] = {
                name: []
                for name in set(
                    str(run["function_name"]) for run in no_correct_flow(class_runs)
                )
            }

            for param_id in sorted(list([str(id) for id in by_param_id.keys()])):
                param_runs = by_param_id[param_id]
                for run in no_correct_flow(param_runs):
                    function_name = str(run["function_name"])

                    h9_measurement = cast(float, run[prefixed_metric])
                    h6_measurement = find_in_h6(
                        h6_data,
                        prefixed_metric,
                        cast(str, class_name),
                        param_id,
                        function_name,
                    )

                    diff_percentage = (
                        ((h9_measurement - h6_measurement) / h9_measurement) * 100
                        if h6_measurement != 0
                        else 0
                    )
                    print(
                        f"{metric};{class_name};{function_name};{param_id};{h9_measurement:.2f};{h6_measurement:.2f};{diff_percentage:.2f}%"
                    )


def load_data(file_path: str) -> BenchmarkData:
    with open(file_path, "r") as f:
        data: BenchmarkData = json.load(f)
    return data


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: uv run comparer.py <path_to_9h_bench_file> <path_to_6h_bench_file>"
        )
        exit(1)

    h9_data = preprocess(load_data(sys.argv[1]))
    h6_data = preprocess(load_data(sys.argv[2]))

    cmp_weight_functions(h9_data, h6_data)
