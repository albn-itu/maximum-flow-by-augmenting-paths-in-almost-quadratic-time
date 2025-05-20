from src import benchmark


def benchmark_iteration(prefix: str, edge_updates: int):
    benchmark.register_or_update(
        f"{prefix}.edge_updates", edge_updates, lambda x: x + edge_updates
    )
    benchmark.register_or_update(
        f"{prefix}.max_edge_updates",
        edge_updates,
        lambda x: max(edge_updates, x),
    )
    benchmark.register_or_update(
        f"{prefix}.min_edge_updates",
        edge_updates,
        lambda x: min(edge_updates, x),
    )
    benchmark.register_or_update(f"{prefix}.iterations", 1, lambda x: x + 1)


def finish_benchmark(prefix: str, flow: int):
    benchmark.register(f"{prefix}.flow", flow)
    updates = benchmark.get_or_default(f"{prefix}.edge_updates", 0)
    iters = benchmark.get_or_default(f"{prefix}.iterations", 1)
    if iters is not None and updates is not None:
        benchmark.register(f"{prefix}.avg_updates", updates / iters)
