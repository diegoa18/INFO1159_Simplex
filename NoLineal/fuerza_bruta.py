import numpy as np
import sympy as sp
from sympy import pretty

theta = float(input("ingrese theta (coeficiente de aversión al riesgo): "))
step = float(input("ingrese el intervalo (step): "))

x, y = sp.symbols("x y")
obj_expression = 1.2 * x + 1.16 * y - theta * (2 * x**2 + y**2 + (x + y) ** 2)
obj = sp.lambdify((x, y), obj_expression, "numpy")

range = np.arange(0, 5000 + step, step)
X, Y = np.meshgrid(range, range, indexing="ij")
mask = (X >= 0) & (Y >= 0) & ((X + Y) <= 5000)
X_valid = X[mask]
Y_valid = Y[mask]

if X_valid.size == 0:
    print("\nno se encontraron soluciones factibles")
    exit()

factible_vals = obj(X_valid, Y_valid)
opt_index = np.argmax(factible_vals)
x_opt = X_valid[opt_index]
y_opt = Y_valid[opt_index]
f_opt = factible_vals[opt_index]


print("FUNCION OBJETIVO:")
print(pretty(obj_expression, use_unicode=True))

print("PARAMETROS PRESENTES:")
print(f"theta (aversion al riesgo): {theta:.2e}")
print(f"intervalo: {step}")

print("RESULTADO OPTIMO")
print(f"x optimo = {x_opt:.2f}")
print(f"y optimo = {y_opt:.2f}")
print(f"\nvalor maximo encontrado = {f_opt:,.2f}")
print(f"\nsoluciones factibles evaluadas = {X_valid.size:,}")
