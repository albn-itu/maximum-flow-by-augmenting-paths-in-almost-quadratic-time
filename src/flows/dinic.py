from flows.utils import benchmark_iteration, finish_benchmark
from src import benchmark
from collections import defaultdict, deque
from dataclasses import dataclass, field

from src.utils import Edge, Vertex, Graph

INF = 1000000000


@dataclass
class Dinic:
    g: Graph
    s: Vertex
    t: Vertex

    flow: defaultdict[Edge, int] = field(default_factory=defaultdict)

    level: dict[Vertex, int] = field(default_factory=dict)
    ptr: dict[Vertex, int] = field(default_factory=dict)
    edge_adj: dict[Vertex, list[Edge]] = field(default_factory=dict)

    edge_updates: int = 0

    def __init__(self, G: Graph):
        self.g = G

    def c_f(self, edge: Edge) -> int:
        if edge.forward:
            return edge.c - self.flow[edge]
        else:
            return self.flow[edge.reversed()]

    def bfs(self) -> bool:
        self.level = {u: -1 for u in self.g.V}
        self.level[self.s] = 0

        q: deque[Vertex] = deque()
        q.append(self.s)

        while q:
            u = q.popleft()

            for edge in self.g.outgoing[u]:
                v = edge.v
                if self.c_f(edge) > 0 and self.level[v] == -1:
                    self.level[v] = self.level[u] + 1
                    q.append(v)

        return self.level[self.t] != -1

    def dfs(self, u: Vertex, limit: int) -> int:
        if limit == 0:
            return 0
        if u == self.t:
            return limit

        if u not in self.edge_adj:
            return 0

        while self.ptr[u] < len(self.edge_adj[u]):
            edge = self.edge_adj[u][self.ptr[u]]
            v = edge.v

            if self.c_f(edge) == 0 or self.level[v] != self.level[u] + 1:
                self.ptr[u] += 1
                continue

            new_flow = min(limit, self.c_f(edge))
            new_flow = self.dfs(v, new_flow)

            if new_flow == 0:
                self.ptr[u] += 1
                continue

            if edge.forward:
                self.flow[edge] += new_flow
            else:
                self.flow[edge.reversed()] -= new_flow

            self.edge_updates += 2

            return new_flow

        return 0

    def max_flow(self, s: Vertex, t: Vertex) -> int:
        benchmark.set_bench_scope("dinic")

        self.s = s
        self.t = t

        self.flow = defaultdict(int)

        self.level = {}
        self.ptr = {}
        self.edge_adj = {}

        flow = 0

        while self.bfs():
            self.edge_adj.clear()

            for u in self.g.V:
                if self.level.get(u, -1) != -1:
                    self.edge_adj[u] = list(self.g.outgoing[u])

            self.ptr = {u: 0 for u in self.edge_adj}

            while True:
                new_flow = self.dfs(self.s, INF)

                if new_flow == 0:
                    break

                flow += new_flow
            benchmark_iteration(self.edge_updates)
            self.edge_updates = 0

        finish_benchmark(flow)

        return flow
