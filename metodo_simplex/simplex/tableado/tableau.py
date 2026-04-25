from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from ..constants import EPSILON
from ..types import ConstraintType, Matrix, ObjectiveType
from .csv_tableau_repo import save_original_tableau_excel

if TYPE_CHECKING:
    from ..problem import LinearProgram


@dataclass
class Tableau:
    data: Matrix
    basic_vars: np.ndarray
    nonbasic_vars: np.ndarray
    num_original_vars: int
    num_constraints: int
    num_slack: int
    num_surplus: int
    num_artificial: int

    @classmethod
    def from_lp(cls, problem: LinearProgram, epsilon: float = EPSILON) -> Tableau:
        A, b = problem.A.copy(), problem.b.copy()
        constraints = problem.constraints.copy()

        for i in range(problem.m):
            if b[i] < 0:
                A[i] *= -1
                b[i] *= -1
                ct = int(constraints[i])
                constraints[i] = (
                    ConstraintType.GE if ct == ConstraintType.LE else ConstraintType.LE
                )

        n, m = problem.n, problem.m
        num_slack = int(np.sum(constraints == ConstraintType.LE))
        num_surplus = int(np.sum(constraints == ConstraintType.GE))
        num_artificial = int(
            np.sum(
                (constraints == ConstraintType.GE) | (constraints == ConstraintType.EQ)
            )
        )

        total_cols = n + num_slack + num_surplus + num_artificial + 1
        tableau = np.zeros((m + 1, total_cols), dtype=np.float64)

        slack_col = n
        surplus_col = n + num_slack
        artificial_col = n + num_slack + num_surplus
        basic_vars = []

        for i in range(m):
            tableau[i, :n] = A[i]
            ct = int(constraints[i])

            if ct == ConstraintType.LE:
                tableau[i, slack_col] = 1.0
                basic_vars.append(slack_col)
                slack_col += 1
            elif ct == ConstraintType.GE:
                tableau[i, surplus_col] = -1.0
                tableau[i, artificial_col] = 1.0
                basic_vars.append(artificial_col)
                surplus_col += 1
                artificial_col += 1
            else:
                tableau[i, artificial_col] = 1.0
                basic_vars.append(artificial_col)
                artificial_col += 1

            tableau[i, -1] = b[i]

        obj_row = -problem.c
        if problem.objective == ObjectiveType.MIN:
            obj_row = problem.c
        tableau[m, :n] = obj_row

        save_original_tableau_excel(
            matriz_tableau=tableau,
            variables_basicas=basic_vars,
            cantidad_variables_originales=n,
            cantidad_variables_holgura=num_slack,
            cantidad_variables_exceso=num_surplus,
            cantidad_variables_artificiales=num_artificial,
        )

        return cls(
            data=tableau,
            basic_vars=np.array(basic_vars, dtype=np.intp),
            nonbasic_vars=np.arange(n, dtype=np.intp),
            num_original_vars=n,
            num_constraints=m,
            num_slack=num_slack,
            num_surplus=num_surplus,
            num_artificial=num_artificial,
        )

    # PROPIEDADEWSSSWS
    @property
    def rhs_col(self) -> int:
        return self.data.shape[1] - 1

    @property
    def objective_row(self) -> int:
        return self.data.shape[0] - 1

    @property
    def artificial_start(self) -> int:
        return self.num_original_vars + self.num_slack + self.num_surplus

    @property
    def artificial_range(self) -> range:
        return range(self.artificial_start, self.artificial_start + self.num_artificial)

    @property
    def has_artificial(self) -> bool:
        return self.num_artificial > 0

    @property
    def original_range(self) -> range:
        return range(self.num_original_vars)

    @property
    def slack_range(self) -> range:
        return range(self.num_original_vars, self.num_original_vars + self.num_slack)

    @property
    def surplus_range(self) -> range:
        return range(
            self.num_original_vars + self.num_slack,
            self.num_original_vars + self.num_slack + self.num_surplus,
        )

    def var_name(self, var_index: int) -> str:
        if var_index < self.num_original_vars:
            return f"x{var_index + 1}"

        elif var_index < self.num_original_vars + self.num_slack:
            return f"s{var_index - self.num_original_vars + 1}"

        elif var_index < self.artificial_start:
            return f"e{var_index - self.num_original_vars - self.num_slack + 1}"

        else:
            return f"a{var_index - self.artificial_start + 1}"

    def value(self) -> float:
        return float(self.data[self.objective_row, self.rhs_col])

    def remove_artificial_columns(self) -> Tableau:
        if not self.has_artificial:
            return self

        end = self.artificial_start + self.num_artificial
        new_data = np.delete(self.data, range(self.artificial_start, end), axis=1)

        new_basic = np.array(
            [v - self.num_artificial if v >= end else v for v in self.basic_vars],
            dtype=np.intp,
        )

        total = self.num_original_vars + self.num_slack + self.num_surplus
        new_nonbasic = np.array(
            sorted(set(range(total)) - set(new_basic)), dtype=np.intp
        )

        return Tableau(
            data=new_data,
            basic_vars=new_basic,
            nonbasic_vars=new_nonbasic,
            num_original_vars=self.num_original_vars,
            num_constraints=self.num_constraints,
            num_slack=self.num_slack,
            num_surplus=self.num_surplus,
            num_artificial=0,
        )

    def restore_objective(self, c: np.ndarray, is_minimization: bool) -> None:
        self.data[self.objective_row, : self.num_original_vars] = (
            c if is_minimization else -c
        )

    def zero_basic_in_objective(self) -> None:
        for i in range(self.num_constraints):
            col = self.basic_vars[i]

            if col < self.cols - 1:
                self.data[self.objective_row, col] = 0.0

    def update_objective_rhs(self) -> None:
        rhs = sum(
            self.data[self.objective_row, self.basic_vars[i]]
            * self.data[i, self.rhs_col]
            for i in range(self.num_constraints)
            if self.basic_vars[i] < self.num_original_vars
        )
        self.data[self.objective_row, self.rhs_col] = -rhs

    @property
    def cols(self) -> int:
        return self.data.shape[1]

    @property
    def rows(self) -> int:
        return self.data.shape[0]

    def has_artificial_in_basis(self) -> bool:
        return np.any(
            (self.basic_vars >= self.artificial_start)
            & (self.basic_vars < self.artificial_start + self.num_artificial)
        )
