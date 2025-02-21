from tests.known_inputs import INPUT_EXPECTED, INPUT_EXPECTED_DAG
from tests.utils import run_test_with_topsort, wrap_correct, run_test, bench
from src.weighted_push_relabel import weighted_push_relabel
import pytest


@pytest.mark.paper
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_flow_known_inputs(input: str, expected: int):
    run_test(input, expected, weighted_push_relabel)


@pytest.mark.paper
@pytest.mark.w_top_sort
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED_DAG)
@bench
def test_flow_known_inputs_with_topsort(input: str, expected: int):
    run_test_with_topsort(input, expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
def test_correct_known_inputs(input: str, expected: int):
    run_test(input, expected, wrap_correct)


@pytest.mark.benchmark
@pytest.mark.parametrize("input,expected", INPUT_EXPECTED)
@bench
def test_benchmark_known_inputs(input: str, expected: int):
    run_test_with_topsort(input, expected, weighted_push_relabel)
    run_test(input, expected, wrap_correct)
