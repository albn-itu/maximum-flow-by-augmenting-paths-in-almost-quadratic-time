from tests.random_inputs import INPUT_EXPECTED
from tests.utils import bench, run_test, run_test_with_topsort, wrap_correct
from src.weighted_push_relabel import weighted_push_relabel
import pytest


@pytest.mark.paper
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_flow_random(input: str, expected: int):
    run_test(input, expected, weighted_push_relabel)


@pytest.mark.paper
@pytest.mark.w_top_sort
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_flow_random_inputs_with_topsort(input: str, expected: int):
    run_test_with_topsort(input, expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_correct_random(input: str, expected: int):
    run_test(input, expected, wrap_correct)


@pytest.mark.benchmark
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
@bench
def test_benchmark_random(input: str, expected: int):
    run_test_with_topsort(input, expected, weighted_push_relabel)
    run_test(input, expected, wrap_correct)
