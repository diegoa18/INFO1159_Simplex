from __future__ import annotations

import numpy as np
from sympy import Eq, linear_eq_to_matrix, symbols, sympify

from .problem import LinearProgram
from .types import ConstraintType, ObjectiveType


def _ask_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Ingrese un entero positivo.")


def parse_float_value(text: str) -> float:
    try:
        value = sympify(text.strip())
    except Exception as error:
        raise ValueError(f"'{text}' no es un numero valido") from error

    if not bool(getattr(value, "is_real", False)):
        raise ValueError(f"'{text}' no es un numero real")

    as_float = float(value)
    if not np.isfinite(as_float):
        raise ValueError(f"'{text}' no es un numero finito")

    return as_float


def _parse_objective_type(raw: str) -> ObjectiveType:
    value = raw.strip().lower()
    if value == "min":
        return ObjectiveType.MIN
    return ObjectiveType.MAX


def _parse_objective_coefficients(raw: str, n: int) -> np.ndarray:
    tokens = raw.split()
    if len(tokens) != n:
        raise ValueError(
            f"Se esperaban {n} coeficientes para la funcion objetivo y llegaron {len(tokens)}."
        )
    return np.array([parse_float_value(token) for token in tokens], dtype=np.float64)


def _parse_constraint_line(raw: str, n: int, variables_sympy):
    tokens = raw.split()
    relation_map = {
        "<=": ConstraintType.LE,
        ">=": ConstraintType.GE,
        "=": ConstraintType.EQ,
    }

    relation_idx = -1
    relation_symbol = None

    for symbol in ("<=", ">=", "="):
        if symbol in tokens:
            idx = tokens.index(symbol)
            if relation_symbol is not None:
                raise ValueError("La restriccion tiene mas de un signo de relacion.")
            relation_symbol = symbol
            relation_idx = idx

    if relation_symbol is None:
        raise ValueError("La restriccion debe incluir <=, >= o =")

    if relation_idx != n or len(tokens) != n + 2:
        raise ValueError(
            f"Formato invalido. Use: a1 a2 ... a{n} {relation_symbol} b"
        )

    coeficientes_raw = [parse_float_value(token) for token in tokens[:n]]
    lado_derecho = parse_float_value(tokens[-1])

    lhs_expr = sum(coeficientes_raw[i] * variables_sympy[i] for i in range(n))
    matrix, rhs = linear_eq_to_matrix([Eq(lhs_expr, lado_derecho)], variables_sympy)

    coeffs = np.array([float(v) for v in matrix.tolist()[0]], dtype=np.float64)
    rhs_value = float(rhs[0])
    return coeffs, rhs_value, relation_map[relation_symbol]


def _build_objective_vector(coeficientes_raw: np.ndarray, variables_sympy) -> np.ndarray:
    expr = sum(coeficientes_raw[i] * variables_sympy[i] for i in range(len(coeficientes_raw)))
    matrix, _ = linear_eq_to_matrix([Eq(expr, 0)], variables_sympy)
    return np.array([float(v) for v in matrix.tolist()[0]], dtype=np.float64)


def build_problem_from_input() -> LinearProgram:
    print("--- INPUT SIMPLEX ---")

    cantidad_variables = _ask_positive_int("Cantidad de variables de decision: ")
    variables_sympy = symbols(f"x1:{cantidad_variables + 1}", real=True)

    while True:
        try:
            texto_objetivo = input(
                f"Coeficientes FO ({cantidad_variables} valores, ej: 6 5 4): "
            ).strip()
            coeficientes_fo = _parse_objective_coefficients(
                texto_objetivo, cantidad_variables
            )
            c = _build_objective_vector(coeficientes_fo, variables_sympy)
            break
        except ValueError as error:
            print(error)

    objetivo = _parse_objective_type(input("Objetivo (max/min) [max]: ") or "max")

    cantidad_restricciones = _ask_positive_int("Cantidad de restricciones: ")
    filas_A = []
    valores_b = []
    tipos_restriccion = []

    for i in range(cantidad_restricciones):
        while True:
            try:
                texto_restriccion = input(
                    f"Restriccion {i + 1} (formato: a1 a2 ... a{cantidad_variables} <= b): "
                ).strip()
                fila, lado_derecho, tipo = _parse_constraint_line(
                    texto_restriccion, cantidad_variables, variables_sympy
                )
                filas_A.append(fila)
                valores_b.append(lado_derecho)
                tipos_restriccion.append(tipo)
                break
            except ValueError as error:
                print(error)

    A = np.array(filas_A, dtype=np.float64)
    b = np.array(valores_b, dtype=np.float64)
    constraints = np.array(tipos_restriccion, dtype=np.int_)

    return LinearProgram(
        A=A,
        b=b,
        c=c,
        constraints=constraints,
        objective=objetivo,
    )
