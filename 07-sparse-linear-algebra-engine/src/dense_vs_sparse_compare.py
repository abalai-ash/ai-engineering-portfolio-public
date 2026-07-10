from sparse_linear_algebra_v1 import SparseMatrixCOO, build_demo_link_matrix


def dense_matvec(matrix, vector):
    result = []

    for row in matrix:
        total = 0.0
        for value, vector_value in zip(row, vector):
            total += value * vector_value
        result.append(total)

    return result


def sparse_to_dense(matrix: SparseMatrixCOO):
    dense = [[0.0 for _ in range(matrix.cols)] for _ in range(matrix.rows)]

    for row, col, value in matrix.entries:
        dense[row][col] = value

    return dense


def main():
    sparse_matrix = build_demo_link_matrix()
    dense_matrix = sparse_to_dense(sparse_matrix)
    vector = [0.25, 0.25, 0.25, 0.25]

    sparse_result = sparse_matrix.matvec(vector)
    dense_result = dense_matvec(dense_matrix, vector)

    dense_cells = sparse_matrix.rows * sparse_matrix.cols
    sparse_cells = len(sparse_matrix.entries)

    print("Dense vs Sparse Comparison")
    print("--------------------------")
    print(f"Dense stored cells: {dense_cells}")
    print(f"Sparse stored entries: {sparse_cells}")
    print(f"Storage reduction: {dense_cells - sparse_cells} fewer stored values")
    print()
    print(f"Sparse result: {[round(value, 4) for value in sparse_result]}")
    print(f"Dense result:  {[round(value, 4) for value in dense_result]}")
    print(f"Results match: {sparse_result == dense_result}")


if __name__ == "__main__":
    main()
