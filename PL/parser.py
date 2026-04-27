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
    texto = texto.replace(" ", "").lower()

    for signo in ("<=", ">=", "<", ">"):
        if signo in texto:
            izq, der = texto.split(signo)
            c = float(der)

            izq = izq.replace("-", "+-")
            partes = [p for p in izq.split("+") if p]
            a, b = 0.0, 0.0

            for p in partes:
                if "x" in p:
                    coef = p.replace("x", "")
                    a = float(coef) if coef not in ("", "+") else 1.0
                    if coef == "-":
                        a = -1.0
                elif "y" in p:
                    coef = p.replace("y", "")
                    b = float(coef) if coef not in ("", "+") else 1.0
                    if coef == "-":
                        b = -1.0

            return (a, b, c, signo)

    raise ValueError("no se encontró signo válido")


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
