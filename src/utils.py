from collections import defaultdict
from dataclasses import dataclass, field
import random
from typing import override

from networkx import graph

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


def topological_sort_with_backwards_edges(
    G: Graph,
) -> tuple[list[Vertex], set[tuple[int, int]]]:
    no_cycle_g, backwards_edges = remove_cycles(G)
    order = topological_sort(no_cycle_g)

    return (order, backwards_edges)


def remove_cycles(
    G: Graph,
) -> tuple[Graph, set[tuple[int, int]]]:
    """
    Create a new graph without cycles
    """
    adj: dict[Vertex, set[Vertex]] = defaultdict(set)
    for u, v in G.E:
        adj[u].add(v)

    edges_to_remove: set[tuple[int, int]] = set()
    visited: set[int] = set()
    in_progress: set[int] = set()

    def dfs(vertex: int, path: list[int] | None = None) -> bool:
        """
        Depth-first search to detect cycles.

        Args:
            vertex: Current vertex being explored
            path: Path taken to reach the current vertex

        Returns:
            True if a cycle was detected and removed, False otherwise
        """
        if path is None:
            path = []

        # Already completely explored this vertex
        if vertex in visited:
            return False

        # Cycle detected
        if vertex in in_progress:
            # Remove the last edge in the cycle
            u = path[-1]
            v = vertex

            if (u, v) not in edges_to_remove:
                edges_to_remove.add((u, v))
                print(f"Removed edge: {u} -> {v}")

            return True

        in_progress.add(vertex)
        path.append(vertex)

        # Check all neighbors
        for neighbor in adj[vertex]:
            if dfs(neighbor, path):
                return True

        # Vertex exploration complete
        in_progress.remove(vertex)
        visited.add(vertex)
        _ = path.pop()

        return False

    # Process each vertex that hasn't been visited
    for vertex in G.V:
        if vertex not in visited and vertex not in in_progress:
            dfs(vertex)

    return (
        Graph(
            V=G.V,
            E=[e for e in G.E if e not in edges_to_remove],
            c=[c for e, c in zip(G.E, G.c) if e not in edges_to_remove],
        ),
        edges_to_remove,
    )


def next_multiple_of(n: int, multiple_of: int) -> int:
    if multiple_of == 0:
        return n + 1
    return n + multiple_of - n % multiple_of


def export_russian_graph(G: Graph, s: int, t: int) -> str:
    capacities = G.c

    output = [f"{len(G.V)} {len(G.E)} {s} {t}"]
    for i, e in enumerate(G.E):
        output.append(f"{e[0]}-({capacities[i]})>{e[1]}")

    return "\n".join(output)


def generate_random_capacities(g: Graph) -> Graph:
    capacities = [random.randint(1, 100) for _ in range(len(g.E))]
    return Graph(
        V=g.V,
        E=g.E,
        c=capacities,
    )


def parse_input(input: str, expected: int) -> tuple[Graph, list[int], list[int]]:
    lines = input.strip().split("\n")
    _, _, s, t = map(int, lines[0].split())

    edges: list[tuple[int, int]] = []
    capacities: list[int] = []

    for line in lines[1:]:
        u, rest = line.split("-(")
        cap, v = rest.split(")>")

        edges.append((int(u), int(v)))
        capacities.append(int(cap))

    n = max(max(e[0] for e in edges), max(e[1] for e in edges)) + 1
    vertices = list(range(n))

    sources = [0] * n
    sinks = [0] * n

    sources[s] = expected
    sinks[t] = expected

    return (Graph(vertices, edges, capacities), sources, sinks)
