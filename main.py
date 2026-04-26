import numpy as np

R = np.array([ # restricciones
	[1, 0],
	[0, 2],
    [3, 2]
], dtype=float)

b = np.array([4, 12, 18], dtype=float) # resultados de las restricciones
c = np.array([30000,50000], dtype=float) # función objetivo

MI = np.eye(len(R)) # matriz de identidad 

# reshape : cambia la forma de un array sin cambiar sus datos
# hstack : apila arrays en secuencia horizontal (columnas)
restricciones = np.hstack((np.zeros((3,1)), R, MI, b.reshape(-1,1)))

fila_z = np.hstack(([1], -c, np.zeros(3), [0])) # fila de la función objetivo

# vstack : apila arrays en secuencia vertical (filas)
tabla = np.vstack((fila_z, restricciones))

columnas = ["Z", "x1", "x2", "h1", "h2", "h3", "LD"]
filas = ["Z","h1", "h2", "h3"]

def imprimir_tabla(tabla, filas, columnas):
    print("\nMétodo Simples: Forma tabular\n")

    header = ["VB"] + columnas # encabezado
    print("  ".join(f"{h:>8}" for h in header)) # imprimir encabezado 
    print("-" * (10 * len(header))) # imprimir línea separadora

    for i, fila in enumerate(tabla): # imprimir cada fila de la tabla
        nombre = filas[i] # nombre de la fila
        print(f"{nombre:>8}", end="  ") # imprimir nombre de la fila
        for val in fila: 
            print(f"{val:>8.1f}", end="  ") # imprimir cada valor de la fila
        print() # nueva línea después de cada fila

    print("-" * (10 * len(header)))

def columna_pivote(tabla):
	return np.argmin(tabla[0, 1:-1]) + 1 # encontrar el índice de la columna pivote, evita Z y LD
# argmin : devuelve el índice del valor mínimo a lo largo de un ejes

def fila_pivote(tabla, col_pivote):
	# full : crea un array con un mismo valor
	# shape : dimensiones del array
	# inf : representa el infinito, se usa para inicializar los coeficientes
	coeficiente = np.full(tabla.shape[0] - 1, np.inf) # crea un array con las filas - 1 (Z) y lo llena con infinitos
	for i in range(1, tabla.shape[0]):
		if tabla[i, col_pivote] > 0: # solo considerar filas con coeficiente positivo en la columna pivote
			coeficiente[i-1] = tabla[i, -1] / tabla[i, col_pivote] # calcular ratio LD / coeficiente pivote
	return np.argmin(coeficiente) + 1 # devolver el índice de la fila pivote

def pivotear(tabla, fila, col):
	pivote = tabla[fila][col] # valor del pivote 
	tabla[fila] = tabla[fila] / pivote # dividir la fila pivote por el valor del pivote para hacer que el pivote sea 1

	for i in range(len(tabla)): # iterar sobre todas las filas
		if i != fila: # para todas las filas excepto la fila pivote
			factor = tabla[i][col] # coeficiente en la columna pivote de la fila actual
			tabla[i] = tabla[i] - factor * tabla[fila] # fn - n * fp para que sea 0
	return tabla # devuelve la tablita

def negativos(tabla):
	return np.any(tabla[0, 1:-1] < 0) # verificar si hay coeficientes negativos en la fila Z

print("\n--- TABLA INICIAL ---")
imprimir_tabla(tabla, filas, columnas)

# pa que pivetee hasta que no hayan coeficientes negativos en la fila Z
iteracion = 1
while negativos(tabla):
    print(f"\n--- ITERACIÓN {iteracion} ---")

    col = columna_pivote(tabla)
    fila = fila_pivote(tabla, col)

    print(f"Columna pivote: {columnas[col]}")
    print(f"Fila pivote: {filas[fila]}")

    filas[fila] = columnas[col]

    tabla = pivotear(tabla, fila, col)

    print("\nTabla después del pivoteo:")
    imprimir_tabla(tabla, filas, columnas)

    iteracion += 1