GRAPH: str = """
0>1
0>2
0>3
0>4
1>5
2>5
3>5
4>5
5>6
6>7
6>8
6>9
6>10
7>11
8>11
9>11
10>11
"""

import random


lines = GRAPH.strip().split("\n")

nodes = 0
edges: list[tuple[int, int, int]] = []
capacities: list[int] = []

for line in lines:
    u, v = line.split(">")
    nodes = max(nodes, int(u), int(v))
    edges.append((int(u), int(v), random.randint(1, 100)))

print(f"{nodes + 1} {len(edges)} 0 {nodes}")
for u, v, cap in edges:
    print(f"{u}-({cap})>{v}")
