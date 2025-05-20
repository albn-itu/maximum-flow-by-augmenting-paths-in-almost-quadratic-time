from collections import deque, defaultdict
from dataclasses import dataclass, field

from src.flows.utils import finish_benchmark, benchmark_iteration
from src.utils import Edge, Vertex, Graph

INF = 1000000000


@dataclass
class CapacityScaling:
    g: Graph
    s: Vertex
    t: Vertex

    flow: defaultdict[Edge, int] = field(default_factory=defaultdict)

    def __init__(self, G: Graph):
        self.g = G

    def c_f(self, edge: Edge) -> int:
        if edge.forward:
            return edge.c - self.flow[edge]
        else:
            return self.flow[edge.reversed()]

    def bfs(self, delta: int) -> tuple[int, dict[Vertex, Edge] | None]:
        parent: dict[Vertex, Edge] = {}

        q: deque[tuple[Vertex, int]] = deque()
        q.append((self.s, INF))

        visited = {self.s}

        while q:
            u, flow = q.popleft()

            for edge in self.g.outgoing[u]:
                v = edge.v

                if v in visited:
                    continue

                cap = self.c_f(edge)

                if cap >= delta:
                    visited.add(v)
                    parent[v] = edge
                    new_flow = min(flow, cap)
                    if v == self.t:
                        return new_flow, parent
                    q.append((v, new_flow))

        return 0, None

    def max_flow(self, s: Vertex, t: Vertex) -> int:
        self.s = s
        self.t = t

        self.flow = defaultdict(int)

        flow = 0

        max_capacity: int = max(self.g.c)
        delta = 1
        while delta * 2 <= max_capacity:
            delta *= 2

        while delta >= 1:
            while True:
                new_flow, parent = self.bfs(delta)

                if new_flow == 0 or parent is None:
                    break

                flow += new_flow

                cur = self.t
                edge_updates = 0
                while cur != self.s:
                    edge = parent[cur]
                    cur = edge.u

                    if edge.forward:
                        self.flow[edge] = self.flow[edge] + new_flow
                    else:
                        edge = edge.reversed()
                        self.flow[edge] = self.flow[edge] - new_flow

                    edge_updates += 2
                benchmark_iteration("capacity", edge_updates)
            delta //= 2

        finish_benchmark("capacity", flow)

        return flow
