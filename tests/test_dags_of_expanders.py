import pytest
from src.utils import export_russian_graph
from src.weighted_push_relabel import weighted_push_relabel
from src.expander_generator import ConstructedInstance
from tests.utils import run_test


def make_input(instance: ConstructedInstance):
    # instance.export_graphviz()

    G, s, t, h, w, *rem = instance.export_weighted_push_relabel_input()
    input = export_russian_graph(G, s, t)

    return input, h, w


INPUT_EXPECTED = [
    pytest.param(
        ConstructedInstance.new(
            seed=420,
            num_ranks=3,
            connections_per_rank=2,
            expanders_per_rank=3,
            nodes_per_expander=15,
            expander_degree=4,
        ),
        81,
        id="15size_3x3_expanders",
    ),
    pytest.param(
        ConstructedInstance.new(
            seed=420,
            num_ranks=5,
            connections_per_rank=2,
            expanders_per_rank=5,
            nodes_per_expander=10,
            expander_degree=4,
        ),
        66,
        id="10size_5x5_expanders",
    ),
]


@pytest.mark.expander
@pytest.mark.parametrize("instance,expected", INPUT_EXPECTED)
def test_flow_with_dag_of_expanders_without_weight_fn(
    instance: ConstructedInstance, expected: int
):
    input, h, _ = make_input(instance)
    run_test(input, expected, weighted_push_relabel, h=h)


@pytest.mark.expander
@pytest.mark.parametrize("instance,expected", INPUT_EXPECTED)
def test_flow_with_dag_of_expanders_with_weight_fn(
    instance: ConstructedInstance, expected: int
):
    input, h, w = make_input(instance)
    run_test(input, expected, weighted_push_relabel, weight_fn=w, h=h)
