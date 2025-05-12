from src.expander_decomposition import expander_decomposition
from src.utils import Edge, parse_input
from tests.known_inputs import INPUT_EXPECTED
from tests.utils import input_expected_list_to_params
import pytest


def run_expander_decomposition(input: str, expected: int, kappa: int) -> set[Edge]:
    G, sources, sinks = parse_input(input, expected)
    c = G.c
    _sources = {v: sources[i] for i, v in enumerate(G.V)}
    _sinks = {v: sinks[i] for i, v in enumerate(G.V)}

    edges = G.all_edges()

    return expander_decomposition(
        I=(G, c, _sources, _sinks), kappa=kappa, F=edges, H={}, phi=0.2
    )


@pytest.mark.weighted_push_relabel
@pytest.mark.expander_decomposition
@pytest.mark.parametrize(
    "input,expected", input_expected_list_to_params(INPUT_EXPECTED)
)
def test_expander_decomposition_known_inputs(input: str, expected: int):
    # benchmark.register_or_update("bench_config.top_sort", False, lambda x: x)

    cut = run_expander_decomposition(input, expected, kappa=10)
    print("cut", cut)

    assert len(cut) != 0


@pytest.mark.weighted_push_relabel
@pytest.mark.expander_decomposition
@pytest.mark.parametrize(
    "input,expected", input_expected_list_to_params(INPUT_EXPECTED)
)
def test_expander_decomposition_known_inputs_dag(input: str, expected: int):
    # benchmark.register_or_update("bench_config.top_sort", False, lambda x: x)

    cut = run_expander_decomposition(input, expected, kappa=1)
    print("cut", cut)

    assert len(cut) != 0
