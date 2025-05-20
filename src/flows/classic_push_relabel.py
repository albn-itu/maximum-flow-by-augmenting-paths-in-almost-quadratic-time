from collections import defaultdict, deque
from dataclasses import dataclass, field

from flows.utils import benchmark_iteration, finish_benchmark

from src import benchmark
from src.utils import Edge, Graph, Vertex

INF = 1000000000


@dataclass
class PushRelabel:
    g: Graph
    n: int
    s: Vertex
    t: Vertex

    height: dict[Vertex, int] = field(default_factory=dict)
    excess: dict[Vertex, int] = field(default_factory=dict)

    flow: defaultdict[Edge, int] = field(default_factory=defaultdict)

    active_node_queue: deque[Vertex] = field(default_factory=deque)
    is_active: dict[Vertex, bool] = field(default_factory=dict)

    edge_updates: int = 0

    def __init__(self, G: Graph):
        """Initialize push-relabel algorithm with n vertices."""
        self.g = G
        self.n = len(G.V)

    def c_f(self, edge: Edge) -> int:
        if edge.forward:
            return edge.c - self.flow[edge]
        else:
            return self.flow[edge.reversed()]

    def push(self, edge: Edge, to_push: int | None = None) -> None:
        u, v = edge.u, edge.v
        if to_push is None:
            to_push = min(self.excess[u], self.c_f(edge))

        if edge.forward:
            self.flow[edge] = self.flow[edge] + to_push
        else:
            edge = edge.reversed()
            self.flow[edge] = self.flow[edge] - to_push

        self.excess[u] -= to_push
        self.excess[v] += to_push

        self.edge_updates += 2

        if v != self.s and v != self.t and self.excess[v] > 0 and not self.is_active[v]:
            self.active_node_queue.append(v)
            self.is_active[v] = True

    def relabel(self, u: int) -> None:
        """Relabel vertex u by increasing its height."""
        benchmark.register_or_update("push_relabel.relabels", 1, lambda x: x + 1)

        d = INF
        for edge in self.g.outgoing[u]:
            if self.c_f(edge) > 0:
                d = min(d, self.height[edge.v])

        if d < INF:
            new_height = d + 1
            self.height[u] = new_height

            benchmark.register_or_update(
                "push_relabel.highest_level", new_height, lambda x: max(x, new_height)
            )

    def discharge(self, u: int):
        while self.excess[u] > 0:
            pushed = False

            for edge in self.g.outgoing[u]:
                if self.c_f(edge) > 0 and self.height[u] == self.height[edge.v] + 1:
                    self.push(edge)
                    pushed = True
                    if self.excess[u] == 0:
                        return

            if not pushed:
                self.relabel(u)

    def max_flow(self, s: int, t: int) -> int:
        # == Init ==
        self.s = s
        self.t = t

        self.height = {u: 0 for u in self.g.V}
        self.height[s] = self.n

        self.active_node_queue = deque()
        self.is_active = {u: False for u in self.g.V}

        self.excess = {u: 0 for u in self.g.V}

        self.flow = defaultdict(int)
        for edge in self.g.outgoing[s]:
            if not edge.forward:
                continue

            to_push = edge.c
            self.push(edge, to_push)

        for u in self.g.V:
            if u != s and u != t and self.excess[u] > 0 and not self.is_active[u]:
                self.active_node_queue.append(u)
                self.is_active[u] = True

        while self.active_node_queue:
            u = self.active_node_queue.popleft()
            self.is_active[u] = False

            self.discharge(u)

            benchmark_iteration("push_relabel", self.edge_updates)
            self.edge_updates = 0

        max_flow = self.excess[t]
        finish_benchmark("push_relabel", max_flow)

        return max_flow
