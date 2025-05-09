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
    print("Flow edges in DAG:", dag_flow_edges)

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

    vertices = set(flow.keys()).union(*flow.values())

    edges_to_keep: set[tuple[int, int]] = set(
        (u, v) for u in vertices for v in flow[u].keys() if flow[u][v] > 0
    )
    visited: set[int] = set()
    in_progress: set[int] = set()

    def dfs(vertex: int, path: list[int] | None = None) -> bool:
        """
        Depth-first search to detect cycles.

        Args:
            vertex: Current vertex being explored
            path: Path taken to reach the current vertex

        Returns:
            True if a cycle was detected and removed, False otherwise
        """
        if path is None:
            path = []

        # Already completely explored this vertex
        if vertex in visited:
            return False

        # Cycle detected
        if vertex in in_progress:
            # Remove the last edge in the cycle
            u = path[-1]
            v = vertex

            if (u, v) in edges_to_keep:
                edges_to_keep.remove((u, v))
                print(f"Removed edge: {u} -> {v}")

            return True

        in_progress.add(vertex)
        path.append(vertex)

        # Check all neighbors
        for neighbor in list(flow[vertex].keys()):
            if flow[vertex][neighbor] > 0 and dfs(neighbor, path):
                return True

        # Vertex exploration complete
        in_progress.remove(vertex)
        visited.add(vertex)
        _ = path.pop()

        return False

    # Process each vertex that hasn't been visited
    for vertex in vertices:
        if vertex not in visited and vertex not in in_progress:
            dfs(vertex)

    return edges_to_keep
