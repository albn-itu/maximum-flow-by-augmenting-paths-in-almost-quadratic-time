from tests.random_inputs import INPUT_EXPECTED
from tests.utils import run_test, wrap_correct
from src.weighted_push_relabel import weighted_push_relabel
import pytest


@pytest.mark.slow
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_flow_random(input: str, expected: int):
    run_test(input, expected, weighted_push_relabel)


@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_correct_random(input: str, expected: int):
    run_test(input, expected, wrap_correct)
