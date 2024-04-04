
import numpy as np

def hungarian_algorithm(cost_matrix):
    """
    Implementation of the Hungarian algorithm for solving the assignment problem.
    
    Parameters:
    - cost_matrix: A square numpy array representing the cost matrix.
    
    Returns:
    - assignment: A list of tuples where each tuple represents the assignment (worker, job).
    - total_cost: The total cost of the optimal assignment.
    """
    num_workers, num_jobs = cost_matrix.shape
    
    # Step 1: Subtract the minimum value of each row from all elements of the row.
    for i in range(num_workers):
        min_val = np.min(cost_matrix[i])
        cost_matrix[i] -= min_val
    
    # Step 2: Subtract the minimum value of each column from all elements of the column.
    for j in range(num_jobs):
        min_val = np.min(cost_matrix[:, j])
        cost_matrix[:, j] -= min_val
    
    # Step 3: Find the maximum number of independent zeros in the matrix.
    num_zeros = 0
    while num_zeros < num_workers:
        num_zeros = 0
        marked_rows = np.zeros(num_workers, dtype=bool)
        marked_cols = np.zeros(num_jobs, dtype=bool)
        for i in range(num_workers):
            for j in range(num_jobs):
                if cost_matrix[i, j] == 0 and not marked_rows[i] and not marked_cols[j]:
                    marked_rows[i] = True
                    marked_cols[j] = True
                    num_zeros += 1
        if num_zeros < num_workers:
            min_unmarked_val = np.inf
            for i in range(num_workers):
                if not marked_rows[i]:
                    min_unmarked_val = min(min_unmarked_val, np.min(cost_matrix[i, ~marked_cols]))
            for i in range(num_workers):
                for j in range(num_jobs):
                    if not marked_rows[i] and not marked_cols[j]:
                        cost_matrix[i, j] -= min_unmarked_val
    
    # Step 4: Find a complete assignment of workers to jobs with minimum cost.
    assignment = []
    while len(assignment) < num_workers:
        marked_rows = np.zeros(num_workers, dtype=bool)
        marked_cols = np.zeros(num_jobs, dtype=bool)
        for i in range(num_workers):
            for j in range(num_jobs):
                if cost_matrix[i, j] == 0 and not marked_rows[i] and not marked_cols[j]:
                    assignment.append((i, j))
                    marked_rows[i] = True
                    marked_cols[j] = True
                    break
        if len(assignment) < num_workers:
            min_val = np.inf
            for i in range(num_workers):
                if not marked_rows[i]:
                    for j in range(num_jobs):
                        if not marked_cols[j]:
                            min_val = min(min_val, cost_matrix[i, j])
            for i in range(num_workers):
                for j in range(num_jobs):
                    if marked_rows[i] and marked_cols[j]:
                        cost_matrix[i, j] += min_val
                    elif not marked_rows[i] and not marked_cols[j]:
                        cost_matrix[i, j] -= min_val
    
    total_cost = sum(cost_matrix[worker, job] for worker, job in assignment)
    
    return assignment, total_cost

# Example usage:
cost_matrix = np.array([[7, 6, 2, 9, 2],
				[6, 2, 1, 3, 9],
				[5, 6, 8, 9, 5],
				[6, 8, 5, 8, 6],
				[9, 5, 6, 4, 7]])

assignment, total_cost = hungarian_algorithm(cost_matrix)
print("Optimal assignment:", assignment)
print("Total cost:", total_cost)

