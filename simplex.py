import numpy as np

def simplex(A, B, C, maximizar=True):
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    C = np.array(C, dtype=float)
    m, n = A.shape  # m restricciones, n variables

    # Forma aumentada: agregar variables de holgura automáticamente
    tablero = np.zeros((m + 1, n + m + 2))
    tablero[0, 0] = 1
    tablero[0, 1:n+1] = -C if maximizar else C
    for i in range(m):
        tablero[i+1, 1:n+1] = A[i]
        tablero[i+1, n+1+i] = 1
        tablero[i+1, -1] = B[i]

    variables_basicas = list(range(n+1, n+m+1))
    nombres = ["Z"] + [f"x{i+1}" for i in range(n)] + [f"h{i+1}" for i in range(m)] + ["LD"]

    print("\nTabla inicial:")
    imprimir(tablero, variables_basicas, nombres)

    while any(tablero[0, 1:-1] < 0):
        col = int(np.argmin(tablero[0, 1:-1])) + 1

        cocientes = [(tablero[i, -1] / tablero[i, col], i)
                     for i in range(1, m+1) if tablero[i, col] > 0]
        if not cocientes:
            print("Problema ilimitado.")
            return
        fila = min(cocientes)[1]

        print(f"\nEntra: {nombres[col]}, Sale: {nombres[variables_basicas[fila-1]]}")
        tablero[fila] /= tablero[fila, col]
        for i in range(len(tablero)):
            if i != fila:
                tablero[i] -= tablero[i, col] * tablero[fila]
        tablero[np.abs(tablero) < 1e-10] = 0

        variables_basicas[fila-1] = col
        print("Tabla actual:")
        imprimir(tablero, variables_basicas, nombres)

    print("\n--- Resultados finales ---")
    for i, vb in enumerate(variables_basicas):
        print(f"  {nombres[vb]} = {tablero[i+1, -1]:.4f}")
    print(f"  Z = {tablero[0, -1]:.4f}")

def imprimir(tablero, variables_basicas, nombres):
    print("        " + " ".join(f"{n:>8}" for n in nombres))
    print("        " + "-" * (9 * len(nombres)))
    for i, fila in enumerate(tablero):
        nombre_fila = "Z" if i == 0 else nombres[variables_basicas[i-1]]
        print(f"{nombre_fila:>6}: " + " ".join(f"{v:>8.4f}" for v in fila))

def pedir_entero(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("  X Ingrese un numero entero valido.")

def pedir_fila(mensaje, n):
    while True:
        try:
            valores = list(map(float, input(mensaje).split()))
            if len(valores) != n:
                print(f"  X Se esperaban {n} valores, ingreso {len(valores)}. Intente de nuevo.")
                continue
            return valores
        except ValueError:
            print("  X Solo se aceptan numeros. Intente de nuevo.")

if __name__ == "__main__":
    print("=" * 50)
    print("         METODO SIMPLEX")
    print("=" * 50)

    m = pedir_entero("Numero de restricciones: ")
    n = pedir_entero("Numero de variables (x1, x2, ...): ")

    print(f"\nMatriz A - coeficientes de x1..x{n} en cada restriccion")
    print(f"  (ingresar {n} valores por fila, separados por espacio)")
    A = []
    i = 0
    while i < m:
        fila = pedir_fila(f"  Restriccion {i+1}: ", n)
        A.append(fila)
        i += 1

    print(f"\nVector B - lado derecho de cada restriccion ({m} valores separados por espacio)")
    print(f"  Ej: si las restricciones terminan en <= 4, <= 12, <= 18  ->  '4 12 18'")
    B = pedir_fila("  B: ", m)

    print(f"\nVector C - coeficientes de la funcion objetivo ({n} valores separados por espacio)")
    print(f"  Ej: Z = 30000*x1 + 50000*x2  ->  '30000 50000'")
    C = pedir_fila("  C: ", n)

    print("\nObjetivo: ingrese  1  para maximizar  o  -1  para minimizar")
    while True:
        obj = pedir_entero("  Objetivo: ")
        if obj in [1, -1]:
            break
        print("  X Solo se acepta 1 o -1.")
    maximizar = (obj == 1)

    simplex(A, B, C, maximizar=maximizar)