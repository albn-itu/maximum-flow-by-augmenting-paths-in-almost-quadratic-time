from tests.scripts.generator_dag import make_random_dag
from tests.utils import parse_input, run_test_with_topsort, wrap_correct
from src.weighted_push_relabel import weighted_push_relabel
import pytest


def compare_answers(input: str, h: int | None = None):
    g, c, sources, sinks = parse_input(input, 10_000)
    h = h if h is not None else len(g.V)
    mf, _ = wrap_correct(g, c, sources, sinks, lambda _: 1, h)

    print("Correct answer:", mf)

    run_test_with_topsort(input, mf, weighted_push_relabel, h=h)

    print(mf)


@pytest.mark.paper
def test_compare_random_dags_with_correct_answer():
    for i in range(1_000):
        dag = make_random_dag()

        print(f"Attempt {i} with graph:")
        print(dag)
        print()

        compare_answers(dag)


@pytest.mark.paper
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

    compare_answers(dag, h=7)  # fails on 6 with "approximate flow"
