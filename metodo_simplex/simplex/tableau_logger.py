from .tableado.xlsx_tableau_repo import (
    save_original_tableau_excel,
    save_iteration_tableau_excel,
    _ruta_excel,
    _ruta_carpeta_historial_xlsx,
)
from .tableado.tableau import Tableau
import os
import shutil
from pathlib import Path


def clean_xlsx_files() -> None:
    # eliminar todos los archivos .xlsx en la carpeta tableado
    ruta_tableado = _ruta_excel().parent
    for archivo in ruta_tableado.glob("*.xlsx"):
        archivo.unlink()
    
    # eliminar todos los archivos .xlsx en la carpeta historial_xlsx
    ruta_historial = _ruta_carpeta_historial_xlsx()
    if ruta_historial.exists():
        for archivo in ruta_historial.glob("*.xlsx"):
            archivo.unlink()


def save_initial_tableau(tableau: Tableau, filename: str = "tabla_inicial.xlsx") -> None:
    save_original_tableau_excel(
        matriz_tableau=tableau.data,
        variables_basicas=[int(v) for v in tableau.basic_vars.tolist()],
        cantidad_variables_originales=tableau.num_original_vars,
        cantidad_variables_holgura=tableau.num_slack,
        cantidad_variables_exceso=tableau.num_surplus,
        cantidad_variables_artificiales=tableau.num_artificial,
        nombre_archivo=filename,
    )

def save_final_tableau(tableau: Tableau, filename: str = "tabla_final.xlsx") -> None:
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