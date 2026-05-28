from math import cos, pi, sin

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from sympy.core.sympify import converter

x = sp.symbols("x")

Δλ = np.arange(0.01, 1, 0.01)

funcion_str = input("ingrese la funcion: ")
funcion = sp.sympify(funcion_str)

f_num = sp.lambdify(x, funcion)

puntos_str = input("Ingrese los puntos xa y xb: ")
xa_val, xb_val = sp.sympify(puntos_str)


def convex_o_conca(funcion, var, xa, xb):
    f_xa = funcion.subs(var, xa)
    f_xb = funcion.subs(var, xb)
    for λ in Δλ:
        evaluado = λ * xa + (1 - λ) * xb

        lado_izq = funcion.subs(var, evaluado)
        lado_der = λ * f_xa + (1 - λ) * f_xb

        # Comparamos
        if lado_izq > lado_der:
            return "es cóncava"

        elif lado_izq < lado_der:
            return "es convexa"

    return "No es ni convexa ni cóncava"


resultado = convex_o_conca(funcion, x, xa_val, xb_val)
print(f"resultado: {resultado}")

xa_f = float(xa_val)
xb_f = float(xb_val)
ya_f = f_num(xa_f)
yb_f = f_num(xb_f)

margen = (xb_f - xa_f) * 0.5
x_vals = np.linspace(xa_f - margen, xb_f + margen, 100)

fig, ax = plt.subplots()
ax.plot(x_vals, f_num(x_vals), label="f(x)", color="red")

ax.plot([xa_f, xb_f], [ya_f, yb_f], color="blue", label="Interpolación")
ax.plot([xa_f, xb_f], [ya_f, yb_f], "ro")

ax.set_xlabel("x")
ax.set_ylabel("f(x)")
ax.set_title("Gráfico de la función")
ax.axhline(0, color="black", linewidth=0.5)
ax.axvline(0, color="black", linewidth=0.5)
ax.legend()

plt.show()
