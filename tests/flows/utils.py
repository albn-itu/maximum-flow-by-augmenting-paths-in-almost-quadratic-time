from collections import defaultdict
from typing import Callable
from src import benchmark
from src.utils import Edge, Graph, topological_sort
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
    print("Flow ordering:", ordering)

    weights = {v: i for i, v in enumerate(ordering)}
    for v in G.V:
        if v not in weights:
            weights[v] = len(G.V)

    def weight_function(edge: Edge) -> int:
        u, v = edge.start(), edge.end()
        return abs(weights[v] - weights[u])

    return weight_function


def topological_sort_induced_flow_dag(
    flow: defaultdict[int, defaultdict[int, int]],
) -> list[int]:
    """
    Create a new graph with only the edges that have flow in the original graph.
    """

    vertices = list(set(flow.keys()).union(*flow.values()))
    edges_to_keep: list[tuple[int, int]] = [
        (u, v) for u in vertices for v in flow[u].keys() if flow[u][v] > 0
    ]
    capacities = [1] * len(edges_to_keep)

    G = Graph(vertices, edges_to_keep, capacities)
    return topological_sort(G)
