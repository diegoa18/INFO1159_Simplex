from __future__ import annotations

import numpy as np
from typing import Optional

from .exceptions import StabilityError, UnboundedError
from .pivot import pivot
from .problem import LinearProgram, Solution
from .tableau import Tableau , print_tableau
from .types import ObjectiveType, EPSILON, MAX_ITERATIONS

# clase que maneja todo el algoritmo simplex 
class SimplexSolver:
    def __init__(self, trazo: bool = False):
        self.trazo = trazo # el que imprime cada iteracion del simplex

    def solve(self, problem: LinearProgram):
        tableau = Tableau.desde_programa_lineal(problem) #construye el tableau a partir del problema lineal

        es_min = problem.objective == ObjectiveType.MIN # verifica si es problema de minimizacion
        
        if len(tableau.rango_artificiales) > 0: #si tiene vars artificiales ejecuta dos fases
            return self.two_phases(tableau, problem, es_min)
        
        return self.standar(tableau, problem, es_min) # sino tiene vars artificiales, simplex normal
    # simplex estandar
    def standar(self, tableau, problem, es_min):
        if es_min: #si es minimizacion convierte la fo en maximizacion multiplicando por -1
            tableau.datos[tableau.fila_objetivo, :tableau.num_variables_originales] = problem.c
        # indice de la fila objetivo
        fila_z = tableau.fila_objetivo
        # recorre cada restriccion
        for i in range(tableau.num_restricciones):
            var_base = int(tableau.variables_basicas[i]) # variable basica de i fila
            coef_z = tableau.datos[fila_z, var_base] # coef de Z
            if abs(coef_z) > EPSILON: # evita q errores de decimales alteren el simplex
                tableau.datos[fila_z, :] -= coef_z * tableau.datos[i, :] # se pitea las variables basicas

        if self.trazo: # imprime la tabla inicial
            print("\n--- TABLA INICIAL SIMPLEX ---")
            print_tableau(tableau)
        # empieza a ejetutar el simplex iterando, hasta llegar a una sol optima
        tableau, iterations = simplex_iterate(tableau, trazo=self.trazo)
        # recoge valor optimo y variables de la tabla final
        valor_optimo, variables = extract(tableau)

        if es_min: # si el problema es de minimizacion se vuelve a multiplicar por -1 para q el valor concuerde
            valor_optimo = -valor_optimo

        return Solution(valor_optimo, variables, True, iterations)

    # ejecuta el método simplex con dos fases
    def two_phases(self, tableau, problem, es_min):
        fila_z = tableau.fila_objetivo # fila de la FO

        tableau.datos[fila_z, :] = 0 # reinicia la FO a 0
        for j in tableau.rango_artificiales: # construye una nueva FO para fase 1
            tableau.datos[fila_z, j] = 1.0

        print("\n--- Tableado inicial ---")
        print_tableau(tableau) 
        for i in range(tableau.num_restricciones): # recorre cada restriccion
            var_base = int(tableau.variables_basicas[i]) # variable basica de i fila
            if var_base in tableau.rango_artificiales: # compara si al var basica es artificial
                tableau.datos[fila_z, :] -= tableau.datos[i, :] # si es artificial, ajusta y se la pitea jijija

        if self.trazo:
            print("\n--- TABLA INICIAL FASE 1 ---")
            print_tableau(tableau)

        # comienza la ejecucion de la fase 1, iterando la nueva tabla hasta llegar a una sol optima
        tableau, iter1 = simplex_iterate(tableau, trazo=self.trazo) 
        # verifica si es != 0 y determina si el problema es infactible o no estable
        if abs(tableau.obtener_valor()) > EPSILON:
            raise StabilityError(f"Infactible: Z={tableau.obtener_valor():.4f}")

        # termina fase 1 y elimina col de vars artificiales
        tableau = tableau.eliminar_columnas_artificiales()
        tableau.restaurar_objetivo(problem.c, es_min) # restaura la FO original para fase 2

        new_fila_z = tableau.fila_objetivo # indicre de la nueva fila FO , despues de las vars artificiales
        for i in range(tableau.num_restricciones): # recorre cada restriccion
            var_idx = int(tableau.variables_basicas[i]) # variable basica de i fila
            coef_z = tableau.datos[new_fila_z, var_idx] # coef de Z en la nueva fila
            if abs(coef_z) > EPSILON: # evita q errores de decimales alteren el simplex
                tableau.datos[new_fila_z, :] -= coef_z * tableau.datos[i, :] # se pitea las variables basicas

        if self.trazo:
            print("\n--- TABLA INICIAL FASE 2 ---")
            print_tableau(tableau)
        # empieza la fase 2 y resuelve esta
        tableau, iter2 = simplex_iterate(tableau, trazo=self.trazo) 
        # recoge valor optimo y variables de la tabla final
        valor_optimo, variables = extract(tableau)
        # si el problema es de minimizacion se multiplica por -1 como toda la vida
        if es_min:
            valor_optimo = -valor_optimo
        # retorna la solucion con el valor optimo, variables, factibilidad y la suma de iteraciones de ambas fases
        return Solution(valor_optimo, variables, True, iter1 + iter2)


# ve la fila de la función objetivo para encontrar la variable que entra
def quien_entra(tableau: Tableau, epsilon: float = EPSILON) -> Optional[int]:
    fila_z = tableau.datos[tableau.fila_objetivo, :-1] # pesca la fila Z menos LD 

    fila_z = np.where(abs(fila_z) < epsilon, 0.0, fila_z) # evita q errores de decimales alteren el simplex
    candidatos = np.where(fila_z < -epsilon)[0]  # candidatos a mejorar la F0
    if len(candidatos) == 0: # si no hay candidatos se llego al punto optimo
        return None
    return int(min(candidatos)) # retorna el indice del candidato con menos valor


# ve la fila de la tabla para encontrar la variable que sale
def quien_sale(
    tableau: Tableau, col_pivote: int, epsilon: float = EPSILON
) -> Optional[int]:

    LD = tableau.datos[:-1, -1] # pesca el lado derecho de las restricciones (sin la fila de la FO)
    col = tableau.datos[:-1, col_pivote] # pesca la columna pivote (sin la fila de la FO)

    min_ratio = np.inf # busca el menor ratio valido para ver que fila sale
    fila_saliente = None

    for i in range(len(LD)): # recorre cada fila de la tabla (sin la fila de la FO)
        if col[i] > epsilon and LD[i] >= -epsilon: # solo considera filas con coef >0 y LD >= 0
            ratio = LD[i] / col[i] # calcula ratio para la fila i 

            if ratio < min_ratio - epsilon or (
                abs(ratio - min_ratio) < epsilon
                and (fila_saliente is None or i < fila_saliente)
            ): # escoge el menor valor y actualiza el candidato
                min_ratio = ratio
                fila_saliente = i

    return fila_saliente


# identifica pivote, printea la tabla y llama a pivor para actualizar el tableau
def simplex_iterate(
    tableau: Tableau,
    epsilon: float = EPSILON,
    trazo: bool = False,
) -> tuple[Tableau, int]:

    iteration = 0
    vb_vistas = set()

    while True:
        if iteration >= MAX_ITERATIONS: 
            raise StabilityError("Número máximo de iteraciones alcanzado")
    
        vb_actual = tuple(tableau.variables_basicas) # convierte las vb a tupla
        if vb_actual in vb_vistas: # revisa si aparecio antes
            raise StabilityError("Ciclaje detectado")
        vb_vistas.add(vb_actual)# guarda la vb como visitada

        col = quien_entra(tableau, epsilon)

        # si no hay variable, se llego al punto optimo
        if col is None:
            if trazo:
                print("Punto optimo alcanzado")
            return tableau, iteration

        fila = quien_sale(tableau, col, epsilon)
        # si no hay fila, el problema no esta acotado
        if fila is None:
            raise UnboundedError(f"No acotado: columna pivote {col} sin fila válida")

        # guarda el indice de la variable que sale para imprimirla en el trazo
        saliente = int(tableau.variables_basicas[fila])
        
        # pivotea la tabla 
        tableau = pivot(tableau, fila, col, epsilon)

        # imprime la tabla despues del pivoteo
        if trazo:
            print_tableau(
                tableau,
                iteracion=iteration + 1,
                fila_pivote=fila,
                columna_pivote=col,
                variable_saliente=saliente,
            )

        iteration += 1


# una vez que quien entra es None, extrae las soluciones básicas y devuelve el valor óptimo
def extract(tableau: Tableau):
    n = tableau.num_variables_originales # num de variables originales, descarta h, a , e
    x = np.zeros(n) #crea vector de ceros

    # recorre cada restriccion 
    for i in range(tableau.num_restricciones):
        var = int(tableau.variables_basicas[i]) # variable basica de i fila
        # si la variable basica es una de las originales, asigna su valor en el vector x
        if var < n:
            x[var] = tableau.datos[i, tableau.columna_lado_derecho]

    return tableau.obtener_valor(), tuple(x) # retorna el valor optimo y var en tupla
