import numpy as np

# Función para valores muy pequeños
def casi_Cero(tablero):

    # Crear una copia del tablero para evitar modificar el original
    tablero = tablero.copy()

    # Definir un valor pequeño para considerar como cero
    epsilon = 1e-7

    # Modificar cada valor del tablero a 0 si es menor que epsilon
    for fila in tablero:
        for j in range(len(fila)):
            if abs(fila[j]) < epsilon:
                fila[j] = 0.0

    # Retornar el tablero modificado
    return tablero

# Función para un valor muy pequeños
def casi_Cero_Val(val):

    # Definir un valor pequeño para considerar como cero
    epsilon = 1e-10

    # Modificar el valor a 0 si es menor que epsilon
    if abs(val) < epsilon:
        val = 0.0

    # Retornar el valor modificado
    return val

# Función para construir la matriz aumentada
def matriz_aumentada(A, B, C, Cf, signos, objetivo):

    # Convertir las entradas a arreglos numpy
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float).reshape(-1, 1)  # Convertir B en un vector columna
    C = np.array(C, dtype=float)

    # Asegurarse de que no haya restricciones con lado derecho negativo
    A, B, signos = noNegatividad(A, B, signos)

    # Inicializar la lista de variables básicas
    variables_basicas = []

    # Determinar el número de restricciones y variables
    num_restricciones, num_variables = A.shape

    # Variable para determinar si se necesita usar el metodo de dos fases
    fase = False

    # Verificar si hay restricciones de tipo >=
    if any(signo == 2 for signo in signos):

        # Si hay restricciones de tipo >=, se necesita metodo de dos fases
        fase = True

        # Construir la fila de la función objetivo
        # Se agrega un cero al inicio seguido de tantos ceros como variables de la función objetivo
        fila_objetivo = np.concatenate([[objetivo], np.zeros(len(C))])

        # En la fila de la función objetivo se agregan:
        for i in range(num_restricciones):

            # Si el signo es <=
            if signos[i] == 1:

                # - Ceros para las variables de holgura
                fila_objetivo = np.concatenate([fila_objetivo, [0]])

            # Si el signo es >=
            else:

                # - Ceros para las variables de exceso
                # - Unos para las variables artificiales
                fila_objetivo = np.concatenate([fila_objetivo, [0], [1]])

        # Se agrega el valor de Cf al final para el lado derecho (LD)
        fila_objetivo = np.concatenate([fila_objetivo, [Cf]])

        # Inicializar el tablero con la fila de la función objetivo
        tablero = [fila_objetivo]

        # Construir cada fila del sistema
        cerosIzquierda = 0
        cerosDerecha = sum(1 if s == 1 else 2 for s in signos)  # Contar variables adicionales

        # Iterar sobre las restricciones
        for i in range(num_restricciones):

            # Construir la fila coeficientes de A y los ceros que le siguen
            fila = np.concatenate([[0], A[i], np.zeros(cerosIzquierda)])

            # Si el signo es <=
            if signos[i] == 1:

                # Se disminuye el contadore de los ceros que van al lado derecho (ya que tenia el maximo en un inicio)
                cerosDerecha -= 1

                # Se agrega a la fila actual un 1 para la variable de holgura
                fila = np.concatenate([fila, [1], np.zeros(cerosDerecha)])

                # Se agrega el índice de la variable básica a la lista
                variables_basicas.append(num_variables + cerosIzquierda + 1)

                # Se incrementa el contador de ceros a la izquierda
                cerosIzquierda += 1

            # Si el signo es >=
            elif signos[i] == 2:

                # Se disminuye el contador de los ceros que van al lado derecho (ya que tenia el maximo en un inicio)
                cerosDerecha -= 2

                # Se agrega a la fila actual un -1 para la variable de exceso y un 1 para la variable artificial
                fila = np.concatenate([fila, [-1], [1], np.zeros(cerosDerecha)])

                # Se agrega el índice de la variable básica a la lista
                variables_basicas.append(num_variables + cerosIzquierda + 2)

                # Se incrementa el contador de ceros a la izquierda
                cerosIzquierda += 2

            # Agregar el lado derecho (LD)
            fila = np.concatenate([fila, [B[i][0]]])

            # Agregar la fila al tablero
            tablero.append(fila)

    else:
        
        # Construir la fila de la función objetivo
        fila_objetivo = np.concatenate([[objetivo], -1 * C, np.zeros(num_restricciones), [Cf]])
        tablero = [fila_objetivo]

        # Construir cada fila del sistema
        cerosIzquierda = 0
        cerosDerecha = sum(1 for s in signos)  # Contar variables adicionales

        # Iterar sobre las restricciones
        for i in range(num_restricciones):

            # Construir la fila con los coeficientes de A y ceros a la izquierda
            fila = np.concatenate([[0], A[i], np.zeros(cerosIzquierda)])

            # Se disminuye el contador de los ceros que van al lado derecho (ya que tenia el maximo en un inicio)
            cerosDerecha -= 1

            # Se agrega a la fila actual un 1 para la variable de holgura
            fila = np.concatenate([fila, [1], np.zeros(cerosDerecha)])

            # Se agrega el índice de la variable básica a la lista
            variables_basicas.append(num_variables + cerosIzquierda + 1)

            # Se incrementa el contador de ceros a la izquierda
            cerosIzquierda += 1

            # Agregar el lado derecho (LD)
            fila = np.concatenate([fila, [B[i][0]]])
            tablero.append(fila)

    # Convertir el tablero a un arreglo numpy y retornarlo junto con las variables básicas
    return np.array(tablero, dtype=float), variables_basicas, fase

# Verificar que no haya restricciones con lado derecho negativo
def noNegatividad(A, B, signos):

    # Se copian las matrices para evitar modificar las originales
    A = A.copy()
    B = B.copy()
    signos = signos.copy()

    # Se itera sobre las restricciones
    for i in range(len(B)):

        # Si el lado derecho de alguna restricción es negativo
        if B[i][0] < 0:

            # Se multiplica el lado derecho de la restricción por -1
            B[i][0] *= -1

            # Se multiplican los coeficientes de la matriz A por -1
            A[i] *= -1

            # Se cambia el signo de la restricción
            # Si el signo es <=, se cambia a >= y viceversa
            signos[i] = 1 if signos[i] == 2 else 2  # Cambiar el signo de la restricción

    # Retornar las matrices modificadas
    return A, B, signos

# Encontrar la columna pivote
def columna_pivote(tablero, fase=False):

    # Encontrar el índice del pivote (valor más negativo)
    pivote = np.argmin(tablero[0][1:-1]) + 1

    # Si se está en la fase 2, buscar el máximo (valor más positivo)
    if fase:
        pivote = np.argmax(tablero[0][1:-1]) + 1

    # Se retorna el indice de la columna pivote
    return pivote

# Encontrar la fila pivote
def fila_pivote(tablero, columna_pivote):

    # Encontrar el índice de la fila pivote (mínimo cociente)
    cocientes = []

    # Iterar sobre las filas del tablero (omitimos la fila Z)
    for i in range(1, len(tablero)):

        # Si el valor de la columna pivote es positivo?
        # Preguntar al profe si debe ser positivo
        if tablero[i][columna_pivote] > 0:

            # Calcular el cociente entre el lado derecho y el valor de la columna pivote
            cociente = tablero[i][-1] / tablero[i][columna_pivote]

            # Agregar el cociente y el índice de la fila a la lista
            cocientes.append((cociente, i))

    # Si no hay cocientes válidos, retornar None
    if not cocientes:
        return None
    
    # Se busca el mínimo cociente y se retorna el índice de la fila pivote
    return min(cocientes)[1]

# Verificar si alguno de los elementos de la fila de la función objetivo son negativos
def no_negativos(tablero):
    
    # Identificador si se encontro un valor negativo
    negativo = False

    # Iterar sobre los elementos de la fila de la función objetivo (omitimos el primer y último elemento)
    for i in tablero[0][1:-1]:

        # Si el elemento es negativo
        if i < 0:

            # Cambiamos el identificador a True
            negativo = True

    # Retornar el identificador
    return negativo

# Verificar si alguno de los elementos de la fila de la función objetivo son positivos
def no_positivos(tablero):
    
    # Identificador si se encontro un valor positivo
    positivo = False

    # Iterar sobre los elementos de la fila de la función objetivo (omitimos el primer y último elemento)
    for i in tablero[0][1:-1]:

        # Si el elemento es positivo
        if i > 0:

            # Cambiamos el identificador a True
            positivo = True

    # Retornar el identificador
    return positivo

# Función para pivotear el tablero
def pivotear(tablero, fila, columna):

    # Crear una copia del tablero para evitar modificar el original
    tablero = tablero.copy()

    # Normalizar la fila pivote
    tablero[fila] /= tablero[fila][columna]

    # Pivotear cada fila del tablero según la fila pivote
    for i in range(len(tablero)):

        # Pivotear las demas que no sean la fila pivote (Ya esta normalizada)
        if i != fila:

            # Actualizar la fila restando el producto de la fila pivote por el valor de la columna pivote
            tablero[i] -= tablero[i][columna] * tablero[fila]
            
    # Retornar el tablero modificado
    return tablero

# Función para imprimir qué variable entra y qué variable sale de la base
def imprimir_cambio_base(columna, fila, variables_basicas, nombres_columnas):

    # Variable que entra
    variable_entra = nombres_columnas[columna]

    # Variable que sale
    variable_sale = nombres_columnas[variables_basicas[fila - 1]]

    print(f"Variable que entra: {variable_entra}")
    print(f"Variable que sale: {variable_sale}")

# Función para definir los nombres de las columnas
def nombre_columnas(signos, C):

    # Se define el nombre de las columnas de la tabla
    # Se agrega "Z" al inicio, seguido de "x1", "x2", ..., "xn"
    nombres_columnas = ["Z"] + [f"x{i+1}" for i in range(len(C))]

    # Se inicializan contadores para las variables artificiales, de exceso y holgura
    count_artificiales = 1
    count_exceso = 1
    count_holguras = 1

    # Se itera sobre los signos de las restricciones
    for signo in signos:

        # Si el signo es 1 (≤), se agrega una variable de holgura (h)
        if signo == 1:

            # Se agrega una variable de holgura (h) a la lista de nombres de columnas
            nombres_columnas.append(f"h{count_holguras}")

            # Se incrementa el contador de holguras
            count_holguras += 1
        
        # Si el signo es 2 (≥), se agregan una variable de exceso (e) y una artificial (a)
        elif signo == 2:

            # Se agrega una variable de exceso (e) y una artificial (a) a la lista de nombres de columnas
            nombres_columnas.append(f"e{count_exceso}")
            nombres_columnas.append(f"a{count_artificiales}")

            # Se incrementan los contadores de exceso y artificiales
            count_exceso += 1
            count_artificiales += 1

    # Se agrega la columna LD (lado derecho) al final de la lista de nombres de columnas
    nombres_columnas.append("LD")

    # Se retorna la lista de nombres de columnas
    return nombres_columnas

# Función para imprimir la tabla del método Simplex
def imprimirTabla(tablero, C, variables_basicas, nombres_columnas, columnas_a_omitir=None, fase=False):

    # Si se está en la fase 2, se omiten las columnas de variables artificiales y de exceso
    if fase:

        # Se omiten las columnas de variables artificiales
        nombres_columnas = [col for i, col in enumerate(nombres_columnas) if i not in columnas_a_omitir]

        # Se eliminan las columnas de variables artificiales
        tablero = np.delete(tablero, columnas_a_omitir, axis=1)

        # Filtrar las variables básicas eliminando aquellas que corresponden a las columnas omitidas (artificiales)
        variables_basicas = [var for var in variables_basicas if var not in columnas_a_omitir]

        # Itera sobre las columnas a omitir (artificiales) y sus índices
        # "i" es el índice de la iteración, y "col" es el indice de las columnas a omitit
        for i, col in enumerate(columnas_a_omitir):

            # Se ajustan los índices de las variables básicas
            variables_basicas = [var - 1 if var > col else var for var in variables_basicas]

    # Se imprimen los nombres de las columnas
    print("        " + " ".join(f"{name:>8}" for name in nombres_columnas))

    # Se agregan guiones para separar el nombre de las columnas y los valores
    print("        " + "-" * (9 * len(nombres_columnas)))

    # Se define un indice para cada fila de la tabla
    for i, fila in enumerate(tablero):

        # Si es la primera fila se asigna "Z" al nombre de la fila
        if i == 0:
            nombre_fila = "Z"
        else:

            # Si la diferencia entre el índice de la fila y 1 es menor que la cantidad de variables básicas
            if i - 1 < len(variables_basicas):

                # Se obtiene el índice de la variable básica correspondiente
                idx = variables_basicas[i - 1]

                # Si el índice es menor o igual que el número de variables
                if idx <= len(C):

                    # Se asigna el nombre de la fila como "x" seguido del índice
                    nombre_fila = f"x{idx}"
                else:
 
                    # Se toman todos los nombres de las columnas desde el indice 1 hasta el penultimo
                    extras = nombres_columnas[1:-1]

                    # Se asigna el nombre de la fila como el nombre correspondiente de la variable básica
                    nombre_fila = extras[idx - 1] if idx - 1 < len(extras) else f"v{idx}"
            else:

                # Se asigna "?" en caso que i-1 no sea menor a la cantidad de variables basicas 
                nombre_fila = "?"

        # Formatea cada valor de la fila para que se muestre con un ancho de 8 caracteres, alineado a la derecha,
        # y redondeado a 4 decimales en formato de punto flotante.
        fila_formateada = [f"{val:>8.4f}" for val in fila]

        # Se imprime la fila con su nombre correspondiente
        print(f"{nombre_fila:>6}: " + " ".join(fila_formateada))

# Función para eliminar columnas de variables artificiales
def eliminar_columnas_artificiales(tablero, variables_basicas, nombres_columnas):

    # Identificar las columnas de las variables artificiales
    columnas_a_eliminar = [i for i, nombre in enumerate(nombres_columnas) if nombre.startswith("a")]

    # Eliminar las columnas del tablero
    tablero = np.delete(tablero, columnas_a_eliminar, axis=1)

    # Ajustar las variables básicas eliminando las que corresponden a las columnas artificiales
    variables_basicas = [var for var in variables_basicas if var not in columnas_a_eliminar]

    # Ajustar los índices de las variables básicas restantes
    for col in sorted(columnas_a_eliminar):
        variables_basicas = [var - 1 if var > col else var for var in variables_basicas]

    # Eliminar los nombres de las columnas artificiales
    nombres_columnas = [nombre for i, nombre in enumerate(nombres_columnas) if i not in columnas_a_eliminar]

    # Retornar el tablero ajustado, las variables básicas y los nombres de las columnas
    return tablero, variables_basicas, nombres_columnas

# No se si esta bien
'''
def ajustar(tablero, variables_basicas):

    tablero = tablero.copy()
    # Ajustar la tabla para que las variables básicas estén en forma canónica
    for fila in range(1, len(tablero)):  # Iterar sobre las filas (omitimos la fila Z)
        col = variables_basicas[fila - 1]  # Obtener la columna correspondiente a la variable básica

        # Verificar si el valor en la posición (fila, col) no es 1
        if not casi_Cero_Val(tablero[fila][col] - 1):  # Si no es aproximadamente 1
            tablero = pivotear(tablero, fila, col)  # Pivotear para ajustar

        # Verificar si los demás valores en la columna no son 0
        for i in range(len(tablero)):
            if i != fila and not casi_Cero_Val(tablero[i][col]):  # Si no es aproximadamente 0
                tablero = pivotear(tablero, fila, col)  # Pivotear para ajustar

    return tablero
'''

def verificar(tablero, variables_basicas):
    """
    Ajusta el tablero para que las columnas de las variables básicas estén en forma canónica.
    
    Parámetros:
    - tablero: Matriz del método Simplex.
    - variables_basicas: Lista de índices de las variables básicas actuales.

    Retorna:
    - tablero: Tablero ajustado.
    """
    tablero = tablero.copy()  # Crear una copia del tablero para evitar modificar el original

    # Iterar sobre las filas de las variables básicas
    for fila in range(1, len(tablero)):  # Omitimos la fila Z (fila 0)
        col = variables_basicas[fila - 1]  # Obtener la columna correspondiente a la variable básica

        # Verificar si el valor en la posición (fila, col) no es 1
        if not np.isclose(tablero[fila][col], 1.0):  # Si no es aproximadamente 1
            tablero = pivotear(tablero, fila, col)  # Pivotear para normalizar la fila

        # Asegurarse de que los demás valores en la columna sean 0
        for i in range(len(tablero)):
            if i != fila and not np.isclose(tablero[i][col], 0.0):  # Si no es aproximadamente 0
                tablero = pivotear(tablero, fila, col)  # Pivotear para ajustar

    return tablero

# Función para imprimir los resultados finales
def imprimir_resultados(tablero, C, nombres_columnas, variables_basicas):

    # Imprimir los resultados finales
    print("\nResultados finales:")

    # Número de variables originales
    num_variables = len(C)

    # Inicializar el vector de resultados
    resultados = np.zeros(num_variables)

    # Obtener los valores de las variables básicas
    for i, var in enumerate(variables_basicas):
        if var <= num_variables:  # Solo considerar las variables originales
            resultados[var - 1] = tablero[i + 1, -1]  # LD de la fila correspondiente

    # Imprimir los valores de las incógnitas
    print("\nValores de las incógnitas:")
    for i, valor in enumerate(resultados):
        print(f"x{i + 1} = {valor:.4f}")

    valor_optimo = tablero[0, -1]
    print(f"\nValor óptimo de Z = {valor_optimo:.4f}")

    # Imprimir los precios sombra
    print("\nPrecios sombra:")
    for i, nombre in enumerate(nombres_columnas):
        if nombre.startswith("e") or nombre.startswith("h"):  # Variables de exceso o holgura
            precio_sombra = tablero[0, i]
            if tablero[0, 0] == -1:
                precio_sombra = -precio_sombra
            if precio_sombra != 0:
                print(f"Restricción asociada a {nombre}: Precio sombra = {precio_sombra:.4f}")

def simplex(A, B, C, Cf, signos, objetivo):

    # Convertir las entradas a arreglos numpy de tipo float (flotante)
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float).reshape(-1, 1)  # Convertir B en un vector columna
    C = np.array(C, dtype=float)
    Cf = np.array(Cf, dtype=float)
    signos = np.array(signos, dtype=float)

    A, B, signos = noNegatividad(A, B, signos)

    tablero, variables_basicas, fase = matriz_aumentada(A, B, C, Cf, signos, objetivo)

    for x, i in enumerate(signos):
        if i == 2:
            tablero[0] = tablero[0] - tablero[x + 1]

    nombres_columnas = nombre_columnas(signos, C)

    print("Tablero inicial:")
    imprimirTabla(tablero, C, variables_basicas, nombres_columnas)

    while no_negativos(tablero):

        # Encontrar la columna pivote
        columna = columna_pivote(tablero)

        # Encontrar la fila pivote
        fila = fila_pivote(tablero, columna)

        if fila is None:
            print("El problema es ilimitado.")
            break

        print(f"\nPivotear con respecto a\nColumna pivote: {columna}, Fila pivote: {fila}\n")
        tablero = pivotear(tablero, fila, columna)

        # Imprimir qué variable entra y qué variable sale
        imprimir_cambio_base(columna, fila, variables_basicas, nombres_columnas)

        variables_basicas[fila - 1] = columna

        tablero = casi_Cero(tablero)

        # Imprimir la tabla actual
        print("\nTabla actual:")
        imprimirTabla(tablero, C, variables_basicas, nombres_columnas)

    # Verificar si se está usando el metodo de las dos fases
    if fase:

        # Eliminar columnas de variables artificiales
        tablero, variables_basicas, nombres_columnas = eliminar_columnas_artificiales(tablero, variables_basicas, nombres_columnas)

        # Imprimir la tabla después de eliminar columnas artificiales
        print("\nTabla después de eliminar columnas artificiales:\n")
        imprimirTabla(tablero, C, variables_basicas, nombres_columnas)

        # Actualizar el tablero agregando los coeficientes de la función objetivo
        print("\nAgregando los coeficientes de la función objetivo:")
        for i, x in enumerate(C):
            tablero[0][i + 1] = -x

        print("\nTabla después de agregar los coeficientes de la función objetivo:\n")
        imprimirTabla(tablero, C, variables_basicas, nombres_columnas)

        if objetivo == 1:
            while no_negativos(tablero):

                # Encontrar la columna pivote
                columna = columna_pivote(tablero, fase=False)

                # Encontrar la fila pivote
                fila = fila_pivote(tablero, columna)

                if fila is None:
                    print("El problema es ilimitado.")
                    break

                print(f"\nPivotear con respecto a\nColumna pivote: {columna}, Fila pivote: {fila}\n")
                tablero = pivotear(tablero, fila, columna)

                # Imprimir qué variable entra y qué variable sale
                imprimir_cambio_base(columna, fila, variables_basicas, nombres_columnas)

                variables_basicas[fila - 1] = columna

                tablero = casi_Cero(tablero)

                # Imprimir la tabla actual
                print("\nTabla actual:")
                imprimirTabla(tablero, C, variables_basicas, nombres_columnas)
        else:
            # Verificar y ajustar el tablero para las variables básicas
            tablero = verificar(tablero, variables_basicas)

            # Imprimir la tabla ajustada
            print("\nTabla ajustada para las variables básicas:\n")
            imprimirTabla(tablero, C, variables_basicas, nombres_columnas)

        #tablero = ajustar(tablero, variables_basicas)

    print("\nTablero final:")
    imprimirTabla(tablero, C, variables_basicas, nombres_columnas)

    # Imprimir los resultados finales
    imprimir_resultados(tablero, C, nombres_columnas, variables_basicas)

'''
Valores de prueba

A = [[4, 1, 2], [1, 2, 3], [2, 3, 1]]
B = [70, 60, 80]
C = [3, 5, 4]
Cf = 0
signos = [1, 2, 1]  # 1. <= 2. >=
objetivo = -1

A = [[60, 60], [12, 6], [10, 30]]
B = [300, 36, 90]
C = [0.12, 0.15]
Cf = 0
signos = [2,2,2]
objetivo = -1

A = [[2, 1], [1, 3], [1, 0], [0, 1]]
B = [100, 80, 45, 100]
C = [2, 2]
Cf = 0
signos = [1, 1, 1, 1]
objetivo = 1

simplex(A, B, C, Cf, signos, objetivo)
'''

if __name__ == "__main__":
    print("Método Simplex")

    # Solicitar el número de restricciones
    num_restricciones = int(input("Ingrese el número de restricciones: "))

    # Solicitar el número de variables
    num_variables = int(input("Ingrese el número de variables: "))

    # Solicitar la matriz A
    print("\nIngrese la matriz A (coeficientes de las restricciones):")
    A = []
    for i in range(num_restricciones):
        fila = list(map(float, input(f"Fila {i + 1}: ").split()))
        if len(fila) != num_variables:
            raise ValueError(f"La fila {i + 1} debe tener {num_variables} valores.")
        A.append(fila)

    # Solicitar el vector B
    print("\nIngrese el vector B (lado derecho de las restricciones):")
    B = list(map(float, input().split()))
    if len(B) != num_restricciones:
        raise ValueError(f"El vector B debe tener {num_restricciones} valores.")

    # Solicitar el vector C
    print("\nIngrese el vector C (coeficientes de la función objetivo):")
    C = list(map(float, input().split()))
    if len(C) != num_variables:
        raise ValueError(f"El vector C debe tener {num_variables} valores.")

    # Solicitar el valor de Cf
    print("\nIngrese el valor de Cf (constante de la función objetivo):")
    Cf = float(input())

    # Solicitar el vector de signos
    print("\nIngrese el vector de signos (1 para <=, 2 para >=):")
    signos = list(map(int, input().split()))
    if len(signos) != num_restricciones:
        raise ValueError(f"El vector de signos debe tener {num_restricciones} valores.")

    # Solicitar el tipo de objetivo
    print("\nIngrese el tipo de objetivo (1 para maximizar, -1 para minimizar):")
    objetivo = int(input())
    if objetivo not in [1, -1]:
        raise ValueError("El objetivo debe ser 1 (maximizar) o -1 (minimizar).")

    # Ejecutar el método Simplex
    print("\nEjecutando el método Simplex...\n")
    simplex(A, B, C, Cf, signos, objetivo)