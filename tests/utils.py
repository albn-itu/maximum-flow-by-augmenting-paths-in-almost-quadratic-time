from src.weighted_push_relabel import Graph


def parse_input(input: str) -> tuple[Graph, list[int], list[int], list[int]]:
    lines = input.strip().split("\n")
    n, _, s, t = map(int, lines[0].split())

    vertices = list(range(n))
    edges: list[tuple[int, int]] = []
    capacities: list[int] = []

    for line in lines[1:]:
        u, rest = line.split("-(")
        cap, v = rest.split(")>")

        edges.append((int(u), int(v)))
        capacities.append(int(cap))

    return (Graph(vertices, edges), capacities, [s], [t])

