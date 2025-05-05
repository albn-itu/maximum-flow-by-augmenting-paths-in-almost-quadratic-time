from dataclasses import dataclass
import sys
import math
import heapq
from collections import defaultdict
from typing import Callable, Self

from .utils import Edge, Graph, Vertex
from .weighted_push_relabel import WeightedPushRelabel


def sparse_cut(
    I: tuple[Graph, list[int], dict[Vertex, int], dict[Vertex, int]],
    kappa: int,
    F: set[Edge],
    H: dict[int, set[Edge]],
    c_6_5: int = 1,  # Constant from the paper
    phi: float = 0.2,  # Phi parameter from the paper
    w_H: Callable[[Edge], int] = lambda e: 1,
) -> tuple[dict[Edge, int], tuple[set[Vertex], set[Vertex], set[Edge]]]:
    """
    Implementation of the SparseCut algorithm (Algorithm 2 from the paper).

    Args:
        I: tuple (G, c, Delta, Nabla) where:
            G: Graph
            c: list of edge capacities
            sources: dictionary mapping vertices to source values
            sinks: dictionary mapping vertices to sink values
        kappa: Integer parameter
        F: set of terminal edges
        H: Expander hierarchy
        c_6_5: Constant from the paper
        phi: Phi parameter from the paper
        w_H: Function to calculate weights for edges in the hierarchy

    Returns:
        tuple of (flow, cut) where:
            flow: dictionary mapping edges to flow values
            cut: tuple (S, Sbar) representing the cut
    """
    G, c, sources, sinks = I
    n = len(G.V)
    # eta = math.log(n)  # Height of the hierarchy
    D_H = H.get(0, set())  # DAG edges from hierarchy

    print("I", I)
    print("kappa", kappa)
    print("F", F)
    print("H", H)
    print("c_6_5", c_6_5)
    print("phi", phi)
    print("w_H", w_H)
    print("D_H", D_H)
    print("n", n)

    # Calculate h as defined in the algorithm
    # h = math.ceil((4 * (eta**4) * c_6_5 * (math.log(n) ** 7) * kappa) / (phi**2) * n)
    h = math.ceil(1 / phi)
    # h = math.ceil(n / 3)
    print("Height h:", h)

    # Define c^κ = κ · c
    c_kappa = [kappa * cap for cap in c]

    # Verify properties
    assert kappa <= n, "kappa should be less than or equal to n"  # Theorem 6.1
    assert kappa > 0, "kappa should be greater than 0"  # Theorem 6.1
    print(1 / phi, 1 / (10 * math.log(n)))
    # assert 1 / phi <= n, (
    #     f"1/phi={1 / phi} should be less than or equal to n={n}"
    # )  # Theorem 6.1
    assert c_6_5 >= 1, "c_6_5 should be greater than or equal to 1"  # Theorem 6.5

    # Define w_G(e)
    def w_G(e: Edge) -> int:
        if e in F:
            return n
        else:
            return w_H(e)

    print("Initialized", c_kappa, h)
    # Run PushRelabel to get a flow f
    instance = WeightedPushRelabel(G, c_kappa, sources, sinks, w_G, h)
    flow_value, f = instance.solve()
    print("Flow value:", flow_value, sum(sources.values()))

    # If |f| = ||Δ||₁, return f
    if flow_value == sum(sources.values()):
        return f, (set(), set(), set())

    # else
    # Let w_f be w_G extended to G_f
    def w_f(e: Edge) -> int:
        # , except set w_f(e->) = 0 for e ∈ D_H
        if e in D_H and e.forward:
            return 0
        else:
            return w_G(e)

    # set S₀ = {s ∈ V : Δ_f(s) > 0}
    S_0: list[Vertex] = [s for s in G.V if instance.excess(s) > 0]
    print("excess", S_0)

    print("Calculating distance levels")
    distance_level_collections = dijsktra(G, instance, S_0, w_f)
    print("Distance levels:", distance_level_collections)

    # Calculate vol_F for each vertex
    vol_F: dict[Vertex, int] = defaultdict(int)
    for edge in set(e for edges in G.outgoing.values() for e in edges):
        if edge in F and instance.c_f(edge) > 0:
            vol_F[edge.start()] += 1
            vol_F[edge.end()] += 1

    best_global_cut = None
    for distance_levels in distance_level_collections:
        max_level = max(distance_levels.keys())
        assert max_level >= 0, "Max level should be non-negative"

        best_local_cut = None

        S_leq_i: set[Vertex] = set()  # S_≤i
        for i in sorted(list(distance_levels.keys())):
            # Add vertices from level i to S_≤i
            S_leq_i.update(distance_levels[i])
            S_leq_i_complement = set(G.V) - S_leq_i

            # Calculate c^κ_f(E_{G_f}(S_≤i, S̄_≤i))
            cut_capacity = 0
            boundary: set[Edge] = set()
            reverse_boundary: set[Edge] = set()
            for u in S_leq_i:
                for edge in G.incident[u]:
                    if instance.c_f(edge) <= 0:
                        continue

                    if edge.end() in S_leq_i_complement:
                        cut_capacity += edge.c
                        boundary.add(edge)

                    if edge.start() in S_leq_i_complement:
                        reverse_boundary.add(edge)

            # Calculate vol_F(S_≤i) and vol_F(S̄_≤i)
            vol_S = sum(vol_F[v] for v in S_leq_i)
            vol_S_complement = sum(vol_F[v] for v in S_leq_i_complement)

            # Calculate the minimum of vol_F(S_≤i) and vol_F(S̄_≤i)
            min_vol = min(vol_S, vol_S_complement)

            # Calculate the value to be minimized
            value = cut_capacity - min_vol
            print(f"\n== Level {i} ==")
            if len(boundary) == 0:
                print("Boundary size is 0, skipping")
                continue

            local_cut = Cut(
                S_leq_i.copy(),
                S_leq_i_complement.copy(),
                boundary | reverse_boundary,
                value,
            )
            local_cut.print()
            print(
                f"cut_cap - min(vol_S, vol_S_complement): {cut_capacity} - min({vol_S}, {vol_S_complement})"
            )

            # For interest, calculate the Cheeger constant
            if min_vol == 0:
                cheeger_constant = float("inf")
            else:
                cheeger_constant = len(boundary) / min_vol
            print("Boundary size:", len(boundary))
            print("Cheeger constant:", cheeger_constant)

            # For interest, calculate the sparsity of the cut
            # Calculated based on https://home.ttic.edu/~yury/courses/geometry/notes/sparsest-cut.pdf
            smallest_vertex_set = min(len(S_leq_i), len(S_leq_i_complement))
            if smallest_vertex_set == 0:
                sparsity = float("inf")
            else:
                sparsity = len(boundary) / smallest_vertex_set
            print("Sparsity:", sparsity)
            print(
                "min{|E(S, S)|, |E(S, S)|} < ϕ · min{vol(S), vol(S̄)}",
                f" = min({len(boundary)}, {len(reverse_boundary)}) < {phi} · min({vol_S}, {vol_S_complement})",
                f" = {min(len(boundary), len(reverse_boundary))} < {phi * min(vol_S, vol_S_complement)}",
                f" = {min(len(boundary), len(reverse_boundary)) < phi * min(vol_S, vol_S_complement)}",
            )

            if best_local_cut is None:
                best_local_cut = local_cut
            else:
                print("Updating local best cut")
                best_local_cut.update(local_cut)

        if best_global_cut is None and best_local_cut is not None:
            best_global_cut = best_local_cut
        elif best_global_cut is not None and best_local_cut is not None:
            print("Updating global best cut")
            best_global_cut.update(best_local_cut)

    if best_global_cut is None:
        return f, (set(), set(), set())

    return f, best_global_cut.get_tuple()


@dataclass
class Cut:
    S_leq_i: set[Vertex]
    S_leq_i_complement: set[Vertex]
    edges: set[Edge]
    value: int

    def update(self, other: Self):
        if other.value < self.value:
            print("Best cut updated:", other.value)

            self.S_leq_i = other.S_leq_i
            self.S_leq_i_complement = other.S_leq_i_complement
            self.edges = other.edges
            self.value = other.value

    def print(self):
        print("Cut:", self.S_leq_i, self.S_leq_i_complement)
        print("value:", self.value)
        print("edges:", self.edges)

    def get_tuple(self):
        return (
            self.S_leq_i.copy(),
            self.S_leq_i_complement.copy(),
            self.edges,
        )


def dijsktra(
    G: Graph,
    instance: WeightedPushRelabel,
    S_0: list[Vertex],
    w_f: Callable[[Edge], int],
) -> list[dict[int, set[Vertex]]]:
    level_collections: list[dict[int, set[Vertex]]] = []

    for start in S_0:
        # Compute w_f-distance levels in the residual graph
        # We'll use Dijkstra's algorithm to compute distances
        # Initialize distances
        distances = {v: sys.maxsize for v in instance.G.V}
        distances[start] = 0

        # Compute distances using Dijkstra's algorithm
        queue = [(0, start)]
        heapq.heapify(queue)
        visited: set[Vertex] = set()

        print("Distances initialized:", distances)
        while queue:
            dist, u = heapq.heappop(queue)
            if u in visited:
                continue

            visited.add(u)
            for edge in G.outgoing[u]:
                v = edge.end()
                if v in visited or instance.c_f(edge) == 0:
                    continue

                weight = w_f(edge)

                if dist + weight < distances[v]:
                    distances[v] = dist + weight
                    heapq.heappush(queue, (distances[v], v))

        levels: dict[int, set[Vertex]] = defaultdict(set)
        for v, dist in distances.items():
            levels[dist].add(v)

        level_collections.append(levels)

    return level_collections
