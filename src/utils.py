from collections import defaultdict
from dataclasses import dataclass, field
import random
from typing import Self, override

from src import benchmark

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
class EdgeSet:
    inner: set[Edge] = field(default_factory=set)

    def add(self, edge: Edge):
        benchmark.register_or_update_s("edge_set.add", 1, lambda x: x + 1)
        self.inner.add(edge)

    def __or__(self, other: Self):
        benchmark.register_or_update_s("edge_set.or", 1, lambda x: x + 1)
        return EdgeSet(self.inner | other.inner)

    def __ror__(self, other: Self):
        benchmark.register_or_update_s("edge_set.ror", 1, lambda x: x + 1)
        return EdgeSet(other.inner | self.inner)

    def __contains__(self, edge: Edge) -> bool:
        benchmark.register_or_update_s("edge_set.contains", 1, lambda x: x + 1)
        return edge in self.inner

    def __iter__(self):
        benchmark.register_or_update_s("edge_set.iter", 1, lambda x: x + 1)

        # Create a generator that tracks each item access
        for edge in self.inner:
            benchmark.register_or_update_s("edge_set.next", 1, lambda x: x + 1)
            yield edge


@dataclass
class EdgeDict:
    inner: dict[Vertex, EdgeSet] = field(default_factory=dict)

    def __getitem__(self, vertex: Vertex) -> EdgeSet:
        benchmark.register_or_update_s("edge_dict.get", 1, lambda x: x + 1)
        return self.inner.get(vertex, EdgeSet(set()))

    def __setitem__(self, vertex: Vertex, edges: EdgeSet):
        benchmark.register_or_update_s("edge_dict.set", 1, lambda x: x + 1)
        self.inner[vertex] = edges

    def __contains__(self, vertex: Vertex) -> bool:
        benchmark.register_or_update_s("edge_dict.contains", 1, lambda x: x + 1)
        return vertex in self.inner

    def values(self) -> list[EdgeSet]:
        benchmark.register_or_update_s("edge_dict.values", 1, lambda x: x + 1)
        return list(self.inner.values())

    def all(self) -> EdgeSet:
        benchmark.register_or_update_s("edge_dict.all", 1, lambda x: x + 1)
        return EdgeSet(
            set(edge for edges in self.inner.values() for edge in edges.inner)
        )


@dataclass
class Graph:
    V: list[Vertex]
    E: list[tuple[Vertex, Vertex]]
    c: list[int]

    # Our state
    outgoing: EdgeDict = field(default_factory=EdgeDict)
    incoming: EdgeDict = field(default_factory=EdgeDict)
    incident: EdgeDict = field(default_factory=EdgeDict)

    def __post_init__(self):
        for u, v in self.E:
            if u == v:
                raise ValueError(f"Self-loop detected: {u} -> {v}")

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

    def all_edges(self) -> EdgeSet:
        """
        Returns all edges in the graph.
        """
        return self.outgoing.all() | self.incoming.all()

    def _all_edges(self) -> set[Edge]:
        """
        Returns all edges in the graph without benchmarking
        """
        return set(
            edge for edges in self.incident.inner.values() for edge in edges.inner
        )


def make_outgoing_incoming(
    G: Graph, c: list[int]
) -> tuple[EdgeDict, EdgeDict, EdgeDict]:
    # This function is a little messy, but it's to ensure we don't fill benchmarks
    outgoing = EdgeDict({u: EdgeSet() for u in G.V})
    incoming = EdgeDict({u: EdgeSet() for u in G.V})

    for i, ((u, v), cap) in enumerate(zip(G.E, c)):
        e = Edge(id=i + 1, u=u, v=v, c=cap, forward=True)
        e_rev = e.reversed()

        outgoing.inner[u].inner.add(e)
        outgoing.inner[v].inner.add(e_rev)
        incoming.inner[u].inner.add(e_rev)
        incoming.inner[v].inner.add(e)

    incident = {
        u: EdgeSet(outgoing.inner[u].inner | incoming.inner[u].inner) for u in G.V
    }

    return outgoing, incoming, EdgeDict(incident)


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
    vertices: set[int] = set()

    for line in lines[1:]:
        u, rest = line.split("-(")
        cap, v = rest.split(")>")

        u, v = int(u), int(v)
        if u == v:
            continue

        vertices.add(u)
        vertices.add(v)

        edges.append((u, v))
        capacities.append(int(cap))

    # Remap vertices such that there are no holes
    sorted_vertices = sorted(vertices)
    vertex_map = {v: i for i, v in enumerate(sorted_vertices)}
    edges = [(vertex_map[u], vertex_map[v]) for u, v in edges]
    s = vertex_map[s]
    t = vertex_map[t]

    n = len(sorted_vertices)
    sources = [0] * n
    sinks = [0] * n

    sources[s] = expected
    sinks[t] = expected

    benchmark.register(
        "instance",
        {
            "n": n,
            "m": len(edges),
            "s": s,
            "t": t,
        },
    )

    return (Graph(list(range(len(sorted_vertices))), edges, capacities), sources, sinks)
