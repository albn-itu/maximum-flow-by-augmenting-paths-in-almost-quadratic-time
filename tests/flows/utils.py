from collections import defaultdict
from typing import Callable
from src import benchmark
from src.utils import (
    Edge,
    Graph,
    topological_sort,
    topological_sort_with_backwards_edges,
)
from src.classic_push_relabel import PushRelabel


def get_source_and_sink(sources: list[int], sinks: list[int]) -> tuple[int, int]:
    source = next((i for i, s in enumerate(sources) if s > 0), -1)
    sink = next((i for i, s in enumerate(sinks) if s > 0), -1)
    return source, sink


def make_test_flow_input(
    G: Graph,
    sources: list[int],
    sinks: list[int],
    _w: Callable[[Edge], int],
    _h: int,
) -> tuple[list[tuple[int, int]], list[int], int, int]:
    edges = G.E
    source, sink = get_source_and_sink(sources, sinks)

    benchmark.register("bench_config.source", source)
    benchmark.register("bench_config.sink", sink)

    return edges, G.c, source, sink


def weight_function_from_flow(
    G: Graph,
    sources: list[int],
    sinks: list[int],
) -> Callable[[Edge], int]:
    pr_instance = PushRelabel(G)

    source, sink = get_source_and_sink(sources, sinks)

    _ = pr_instance.max_flow(source, sink)
    flow = pr_instance.flow

    ordering = topological_sort_induced_flow_dag(flow)
    ordering_map = {v: i for i, v in enumerate(ordering)}

    default = 100 * len(G.V)

    def weight_function(edge: Edge) -> int:
        u, v = edge.start(), edge.end()
        if u not in ordering_map and v not in ordering_map:
            return default

        return abs(ordering_map.get(u, default) - ordering_map.get(v, default))

    return weight_function


def topological_sort_induced_flow_dag(
    flow: defaultdict[int, defaultdict[int, int]],
) -> list[int]:
    """
    Create a new graph with only the edges that have flow in the original graph.
    """

    vertices = list(set(flow.keys()).union(*flow.values()))
    edges: list[tuple[int, int]] = [
        (u, v) for u in vertices for v in flow[u].keys() if flow[u][v] > 0
    ]

    G = Graph(vertices, edges, [])
    return topological_sort_with_backwards_edges(G)[0]
