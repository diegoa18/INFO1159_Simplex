import sympy as sp


def gradiente_numerico():
    variables = tuple(sp.symbols(input("ingrese las variables (espacios): ")))
    func = sp.sympify(input("ingrese f(x): "))
    x_vals = list(map(float, input("ingrese el punto x (coma): ").split(",")))
    deltas = list(map(float, input("ingrese los Δx (coma): ").split(",")))

    if not (len(variables) == len(x_vals) == len(deltas)):
        print("cantidad incompatible de datos")
        return

    punto = {v: xv for v, xv in zip(variables, x_vals)}
    f_x = float(func.subs(punto))

    grad = []
    for var, d in zip(variables, deltas):
        punto_pert = punto.copy()
        punto_pert[var] += d
        grad.append((float(func.subs(punto_pert)) - f_x) / d)

    print(f"gradiente: {grad}")
