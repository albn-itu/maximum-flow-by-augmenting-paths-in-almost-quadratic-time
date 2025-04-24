import random
from dataclasses import dataclass
import math


@dataclass
class Graph:
    n: int
    m: int

    vertices: set[int]
    edges: list[tuple[int, int]]
    adj: dict[int, set[int]]

    in_degree: dict[int, int]
    out_degree: dict[int, int]
    degree: dict[int, int]


def generate_phi_expander(phi=None):
    for _ in range(100_000):
        graph = generate_random_graph()

        phii = phi if phi is not None else 2 ** (-math.sqrt(
            math.log2(graph.n)))

        expanding, quality = is_phi_expander(graph, phii)

        if expanding:
            return graph, quality

    raise Exception("Failed to generate a ϕ-expander")


def is_phi_expander(g: Graph, phi: float):
    checks = []

    def is_phi_sparse(subset: set[int]):
        s, sc = subset, g.vertices - subset
        if len(subset) >= g.n / 2:
            s, sc = sc, s

        volume_s = sum(g.degree[v] for v in s)
        volume_sc = sum(g.degree[v] for v in sc)

        cross_s_to_sc = [e for e in g.edges if e[0] in s and e[1] in sc]
        cross_sc_to_s = [e for e in g.edges if e[0] in sc and e[1] in s]
        e_s_sc, e_sc_s = len(cross_s_to_sc), len(cross_sc_to_s)

        cut_size = min(e_s_sc, e_sc_s)
        vol_size = min(volume_s, volume_sc)
        phine = cut_size < phi * vol_size

        quality = cut_size / vol_size if vol_size > 0 else float("inf")

        checks.append(
            {"s": s, "sc": sc, "sparse cut": phine, "quality": quality})

        return phine

    vs = list(g.vertices)

    def has_phi_sparse_cut(subset: set[int] = set(), i: int = 0):
        if i == len(vs):
            if len(subset) == 0 or len(subset) == len(vs):
                return False

            return is_phi_sparse(subset)

        subset.add(vs[i])
        if has_phi_sparse_cut(subset, i + 1):
            return True

        subset.remove(vs[i])
        if has_phi_sparse_cut(subset, i + 1):
            return True

        return False

    expanding = not has_phi_sparse_cut()

    quality = min([c["quality"] for c in checks])
    if phi <= quality:
        print(f"SUCCESS: ϕ={phi:.8f} <= {quality:.8f}")
    else:
        print(f"FAILURE: ϕ={phi:.8f} > {quality:.8f}")

    return expanding, quality


def generate_random_graph() -> Graph:
    n, m = random.randint(5, 20), random.randint(5, 20)

    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    for _ in range(m):
        u, v = random.sample(range(n), 2)
        adj[u].add(v)
    edges = [(u, v) for u in adj for v in adj[u]]

    in_degree = {i: 0 for i in range(n)}
    out_degree = {i: 0 for i in range(n)}
    for u in adj:
        for v in adj[u]:
            in_degree[v] += 1
            out_degree[u] += 1

    degree = {i: in_degree[i] + out_degree[i] for i in range(n)}

    return Graph(
        n=n,
        m=len(edges),
        vertices=set(range(n)),
        edges=edges,
        adj=adj,
        in_degree=in_degree,
        out_degree=out_degree,
        degree=degree,
    )


if __name__ == "__main__":
    expander, quality = generate_phi_expander()

    print(f"{quality}-expander", expander)
    print()
    print("\n".join([f"{e[0]}>{e[1]}" for e in expander.edges]))
