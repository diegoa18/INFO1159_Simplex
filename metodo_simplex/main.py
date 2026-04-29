from __future__ import annotations

import sys
sys.path.insert(0, "..")

import numpy as np
from parser import pedir_problema
from simplex import InfeasibleError, UnboundedError
from simplex.simplex_solver import SimplexSolver
from simplex.problem import LinearProgram
from simplex.types import ConstraintType, ObjectiveType

# convierte formato neutro a LinearProgram (simplex)
def _convertir(tipo: str, fo: list[float], restricciones) -> LinearProgram:
    
    A = np.array([r[0] for r in restricciones], dtype=np.float64) # array de coeficientes de reestricciones
    b = np.array([r[1] for r in restricciones], dtype=np.float64) # array de LD de reestricciones
    c = np.array(fo, dtype=np.float64) # array de ceoficientes de la FO

    # convierte strings en numeraciones
    tipo_map = {
        "<=": ConstraintType.LE, # menor o igual que
        ">=": ConstraintType.GE, # mayor o igual que
        "=": ConstraintType.EQ, # igual a 
    }
    # convertimos los tipos de restricciones a un array de ConstraintType
    constraints_arr = np.array(
        [tipo_map[r[2]] for r in restricciones], dtype=np.int_
    )
    # convertimos el tipo de objetivo a ObjectiveType con su tipo de optimización
    obj = ObjectiveType.MAX if tipo == "max" else ObjectiveType.MIN

    # devuelve el problema en objeto para su uso 
    return LinearProgram(A=A, b=b, c=c, constraints=constraints_arr, objective=obj)


# pedimos problema y convertimos a formato simplex, luego resolvemos e imprimimos resultados
def main() -> None:
    # pedimos problema  
    tipo, fo, restricciones = pedir_problema()

    # instanciamos el problema en formato simplex
    lp = _convertir(tipo, fo, restricciones)
    # activa simplex solver 
    solver = SimplexSolver(trazo=True)

    try:
        #resuelve el problema 
        solution = solver.solve(lp)
        # imprime resultados
        print("SOLUCION OPTIMA")
        print("-" * 60)

        print(f"valor optimo: {solution.optimal_value:.6f}")

        for i, val in enumerate(solution.variables, start=1):
            print(f"x{i} = {val:.6f}")

        print(f"iteraciones: {solution.iterations}")

    except UnboundedError as e:
        print("Problema no acotado")
        print(e)

    except InfeasibleError as e:
        print("Problema infactible")
        print(e)


if __name__ == "__main__":
    main()