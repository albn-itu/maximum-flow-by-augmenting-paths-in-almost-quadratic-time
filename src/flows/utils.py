from src import benchmark


def benchmark_iteration(edge_updates: int):
    benchmark.register_or_update_s(
        "edge_updates", edge_updates, lambda x: x + edge_updates
    )
    benchmark.register_or_update_s(
        "max_edge_updates",
        edge_updates,
        lambda x: max(edge_updates, x),
    )
    benchmark.register_or_update_s(
        "min_edge_updates",
        edge_updates,
        lambda x: min(edge_updates, x),
    )
    benchmark.register_or_update_s("iterations", 1, lambda x: x + 1)


def finish_benchmark(flow: int):
    benchmark.register_s("flow", flow)
    updates = benchmark.get_or_default_s("edge_updates", 0)
    iters = benchmark.get_or_default_s("iterations", 1)
    if iters is not None and updates is not None:
        benchmark.register_s("avg_updates", updates / iters)
