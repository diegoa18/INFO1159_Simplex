from parser import (
    pedir_funcion_objetivo,
    pedir_num_restricciones,
    pedir_restricciones,
    pedir_tipo,
)
from programacion_lineal import graficar, resolver_PL


def main():
    print("=== Solver de Programación Lineal ===\n")

    tipo = pedir_tipo()
    a, b = pedir_funcion_objetivo()
    n = pedir_num_restricciones()
    restricciones = pedir_restricciones(n)

    # ejes por defecto
    restricciones += [
        (1, 0, 0, ">="),
        (0, 1, 0, ">="),
    ]

    solucion = resolver_PL(restricciones, a, b, tipo)

    print("\nEstado:", solucion["estado"])

    if solucion["optimo"]:
        (x, y), z = solucion["optimo"]
        print(f"Óptimo en ({x}, {y}) → Z = {z}")

    graficar(solucion, restricciones)


main()
