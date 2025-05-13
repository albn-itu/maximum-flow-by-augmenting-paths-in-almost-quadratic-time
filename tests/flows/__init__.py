from .capacity_scaling import find_max_flow as cap_find_max_flow
from .edmond_karp import MaxFlow
from .push_relabel import PushRelabel
from tests.flows.utils import TestEdge
import time
from src import benchmark


def find_max_flow(edges: list[TestEdge], capacities: list[int], s: int, t: int):
    cap, _ = wrap_register_time(cap_find_max_flow, "capacity")(edges, capacities, s, t)
    edk = wrap_register_time(
        lambda: MaxFlow(edges, capacities).max_flow(s, t), "edmond"
    )()
    pr = wrap_register_time(
        lambda: PushRelabel(edges, capacities).max_flow(s, t), "push_relabel"
    )()

    assert cap == edk
    assert cap == pr

    return cap


def wrap_register_time(func, label):
    def wrapper(*args, **kwargs):
        start = time.time_ns()
        res = func(*args, **kwargs)
        end = time.time_ns()
        benchmark.register(f"{label}.duration_s", (end - start) / 1e9)
        return res

    return wrapper
