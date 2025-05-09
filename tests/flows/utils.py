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

    def weight_function(edge: Edge) -> int:
        u, v = edge.start(), edge.end()

        default_weight = len(G.E) * 100
        if (
            u in flow and v in flow[u] and flow[u][v] > 0
        ):  # If there is flow, return 0, as we want to use this edge
            if (
                v in flow and u in flow[v] and flow[v][u] > 0
            ):  # If the reverse edge also has flow, then we only use the forward edge
                if edge.forward:  # If the edge is forward, we return 0
                    return 1
                else:
                    return default_weight
            return 1
        return default_weight

    return weight_function
