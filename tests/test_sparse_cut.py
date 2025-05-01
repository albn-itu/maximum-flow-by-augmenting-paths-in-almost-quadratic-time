from itertools import chain
from src.sparse_cut import sparse_cut
from tests.known_inputs import INPUT_EXPECTED
from tests.utils import parse_input
import pytest


def run_sparse_cut(input: str, expected: int, kappa: int):
    G, sources, sinks = parse_input(input, expected)
    c = G.c
    _sources = {v: sources[i] for i, v in enumerate(G.V)}
    _sinks = {v: sinks[i] for i, v in enumerate(G.V)}

    edges = set(chain.from_iterable(G.incident.values()))

    return sparse_cut(
        I=(G, c, _sources, _sinks),
        kappa=kappa,
        F=edges,
        H={},
    )


@pytest.mark.paper
@pytest.mark.sparse_cut
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_flow_known_inputs(input: str, expected: int):
    # benchmark.register_or_update("bench_config.top_sort", False, lambda x: x)

    flow, cut = run_sparse_cut(input, expected, kappa=1)
    print("flow", flow)
    print("cut", cut)

    assert flow is not None
