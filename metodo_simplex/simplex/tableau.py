from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import numpy as np , math

from .types import (ConstraintType, Matriz, ObjectiveType, EPSILON,
    UMBRAL_NOTACION_CIENTIFICA_GRANDE, UMBRAL_NOTACION_CIENTIFICA_PEQUENA, TOLERANCIA_MANTISA,
    DECIMALES_NORMAL, ANCHO_COLUMNA_DEFAULT, ANCHO_COLUMNA_TABLAU,
)

if TYPE_CHECKING:
    from .problem import LinearProgram

# clase de datos que sirve de contenedor
# de toda la info del estado actual del tableau
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
    objective: ObjectiveType

    # metodo que crea un Tableau a partir de un programa lineal, inicializando 
    # el tableau con las restricciones y la funcion objetivo
    @classmethod
    def desde_programa_lineal(cls, problem: LinearProgram, epsilon: float = EPSILON) -> Tableau:
        matriz_coeficientes, vector_lado_derecho = problem.A.copy(), problem.b.copy() # copia los daos
        tipos_restricciones = problem.constraints.copy() # copiar los tipos de restricciones

        for i in range(problem.m): 
            if vector_lado_derecho[i] < 0: # ver si el lado derecho es negativo
                matriz_coeficientes[i] *= -1 # multiplica por -1
                vector_lado_derecho[i] *= -1 # multiplica por -1
                tipo_restriccion = int(tipos_restricciones[i]) # copia los indices
                tipos_restricciones[i] = ( # invierte el tipo de restriccion
                    ConstraintType.GE if tipo_restriccion == ConstraintType.LE else ConstraintType.LE
                )

        num_variables, num_restricciones = problem.n, problem.m # numero de variables y restricciones
        num_holguras = int(np.sum(tipos_restricciones == ConstraintType.LE)) # holgura
        num_excesos = int(np.sum(tipos_restricciones == ConstraintType.GE)) # # exceso
        num_artificiales = int( # contar el numero de variables artificiales necesarias
            np.sum(
                (tipos_restricciones == ConstraintType.GE) | (tipos_restricciones == ConstraintType.EQ)
            )
        )

        total_columnas = num_variables + num_holguras + num_excesos + num_artificiales + 1 # suma las columnas
        # crea la matriz con 0, filas = restriciones + Z(1), columnas = variables + LD 
        tabla_simplex = np.zeros((num_restricciones + 1, total_columnas), dtype=np.float64)

        # donde empieza cada tipo de variable en el tableau
        columna_holgura = num_variables 
        columna_exceso = num_variables + num_holguras
        columna_artificial = num_variables + num_holguras + num_excesos
        variables_basicas = [] # la vb inicial

        for i in range(num_restricciones): 
            tabla_simplex[i, :num_variables] = matriz_coeficientes[i] #copia los coeficientes
            tipo_restriccion = int(tipos_restricciones[i])

            # dependiendo de la restricciones, añade variables de h, a o e, y actualiza las VB
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

            tabla_simplex[i, -1] = vector_lado_derecho[i] # lado derecho

        # para max se pone -c, para min se pone c
        fila_objetivo = -problem.c
        if problem.objective == ObjectiveType.MIN: 
            fila_objetivo = problem.c
        tabla_simplex[num_restricciones, :num_variables] = fila_objetivo # se pone en la ultima fila

        return cls( # crea el objeto final
            datos=tabla_simplex,
            variables_basicas=np.array(variables_basicas, dtype=np.intp),
            variables_no_basicas=np.arange(num_variables, dtype=np.intp),
            num_variables_originales=num_variables,
            num_restricciones=num_restricciones,
            num_holguras=num_holguras,
            num_excesos=num_excesos,
            num_artificiales=num_artificiales,
            objective=problem.objective,
        )

    # property convierte metodos en atributos
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
        # si es una variable original la nombra con xn
        if var_index < self.num_variables_originales: 
            return f"x{var_index + 1}"
        # si es una variable de holgura la nombra con hn
        elif var_index < self.num_variables_originales + self.num_holguras:
            return f"h{var_index - self.num_variables_originales + 1}"
        # si es una variable de exceso la nombra con en
        elif var_index < self.inicio_artificiales:
            return f"e{var_index - self.num_variables_originales - self.num_holguras + 1}"
        # si es una variable artificial la nombra con an
        else:
            return f"a{var_index - self.inicio_artificiales + 1}"

    def obtener_valor(self) -> float:
        # devuelve el valor actual de Z
        return float(self.datos[self.fila_objetivo, self.columna_lado_derecho]) 

    def eliminar_columnas_artificiales(self) -> Tableau:
        if not self.tiene_artificiales:
            return self

        end = self.inicio_artificiales + self.num_artificiales # rango de columnas a eliminar
        new_data = np.delete(self.datos, range(self.inicio_artificiales, end), axis=1) # elimina las columnas

        new_basic = np.array( # ajusta las VB xq elimine las columnas de artificiales
            [v - self.num_artificiales if v >= end else v for v in self.variables_basicas],
            dtype=np.intp,
        )
        # reconstruimos las no basicas, todas las variables - aartificiales
        total = self.num_variables_originales + self.num_holguras + self.num_excesos
        new_nonbasic = np.array( # reconstruye las no basicas, todas las variables - aartificiales
            sorted(set(range(total)) - set(new_basic)), dtype=np.intp
        )
        #crea un nuevo tableau
        return Tableau(
            datos=new_data,
            variables_basicas=new_basic,
            variables_no_basicas=new_nonbasic,
            num_variables_originales=self.num_variables_originales,
            num_restricciones=self.num_restricciones,
            num_holguras=self.num_holguras,
            num_excesos=self.num_excesos,
            num_artificiales=0,
            objective=self.objective,
        )

    # reescribe la fila Z, con la fo original (fase=2)
    def restaurar_objetivo(self, c: np.ndarray, is_minimization: bool) -> None:
        self.datos[self.fila_objetivo, : self.num_variables_originales] = (
            c if is_minimization else -c
        )

    #PROPIEDADESEDAWADA PERDONE PROFE
    @property # devuelve el numero total de columnas en el tableau
    def columnas(self) -> int:  
        return self.datos.shape[1]

    @property # devuelve el numero total de filas en el tableau
    def filas(self) -> int:  
        return self.datos.shape[0]

def format_number_scientific(value: float) -> str:
    valor_absoluto = abs(value) 
    if valor_absoluto == 0: 
        return f"{0.0:.{DECIMALES_NORMAL}f}" # evita problemas con log(0) y muestra 0 con formato normal
    # notación de potencia 10^n para números muy grandes o muy pequeños
    if valor_absoluto >= UMBRAL_NOTACION_CIENTIFICA_GRANDE or valor_absoluto < UMBRAL_NOTACION_CIENTIFICA_PEQUENA:  
        exponente = math.floor(math.log10(valor_absoluto))
        mantisa = value / (10 ** exponente)

        # formato: mantisa×10^exp
        if abs(mantisa - round(mantisa)) < TOLERANCIA_MANTISA:
            # si la mantisa es casi un entero
            return f"{int(round(mantisa))}×10^{exponente}"
        # si tiene decimales
        return f"{mantisa:.1f}×10^{exponente}"

    # formato normal con 2 decimales
    return f"{value:.{DECIMALES_NORMAL}f}"

# convierte el numero a un string bonito y lo alinea con un ancho fijo
def format_number(valor: float, ancho: int = ANCHO_COLUMNA_DEFAULT) -> str:
    return f"{format_number_scientific(valor):>{ancho}}"


def print_tableau(
    tableau: Tableau, iteracion: Optional[int] = None,
    fila_pivote: Optional[int] = None, columna_pivote: Optional[int] = None,
    variable_saliente: Optional[int] = None, objective: Optional[ObjectiveType] = None,
) -> None:

    num_restricciones = tableau.num_restricciones 

    # encabezado de iteración (solo simplex)
    if iteracion is not None:
        print(f"Iteración {iteracion}\n")

    # orden de columnas
    columnas_ordenadas = (
        list(tableau.rango_originales)
        + list(tableau.rango_excesos)
        + list(tableau.rango_artificiales)
        + list(tableau.rango_holguras)
    )

    ancho_columna = ANCHO_COLUMNA_TABLAU
    mapa_nombres = {j: tableau.nombre_variable(j) for j in columnas_ordenadas} # crea un diccionario 

    encabezado = "VB".ljust(3) + "Z".center(ancho_columna) 

    for j in columnas_ordenadas: # añade el nombre de de las columnas
        encabezado += mapa_nombres[j].center(ancho_columna)

    encabezado += "LD".rjust(ancho_columna)
    print(encabezado)
    print("-" * len(encabezado))

    # fila Z
    fila_z = tableau.datos[tableau.fila_objetivo] # fila objetivo
    z_sign = float(tableau.objective) # max o min 
    cadena_fila = "Z ".ljust(3) + format_number(z_sign, ancho_columna).rjust(ancho_columna) 

    # añade los coeficientes de la fila Z
    for j in columnas_ordenadas:
        cadena_fila += format_number(fila_z[j], ancho_columna).rjust(ancho_columna)

    # agregar valor de
    cadena_fila += format_number(fila_z[-1], ancho_columna).rjust(ancho_columna)
    print(cadena_fila)
    
    # 
    for i in range(num_restricciones):
        variable_basica = int(tableau.variables_basicas[i]) # variable basica de la fila i
        # columna VB + columna Z para restricciones 
        cadena_fila = tableau.nombre_variable(variable_basica).ljust(3) + format_number(0.0, ancho_columna).rjust(ancho_columna)

        for j in columnas_ordenadas:
            valor = tableau.datos[i, j]
        
            cadena_fila += format_number(valor, ancho_columna).rjust(ancho_columna) # ultima columna LD

        cadena_fila += format_number(tableau.datos[i, -1], ancho_columna).rjust(ancho_columna) 
        print(cadena_fila)

    print("-" * len(encabezado)) # linea de separación

    # info pivote
    if fila_pivote is not None and columna_pivote is not None and variable_saliente is not None:
        print() # salto de linea
        # variable que entra y sale
        entrante = mapa_nombres.get(columna_pivote, tableau.nombre_variable(columna_pivote))
        print(f"entra {entrante}, sale {tableau.nombre_variable(variable_saliente)}")

    print()
