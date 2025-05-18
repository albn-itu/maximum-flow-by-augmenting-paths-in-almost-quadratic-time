from dataclasses import dataclass
import heapq
import pathlib
import random
import sys

from .classic_push_relabel import PushRelabel

from .phi_expander_generator import generate_phi_expander, Graph as PhiGraph
from .utils import (
    Graph,
    Vertex,
    parse_input,
    export_russian_graph,
    generate_random_capacities,
    topological_sort_with_backwards_edges,
)


@dataclass
class ExpanderHierarchy:
    G: Graph  # The full graph
    order: list[int]  # Topological order of the full graph
    hierarchy: list[set[tuple[int, int]]]  # The hierarchy of the graph
    components: list[list[int]]  # The components of the graph
    s: int  # source
    t: int  # sink
    flow: int  # The flow of the graph

    def dump_to_json_file(self, filename: str):
        import json

        data = {
            "edge_list": export_russian_graph(self.G, self.s, self.t),
            "order": self.order,
            "components": self.components,
            "hierarchy": [list(h) for h in self.hierarchy],
            "s": self.s,  # Also in edge_list
            "t": self.t,  # Also in edge_list
            "flow": self.flow,
        }
        path = pathlib.Path(filename).parent
        path.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def export_to_d3(self, filename: str):
        import json

        output = {
            "nodes": [],
            "links": [],
            "frames": [
                {"label": "initial", "vertices": {}, "edges": {}, "augmentingPath": []}
            ],
        }

        for i, vertices in enumerate(self.components):
            for v in vertices:
                spec = {"id": v, "group": i}
                if v == self.s:
                    spec["source"] = True
                if v == self.t:
                    spec["sink"] = True

                output["nodes"].append(spec)
                output["frames"][0]["vertices"][str(v)] = {"alive": True, "height": 0}

        for i, edge in enumerate(self.G.E):
            u, v = edge
            c = self.G.c[i]
            output["links"].append(
                {"source": u, "target": v, "capacity": c, "id": i, "weight": 0}
            )
            output["frames"][0]["edges"][str(i)] = {
                "flow": 0,
                "remainingCapacity": c,
                "weight": 0,
                "admissible": False,
                "reverseAdmissible": False,
            }

        with open(filename, "w") as f:
            json.dump(output, f, indent=4)


def from_json_file(filename: str) -> ExpanderHierarchy:
    import json

    with open(filename, "r") as f:
        # Type safety? Not for this. We assume the file is correct.
        data = json.load(f)
        edge_list: str = data["edge_list"]
        return ExpanderHierarchy(
            G=parse_input(edge_list, 0)[0],
            order=data["order"],
            components=data["components"],
            hierarchy=[set(tuple(edge) for edge in h) for h in data["hierarchy"]],
            s=data["s"],
            t=data["t"],
            flow=data["flow"],
        )


def phi_graph_to_graph(g: PhiGraph) -> Graph:
    capacities = [1] * len(g.edges)

    # Remap vertices such that there are no holes
    sorted_vertices = sorted(g.vertices)
    vertex_map = {v: i for i, v in enumerate(sorted_vertices)}
    edges = [(vertex_map[u], vertex_map[v]) for u, v in g.edges]

    return Graph(
        V=list(range(len(sorted_vertices))),
        E=edges,
        c=capacities,
    )


def find_furthest_reachable_vertex(G: Graph, s: int) -> int:
    # Reverse Dijkstra
    distances = {v: -float("inf") for v in G.V}
    distances[s] = 0
    queue = [(0, s)]
    heapq.heapify(queue)
    visited: set[Vertex] = set()

    while queue:
        dist, u = heapq.heappop(queue)
        if u in visited:
            continue

        visited.add(u)
        for edge in G.outgoing[u]:
            v = edge.end()
            if v in visited or not edge.forward:
                continue

            new_dist = dist + 1
            if new_dist > distances[v]:
                distances[v] = new_dist
                heapq.heappush(queue, (new_dist, v))

    vertex = -1
    max_dist = -float("inf")
    for v in G.V:
        if distances[v] > max_dist:
            max_dist = distances[v]
            vertex = v
    return vertex


def debug_print(*args, **kwargs):
    # print(*args, **kwargs)
    pass


def generate_phi_expander_hierarchy(
    phi: float | None = None,
    n: int | None = None,
    seed: int | None = None,
    rand_child_size: bool = True,
) -> ExpanderHierarchy:
    phi = phi or 0.15
    seed = seed or random.randrange(sys.maxsize)
    parent_size = n or random.randint(6, 15)

    debug_print("Seed:", seed)

    # 1. Generate a parent expander of size `parent_size`.
    debug_print("Generating parent expander of size", parent_size)
    parent_expander = phi_graph_to_graph(generate_phi_expander(phi=phi, n=parent_size))
    debug_print("Parent expander:", export_russian_graph(parent_expander, 0, 1))
    children: dict[int, Graph] = {}

    # 2. Generate `parent_size` children of size `child_size`.
    for i, v in enumerate(parent_expander.V):
        debug_print(f"Generating child {i + 1} of {len(parent_expander.V)}")
        child_size = (
            random.randint(2, parent_size - 1) if rand_child_size else parent_size - 1
        )
        children[v] = phi_graph_to_graph(generate_phi_expander(phi=phi, n=child_size))

    # 3. The parent_expander is topologically sorted to generate the weight function.
    parent_order, backwards_edges = topological_sort_with_backwards_edges(
        parent_expander
    )

    # 4. Each "child" takes the place of a vertex in the parent expander.
    components: dict[int, list[int]] = {}
    x_1: set[tuple[int, int]] = set()

    # If done correctly this will just be 0,1,2,3...n
    # Read the next comment as to why that happens
    final_order: list[int] = []

    # This loops through in the topological order of the parent expander
    # We do this to make the final order much easier to work with
    for vertex in parent_order:
        child = children[vertex]

        #   - The edges inside the child is the first level of the expander
        vertex_start = max(final_order, default=-1) + 1

        edges = set((u + vertex_start, v + vertex_start) for u, v in child.E)
        x_1 = x_1.union(edges)

        components[vertex] = [v + vertex_start for v in child.V]
        debug_print("Vertices", components[vertex], " replaces ", vertex)
        final_order += components[vertex]

    #   - The edges in the parent_expander are the second level of the expander.
    dag_edges: set[tuple[int, int]] = set()
    x_2: set[tuple[int, int]] = set()
    for u, v in parent_expander.E:
        component_u = components[u]
        component_v = components[v]

        #   - The edges going to the vertex the child replaces are connected randomly to the vertices in the child
        new_u = random.choice(component_u)
        new_v = random.choice(component_v)

        new_edge = (new_u, new_v)
        if (u, v) in backwards_edges:
            x_2.add(new_edge)
        else:
            dag_edges.add(new_edge)

    # The resulting graph
    all_edges = dag_edges.union(x_1).union(x_2)
    try:
        g = Graph(
            V=sorted(final_order),
            E=list(all_edges),
            c=[1] * len(all_edges),
        )
    except KeyError as e:
        debug_print("Error in graph generation")
        debug_print("Seed", seed)
        raise e

    g = generate_random_capacities(g)

    # 5. Choose a source and sink
    # For now the source and sink are the first and last vertices in the final order
    s = final_order[0]
    t = find_furthest_reachable_vertex(g, s)

    # 6. Find the correct flow through the graph
    # This is done by running the push relabel algorithm
    flow = PushRelabel(g).max_flow(s, t)

    # 6. The resulting graph, it's hierarchy and the topological order are returned.
    return ExpanderHierarchy(
        G=g,
        hierarchy=[dag_edges, x_1, x_2],
        components=list(components.values()),
        order=final_order,
        s=s,
        t=t,
        flow=flow,
    )


if __name__ == "__main__":
    seed = random.randrange(sys.maxsize)
    print("Seed:", seed)

    graphs = 36

    ns = list(range(15, 50))
    for n in ns:
        for i in range(3):
            print(f"Generating graph {graphs}/{len(ns) * 3}")
            expander_hierarchy = generate_phi_expander_hierarchy(
                phi=0.15,
                n=n,
                seed=seed,
                rand_child_size=False,
            )

            filename = f"{graphs:04}_{n}_expander.json"
            expander_hierarchy.dump_to_json_file(
                f"tests/data/varying_expander_hierarchies/{filename}"
            )

            graphs += 1
