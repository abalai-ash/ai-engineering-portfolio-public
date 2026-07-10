from dataclasses import dataclass
from typing import Dict, List, Tuple
import math


@dataclass
class SparseMatrixCOO:
    rows: int
    cols: int
    entries: List[Tuple[int, int, float]]

    def matvec(self, vector: List[float]) -> List[float]:
        if len(vector) != self.cols:
            raise ValueError("Vector length must match matrix column count.")

        result = [0.0 for _ in range(self.rows)]

        for row, col, value in self.entries:
            result[row] += value * vector[col]

        return result

    def density(self) -> float:
        total_cells = self.rows * self.cols
        if total_cells == 0:
            return 0.0
        return len(self.entries) / total_cells


def normalize_vector(vector: List[float]) -> List[float]:
    total = sum(vector)
    if total == 0:
        return [1.0 / len(vector) for _ in vector]
    return [value / total for value in vector]


def l1_distance(left: List[float], right: List[float]) -> float:
    return sum(abs(a - b) for a, b in zip(left, right))


def build_demo_link_matrix() -> SparseMatrixCOO:
    """
    Small column-stochastic link matrix.

    Entry (row, col, value) means:
    node col passes value of its score to node row.
    This is similar to the structure used in PageRank-style ranking.
    """
    entries = [
        (1, 0, 0.5),
        (2, 0, 0.5),

        (2, 1, 1.0),

        (0, 2, 0.5),
        (3, 2, 0.5),

        (0, 3, 1.0),
    ]

    return SparseMatrixCOO(rows=4, cols=4, entries=entries)


def pagerank_style_iteration(
    matrix: SparseMatrixCOO,
    damping: float = 0.85,
    max_steps: int = 30,
    tolerance: float = 1e-6,
) -> Dict[str, object]:
    n = matrix.rows
    rank = [1.0 / n for _ in range(n)]
    history = []

    for step in range(1, max_steps + 1):
        linked_score = matrix.matvec(rank)
        random_jump = (1.0 - damping) / n
        next_rank = [random_jump + damping * score for score in linked_score]
        next_rank = normalize_vector(next_rank)

        delta = l1_distance(rank, next_rank)
        history.append({"step": step, "rank": next_rank, "delta": delta})

        rank = next_rank

        if delta < tolerance:
            break

    ranked_nodes = sorted(
        [{"node": idx, "score": score} for idx, score in enumerate(rank)],
        key=lambda item: item["score"],
        reverse=True,
    )

    return {
        "final_rank": rank,
        "ranked_nodes": ranked_nodes,
        "steps": len(history),
        "history": history,
        "converged": history[-1]["delta"] < tolerance if history else False,
    }


def main() -> None:
    matrix = build_demo_link_matrix()
    result = pagerank_style_iteration(matrix)

    print("Sparse Linear Algebra Demo")
    print("--------------------------")
    print(f"Matrix shape: {matrix.rows} x {matrix.cols}")
    print(f"Stored entries: {len(matrix.entries)}")
    print(f"Density: {matrix.density():.3f}")
    print(f"Converged: {result['converged']}")
    print(f"Steps: {result['steps']}")
    print()
    print("Final ranking:")

    for item in result["ranked_nodes"]:
        print(f"node_{item['node']}: {item['score']:.4f}")


if __name__ == "__main__":
    main()
