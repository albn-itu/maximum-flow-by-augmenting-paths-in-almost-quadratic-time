import random
import pathlib
from dataclasses import dataclass
import sys

from src.classic_push_relabel import PushRelabel
from src.utils import Graph, export_russian_graph


@dataclass
class DagParams:
    min_per_rank: int  # Nodes/Rank: How 'fat' the DAG should be
    max_per_rank: int
    min_ranks: int  # Ranks: How 'tall' the DAG should be
    max_ranks: int
    percent: float  # Chance of having an Edge
    min_weight: int
    max_weight: int

    num_edges: int
    seed: int


def generate_random_dag(config: DagParams):
    random.seed(config.seed)

    source = 0
    nodes = 1
    node_counter = 1

    MIN_PER_RANK = config.min_per_rank
    MAX_PER_RANK = config.max_per_rank
    MIN_RANKS = config.min_ranks
    MAX_RANKS = config.max_ranks
    PERCENT = config.percent
    MIN_WEIGHT = config.min_weight
    MAX_WEIGHT = config.max_weight

    ranks = random.randint(MIN_RANKS, MAX_RANKS)

    adjacency = []
    rank_list = []
    for i in range(ranks):
        if i == ranks - 1:
            sink = node_counter
            node_counter += 1
            nodes += 1
            for j in rank_list[i - 1]:
                weight = random.randint(MIN_WEIGHT, MAX_WEIGHT)
                adjacency.append((j, sink, weight))
            break

        # New nodes of 'higher' rank than all nodes generated till now
        new_nodes = random.randint(MIN_PER_RANK, MAX_PER_RANK)

        list = []
        for j in range(new_nodes):
            if i == 0:
                weight = random.randint(MIN_WEIGHT, MAX_WEIGHT)
                adjacency.append((source, node_counter, weight))
            list.append(node_counter)
            node_counter += 1
        rank_list.append(list)

        # Edges from old nodes ('nodes') to new ones ('new_nodes')
        if i > 0:
            for j in rank_list[i - 1]:
                for k in range(new_nodes):
                    if random.random() <= PERCENT:
                        weight = random.randint(MIN_WEIGHT, MAX_WEIGHT)
                        adjacency.append((j, k + nodes, weight))

        nodes += new_nodes

    num_edge_error = 0.4
    NUM_EDGES = config.num_edges
    # assert NUM_EDGES * (1 - num_edge_error) <= len(adjacency) <= NUM_EDGES * (1 + num_edge_error), f"Want {NUM_EDGES} edges, got {len(adjacency)}"

    lines = [f"{nodes} {len(adjacency)} {source} {sink}"]
    for u, v, cap in adjacency:
        lines.append(f"{u}-({cap})>{v}")

    return "\n".join(lines)


def make_random_dag() -> str:
    def try_generate() -> str:
        SEED = random.randint(0, 1000000)

        config = DagParams(
            num_edges=8,
            min_per_rank=3,
            max_per_rank=5,
            min_ranks=4,
            max_ranks=5,
            percent=0.2,
            min_weight=1,
            max_weight=100,
            seed=SEED,
        )

        try:
            return generate_random_dag(config)
        except:
            print(f"Failed generating with {SEED}, trying again")
            return try_generate()

    return try_generate()


def generate_random_dag_nm(n: int, m: int, seed: int | None = None) -> Graph:
    if n < 2 or m < 1:
        raise ValueError("n and m must be greater than 1 and 0 respectively")
    if m < n - 1:
        raise ValueError("m must be greater than n - 1")

    if seed is not None:
        random.seed(seed)
    else:
        seed = random.randrange(sys.maxsize)
        print("Seed:", seed)
        random.seed(seed)

    source = 0
    sink = n - 1
    vertices_between = list(range(1, n - 1))

    # Create a number of ranks to spread the between vertices across
    ranks = random.randint(1, n - 2) if n > 2 else 1
    rank_list: list[list[int]] = [[source]]
    for i in range(ranks - 1):
        rank_size = random.randint(1, len(vertices_between) // (ranks - i))
        rank = random.sample(vertices_between, rank_size)
        vertices_between = [v for v in vertices_between if v not in rank]
        rank_list.append(rank)
    if len(vertices_between) != 0:
        rank_list.append(vertices_between)
    rank_list.append([sink])

    # Create a list of Edges
    edges: list[tuple[int, int]] = []
    capacities: list[int] = []

    def add_edge(u: int, v: int):
        cap = random.randint(1, m)
        edges.append((u, v))
        capacities.append(cap)

    # First connect the source to the first rank
    for v in rank_list[1]:
        add_edge(source, v)
    # Then connect the last rank to the sink
    for v in rank_list[-2]:
        add_edge(v, sink)
    # Finally connect the ranks together
    for i in range(1, len(rank_list) - 2):
        for u in rank_list[i]:
            v = random.choice(rank_list[i + 1])
            add_edge(u, v)

    # Add random edges between the ranks until we reach m edges
    while len(edges) < m:
        u_rank = random.randint(0, len(rank_list) - 2)
        v_rank = random.randint(u_rank + 1, len(rank_list) - 1)
        u = random.choice(rank_list[u_rank])
        v = random.choice(rank_list[v_rank])
        if u != v:
            add_edge(u, v)

    return Graph(V=list(range(n)), E=edges, c=capacities)


if __name__ == "__main__":
    # for _ in range(100):
    #     print(make_random_dag())
    #     break
    seed = random.randrange(sys.maxsize)
    print("Seed:", seed)

    max_n = 40
    graphs = 1
    for n in range(2, max_n, 2):
        for m in range(n - 1, max_n**2, 100):
            if m != n - 1:
                # round to nearest 100
                m = round(m / 100) * 100

            for i in range(3):
                graphs += 1
                if graphs % 100 == 0:
                    print(f"Generating graph {graphs}")

                try:
                    g = generate_random_dag_nm(n, m, seed)
                except ValueError as e:
                    print(f"Error generating graph {graphs}: {n} {m} {i} {seed}")
                    raise e

                s = g.V[0]
                t = g.V[-1]
                expected = PushRelabel(g).max_flow(s, t)

                filename = f"{graphs:04}_{n}_{m}_{expected}.txt"
                path = pathlib.Path("tests/data/random_dags")
                path.mkdir(parents=True, exist_ok=True)
                with open(path / filename, "w") as f:
                    f.write(export_russian_graph(g, s, t))
