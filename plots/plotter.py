import sys
import json
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
from typing import TypedDict
import pathlib


class BenchmarkConfig(TypedDict):
    expected: int
    file: str
    name: str
    sink: int
    source: int
    top_sort: bool


class AlgorithmMetrics(TypedDict, total=False):
    avg_updates: float
    edge_updates: int
    flow: int
    iterations: int
    max_edge_updates: int
    min_edge_updates: int
    highest_level: int | None
    marked_admissible: int | None
    marked_dead: int | None
    marked_inadmissible: int | None
    dag_marked_admissible: int | None
    dag_marked_inadmissible: int | None
    relabels: int | None


class InstanceData(TypedDict):
    h: int
    m: int
    n: int


class BenchmarkResult(TypedDict):
    bench_config: BenchmarkConfig
    blik: AlgorithmMetrics
    capacity: AlgorithmMetrics
    edmond: AlgorithmMetrics
    push_relabel: AlgorithmMetrics
    duration_s: float
    end: int
    instance: InstanceData
    start: int


# Example for handling multiple test cases in a JSON file
type BenchmarkData = dict[str, BenchmarkResult]


def default[T](data: dict[str, T], key: str, default: T) -> T:
    try:
        return data[key]
    except KeyError:
        return default


def dbg[T](data: T, **kwargs) -> T:
    print(data, "tags:", {k: v for k, v in kwargs.items()})
    return data


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


def plot_cmp(data: BenchmarkData):
    metrics = ["relabels", "edge_updates"]

    for metric in metrics:
        fig, ax = plt.subplots()
        algorithms = ["blik", "push_relabel"]

        inputs = data.keys()
        series: dict[str, list[int]] = {}

        for alg in algorithms:
            series[alg] = [default(data[inp][alg], metric, 0) for inp in inputs]

        x = np.arange(len(inputs))
        width = 0.35

        for i, (alg, values) in enumerate(series.items()):
            offset = width * i
            ax.bar(x + offset, values, width - 0.05, label=alg)

        ax.set_ylabel(metric)
        ax.set_xticks(x + width, inputs)
        ax.legend()

        save_plot(f"cmp_{metric}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run plotter.py <path_to_bench_file>")
        exit(1)

    bench_file = sys.argv[1]
    with open(bench_file, "r") as f:
        data: BenchmarkData = json.load(f)

    plot_cmp(data)
