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

# Small graph that fails
SIMOLEAN_GRAPH = """
6 8 0 5
0-(3)>1
0-(9)>2
0-(9)>3
0-(8)>4
1-(4)>5
2-(1)>5
3-(3)>5
4-(3)>5
"""

# Reverse edge graph
REVERSE_GRAPH = """
12 13 0 3
0-(10)>1
1-(1)>2
2-(10)>3
0-(10)>4
4-(10)>5
5-(10)>6
6-(10)>7
7-(10)>8
8-(10)>2
1-(10)>9
9-(10)>10
10-(10)>11
11-(10)>3
"""

POSSIBLY_INTERESTING_GRAPH = """
13 18 0 11
0-(1)>1
0-(1)>2
0-(1)>6
1-(1)>3
2-(1)>1
2-(1)>5
3-(1)>2
3-(1)>4
4-(1)>6
4-(1)>5
5-(1)>6
5-(1)>7
6-(1)>7
6-(1)>8
7-(1)>8
7-(1)>9
8-(1)>10
9-(1)>11
10-(1)>11
"""

ADRIANS_ZIP_BOMB = """
6 9 0 5
0-(1)>1
1-(1)>3
1-(1)>5
2-(1)>0
2-(1)>5
3-(1)>1
3-(1)>2
4-(1)>3
5-(1)>4
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
    pytest.param(SIMOLEAN_GRAPH, 10, id="SIMOLEAN_GRAPH"),
    pytest.param(REVERSE_GRAPH, 20, id="REVERSE_GRAPH"),
    pytest.param(POSSIBLY_INTERESTING_GRAPH, 2, id="POSSIBLY_INTERESTING_GRAPH"),
    pytest.param(ADRIANS_ZIP_BOMB, 1, id="ADRIANS_ZIP_BOMB"),
]

INPUT_EXPECTED_DAG = [
    pytest.param(CP_ALGORITHMS_GRAPH, 10, id="CP_ALGORITHMS_GRAPH"),
    pytest.param(SIMOLEAN_GRAPH, 10, id="SIMOLEAN_GRAPH"),
    pytest.param(REVERSE_GRAPH, 20, id="REVERSE_GRAPH"),
]
