from __future__ import annotations

import numpy as np
from typing import Optional

from .printer_tableau import print_tableau
from .exceptions import StabilityError
from .pivot import pivot
from .problem import LinearProgram, Solution
from .tableau import Tableau
from .types import ObjectiveType, EPSILON

class SimplexSolver:
    def __init__(self, trace: bool = False):
        self.trace = trace

    def solve(self, problem: LinearProgram):
        tableau = Tableau.from_lp(problem)

        is_min = problem.objective == ObjectiveType.MIN
        
        if len(tableau.artificial_range) > 0:
            return self.two_phases(tableau, problem, is_min)
        
        return self.standar(tableau, problem, is_min)

    def standar(self, tableau, problem, is_min):
        if is_min:
            tableau.data[tableau.objective_row, :tableau.num_original_vars] = problem.c

        tableau, iterations = simplex_iterate(tableau, trace=self.trace)

        optimal_value, variables = extract(tableau)

        if is_min:
            optimal_value = -optimal_value

        return Solution(optimal_value, variables, True, iterations)
    
    def two_phases(self, tableau, problem, is_min):
        z_row = tableau.objective_row
        
        tableau.data[z_row, :] = 0
        for j in tableau.artificial_range:
            tableau.data[z_row, j] = 1.0
        
        for i in range(tableau.num_constraints):
            var_en_base = int(tableau.basic_vars[i])
            if var_en_base in tableau.artificial_range:
                tableau.data[z_row, :] -= tableau.data[i, :]

        if self.trace:
            print("\n--- TABLA INICIAL FASE 1 ---")
            print_tableau(tableau)

        tableau, iter1 = simplex_iterate(tableau, trace=self.trace)

        if abs(tableau.value()) > EPSILON:
            raise StabilityError(f"Infactible: Z={tableau.value():.4f}")
        
        tableau = tableau.remove_artificial_columns()
        tableau.restore_objective(problem.c, is_min)

        new_z_row = tableau.objective_row
        for i in range(tableau.num_constraints):
            var_idx = int(tableau.basic_vars[i])
            coef_z = tableau.data[new_z_row, var_idx]
            if abs(coef_z) > EPSILON:
                tableau.data[new_z_row, :] -= coef_z * tableau.data[i, :]

        if self.trace:
            print("\n--- TABLA INICIAL FASE 2 ---")
            print_tableau(tableau)

        tableau, iter2 = simplex_iterate(tableau, trace=self.trace)

        optimal_value, variables = extract(tableau)

        if is_min:
            optimal_value = -optimal_value

        return Solution(optimal_value, variables, True, iter1 + iter2)

def choose_entering(tableau: Tableau, epsilon: float = EPSILON) -> Optional[int]:
    obj = tableau.data[tableau.objective_row, :-1]
    candidates = np.where(obj < -epsilon)[0]
    return int(candidates[0]) if candidates.size else None


def choose_leaving(
    tableau: Tableau,
    pivot_col: int,
    epsilon: float = EPSILON
) -> Optional[int]:

    rhs = tableau.data[:-1, -1]
    col = tableau.data[:-1, pivot_col]

    min_ratio = np.inf
    leaving_row = None

    for i in range(len(rhs)):
        if col[i] > epsilon:
            ratio = rhs[i] / col[i]

            if ratio < min_ratio - epsilon or (
                abs(ratio - min_ratio) < epsilon and
                (leaving_row is None or i < leaving_row)
            ):
                min_ratio = ratio
                leaving_row = i

    return leaving_row

def simplex_iterate(
    tableau: Tableau,
    epsilon: float = EPSILON,
    trace: bool = False,
) -> tuple[Tableau, int]:

    iteration = 0

    while True:

        col = choose_entering(tableau, epsilon)
        if col is None:
            return tableau, iteration

        row = choose_leaving(tableau, col, epsilon)
        if row is None:
            return tableau, iteration

        leaving = int(tableau.basic_vars[row])

        tableau = pivot(tableau, row, col, epsilon)

        if trace:
            print_tableau(
                tableau,
                iteration=iteration + 1,
                pivot_row=row,
                pivot_col=col,
                leaving_var=leaving,
            )

        iteration += 1

def extract(tableau: Tableau):
    n = tableau.num_original_vars
    x = np.zeros(n)

    for i in range(tableau.num_constraints):
        var = int(tableau.basic_vars[i])
        if var < n:
            x[var] = tableau.data[i, tableau.rhs_col]

    return tableau.value(), tuple(x)