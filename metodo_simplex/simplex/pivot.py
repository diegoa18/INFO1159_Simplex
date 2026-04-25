from __future__ import annotations

import numpy as np

# SIEMPRE SE BUSCA [[0],[0],[1],[0],[O]], osea un solo 1 en la columna
from .constants import EPSILON
from .exceptions import PivotError, StabilityError
from .tableado.tableau import Tableau


def pivot(
    tableau: Tableau,  # estado actual
    pivot_row: int,  # fil var saliente
    pivot_col: int,  # col var entrante
    epsilon: float = EPSILON,
) -> Tableau:

    data = tableau.data.copy()

    pivot_val = data[pivot_row, pivot_col]

    if abs(pivot_val) < epsilon:  # pivot != 0
        raise PivotError(f"Pivot value at ({pivot_row}, {pivot_col}) is zero")

    data[pivot_row] /= pivot_val  # dividir fila

    # eliminar colpivot
    for i in range(data.shape[0]):
        if i == pivot_row:  # no modificar filpivot
            continue

        # coeficiente a pitiar
        factor = data[i, pivot_col]
        if abs(factor) > epsilon:
            data[i] -= (
                factor * data[pivot_row]
            )  # Ri = Ri - factor * Rpivot, para colpivot = 0

    # actualizar VB
    new_basic = tableau.basic_vars.copy()
    new_basic[pivot_row] = pivot_col  # ej: s1->x1

    total_vars = (
        tableau.num_original_vars
        + tableau.num_slack
        + tableau.num_surplus
        + tableau.num_artificial
    )
    all_vars = np.arange(total_vars, dtype=np.intp)  # para [0,1,2,..,n]

    nonbasic = np.setdiff1d(all_vars, new_basic, assume_unique=True)  # todas - VB

    return Tableau(  # nuevo objeto tableau actualizado
        data=data,
        basic_vars=new_basic,
        nonbasic_vars=nonbasic,
        num_original_vars=tableau.num_original_vars,
        num_constraints=tableau.num_constraints,
        num_slack=tableau.num_slack,
        num_surplus=tableau.num_surplus,
        num_artificial=tableau.num_artificial,
    )
