import numpy as np
import sympy as sp

# definimos tus variables simbólicas
x1, x2 = sp.symbols("x1 x2")
theta = sp.symbols("theta")

# pedimos los datos por terminal
print("ejemplo: 1.20*x1 + 1.16*x2 - theta*(2*(x1**2) + x2**2 + (x1 + x2)**2)")
func_str = input("ingresa la función objetivo usando x1, x2 y theta: ")
theta_value = float(input("ingresa el valor de theta: "))

# convertimos el texto a una expresión matemática de sympy
f_expr = sp.sympify(func_str)

# creamos una función evaluable con numpy (esto es necesario para que el ciclo for sea rápido)
funcion_evaluable = sp.lambdify((x1, x2, theta), f_expr, "numpy")

# mantenemos tu función original intacta en su lógica
def fc(x, y, var):
    # evalúa la función ingresada en vez de tenerla escrita en el código
    f = funcion_evaluable(x, y, var)
    return f

# definir el rango para x1 y x2
Δx = np.arange(0, 5, 1e-2)

postulantes = []

# búsqueda por fuerza bruta: evaluar en cada punto de la cuadrícula
for x in Δx:
    for y in Δx:
        if x + y <= 5:
            f_value = fc(x, y, theta_value)
            postulantes.append((f_value, x, y))

# se extraen los resultado y se encuentran los indices optimos
resultados_f = [tupla[0] for tupla in postulantes]
indice_optimo = np.argmax(resultados_f)

# se extraen los valores optimos
f_max, x1_opt, x2_opt = postulantes[indice_optimo]

print(f"Valor máximo de la función f(x*) = {f_max:.4f}")
print(f"En los puntos óptimos: x1* = {x1_opt:.4f}, x2* = {x2_opt:.4f}")
