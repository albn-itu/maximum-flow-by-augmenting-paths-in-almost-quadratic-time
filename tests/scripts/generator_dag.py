import random
import pathlib
from dataclasses import dataclass


@dataclass
class DagParams:
    min_per_rank: int # Nodes/Rank: How 'fat' the DAG should be
    max_per_rank: int
    min_ranks: int # Ranks: How 'tall' the DAG should be
    max_ranks: int
    percent: float # Chance of having an Edge
    min_weight: int
    max_weight: int

    num_edges: int
    seed: int


def generate_random_dag(config: DagParams):
    random.seed(config.seed)

    source = 0
    nodes = 1
    node_counter = 1

    MIN_PER_RANK = config.min_per_rank
    MAX_PER_RANK = config.max_per_rank
    MIN_RANKS = config.min_ranks
    MAX_RANKS = config.max_ranks
    PERCENT = config.percent
    MIN_WEIGHT = config.min_weight
    MAX_WEIGHT = config.max_weight

    ranks = random.randint(MIN_RANKS, MAX_RANKS)

    adjacency = []
    rank_list = []
    for i in range(ranks):
        if i == ranks - 1:
            sink = node_counter
            node_counter += 1
            nodes += 1
            for j in rank_list[i - 1]:
                weight = random.randint(MIN_WEIGHT, MAX_WEIGHT)
                adjacency.append((j, sink, weight))
            break

        # New nodes of 'higher' rank than all nodes generated till now
        new_nodes = random.randint(MIN_PER_RANK, MAX_PER_RANK)

        list = []
        for j in range(new_nodes):
            if i == 0:
                weight = random.randint(MIN_WEIGHT, MAX_WEIGHT)
                adjacency.append((source, node_counter, weight))
            list.append(node_counter)
            node_counter += 1
        rank_list.append(list)

        # Edges from old nodes ('nodes') to new ones ('new_nodes')
        if i > 0:
            for j in rank_list[i - 1]:
                for k in range(new_nodes):
                    if random.random() <= PERCENT:
                        weight = random.randint(MIN_WEIGHT, MAX_WEIGHT)
                        adjacency.append((j, k+nodes, weight))


        nodes += new_nodes

    num_edge_error = 0.4
    NUM_EDGES = config.num_edges
    # assert NUM_EDGES * (1 - num_edge_error) <= len(adjacency) <= NUM_EDGES * (1 + num_edge_error), f"Want {NUM_EDGES} edges, got {len(adjacency)}"

    lines = [f"{nodes} {len(adjacency)} {source} {sink}"]
    for u, v, cap in adjacency:
        lines.append(f"{u}-({cap})>{v}")

    return "\n".join(lines)


def make_random_dag() -> str:
    def try_generate() -> str:
        SEED = random.randint(0, 1000000)

        config = DagParams(
            num_edges=8,
            min_per_rank=3,
            max_per_rank=5,
            min_ranks=4,
            max_ranks=5,
            percent=0.2,
            min_weight=1,
            max_weight=100,
            seed=SEED
        )

        try:
            return generate_random_dag(config)
        except:
            print(f"Failed generating with {SEED}, trying again")
            return try_generate()

    return try_generate()

if __name__ == "__main__":
    for _ in range(100):
        print(make_random_dag())
        break
