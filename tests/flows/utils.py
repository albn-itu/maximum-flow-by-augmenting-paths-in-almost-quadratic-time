from src.weighted_push_relabel import Graph

TestEdge = tuple[int, int]


def make_test_flow_input(
    G: Graph, c: list[int], sources: list[int], sinks: list[int], _w: int, _h: int
) -> tuple[list[TestEdge], list[int], int, int]:
    edges = G.E
    capacities = c
    source = sources[0]
    sink = sinks[0]

    return edges, capacities, source, sink
