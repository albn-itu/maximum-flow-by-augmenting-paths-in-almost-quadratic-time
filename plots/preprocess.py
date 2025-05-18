from typing import TypedDict


class BenchmarkConfig(TypedDict):
    expected: int
    file: str
    name: str
    sink: int
    source: int
    top_sort: bool


class AlgorithmMetrics(TypedDict, total=False):
    avg_updates: float
    edge_updates: int
    flow: int
    iterations: int
    max_edge_updates: int
    min_edge_updates: int
    highest_level: int | None
    marked_admissible: int | None
    marked_dead: int | None
    marked_inadmissible: int | None
    dag_marked_admissible: int | None
    dag_marked_inadmissible: int | None
    relabels: int | None


class InstanceData(TypedDict):
    h: int
    m: int
    n: int


class BenchmarkResult(TypedDict):
    bench_config: BenchmarkConfig
    blik: AlgorithmMetrics
    capacity: AlgorithmMetrics
    edmond: AlgorithmMetrics
    push_relabel: AlgorithmMetrics
    duration_s: float
    end: int
    instance: InstanceData
    start: int


# Example for handling multiple test cases in a JSON file
type BenchmarkData = dict[str, BenchmarkResult]
type ProcessedKey = str | int | float | bool | None
type ProcessedRun = dict[str, ProcessedKey]
type ProcessedRunList = list[ProcessedRun]


def set_keys(
    processed_data: ProcessedRun, data: BenchmarkResult, key: str
) -> ProcessedRun:
    if key not in data:
        return processed_data

    for child_key, value in data[key].items():
        if isinstance(value, dict):
            new_data = set_keys({}, data[key], f"{child_key}")
            for new_key, new_value in new_data.items():
                processed_data[f"{key}.{new_key}"] = new_value
        else:
            processed_data[f"{key}.{child_key}"] = value

    return processed_data


def preprocess(data: BenchmarkData) -> ProcessedRunList:
    processed_runs: ProcessedRunList = []

    for run_name, run_data in data.items():
        if "end" not in run_data.keys():
            continue
        names = run_name.replace("tests/", "").replace(" (call)", "").split("::")

        run_file = names[0]
        run_class_name = names[1] if len(names) > 2 else None

        if len(names) > 2:
            function_name_split = names[2].split("[")
            run_function_name = function_name_split[0]
            run_id = (
                function_name_split[1].replace("]", "")
                if len(function_name_split) > 1
                else None
            )
        else:
            run_function_name = names[1]
            run_id = None

        processed_data: ProcessedRun = {
            "file": run_file,
            "class_name": run_class_name,
            "function_name": run_function_name,
            "param_id": run_id,
            "start": run_data["start"],
            "end": run_data["end"],
            "duration_s": run_data["duration_s"],
        }
        processed_data = set_keys(processed_data, run_data, "bench_config")
        processed_data = set_keys(processed_data, run_data, "instance")
        processed_data = set_keys(processed_data, run_data, "blik")
        processed_data = set_keys(processed_data, run_data, "capacity")
        processed_data = set_keys(processed_data, run_data, "edmond")
        processed_data = set_keys(processed_data, run_data, "push_relabel")
        processed_data = set_keys(processed_data, run_data, "state_change")

        processed_runs.append(processed_data)

    return processed_runs
