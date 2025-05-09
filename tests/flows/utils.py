from collections import defaultdict
from typing import Callable
from src import benchmark
from src.utils import Edge, Graph
from tests.flows.push_relabel import PushRelabel


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

    dag_flow_edges = induced_flow_dag(flow)

    def weight_function(edge: Edge) -> int:
        u, v = edge.start(), edge.end()

        if (u, v) in dag_flow_edges:
            return 1

        return len(G.V) * 100

    return weight_function


def induced_flow_dag(
    flow: defaultdict[int, defaultdict[int, int]],
) -> set[tuple[int, int]]:
    """
    Create a new graph with only the edges that have flow in the original graph.
    """

    edges_to_keep: set[tuple[int, int]] = set()
    seen_vertices: set[int] = set()

    # Iterate the flow dictionary keeping all edges that don't induce a cycle
    for u in flow:
        seen_vertices.add(u)

        for v in flow[u]:
            if v in seen_vertices:
                continue  # Keeping this edge would create a cycle
            if flow[u][v] > 0:
                edges_to_keep.add((u, v))

    return edges_to_keep
