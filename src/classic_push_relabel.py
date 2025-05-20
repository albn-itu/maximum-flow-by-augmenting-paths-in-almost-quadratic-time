from collections import deque
from dataclasses import dataclass, field

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

    flow: dict[Edge, int] = field(default_factory=dict)

    edge_updates: int = 0

    active_node_queue: deque[Vertex] = field(default_factory=deque)
    is_active: dict[Vertex, bool] = field(default_factory=dict)

    def __init__(self, G: Graph):
        """Initialize push-relabel algorithm with n vertices."""
        self.g = G
        self.n = len(G.V)

    def new_iteration(self):
        """Reset edge update counter."""
        edge_updates = self.edge_updates
        benchmark.register_or_update(
            "push_relabel.edge_updates", edge_updates, lambda x: x + edge_updates
        )
        benchmark.register_or_update(
            "push_relabel.max_edge_updates",
            edge_updates,
            lambda x: max(x, edge_updates),
        )
        benchmark.register_or_update(
            "push_relabel.min_edge_updates",
            edge_updates,
            lambda x: min(x, edge_updates),
        )
        benchmark.register_or_update("push_relabel.iterations", 1, lambda x: x + 1)
        self.edge_updates = 0

    def c_f(self, edge: Edge) -> int:
        if edge.forward:
            return edge.c - self.flow.get(edge, 0)
        else:
            return self.flow.get(edge.reversed(), 0)

    def push(self, edge: Edge, to_push: int | None = None) -> None:
        u, v = edge.u, edge.v
        if to_push is None:
            to_push = min(self.excess[u], self.c_f(edge))

        if edge.forward:
            self.flow[edge] = self.flow.get(edge, 0) + to_push
        else:
            edge = edge.reversed()
            self.flow[edge] = self.flow.get(edge, 0) - to_push

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
            self.height[u] = d + 1

            benchmark.register_or_update(
                "push_relabel.highest_level", d + 1, lambda x: max(x, d + 1)
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

        # Set all flow to 0
        self.flow = {}
        for edge in self.g.all_edges():
            if edge.forward:
                self.flow[edge] = 0
        # Initial push from source
        for edge in self.g.outgoing[s]:
            if not edge.forward:
                continue

            to_push = edge.c
            self.push(edge, to_push)

        self.edge_updates = 0

        for u in self.g.V:
            if u != s and u != t and self.excess[u] > 0 and not self.is_active[u]:
                self.active_node_queue.append(u)
                self.is_active[u] = True

        first = True
        # Main loop
        while self.active_node_queue:
            if not first:
                self.new_iteration()
            first = False

            u = self.active_node_queue.popleft()
            self.is_active[u] = False

            self.discharge(u)

        total_updates = benchmark.get_or_default("push_relabel.edge_updates", 0)
        iters = benchmark.get_or_default("push_relabel.iterations", 1)
        if iters is not None and total_updates is not None:
            benchmark.register("push_relabel.avg_updates", total_updates / iters)
        benchmark.register("push_relabel.flow", self.excess[t])

        return self.excess[t]
