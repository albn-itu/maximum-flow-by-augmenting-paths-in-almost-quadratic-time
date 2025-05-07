from collections import defaultdict
from dataclasses import dataclass, field
from typing import override

type Vertex = int


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
        return f"{self.u}-({self.c})>{self.v}"


@dataclass
class Graph:
    V: list[Vertex]
    E: list[tuple[Vertex, Vertex]]
    c: list[int]

    # Our state
    outgoing: dict[Vertex, set[Edge]] = field(default_factory=dict)
    incoming: dict[Vertex, set[Edge]] = field(default_factory=dict)
    incident: dict[Vertex, set[Edge]] = field(default_factory=dict)

    def __post_init__(self):
        self.outgoing, self.incoming, self.incident = make_outgoing_incoming(
            self, self.c
        )

    def volume(self, v: int) -> int:
        """
        Returns the volume of the vertex v.
        """
        return sum(1 for edge in self.incident[v] if edge.forward)

    def volume_c(self, v: int) -> int:
        """
        Returns the volume of the vertex v.
        """
        return sum(edge.c for edge in self.incident[v] if edge.forward)

    def all_edges(self) -> set[Edge]:
        """
        Returns all edges in the graph.
        """
        return set(edge for edges in self.incident.values() for edge in edges)


def make_outgoing_incoming(
    G: Graph, c: list[int]
) -> tuple[dict[Vertex, set[Edge]], dict[Vertex, set[Edge]], dict[Vertex, set[Edge]]]:
    outgoing: dict[Vertex, set[Edge]] = {u: set() for u in G.V}
    incoming: dict[Vertex, set[Edge]] = {u: set() for u in G.V}

    for i, ((u, v), cap) in enumerate(zip(G.E, c)):
        e = Edge(id=i + 1, u=u, v=v, c=cap, forward=True)
        e_rev = e.reversed()

        outgoing[u].add(e)
        outgoing[v].add(e_rev)
        incoming[u].add(e_rev)
        incoming[v].add(e)

    incident = {u: outgoing[u] | incoming[u] for u in G.V}

    return outgoing, incoming, incident


def topological_sort(G: Graph) -> list[Vertex]:
    adj: dict[Vertex, set[Vertex]] = defaultdict(set)
    for u, v in G.E:
        adj[u].add(v)

    visited: set[Vertex] = set()
    sorted_vertices: list[Vertex] = []

    def dfs(v: Vertex):
        visited.add(v)

        for w in adj[v]:
            if w not in visited:
                dfs(w)

        sorted_vertices.append(v)

    for v in G.V:
        if v not in visited:
            dfs(v)

    return sorted_vertices[::-1]


def next_multiple_of(n: int, multiple_of: int) -> int:
    if multiple_of == 0:
        return n + 1
    return n + multiple_of - n % multiple_of
