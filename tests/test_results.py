from tests.known_inputs import INPUT_EXPECTED
from tests.utils import parse_input
from tests.flows.utils import make_test_flow_input
from tests.flows import find_max_flow as find_max_flow_correct
from src.weighted_push_relabel import weighted_push_relabel
import pytest


@pytest.mark.slow
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_flow_random(input: str, expected: int):
    g, c, sources, sinks = parse_input(input)
    mf = weighted_push_relabel(g, c, sources, sinks, 0, 0)

    assert mf == expected


@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_correct(input: str, expected: int):
    g, c, sources, sinks = parse_input(input)
    edges, capacities, s, t = make_test_flow_input(g, c, sources, sinks, 0, 0)

    mf = find_max_flow_correct(edges, capacities, s=s, t=t)
    assert mf == expected
