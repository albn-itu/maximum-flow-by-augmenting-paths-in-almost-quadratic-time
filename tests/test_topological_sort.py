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


# source: https://www.interviewcake.com/images/svgs/messy_graph.svg?bust=210
def test_interview_cake_example():
    G = Graph(
        V=[0, 1, 2, 3, 4],
        E=[(0, 1), (0, 2), (1, 3), (1, 4), (2, 3), (3, 4)],
        c=[],
    )

    order, backwards_edges = topological_sort_with_backwards_edges(G)

    assert order == [0, 2, 1, 3, 4], (
        f"Expected order to be [0, 1, 2, 3, 4], got {order}"
    )
    assert backwards_edges == set(), (
        f"Expected backwards edges to be [], got {backwards_edges}"
    )


# source: https://i.imgur.com/Q3MA6dZ.png
def test_codepath_example():
    G = Graph(
        V=[0, 1, 2, 3, 4, 5, 6],
        E=[(0, 1), (0, 2), (1, 5), (1, 2), (2, 3), (5, 4), (5, 3), (6, 1), (6, 5)],
        c=[],
    )

    order, backwards_edges = topological_sort_with_backwards_edges(G)

    assert order == [6, 0, 1, 5, 4, 2, 3], (
        f"Expected order to be [6, 0, 1, 5, 4, 2, 3], got {order}"
    )
    assert backwards_edges == set(), (
        f"Expected backwards edges to be [], got {backwards_edges}"
    )
