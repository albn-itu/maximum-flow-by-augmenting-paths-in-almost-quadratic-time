import math
import pathlib
import random
import sys
from typing import Callable

from flows.classic_push_relabel import PushRelabel
from utils import Graph, export_russian_graph, parse_input
from .generator_dag import generate_random_dag_nm
from .generator_non_dag import generate_fully_connected_graph, generate_random_graph_nm


def doubling_range(start: int, end: int):
    i = start
    while i <= end:
        yield i
        i *= 2


def percentage_range(start: int, end: int, step: float = 1.1):
    i = start
    while i <= end:
        yield i
        i = math.ceil(i * step)


def generate_graph(
    generate_function: Callable[[int, int, int], str | Graph],
    seed: int,
    n: int,
    m: int,
    dir: str,
    num: int,
):
    g_raw = generate_function(n, m, seed)
    if isinstance(g_raw, str):
        g, _, _ = parse_input(g_raw, 0)
    else:
        g = g_raw

    s = g.V[0]
    t = g.V[-1]
    expected = PushRelabel(g).max_flow(s, t)

    filename = f"{num:04}_{len(g.V)}_{len(g.E)}_{expected}.txt"
    path = pathlib.Path(dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(export_russian_graph(g, s, t))


if __name__ == "__main__":
    growth_rate = 1.50
    ns = list(percentage_range(16, 277, growth_rate))
    max_n = max(ns)

    ms = list(percentage_range(100, max_n**2, growth_rate))
    if max_n**2 != max(ms):
        ms.append(max_n**2)

    copies = 3

    base_path = "tests/data"

    seed = random.randrange(sys.maxsize)
    random.seed(seed)
    print("Seed:", seed)
    print("Generating graphs...")
    print("Growth rate:", growth_rate)
    print("N range:", ns)
    print("M range:", ms)
    print("Copies:", copies)

    graphs = 0
    for n in ns:
        for _ in range(copies):
            graphs += 1
            if graphs % 100 == 0:
                print(f"Generating graph {graphs}")

            generate_graph(
                lambda n, m, s: generate_fully_connected_graph(s, n),
                seed,
                n,
                -1,
                f"{base_path}/fully_connected_same_cap_{growth_rate}",
                graphs,
            )

    graphs = 0
    for n in ns:
        actual_ms = [m for m in ms if m >= n - 1 and m <= n**2]
        actual_ms.extend(list(percentage_range(n - 1, 100, growth_rate)))

        for m in actual_ms:
            for _ in range(copies):
                graphs += 1
                if graphs % 100 == 0:
                    print(f"Generating graph {graphs}")

                generate_graph(
                    generate_random_graph_nm,
                    seed,
                    n,
                    m,
                    f"{base_path}/random_graphs_{growth_rate}",
                    graphs,
                )
                generate_graph(
                    generate_random_dag_nm,
                    seed,
                    n,
                    m,
                    f"{base_path}/random_dags_{growth_rate}",
                    graphs,
                )
