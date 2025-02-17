from tests.known_inputs import INPUT_EXPECTED
from tests.utils import wrap_correct, run_test
from src.weighted_push_relabel import weighted_push_relabel
import pytest


@pytest.mark.paper
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_flow_known_inputs(input: str, expected: int):
    run_test(input, expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_correct_known_inputs(input: str, expected: int):
    run_test(input, expected, wrap_correct)
