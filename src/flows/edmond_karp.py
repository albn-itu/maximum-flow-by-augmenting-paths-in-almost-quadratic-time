from collections import defaultdict, deque
from dataclasses import dataclass, field
from src.flows.utils import finish_benchmark, benchmark_iteration
from src.utils import Edge, Graph, Vertex

INF = 1000000000


@dataclass
class MaxFlow:
    g: Graph
    n: int
    s: Vertex
    t: Vertex

    flow: defaultdict[Edge, int] = field(default_factory=defaultdict)

    def __init__(self, G: Graph):
        self.g = G
        self.n = len(G.V)

    def c_f(self, edge: Edge) -> int:
        if edge.forward:
            return edge.c - self.flow[edge]
        else:
            return self.flow[edge.reversed()]

    def bfs(self) -> tuple[int, dict[Vertex, Edge] | None]:
        parent = dict[Vertex, Edge]()

        q = deque[tuple[Vertex, int]]()
        q.append((self.s, INF))

        visited = {self.s}

        while q:
            u, flow = q.popleft()

            for edge in self.g.outgoing[u]:
                v = edge.v

                if v in visited:
                    continue

                cap = self.c_f(edge)
                if cap > 0:
                    visited.add(v)
                    parent[v] = edge
                    new_flow = min(flow, cap)
                    if v == self.t:
                        return new_flow, parent
                    q.append((v, new_flow))

        return 0, None

    def max_flow(self, s: int, t: int) -> int:
        self.s = s
        self.t = t

        self.flow = defaultdict(int)

        flow = 0

        while True:
            new_flow, parent = self.bfs()

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
            benchmark_iteration("edmond", edge_updates)

        finish_benchmark("edmond", flow)

        return flow
