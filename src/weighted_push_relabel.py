from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
import time

from src import benchmark
from tests.utils import bench
from .visualisation import (
    export_custom_visualisation,
    graphviz_frame,
    init_custom_visualisation,
    write_custom_frame_into,
)
from .utils import Edge, Graph, Vertex, next_multiple_of


@dataclass
class WeightedPushRelabel:
    # Parameters from paper
    G: Graph
    c: list[int]
    sources: dict[Vertex, int]
    sinks: dict[Vertex, int]
    w: Callable[[Edge], int]
    h: int
    dag_edges: set[tuple[Vertex, Vertex]] = field(default_factory=set)

    # State from paper
    f: dict[Edge, int] = field(default_factory=defaultdict[Edge, int])
    l: dict[Vertex, int] = field(default_factory=dict)
    alive: set[Vertex] = field(default_factory=set)
    admissible_outgoing: dict[Vertex, set[Edge]] = field(default_factory=dict)
    alive_vertices_with_no_admissible_out_edges: set[Vertex] = field(
        default_factory=set
    )

    # Extra state
    unique_weights: dict[Vertex, list[int]] = field(default_factory=dict)

    def solve(self) -> tuple[int, dict[Edge, int]]:
        benchmark.set_bench_scope("blik")
        benchmark.register("instance.h", self.h)

        self.f = defaultdict(int)
        self.l = {v: 0 for v in self.G.V}
        self.alive = set(self.G.V)
        self.admissible_outgoing = defaultdict(set)
        self.alive_vertices_with_no_admissible_out_edges = set(self.G.V)

        # Shorthands
        w = {
            e: self.w(e.forward_edge()) for e in self.G._all_edges()
        }  # NOTE: Not included in benchmark
        h = self.h
        f, l, c_f = self.f, self.l, self.c_f

        self.unique_weights = {
            v: sorted(set(w[e] for e in self.G.incident.inner[v].inner))
            for v in self.G.V
        }  # NOTE: Not included in benchmark

        def relabel(v: Vertex):
            l[v] = min(
                (
                    next_multiple_of(n=l[v], multiple_of=weight)
                    for weight in self.unique_weights[v]
                ),
                default=9 * h + 1,
            )

            benchmark.register_or_update_s(
                "highest_level", l[v], lambda x: max(x, l[v])
            )

            if l[v] > 9 * h:
                self.mark_dead(v)
                return

            benchmark.set_bench_scope("blik.relabel")
            edges = self.G.incident[v]  # NOTE: Gets looped
            benchmark.set_bench_scope("blik")

            for e in (e for e in edges.inner if l[v] % w[e] == 0):
                benchmark.register_or_update_s(
                    "relabel.edge_set.next", 1, lambda x: x + 1
                )

                x, y = e.start(), e.end()
                if l[x] - l[y] >= 2 * w[e] and c_f(e) > 0:
                    self.mark_admissible(e)
                else:
                    self.mark_inadmissible(e)

        graphviz_frame(self, "Initial")
        vis = init_custom_visualisation(self)
        write_custom_frame_into(self, vis, label="Initial")

        while True:
            benchmark.register_or_update_s("iterations", 1, lambda x: x + 1)

            for v in AliveSaturatedVerticesWithNoAdmissibleOutEdges(self):
                relabel(v)
                benchmark.register_or_update_s("relabels", 1, lambda x: x + 1)

            graphviz_frame(self, "After relabel")
            write_custom_frame_into(self, vis, label="After relabel")

            if (s := self.find_alive_vertex_with_excess()) is not None:
                P = self.trace_path(
                    s
                )  # NOTE: P gets looped but doesn't count in the benchmark
                assert P is not None, "Path not found, but we always expect one."

                graphviz_frame(self, "Traced path", aug_path=set(P))
                write_custom_frame_into(
                    self, vis, label="Traced path", augmenting_path=P
                )

                t = P[-1].end()

                c_augment = min(
                    self.residual_source(s),
                    self.residual_sink(t),
                    min(c_f(e) for e in P),
                )

                benchmark.register_or_update_s(
                    "max_edge_updates", len(P), lambda x: max(x, len(P or []))
                )
                benchmark.register_or_update_s(
                    "min_edge_updates", len(P), lambda x: min(x, len(P or []))
                )

                for e in P:
                    benchmark.register_or_update_s("edge_updates", 1, lambda x: x + 1)

                    if e.forward:
                        f[e] += c_augment
                    else:
                        f[e.forward_edge()] -= c_augment

                    # "Adjust ..." - is this automatically done via c_f()?

                    if c_f(e) == 0:
                        self.mark_inadmissible(e)

                sum_w = sum(w[e] for e in P)
                benchmark.register_or_update_s(
                    "average_w_length",
                    sum_w / c_augment,
                    lambda x: x + (sum_w / c_augment),
                )

                def transfer_bench_key(from_key: str, to_key: str):
                    benchmark.register_or_update_s(
                        to_key,
                        benchmark.get_or_default_s(from_key, 0) or 0,
                        lambda x: benchmark.get_or_default_s(to_key, 0) or 0,
                    )

                transfer_bench_key("relabels", "before_kill.relabels")
                transfer_bench_key("marked_admissible", "before_kill.marked_admissible")
                transfer_bench_key(
                    "marked_inadmissible", "before_kill.marked_inadmissible"
                )

                graphviz_frame(self, "After pushing")
                write_custom_frame_into(self, vis, label="After pushing")
            else:
                graphviz_frame(self, "Final")
                write_custom_frame_into(self, vis, label="Final")
                export_custom_visualisation(vis)

                result = self.amount_of_routed_flow(f)
                finish_benchmark(result)

                return result, f

    def c_f(self, e: Edge):
        f_e = self.f.get(e.forward_edge(), 0)
        if e.forward:
            return e.c - f_e
        else:
            return f_e

    def mark_admissible(self, e: Edge):
        benchmark.register_or_update_s("marked_admissible", 1, lambda x: x + 1)
        if e not in self.admissible_outgoing[e.start()]:
            benchmark.register_or_update_s(
                "state_change.marked_admissible", 1, lambda x: x + 1
            )
        else:
            benchmark.register_or_update_s(
                "state_change.already_marked_admissible", 1, lambda x: x + 1
            )

        if (e.start(), e.end()) in self.dag_edges:
            benchmark.register_or_update_s("dag_marked_admissible", 1, lambda x: x + 1)

        self.admissible_outgoing[e.start()].add(e)
        self.alive_vertices_with_no_admissible_out_edges.discard(e.start())

    def mark_inadmissible(self, e: Edge):
        benchmark.register_or_update_s("marked_inadmissible", 1, lambda x: x + 1)
        if e in self.admissible_outgoing[e.start()]:
            benchmark.register_or_update_s(
                "state_change.marked_inadmissible", 1, lambda x: x + 1
            )
        else:
            benchmark.register_or_update_s(
                "state_change.already_marked_inadmissible", 1, lambda x: x + 1
            )
        if (e.start(), e.end()) in self.dag_edges:
            benchmark.register_or_update_s(
                "dag_marked_inadmissible", 1, lambda x: x + 1
            )

        self.admissible_outgoing[e.start()].discard(e)
        if len(self.admissible_outgoing[e.start()]) == 0 and e.start() in self.alive:
            self.alive_vertices_with_no_admissible_out_edges.add(e.start())

    def mark_dead(self, v: Vertex):
        benchmark.register_or_update_s("marked_dead", 1, lambda x: x + 1)
        if v not in self.alive:
            benchmark.register_or_update_s(
                "marked_dead_alread_dead", 1, lambda x: x + 1
            )

        self.alive.remove(v)
        self.alive_vertices_with_no_admissible_out_edges.discard(v)

    def absorption(self, v: Vertex) -> int:
        return min(self.net_flow(v) + self.sources[v], self.sinks[v])

    def excess(self, v: Vertex) -> int:
        return self.net_flow(v) + self.sources[v] - self.absorption(v)

    # This is exactly B^TG(v) from the paper - or alternatively "-f^out(v)".
    def net_flow(self, v: Vertex) -> int:
        benchmark.set_bench_scope("blik.net_flow")
        recv = sum(self.f.get(e, 0) for e in self.G.incoming[v])  # NOTE: Loops edges
        send = sum(self.f.get(e, 0) for e in self.G.outgoing[v])  # NOTE: Loops edges
        benchmark.set_bench_scope("blik")
        return recv - send

    def residual_source(self, v: Vertex) -> int:
        """Corresponds to Δ_f(s)"""
        return self.excess(v)

    def residual_sink(self, v: Vertex) -> int:
        """Corresponds to ∇_f(t)"""
        return self.sinks[v] - self.absorption(v)

    # Black box for line 15 of Alg. 1 in the paper.
    def find_alive_vertex_with_excess(self) -> Vertex | None:
        for s in self.sources:
            if s in self.alive and self.residual_source(s) > 0:
                return s
        return None

    def trace_path(self, s: Vertex) -> list[Edge] | None:
        parent: dict[Vertex, Edge] = {}

        stack = [s]
        visited: set[Vertex] = set()

        while len(stack) > 0:
            v = stack.pop()

            # If we have reached the sink, we are done
            if self.sinks[v] > 0:
                path: list[Edge] = []
                while v in parent.keys() and v != s:
                    path.append(parent[v])
                    v = parent[v].start()
                path.reverse()
                return path

            for e in self.admissible_outgoing[v]:
                if e.end() in visited:
                    continue

                visited.add(e.end())
                stack.append(e.end())
                parent[e.end()] = e

        return None

    def amount_of_routed_flow(self, f: dict[Edge, int]) -> int:
        amount = 0
        for s in self.sources:
            if self.sources[s] > 0:
                amount += sum(f.get(e, 0) for e in self.G.outgoing[s])
        return amount


def weighted_push_relabel(
    G: Graph,
    c: list[int],
    sources: list[int],
    sinks: list[int],
    w: Callable[[Edge], int],
    h: int,
    dag_edges: set[tuple[Vertex, Vertex]] | None = None,
) -> tuple[int, dict[Edge, int]]:
    """
    G: a graph (V, E)
    c: capacities for each edge
    sources: source nodes providing flow
    sinks: sink nodes receiving flow
    w: weight function for edges
    h: height parameter
    """
    _sources = {v: sources[i] for i, v in enumerate(G.V)}
    _sinks = {v: sinks[i] for i, v in enumerate(G.V)}
    res = weighted_push_relabel_dict(G, c, _sources, _sinks, w, h, dag_edges)

    return res


def weighted_push_relabel_dict(
    G: Graph,
    c: list[int],
    sources: dict[Vertex, int],
    sinks: dict[Vertex, int],
    w: Callable[[Edge], int],
    h: int,
    dag_edges: set[tuple[Vertex, Vertex]] | None = None,
) -> tuple[int, dict[Edge, int]]:
    """
    G: a graph (V, E)
    c: capacities for each edge
    sources: source nodes providing flow
    sinks: sink nodes receiving flow
    w: weight function for edges
    h: height parameter
    """
    start = time.time_ns()

    instance = WeightedPushRelabel(G, c, sources, sinks, w, h)
    if dag_edges is not None:
        instance.dag_edges = dag_edges

    res = instance.solve()

    end = time.time_ns()
    benchmark.register_s(f"duration_s", (end - start) / 1e9)

    return res


# Black box for line 13 of Alg. 1 in the paper.
class AliveSaturatedVerticesWithNoAdmissibleOutEdges:
    instance: WeightedPushRelabel

    def __init__(self, instance: WeightedPushRelabel):
        self.instance = instance

    def __iter__(self):
        return self

    def __next__(self) -> Vertex:
        for v in self.instance.alive_vertices_with_no_admissible_out_edges:
            if self.instance.residual_sink(v) == 0:
                return v

        raise StopIteration


if __name__ == "__main__":
    mf, res = weighted_push_relabel(
        Graph(V=[0, 1, 2], E=[(0, 1), (1, 2)], c=[1, 1]),
        c=[1, 1],
        sources=[1, 0, 0],
        sinks=[0, 0, 1],
        w=lambda e: 1,
        h=3,
    )

    print(f"Result: {mf} total flow")
    for e, f in res.items():
        print(f"  {f} flow via {e}")


def finish_benchmark(flow: int):
    benchmark.register_s("flow", flow)

    updates = benchmark.get_or_default_s("edge_updates", 0)
    w_length = benchmark.get_or_default_s("average_w_length", 0)
    iters = benchmark.get_or_default_s("iterations", 1)
    if iters is not None and updates is not None and w_length is not None:
        benchmark.register_s("avg_updates", updates / iters)
        benchmark.register_s("average_w_length", w_length / iters)

    marked_inadmissible = benchmark.get_or_default_s(
        "state_change.marked_inadmissible", 0
    )
    marked_admissible = benchmark.get_or_default_s("state_change.marked_admissible", 0)
    if marked_inadmissible is not None and marked_admissible is not None:
        benchmark.register_s(
            "state_change.state_changes",
            marked_inadmissible + marked_admissible,
        )
