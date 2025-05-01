import random
from dataclasses import dataclass
import math
from collections import defaultdict


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
        graph = generate_random_connected_graph()

        phii = phi if phi is not None else 2 ** (-math.sqrt(
            math.log2(graph.n)))

        expanding = is_phi_expander(graph, phii)

        if expanding:
            return graph

    raise Exception("Failed to generate a ϕ-expander")


def expander_decompose(graph: Graph, phi: float):
    vs = list(graph.vertices)

    if (cut := find_phi_sparse_cut(graph, vs, phi)) is None:
        return [graph], set()

    a, b, crossing = split(graph, cut)

    r1, c1 = expander_decompose(a, phi)
    r2, c2 = expander_decompose(b, phi)

    return r1 + r2, crossing | c1 | c2


def is_phi_expander(g: Graph, phi: float):
    checks = []
    vs = list(g.vertices)

    phi_sparse_cut = find_phi_sparse_cut(g, vs, phi)
    expanding = phi_sparse_cut is None

    # quality = min([c["quality"] for c in checks])
    # if phi <= quality:
    #     print(f"SUCCESS: ϕ={phi:.8f} <= {quality:.8f}")
    # else:
    #     print(f"FAILURE: ϕ={phi:.8f} > {quality:.8f}")

    if expanding:
        ...

    return expanding


def is_phi_sparse(g: Graph, phi: float, subset: set[int]):
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

    # checks.append(
    #     {"s": set(s), "sc": set(sc), "sparse cut": phine, "quality": quality})

    return phine


def find_phi_sparse_cut(g: Graph, vs: list[int], phi: float, subset: set[int] = None, i: int = 0):
    if subset is None:
        subset = set()

    if i == len(vs):
        if len(subset) == 0 or len(subset) == len(vs):
            return None

        return subset if is_phi_sparse(g, phi, subset) else None

    subset.add(vs[i])
    if (cut := find_phi_sparse_cut(g, vs, phi, subset, i + 1)) is not None:
        return cut

    subset.remove(vs[i])
    if (cut := find_phi_sparse_cut(g, vs, phi, subset, i + 1)) is not None:
        return cut

    return None


def generate_random_connected_graph():
    g = generate_random_graph()
    while not is_connected(g):
        g = generate_random_graph()
    return g


def generate_random_graph() -> Graph:
    n, m = random.randint(7, 20), random.randint(5, 17)

    adj: dict[int, set[int]] = {i: set() for i in range(n)}
    vs = list(range(n))
    for _ in range(m):
        u, v = random.sample(vs, 2)
        attempts = 0
        while v in adj[u] and (attempts := attempts + 1) < 10:
            u, v = random.sample(vs, 2)
        adj[u].add(v)
    edges = [(u, v) for u in adj for v in adj[u]]

    in_degree = {i: 0 for i in range(n)}
    out_degree = {i: 0 for i in range(n)}
    for u in adj:
        for v in adj[u]:
            in_degree[v] += 1
            out_degree[u] += 1

    degree = {i: in_degree[i] + out_degree[i] for i in range(n)}

    for v in list(adj.keys()):
        if degree[v] == 0:
            adj.pop(v)
            in_degree.pop(v)
            out_degree.pop(v)
            degree.pop(v)

    graph = Graph(
        n=len(adj),
        m=len(edges),
        vertices=set(degree.keys()),
        edges=edges,
        adj=adj,
        in_degree=in_degree,
        out_degree=out_degree,
        degree=degree,
    )

    return graph


def is_connected(graph: Graph):
    adj = defaultdict(list)
    for (u, v) in graph.edges:
        adj[u].append(v)
        adj[v].append(u)

    stack = [next(iter(graph.vertices))]
    visited = set()
    while stack:
        u = stack.pop()

        if u in visited:
            continue

        visited.add(u)

        for v in adj[u]:
            if v in visited:
                continue
            stack.append(v)

    return len(graph.vertices - visited) == 0


def split(graph: Graph, cut: set[int]):
    a_adj, b_adj, crossing = dict(), dict(), set()

    for (u, v) in graph.edges:
        if u in cut:
            a_adj[u] = set()
        if v in cut:
            a_adj[v] = set()
        if u not in cut:
            b_adj[u] = set()
        if v not in cut:
            b_adj[v] = set()

    for (u, v) in graph.edges:
        if u in cut and v in cut:
            a_adj[u].add(v)
        elif u not in cut and v not in cut:
            b_adj[u].add(v)
        else:
            crossing.add((u, v))

    def mk_from_adj(adj: dict[int, int]) -> Graph:
        edges = [(u, v) for u in adj for v in adj[u]]

        in_degree = {i: 0 for i in adj.keys()}
        out_degree = {i: 0 for i in adj.keys()}
        for u in adj:
            for v in adj[u]:
                in_degree[v] += 1
                out_degree[u] += 1

        degree = {i: in_degree[i] + out_degree[i] for i in adj.keys()}

        return Graph(
            n=len(adj),
            m=len(edges),
            vertices=set(adj.keys()),
            edges=edges,
            adj=dict(adj),
            in_degree=in_degree,
            out_degree=out_degree,
            degree=degree,
        )

    a = mk_from_adj(a_adj)
    b = mk_from_adj(b_adj)
    return a, b, crossing


if __name__ == "__main__":
    # graph = generate_random_connected_graph()
    # phi = 1 / (10 * math.log2(graph.n))
    # res = expander_decompose(graph, phi)
    # ...
    expander = generate_phi_expander()

    print("expander", expander)
    print()
    print("\n".join([f"{e[0]}>{e[1]}" for e in expander.edges]))
