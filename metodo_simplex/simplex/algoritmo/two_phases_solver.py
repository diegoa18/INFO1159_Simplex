from __future__ import annotations
import numpy as np
from .simplex_solver import simplex_iterate, extract
from ..solution import Solution
from ..tableau_logger import save_initial_tableau, save_final_tableau
from ..constants import EPSILON, MAX_ITERATIONS
from ..exceptions import StabilityError, UnboundedError
from ..problem import LinearProgram
from ..tableado.tableau import Tableau
from ..types import ObjectiveType, ConstraintType
from ..printer_tableau import print_tableau

class TwoPhaseSolver:
    def __init__(self, trace: bool = False):
        self.trace = trace

    def solve(self, problem: LinearProgram):
        tableau = Tableau.from_lp(problem)
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
        
        save_initial_tableau(tableau)
        
        tableau, iter1 = simplex_iterate(tableau, trace=self.trace)

        if abs(tableau.value()) > EPSILON:
            raise UnboundedError(f"Infactible: Z={tableau.value():.4f}")

        tableau = tableau.remove_artificial_columns()

        is_min = problem.objective == ObjectiveType.MIN
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

        save_final_tableau(tableau)
        optimal_value, variables = extract(tableau)


        if is_min:
            optimal_value = -optimal_value

        return Solution(optimal_value, variables, True, iter1 + iter2)