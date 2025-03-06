import networkx as nx
from dataclasses import dataclass
import random
from .utils import Edge, Graph


@dataclass
class ConstructedInstance:
    expanders: list[nx.DiGraph]
    rank_vertices: list[list[int]]
    num_vertices: int
    s: int
    t: int
    dag_edges: list[tuple[int, int, int]]
    top_order: dict[int, int]

    @staticmethod
    def new(
        seed: int | None = None,
        num_ranks: int = 5,
        connections_per_rank: int = 2,
        expanders_per_rank: int = 5,
        nodes_per_expander: int = 10,
        expander_degree: int = 4,
    ):
        inner_seed = seed

        def get_seed():
            nonlocal inner_seed
            if inner_seed is not None:
                ret = inner_seed
                inner_seed += 1
                return ret

        random.seed(get_seed())

        num_vertices = 0

        def next_vertex():
            nonlocal num_vertices
            num_vertices += 1
            return num_vertices - 1

        s = next_vertex()

        rank_vertices: list[list[int]] = [[] for _ in range(num_ranks)]
        for r in range(num_ranks):
            for _ in range(connections_per_rank):
                v = num_vertices
                num_vertices += 1
                rank_vertices[r].append(v)

        expanders = []
        for _ in range(expanders_per_rank * (num_ranks - 1)):
            G = nx.DiGraph()
            G_init = nx.random_regular_expander_graph(
                nodes_per_expander, expander_degree, seed=get_seed()).to_directed()

            for u, v in G_init.edges:
                G.add_edge(u + num_vertices, v + num_vertices,
                           weight=random.randint(10, 20))

            expanders.append(G)
            num_vertices += G.number_of_nodes()

        t = next_vertex()

        dag_edges: list[tuple[int, int, int]] = []
        exp_i = 0

        def rand_weight(min=25, max=50):
            return random.randint(min, max)

        top_order: dict[int, int] = {}

        def add_to_top_order(u: int):
            if u not in top_order:
                top_order[u] = len(top_order)

        add_to_top_order(s)

        for u in rank_vertices[0]:
            dag_edges.append((s, u, rand_weight()))
        for u in rank_vertices[-1]:
            dag_edges.append((u, t, rand_weight()))

        for ri in range(num_ranks - 1):
            rj = ri + 1

            # for u in rank_vertices[ri]:
            #     for v in rank_vertices[rj]:
            #         dag_edges.append((u, v))

            for u in rank_vertices[ri]:
                add_to_top_order(u)

            for _ in range(expanders_per_rank):
                if exp_i < len(expanders):
                    nodes: list[int] = list(expanders[exp_i].nodes)
                    random.shuffle(nodes)

                    for n in nodes:
                        add_to_top_order(n)

                    for u in rank_vertices[ri]:
                        v = nodes.pop()
                        dag_edges.append((u, v, rand_weight()))
                    for v in rank_vertices[rj]:
                        u = nodes.pop()
                        dag_edges.append((u, v, rand_weight()))
                    exp_i += 1

            for v in rank_vertices[rj]:
                add_to_top_order(v)

        add_to_top_order(t)

        # assert len(top_order) == num_vertices

        return ConstructedInstance(expanders=expanders, num_vertices=num_vertices, rank_vertices=rank_vertices, s=s, t=t, dag_edges=dag_edges, top_order=top_order)

    def export_graphviz(self):
        indent = 0

        def p(*args):
            print(indent * 2 * ' ', end='')
            print(*args)

        p('digraph G {')
        indent += 1

        p(f'{self.s} [label="{self.s} τ={self.top_order[self.s]} (source)"];')
        for r in self.rank_vertices:
            for v in r:
                p(f'{v} [label="{v} τ={self.top_order[v]}"];')
        p(f'{self.t} [label="{self.t} τ={self.top_order[self.t]} (sink)"];')

        for i, G in enumerate(self.expanders):
            p('subgraph', f'cluster_expander_{i}', '{')
            indent += 1

            p('node [style="filled", fillcolor="lightgreen"];')
            p('edge [color="green"];')

            for u in G.nodes:
                p(f'{u} [label="{u} τ={self.top_order[u]}"];')

            for u, v, c in G.edges(data="weight"):
                p(f'{u} -> {v} [label="{c}"];')

            indent -= 1
            p('}')

        for u, v, c in self.dag_edges:
            p(f'{u} -> {v} [label="{c}"];')

        indent -= 1
        p('}')

    def export_weighted_push_relabel_input(self):
        h = self.num_vertices

        edges: list[tuple[int, int]] = []
        capacities: list[int] = []
        for u, v, c in self.dag_edges:
            edges.append((u, v))
            capacities.append(c)
        for expander in self.expanders:
            for u, v, c in expander.edges(data="weight"):
                edges.append((u, v))
                capacities.append(c)

        vertices: list[int] = sorted(
            set(u for u, _ in edges) | set(v for _, v in edges))

        G = Graph(E=edges, V=vertices)

        def w(e: Edge):
            return abs(self.top_order[e.u] - self.top_order[e.v])

        return G, self.s, self.t, h, w, capacities

    def export_russian_graph(self):
        G, s, t, h, w, capacities = self.export_weighted_push_relabel_input()

        output = [f'{len(G.V)} {len(G.E)} {s} {t}']
        for i, e in enumerate(G.E):
            output.append(f'{e[0]}-({capacities[i]})>{e[1]}')

        return '\n'.join(output)

    def export_custom(self):
        output = {
            "nodes": [],
            "links": []
        }

        output["nodes"].append({ "id": self.s, "source": True })
        output["nodes"].append({ "id": self.t, "sink": True })

        for r in self.rank_vertices:
            for v in r:
                output["nodes"].append({ "id": v })

        for i, G in enumerate(self.expanders):
            for u in G.nodes:
                output["nodes"].append({
                    "id": u,
                    "group": i+1,
                })

            for u, v, c in G.edges(data="weight"):
                output["links"].append({ "source": u, "target": v, "value": c })

        for u, v, c in self.dag_edges:
            output["links"].append({ "source": u, "target": v, "value": c })

        return output


if __name__ == "__main__":
    instance = ConstructedInstance.new()
    # instance.export_graphviz()
    print(instance.export_weighted_push_relabel_input())
