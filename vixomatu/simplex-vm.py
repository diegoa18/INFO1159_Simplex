import numpy as np

def imprimir_tabla(tabla, base_vars, var_names, iteracion):
    print(f"\nTabla Iteración {iteracion}")
    #encabezado con el nombre de las variables (base + no básicas + solución)
    header = ["Base"] + var_names + ["Sol"]
    #define el formato para alinear columnas
    row_format = "{:>8}" * len(header)
    print(row_format.format(*header))
    #se imprimen todas las filas del tableau (excepto W y Z), junto con su variable básica
    for var, fila in zip(base_vars, tabla[1:]):
        print(row_format.format(var, *[f"{x:.2f}" for x in fila]))


def simplex(A, b, c, signos, objetivo='max'):
    #se convierten las matrices a tipo float para precisión decimal en los calculos
    A = np.array(A, dtype=float)       #matriz de coeficientes de restricciones
    b = np.array(b, dtype=float).reshape(-1, 1)  #lado derecho (términos independientes)
    c = np.array(c, dtype=float).flatten()      #coeficientes de la función objetivo

    m, n = A.shape  # m = número de restricciones, n = número de variables ori2ginales

    #---- Etapa de clasificación de restricciones ----
    #slack: indica si se debe agregar variable de holgura (1 para ≤, -1 para ≥)
    #artificial: 1 si se necesita variable artificial (para ≥ o =)
    slack = []
    artificial = []
    for s in signos:
        if s == '<=':
            slack.append(1)        #se agrega variable de holgura positiva
            artificial.append(0)  #no requiere variable artificial
        elif s == '>=':
            slack.append(-1)       #variable de exceso (negativa)
            artificial.append(1)   #se necesita variable artificial para formar base
        elif s == '=':
            slack.append(0)        #no hay holgura, pero no garantiza base canónica
            artificial.append(1)   #necesita artificial para iniciar el método


    #se crean matrices identidad para agregar slack y artificiales segun necesidades
    S = np.zeros((m, m))      #variables de holgura (slack)
    A_art = np.zeros((m, m))  #variables artificiales (para ≥ o =)

    for i in range(m):
        if slack[i] != 0:
            S[i, i] = slack[i]  #se añade 1 o -1 en la posición correspondiente
        if artificial[i]:
            A_art[i, i] = 1     #se añade 1 si se necesita una artificial


    #se forma la matriz extendida A | S | A_art (todas las variables lado izquierdo)
    A_ext = np.hstack([A, S, A_art])
    #se definen los nombres de todas las variables: x (originales), s (slack), a (artificiales)
    var_names = [f"x{i+1}" for i in range(n)] + [f"s{i+1}" for i in range(m)] + [f"a{i+1}" for i in range(m)]
    #se arma el tableau inicial: se concatena la matriz extendida con los términos independientes
    tableau = np.hstack([A_ext, b])
    #fila de Z: se extiende la función objetivo con ceros (slack, artificiales, término independiente)
    c_ext = np.hstack([-c, np.zeros(2*m + 1)])


    #se construye la fila W: combinación lineal negativa de las restricciones con artificiales
    Z_row = np.zeros(c_ext.shape)
    for i in range(m):
        if artificial[i]:
            Z_row[:-1] -= tableau[i, :-1]   #suma negativa de cada fila con artificial
            Z_row[-1] -= tableau[i, -1]     #también se resta el termino independiente


    #se inserta la fila W (0), fila Z (1) y las restricciones (2 en adelante)
    tableau = np.vstack([Z_row, c_ext, tableau])
    #se definen las variables en la base: W, Z, y la variable asociada a cada restricción
    base_vars = ["W", "Z"] + [var_names[n + m + i] if artificial[i] else var_names[n + i] for i in range(m)]


    iteracion = 0
    while True:
        iteracion += 1
        imprimir_tabla(tableau, base_vars, var_names, iteracion)

        #se selecciona la columna pivote (variable entrante): la más negativa en fila Z
        pivot_col = np.argmin(tableau[1, :-1])  #solo se considera hasta la penultima columna
        if tableau[1, pivot_col] >= 0:
            break  #si no hay valores negativos en Z, se ha alcanzado el optimo


        #se calculamos las razones para decidir la fila pivote (variable que sale)
        ratios = []
        for i in range(2, tableau.shape[0]):
            elem = tableau[i, pivot_col]
            if elem > 0:
                ratios.append(tableau[i, -1] / elem)
            else:
                ratios.append(np.inf)
        pivot_row = np.argmin(ratios) + 2  #se ajusta por el offset de las filas W y Z

        #se normaliza la fila pivote
        pivot_val = tableau[pivot_row, pivot_col]
        tableau[pivot_row] /= pivot_val

        #se realizan operaciones fila para anular la columna pivote en las demás filas
        for i in range(tableau.shape[0]):
            if i != pivot_row:
                tableau[i] -= tableau[i, pivot_col] * tableau[pivot_row]

        #se actualiza la variable base con la nueva variable que entra
        base_vars[pivot_row] = var_names[pivot_col]

    #imprime la tabla final después de terminar las iteraciones
    imprimir_tabla(tableau, base_vars, var_names, "Final")

    #se extrae la solución óptima: se asigna 0 a todas y luego se toman los valores de las básicas
    sol = {v: 0 for v in var_names}
    for i in range(2, tableau.shape[0]):
        var = base_vars[i]
        if var in sol:
            sol[var] = tableau[i, -1]
    z_opt = tableau[1, -1] if objetivo == 'min' else -tableau[1, -1]  #valor óptimo de Z

    return sol, z_opt

#esta funcion convierte un modelo en texto a estructuras que puede usar el método simplex
def parser(cadena_modelo):
    #se limpia y separan cada línea del texto del modelo
    lineas = [line.strip() for line in cadena_modelo.strip().split('\n') if line.strip()]

    #determina si es un problema de maximización o minimización
    objetivo = 'max' if 'max' in lineas[0].lower() else 'min'
    #se extrae los coeficientes de la función objetivo
    c = list(map(float, lineas[1].split(':')[1].strip().split()))

    #inicializa las listas para restricciones
    A = []
    b = []
    signos = []

    #se procesa cada línea de restricción: coeficientes, signo y término independiente
    for linea in lineas[3:]:
        *coef, signo, termino = linea.split()
        A.append(list(map(float, coef)))
        signos.append(signo)
        b.append(float(termino))

    return A, b, c, signos, objetivo

#define el modelo de ejemplo como una cadena multilínea
modelo_str = """
objetivo: min
funcion: 2 2
restricciones:
2 1 <= 100
1 3 <= 80
1 0 <= 45
0 1 <= 100
"""

#parseamos el modelo desde el string
A, b, c, signos, objetivo = parser(modelo_str)
#llama al método simplex para resolver el problema
sol, z = simplex(A, b, c, signos, objetivo)


print("\n--- Solución Final ---")
for k, v in sol.items():
    print(f"{k} = {v:.2f}")
print(f"Valor óptimo Z = {z:.2f}")
    
    
    