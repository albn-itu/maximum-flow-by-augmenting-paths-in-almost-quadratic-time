from typing import Callable
from src import benchmark
from src.utils import (
    Edge,
    Graph,
    topological_sort_with_backwards_edges,
)
from src.flows.classic_push_relabel import PushRelabel


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
        def meta(edge: Edge) -> int:
            u, v = edge.start(), edge.end()

            if u not in ordering_map and v not in ordering_map:
                return default

            if edge in flow and flow[edge] > 0:
                return abs(ordering_map.get(u, default) - ordering_map.get(v, default))

            return default

        return min(meta(edge), meta(edge.forward_edge()))

    return weight_function


def topological_sort_induced_flow_dag(
    flow: dict[Edge, int],
) -> list[int]:
    """
    Create a new graph with only the edges that have flow in the original graph.
    """

    edges: list[tuple[int, int]] = [
        (edge.u, edge.v) for edge, flow in flow.items() if flow > 0
    ]
    vertices: set[int] = set()
    for edge in edges:
        vertices.add(edge[0])
        vertices.add(edge[1])

    G = Graph(list(vertices), edges, [])
    return topological_sort_with_backwards_edges(G)[0]
