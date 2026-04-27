from __future__ import annotations

import numpy as np
from sympy import Eq, linear_eq_to_matrix, symbols, sympify

from .exceptions import (
    InputFormatError,
    InputParserError,
    InputValueError,
)
from .problem import LinearProgram
from .types import ConstraintType, ObjectiveType


def _ask_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if value <= 0:
                raise InputValueError.positive_int()
            return value
        except ValueError:
            print(InputValueError.positive_int())
        except InputParserError as error:
            print(error)


def _parse_real_finite_number(text: str) -> float:
    try:
        value = sympify(text.strip())
    except Exception as error:
        raise InputValueError.invalid_number(text) from error

    if not bool(getattr(value, "is_real", False)):
        raise InputValueError.non_real(text)

    as_float = float(value)
    if not np.isfinite(as_float):
        raise InputValueError.non_finite(text)

    return as_float


def _parse_objective_type(raw: str) -> ObjectiveType:
    value = raw.strip().lower()
    if value == "min":
        return ObjectiveType.MIN
    return ObjectiveType.MAX


def _parse_objective_coefficients(raw: str, n: int) -> np.ndarray:
    tokens = raw.split()
    if len(tokens) != n:
        raise InputFormatError.objective_coeff_count(n, len(tokens))
    return np.array([_parse_real_finite_number(token) for token in tokens], dtype=np.float64)


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
                raise InputFormatError.multiple_relations()
            relation_symbol = symbol
            relation_idx = idx

    if relation_symbol is None:
        raise InputFormatError.missing_relation()

    if relation_idx != n or len(tokens) != n + 2:
        raise InputFormatError.invalid_constraint_format(n, relation_symbol)

    coeficientes_raw = [_parse_real_finite_number(token) for token in tokens[:n]]
    lado_derecho = _parse_real_finite_number(tokens[-1])

    lhs_expr = sum(coeficientes_raw[i] * variables_sympy[i] for i in range(n))
    matrix, rigth = linear_eq_to_matrix([Eq(lhs_expr, lado_derecho)], variables_sympy)

    coeffs = np.array([float(v) for v in matrix.tolist()[0]], dtype=np.float64)
    rigth_value = float(rigth[0])
    return coeffs, rigth_value, relation_map[relation_symbol]


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
        except InputParserError as error:
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
            except InputParserError as error:
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
