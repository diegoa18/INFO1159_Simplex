from __future__ import annotations

import numpy as np
from typing import Optional

from ..printer_tableau import print_tableau
from ..solution import Solution
from ..tableau_logger import save_initial_tableau, save_iteration, save_final_tableau
from ..constants import EPSILON, MAX_ITERATIONS
from ..exceptions import StabilityError, UnboundedError
from ..pivot import pivot
from ..problem import LinearProgram
from ..tableado.tableau import Tableau
from ..types import ObjectiveType

class SimplexSolver:
    def __init__(self, trace: bool = False):
        self.trace = trace

    def solve(self, problem: LinearProgram):
        # 1. Preparar el Tableau (Standard: solo holguras)
        tableau = Tableau.from_lp(problem)
        save_initial_tableau(tableau)

        is_min = problem.objective == ObjectiveType.MIN
        
        # Sincronizar función objetivo si es minimización
        if is_min:
            tableau.data[tableau.objective_row, :tableau.num_original_vars] = problem.c

        # 2. Iterar hasta el óptimo
        tableau, iterations = simplex_iterate(tableau, trace=self.trace)

        if iterations >= MAX_ITERATIONS:
            raise StabilityError("Exceso de iteraciones")

        # 3. Extraer y retornar
        save_final_tableau(tableau)
        optimal_value, variables = extract(tableau)

        if is_min:
            optimal_value = -optimal_value

        return Solution(optimal_value, variables, True, iterations)

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
            save_iteration(tableau, iteration)
            return tableau, iteration

        row = choose_leaving(tableau, col, epsilon)
        if row is None:
            save_iteration(tableau, iteration)
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
        save_iteration(tableau, iteration)

def extract(tableau: Tableau):
    n = tableau.num_original_vars
    x = np.zeros(n)

    for i in range(tableau.num_constraints):
        var = int(tableau.basic_vars[i])
        if var < n:
            x[var] = tableau.data[i, tableau.rhs_col]

    return tableau.value(), tuple(x)