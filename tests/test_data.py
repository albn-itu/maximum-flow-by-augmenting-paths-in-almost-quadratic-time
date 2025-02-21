import os
from src import benchmark
from src.weighted_push_relabel import weighted_push_relabel
from tests.utils import (
    run_test as run_test_str,
    run_test_with_topsort,
    wrap_correct,
    FlowFn,
)
import pytest


DAG_INPUT_EXPECTED = [
    pytest.param("tests/data/dag_edges_25.txt", 65, id="dag_edges_25"),
    pytest.param("tests/data/dag_edges_50.txt", 169, id="dag_edges_50"),
    pytest.param("tests/data/dag_edges_100.txt", 222, id="dag_edges_100"),
    pytest.param("tests/data/dag_edges_150.txt", 264, id="dag_edges_150"),
    pytest.param("tests/data/dag_edges_200.txt", 357, id="dag_edges_200"),
    pytest.param("tests/data/dag_edges_250.txt", 383, id="dag_edges_250"),
    pytest.param("tests/data/dag_edges_500.txt", 674, id="dag_edges_500"),
]

FULLY_CONNECTED_INPUT_EXPECTED = [
    pytest.param(
        "tests/data/fully_connected_edges_20.txt", 40, id="fully_connected_edges_20"
    ),
    pytest.param(
        "tests/data/fully_connected_edges_210.txt", 312, id="fully_connected_edges_210"
    ),
    pytest.param(
        "tests/data/fully_connected_edges_90.txt", 179, id="fully_connected_edges_90"
    ),
    pytest.param(
        "tests/data/fully_connected_edges_380.txt", 462, id="fully_connected_edges_380"
    ),
    # pytest.param("tests/data/fully_connected_edges_600.txt", 10, id="fully_connected_edges_600"),
]

LINE_INPUT_EXPECTED = [
    pytest.param("tests/data/line_edges_25.txt", 4, id="line_edges_25"),
    pytest.param("tests/data/line_edges_50.txt", 4, id="line_edges_50"),
    pytest.param("tests/data/line_edges_100.txt", 4, id="line_edges_100"),
    pytest.param("tests/data/line_edges_150.txt", 4, id="line_edges_150"),
    pytest.param("tests/data/line_edges_200.txt", 4, id="line_edges_200"),
    pytest.param("tests/data/line_edges_250.txt", 4, id="line_edges_250"),
    pytest.param("tests/data/line_edges_500.txt", 4, id="line_edges_500"),
]


def read_file(file: str) -> str:
    with open(file, "r") as f:
        return f.read()


def run_test(input_file: str, expected: int, flow_fn: FlowFn):
    benchmark.start_benchmark(os.environ.get("PYTEST_CURRENT_TEST") or "unknown")
    benchmark.register_or_update("bench_config.file", input_file, lambda x: x)

    input_str = read_file(input_file)
    run_test_str(input_str, expected, flow_fn)


@pytest.mark.paper
@pytest.mark.parametrize("input_file,expected", DAG_INPUT_EXPECTED)
def test_flow_dag(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.paper
@pytest.mark.w_top_sort
@pytest.mark.parametrize("input_file,expected", DAG_INPUT_EXPECTED)
def test_flow_dag_with_topsort(input_file: str, expected: int):
    run_test_with_topsort(read_file(input_file), expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.parametrize("input_file,expected", DAG_INPUT_EXPECTED)
def test_correct_dag(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


@pytest.mark.paper
@pytest.mark.notdag
@pytest.mark.parametrize("input_file,expected", FULLY_CONNECTED_INPUT_EXPECTED)
def test_flow_fully_connected(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.notdag
@pytest.mark.parametrize("input_file,expected", FULLY_CONNECTED_INPUT_EXPECTED)
def test_correct_fully_connected(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


@pytest.mark.paper
@pytest.mark.parametrize("input_file,expected", LINE_INPUT_EXPECTED)
def test_flow_line(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.parametrize("input_file,expected", LINE_INPUT_EXPECTED)
def test_correct_line(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


def get_maxflow_files(small: bool) -> list[tuple[str, int]]:
    files = os.listdir("tests/data/maxflow")
    file_expected = []

    for file in files:
        if not file.endswith(".txt"):
            continue

        _, _, _, expected = file.split("_")
        expected = int(expected.split(".")[0])
        if small and int(expected) > 10**5:
            continue

        file_expected.append(
            pytest.param(f"tests/data/maxflow/{file}", expected, id=file)
        )

    return file_expected


@pytest.mark.paper
@pytest.mark.maxflow
@pytest.mark.parametrize("input_file,expected", get_maxflow_files(True))
def test_flow_maxflow_small(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.maxflow
@pytest.mark.parametrize("input_file,expected", get_maxflow_files(True))
def test_correct_maxflow_small(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


@pytest.mark.paper
@pytest.mark.large
@pytest.mark.maxflow
@pytest.mark.parametrize("input_file,expected", get_maxflow_files(False))
def test_flow_maxflow_large(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.correct
@pytest.mark.large
@pytest.mark.maxflow
@pytest.mark.parametrize("input_file,expected", get_maxflow_files(False))
def test_correct_maxflow_large(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)
