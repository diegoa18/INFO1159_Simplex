from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _ruta_excel(nombre_archivo: str = "tabla.xlsx") -> Path:
    # archivo unico donde se va guardando el estado de la tabla
    return Path(__file__).resolve().parent / nombre_archivo


def _ruta_carpeta_historial_xlsx() -> Path:
    # carpeta donde se guardan los excel de cada iteracion
    return Path(__file__).resolve().parent / "historial_xlsx"


def _nombre_variable(
    indice_columna: int,
    cantidad_variables_originales: int,
    cantidad_variables_holgura: int,
    cantidad_variables_exceso: int,
) -> str:
    if indice_columna < cantidad_variables_originales:
        return f"x{indice_columna + 1}"
    if indice_columna < cantidad_variables_originales + cantidad_variables_holgura:
        return f"s{indice_columna - cantidad_variables_originales + 1}"
    if indice_columna < (
        cantidad_variables_originales
        + cantidad_variables_holgura
        + cantidad_variables_exceso
    ):
        return f"e{indice_columna - cantidad_variables_originales - cantidad_variables_holgura + 1}"
    return f"a{indice_columna - cantidad_variables_originales - cantidad_variables_holgura - cantidad_variables_exceso + 1}"


# esta funcion guarda la tabla inicial del simplex en excel, creando encabezados
# y poniendo primero la fila objetivo z y despues las filas de restricciones.
def save_original_tableau_excel(
    matriz_tableau: np.ndarray,
    variables_basicas: list[int],
    cantidad_variables_originales: int,
    cantidad_variables_holgura: int,
    cantidad_variables_exceso: int,
    cantidad_variables_artificiales: int,
    nombre_archivo: str = "tabla.xlsx",
) -> Path:
    # guardar la tabla original con encabezados y fila objetivo marcada
    ruta_excel = _ruta_excel(nombre_archivo)
    tabla_formateada = _crear_dataframe_tableau(
        matriz_tableau=matriz_tableau,
        variables_basicas=variables_basicas,
        cantidad_variables_originales=cantidad_variables_originales,
        cantidad_variables_holgura=cantidad_variables_holgura,
        cantidad_variables_exceso=cantidad_variables_exceso,
        cantidad_variables_artificiales=cantidad_variables_artificiales,
    )
    tabla_formateada.to_excel(
        ruta_excel,
        index=False,
    )
    return ruta_excel


def _crear_dataframe_tableau(
    matriz_tableau: np.ndarray,
    variables_basicas: list[int],
    cantidad_variables_originales: int,
    cantidad_variables_holgura: int,
    cantidad_variables_exceso: int,
    cantidad_variables_artificiales: int,
) -> pd.DataFrame:
    total_variables = (
        cantidad_variables_originales
        + cantidad_variables_holgura
        + cantidad_variables_exceso
        + cantidad_variables_artificiales
    )

    nombres_columnas_variables = [
        _nombre_variable(
            i,
            cantidad_variables_originales,
            cantidad_variables_holgura,
            cantidad_variables_exceso,
        )
        for i in range(total_variables)
    ]
    nombres_columnas_excel = ["VB", "Z", *nombres_columnas_variables, "LD"]

    indice_fila_objetivo = matriz_tableau.shape[0] - 1
    # aqui se agrega la fila z primero en los datos, por eso queda como segunda fila del excel
    # (la primera fila del excel es el dato de columnas, x1, x1 , a1, etc)
    filas_tabla = [
        [
            "Z",
            -1.0,
            *matriz_tableau[indice_fila_objetivo, :total_variables].tolist(),
            float(matriz_tableau[indice_fila_objetivo, -1]),
        ]
    ]

    # este for recorre cada variable basica y agrega su fila de restriccion a la tabla
    for indice_fila_restriccion, indice_variable_basica in enumerate(variables_basicas):
        filas_tabla.append(
            [
                _nombre_variable(
                    int(indice_variable_basica),
                    cantidad_variables_originales,
                    cantidad_variables_holgura,
                    cantidad_variables_exceso,
                ),
                0.0,
                *matriz_tableau[indice_fila_restriccion, :total_variables].tolist(),
                float(matriz_tableau[indice_fila_restriccion, -1]),
            ]
        )

    return pd.DataFrame(filas_tabla, columns=nombres_columnas_excel)


def save_iteration_tableau_excel(
    matriz_tableau: np.ndarray,
    variables_basicas: list[int],
    cantidad_variables_originales: int,
    cantidad_variables_holgura: int,
    cantidad_variables_exceso: int,
    cantidad_variables_artificiales: int,
    fase: int,
    iteracion: int,
) -> Path:
    # guarda una copia del tableau al final de cada iteracion en historial_xlsx
    carpeta_historial = _ruta_carpeta_historial_xlsx()
    carpeta_historial.mkdir(parents=True, exist_ok=True)

    nombre_base = f"tabla_F{fase}_{iteracion}.xlsx"
    ruta_archivo = carpeta_historial / nombre_base

    tabla_formateada = _crear_dataframe_tableau(
        matriz_tableau=matriz_tableau,
        variables_basicas=variables_basicas,
        cantidad_variables_originales=cantidad_variables_originales,
        cantidad_variables_holgura=cantidad_variables_holgura,
        cantidad_variables_exceso=cantidad_variables_exceso,
        cantidad_variables_artificiales=cantidad_variables_artificiales,
    )
    tabla_formateada.to_excel(ruta_archivo, index=False)
    return ruta_archivo


def cargar_matriz_desde_excel(
    total_variables: int,
    cantidad_restricciones: int,
) -> np.ndarray:
    # esta funcion lee la tabla desde excel y devuelve solo la matriz numerica
    ruta_excel = _ruta_excel()
    if not ruta_excel.exists():
        raise FileNotFoundError(f"no existe el archivo: {ruta_excel}")

    tabla_excel = pd.read_excel(ruta_excel)
    if tabla_excel.empty:
        raise ValueError("el archivo excel existe pero esta vacio")

    if tabla_excel.shape[0] < cantidad_restricciones + 1:
        raise ValueError(
            "el excel no tiene suficientes filas para reconstruir la matriz"
        )

    matriz = np.zeros(
        (cantidad_restricciones + 1, total_variables + 1), dtype=np.float64
    )

    # fila 0 de datos en excel corresponde a la fila objetivo Z
    matriz[cantidad_restricciones, :total_variables] = tabla_excel.iloc[
        0, 2 : 2 + total_variables
    ].to_numpy(dtype=np.float64)
    matriz[cantidad_restricciones, -1] = float(tabla_excel.iloc[0, -1])

    # desde la fila 1 en excel vienen las restricciones
    for indice_fila in range(cantidad_restricciones):
        fila_excel = tabla_excel.iloc[indice_fila + 1]
        matriz[indice_fila, :total_variables] = fila_excel.iloc[
            2 : 2 + total_variables
        ].to_numpy(dtype=np.float64)
        matriz[indice_fila, -1] = float(fila_excel.iloc[-1])

    return matriz
