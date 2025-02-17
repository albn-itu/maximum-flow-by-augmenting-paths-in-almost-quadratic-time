from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import override

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

    def forward_edge(self):
        return self if self.forward else self.reversed()

    @override
    def __hash__(self) -> int:
        return hash(self.id)

    @override
    def __str__(self) -> str:
        return f"{self.u} -({self.c})> {self.v}"


@dataclass
class WeightedPushRelabel:
    # Parameters from paper
    G: Graph
    c: list[int]
    sources: dict[Vertex, int]
    sinks: dict[Vertex, int]
    w: Callable[[Edge], int]
    h: int

    # State from paper
    f: dict[Edge, int] = field(default_factory=defaultdict[Edge, int])
    l: dict[Vertex, int] = field(default_factory=dict)
    alive: set[Vertex] = field(default_factory=set)
    admissible: set[Edge] = field(default_factory=set)

    # Our state
    outgoing: dict[Vertex, set[Edge]] = field(default_factory=dict)
    incoming: dict[Vertex, set[Edge]] = field(default_factory=dict)

    def solve(self) -> tuple[int, dict[Edge, int]]:
        self.outgoing, self.incoming = make_outgoing_incoming(self.G, self.c)

        self.f = defaultdict(int)
        self.l = {v: 0 for v in self.G.V}
        self.alive = set(self.G.V)
        self.admissible = set()

        print(f"Initial state: {self}")

        # Shorthands
        w, h = self.w, self.h
        f, l, alive, admissible, c_f = (
            self.f,
            self.l,
            self.alive,
            self.admissible,
            self.c_f,
        )

        def relabel(v: Vertex):
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
                print(f"Relabeling {v}")
                relabel(v)

            if (s := self.find_alive_vertex_with_excess()) is not None:
                P = self.trace_path(s)
                assert P is not None, "Path not found, but we always expect one."

                t = P[-1].end()

                c_augment = min(
                    self.residual_source(s),
                    self.residual_sink(t),
                    min(c_f(e) for e in P),
                )

                for e in P:
                    if e.forward:
                        f[e] += c_augment
                    else:
                        f[e.forward_edge()] -= c_augment

                    # "Adjust ..." - is this automatically done via c_f()?

                    if c_f(e) == 0:
                        admissible.discard(e)
            else:
                return self.amount_of_routed_flow(f), f

    def c_f(self, e: Edge):
        f_e = self.f.get(e.forward_edge(), 0)
        if e.forward:
            return e.c - f_e
        else:
            return f_e

    def absorption(self, v: Vertex) -> int:
        return min(self.net_flow(v) + self.sources[v], self.sinks[v])

    def excess(self, v: Vertex) -> int:
        return self.net_flow(v) + self.sources[v] - self.absorption(v)

    # This is exactly B^TG(v) from the paper - or alternatively "-f^out(v)".
    def net_flow(self, v: Vertex) -> int:
        recv = sum(self.f.get(e, 0) for e in self.incoming[v])
        send = sum(self.f.get(e, 0) for e in self.outgoing[v])
        return recv - send

    def residual_source(self, v: Vertex) -> int:
        """Corresponds to Δ_f(s)"""
        return self.excess(v)

    def residual_sink(self, v: Vertex) -> int:
        """Corresponds to ∇_f(t)"""
        return self.sinks[v] - self.absorption(v)

    # Black box for line 15 of Alg. 1 in the paper. Currently runs in inefficient O(n) time.
    def find_alive_vertex_with_excess(self) -> Vertex | None:
        # TODO: Make fast.
        for v in self.alive:
            if self.residual_source(v) > 0:
                return v
        return None

    def trace_path(self, s: Vertex) -> list[Edge] | None:
        parent: dict[Vertex, Edge] = {}

        stack = [s]

        while len(stack) > 0:
            v = stack.pop()

            # If we have reached the sink, we are done
            if self.sinks[v] > 0:
                path: list[Edge] = []
                while v in parent.keys():
                    path.append(parent[v])
                    v = parent[v].start()
                path.reverse()
                return path

            for e in self.outgoing[v]:
                if e not in self.admissible:
                    continue
                stack.append(e.end())
                parent[e.end()] = e

        return None

    def amount_of_routed_flow(self, f: dict[Edge, int]) -> int:
        amount = 0
        for s in self.sources:
            if self.sources[s] > 0:
                amount += sum(f.get(e, 0) for e in self.outgoing[s])
        return amount


def weighted_push_relabel(
    G: Graph,
    c: list[int],
    sources: list[int],
    sinks: list[int],
    w: Callable[[Edge], int],
    h: int,
) -> tuple[int, dict[Edge, int]]:
    """
    G: a graph (V, E)
    c: capacities for each edge
    sources: source nodes providing flow
    sinks: sink nodes receiving flow
    w: weight function for edges
    h: height parameter
    """
    _sources = {v: sources[i] for i, v in enumerate(G.V)}
    _sinks = {v: sinks[i] for i, v in enumerate(G.V)}
    return WeightedPushRelabel(G, c, _sources, _sinks, w, h).solve()


# Black box for line 13 of Alg. 1 in the paper. Currently runs in inefficient O(n^2) time.
# TODO: Make fast.
class AliveSaturatedVerticesWithNoAdmissibleOutEdges:
    instance: WeightedPushRelabel

    # Overriden in __iter__
    cur_iteration: list[Vertex] = []
    returned_some: bool = False

    def __init__(self, instance: WeightedPushRelabel):
        self.instance = instance

    def __iter__(self):
        self.cur_iteration = list(self.instance.alive)
        self.returned_some = False
        return self

    def __next__(self) -> Vertex:
        while self.cur_iteration:
            v = self.cur_iteration.pop()

            is_saturated = self.instance.residual_sink(v) == 0
            has_admissible = any(
                e in self.instance.admissible for e in self.instance.outgoing[v]
            )

            if is_saturated and not has_admissible:
                self.returned_some = True
                return v

        if self.returned_some:
            self.cur_iteration = list(self.instance.alive)
            self.returned_some = False
            return self.__next__()

        raise StopIteration


def make_outgoing_incoming(G: Graph, c: list[int]) -> tuple[dict[Vertex, set[Edge]], dict[Vertex, set[Edge]]]:
    outgoing: dict[Vertex, set[Edge]] = {u: set() for u in G.V}
    incoming: dict[Vertex, set[Edge]] = {u: set() for u in G.V}

    for i, ((u, v), cap) in enumerate(zip(G.E, c)):
        e = Edge(id=i + 1, u=u, v=v, c=cap, forward=True)
        e_rev = e.reversed()

        outgoing[u].add(e)
        outgoing[v].add(e_rev)
        incoming[u].add(e_rev)
        incoming[v].add(e)

    return outgoing, incoming


if __name__ == "__main__":
    mf, res = weighted_push_relabel(
        Graph(V=[0, 1, 2], E=[(0, 1), (1, 2)]),
        c=[1, 1],
        sources=[1, 0, 0],
        sinks=[0, 0, 1],
        w=lambda e: 1,
        h=3,
    )

    print(f"Result: {mf} total flow")
    for e, f in res.items():
        print(f"  {f} flow via {e}")
