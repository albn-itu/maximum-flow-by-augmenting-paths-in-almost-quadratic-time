import typing
import pytest
from src.weighted_push_relabel import weighted_push_relabel
from tests import known_inputs, large_inputs, random_inputs
from tests.utils import (
    bench,
    run_test,
    run_test_with_flow_weight,
    run_test_with_topsort,
    wrap_correct,
)


def read_file(file: str) -> str:
    with open(file, "r") as f:
        return f.read()


class Base:
    file_based: bool = False
    params: list[tuple[str, int, str]] = []

    @pytest.mark.weighted_push_relabel
    @bench
    def test_weighted_push_relabel(self, input: str, expected: int):
        run_test(input, expected, weighted_push_relabel)

    @pytest.mark.weighted_push_relabel
    @pytest.mark.with_flow_weight
    @bench
    def test_weighted_push_relabel_with_flow_weight(self, input: str, expected: int):
        run_test_with_flow_weight(input, expected, weighted_push_relabel)

    @pytest.mark.correct_flow
    @bench
    def test_correct_flow_algorithms(self, input: str, expected: int):
        run_test(input, expected, wrap_correct)


def create_test_params(class_instance: Base) -> tuple[list[tuple[str, int]], list[str]]:
    params = class_instance.params
    if not params:
        raise ValueError(
            f"Class {class_instance.__qualname__} does not have 'params' attribute."
        )

    if class_instance.file_based:
        for i, param in enumerate(params):
            input, expected, id = param

            params[i] = (read_file(input), expected, id)
        class_instance.file_based = False

    in_ex: list[tuple[str, int]] = []
    ids: list[str] = []

    for param in params:
        input, expected, id = param
        in_ex.append((input, expected))
        ids.append(id)

    return in_ex, ids


def pytest_generate_tests(metafunc: pytest.Metafunc):
    class_instance: Base = typing.cast(Base, metafunc.cls)
    in_ex, ids = create_test_params(class_instance)

    metafunc.parametrize("input, expected", in_ex, ids=ids)


class TopSortable(Base):
    @pytest.mark.weighted_push_relabel
    @pytest.mark.with_top_sort
    @bench
    def test_weighted_push_relabel_with_topsort(self, input: str, expected: int):
        run_test_with_topsort(input, expected, weighted_push_relabel)


@typing.final
class TestKnownInputs(Base):
    params = known_inputs.INPUT_EXPECTED


@typing.final
class TestKnownInputsDAG(TopSortable):
    params = known_inputs.INPUT_EXPECTED_DAG


@typing.final
class TestRandomInputs(TopSortable):
    params = random_inputs.INPUT_EXPECTED


@typing.final
@pytest.mark.slow
class TestLargeInputsDAG(TopSortable):
    file_based = True
    params = large_inputs.DAG_INPUT_EXPECTED


@typing.final
@pytest.mark.slow
class TestLargeInputsFullyConnected(Base):
    file_based = True
    params = large_inputs.FULLY_CONNECTED_INPUT_EXPECTED


@typing.final
@pytest.mark.slow
class TestLargeInputsLine(TopSortable):
    file_based = True
    params = large_inputs.LINE_INPUT_EXPECTED


@typing.final
@pytest.mark.slow
class TestLargeInputsMaxflowDAG(TopSortable):
    file_based = True
    params = large_inputs.MAXFLOW_DAG_INPUT_EXPECTED


@typing.final
@pytest.mark.slow
class TestLargeInputsMaxflow(Base):
    file_based = True
    params = large_inputs.MAXFLOW_NOT_DAG_INPUT_EXPECTED


@typing.final
@pytest.mark.slow
class TestLargeInputsWaissi(Base):
    file_based = True
    params = large_inputs.WAISSI_INPUT_EXPECTED
