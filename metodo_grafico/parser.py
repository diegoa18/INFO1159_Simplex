from programacion_lineal import graficar, resolver_PL


def pedir_tipo():
    while True:
        tipo = input("Tipo de optimización (max/min): ").strip().lower()
        if tipo in ("max", "min"):
            return tipo
        print("entrada invalida. escribe 'max' o 'min'.")


def pedir_funcion_objetivo():
    while True:
        try:
            raw = input("Función objetivo (formato: a b para Z = ax + by): ")
            a, b = map(float, raw.strip().split())
            return a, b
        except:
            print("formato inválido. ejemplo valido: 3 5")


def pedir_num_restricciones():
    while True:
        try:
            n = int(input("cantidad de restricciones: "))
            if n >= 0:
                return n
        except:
            pass
        print("debe ser un entero ≥ 0.")


def parse_restriccion(texto):
    """
    Soporta dos formatos:
    1. Simbólico: "2x + 3y <= 10"
    2. Coeficientes: "2 3 <= 10"
    """
    texto = texto.strip()
    
    # Buscar signo de relacion
    signo = None
    for s in ("<=", ">=", "<", ">"):
        if s in texto:
            signo = s
            break
    
    if not signo:
        raise ValueError("no se encontró signo válido (<, >, <=, >=)")
    
    izq_str, der_str = texto.split(signo)
    izq_str = izq_str.strip()
    der_str = der_str.strip()
    
    try:
        c = float(der_str)
    except ValueError:
        raise ValueError(f"lado derecho inválido: '{der_str}' no es número")
    
    # Detectar formato: si hay 'x' o 'y', es simbólico; si solo números, es coeficientes
    if "x" in izq_str.lower() or "y" in izq_str.lower():
        # Formato simbólico: "2x + 3y"
        a, b = _parse_simbolico(izq_str)
    else:
        # Formato coeficientes: "2 3"
        a, b = _parse_coeficientes(izq_str)
    
    return (a, b, c, signo)


def _parse_coeficientes(texto):
    """
    Parsea formato: "a b" → (a, b)
    """
    partes = texto.split()
    if len(partes) != 2:
        raise ValueError(f"se esperaban 2 coeficientes, se recibieron {len(partes)}: '{texto}'")
    
    try:
        a = float(partes[0])
        b = float(partes[1])
    except ValueError as e:
        raise ValueError(f"coeficientes inválidos: {e}")
    
    return a, b


def _parse_simbolico(texto):
    """
    Parsea formato: "2x + 3y" o "x - 2y" etc → (a, b)
    """
    texto = texto.replace(" ", "").lower()
    texto = texto.replace("-", "+-")
    partes = [p for p in texto.split("+") if p]
    
    a, b = 0.0, 0.0
    
    for p in partes:
        if "x" in p:
            coef = p.replace("x", "")
            if coef in ("", "+"):
                a = 1.0
            elif coef == "-":
                a = -1.0
            else:
                a = float(coef)
        elif "y" in p:
            coef = p.replace("y", "")
            if coef in ("", "+"):
                b = 1.0
            elif coef == "-":
                b = -1.0
            else:
                b = float(coef)
    
    return a, b


def pedir_restricciones(n):
    restricciones = []

    print("\ningresa las restricciones (ej: 2x + 3y <= 10):")

    for i in range(n):
        while True:
            try:
                r = input(f"restricción {i + 1}: ")
                restricciones.append(parse_restriccion(r))
                break
            except Exception:
                print("formato invalido. intenta nuevamente.")

    return restricciones
