from collections import defaultdict
from src import benchmark
from tests.flows.utils import TestEdge


INF = 1000000000


class PushRelabel:
    n: int
    capacities: defaultdict[int, defaultdict[int, int]]
    flow: defaultdict[int, defaultdict[int, int]]

    height: list[int]
    excess: list[int]

    edge_updates: int

    def __init__(self, edges: list[TestEdge], capacities: list[int]):
        """Initialize push-relabel algorithm with n vertices."""
        self.capacities = defaultdict(lambda: defaultdict(lambda: 0))
        self.flow = defaultdict(lambda: defaultdict(lambda: 0))

        vs: set[int] = set()
        for (u, v), cap in zip(edges, capacities):
            vs.add(u)
            vs.add(v)

            self.capacities[u][v] = cap

        self.n = len(vs)

        self.height = [0] * self.n
        self.excess = [0] * self.n

        self.edge_updates = 0

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

    def add_edge(self, u: int, v: int, cap: int) -> None:
        """Add an edge from u to v with capacity cap."""
        self.capacities[u][v] = cap

    def push(self, u: int, v: int) -> None:
        """Push excess flow from vertex u to v."""
        d = min(self.excess[u], self.capacities[u][v] - self.flow[u][v])
        self.flow[u][v] += d
        self.flow[v][u] -= d
        self.excess[u] -= d
        self.excess[v] += d

        self.edge_updates += 2

    def relabel(self, u: int) -> None:
        """Relabel vertex u by increasing its height."""
        d = INF
        for i in range(self.n):
            if self.capacities[u][i] - self.flow[u][i] > 0:
                d = min(d, self.height[i])
        if d < INF:
            self.height[u] = d + 1

            benchmark.register_or_update(
                "push_relabel.highest_level", d + 1, lambda x: max(x, d + 1)
            )

    def find_max_height_vertices(self, s: int, t: int) -> list[int]:
        """Find vertices with maximum height and positive excess flow."""
        max_height: list[int] = []
        for i in range(self.n):
            if i != s and i != t and self.excess[i] > 0:
                if max_height and self.height[i] > self.height[max_height[0]]:
                    max_height.clear()
                if not max_height or self.height[i] == self.height[max_height[0]]:
                    max_height.append(i)
        return max_height

    def max_flow(self, s: int, t: int) -> int:
        """
        Calculate maximum flow from source s to sink t using push-relabel algorithm.
        Returns the maximum flow value.
        """
        # Initialize height, flow, and excess arrays
        self.height[s] = self.n
        self.excess[s] = INF

        # Initial push from source
        for i in range(self.n):
            if i != s:
                self.push(s, i)

        first = True
        # Main loop
        while True:
            if not first:
                self.new_iteration()
            first = False

            current = self.find_max_height_vertices(s, t)
            if not current:
                break

            for i in current:
                pushed = False
                for j in range(self.n):
                    if (
                        self.excess[i]
                        and self.capacities[i][j] - self.flow[i][j] > 0
                        and self.height[i] == self.height[j] + 1
                    ):
                        self.push(i, j)
                        pushed = True

                if not pushed:
                    self.relabel(i)
                    break

        total_updates = benchmark.get_or_default("push_relabel.edge_updates", 0)
        iters = benchmark.get_or_default("push_relabel.iterations", 1)
        if iters is not None and total_updates is not None:
            benchmark.register("push_relabel.avg_updates", total_updates / iters)
        benchmark.register("push_relabel.flow", self.excess[t])

        return self.excess[t]
