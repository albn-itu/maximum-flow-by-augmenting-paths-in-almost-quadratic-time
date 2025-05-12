from src.utils import Graph, topological_sort_with_backwards_edges


def test_backwards_edges_are_handled():
    # Create a simple directed graph with a backward edge
    G = Graph(
        V=[0, 1, 2, 3, 4],
        E=[
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1),  # Backward edge creating a cycle
        ],
        c=[1, 1, 1, 1, 1],  # Capacities for each edge
    )

    # Perform topological sort
    order, backwards_edges = topological_sort_with_backwards_edges(G)

    # Check if the order is correct (should be a valid topological sort)
    assert order == [0, 1, 2, 3, 4], (
        f"Expected order to be [0, 1, 2, 3, 4], got {order}"
    )

    # Check if the backwards edges are correctly identified
    assert backwards_edges == {(4, 1)}, (
        f"Expected backwards edges to be {(4, 1)}, got {backwards_edges}"
    )


def test_backwards_edges_are_handled_2():
    # Create a simple directed graph with a backward edge
    G = Graph(
        V=[0, 1, 2, 3, 4],
        E=[
            (0, 1),
            (1, 2),
            (3, 1),  # Backward edge creating a cycle
            (2, 3),
            (3, 4),
            (4, 1),  # Backward edge creating a cycle
        ],
        c=[1, 1, 1, 1, 1],  # Capacities for each edge
    )

    # Perform topological sort
    order, backwards_edges = topological_sort_with_backwards_edges(G)

    # Check if the order is correct (should be a valid topological sort)
    assert order == [0, 1, 2, 3, 4], (
        f"Expected order to be [0, 1, 2, 3, 4], got {order}"
    )

    # Check if the backwards edges are correctly identified
    assert backwards_edges == {(4, 1), (3, 1)}, (
        f"Expected backwards edges to be {(4, 1), (3, 1)}, got {backwards_edges}"
    )
