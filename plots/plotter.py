from collections import defaultdict
import pathlib
import sys
import json
from typing import Any, cast
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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

    plt.savefig(make_out_path(name, format),
                format=format, bbox_inches="tight",
                dpi=300)


def group_by(data: ProcessedRunList, key: str) -> dict[ProcessedKey, ProcessedRunList]:
    grouped: dict[ProcessedKey, ProcessedRunList] = defaultdict(list)
    for run in data:
        grouped[run[key]].append(run)
    return grouped


def average_by(data: ProcessedRunList, key: str) -> float:
    total = 0.0
    count = 0
    for run in data:
        total += cast(float, run[key])
        count += 1
    return total / count if count > 0 else 0.0


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
        ("state_change.marked_admissible", "instance.m"),
        ("state_change.marked_inadmissible", "instance.m"),
        ("state_change.state_changes", "instance.m"),
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
                        measurement /= cast(float,
                                            run[normalization_parameter])
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
            fig.set_size_inches((20, 6))

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


def plot_with_respect_to_graph_size(data: ProcessedRunList):
    by_fn = dict()

    min_n = 8
    min_m = 8

    for fn, fn_runs in group_by(data, "function_name").items():
        x_m_series = {}
        for n, n_runs in sorted(group_by(fn_runs, "instance.n").items(), key=lambda x: x[0], reverse=True):
            if n < min_n:
                continue

            id = n
            x_m_series[id] = {
                "label": f"$n={int(n)}$",
                "line": [],
            }
            for m, runs in sorted(group_by(n_runs, "instance.m").items(), key=lambda x: x[0]):
                val = int(average_by(runs, "blik.marked_admissible") + average_by(runs, "blik.marked_inadmissible"))
                x_m_series[id]["line"].append((m/n, val))

        x_n_series = {}
        for m, m_runs in sorted(group_by(fn_runs, "instance.m").items(), key=lambda x: x[0], reverse=True):
            if m < min_m:
                continue

            id = m
            x_n_series[id] = {
                "label": f"$m={int(m)}$",
                "line": [],
            }
            for n, runs in sorted(group_by(m_runs, "instance.n").items(), key=lambda x: x[0]):
                val = int(average_by(runs, "blik.marked_admissible") + average_by(runs, "blik.marked_inadmissible"))
                x_n_series[id]["line"].append((n, val))

        by_fn[fn] = {
            "x=m": x_m_series,
            "x=n": x_n_series,
        }

    def plot_series_data(fn: str, series: str):
        plots = by_fn[fn]
        # print(json.dumps(series, indent=2))

        fig, ax = plt.subplots(layout="constrained")
        fig.set_size_inches((8, 5))
        for id, item in plots[series].items():
            xs, ys = zip(*item["line"])

            z = np.polyfit(xs, ys, 2)
            p = np.poly1d(z)

            yhat = p(xs)                         # or [p(z) for z in x]
            ybar = np.sum(ys)/len(ys)          # or sum(y)/len(y)
            ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
            sstot = np.sum((np.array(ys) - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
            r2 = ssreg / sstot

            fit_eq = f"$R^2={r2:.3f}$: ${z[0]:.2f}x^2 + {z[1]:.2f}x + c$"

            l = ax.plot(xs, ys, label=item["label"] + f" ({fit_eq})", marker="o", linestyle='None')

            fx = np.linspace(min(xs), max(xs), 100)
            ax.plot(fx, p(fx), linestyle='--', alpha=0.5, color=l[0].get_color())

        # Put a legend to the right of the current axis
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        return fig, ax

    for fn in by_fn:
        name = fn.replace("test_", "").replace("_", " ").title()

        fig, ax = plot_series_data(fn, "x=m")
        ax.set_xlabel(r"Edge scale factor ($m = x \cdot n$)")
        ax.set_ylabel("Number of times edges change status")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log", base=2)
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
        ax.set_title(f"Number of status changes for different graph sizes ({name})", loc="left")
        ax.grid(True)
        save_plot(f"graph_size_xm_{fn}")

        fig, ax = plot_series_data(fn, "x=n")
        ax.set_xlabel(r"$n$")
        ax.set_ylabel("Number of times edges change status")
        ax.set_xscale("log", base=2)
        ax.set_yscale("log", base=2)
        ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
        ax.set_title(f"Number of status changes for different graph sizes ({name})", loc="left")
        ax.grid(True)
        save_plot(f"graph_size_xn_{fn}")

        # plt.show()

    # fig, ax = plt.subplots(layout="constrained")
    # for m in ms:
    #     row = []
    #     for n in ns:
    #         runs = keep[n][m]
    #         val = int(average_by(runs, "blik.marked_admissible") + average_by(runs, "blik.marked_inadmissible"))
    #         row.append(val)
    #
    #     ax.plot(ns, row, label=f"$m={int(m)}$", marker="o")
    #     table.append((n, row))
    #
    # ax.legend()
    # ax.set_xlabel("$n$")
    # ax.set_ylabel("adm + inadm")
    # ax.set_title("Number of status changes for different graph sizes")
    # save_plot("graph_size_xn")


    # for r in table:
    #     print(r)
    #
    # print("\\begin{tabular}{|c|" + "|".join(["c"] * len(ms)) + "|}")
    # print("\\hline")
    # print("& " + " & ".join(f"$m={int(m)}$" for m in ms) + "\\\\")
    # print("\\hline")
    # for n, row in table[1:]:
    #     print(f"$n={int(n)}$ &", " & ".join(f"{x:,}" for x in row) + "\\\\")
    #     print("\\hline")
    # print("\\end{tabular}")

    # for n in ns:

    # print(\n'.join(str(x) for x in sorted(sizes)))
    # print(json.dumps(by_fn, indent=2)


def load_data(file_path: str) -> BenchmarkData:
    with open(file_path, "r") as f:
        data: BenchmarkData = json.load(f)

    # for k in list(data.keys()):
    #     if "with_n_weight" in k:
    #         _ = data.pop(k)

    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run plotter.py <path_to_bench_file>")
        exit(1)

    bench_file = sys.argv[1]
    data = load_data(bench_file)

    preprocessed_data = preprocess(data)
    # plot_with_respect_to_graph_size(no_correct_flow(preprocessed_data))
    cmp_weight_functions(preprocessed_data)
