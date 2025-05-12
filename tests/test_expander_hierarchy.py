import os
from typing import final, override
import typing

import src.benchmark as benchmark

from src.weighted_push_relabel import weighted_push_relabel
from src.expander_hierarchy_generator import from_json_file
import pytest
from src.utils import Edge, export_russian_graph

from tests.utils import bench, run_test
from .test_weighted_push_relabel import (
    Base,
    create_test_params,
)

TEST_FILE_DIR = "tests/data/expander_hierarchies"


def create_input_expected() -> list[tuple[str, int, str]]:
    input_expected: list[tuple[str, int, str]] = []
    for file in os.listdir(TEST_FILE_DIR):
        if file.endswith(".json"):
            basename = os.path.basename(file)
            hierarchy = from_json_file(os.path.join(TEST_FILE_DIR, file))

            input_expected.append(
                (
                    export_russian_graph(hierarchy.G, hierarchy.s, hierarchy.t),
                    hierarchy.flow,
                    basename,
                )
            )

    return input_expected


def pytest_generate_tests(metafunc: pytest.Metafunc):
    class_instance: Base = typing.cast(Base, metafunc.cls)
    in_ex, ids = create_test_params(class_instance)

    if "filename" in metafunc.fixturenames:
        # Add the filename to the test parameters
        in_ex = [
            (input, expected, f"{filename}")
            for (input, expected), filename in zip(in_ex, ids)
        ]
        metafunc.parametrize("input,expected,filename", in_ex, ids=ids)
    else:
        metafunc.parametrize("input,expected", in_ex, ids=ids)


@final
class TestExpanderHierarchyInputs(Base):
    file_based = False
    params = create_input_expected()

    @pytest.mark.weighted_push_relabel
    @pytest.mark.with_expander_hierarchy
    @pytest.mark.with_top_sort
    @bench
    @override
    def test_weighted_push_relabel_with_expander_hierarchy_weights(
        self, input: str, expected: int, filename: str
    ):
        benchmark.register("bench_config.top_sort_from_expander", True)
        expander_hierarchy = from_json_file(os.path.join(TEST_FILE_DIR, filename))

        ranks = {v: i for i, v in enumerate(expander_hierarchy.order)}

        def weight_fn(e: Edge):
            return abs(ranks[e.v] - ranks[e.u])

        return run_test(input, expected, weighted_push_relabel, weight_fn)
