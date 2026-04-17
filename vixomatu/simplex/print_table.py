def imprimir_tabla(tabla, base_vars, var_names, iteracion):
    # paso 1: imprimir el titulo de la tabla
    # esto es como poner un encabezado grande en la tabla
    print(f"\nTabla Iteración {iteracion}")
    
    # paso 2: crear el encabezado de las columnas
    # el encabezado es la fila superior: "base", luego los nombres de variables, y al final "sol"
    # imagina que es el titulo de cada columna en excel
    columna_base = ["Base"]  # siempre empezamos con "base"
    columnas_variables = var_names  # los nombres de las variables (ej: ["x1", "x2"])
    columna_solucion = ["Sol"]  # al final, la columna de "solucion"
    # unimos todo en una sola lista
    encabezado_completo = columna_base + columnas_variables + columna_solucion
    # ahora encabezado_completo es algo como ["base", "x1", "x2", "sol"]
    
    # paso 3: crear un formato para alinear las columnas
    # queremos que cada columna tenga el mismo ancho (8 espacios) y este alineada a la derecha
    # es como configurar el ancho de las celdas en una tabla
    numero_de_columnas = len(encabezado_completo)  # contamos cuantas columnas hay
    formato_para_fila = "{:>8}" * numero_de_columnas  # repetimos "{:>8}" tantas veces como columnas
    
    # paso 4: imprimir el encabezado
    # usamos el formato para mostrar el encabezado alineado
    print(formato_para_fila.format(*encabezado_completo))
    
    # paso 5: preparar las filas de datos
    # la tabla tiene filas: la primera es especial (w), la segunda (z), y luego las restricciones
    # pero solo imprimimos desde la fila 1 en adelante (saltamos la fila 0 si existe)
    filas_a_imprimir = tabla[1:]  # tomamos todas las filas excepto la primera
    
    # paso 6: recorrer cada fila y imprimirla
    # usamos un bucle para ir fila por fila
    # "zip" combina dos listas: base_vars (nombres) con filas_a_imprimir (numeros)
    for nombre_variable_base, fila_de_numeros in zip(base_vars, filas_a_imprimir):
        # nombre_variable_base: el nombre de la variable para esta fila (ej: "z")
        # fila_de_numeros: la lista de numeros en esa fila (ej: [1.0, 2.5, 3.0])
        
        # paso 6.1: convertir los numeros a texto con 2 decimales
        # queremos que se vean bonitos, como "1.23" en lugar de "1.234567"
        # creamos una lista nueva con los numeros formateados
        fila_formateada = []  # lista vacia para guardar los textos
        for numero in fila_de_numeros:
            numero_como_texto = f"{numero:.2f}"  # convierte a texto con 2 decimales
            fila_formateada.append(numero_como_texto)  # agrega a la lista
        
        # paso 6.2: preparar la fila completa para imprimir
        # la fila incluye: el nombre de la variable base, luego los numeros formateados
        fila_completa = [nombre_variable_base] + fila_formateada
        
        # paso 6.3: imprimir la fila usando el formato
        # esto alinea todo y lo muestra en pantalla
        print(formato_para_fila.format(*fila_completa))
    
    # fin de la funcion. no devuelve nada, solo imprime