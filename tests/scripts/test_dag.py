import os
from src import benchmark
from networkx import is_directed_acyclic_graph, MultiDiGraph


def parse_input(input: str) -> list[tuple[int, int]]:
    lines = input.strip().split("\n")
    _, _, _, _ = map(int, lines[0].split())

    edges: list[tuple[int, int]] = []

    for line in lines[1:]:
        u, rest = line.split("-(")
        _, v = rest.split(")>")

        edges.append((int(u), int(v)))

    return edges


def get_graph(input_file: str) -> list[tuple[int, int]]:
    with open(input_file, "r") as f:
        content = f.read()

    return parse_input(content)


def check_if_dag(input_file: str) -> bool:
    edges = get_graph(input_file)
    g = MultiDiGraph(edges)

    return is_directed_acyclic_graph(g)


if __name__ == "__main__":
    base_path = "./tests/data/maxflow"
    files = os.listdir(base_path)

    is_dag: list[str] = []
    not_dag: list[str] = []

    for file in files:
        if file == ".gitignore":
            continue
        file = os.path.join(base_path, file)

        if check_if_dag(file):
            is_dag.append(file)
        else:
            not_dag.append(file)

    print("Is DAG:")
    print("\n".join(is_dag))
    print("Not DAG:")
    print("\n".join(not_dag))
