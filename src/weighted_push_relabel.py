from dataclasses import dataclass


@dataclass
class Graph:
    V: list[int]
    E: list[tuple[int, int]]


@dataclass
class Edge:
    """u -> v with capacity c"""
    u: int
    v: int
    c: int

    forward: bool

    def c_f(self, f: dict["Edge", int]) -> int:
        if self.forward:
            return self.c - f.get(self, 0)
        else:
            return f.get(self, 0)

    def reversed(self):
        return Edge(u=self.v, v=self.u, c=self.c, forward=not self.forward)

    def __hash__(self):
        return hash((self.u, self.v))


def weighted_push_relabel(G, c, sources, sinks, w, h):
    """
    G: a graph (V, E)
    c: capacities for each edge
    sources: source nodes providing flow
    sinks: sink nodes receiving flow
    w: weight function for edges
    h: height parameter
    """

    outgoing = make_outgoing(G, c)

    f = {}

    l = {v: 0 for v in G.V}
    alive = set(G.V)
    admissible = set()

    def relabel(v):
        l[v] += 1

        if l[v] > 9 * h:
            alive.remove(v)
            return

        for e in outgoing[v]:
            if l[v] % w(e) != 0:
                continue

            x, y = (e.u, e.v)
            if l[x] - l[y] >= 2 * w(e) and e.c_f(f) > 0:
                admissible.add(e)
            else:
                admissible.discard(e)


def make_outgoing(G: Graph, c) -> dict[int, list[Edge]]:
    outgoing = {v: [] for v in G.V}
    for u, v in G.E:
        outgoing[u].append(Edge(u=u, v=v, c=c[(u, v)], forward=True))
    return outgoing
