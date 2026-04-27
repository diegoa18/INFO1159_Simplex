from .tableado.xlsx_tableau_repo import (
    _ruta_carpeta_historial_xlsx,
    _ruta_excel,
    save_original_tableau_excel,
    save_iteration_tableau_excel,
)
from .tableado.tableau import Tableau


def _basic_variables(tableau: Tableau) -> list[int]:
    return [int(v) for v in tableau.basic_vars.tolist()]


def _clean_xlsx_files() -> None:
    ruta_tableado = _ruta_excel().parent
    for archivo in ruta_tableado.glob("*.xlsx"):
        archivo.unlink()

    ruta_historial = _ruta_carpeta_historial_xlsx()
    if ruta_historial.exists():
        for archivo in ruta_historial.glob("*.xlsx"):
            archivo.unlink()


def _save_tableau_snapshot(tableau: Tableau, filename: str) -> None:
    save_original_tableau_excel(
        matriz_tableau=tableau.data,
        variables_basicas=_basic_variables(tableau),
        cantidad_variables_originales=tableau.num_original_vars,
        cantidad_variables_holgura=tableau.num_slack,
        cantidad_variables_exceso=tableau.num_surplus,
        cantidad_variables_artificiales=tableau.num_artificial,
        nombre_archivo=filename,
    )


def save_initial_tableau(tableau: Tableau, filename: str = "tabla_inicial.xlsx") -> None:
    _clean_xlsx_files()
    _save_tableau_snapshot(tableau, filename)

def save_final_tableau(tableau: Tableau, filename: str = "tabla_final.xlsx") -> None:
    _save_tableau_snapshot(tableau, filename)

def save_iteration(
    tableau,
    iteration: int,
) -> None:

    save_iteration_tableau_excel(
        matriz_tableau=tableau.data,
        variables_basicas=_basic_variables(tableau),
        cantidad_variables_originales=tableau.num_original_vars,
        cantidad_variables_holgura=tableau.num_slack,
        cantidad_variables_exceso=tableau.num_surplus,
        cantidad_variables_artificiales=tableau.num_artificial,
        fase=0,  # simplex puro (sin fase)
        iteracion=iteration,
    )