from typing import Callable
from src import benchmark
from src.utils import Edge, Graph

TestEdge = tuple[int, int]


def make_test_flow_input(
    G: Graph,
    c: list[int],
    sources: list[int],
    sinks: list[int],
    _w: Callable[[Edge], int],
    _h: int,
) -> tuple[list[TestEdge], list[int], int, int]:
    edges = G.E
    capacities = c
    sources = [v for v in G.V if sources[v] > 0]
    sinks = [v for v in G.V if sinks[v] > 0]

    source = sources[0] if sources else 0
    sink = sinks[0] if sinks else 0

    benchmark.register("bench_config.source", source)
    benchmark.register("bench_config.sink", sink)

    return edges, capacities, source, sink
