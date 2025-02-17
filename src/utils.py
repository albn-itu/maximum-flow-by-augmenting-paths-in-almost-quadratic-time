from collections import defaultdict
from dataclasses import dataclass
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
        return f"{self.u}-({self.c})>{self.v}"


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
