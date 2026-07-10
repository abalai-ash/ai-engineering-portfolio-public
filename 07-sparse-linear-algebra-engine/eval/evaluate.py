from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.append(str(SRC_PATH))

from sparse_linear_algebra_v1 import build_demo_link_matrix, pagerank_style_iteration


def main() -> None:
    matrix = build_demo_link_matrix()
    result = pagerank_style_iteration(matrix)

    ranked_nodes = result["ranked_nodes"]
    top_nodes = [ranked_nodes[0]["node"], ranked_nodes[1]["node"]]

    checks = [
        {
            "name": "matrix_has_sparse_entries",
            "passed": len(matrix.entries) < matrix.rows * matrix.cols,
            "detail": f"{len(matrix.entries)} stored entries for {matrix.rows * matrix.cols} possible cells",
        },
        {
            "name": "rank_vector_sums_to_one",
            "passed": abs(sum(result["final_rank"]) - 1.0) < 1e-6,
            "detail": f"sum={sum(result['final_rank']):.6f}",
        },
        {
            "name": "iteration_converged",
            "passed": result["converged"],
            "detail": f"steps={result['steps']}",
        },
        {
            "name": "expected_top_nodes",
            "passed": set(top_nodes) == {0, 2},
            "detail": f"top nodes={top_nodes}",
        },
    ]

    passed = sum(1 for check in checks if check["passed"])
    total = len(checks)

    output_path = PROJECT_ROOT / "eval" / "eval_results.md"

    lines = [
        "# Evaluation Results",
        "",
        f"Passed {passed}/{total} checks.",
        "",
        "| Check | Passed | Detail |",
        "|---|---:|---|",
    ]

    for check in checks:
        status = "yes" if check["passed"] else "no"
        lines.append(f"| {check['name']} | {status} | {check['detail']} |")

    lines.extend(
        [
            "",
            "## Final Ranking",
            "",
            "| Node | Score |",
            "|---:|---:|",
        ]
    )

    for item in ranked_nodes:
        lines.append(f"| {item['node']} | {item['score']:.4f} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This is a small synthetic sparse linear algebra demo. It is not a production search or recommendation system.",
            "The goal is to show sparse matrix representation, matrix-vector multiplication, iterative ranking, convergence checks, and basic evaluation.",
        ]
    )

    output_path.write_text("\n".join(lines) + "\n")

    print(f"Evaluation complete: {passed}/{total} checks passed")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
