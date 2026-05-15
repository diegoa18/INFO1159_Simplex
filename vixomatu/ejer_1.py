import numpy as np
import sympy as sp

x1, x2 = sp.symbols("x1 x2")
theta = sp.symbols("theta")

print("ejemplo: 1.20*x1 + 1.16*x2 - theta*(2*(x1**2) + x2**2 + (x1 + x2)**2)")
func_str = input("ingresa la función objetivo usando x1, x2 y theta: ")
theta_value = float(input("ingresa el valor de theta: "))

f_expr = sp.sympify(func_str, locals={"x1": x1, "x2": x2, "theta": theta})
f_expr_eval = f_expr.subs(theta, theta_value)

funcion_evaluable = sp.lambdify((x1, x2), f_expr_eval, "numpy")


def fc(x, y, var):
    f = funcion_evaluable(x, y)
    return f


Δx = np.arange(0, 5001, 1)

postulantes = []

for x in Δx:
    for y in Δx:
        if x + y <= 5000:
            f_value = fc(x, y, theta_value)
            postulantes.append((f_value, x, y))

resultados_f = [tupla[0] for tupla in postulantes]
indice_optimo = np.argmax(resultados_f)

f_max, x1_opt, x2_opt = postulantes[indice_optimo]

print(f"\nValor máximo de la función f(x*) = {f_max:.4f}")
print(f"En los puntos óptimos: x1* = {x1_opt:.4f}, x2* = {x2_opt:.4f}")
