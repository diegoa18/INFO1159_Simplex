def parser(cadena_modelo):
    # esta funcion toma un texto (cadena_modelo) y lo convierte en datos utiles
    # el texto tiene formato como "objetivo: min", "funcion: 2 2", etc.
    # devuelve: matriz_a (coeficientes), lista_b (terminos), lista_c (funcion), signos, objetivo
    
    # paso 1: limpiar y separar el texto en lineas
    # quita espacios extra y salta lineas vacias
    lineas = [linea.strip() for linea in cadena_modelo.strip().split('\n') if linea.strip()]
    # ahora lineas es una lista de strings limpios, como ['objetivo: min', 'funcion: 2 2', ...]
    
    # paso 2: determinar si es maximizar o minimizar
    # mira la primera linea: si dice 'max', es maximizar; sino, minimizar
    primera_linea = lineas[0].lower()  # convierte a minusculas para comparar
    objetivo = 'max' if 'max' in primera_linea else 'min'  # asigna 'max' o 'min'
    
    # paso 3: extraer los coeficientes de la funcion objetivo
    # la segunda linea es como "funcion: 2 2", toma lo que esta despues de ':'
    segunda_linea = lineas[1]  # 'funcion: 2 2'
    parte_despues_dos_puntos = segunda_linea.split(':')[1].strip()  # '2 2'
    lista_c = list(map(float, parte_despues_dos_puntos.split()))  # convierte a lista de floats: [2.0, 2.0]
    
    # paso 4: inicializar listas para restricciones
    # estas listas guardaran los datos de cada restriccion
    matriz_a = []  # coeficientes de variables en restricciones
    lista_b = []  # terminos independientes (lado derecho)
    signos = []  # signos como '<=', '>=', '='
    
    # paso 5: procesar cada linea de restriccion
    # las restricciones empiezan desde la linea 3 (indice 3 en la lista)
    for linea in lineas[3:]:  # recorre desde la cuarta linea en adelante
        # cada linea es como "2 1 <= 100"
        partes = linea.split()  # separa por espacios: ['2', '1', '<=', '100']
        coeficientes = partes[:-2]  # toma todo menos los ultimos 2: ['2', '1']
        signo = partes[-2]  # el penultimo: '<='
        termino = partes[-1]  # el ultimo: '100'
        
        # convierte coeficientes a floats y agrega a matriz_a
        matriz_a.append(list(map(float, coeficientes)))  # ej: [2.0, 1.0]
        # agrega el signo a la lista
        signos.append(signo)  # ej: '<='
        # convierte termino a float y agrega a lista_b
        lista_b.append(float(termino))  # ej: 100.0
    
    # paso 6: devolver todos los datos
    # esto es lo que main.py usara
    return matriz_a, lista_b, lista_c, signos, objetivo