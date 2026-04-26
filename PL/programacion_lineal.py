from unittest import result

import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm

EPS = 1e-9  # 0.000000001 -> epsilon numerico para evitar errores de precision
EPS_PAR = 1e-7


def normalizar(valor):  # redondear a 0 o a 6 decimales
    return 0.0 if abs(valor) < EPS else round(valor, 6)


def es_eje(r):
    a, b, c, _ = r
    return abs(c) < EPS and (
        abs(a) < EPS or abs(b) < EPS
    )  # es decir si a=0 o b=0 si c=0


def parse_num(x):
    # parse para visualizacion sin decimales en las restricciones si es necessario como 3.0 -> 3
    return f"{x:.1f}" if x != int(x) else f"{int(x)}"


def son_paralelas(r1, r2):
    # [:2] para ignorar c y asi sacar determinante con (an,bn), si det = 0 -> ||
    (a1, b1), (a2, b2) = r1[:2], r2[:2]
    return abs(a1 * b2 - a2 * b1) < EPS_PAR


def calcular_interseccion(r1, r2):
    if son_paralelas(r1, r2):  # no calcular si ||
        return None

    (a1, b1, c1), (a2, b2, c2) = r1[:3], r2[:3]  # desempaquetar restriccion
    det = a1 * b2 - a2 * b1  # det

    if abs(det) < EPS:
        return None

    return (
        (c1 * b2 - c2 * b1) / det,
        (a1 * c2 - a2 * c1) / det,
    )  # obtener tupla de interseccion


# origen -> a -> b | orientacion de giro y mantener un sentido
def orientacion(origen, a, b):
    return (a[0] - origen[0]) * (b[1] - origen[1]) - (a[1] - origen[1]) * (
        b[0] - origen[0]
    )  # positivo -> izquierda


def convex_hull(puntos):
    if len(puntos) < 3:  # caso trivial
        return list(puntos)

    pts = sorted(puntos)  # orden lexicografico (x,y)
    lower, upper = [], []  # lower = parte inferior del poligono, upper = superior

    # almenos 2 anteriores y determinar orientacion
    for p in pts:
        while len(lower) >= 2 and orientacion(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and orientacion(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # ambos lados eliminando lo extremos para evitar duplicados
    return lower[:-1] + upper[:-1]


# diccionario de funciones para interpretar inecuaciones
# a c se le opera con EPS dependiendo de la inecuancion en casos donde v == c pero de false erroneamente por floats
CUMPLE = {
    "<=": lambda v, c: v <= c + EPS,
    ">=": lambda v, c: v >= c - EPS,
    "<": lambda v, c: v < c - EPS,
    ">": lambda v, c: v > c + EPS,
}


def cumple_restriccion(punto, restriccion):
    x, y = punto
    a, b, c, signo = restriccion
    # ssi no existe operador -> false, si no cumple la operacion -> falsex
    return CUMPLE.get(signo, lambda v, c: False)(a * x + b * y, c)


def es_factible(punto, restricciones):
    return all(cumple_restriccion(punto, r) for r in restricciones)


def calcular_vertices(restricciones):
    all_v, factibles, seen = [], [], set()
    hull = []
    lineas = [(a, b, c) for a, b, c, _ in restricciones]

    for i, l1 in enumerate(lineas):
        for l2 in lineas[i + 1 :]:
            p = calcular_interseccion(l1, l2)
            if p is None:
                continue

            px, py = map(normalizar, p)
            key = (round(px, 6), round(py, 6))

            if key in seen:
                continue

            seen.add(key)
            all_v.append((px, py))

            if es_factible((px, py), restricciones):
                factibles.append((px, py))
                hull = (
                    convex_hull(factibles) if len(factibles) >= 3 else factibles.copy()
                )

    return all_v, factibles, hull


def evaluar_objetivo(vertices, a, b):  # evaluar Z con ciertos vertices
    return [(v, a * v[0] + b * v[1]) for v in vertices]  # retorna tuplas -> ((x,y), Z)


def no_acotado(hull, a, b):
    if len(hull) < 3:
        return True

    d = np.array([a, b], float)
    d /= norm(d) + EPS

    for p1, p2 in zip(hull, hull[1:] + [hull[0]]):
        edge = np.subtract(p2, p1)
        normal = np.array([-edge[1], edge[0]])
        normal /= norm(normal) + EPS

        if np.dot(normal, d) > EPS:
            return False

    return True


def clasificar_hull(hull, a_obj, b_obj):
    n = len(hull)

    if n == 0:
        return "infactible"

    if abs(a_obj) < EPS and abs(b_obj) < EPS:
        raise ValueError("Función objetivo inválida")

    if n < 3:
        return {
            1: "optimo_degenerado_punto",
            2: "optimo_degenerado_segmento",
        }[n]

    area = abs(
        sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(hull, hull[1:] + [hull[0]]))
    )
    if area < EPS:
        return "degenerado"

    if no_acotado(hull, a_obj, b_obj):
        return "no_acotado"

    return "optimo"


# solver
def resolver_PL(restricciones, a_obj, b_obj, tipo="max"):
    all_v, _, hull = calcular_vertices(restricciones)
    resultados = evaluar_objetivo(hull, a_obj, b_obj)
    estado = clasificar_hull(hull, a_obj, b_obj)

    sol = {
        "estado": estado,
        "all_vertices": all_v,
        "vertices_factibles": hull,
        "hull": hull,
        "resultados": resultados,
        "coeficientes": (a_obj, b_obj),
        "tipo": tipo,
        "optimo": None,
        "valor_optimo": None,
    }

    if estado == "optimo":
        opt = (
            max(resultados, key=lambda r: r[1])
            if tipo == "max"
            else min(resultados, key=lambda r: r[1])
        )
        sol["optimo"] = opt
        sol["valor_optimo"] = opt[1]

    return sol


MENSAJES_ESTADO = {
    "infactible": "No hay región factible",
    "no_acotado": "Problema no acotado",
    "optimo_degenerado_punto": "Óptimo degenerado (punto)",
    "optimo_degenerado_segmento": "Óptimo degenerado (segmento)",
    "degenerado": "Región degenerada (área ~ 0)",
}


def manejar_estado(solucion):
    estado = solucion["estado"]

    if estado != "optimo":
        msg = MENSAJES_ESTADO.get(estado, f"Estado no manejado: {estado}")
        print(msg)
        return False

    return True


# VISUALIZACION


def fmt_num(x, sci_thresh=1e4):
    if x == 0:
        return "0"

    ax = abs(x)

    if ax >= sci_thresh or ax <= 1e-4:
        return f"{x:.2e}"
    elif abs(x - int(x)) < EPS:
        return f"{int(x)}"
    else:
        return f"{x:.2f}"


def fmt_objetivo(a, b):
    terms = []

    for coef, var in ((a, "x"), (b, "y")):
        if abs(coef) < EPS:
            continue

        s = fmt_num(abs(coef)) + var

        if not terms:
            terms.append(s if coef > 0 else f"-{s}")
        else:
            terms.append(f"+ {s}" if coef > 0 else f"- {s}")

    return " ".join(terms) if terms else "0"


def construir_titulo(solucion):
    (x, y), z = solucion["optimo"]
    a, b = solucion["coeficientes"]

    expr = fmt_objetivo(a, b)

    return f"Z = {expr}  |  en ({fmt_num(x)}, {fmt_num(y)}) → Z = {fmt_num(z)}"


def calcular_limites(vertices, margen_rel=0.05):
    if not vertices:
        return -10, 10, -10, 10

    vx, vy = zip(*vertices)

    xmin, xmax = min(vx), max(vx)
    ymin, ymax = min(vy), max(vy)

    dx = xmax - xmin
    dy = ymax - ymin

    dx = dx or max(abs(xmax), 1.0)
    dy = dy or max(abs(ymax), 1.0)

    mx = dx * margen_rel
    my = dy * margen_rel

    return xmin - mx, xmax + mx, ymin - my, ymax + my


def puntos_recta(r, xmin, xmax, ymin, ymax):
    a, b, c, _ = r  # r -> recta

    if abs(b) < EPS:
        return [
            (c / a, y) for y in np.linspace(ymin, ymax, 3)
        ]  # verticalidad, con 3 puntos es suficiente

    xs = np.linspace(xmin, xmax, 400)  # 400 equiespaciados
    ys = (c - a * xs) / b  # y

    return list(
        zip(xs[np.isfinite(ys)], ys[np.isfinite(ys)])
    )  # pares (eliminando valores invalidos)


def formatear_restriccion(r):
    a, b, c, signo = r
    return f"{parse_num(a)}x {'+' if b >= 0 else '-'}{parse_num(abs(b))}y {signo} {parse_num(c)}"


def configurar_ejes(ax, limites):  # limites -> (xmin, xmax, ymin, ymax)
    ax.set_xlim(limites[:2])
    ax.set_ylim(limites[2:])

    ax.set_aspect("auto")

    ax.ticklabel_format(style="sci", axis="both", scilimits=(0, 0))

    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_xlabel("x", fontsize=11)
    ax.set_ylabel("y", fontsize=11)


def graficar_restricciones(ax, restricciones, limites):
    cmap = plt.colormaps["tab10"]

    for idx, r in enumerate(restricciones):
        pts = puntos_recta(
            r, *limites
        )  # *limites desempaqueta (xmin, xmax, ymin, ymax)

        if not pts:
            continue

        xs, ys = zip(*pts)  # separacion x e y

        kw = (  # dibujado
            dict(color="black", linewidth=2.5, alpha=0.9)
            if es_eje(r)
            else dict(
                color=cmap(idx % 10),
                linestyle="--",
                linewidth=1.5,
                alpha=0.8,
                label=formatear_restriccion(r),
            )
        )
        ax.plot(xs, ys, **kw)


def graficar_region(ax, hull):
    if len(hull) < 3:  # base 3
        return

    hx, hy = zip(*(hull + [hull[0]]))  # sellado de poligono

    ax.fill(hx, hy, color="lightgreen", alpha=0.3, zorder=1)  # area

    ax.plot(  # borde
        hx,
        hy,
        color="green",
        linewidth=2.5,
        alpha=0.9,
        zorder=2,
        label="Región Factible",
    )


def graficar_vertices(ax, all_v, factibles_v, optimo):  # puntos clave
    factibles_set = set(factibles_v)

    no_factibles = [v for v in all_v if v not in factibles_set]  # no factibles

    if no_factibles:  # no factible
        vx, vy = zip(*no_factibles)
        ax.scatter(
            vx, vy, c="gray", s=50, alpha=0.8, zorder=3, label="Vértices no factibles"
        )

    for v in factibles_v:  # optimo
        if optimo is not None and v == optimo[0]:
            ax.scatter(
                *v,
                c="gold",
                s=300,
                zorder=8,
                edgecolors="orange",
                linewidths=2,
                marker="*",
                label="Óptimo",
            )

        else:  # factibles
            ax.scatter(*v, c="red", s=80, zorder=5, edgecolors="darkred")


def graficar_Z(ax, resultados, a, b, limites, optimo):

    xmin, xmax, ymin, ymax = limites

    x_vals = np.linspace(xmin, xmax, 200)

    for v, z in resultados:
        es_opt = v == optimo[0]
        color, lw, alpha, ls = (
            ("blue", 2.5, 1.0, "-") if es_opt else ("steelblue", 1.2, 0.4, "--")
        )
        zorder = 6 if es_opt else 4

        if abs(b) > EPS:
            y_vals = (z - a * x_vals) / b
            # evitar dibujar lineas gigantes
            mask = (y_vals >= ymin - 1) & (y_vals <= ymax + 1)

            if mask.any():
                ax.plot(
                    x_vals[mask],
                    y_vals[mask],
                    color=color,
                    lw=lw,
                    alpha=alpha,
                    ls=ls,
                    zorder=zorder,
                )
        else:
            ax.plot(
                [z / a] * 2,
                [ymin, ymax],
                color=color,
                lw=lw,
                alpha=alpha,
                ls=ls,
                zorder=zorder,
            )


def graficar_etiquetas(ax, resultados, optimo):
    for v, z in resultados:
        es_opt = v == optimo[0]
        ax.annotate(
            f"Z = {fmt_num(z)}",
            v,
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=9 if es_opt else 8,
            color="darkgreen" if es_opt else "dimgray",
            fontweight="bold" if es_opt else "normal",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7),
            zorder=7,
        )


def graficar(solucion, restricciones):

    if not manejar_estado(solucion):
        return

    fig, ax = plt.subplots(figsize=(12, 10))

    hull = solucion["hull"]
    limites = calcular_limites(hull or [(0, 0)])

    configurar_ejes(ax, limites)
    graficar_restricciones(ax, restricciones, limites)
    graficar_region(ax, hull)

    optimo = solucion["optimo"]

    graficar_vertices(
        ax,
        solucion["all_vertices"],
        solucion["vertices_factibles"],
        optimo,
    )

    if optimo:
        graficar_Z(
            ax,
            solucion["resultados"],
            *solucion["coeficientes"],
            limites,
            optimo,
        )
        graficar_etiquetas(ax, solucion["resultados"], optimo)
        titulo = construir_titulo(solucion)
    else:
        titulo = "Problema no acotado"

    ax.set_title(titulo, fontsize=14, fontweight="bold", pad=12)

    loc = "best" if len(hull) > 3 else "upper right"
    ax.legend(loc=loc, fontsize=9, framealpha=0.9).set_zorder(100)

    plt.tight_layout()
    plt.show()


# restricciones = [
#    (1, 0, 0, ">="),
#    (0, 1, 0, ">="),
#    (1, 1, 10, "<="),
#    (1, 1, 10, ">="),  # colapsa a una recta
# ]

# solucion = resolver_PL(restricciones, a_obj=1, b_obj=1, tipo="max")
# graficar(solucion, restricciones)


"""DEBE CONTENER INPUT NATURAL PARA PROBLEMAS DE PROGRAMACION wswsLINEAL"""
