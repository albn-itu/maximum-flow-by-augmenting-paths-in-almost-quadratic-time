from collections.abc import Callable
from dataclasses import dataclass

type Vertex = int

@dataclass
class Graph:
    V: list[Vertex]
    E: list[tuple[Vertex, Vertex]]


@dataclass
class Edge:
    """u -> v with capacity c"""
    id: int

    u: Vertex
    v: Vertex
    c: int

    forward: bool

    def start(self):
        return self.u

    def end(self):
        return self.v

    def reversed(self):
        return Edge(u=self.v, v=self.u, c=self.c, forward=not self.forward, id=-self.id)

    def __hash__(self):
        return hash(self.id)


@dataclass
class WeightedPushRelabel:
    # Parameters from paper
    G: Graph
    c: dict[tuple[Vertex, Vertex], int]
    sources: dict[Vertex, int]
    sinks: dict[Vertex, int]
    w: Callable[[Edge], int]
    h: int

    # State from paper
    f: dict[Edge, int] = {}
    l: dict[Vertex, int] = {}
    alive: set[Vertex] = set()
    admissible: set[Edge] = set()

    # Our state
    outgoing: dict[Vertex, set[Edge]] = {}
    incoming: dict[Vertex, set[Edge]] = {}

    def solve(self):
        self.outgoing, self.incoming = make_outgoing_incoming(self.G, self.c)

        self.f = {}
        self.l = {v: 0 for v in self.G.V}
        self.alive = set(self.G.V)
        self.admissible = set()

        # Shorthands
        w, h = self.w, self.h
        f, l, alive, admissible, c_f = self.f, self.l, self.alive, self.admissible, self.c_f

        def relabel(v):
            l[v] += 1

            if l[v] > 9 * h:
                alive.remove(v)
                return

            for e in (e for e in self.outgoing[v] if l[v] % w(e) == 0):
                x, y = e.start(), e.end()
                if l[x] - l[y] >= 2 * w(e) and c_f(e) > 0:
                    admissible.add(e)
                else:
                    admissible.discard(e)

        while True:
            for v in AliveSaturatedVerticesWithNoAdmissibleOutEdges(self):
                print("Relabeling v")
                relabel(v)

            if (s := self.find_alive_vertex_with_excess()) is not None:
                P = self.trace_path()
                t = P[-1].end()

                c_augment = min(self.residual_source(s),
                                self.residual_sink(t),
                                min(c_f(e) for e in P))

                for e in P:
                    if e.forward:
                        f[e] += c_augment
                    else:
                        f[e.reversed()] -= c_augment

                    # "Adjust ..." - is this automatically done via c_f()?

                    if c_f(e) == 0:
                        admissible.discard(e)
            else:
                return f

    def c_f(self, e: Edge):
        if e.forward:
            return e.c - self.f.get(e, 0)
        else:
            return self.f.get(e, 0)

    def absorption(self, v):
        # see def. of f^out in the paper (p. 17) for why we can use -f_out below - just substitution
        return min(-self.f_out(v) + self.sources[v], self.sinks[v])

    def excess(self, v):
        # recv = sum(f.get(e, 0) for e in incoming[v])
        # send = sum(f.get(e, 0) for e in outgoing[v])
        # return recv - send
        # Above is logically simple variant. Below is def. from paper.
        return -self.f_out(v) + self.sources[v] - self.absorption(v)

    def f_out(self, v):
        return sum(self.f.get(e, 0) for e in self.outgoing[v])

    def residual_source(self, v):
        """Corresponds to Δ_f(s)"""
        return self.excess(v)

    def residual_sink(self, v):
        """Corresponds to ∇_f(t)"""
        return self.sinks[v] - self.absorption(v)

    # Black box for line 15 of Alg. 1 in the paper. Currently runs in inefficient O(n) time.
    def find_alive_vertex_with_excess(self):
        # TODO: Make fast.
        for v in self.alive:
            if self.residual_source(v) > 0:
                return v
        return None

    def trace_path(self) -> list[Edge]:
        raise NotImplementedError


def weighted_push_relabel(G, c, sources, sinks, w, h):
    """
    G: a graph (V, E)
    c: capacities for each edge
    sources: source nodes providing flow
    sinks: sink nodes receiving flow
    w: weight function for edges
    h: height parameter
    """
    return WeightedPushRelabel(G, c, sources, sinks, w, h).solve()


# Black box for line 13 of Alg. 1 in the paper. Currently runs in inefficient O(n^2) time.
# TODO: Make fast.
class AliveSaturatedVerticesWithNoAdmissibleOutEdges:
    def __init__(self, instance: WeightedPushRelabel):
        self.instance = instance

    def __iter__(self):
        self.cur_iteration = list(self.instance.alive)
        self.returned_some = False
        return self

    def __next__(self):
        while self.cur_iteration:
            v = self.cur_iteration.pop()

            is_saturated = self.instance.residual_sink(v) == 0
            has_admissible = any(e in self.instance.admissible for e in self.instance.outgoing[v])

            if is_saturated and not has_admissible:
                self.returned_some = True
                return v

        if self.returned_some:
            self.cur_iteration = list(self.instance.alive)
            self.returned_some = False
            return self.__next__()

        raise StopIteration


def make_outgoing_incoming(G: Graph, c) -> tuple[dict[int, set[Edge]], dict[int, set[Edge]]]:
    incoming = {v: set() for v in G.V}
    outgoing = {u: set() for u in G.V}
    for i, (u, v) in enumerate(G.E):
        e = Edge(id=i+1, u=u, v=v, c=c[(u, v)], forward=True)
        outgoing[e.start()].add(e)
        incoming[e.end()].add(e)
    return outgoing, incoming
