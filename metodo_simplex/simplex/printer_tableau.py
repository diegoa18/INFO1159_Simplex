from typing import Optional

from .tableado.tableau import Tableau


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

    col_width = 7
    name_map = {j: tableau.var_name(j) for j in ordered_cols}

    header = "VB".ljust(3) + "Z".center(col_width)

    for j in ordered_cols:
        header += name_map[j].center(col_width)

    header += "LD".rjust(col_width)
    print(header)
    print("-" * len(header))

    for i in range(m):
        basic_var = int(tableau.basic_vars[i])
        row_str = tableau.var_name(basic_var).ljust(3) + f"{0.0:>{col_width}.2f}"

        for j in ordered_cols:
            val = tableau.data[i, j]

            if pivot_row == i and pivot_col == j:
                row_str += f"[{val:>{col_width - 2}.2f}]"
            else:
                row_str += f"{val:>{col_width}.2f}"

        row_str += f"{tableau.data[i, -1]:>{col_width}.2f}"
        print(row_str)

    print("-" * len(header))

    # fila Z
    z_row = tableau.data[tableau.objective_row]
    row_str = "Z ".ljust(3) + f"{-1.0:>{col_width}.2f}"

    for j in ordered_cols:
        row_str += f"{z_row[j]:>{col_width}.2f}"

    row_str += f"{z_row[-1]:>{col_width}.2f}"
    print(row_str)

    # info pivote
    if pivot_row is not None and pivot_col is not None and leaving_var is not None:
        print()
        entering = name_map.get(pivot_col, tableau.var_name(pivot_col))
        print(f"entra {entering}, sale {tableau.var_name(leaving_var)}")

    print()