# Based upon the C++ implementation from here https://cp-algorithms.com/graph/min_cost_flow.html
from collections import defaultdict, deque
from tests.flows.utils import TestEdge


class MaxFlow:
    n: int
    capacities: defaultdict[int, defaultdict[int, int]]
    adj: defaultdict[int, list[int]]

    def __init__(self, edges: list[TestEdge], capacities: list[int]):
        self.capacities = defaultdict(lambda: defaultdict(lambda: 0))

        vs: set[int] = set()
        for (u, v), cap in zip(edges, capacities):
            vs.add(u)
            vs.add(v)

            self.capacities[u][v] = cap

        self.n = len(vs)

        self.adj = defaultdict(list)
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)

    def bfs(self, s: int, t: int, parent: list[int]) -> int:
        INF = float("inf")
        parent[:] = [-1] * len(parent)
        parent[s] = -2

        q = deque([(s, INF)])

        while q:
            cur, flow = q.popleft()
            for next_node in self.adj[cur]:
                if parent[next_node] == -1 and self.capacities[cur][next_node]:
                    parent[next_node] = cur
                    new_flow = min(flow, self.capacities[cur][next_node])
                    if next_node == t:
                        return int(new_flow)
                    q.append((next_node, new_flow))
        return 0

    def maxflow_bfs(self, s: int, t: int) -> int:
        flow = 0
        parent = [-1] * self.n

        while True:
            new_flow = self.bfs(s, t, parent)
            if not new_flow:
                break

            flow += new_flow
            cur = t

            while cur != s:
                prev = parent[cur]
                self.capacities[prev][cur] -= new_flow
                self.capacities[cur][prev] += new_flow
                cur = prev

        return flow

    def max_flow(self, s: int, t: int) -> int:
        bfs_flow = self.maxflow_bfs(s, t)

        return bfs_flow
