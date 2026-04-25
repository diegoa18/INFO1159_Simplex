from __future__ import annotations

import numpy as np
from simplex import (
    ConstraintType,
    InfeasibleError,
    LinearProgram,
    ObjectiveType,
    UnboundedError,
    solve,
)


def main() -> None:
    # MATRIZ A
    A = np.array(
        [
            [1, 0],
            [0, 2],
            [3, 2],
        ],
        dtype=np.float64,
    )

    # LADO DERECHO B (MISMO NUMERO DE FILAS QUE A)
    b = np.array(
        [
            4,
            12,
            18,
        ],
        dtype=np.float64,
    )

    # Z
    c = np.array(
        [
            30000,
            50000,
        ],
        dtype=np.float64,
    )

    # TIPO DE RESTRICCIONES
    constraints = np.array(
        [
            ConstraintType.LE,
            ConstraintType.LE,
            ConstraintType.LE,
        ]
    )

    # TIPO OBJETIVO
    objective = ObjectiveType.MAX

    # DEFINICION
    problem = LinearProgram(
        A=A,
        b=b,
        c=c,
        constraints=constraints,
        objective=objective,
    )

    # RESOLUCION
    try:
        solution = solve(problem, trace=True)
        print("SOLUCION OPTIMA")
        print("-" * 60)

        print(f"valor optimo: {solution.optimal_value:.6f}")

        for i, val in enumerate(solution.variables, start=1):
            print(f"x{i} = {val:.6f}")

        print(f"iteraciones: {solution.iterations}")

    except UnboundedError as e:
        print("cueck")
        print(e)

    except InfeasibleError as e:
        print("es infactible")
        print(e)


if __name__ == "__main__":
    main()
