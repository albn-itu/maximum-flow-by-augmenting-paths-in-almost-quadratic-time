"""
Pseudocode for computing expander decomposition via sparse cuts.
Based on the approach described in "Maximum Flow by Augmenting Paths in n^2+o(1) Time".
"""

from collections import defaultdict
from src.sparse_cut import sparse_cut
from src.utils import Edge, Graph, Vertex


def expander_decomposition(
    I: tuple[Graph, list[int], dict[Vertex, int], dict[Vertex, int]],
    kappa: int,
    F: set[Edge],
    H: dict[int, set[Edge]],
    c_6_5: int = 1,  # Constant from the paper
    phi: float = 0.1,  # Phi parameter from the paper
) -> set[Edge]:
    """
    Computes a ϕ-expander decomposition of graph G with respect to terminal set F.


    Parameters:
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

    Returns:
    - X: Separator set such that F is ϕ-expanding in G \\ X
    """
    G_init, c, sources_init, sinks_init = I

    # Initialize working variables
    queue = [(G_init, sources_init, sinks_init)]
    X: set[Edge] = set()  # Accumulates cut edges
    U: list[set[Vertex]] = []  # Collection of vertex sets

    # Process each strongly connected component
    while len(queue) > 0:
        G, sources, sinks = queue.pop(0)

        print("\n================")
        if len(G.V) <= 1:
            print("Trivially expanding due to 1 vertex", G.V)
            U.append(set(G.V))
            continue

        # Check if trivially expanding
        sum_vol = sum(G.volume(v) for v in G.V)
        print(f"Sum volume: {sum_vol} for vertices {G.V}, 1/phi: {1 / phi}")
        if sum_vol < 1 / phi:
            print(f"Trivially expanding since not {sum_vol} < {1 / phi}", G.V)
            U.append(set(G.V))
            # Small volume makes F trivially ϕ-expanding
            continue

        if not (1 / phi <= len(G.V)):
            print(f"Trivially expanding since not {1 / phi} <= {len(G.V)}", G.V)
            U.append(set(G.V))
            # Small volume makes F trivially ϕ-expanding
            continue

        print(
            "Processing component with vertices:",
            G.V,
            " sinks, sources:",
            sinks,
            sources,
        )

        # Subgraph induced by the component
        F_component = F.intersection(G.all_edges())

        # Try to find a sparse cut or certify that F is expanding
        _, cut = sparse_cut(
            I=(
                G,
                G.c,
                sources,
                sinks,
            ),
            kappa=min(len(G.V), kappa),
            F=F_component,
            H=H,
            c_6_5=c_6_5,
            phi=phi,
            # TODO: w_H
        )

        S, S_hat, edges = cut

        if len(S) == 0 and len(S_hat) == 0:
            print("Already expanding", G.V)
            # F is already ϕ-expanding in this component, nothing to do
            U.append(set(G.V))
            continue
        else:
            print("Edges added to cut", edges)
            # Add cut edges to separator
            X.update(edges)

            # Recurse on both sides of the cut
            G_S = subgraph(G, c, S)
            G_S_hat = subgraph(G, c, S_hat)

            queue.append((G_S, *select_sources_and_sinks(G_S)))
            queue.append((G_S_hat, *select_sources_and_sinks(G_S_hat)))

    print("Final cut", X)
    print("Vertex sets", U)
    return X


def subgraph(
    G: Graph,
    c: list[int],
    vertices: set[Vertex],
) -> Graph:
    """
    Returns the subgraph of G induced by the given vertices.
    """

    new_edges: list[tuple[int, int]] = []

    for edge in G.E:
        u, v = edge
        if u in vertices and v in vertices:
            new_edges.append(edge)

    return Graph(
        list(vertices),
        new_edges,
        c,  # Just use c, since we use edge.id to lookup capacities
    )


def select_sources_and_sinks(G: Graph) -> tuple[dict[Vertex, int], dict[Vertex, int]]:
    if len(G.V) <= 1:
        return {}, {}

    out_degrees: dict[int, set[Vertex]] = defaultdict(set)
    in_degrees: dict[int, set[Vertex]] = defaultdict(set)

    for u in G.V:
        out_degrees[len(list(filter(lambda t: t.forward, G.outgoing[u])))].add(u)
        in_degrees[len(list(filter(lambda t: t.forward, G.incoming[u])))].add(u)

    largest_out_degree = max(out_degrees.keys())

    sources = {
        v: sum(G.c[e.id] for e in G.outgoing[v])
        for v in out_degrees[largest_out_degree]
    }

    sinks = {}
    for degree in sorted(list(in_degrees.keys()), reverse=True):
        sinks = {
            v: sum(G.c[e.id] for e in G.incoming[v])
            for v in in_degrees[degree]
            if v not in sources
        }
        print(degree, sinks, in_degrees, in_degrees[degree])

        if len(sinks) > 0:
            break

    if len(sinks) == 0 and len(sources) > 1 and len(in_degrees) == 1:
        largest_in_degree = max(in_degrees.keys())
        sinks = {
            v: sum(G.c[e.id] for e in G.incoming[v])
            for v in in_degrees[largest_in_degree]
        }
        del sources[in_degrees[largest_in_degree].pop()]
    elif len(sinks) == 0:
        raise ValueError(
            "No sinks found, check the graph structure or the source selection logic."
        )

    return defaultdict(int, sources), defaultdict(int, sinks)
