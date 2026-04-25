from .tableado.xlsx_tableau_repo import (
    save_original_tableau_excel,
    save_iteration_tableau_excel,
)
from .tableado.tableau import Tableau


def save_initial_tableau(tableau: Tableau, filename: str = "tabla.xlsx") -> None:
    save_original_tableau_excel(
        matriz_tableau=tableau.data,
        variables_basicas=[int(v) for v in tableau.basic_vars.tolist()],
        cantidad_variables_originales=tableau.num_original_vars,
        cantidad_variables_holgura=tableau.num_slack,
        cantidad_variables_exceso=tableau.num_surplus,
        cantidad_variables_artificiales=tableau.num_artificial,
        nombre_archivo=filename,
    )

def save_iteration(
    tableau,
    iteration: int,
) -> None:

    save_iteration_tableau_excel(
        matriz_tableau=tableau.data,
        variables_basicas=[int(v) for v in tableau.basic_vars.tolist()],
        cantidad_variables_originales=tableau.num_original_vars,
        cantidad_variables_holgura=tableau.num_slack,
        cantidad_variables_exceso=tableau.num_surplus,
        cantidad_variables_artificiales=tableau.num_artificial,
        fase=0,  # simplex puro (sin fase)
        iteracion=iteration,
    )