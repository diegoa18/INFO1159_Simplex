from mimetypes import common_types

import numpy as np
import sympy as sp

eps = np.finfo(float).eps

x = sp.symbols("x")

funcion_str = input("Ingrese la función: ")
punto = float(input("Ingrese el punto a evaluar: "))
error = float(input("Ingrese el valor de error (tolerancia): "))

if error < eps:
    print(f"el error debe ser mayor o igual al epsilon de la máquina ({eps})")
    exit()

funcion = sp.sympify(funcion_str)
f_num = sp.lambdify(x, funcion)


def calcular_derivada_explicita(funcion, var, punto_eva):
    df = sp.diff(funcion, var)
    dfx = sp.lambdify(var, df)
    return dfx(punto_eva)


def calcular_derivada_definicion(f_num, punto_eva, error):
    delta_x = (error ** (1 / 2)) * abs(punto_eva)
    if delta_x == 0:
        delta_x = error ** (1 / 2)
    derivada_def = (f_num(punto_eva + delta_x) - f_num(punto_eva)) / delta_x
    return derivada_def


def comparar_derivadas(derivada_explicita, derivada_definicion):
    derivada_explicita = calcular_derivada_explicita(funcion, x, punto)
    derivada_definicion = calcular_derivada_definicion(f_num, punto, error)

    print(f"derivada explícita : {derivada_explicita}")
    print(f"derivada por definición : {derivada_definicion}")

    if abs(derivada_explicita - derivada_definicion) < error:
        return True
    return False


print(comparar_derivadas(funcion, f_num))
