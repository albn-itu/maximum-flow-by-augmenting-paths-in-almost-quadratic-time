from collections.abc import Callable
from dataclasses import dataclass
from collections import deque


@dataclass
class Graph:
    V: list[int]
    E: list[tuple[int, int]]


type Vertex = int


@dataclass
class Edge:
    """u -> v with capacity c"""
    u: Vertex
    v: Vertex
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
        f, l, alive, admissible = self.f, self.l, self.alive, self.admissible

        def relabel(v):
            l[v] += 1

            if l[v] > 9 * h:
                alive.remove(v)
                return

            for e in self.outgoing[v]:
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

        while True:
            for v in AliveSaturatedVerticesWithNoAdmissibleOutEdges(self):
                print("Relabeling v")
                relabel(v)

            break
            # queue = deque(alive)
            # while queue:
            #     v = queue.popleft()

    def absorption(self, v, f):
        # see def. of f^out in the paper (p. 17) for why we can use -f_out below
        return min(-self.f_out(v, f) + self.sources[v], self.sinks[v])

    def excess(self, v, f):
        # recv = sum(f.get(e, 0) for e in incoming[v])
        # send = sum(f.get(e, 0) for e in outgoing[v])
        # return recv - send
        # Above is logically simple variant. Below is def. from paper.
        return -self.f_out(v, f) + self.sources[v] - self.absorption(v, f)

    def f_out(self, v, f):
        return sum(f.get(e, 0) for e in self.outgoing[v])

    def residual_source(self, v, f):
        """Corresponds to Δ_f(s)"""
        return self.excess(v, f)

    def residual_sink(self, v, f):
        """Corresponds to ∇_f(t)"""
        return self.sinks[v] - self.absorption(v, f)


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

            is_saturated = self.instance.residual_sink(v, self.instance.f) == 0
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
    for u, v in G.E:
        assert (u, v) not in outgoing[u] and (
            u, v) not in incoming[v], "Parallel edges are not supported yet."
        e = Edge(u=u, v=v, c=c[(u, v)], forward=True)
        outgoing[u].add(e)
        incoming[v].add(e)
    return outgoing, incoming
