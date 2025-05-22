from collections.abc import Callable


from src.utils import Graph
from .capacity_scaling import CapacityScaling
from .edmond_karp import MaxFlow
from .classic_push_relabel import PushRelabel
from .dinic import Dinic
import time
from src import benchmark


def find_max_flow(G: Graph, s: int, t: int) -> int:
    cap = wrap_register_time(lambda: CapacityScaling(G).max_flow(s, t), "capacity")()
    edk = wrap_register_time(lambda: MaxFlow(G).max_flow(s, t), "edmond")()
    pr = wrap_register_time(lambda: PushRelabel(G).max_flow(s, t), "push_relabel")()
    dinic = wrap_register_time(lambda: Dinic(G).max_flow(s, t), "dinic")()

    assert edk == pr, f"Edmond-Karp: {edk}, Push-Relabel: {pr}"
    assert cap == edk, f"Capacity: {cap}, Edmond-Karp: {edk}"
    assert dinic == pr, f"Dinic: {dinic}, Push-Relabel: {pr}"

    return pr


def wrap_register_time(func: Callable[[], int], label: str):
    def wrapper(*args, **kwargs):
        start = time.time_ns()
        res = func(*args, **kwargs)
        end = time.time_ns()
        benchmark.register(f"{label}.duration_s", (end - start) / 1e9)
        return res

    return wrapper
