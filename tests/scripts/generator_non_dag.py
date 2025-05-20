import random
import pathlib
import sys

from src.flows.classic_push_relabel import PushRelabel
from src.utils import Graph, export_russian_graph, parse_input


def generate_random_graph_nm(n: int, m: int, seed: int | None = None) -> Graph:
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

    # Create a number of ranks to spread the between vertices across
    vertices_between = list(range(1, n - 1))
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
        cap = random.randint(1, 100)
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

    # Add random edges until we reach m edges
    while len(edges) < m:
        u, v = -1, -1
        while u == v:
            u = random.randint(0, n - 2)  # Exclude the sink
            v = random.randint(1, n - 1)  # Include the sink
        add_edge(u, v)

    return Graph(V=list(range(n)), E=edges, c=capacities)


def doubling_range(start: int, end: int):
    i = start
    while i <= end:
        yield i
        i *= 2


def generate_fully_connected_graph(seed: int, num_vertices: int):
    MIN_WEIGHT = 2
    MAX_WEIGHT = 2 * num_vertices

    weight = random.randint(MIN_WEIGHT, MAX_WEIGHT)

    adjacency = []

    for i in range(num_vertices):
        for j in range(num_vertices):
            if i == j:
                continue
            adjacency.append((i, j, weight))

    s, t = 0, num_vertices - 1

    lines = [f"{num_vertices} {len(adjacency)} {s} {t}"]
    for u, v, cap in adjacency:
        lines.append(f"{u}-({cap})>{v}")

    return "\n".join(lines)


if __name__ == "__main__":
    # for _ in range(100):
    #     print(make_random_dag())
    #     break
    seed = random.randrange(sys.maxsize)
    print("Seed:", seed)

    # ns = [256]
    # max_n = 64
    ns = list(doubling_range(2, 64))
    max_n = max(ns)
    # ms = list(doubling_range(100, max_n**2))
    # if max_n**2 != max(ms):
    #     ms.append(max_n**2)

    graphs = 0
    for n in ns:
        # actual_ms = [m for m in ms if m >= n - 1]
        # actual_ms.extend(list(doubling_range(n - 1, 100)))
        # actual_ms = []
        # c = 1
        # while c * n <= n**2:
        #     actual_ms.append(c * n)
        #     c *= 2

        # for m in actual_ms:
        for i in range(3):
            if graphs % 100 == 0:
                print(f"Generating graph {graphs}")

            try:
                g = generate_fully_connected_graph(seed, n)
            except ValueError as e:
                print(f"Error generating graph {graphs}: {n} {i} {seed}")
                raise e

            g, _, _ = parse_input(g, 0)

            s = g.V[0]
            t = g.V[-1]
            expected = PushRelabel(g).max_flow(s, t)

            filename = f"{graphs:04}_{n}_{len(g.E)}_{expected}.txt"
            path = pathlib.Path("tests/data/fully_connected_same_cap")
            path.mkdir(parents=True, exist_ok=True)
            with open(path / filename, "w") as f:
                f.write(export_russian_graph(g, s, t))

            graphs += 1
