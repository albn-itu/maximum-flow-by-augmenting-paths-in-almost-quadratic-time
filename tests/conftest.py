import pytest

from src import benchmark


@pytest.fixture(scope="session", autouse=True)
def end_benchmark_after_tests():
    yield
    if benchmark.bench_info != {}:
        benchmark.write_benchmark()
