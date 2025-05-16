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


def weight_function_to_color(function_name: str) -> str:
    if function_name == "test_correct_flow_algorithms":
        return "black"
    if function_name == "test_weighted_push_relabel":
        return "tab:blue"
    if function_name == "test_weighted_push_relabel_with_flow_weight":
        return "tab:green"
    if function_name == "test_weighted_push_relabel_with_expander_hierarchy_weights":
        return "tab:orange"
    if function_name == "test_weighted_push_relabel_with_topsort":
        return "tab:red"
    if function_name == "test_weighted_push_relabel_with_n_weight":
        return "tab:gray"
    if function_name == "test_weighted_push_relabel_with_2_weight":
        return "tab:purple"
    raise ValueError(f"Unknown function name: {function_name}")


def cmp_weight_functions(data: ProcessedRunList):
    metrics: list[tuple[str, str | None]] = [
        ("avg_updates", None),
        ("average_w_length", None),
        ("duration_s", "instance.n"),
        ("marked_admissible", "instance.m"),
        ("marked_dead", "instance.n"),
        ("marked_inadmissible", "instance.m"),
        ("before_kill.marked_admissible", "instance.m"),
        ("before_kill.marked_inadmissible", "instance.m"),
        ("before_kill.relabels", "instance.n"),
        ("relabels", "instance.n"),
        ("iterations", "instance.n"),
        ("edge_updates", "instance.m"),
        ("highest_level", "instance.n"),
    ]
    for metric, normalization_parameter in metrics:
        prefixed_metric = f"blik.{metric}"

        by_class = group_by(data, "class_name")
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

                    measurement = cast(float, run[prefixed_metric])
                    if normalization_parameter is not None:
                        measurement /= cast(float, run[normalization_parameter])
                    functions[function_name].append(measurement)

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

                real_name = function_name.replace("test_", "")
                if real_name == "weighted_push_relabel":
                    real_name = "No weights"
                else:
                    real_name = (
                        real_name.replace("weighted_push_relabel_", "")
                        .replace("_", " ")
                        .title()
                    )

                rects = ax.bar(
                    x + offset,
                    measurement,
                    width,
                    label=real_name,
                    color=weight_function_to_color(function_name),
                )
                # ax.bar_label(rects, padding=3)
                multiplier += 1

            title = f"{metric} for {class_name}"
            if normalization_parameter is not None:
                title += f" normalized by {normalization_parameter}"
            ax.set_title(title)
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
