from __future__ import annotations

from pathlib import Path

import pandas as pd
import numpy as np


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
		return (
			f"e{indice_columna - cantidad_variables_originales - cantidad_variables_holgura + 1}"
		)
	return (
		f"a{indice_columna - cantidad_variables_originales - cantidad_variables_holgura - cantidad_variables_exceso + 1}"
	)


# esta funcion guarda la tabla inicial del simplex en excel, creando encabezados
# y poniendo primero la fila objetivo z y despues las filas de restricciones.
def save_original_tableau_excel(
	matriz_tableau: np.ndarray,
	variables_basicas: list[int],
	cantidad_variables_originales: int,
	cantidad_variables_holgura: int,
	cantidad_variables_exceso: int,
	cantidad_variables_artificiales: int,
) -> Path:
	# guardar la tabla original con encabezados y fila objetivo marcada
	ruta_excel = Path(__file__).resolve().parent / "tabla.xlsx"
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


	pd.DataFrame(filas_tabla, columns=nombres_columnas_excel).to_excel(
		ruta_excel,
		index=False,
	)
	return ruta_excel
