import numpy as np
from print_table import imprimir_tabla

def simplex(a, b, c, signos, objetivo='max'):
    # esta funcion resuelve un problema de optimizacion usando el metodo simplex
    # parametros:
    # a: matriz de coeficientes de las restricciones (lista de listas)
    # b: lista de terminos independientes de las restricciones
    # c: lista de coeficientes de la funcion objetivo
    # signos: lista de signos de las restricciones ('<=', '>=', '=')
    # objetivo: 'max' para maximizar o 'min' para minimizar
    
    # paso 1: convertir todo a matrices numpy para calculos faciles
    a = np.array(a, dtype=float)  # convierte a a matriz de flotantes
    b = np.array(b, dtype=float).reshape(-1, 1)  # convierte b a columna de flotantes
    c = np.array(c, dtype=float).flatten()  # convierte c a lista plana de flotantes
    numero_restricciones, numero_variables = a.shape  # obtiene numero de filas y columnas de a
    
    # paso 2: clasificar las restricciones para saber que variables agregar
    # slack: 1 si agrega holgura positiva (<=), -1 si exceso (>=), 0 si nada
    # artificial: 1 si necesita variable artificial (>= o =), 0 si no
    lista_slack = []  # lista para guardar si agregar slack
    lista_artificial = []  # lista para guardar si agregar artificial
    for signo in signos:  # recorre cada signo
        if signo == '<=':  # si es menor o igual
            lista_slack.append(1)  # agrega holgura positiva
            lista_artificial.append(0)  # no necesita artificial
        elif signo == '>=':  # si es mayor o igual
            lista_slack.append(-1)  # agrega exceso (negativo)
            lista_artificial.append(1)  # necesita artificial
        elif signo == '=':  # si es igual
            lista_slack.append(0)  # no agrega slack
            lista_artificial.append(1)  # necesita artificial
    
    # paso 3: crear matrices para slack y artificiales
    matriz_slack = np.zeros((numero_restricciones, numero_restricciones))  # matriz de ceros para slack
    matriz_artificial = np.zeros((numero_restricciones, numero_restricciones))  # matriz de ceros para artificiales
    for i in range(numero_restricciones):  # recorre cada restriccion
        if lista_slack[i] != 0:  # si necesita slack
            matriz_slack[i, i] = lista_slack[i]  # pone 1 o -1 en la diagonal
        if lista_artificial[i]:  # si necesita artificial
            matriz_artificial[i, i] = 1  # pone 1 en la diagonal
    
    # paso 4: formar la matriz extendida con todas las variables
    matriz_extendida = np.hstack([a, matriz_slack, matriz_artificial])  # une a, slack y artificial
    nombres_variables = [f"x{i+1}" for i in range(numero_variables)] + [f"s{i+1}" for i in range(numero_restricciones)] + [f"a{i+1}" for i in range(numero_restricciones)]  # crea nombres: x, s, a
    tableau_inicial = np.hstack([matriz_extendida, b])  # une la matriz con b (lado derecho)
    
    # paso 5: crear la fila de la funcion objetivo (z)
    coeficientes_extendidos = np.hstack([-c, np.zeros(2 * numero_restricciones + 1)])  # extiende c con ceros
    
    # paso 6: crear la fila w (para artificiales)
    fila_w = np.zeros(coeficientes_extendidos.shape)  # fila de ceros del mismo tamaño
    for i in range(numero_restricciones):  # recorre restricciones
        if lista_artificial[i]:  # si tiene artificial
            fila_w[:-1] -= tableau_inicial[i, :-1]  # resta la fila de la restriccion
            fila_w[-1] -= tableau_inicial[i, -1]  # resta el termino independiente
    
    # paso 7: armar el tableau completo
    tableau = np.vstack([fila_w, coeficientes_extendidos, tableau_inicial])  # apila w, z y restricciones
    variables_base = ["w", "z"] + [nombres_variables[numero_variables + numero_restricciones + i] if lista_artificial[i] else nombres_variables[numero_variables + i] for i in range(numero_restricciones)]  # nombres en base
    
    # paso 8: bucle principal del simplex
    numero_iteracion = 0  # contador de iteraciones
    while True:  # bucle infinito hasta que se rompa
        numero_iteracion += 1  # aumenta el contador
        imprimir_tabla(tableau, variables_base, nombres_variables, numero_iteracion)  # imprime la tabla
        
        # paso 8.1: elegir columna pivote (variable entrante)
        indice_columna_pivote = np.argmin(tableau[1, :-1])  # columna con valor mas negativo en fila z
        if tableau[1, indice_columna_pivote] >= 0:  # si no hay negativos
            break  # termina, ya es optimo
        
        # paso 8.2: calcular razones para fila pivote (variable saliente)
        lista_razones = []  # lista para guardar razones
        for i in range(2, tableau.shape[0]):  # recorre filas de restricciones
            elemento = tableau[i, indice_columna_pivote]  # elemento en columna pivote
            if elemento > 0:  # si es positivo
                razon = tableau[i, -1] / elemento  # calcula razon
                lista_razones.append(razon)  # agrega a lista
            else:  # si no es positivo
                lista_razones.append(np.inf)  # agrega infinito
        indice_fila_pivote = np.argmin(lista_razones) + 2  # encuentra la menor razon, ajusta indice
        
        # paso 8.3: normalizar fila pivote
        valor_pivote = tableau[indice_fila_pivote, indice_columna_pivote]  # valor en pivote
        tableau[indice_fila_pivote] /= valor_pivote  # divide la fila por el pivote
        
        # paso 8.4: eliminar columna pivote en otras filas
        for i in range(tableau.shape[0]):  # recorre todas las filas
            if i != indice_fila_pivote:  # excepto la pivote
                factor = tableau[i, indice_columna_pivote]  # factor para multiplicar
                tableau[i] -= factor * tableau[indice_fila_pivote]  # resta la fila pivote multiplicada
        
        # paso 8.5: actualizar variable base
        variables_base[indice_fila_pivote] = nombres_variables[indice_columna_pivote]  # cambia la variable en base
    
    # paso 9: imprimir tabla final
    imprimir_tabla(tableau, variables_base, nombres_variables, "final")  # imprime la ultima tabla
    
    # paso 10: extraer solucion optima
    solucion = {v: 0 for v in nombres_variables}  # diccionario con todas las variables en 0
    for i in range(2, tableau.shape[0]):  # recorre filas de restricciones
        variable = variables_base[i]  # nombre de la variable base
        if variable in solucion:  # si existe en solucion
            solucion[variable] = tableau[i, -1]  # asigna el valor de la columna solucion
    valor_optimo_z = tableau[1, -1] if objetivo == 'min' else -tableau[1, -1]  # calcula z optimo
    
    # paso 11: devolver la solucion
    return solucion, valor_optimo_z  # devuelve diccionario y valor z