from src.utils import Edge, Graph, topological_sort
from typing import Callable
from tests.flows.utils import make_test_flow_input
from tests.flows import find_max_flow as find_max_flow_correct


def parse_input(
    input: str, expected: int
) -> tuple[Graph, list[int], list[int], list[int]]:
    lines = input.strip().split("\n")
    n, _, s, t = map(int, lines[0].split())

    vertices = list(range(n))
    edges: list[tuple[int, int]] = []
    capacities: list[int] = []

    for line in lines[1:]:
        u, rest = line.split("-(")
        cap, v = rest.split(")>")

        edges.append((int(u), int(v)))
        capacities.append(int(cap))

    sources = [0] * n
    sinks = [0] * n

    sources[s] = expected
    sinks[t] = expected

    return (Graph(vertices, edges), capacities, sources, sinks)


def wrap_correct(
    g: Graph,
    c: list[int],
    sources: list[int],
    sinks: list[int],
    w: Callable[[Edge], int],
    h: int,
) -> tuple[int, dict[Edge, int] | None]:
    edges, capacities, s, t = make_test_flow_input(g, c, sources, sinks, w, h)

    return (find_max_flow_correct(edges, capacities, s=s, t=t), None)


FlowFn = Callable[
    [Graph, list[int], list[int], list[int], Callable[[Edge], int], int],
    tuple[int, dict[Edge, int] | None],
]


def run_test(
    input: str,
    expected: int,
    flow_fn: FlowFn,
    weight_fn: Callable[[Edge], int] = lambda e: 1,
):
    g, c, sources, sinks = parse_input(input, expected)
    mf, _ = flow_fn(g, c, sources, sinks, weight_fn, len(g.V))
    assert mf == expected, f"Expected {expected}, got {mf}"


def run_test_with_topsort(
    input: str,
    expected: int,
    flow_fn: FlowFn,
):
    g, *_ = parse_input(input, expected)

    ordering = topological_sort(g)
    ranks = {v: i for i, v in enumerate(ordering)}

    def weight_fn(e: Edge):
        return abs(ranks[e.v] - ranks[e.u])

    return run_test(input, expected, flow_fn, weight_fn)
