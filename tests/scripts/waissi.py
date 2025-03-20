from collections import defaultdict

input = """
c Random Network
c for Max-Flow
p max        23        40
n             1  s
n            23  t
a        17        20        17
a        10        13        16
a         3        15        26
a         6        11        42
a        12        14        23
a        20        16        14
a        13        18        43
a        12        17         8
a        22         8        28
a        15         6        17
a        15        20        45
a         9         6         4
a        11         5        21
a        12         2        19
a         4        19        10
a         4         5        33
a        12         6        35
a        23         7        38
a         5         8        10
a        17        10        12
a        22         9         7
a        16        23        10
a        14         9         4
a         5        15        43
a        22        18        17
a         5         1        31
a        10         4        19
a        14         7        13
a         5        20        15
a         9        14        38
a        23        11        36
a        10         1        21
a         9        22        23
a        18        22        28
a        13        12        18
a        15         3         5
a        12        18         6
a        12        19         1
a        10        16         6
a        19         6        11
""".strip()

lines = input.split("\n")

ns = [l for l in lines if l.startswith("n")]
source = int(ns[0].split()[1])
sink = int(ns[1].split()[1])

as_ = [l for l in lines if l.startswith("a")]
edges = defaultdict(int)
for a in as_:
    _, to, from_, c = a.split()
    to, from_, c = int(to), int(from_), int(c)
    edges[(to, from_)] += c
    edges[(from_, to)] += c

print(source, sink, edges)

n = len(set(e[0] for e in edges) | set(e[1] for e in edges))
m = len(edges)
print(n, m, source - 1, sink - 1)
for (u, v), c in edges.items():
    print(f"{u-1}-({c})>{v-1}")
