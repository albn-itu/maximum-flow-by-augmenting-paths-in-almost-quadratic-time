from src.utils import Edge
from tests.known_inputs import GEEKS_FOR_GEEKS_GRAPH
from tests.scripts.generator_dag import make_random_dag
from tests.utils import (
    bench,
    parse_input,
    run_test,
    run_test_with_topsort,
    wrap_correct,
)
from src.weighted_push_relabel import weighted_push_relabel
import pytest


def compare_answers(
    input: str, h: int | None = None, topsort: bool = False, weight_fn=None
):
    g, sources, sinks = parse_input(input, 10_000)
    h = h if h is not None else len(g.V)
    mf, _ = wrap_correct(g, g.c, sources, sinks, lambda _: 1, h)

    print("Correct answer:", mf)

    if topsort:
        run_test_with_topsort(input, mf, weighted_push_relabel, h=h)
    else:
        run_test(input, mf, weighted_push_relabel, h=h, weight_fn=weight_fn)

    print(mf)


@pytest.mark.weighted_push_relabel
@pytest.mark.large_graph  # Its not really, it's just really slow
def test_compare_random_dags_with_correct_answer():
    for i in range(1_000):
        dag = make_random_dag()

        print(f"Attempt {i} with graph:")
        print(dag)
        print()

        compare_answers(dag)


@pytest.mark.weighted_push_relabel
def test_random_dag_with_low_h():
    dag = r"""25 37 0 24
0-(11)>1
0-(24)>2
0-(3)>3
0-(24)>4
1-(17)>5
2-(5)>1
2-(7)>6
3-(5)>7
3-(1)>8
4-(20)>9
5-(20)>10
5-(15)>11
6-(3)>5
6-(5)>11
7-(7)>11
8-(7)>12
9-(1)>13
9-(24)>14
10-(2)>16
10-(5)>17
11-(5)>17
11-(20)>18
12-(15)>18
13-(19)>19
14-(15)>13
14-(7)>15
14-(9)>20
15-(7)>20
16-(5)>21
17-(15)>21
18-(15)>22
19-(15)>12
19-(15)>23
20-(19)>19
21-(19)>24
22-(20)>24
23-(19)>24"""

    print(dag)
    print()

    compare_answers(dag, h=6)  # fails on 6 with "approximate flow"


example_dag = r"""7 10 1 6
0-(1)>1
1-(8)>3
1-(4)>5
2-(8)>3
2-(6)>6
3-(7)>4
3-(3)>5
4-(8)>5
4-(4)>6
5-(9)>6"""


@pytest.mark.weighted_push_relabel
@bench
def test_example_dag_no_toppy():
    compare_answers(example_dag, topsort=False)


@pytest.mark.weighted_push_relabel
@bench
def test_example_dag_toppy():
    compare_answers(example_dag, topsort=True)


expander_hieararchytfj = r"""23 51 0 19
1-(20)>4
3-(4)>5
3-(3)>8
1-(18)>11
2-(24)>9
11-(11)>12
11-(7)>13
10-(28)>13
7-(10)>10
7-(22)>14
16-(6)>19
16-(12)>18
17-(11)>21
17-(7)>22
11-(18)>20
0-(64)>1
1-(17)>3
3-(17)>2
2-(28)>0
9-(11)>8
8-(14)>10
10-(4)>9
10-(16)>11
11-(22)>9
4-(27)>6
6-(26)>7
7-(15)>4
7-(6)>5
5-(20)>4
12-(17)>13
13-(17)>16
13-(17)>14
14-(18)>17
17-(9)>16
16-(15)>12
16-(26)>15
15-(15)>12
19-(27)>18
18-(18)>21
21-(16)>22
22-(6)>18
21-(18)>19
21-(8)>20
20-(21)>19
11-(21)>2
10-(9)>5
6-(17)>1
22-(24)>14
19-(7)>15
20-(11)>0
21-(26)>7"""


@pytest.mark.weighted_push_relabel
@bench
def test_example_dag_expandeerererr_with_weight_fn():
    g, sources, sinks = parse_input(expander_hieararchytfj, 10_000)
    h = len(g.V) // 4
    mf, _ = wrap_correct(g, g.c, sources, sinks, lambda _: 1, h)

    print("h:", h)
    print("Correct answer:", mf)

    def weight_fn(e: Edge):
        return abs(e.u - e.v)

    run_test(
        expander_hieararchytfj, mf, weighted_push_relabel, h=h, weight_fn=weight_fn
    )


@pytest.mark.weighted_push_relabel
@bench
def test_example_dag_expandeerererr_without_weight_fn():
    g, sources, sinks = parse_input(expander_hieararchytfj, 10_000)
    h = len(g.V) // 7
    mf, _ = wrap_correct(g, g.c, sources, sinks, lambda _: 1, h)

    print("h:", h)
    print("Correct answer:", mf)
    run_test(expander_hieararchytfj, mf, weighted_push_relabel, h=h)


dimacs = """22 72 0 22
16-(17)>19
19-(17)>16
9-(16)>12
12-(16)>9
2-(31)>14
14-(31)>2
5-(42)>10
10-(42)>5
11-(23)>13
13-(23)>11
19-(14)>15
15-(14)>19
12-(43)>17
17-(43)>12
11-(8)>16
16-(8)>11
21-(28)>7
7-(28)>21
14-(17)>5
5-(17)>14
14-(45)>19
19-(45)>14
8-(4)>5
5-(4)>8
10-(21)>4
4-(21)>10
11-(19)>1
1-(19)>11
3-(10)>18
18-(10)>3
3-(33)>4
4-(33)>3
11-(35)>5
5-(35)>11
22-(38)>6
6-(38)>22
4-(10)>7
7-(10)>4
16-(12)>9
9-(12)>16
21-(30)>8
8-(30)>21
15-(10)>22
22-(10)>15
13-(42)>8
8-(42)>13
4-(43)>14
14-(43)>4
21-(45)>17
17-(45)>21
4-(31)>0
0-(31)>4
9-(19)>3
3-(19)>9
13-(13)>6
6-(13)>13
4-(15)>19
19-(15)>4
22-(36)>10
10-(36)>22
9-(21)>0
0-(21)>9
12-(18)>11
11-(18)>12
11-(6)>17
17-(6)>11
11-(1)>18
18-(1)>11
9-(6)>15
15-(6)>9
18-(11)>5
5-(11)>18"""


@pytest.mark.weighted_push_relabel
@bench
def test_dimacs():
    compare_answers(dimacs)


@pytest.mark.weighted_push_relabel
@bench
def test_dimacs_with_weight_fn():
    in_flow_solution = set(
        [
            Edge(id=7, u=5, v=10, c=42, forward=True),
            Edge(id=9, u=11, v=13, c=23, forward=True),
            Edge(id=11, u=19, v=15, c=14, forward=True),
            Edge(id=16, u=16, v=11, c=8, forward=True),
            Edge(id=19, u=14, v=5, c=17, forward=True),
            Edge(id=26, u=4, v=10, c=21, forward=True),
            Edge(id=29, u=3, v=18, c=10, forward=True),
            Edge(id=36, u=6, v=22, c=38, forward=True),
            Edge(id=40, u=9, v=16, c=12, forward=True),
            Edge(id=43, u=15, v=22, c=10, forward=True),
            Edge(id=47, u=4, v=14, c=43, forward=True),
            Edge(id=52, u=0, v=4, c=31, forward=True),
            Edge(id=53, u=9, v=3, c=19, forward=True),
            Edge(id=55, u=13, v=6, c=13, forward=True),
            Edge(id=57, u=4, v=19, c=15, forward=True),
            Edge(id=60, u=10, v=22, c=36, forward=True),
            Edge(id=62, u=0, v=9, c=21, forward=True),
            Edge(id=69, u=9, v=15, c=6, forward=True),
            Edge(id=71, u=18, v=5, c=11, forward=True),
        ]
    )

    def weight_fn(e: Edge):
        return 1 if e in in_flow_solution else 25

    compare_answers(dimacs, weight_fn=weight_fn)


@pytest.mark.weighted_push_relabel
@bench
def test_geeks_for_geeks_weight_fn_no():
    compare_answers(GEEKS_FOR_GEEKS_GRAPH)


@pytest.mark.weighted_push_relabel
@bench
def test_geeks_for_geeks_weight_fn_with_w():
    in_flow_solution = set(
        [
            Edge(id=1, u=0, v=1, c=16, forward=True),
            Edge(id=2, u=0, v=2, c=13, forward=True),
            Edge(id=5, u=1, v=3, c=12, forward=True),
            Edge(id=6, u=2, v=4, c=14, forward=True),
            Edge(id=8, u=4, v=3, c=7, forward=True),
            Edge(id=9, u=3, v=5, c=20, forward=True),
            Edge(id=10, u=4, v=5, c=4, forward=True),
        ]
    )

    def weight_fn(e: Edge):
        return 1 if e in in_flow_solution else 100

    compare_answers(GEEKS_FOR_GEEKS_GRAPH, weight_fn=weight_fn)


@pytest.mark.weighted_push_relabel
@bench
def test_weight_function_weight_impact_example():
    graph = """3 2 1 2
0-(1)>1
1-(1)>2"""

    def weight_fn(e: Edge):
        return 8 if (e.u, e.v) == (0, 1) else 1

    compare_answers(graph, weight_fn=weight_fn)


@pytest.mark.weighted_push_relabel
@bench
def test_low_h_in_ranked_graph():
    graph = """14 48 0 13
0-(1)>1
0-(1)>2
0-(1)>3
0-(1)>4
0-(1)>5
0-(1)>6
1-(1)>7
1-(1)>8
1-(1)>9
1-(1)>10
1-(1)>11
1-(1)>12
2-(1)>7
2-(1)>8
2-(1)>9
2-(1)>10
2-(1)>11
2-(1)>12
3-(1)>7
3-(1)>8
3-(1)>9
3-(1)>10
3-(1)>11
3-(1)>12
4-(1)>7
4-(1)>8
4-(1)>9
4-(1)>10
4-(1)>11
4-(1)>12
5-(1)>7
5-(1)>8
5-(1)>9
5-(1)>10
5-(1)>11
5-(1)>12
6-(1)>7
6-(1)>8
6-(1)>9
6-(1)>10
6-(1)>11
6-(1)>12
7-(1)>13
8-(1)>13
9-(1)>13
10-(1)>13
11-(1)>13
12-(1)>13"""

    compare_answers(graph, h=1)


@pytest.mark.weighted_push_relabel
@bench
def test_uses_reverse_edge():
    graph = """6 7 0 5
0-(1)>1
0-(1)>3
1-(1)>2
3-(1)>2
1-(1)>4
4-(1)>5
2-(1)>5"""

    compare_answers(graph, h=3)
