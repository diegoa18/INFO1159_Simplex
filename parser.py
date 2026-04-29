from typing import Optional


# convierte de string a float, maneja signos negativos
def _parse_real(s: str) -> float:
    s = s.strip() # elimina espacios
    if s.startswith("-"): # verifica si es negativo
        s = s[1:] # elimina signo y lo vuelve negativo
        return -float(s) if s else -1.0 # retorna el valor negativo o -1 si no hay numero
    return float(s) if s else 1.0 # si no hay numero, se asume coeficiente 1


# limpia cadena, mapea coeficientes a variables especificas (x, y, z, w, u, v)
def _parse_coeffs(texto: str) -> list[float]:
    texto = texto.replace("-", "+-").replace(" ", "") # cambia los signos por espacio
    partes = [p for p in texto.split("+") if p] # separa los terminos 
    coeffs = []
    vars_orden = ["x", "y", "z", "w", "u", "v"] #variables conocidas
    coef_map = {v: 0.0 for v in vars_orden} # crea mapa de variables a coeficientes
    # recorre cada parte 
    for p in partes:
        for var in vars_orden: # detecta la variable
            if var in p:
                coef = p.replace(var, "") # extrae el coeficiente 
                coef_map[var] = _parse_real(coef) if coef else 1.0 # asigna valor al mapa
                break

    #arma el vector final
    for var in vars_orden:
        if coef_map[var] != 0.0: # verifica si la variable tiene un coeficiente asignado
            coeffs.append(coef_map[var]) # agrega el coeficiente al resultado final

    return coeffs


# detecta operador de restricción y devuelve los lados izquierdo y derecho
def _detectar_signo(texto: str) -> tuple[str, str, str]:
    for signo in ("<=", ">=", "=", "<", ">"):
        if signo in texto:
            izq, der = texto.split(signo, 1)
            return izq.strip(), der.strip(), signo
    raise ValueError("No se reconoció operador de restricción")


# descompone una restricción en coeficientes, lado derecho y signo
def parse_restriccion(
    texto: str, n_vars: Optional[int] = None
) -> tuple[list[float], float, str]:
    izq, der, signo = _detectar_signo(texto) # divide la restriccion en partes ( izq, der, signo)
    rhs = float(der.strip()) # convierte el lado derecho a float

    if "x" in izq.lower() or "y" in izq.lower(): # detecta el formato del lado izquierdo
        coeff = _parse_coeffs(izq) # si hay variables, parsea los coeficientes
    else:
        coeff = [float(x) for x in izq.split()] # si no hay, asume que son coef separados por espacios

    if n_vars and len(coeff) != n_vars: # manejo de erorres para verificar tamaño
        raise ValueError(f"Se esperaban {n_vars} coeficientes, got {len(coeff)}")

    tipo_map = {"<=": "<=", ">=": ">=", "=": "="} # mapea los signos 
    return (coeff, rhs, tipo_map.get(signo, "<=")) # retorna la restriccion parseada


# valida q la entrada no este vacia y parsea los coeficientes de la función objetivo
def parse_funcion_objetivo(texto: str, n_vars: int) -> list[float]:
    texto = texto.strip() #separa los coef por espacios y elimina estos
    if not texto:
        raise ValueError("Función objetivo vacía")

    if "x" in texto.lower():
        coeff = _parse_coeffs(texto) # si no hay var, parsea los coef 
    else:
        coeff = [float(x) for x in texto.split()] # si no hay var, asume que son coef separados por espacios

    if len(coeff) != n_vars: # manejo de errores para verificar tamaño
        raise ValueError(f"Se esperaban {n_vars} coeficientes, got {len(coeff)}")
    return coeff


# pide tipo de optimización (max/min)
def pedir_tipo() -> str:
    while True:
        tipo = input("Tipo de optimización (max/min): ").strip().lower()
        if tipo in ("max", "min"):
            return tipo
        print("Entrada inválida. Escribe 'max' o 'min'.")


# pide cantidad de variables de decisión
def pedir_num_vars() -> int:
    while True:
        try:
            n = int(input("Cantidad de variables de decisión: ").strip())
            if n > 0:
                return n
        except:
            pass
        print("Debe ser un entero positivo.")

# pide coeficientes de la función objetivo
def pedir_funcion_objetivo(n_vars: int) -> list[float]:
    ejemplo = " ".join(["a" + str(i + 1) for i in range(n_vars)])
    while True:
        texto = input(f"Coeficientes FO ({ejemplo}): ").strip()
        try:
            return parse_funcion_objetivo(texto, n_vars)
        except Exception as e:
            print(f"Formato inválido: {e}")


# pide cantidad de restricciones
def pedir_num_restricciones() -> int:
    while True:
        try:
            n = int(input("Cantidad de restricciones: ").strip())
            if n >= 0:
                return n
        except:
            pass
        print("Debe ser un entero >= 0.")


# segun n de restricciones, pide cada una
def pedir_restricciones(
    n_vars: int, n_restricciones: int
) -> list[tuple[list[float], float, str]]:
    ejemplo = f"a1 a2 ... a{n_vars} <= b"
    print(f"\nIngresa restricciones (ej: {ejemplo})")

    restricciones = []
    for i in range(n_restricciones):
        while True:
            try:
                r = parse_restriccion(input(f"restricción {i + 1}: "), n_vars)
                restricciones.append(r)
                break
            except Exception:
                print("Formato inválido. Intenta de nuevo.")
    return restricciones


# usa las otras funciones en orden para construir problema
def pedir_problema(
    modo: str = "simplex",
) -> tuple[str, list[float], list[tuple[list[float], float, str]]]:
    print("=== INPUT PROGRACIÓN LINEAL ===\n")

    if modo == "grafico":
        n_vars = 2
    else:
        n_vars = pedir_num_vars()

    fo = pedir_funcion_objetivo(n_vars)
    tipo = pedir_tipo()
    n_res = pedir_num_restricciones()
    restricciones = pedir_restricciones(n_vars, n_res)
    return (tipo, fo, restricciones)
