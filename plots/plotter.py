from collections import defaultdict
import pathlib
import json
import sys
from typing import cast
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from .preprocess import (
    BenchmarkData,
    BenchmarkResult,
    ProcessedKey,
    ProcessedRun,
    ProcessedRunList,
    preprocess,
)
import re
import itertools

FUNCTIONS = {
    "test_weighted_push_relabel": {"name": "No weights", "color": "tab:blue"},
    "test_weighted_push_relabel_with_flow_weight": {
        "name": "Maximum flow weights",
        "color": "tab:green",
    },
    "test_weighted_push_relabel_with_expander_hierarchy_weights": {
        "name": "Expander hierarchy weights",
        "color": "tab:orange",
    },
    "test_weighted_push_relabel_with_topsort": {
        "name": "Topological order weights",
        "color": "tab:red",
    },
    "test_weighted_push_relabel_with_n_weight": {
        "name": "Weight $n$",
        "color": "tab:gray",
    },
    "test_weighted_push_relabel_with_2_weight": {
        "name": "Weight $2$",
        "color": "tab:purple",
    },
    "test_correct_flow_algorithms": {"name": "Correct flow", "color": "black"},
}

type BenchmarkGroups = dict[str, dict[str, list[BenchmarkResult]]]

work_dir = pathlib.Path(__file__).parent.resolve()


def make_out_path(name: str, format: str):
    out_dir = work_dir / "output" / format
    return out_dir / f"{name}.{format}"


def save_plot(name: str):
    format = "pdf"

    if not (work_dir / "output").exists():
        (work_dir / "output").mkdir()
    if not (work_dir / "output" / format).exists():
        (work_dir / "output" / format).mkdir()

    plt.savefig(
        make_out_path(name, format), format=format, bbox_inches="tight", dpi=150
    )


def group_by(data: ProcessedRunList, key: str) -> dict[ProcessedKey, ProcessedRunList]:
    grouped: dict[ProcessedKey, ProcessedRunList] = defaultdict(list)
    for run in data:
        grouped[run[key]].append(run)
    return grouped


def get_key(run: ProcessedRun, key: str) -> float:
    return cast(float, run[key])


def get_normalized_key(
    run: ProcessedRun, key: str, normalization_parameter: str | None
) -> float:
    if normalization_parameter is not None:
        return get_key(run, key) / get_key(run, normalization_parameter)
    return get_key(run, key)


def average_by(
    data: ProcessedRunList, key: str, normalization_parameter: str | None = None
) -> float:
    total = 0.0
    count = 0
    for run in data:
        total += get_normalized_key(run, key, normalization_parameter)
        count += 1
    return total / count if count > 0 else 0.0


def pretty_metric_name(name: str) -> str:
    if name == "state_change.state_changes":
        return "Admissibility changes per edge"
    if name == "edge_considerations":
        return "Avg. edge considerations"
    return name


def no_correct_flow(data: ProcessedRunList) -> ProcessedRunList:
    return [
        run for run in data if run["function_name"] != "test_correct_flow_algorithms"
    ]


def cmp_weight_functions(data: ProcessedRunList):
    metrics: list[tuple[str, str | None]] = [
        # ("avg_updates", None),
        # ("average_w_length", None),
        # ("duration_s", "instance.n"),
        # ("marked_admissible", "instance.m"),
        # ("marked_dead", "instance.n"),
        # ("marked_inadmissible", "instance.m"),
        # ("before_kill.marked_admissible", "instance.m"),
        # ("before_kill.marked_inadmissible", "instance.m"),
        # ("state_change.marked_admissible", "instance.m"),
        # ("state_change.marked_inadmissible", "instance.m"),
        ("state_change.state_changes", None),
        # ("before_kill.relabels", "instance.n"),
        # ("relabels", "instance.n"),
        # ("iterations", "instance.n"),
        # ("edge_updates", "instance.m"),
        # ("highest_level", "instance.n"),
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
                x_axis.append(f"n={thing['instance.n']}\nm={thing['instance.m']}")

            x = np.arange(len(x_axis))
            width = 0.25
            multiplier = 0

            fig, ax = plt.subplots(layout="constrained")
            fig.set_size_inches((20, 6))

            for function_name, measurement in functions.items():
                offset = width * multiplier

                real_name = FUNCTIONS[function_name]["name"]

                _ = ax.bar(
                    x + offset,
                    measurement,
                    width,
                    label=real_name,
                    color=FUNCTIONS[function_name]["color"],
                )
                # ax.bar_label(rects, padding=3)
                multiplier += 1

            title = f"{pretty_metric_name(metric)} for {class_name}"
            # if normalization_parameter is not None:
            #     title += f" normalized by {normalization_parameter}"
            ax.set_title(title)
            ax.set_ylabel(pretty_metric_name(metric))
            ax.set_xticks(x + width, x_axis)
            ax.legend()
            save_plot(f"cmp_{metric}_{class_name}")


def plot_with_respect_to_graph_size(data: ProcessedRunList):
    by_cn = dict()

    min_n = 8
    min_m, max_m = 100, 19000

    for class_name, class_runs in group_by(data, "class_name").items():
        by_fn = dict()
        for fn, fn_runs in group_by(class_runs, "function_name").items():
            x_m_series = {}
            for n, n_runs in sorted(
                group_by(fn_runs, "instance.n").items(),
                key=lambda x: x[0],
                reverse=True,
            ):
                if n < min_n:
                    continue

                id = n
                x_m_series[id] = {
                    "label": f"$n={int(n)}$",
                    "line": [],
                }
                for m, runs in sorted(
                    group_by(n_runs, "instance.m").items(), key=lambda x: x[0]
                ):
                    val = int(
                        average_by(runs, "blik.marked_admissible")
                        + average_by(runs, "blik.marked_inadmissible")
                    )
                    x_m_series[id]["line"].append((m / n, val / m))

            x_n_series = {}
            for m, m_runs in sorted(
                group_by(fn_runs, "instance.m").items(),
                key=lambda x: x[0],
                reverse=True,
            ):
                if m < min_m or m > max_m:
                    continue

                id = m
                x_n_series[id] = {
                    "label": f"$m={int(m)}$",
                    "line": [],
                }
                for n, runs in sorted(
                    group_by(m_runs, "instance.n").items(), key=lambda x: x[0]
                ):
                    val = int(
                        average_by(runs, "blik.marked_admissible")
                        + average_by(runs, "blik.marked_inadmissible")
                    )
                    x_n_series[id]["line"].append((n, val / m))

            by_fn[fn] = {
                "x=m": x_m_series,
                "x=n": x_n_series,
            }
        by_cn[class_name] = by_fn

    def plot_series_data(cn: str, fn: str, series: str):
        plots = by_cn[cn][fn]
        # print(json.dumps(series, indent=2))

        marker_styles = itertools.cycle([
            "o",  # circle
            "s",  # square
            "D",  # diamond
            "P",  # plus (filled)
            "X",  # x (filled)
            "*",  # star
            "+",  # plus
            "x",  # x
            ".",  # pixel
            "1",  # tri-down (kept for variation; remove if needed)
            "|",  # vertical line
            "_"   # horizontal line
        ])

        fig, ax = plt.subplots(layout="constrained")
        fig.set_size_inches((6, 5))
        for id, item in plots[series].items():
            xs, ys = zip(*item["line"])

            z = np.polyfit(xs, ys, 2)
            p = np.poly1d(z)

            yhat = p(xs)  # or [p(z) for z in x]
            ybar = np.sum(ys) / len(ys)  # or sum(y)/len(y)
            ssreg = np.sum(
                (yhat - ybar) ** 2
            )  # or sum([ (yihat - ybar)**2 for yihat in yhat])
            sstot = np.sum(
                (np.array(ys) - ybar) ** 2
            )  # or sum([ (yi - ybar)**2 for yi in y])
            r2 = ssreg / sstot

            sign = "+" if z[1] >= 0 else ""
            fit_eq = f"$R^2={r2:.3f}$: ${z[0]:.2f}x^2 {sign} {z[1]:.2f}x + c$"

            l = ax.plot(
                xs,
                ys,
                label=item["label"],
                marker=next(marker_styles),
                linestyle="None",
            )

            fx = np.linspace(min(xs), max(xs), 100)
            ax.plot(fx, p(fx), linestyle="--", alpha=0.5, color=l[0].get_color(), label=fit_eq)

        # Put a legend to the right of the current axis
        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        # ax.legend()

        return fig, ax

    def pretty_class_name(c: str) -> str:
        if re.match(r"TestRandom(\d*)Inputs", c):
            return "random graphs"
        if re.match(r"TestRandomDag(\d*)Inputs", c):
            return "random DAGs"
        if re.match(r"TestRandomFullyConnectedSameCap(\d*)Inputs", c):
            return "complete graphs"
        if re.match(r"TestVaryingExpanderHierarchy(\d*)Inputs", c):
            return "expander hierarchies"
        return c

    for cn in by_cn:
        continue
        for fn in by_cn[cn]:
            fn_name = FUNCTIONS[fn]["name"].lower()
            cn_name = pretty_class_name(cn)

            fig, ax = plot_series_data(cn, fn, "x=m")
            ax.set_xlabel(r"Edge scale factor ($m = x \cdot n$)")
            ax.set_ylabel(pretty_metric_name("edge_considerations"))
            ax.set_xscale("log", base=2)
            ax.set_yscale("log", base=2)
            ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
            title = f"{pretty_metric_name("edge_considerations")} with {fn_name} ({cn_name})"
            ax.set_title( title, loc="left")
            ax.grid(True)
            save_plot(f"graph_size_xm_{cn}_{fn}")

            fig, ax = plot_series_data(cn, fn, "x=n")
            ax.set_xlabel(r"$n$")
            ax.set_ylabel(pretty_metric_name("edge_considerations"))
            ax.set_xscale("log", base=2)
            ax.set_yscale("log", base=2)
            ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
            title = f"{pretty_metric_name("edge_considerations")} with {fn_name} ({cn_name})"
            ax.set_title( title, loc="left")
            ax.grid(True)
            save_plot(f"graph_size_xn_{cn}_{fn}")

        # plt.show()

    for class_name, class_runs in group_by(data, "class_name").items():
        if not class_name.startswith("TestVaryingExpanderHierarchy"):
            continue

        for fn, fn_runs in group_by(class_runs, "function_name").items():
            if "expander" not in fn:
                continue

            fn_name = FUNCTIONS[fn]["name"].lower()
            cn_name = pretty_class_name(class_name)

            points = []
            for n, n_runs in sorted(
                group_by(fn_runs, "instance.n").items(),
                key=lambda x: x[0],
            ):
                val = average_by(n_runs, "blik.marked_admissible") + average_by(n_runs, "blik.marked_inadmissible")
                points.append((n, val))

            series = {
                "label": "With expander hierarchy weight function",
                "line": points,
            }
            obj = { "dummy": { "dummy": series } }

            by_cn["dummy"] = {}
            by_cn["dummy"]["expand_dummy"] = obj

            fig, ax = plot_series_data("dummy", "expand_dummy", "dummy")
            ax.set_xlabel(r"$n$")
            ax.set_ylabel("Number of edge considerations")
            # ax.set_xscale("log", base=2)
            # ax.set_yscale("log", base=2)
            ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:.0f}"))
            title = f"Total number of edge considerations with {fn_name}"
            ax.set_title(title, loc="left")
            ax.grid(True)
            ax.legend()
            save_plot(f"graph_size_xn_expanduh")

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


def cmp_weight_functions_avg(
    data: ProcessedRunList, sizes: list[int] | list[tuple[int, int]]
):
    metrics: list[tuple[str, str | None]] = [
        # ("avg_updates", None),
        # ("average_w_length", None),
        # ("duration_s", "instance.n"),
        # ("marked_admissible", "instance.m"),
        # ("marked_dead", "instance.n"),
        ("edge_considerations", "instance.m"),
        # ("before_kill.marked_admissible", "instance.m"),
        # ("before_kill.marked_inadmissible", "instance.m"),
        # ("state_change.marked_admissible", "instance.m"),
        # ("state_change.marked_inadmissible", "instance.m"),
        ("state_change.state_changes", None),
        # ("before_kill.relabels", "instance.n"),
        # ("relabels", "instance.n"),
        # ("iterations", "instance.n"),
        # ("edge_updates", "instance.m"),
        # ("highest_level", "instance.n"),
    ]

    def ylabel(metric: str) -> str:
        if metric == "state_change.state_changes":
            return "Admissibility changes per edge ([#changes]/$m$)"
        if metric == "edge_considerations":
            return f"{pretty_metric_name(metric)} ([#considerations]/$m$)"
        return metric

    def pretty_class_name(c: str) -> str:
        if c == "TestRandomCInputs":
            return "random graphs"
        if c == "TestRandomCDagInputsDAG":
            return "random DAGs"
        if c == "TestRandomFullyConnectedSameCapInputs":
            return "complete graphs"
        if c == "TestVaryingExpanderHierarchyInputs":
            return "expander hierarchies"
        return c

    for metric, normalization_parameter in metrics:
        prefixed_metric = f"blik.{metric}"

        by_class = group_by(no_correct_flow(data), "class_name")
        for class_name, class_runs in by_class.items():
            if class_name is None:
                continue

            functions: dict[str, list[float]] = {
                name: []
                for name in set(str(run["function_name"]) for run in class_runs)
            }

            def do(runs: ProcessedRunList):
                for function_name, function_runs in group_by(
                    runs, "function_name"
                ).items():
                    if metric == "edge_considerations":
                        measurement = average_by(
                            function_runs, "blik.marked_inadmissible"
                        ) + average_by(function_runs, "blik.marked_admissible")
                    else:
                        measurement = average_by(function_runs, prefixed_metric)
                    if normalization_parameter is not None:
                        measurement /= cast(
                            float, function_runs[0][normalization_parameter]
                        )
                    functions[str(function_name)].append(measurement)

            x_axis: list[str] = []

            for n, n_runs in group_by(class_runs, "instance.n").items():
                if type(sizes[0]) is int:
                    if n not in sizes:
                        continue
                    m = average_by(n_runs, "instance.m")
                    x_axis.append(f"$n={n}$\n$m={m:.0f}$")
                    do(n_runs)
                else:
                    for m, m_runs in group_by(n_runs, "instance.m").items():
                        if (n, m) not in sizes:
                            continue

                        x_axis.append(f"$n={n}$\n$m={m:.0f}$")
                        do(m_runs)

            x = np.arange(len(x_axis))
            width = 0.25
            multiplier = 0

            fig, ax = plt.subplots(layout="constrained")
            # fig.set_size_inches((20, 6))

            for function_name, measurement in functions.items():
                offset = width * multiplier

                real_name = FUNCTIONS[function_name]["name"]

                _ = ax.bar(
                    x + offset,
                    measurement,
                    width,
                    label=real_name,
                    color=FUNCTIONS[function_name]["color"],
                )
                # ax.bar_label(rects, padding=3)
                multiplier += 1

            title = f"{pretty_metric_name(metric)} for {pretty_class_name(class_name)}"
            # if normalization_parameter is not None:
            #     title += f" normalized by {normalization_parameter}"
            ax.set_title(title)
            ax.set_ylabel(ylabel(metric))
            ax.set_xticks(x + width, x_axis)
            ax.legend()
            save_plot(f"cmp_{metric}_{class_name}")


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
    plot_with_respect_to_graph_size(no_correct_flow(preprocessed_data))
    # cmp_weight_functions(preprocessed_data)

    # files = [
    #     (
    #         "benches/varying-expanders-collected-18-may-22:19.json",
    #         [
    #             (90),
    #             (210),
    #             (306),
    #             (420),
    #         ],
    #     ),
    #     (
    #         "benches/non-dag-runs-18-may-21:16.json",
    #         [
    #             (256, 256),
    #             (256, 512),
    #             (256, 1024),
    #             (256, 2048),
    #         ],
    #     ),
    #     (
    #         "benches/dag-runs-18-may-21:15.json",
    #         [
    #             (256, 256),
    #             (256, 512),
    #             (256, 1024),
    #             (256, 2048),
    #         ],
    #     ),
    #     (
    #         "benches/fully-connected-same-cap-18-may-20:56.json",
    #         [
    #             (8, 56),
    #             (16, 240),
    #             (32, 992),
    #             (64, 4032),
    #         ],
    #     ),
    # ]
    #
    # for file, sizes in files:
    #     print(f"Processing {file}")
    #     data = load_data(file)
    #     preprocessed_data = preprocess(data)
    #
    #     cmp_weight_functions_avg(preprocessed_data, sizes)
