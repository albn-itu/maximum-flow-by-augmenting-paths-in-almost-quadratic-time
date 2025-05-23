import os

from src.flows.classic_push_relabel import PushRelabel

from src.utils import Graph
from .expander_hierarchy_generator import ExpanderHierarchy, from_json_file
from networkx.algorithms import hierarchy


def multiply_graph(G: Graph, factor: int) -> Graph:
    edges: list[tuple[int, int]] = []
    caps: list[int] = []
    for i, (u, v) in enumerate(G.E):
        for j in range(factor):
            edges.append((u, v))
            caps.append(G.c[i])

    return Graph(
        V=G.V,
        E=edges,
        c=caps,
    )


def multiply_hierarchy(hierarchy: ExpanderHierarchy, factor: int) -> ExpanderHierarchy:
    multiplied_g = multiply_graph(hierarchy.G, factor)
    flow = PushRelabel(multiplied_g).max_flow(hierarchy.s, hierarchy.t)

    return ExpanderHierarchy(
        G=multiplied_g,
        order=hierarchy.order,
        components=hierarchy.components,
        hierarchy=hierarchy.hierarchy,
        s=hierarchy.s,
        t=hierarchy.t,
        flow=flow,
    )


if __name__ == "__main__":
    dir = "tests/data/varying_expander_hierarchies"
    files = os.listdir(dir)
    for file in files:
        if not file.endswith(".json"):
            continue

        print(f"Processing {file}")
        for factor in [2, 3]:
            hierarchy = from_json_file(f"{dir}/{file}")
            hierarchy = multiply_hierarchy(hierarchy, 3)

            graphs, n, suffix = file.split("_")
            # filename = f"factor_{factor}_{file}"
            filename = f"{graphs}_{n}_factor-{factor}_{suffix}"

            hierarchy.dump_to_json_file(f"{dir}/{filename}")
