import time
import json
from typing import Callable, cast
import numpy as np
from pathlib import Path

type BenchSimples = float | str | int
type BenchValue = dict[str, BenchValue] | BenchSimples
type BenchType = dict[str, dict[str, BenchValue]]

bench_info: BenchType = {}
cur_bench = None
bench_scope = ""
init_time = int(time.time())


def start_benchmark(id: str):
    global cur_bench
    cur_bench = id
    bench_scope = ""
    bench_info[cur_bench] = {"start": time.time_ns()}


def _set(key: str, value: BenchValue):
    if cur_bench is None:
        return

    cur = bench_info[cur_bench]

    keys = key.split(".")
    for key in keys[:-1]:
        if key not in cur:
            cur[key] = {}
        cur = cast(dict[str, BenchValue], cur[key])

    cur[keys[-1]] = value


def _get[A](key: str) -> A | None:
    if cur_bench is None:
        return None

    cur = bench_info[cur_bench]

    keys = key.split(".")
    for key in keys[:-1]:
        if key not in cur:
            return None
        cur = cast(dict[str, BenchValue], cur[key])

    return cast(A, cur.get(keys[-1], None))


def register(key: str, value: BenchValue):
    _set(key, value)


def register_s(key: str, value: BenchValue):
    register(f"{bench_scope}.{key}", value)


def get_or_default[A: BenchValue](key: str, default: A) -> A | None:
    if cur_bench is None:
        return None

    return _get(key) or default


def get_or_default_s[A: BenchValue](key: str, default: A) -> A | None:
    return get_or_default(f"{bench_scope}.{key}", default)


def register_or_update[A: BenchValue](key: str, default: A, updater: Callable[[A], A]):
    if cur_bench is None:
        return

    val: A | None = _get(key)
    if val is not None:
        _set(key, updater(val))
    else:
        _set(key, default)


def register_or_update_s[A: BenchValue](
    key: str, default: A, updater: Callable[[A], A]
):
    register_or_update(f"{bench_scope}.{key}", default, updater)


def end_benchmark():
    global cur_bench

    if cur_bench is None:
        return

    end = time.time_ns()
    start = cast(int, _get("start") or 0)  # The 0 is just to make pyright happy

    _set("end", end)
    _set("duration_s", (end - start) / 1e9)
    cur_bench = None

    # so we have the data if we kill the program or it crashes
    write_benchmark(f"benchmark-tmp-{init_time}.json")


def write_benchmark(filename: str | None = None):
    dir = Path("benches")
    dir.mkdir(parents=True, exist_ok=True)
    with open(dir / ".gitignore", "w") as f:
        _ = f.write("*")

    if filename is None:
        filename = f"benchmark-{int(time.time())}.json"

    with open(dir / filename, "w") as f:
        json.dump(bench_info, f, cls=NpEncoder, indent=4, sort_keys=True)

    if "tmp" not in filename:
        tmp_file = dir / f"benchmark-tmp-{init_time}.json"
        if tmp_file.exists():
            tmp_file.unlink()


def set_bench_scope(scope: str):
    global bench_scope
    bench_scope = scope


def clear():
    global bench_info, bench_scope, cur_bench
    bench_info = {}
    bench_scope = ""
    cur_bench = None


class NpEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super(NpEncoder, self).default(o)
