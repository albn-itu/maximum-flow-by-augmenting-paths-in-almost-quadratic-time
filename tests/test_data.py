import os
from src.weighted_push_relabel import weighted_push_relabel
from tests.utils import run_test as run_test_str, wrap_correct, FlowFn
import pytest


DAG_INPUT_EXPECTED = [
    ("tests/data/dag_edges_100.txt", 222),
    ("tests/data/dag_edges_150.txt", 264),
    ("tests/data/dag_edges_200.txt", 357),
    ("tests/data/dag_edges_25.txt", 65),
    ("tests/data/dag_edges_250.txt", 383),
    ("tests/data/dag_edges_50.txt", 169),
    ("tests/data/dag_edges_500.txt", 674),
]

FULLY_CONNECTED_INPUT_EXPECTED = [
    ("tests/data/fully_connected_edges_20.txt", 40),
    ("tests/data/fully_connected_edges_210.txt", 312),
    ("tests/data/fully_connected_edges_380.txt", 462),
    # ("tests/data/fully_connected_edges_600.txt", 10),
    ("tests/data/fully_connected_edges_90.txt", 179),
]

LINE_INPUT_EXPECTED = [
    ("tests/data/line_edges_100.txt", 4),
    ("tests/data/line_edges_150.txt", 4),
    ("tests/data/line_edges_200.txt", 4),
    ("tests/data/line_edges_25.txt", 4),
    ("tests/data/line_edges_250.txt", 4),
    ("tests/data/line_edges_50.txt", 4),
    ("tests/data/line_edges_500.txt", 4),
]


def read_file(file: str) -> str:
    with open(file, "r") as f:
        return f.read()


def run_test(input_file: str, expected: int, flow_fn: FlowFn):
    input_str = read_file(input_file)
    run_test_str(input_str, expected, flow_fn)


@pytest.mark.slow
@pytest.mark.parametrize("input_file,expected", DAG_INPUT_EXPECTED)
def test_flow_dag(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.parametrize("input_file,expected", DAG_INPUT_EXPECTED)
def test_correct_dag(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


@pytest.mark.slow
@pytest.mark.parametrize("input_file,expected", FULLY_CONNECTED_INPUT_EXPECTED)
def test_flow_fully_connected(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.parametrize("input_file,expected", FULLY_CONNECTED_INPUT_EXPECTED)
def test_correct_fully_connected(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


@pytest.mark.slow
@pytest.mark.parametrize("input_file,expected", LINE_INPUT_EXPECTED)
def test_flow_line(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.parametrize("input_file,expected", LINE_INPUT_EXPECTED)
def test_correct_line(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


def get_maxflow_files(small: bool) -> list[tuple[str, int]]:
    files = os.listdir("tests/data/maxflow")
    file_expected: list[tuple[str, int]] = []

    for file in files:
        if not file.endswith(".txt"):
            continue

        _, _, _, expected = file.split("_")
        expected = int(expected.split(".")[0])
        if small and int(expected) > 10**5:
            continue

        file_expected.append((f"tests/data/maxflow/{file}", expected))

    return file_expected


@pytest.mark.parametrize("input_file,expected", get_maxflow_files(True))
def test_flow_maxflow_small(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.parametrize("input_file,expected", get_maxflow_files(True))
def test_correct_maxflow_small(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)


@pytest.mark.large
@pytest.mark.parametrize("input_file,expected", get_maxflow_files(False))
def test_flow_maxflow_large(input_file: str, expected: int):
    run_test(input_file, expected, weighted_push_relabel)


@pytest.mark.large
@pytest.mark.parametrize("input_file,expected", get_maxflow_files(False))
def test_correct_maxflow_large(input_file: str, expected: int):
    run_test(input_file, expected, wrap_correct)
