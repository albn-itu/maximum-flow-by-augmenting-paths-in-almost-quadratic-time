from src.weighted_push_relabel import Graph
from typing import Callable
from tests.flows.utils import make_test_flow_input
from tests.flows import find_max_flow as find_max_flow_correct


def parse_input(input: str) -> tuple[Graph, list[int], list[int], list[int]]:
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

    return (Graph(vertices, edges), capacities, [s], [t])


def wrap_correct(
    g: Graph, c: list[int], sources: list[int], sinks: list[int], w: int, h: int
) -> int:
    edges, capacities, s, t = make_test_flow_input(g, c, sources, sinks, w, h)

    return find_max_flow_correct(edges, capacities, s=s, t=t)


FlowFn = Callable[[Graph, list[int], list[int], list[int], int, int], int]


def run_test(
    input: str,
    expected: int,
    flow_fn: FlowFn,
):
    g, c, sources, sinks = parse_input(input)
    mf = flow_fn(g, c, sources, sinks, 0, 0)
    assert mf == expected
