# importa las funciones necesarias de otros archivos
from simplex import simplex  # importa la funcion simplex para resolver el problema
from parser import parser  # importa la funcion parser para convertir texto a datos

# paso 1: definir el modelo como una cadena de texto
# esto es como escribir el problema en un papel, con objetivo, funcion y restricciones
modelo_texto = """
objetivo: min
funcion: 2 2
restricciones:
2 1 <= 100
1 3 <= 80
1 0 <= 45
0 1 <= 100
"""

# paso 2: convertir el texto a datos que entiende el programa
# parser toma el texto y devuelve listas y valores separados
matriz_a, lista_b, lista_c, lista_signos, tipo_objetivo = parser(modelo_texto)
# ahora tenemos:
# matriz_a: coeficientes de restricciones
# lista_b: terminos independientes
# lista_c: coeficientes de la funcion objetivo
# lista_signos: signos como '<='
# tipo_objetivo: 'min' o 'max'

# paso 3: llamar a la funcion simplex para resolver el problema
# simplex toma los datos y calcula la solucion optima
solucion, valor_z = simplex(matriz_a, lista_b, lista_c, lista_signos, tipo_objetivo)
# solucion es un diccionario con valores de variables (ej: {'x1': 10.0})
# valor_z es el valor optimo de la funcion objetivo

# paso 4: imprimir la solucion final
# esto muestra los resultados en pantalla de manera bonita
print("\n--- solucion final ---")  # titulo para la seccion
for nombre_variable, valor in solucion.items():  # recorre cada variable en la solucion
    print(f"{nombre_variable} = {valor:.2f}")  # imprime el nombre y valor con 2 decimales
print(f"valor optimo z = {valor_z:.2f}")  # imprime el valor optimo de z