from typing import Optional
import math

from .tableado.tableau import Tableau


def format_number(value: float, width: int = 7) -> str:
    if value == 0:
        return f"{0.0:>{width}.2f}"

    abs_val = abs(value)

    # notación de potencia 10^n para números muy grandes o muy pequeños
    if abs_val >= 1e4 or (abs_val < 1e-3 and abs_val != 0):
        exp = math.floor(math.log10(abs_val))
        mantisa = value / (10 ** exp)

        # formato: mantisa×10^exp
        if abs(mantisa - round(mantisa)) < 0.01:
            # si la mantisa es casi un entero
            return f"{int(round(mantisa))}×10^{exp}"
        else:
            # si tiene decimales
            return f"{mantisa:.1f}×10^{exp}"

    # formato normal con 2 decimales
    return f"{value:>{width}.2f}"


def print_tableau(
    tableau: Tableau,
    iteration: Optional[int] = None,
    pivot_row: Optional[int] = None,
    pivot_col: Optional[int] = None,
    leaving_var: Optional[int] = None,
) -> None:

    m = tableau.num_constraints

    # encabezado de iteración (solo simplex)
    if iteration is not None:
        print(f"Iteración {iteration}\n")

    ordered_cols = (
        list(tableau.original_range)
        + list(tableau.surplus_range)
        + list(tableau.artificial_range)
        + list(tableau.slack_range)
    )

    col_width = 12
    name_map = {j: tableau.var_name(j) for j in ordered_cols}

    header = "VB".ljust(3) + "Z".center(col_width)

    for j in ordered_cols:
        header += name_map[j].center(col_width)

    header += "LD".rjust(col_width)
    print(header)
    print("-" * len(header))

    for i in range(m):
        basic_var = int(tableau.basic_vars[i])
        row_str = tableau.var_name(basic_var).ljust(3) + format_number(0.0, col_width).rjust(col_width)

        for j in ordered_cols:
            val = tableau.data[i, j]

            if pivot_row == i and pivot_col == j:
                formatted = format_number(val, col_width)
                row_str += f"[{formatted}]"
            else:
                row_str += format_number(val, col_width).rjust(col_width)

        row_str += format_number(tableau.data[i, -1], col_width).rjust(col_width)
        print(row_str)

    print("-" * len(header))

    # fila Z
    z_row = tableau.data[tableau.objective_row]
    row_str = "Z ".ljust(3) + format_number(-1.0, col_width).rjust(col_width)

    for j in ordered_cols:
        row_str += format_number(z_row[j], col_width).rjust(col_width)

    row_str += format_number(z_row[-1], col_width).rjust(col_width)
    print(row_str)

    # info pivote
    if pivot_row is not None and pivot_col is not None and leaving_var is not None:
        print()
        entering = name_map.get(pivot_col, tableau.var_name(pivot_col))
        print(f"entra {entering}, sale {tableau.var_name(leaving_var)}")

    print()
