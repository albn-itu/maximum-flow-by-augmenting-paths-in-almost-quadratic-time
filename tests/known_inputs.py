# https://cp-algorithms.com/graph/edmonds_karp.html
import pytest


CP_ALGORITHMS_GRAPH = """
6 9 0 5
0-(7)>1
0-(4)>2
2-(3)>1
1-(5)>3
1-(3)>4
2-(2)>4
4-(3)>3
3-(8)>5
4-(5)>5
"""

# # https://www.geeksforgeeks.org/max-flow-problem-introduction/
GEEKS_FOR_GEEKS_GRAPH = """
6 10 0 5
0-(16)>1
0-(13)>2
1-(10)>2
2-(4)>1
1-(12)>3
2-(14)>4
3-(9)>2
4-(7)>3
3-(20)>5
4-(4)>5
"""

# # Previous graph but use the graph of the optimal flow. Useful because
# # using half of the edge capacities for initial flow is a feasible flow.
GEEKS_FOR_GEEKS_MAXFLOW_GRAPH = """
6 8 0 5
0-(11)>1
0-(12)>2
2-(1)>1
1-(12)>3
2-(11)>4
4-(7)>3
3-(19)>5
4-(4)>5
"""

PARALLEL_EDGES = """
4 4 0 3
0-(5)>1
2-(1)>1
1-(6)>2
2-(7)>3
"""

IDK_GRAPH = """
6 9 0 5
0-(13)>1
0-(16)>2
1-(4)>2
1-(14)>3
2-(12)>4
4-(9)>1
3-(7)>4
3-(4)>5
4-(20)>5
"""

THORES_FRACTIONAL_GRAPH = """
5 5 0 4
0-(1)>1
0-(1)>2
1-(1)>3
2-(1)>3
3-(1)>4
"""

INPUT_EXPECTED = [
    pytest.param(CP_ALGORITHMS_GRAPH, 10, id="CP_ALGORITHMS_GRAPH"),
    pytest.param(GEEKS_FOR_GEEKS_GRAPH, 23, id="GEEKS_FOR_GEEKS_GRAPH"),
    pytest.param(GEEKS_FOR_GEEKS_MAXFLOW_GRAPH, 23, id="GEEKS_FOR_GEEKS_MAXFLOW_GRAPH"),
    pytest.param(
        PARALLEL_EDGES, 5, id="PARALLEL_EDGES"
    ),  # Not supported before expander
    pytest.param(IDK_GRAPH, 23, id="IDK_GRAPH"),
    pytest.param(THORES_FRACTIONAL_GRAPH, 1, id="THORES_FRACTIONAL_GRAPH"),
]
