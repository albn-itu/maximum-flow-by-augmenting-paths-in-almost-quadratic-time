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

    def start(self):
        return self.u

    def to(self):
        return self.v

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

    outgoing, incoming = make_outgoing_incoming(G, c)

    def f_out(v, f):
        return sum(f.get(e, 0) for e in outgoing[v])

    def absorption(v, f):
        # see def. of f^out in the paper (p. 17) for why we can use -f_out below
        return min(-f_out(v, f) + sources[v], sinks[v])

    def excess(v, f):
        # recv = sum(f.get(e, 0) for e in incoming[v])
        # send = sum(f.get(e, 0) for e in outgoing[v])
        # return recv - send
        # Above is logically simple variant. Below is def. from paper.
        return -f_out(v, f) + sources[v] - absorption(v, f)

    def residual_source(v, f): 
        """Corresponds to Δ_f(s)"""
        return excess(v, f)

    def residual_sink(v, f):
        """Corresponds to ∇_f(t)"""
        return sinks[v] - absorption(v, f)

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

    # main loop:
    #   first loop: while there is an alive, saturated vertex with no admissible edges, ...
    #   second loop: while there is an alive vertex with excess

    # for v in list(alive):
    #     if any(e in admissible for e in outgoing[v]):
    #         continue




def make_outgoing_incoming(G: Graph, c) -> tuple[dict[int, set[Edge]], dict[int, set[Edge]]]:
    incoming = {v: set() for v in G.V}
    outgoing = {u: set() for u in G.V}
    for u, v in G.E:
        assert (u, v) not in outgoing[u] and (u, v) not in incoming[v], "Parallel edges are not supported yet."
        e = Edge(u=u, v=v, c=c[(u, v)], forward=True)
        outgoing[u].add(e)
        incoming[v].add(e)
    return outgoing, incoming
