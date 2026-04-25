import numpy as np

from .tableado.tableau import Tableau
from .simplex_solver import simplex_iterate, SimplexSolver
from .exceptions import InfeasibleError
from .solution import Solution
from .types import ObjectiveType

class TwoPhaseSolver:

    def __init__(self, trace: bool = False):
        self.trace = trace
        self.simplex = SimplexSolver(trace)

    def solve(self, problem):

        tableau = Tableau.from_lp(problem)
        self._build_phase1_objective(tableau)

        tableau, it1 = simplex_iterate(
            tableau,
            trace=self.trace
        )

        if abs(tableau.value()) > 1e-8:
            raise InfeasibleError("El problema es infactible (fase 1 ≠ 0)")

        tableau = self._remove_artificial_columns(tableau)

        self._restore_original_objective(tableau, problem)

        tableau, it2 = simplex_iterate(
            tableau,
            trace=self.trace
        )

        opt, vars_ = self._extract(tableau)

        if problem.objective == ObjectiveType.MIN:
            opt = -opt

        return Solution(opt, vars_, True, it1 + it2)

    def _build_phase1_objective(self, tableau):
        row = tableau.objective_row
        tableau.data[row] = 0

        for j in tableau.artificial_range:
            tableau.data[row, j] = 1

    def _remove_artificial_columns(self, tableau):
        return tableau.remove_artificial_columns()

    def _restore_original_objective(self, tableau, problem):
        is_min = problem.objective == ObjectiveType.MIN

        tableau.data[tableau.objective_row, :tableau.num_original_vars] = problem.c

        if is_min:
            tableau.data[tableau.objective_row] *= -1

    def _extract(self, tableau):
        n = tableau.num_original_vars
        x = np.zeros(n)

        for i in range(tableau.num_constraints):
            var = int(tableau.basic_vars[i])
            if var < n:
                x[var] = tableau.data[i, tableau.rhs_col]

        return tableau.value(), tuple(x)