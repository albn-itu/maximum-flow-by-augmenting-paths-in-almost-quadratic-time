import sys
import math
import heapq
from collections import defaultdict
from typing import Callable

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
) -> tuple[dict[Edge, int], tuple[set[Vertex], set[Vertex]]]:
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

    # Calculate h as defined in the algorithm
    # h = math.ceil((4 * (eta**4) * c_6_5 * (math.log(n) ** 7) * kappa) / (phi**2) * n)
    h = math.ceil(1 / phi)
    print("Height h:", h)

    # Define c^κ = κ · c
    c_kappa = [kappa * cap for cap in c]

    # Verify properties
    assert kappa <= n, "kappa should be less than or equal to n"  # Theorem 6.1
    assert kappa > 0, "kappa should be greater than 0"  # Theorem 6.1
    print(1 / phi, 1 / (10 * math.log(n)))
    assert 1 / phi <= n, (
        f"1/phi={1 / phi} should be less than or equal to n={n}"
    )  # Theorem 6.1
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
        return f, (set(), set())

    # else
    # Let w_f be w_G extended to G_f
    def w_f(e: Edge) -> int:
        # , except set w_f(e->) = 0 for e ∈ D_H
        if e in D_H and e.forward:
            return 0
        else:
            return w_G(e)

    # set S₀ = {s ∈ V : Δ_f(s) > 0}
    S_0: set[Vertex] = set(v for v in G.V if instance.excess(v) > 0)

    print("Calculating distance levels")
    distance_levels = dijsktra(G, instance, S_0, w_f)
    print("Distance levels:", distance_levels)

    # Compute S_≤i for each i and find the minimizing cut
    best_cut_value = float("inf")
    best_cut: tuple[set[Vertex], set[Vertex]] = (set(), set())
    max_level = max(distance_levels.keys())

    assert max_level >= 0, "Max level should be non-negative"

    # Calculate vol_F for each vertex
    vol_F: dict[Vertex, int] = defaultdict(int)
    for edge in set(e for edges in G.outgoing.values() for e in edges):
        if edge in F and instance.c_f(edge) > 0:
            vol_F[edge.start()] += 1
            vol_F[edge.end()] += 1

    S_leq_i: set[Vertex] = set()  # S_≤i
    for i in sorted(list(distance_levels.keys())):
        # Add vertices from level i to S_≤i
        S_leq_i.update(distance_levels[i])
        S_leq_i_complement = set(G.V) - S_leq_i

        # Calculate c^κ_f(E_{G_f}(S_≤i, S̄_≤i))
        cut_capacity = 0
        boundary_size = 0
        reverse_boundary_size = 0
        for u in S_leq_i:
            for edge in G.incident[u]:
                if instance.c_f(edge) <= 0:
                    continue

                if edge.end() in S_leq_i_complement:
                    cut_capacity += edge.c
                    boundary_size += 1

                if edge.start() in S_leq_i_complement:
                    reverse_boundary_size += 1

        # Calculate vol_F(S_≤i) and vol_F(S̄_≤i)
        vol_S = sum(vol_F[v] for v in S_leq_i)
        vol_S_complement = sum(vol_F[v] for v in S_leq_i_complement)

        # Calculate the minimum of vol_F(S_≤i) and vol_F(S̄_≤i)
        min_vol = min(vol_S, vol_S_complement)

        # Calculate the value to be minimized
        value = cut_capacity - min_vol
        print(f"\n== Level {i} ==")
        if boundary_size == 0:
            print("Boundary size is 0, skipping")
            continue

        print("leq", i)
        print("S, S_complement", S_leq_i, S_leq_i_complement)
        print(
            f"cut_cap - min(vol_S, vol_S_complement): {cut_capacity} - min({vol_S}, {vol_S_complement})"
        )
        print("value:", value)
        print("best_cut_value:", best_cut_value)

        # For interest, calculate the Cheeger constant
        if min_vol == 0:
            cheeger_constant = float("inf")
        else:
            cheeger_constant = boundary_size / min_vol
        print("Boundary size:", boundary_size)
        print("Cheeger constant:", cheeger_constant)

        # For interest, calculate the sparsity of the cut
        # Calculated based on https://home.ttic.edu/~yury/courses/geometry/notes/sparsest-cut.pdf
        smallest_vertex_set = min(len(S_leq_i), len(S_leq_i_complement))
        if smallest_vertex_set == 0:
            sparsity = float("inf")
        else:
            sparsity = boundary_size / smallest_vertex_set
        print("Sparsity:", sparsity)
        print(
            "min{|E(S, S)|, |E(S, S)|} < ϕ · min{vol(S), vol(S̄)}",
            f" = min({boundary_size}, {reverse_boundary_size}) < {phi} · min({vol_S}, {vol_S_complement})",
            f" = {min(boundary_size, reverse_boundary_size)} < {phi * min(vol_S, vol_S_complement)}",
            f" = {min(boundary_size, reverse_boundary_size) < phi * min(vol_S, vol_S_complement)}",
        )
        if value < best_cut_value:
            best_cut_value = value
            best_cut = (S_leq_i.copy(), S_leq_i_complement.copy())
            print("Best cut updated:", best_cut)
            print("Best cut Cheeger constant:", cheeger_constant)
            print("Best cut sparsity:", sparsity)

    print("source 0", [instance.residual_source(v) for v in best_cut[0]])
    print("source 1", [instance.residual_source(v) for v in best_cut[1]])
    print("sinks 0", [instance.residual_sink(v) for v in best_cut[0]])
    print("sinks 1", [instance.residual_sink(v) for v in best_cut[1]])

    return f, best_cut


def dijsktra(
    G: Graph,
    instance: WeightedPushRelabel,
    S_0: set[Vertex],
    w_f: Callable[[Edge], int],
) -> dict[int, set[Vertex]]:
    # Compute w_f-distance levels in the residual graph
    # We'll use Dijkstra's algorithm to compute distances
    # Initialize distances
    distances = {v: sys.maxsize for v in instance.G.V}

    for s in S_0:
        distances[s] = 0

    # Compute distances using Dijkstra's algorithm
    queue = [(0, s) for s in S_0]
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

    return levels
