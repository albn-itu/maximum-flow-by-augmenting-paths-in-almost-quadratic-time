from collections import defaultdict
import pathlib
import sys
import json
from typing import Any, cast
import matplotlib.pyplot as plt
import numpy as np
from preprocess import (
    BenchmarkData,
    ProcessedKey,
    ProcessedRunList,
    preprocess,
)


type BenchmarkGroups = dict[str, dict[str, list[BenchmarkResult]]]

work_dir = pathlib.Path(__file__).parent.resolve()


def make_out_path(name: str, format: str):
    out_dir = work_dir / "output" / format
    return out_dir / f"{name}.{format}"


def save_plot(name: str):
    format = "png"

    if not (work_dir / "output").exists():
        (work_dir / "output").mkdir()
    if not (work_dir / "output" / format).exists():
        (work_dir / "output" / format).mkdir()

    plt.savefig(make_out_path(name, format), format=format, bbox_inches="tight")


def group_by(data: ProcessedRunList, key: str) -> dict[ProcessedKey, ProcessedRunList]:
    grouped: dict[ProcessedKey, ProcessedRunList] = defaultdict(list)
    for run in data:
        grouped[run[key]].append(run)
    return grouped


def no_correct_flow(data: ProcessedRunList) -> ProcessedRunList:
    return [
        run for run in data if run["function_name"] != "test_correct_flow_algorithms"
    ]


def cmp_weight_functions(data: ProcessedRunList):
    metrics = [
        "avg_updates",
        "average_w_length",
        "duration_s",
        "marked_admissible",
        "marked_dead",
        "marked_inadmissible",
        "relabels",
        "iterations",
        "edge_updates",
        "highest_level",
        "before_kill.marked_admissible",
        "before_kill.marked_inadmissible",
        "before_kill.relabels",
    ]
    for metric in metrics:
        prefixed_metric = f"blik.{metric}"

        by_class = group_by(data, "class_name")
        for class_name, class_runs in by_class.items():
            if class_name is None:
                continue

            by_param_id = group_by(class_runs, "param_id")
            functions: dict[str, list[int]] = {
                name: []
                for name in set(
                    str(run["function_name"]) for run in no_correct_flow(class_runs)
                )
            }

            for param_id in sorted(list([str(id) for id in by_param_id.keys()])):
                param_runs = by_param_id[param_id]
                for run in no_correct_flow(param_runs):
                    function_name = str(run["function_name"])
                    functions[function_name].append(cast(int, run[prefixed_metric]))

            x_axis: list[str] = []
            for id in by_param_id.keys():
                thing = by_param_id[id][-1]
                x_axis.append(
                    f"{thing['instance.n']} {thing['instance.m']} {thing['instance.h']}"
                )

            x = np.arange(len(x_axis))
            width = 0.25
            multiplier = 0

            fig, ax = plt.subplots(layout="constrained")

            for function_name, measurement in functions.items():
                offset = width * multiplier
                rects = ax.bar(x + offset, measurement, width, label=function_name)
                # ax.bar_label(rects, padding=3)
                multiplier += 1

            ax.set_title(f"{metric} for {class_name}")
            ax.set_ylabel(metric)
            ax.set_xticks(x + width, x_axis, rotation=90)
            ax.legend()
            save_plot(f"cmp_{metric}_{class_name}")


def load_data(file_path: str) -> BenchmarkData:
    with open(file_path, "r") as f:
        data: BenchmarkData = json.load(f)
    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run plotter.py <path_to_bench_file>")
        exit(1)

    bench_file = sys.argv[1]
    data = load_data(bench_file)

    preprocessed_data = preprocess(data)
    cmp_weight_functions(preprocessed_data)
