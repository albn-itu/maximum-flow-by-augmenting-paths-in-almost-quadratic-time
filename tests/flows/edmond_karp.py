# Based upon the C++ implementation from here https://cp-algorithms.com/graph/min_cost_flow.html
from collections import defaultdict, deque
from dataclasses import dataclass, field
from src import benchmark
from src.utils import Edge, Graph, Vertex

INF = 1000000000


@dataclass
class MaxFlow:
    g: Graph
    n: int
    s: Vertex
    t: Vertex

    flow: dict[Edge, int] = field(default_factory=dict)

    def __init__(self, G: Graph):
        self.g = G
        self.n = len(G.V)

    def c_f(self, edge: Edge) -> int:
        if edge.forward:
            return edge.c - self.flow.get(edge, 0)
        else:
            return self.flow.get(edge.reversed(), 0)

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

    def maxflow_bfs(self, s: int, t: int) -> int:
        self.s = s
        self.t = t

        self.flow = {}
        for edge in self.g.all_edges():
            self.flow[edge] = 0

        flow = 0

        while True:
            new_flow, parent = self.bfs()

            if new_flow == 0 or parent is None:
                break

            flow += new_flow

            cur = t
            edge_updates = 0
            while cur != self.s:
                edge = parent[cur]
                cur = edge.u

                if edge.forward:
                    self.flow[edge] = self.flow.get(edge, 0) + new_flow
                else:
                    edge = edge.reversed()
                    self.flow[edge] = self.flow.get(edge, 0) - new_flow

                edge_updates += 2

            benchmark.register_or_update(
                "edmond.edge_updates", edge_updates, lambda x: x + edge_updates
            )
            benchmark.register_or_update(
                "edmond.max_edge_updates",
                edge_updates,
                lambda x: edge_updates if edge_updates > x else x,
            )
            benchmark.register_or_update(
                "edmond.min_edge_updates",
                edge_updates,
                lambda x: edge_updates if edge_updates < x else x,
            )
            benchmark.register_or_update("edmond.iterations", 1, lambda x: x + 1)

        updates = benchmark.get_or_default("edmond.edge_updates", 0)
        iters = benchmark.get_or_default("edmond.iterations", 1)
        if iters is not None and updates is not None:
            benchmark.register("edmond.avg_updates", updates / iters)

        return flow

    def max_flow(self, s: int, t: int) -> int:
        bfs_flow = self.maxflow_bfs(s, t)

        benchmark.register("edmond.flow", bfs_flow)

        return bfs_flow
