from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from .types import ConstraintType, Matriz, ObjectiveType, EPSILON

if TYPE_CHECKING:
    from .problem import LinearProgram


@dataclass
class Tableau:
    datos: Matriz
    variables_basicas: np.ndarray
    variables_no_basicas: np.ndarray
    num_variables_originales: int
    num_restricciones: int
    num_holguras: int
    num_excesos: int
    num_artificiales: int

    # metodo que crea un Tableau a partir de un programa lineal, inicializando 
    # el tableau con las restricciones y la funcion objetivo
    @classmethod
    def desde_programa_lineal(cls, problem: LinearProgram, epsilon: float = EPSILON) -> Tableau:
        matriz_coeficientes, vector_lado_derecho = problem.A.copy(), problem.b.copy()
        tipos_restricciones = problem.constraints.copy()

        for i in range(problem.m):
            if vector_lado_derecho[i] < 0:
                matriz_coeficientes[i] *= -1
                vector_lado_derecho[i] *= -1
                tipo_restriccion = int(tipos_restricciones[i])
                tipos_restricciones[i] = (
                    ConstraintType.GE if tipo_restriccion == ConstraintType.LE else ConstraintType.LE
                )

        num_variables, num_restricciones = problem.n, problem.m
        num_holguras = int(np.sum(tipos_restricciones == ConstraintType.LE))
        num_excesos = int(np.sum(tipos_restricciones == ConstraintType.GE))
        num_artificiales = int(
            np.sum(
                (tipos_restricciones == ConstraintType.GE) | (tipos_restricciones == ConstraintType.EQ)
            )
        )

        total_columnas = num_variables + num_holguras + num_excesos + num_artificiales + 1
        tabla_simplex = np.zeros((num_restricciones + 1, total_columnas), dtype=np.float64)

        columna_holgura = num_variables
        columna_exceso = num_variables + num_holguras
        columna_artificial = num_variables + num_holguras + num_excesos
        variables_basicas = []

        for i in range(num_restricciones):
            tabla_simplex[i, :num_variables] = matriz_coeficientes[i]
            tipo_restriccion = int(tipos_restricciones[i])

            if tipo_restriccion == ConstraintType.LE:
                tabla_simplex[i, columna_holgura] = 1.0
                variables_basicas.append(columna_holgura)
                columna_holgura += 1
            elif tipo_restriccion == ConstraintType.GE:
                tabla_simplex[i, columna_exceso] = -1.0
                tabla_simplex[i, columna_artificial] = 1.0
                variables_basicas.append(columna_artificial)
                columna_exceso += 1
                columna_artificial += 1
            else:
                tabla_simplex[i, columna_artificial] = 1.0
                variables_basicas.append(columna_artificial)
                columna_artificial += 1

            tabla_simplex[i, -1] = vector_lado_derecho[i]

        fila_objetivo = -problem.c
        if problem.objective == ObjectiveType.MIN:
            fila_objetivo = problem.c
        tabla_simplex[num_restricciones, :num_variables] = fila_objetivo

        return cls(
            datos=tabla_simplex,
            variables_basicas=np.array(variables_basicas, dtype=np.intp),
            variables_no_basicas=np.arange(num_variables, dtype=np.intp),
            num_variables_originales=num_variables,
            num_restricciones=num_restricciones,
            num_holguras=num_holguras,
            num_excesos=num_excesos,
            num_artificiales=num_artificiales,
        )

    #PROPIEDADESEDAWADA PERDONE PROFE
    @property # devuelve el índice de la columna del lado derecho (ultima columna)
    def columna_lado_derecho(self) -> int:  
        return self.datos.shape[1] - 1

    @property # devuelve el indice de la fila de la función objetivo (ultima fila)
    def fila_objetivo(self) -> int:  
        return self.datos.shape[0] - 1

    @property # devuelve el índice de inicio de las columnas de variables artificiales
    def inicio_artificiales(self) -> int:  
        return self.num_variables_originales + self.num_holguras + self.num_excesos

    @property # devuelve un rango con los indices de las columnas de variables artificiales
    def rango_artificiales(self) -> range:  
        return range(self.inicio_artificiales, self.inicio_artificiales + self.num_artificiales)

    @property # devuelve TRUE si hay variables artificiales en el tableau
    def tiene_artificiales(self) -> bool:  
        return self.num_artificiales > 0

    @property # devuelve un rango con los indices de las columnas de variables originales
    def rango_originales(self) -> range:  
        return range(self.num_variables_originales)

    @property # devuelve un rango con los indices de las columnas de variables de holgura
    def rango_holguras(self) -> range:  
        return range(self.num_variables_originales, self.num_variables_originales + self.num_holguras)

    @property # devuelve un rango con los indices de las columnas de variables de exceso
    def rango_excesos(self) -> range:  
        return range(
            self.num_variables_originales + self.num_holguras,
            self.num_variables_originales + self.num_holguras + self.num_excesos,
        )

    def nombre_variable(self, var_index: int) -> str:
        if var_index < self.num_variables_originales:
            return f"x{var_index + 1}"

        elif var_index < self.num_variables_originales + self.num_holguras:
            return f"h{var_index - self.num_variables_originales + 1}"

        elif var_index < self.inicio_artificiales:
            return f"e{var_index - self.num_variables_originales - self.num_holguras + 1}"

        else:
            return f"a{var_index - self.inicio_artificiales + 1}"

    def obtener_valor(self) -> float:
        return float(self.datos[self.fila_objetivo, self.columna_lado_derecho])

    def eliminar_columnas_artificiales(self) -> Tableau:
        if not self.tiene_artificiales:
            return self

        end = self.inicio_artificiales + self.num_artificiales
        new_data = np.delete(self.datos, range(self.inicio_artificiales, end), axis=1)

        new_basic = np.array(
            [v - self.num_artificiales if v >= end else v for v in self.variables_basicas],
            dtype=np.intp,
        )

        total = self.num_variables_originales + self.num_holguras + self.num_excesos
        new_nonbasic = np.array(
            sorted(set(range(total)) - set(new_basic)), dtype=np.intp
        )

        return Tableau(
            datos=new_data,
            variables_basicas=new_basic,
            variables_no_basicas=new_nonbasic,
            num_variables_originales=self.num_variables_originales,
            num_restricciones=self.num_restricciones,
            num_holguras=self.num_holguras,
            num_excesos=self.num_excesos,
            num_artificiales=0,
        )

    def restaurar_objetivo(self, c: np.ndarray, is_minimization: bool) -> None:
        self.datos[self.fila_objetivo, : self.num_variables_originales] = (
            c if is_minimization else -c
        )

    @property # devuelve el numero total de columnas en el tableau
    def columnas(self) -> int:  
        return self.datos.shape[1]

    @property # devuelve el numero total de filas en el tableau
    def filas(self) -> int:  
        return self.datos.shape[0]
