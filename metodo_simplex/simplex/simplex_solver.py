from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .constants import EPSILON, MAX_ITERATIONS
from .exceptions import InfeasibleError, StabilityError, UnboundedError
from .pivot import pivot
from .problem import LinearProgram
from .tableau import Tableau
from .types import ObjectiveType

# SOLVER


@dataclass(frozen=True)
class Solution:
    optimal_value: float
    variables: tuple[float, ...]  # vector solucion
    is_optimal: bool
    iterations: int


# visualizacion
def print_tableau(
    tableau: Tableau,
    iteration: Optional[int] = None,
    phase: Optional[int] = None,
    pivot_row: Optional[int] = None,
    pivot_col: Optional[int] = None,
    leaving_var: Optional[int] = None,  # var saliente
) -> None:

    m = tableau.num_constraints  # n restricciones

    if iteration is not None or phase is not None:
        parts = []  # para texto

        if iteration is not None:  # conteo iteracion
            parts.append(f"Iteración {iteration}")

        if phase is not None:  # fase
            parts.append(f"Fase {phase}")

        print(" ".join(parts))  # construccion texto
        print()

    ordered_cols = (  # orden columnas
        list(tableau.original_range)
        + list(tableau.surplus_range)
        + list(tableau.artificial_range)
        + list(tableau.slack_range)
    )

    col_width = 7
    name_map = {
        j: tableau.var_name(j) for j in ordered_cols
    }  # comprension de diccionario para obtener nombre a partir de j

    header = "VB".ljust(3) + "Z".center(col_width)  # centrar VB Z

    for j in ordered_cols:  # 1 col por var
        header += name_map[j].center(col_width)

    header += "LD".rjust(col_width)  # ultima columna LD
    print(header)
    print("-" * len(header))

    for i in range(m):  # m = restricciones
        basic_var = int(tableau.basic_vars[i])  # VB de la fila
        row_str = (
            tableau.var_name(basic_var).ljust(3) + f"{0.0:>{col_width}.2f}"
        )  # inicio fila

        for j in ordered_cols:  # recorrer cols
            val = tableau.data[i, j]
            # "[pivote]"
            if pivot_row == i and pivot_col == j:
                row_str += f"[{val:>{col_width - 2}.2f}]"

            else:
                row_str += f"{val:>{col_width}.2f}"

        # imprimir fila
        row_str += f"{tableau.data[i, -1]:>{col_width}.2f}"
        print(row_str)

    print("-" * len(header))

    # Z
    z_row = tableau.data[tableau.objective_row]
    row_str = " Z".ljust(2) + f"{-1.0:>{col_width}.2f}"

    # coeficientes
    for j in ordered_cols:
        row_str += f"{z_row[j]:>{col_width}.2f}"

    # LD de Z
    row_str += f"{z_row[-1]:>{col_width}.2f}"
    print(row_str)

    # mostrar quien entra y quien sale en el pivoteo
    if pivot_row is not None and pivot_col is not None and leaving_var is not None:
        print()
        entering = name_map.get(pivot_col, tableau.var_name(pivot_col))
        print(f"entra {entering}, sale {tableau.var_name(leaving_var)}")

    print()


# elegir entrante
def choose_entering(tableau: Tableau, epsilon: float = EPSILON) -> Optional[int]:
    obj = tableau.data[tableau.objective_row, :-1]  # fila Z
    candidates = np.where(obj < -epsilon)[0]  # donde Zi < 0(EPS)
    return (
        int(candidates[0]) if candidates.size else None
    )  # elige al primero de los candidatos


def choose_leaving(
    tableau: Tableau, pivot_col: int, epsilon: float = EPSILON
) -> Optional[int]:
    rhs = tableau.data[:-1, -1]  # LD
    col = tableau.data[:-1, pivot_col]  # col piv

    min_ratio = np.inf  # iniciar con inf
    leaving_row = None

    # recorrer cada restriccion
    for i in range(len(rhs)):
        if col[i] > epsilon:  # aij > 0
            ratio = (
                rhs[i] / col[i]
            )  # LDi / aij -> cociente entre LD actual y su valor en la col piv
            if ratio < min_ratio - epsilon or (
                # caso empate -> fila mas pequeña
                abs(ratio - min_ratio) < epsilon
                and (leaving_row is None or i < leaving_row)
            ):
                # update
                min_ratio = ratio
                leaving_row = i

    return leaving_row


def extract(tableau: Tableau) -> tuple[float, tuple[float, ...]]:
    optimal_value = tableau.value()
    n = tableau.num_original_vars  # n var originales
    solution = np.zeros(n)

    for i in range(tableau.num_constraints):
        var = int(tableau.basic_vars[i])  # identificar VB

        if var < n:  # solo VB OG, porque consideramo el LD de las VB originales
            solution[var] = tableau.data[i, tableau.rhs_col]

    return optimal_value, tuple(float(v) for v in solution)


def setup_phase1(tableau: Tableau) -> None:
    tableau.data[tableau.objective_row] = 0.0

    for i in range(tableau.num_constraints):
        basic = tableau.basic_vars[i]
        if (
            tableau.artificial_start
            <= basic
            < tableau.artificial_start + tableau.num_artificial
        ):
            coeff = tableau.data[i, basic]
            row = tableau.data[i, :-1].copy()
            row[basic] = 0.0

            if coeff > 0:
                tableau.data[tableau.objective_row, :-1] -= row
                tableau.data[tableau.objective_row, -1] += tableau.data[i, -1]
            else:
                tableau.data[tableau.objective_row, :-1] += row
                tableau.data[tableau.objective_row, -1] -= tableau.data[i, -1]

    end = tableau.artificial_start + tableau.num_artificial
    tableau.data[tableau.objective_row, tableau.artificial_start : end] = 0.0


def remove_artificial_from_basis(tableau: Tableau, epsilon: float = EPSILON) -> Tableau:
    while tableau.has_artificial_in_basis():
        artificial_col = next(
            (j for j in tableau.artificial_range if j in tableau.nonbasic_vars), None
        )
        if artificial_col is None:
            raise StabilityError("imposible remover 'a' desde base")

        row = choose_leaving(tableau, artificial_col, epsilon)
        if row is None:
            raise StabilityError("no hay fila saliente valida para 'a'")

        tableau = pivot(tableau, row, artificial_col, epsilon)
        setup_phase1(tableau)

    return tableau


def simplex_iterate(
    tableau: Tableau,
    phase: int,
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

        if phase == 1:
            setup_phase1(tableau)

        if trace:
            print_tableau(tableau, iteration + 1, phase, row, col, leaving)

        iteration += 1


def solve(
    problem: LinearProgram,
    epsilon: float = EPSILON,
    max_iterations: int = MAX_ITERATIONS,
    trace: bool = False,
) -> Solution:
    tableau = Tableau.from_lp(problem, epsilon)

    if trace:
        print("-" * 60)
        print("simplex solver, tabla inicial")
        print("-" * 60)
        print_tableau(tableau)

    is_min = problem.objective == ObjectiveType.MIN

    if tableau.has_artificial:
        setup_phase1(tableau)

        if trace:
            print_tableau(tableau, phase=1)
        tableau, iterations_p1 = simplex_iterate(tableau, 1, epsilon, trace)

        if iterations_p1 >= max_iterations:
            raise StabilityError(f"fase excede las {max_iterations} iteraciones")

        if abs(tableau.value()) > epsilon:
            raise InfeasibleError(
                f"problema infactible, fase 1 objetivo: {tableau.value()}"
            )

        tableau = remove_artificial_from_basis(tableau, epsilon)
        tableau = tableau.remove_artificial_columns()
        tableau.restore_objective(problem.c, is_min)
        tableau.update_objective_rhs()
        tableau.zero_basic_in_objective()

        if trace:
            print_tableau(tableau, phase=2)

    else:
        if is_min:
            tableau.data[tableau.objective_row, : tableau.num_original_vars] = problem.c
        if trace:
            print_tableau(tableau, phase=2)

    tableau, iteration = simplex_iterate(tableau, 2, epsilon, trace)

    if iteration >= max_iterations:
        raise StabilityError(f"Simplex excede las {max_iterations} iteraciones")

    if tableau.has_artificial_in_basis():
        raise UnboundedError("cuek")

    optimal_value, variables = extract(tableau)
    if is_min:
        optimal_value = -optimal_value

    return Solution(optimal_value, variables, True, iteration)
