from unittest import result

import matplotlib.pyplot as plt
import numpy as np

EPS = 1e-9  # 0.000000001 -> epsilon numerico para evitar errores de precision


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
    return abs(a1 * b2 - a2 * b1) < EPS


def calcular_interseccion(r1, r2):
    if son_paralelas(r1, r2):  # no calcular si ||
        return None

    (a1, b1, c1), (a2, b2, c2) = r1[:3], r2[:3]  # desempaquetar restriccion
    det = a1 * b2 - a2 * b1  # det
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
    all_vertices, factibles, checked = [], [], set()  # set para evitar duplicados
    hull = []  # region factible
    lineas = [(r[0], r[1], r[2]) for r in restricciones]  # extraer Ec.

    for i, l1 in enumerate(lineas):  # enumeracion index * recta
        for l2 in lineas[i + 1 :]:  # pares de rectas
            p = calcular_interseccion(l1, l2)  # interseccion entre l1 y l2

            if p is None:
                continue

            px, py = normalizar(p[0]), normalizar(p[1])  # normalizar coordenadas

            if (px, py) in checked:  # evitar duplicado
                continue

            # actualizacion
            checked.add((px, py))
            all_vertices.append((px, py))

            # verificar factibilidad
            if px >= -EPS and py >= -EPS and es_factible((px, py), restricciones):
                factibles.append((px, py))

                # recalcular el hull con el nuevo vertice
                hull = convex_hull(factibles)
    return all_vertices, factibles, hull


def evaluar_objetivo(vertices, a, b):  # evaluar Z con ciertos vertices
    return [(v, a * v[0] + b * v[1]) for v in vertices]  # retorna tuplas -> ((x,y), Z)


# solver
def resolver_PL(
    restricciones, a_obj, b_obj, tipo="max"
):  # a/b_obj son los coeficientes en Z

    all_vertices, vertices, hull = calcular_vertices(restricciones)  # obtencion
    resultados = evaluar_objetivo(vertices, a_obj, b_obj)  # evaluacion

    # caso infactible!!!
    if not resultados:
        return dict(
            estado="infactible",
            all_vertices=all_vertices,
            vertces_factibles=[],
            hull=[],
            optimo=None,
            valor_optimo=None,
            resultados=[],
            coeficientes=(a_obj, b_obj),
            tipo=tipo,
        )

    optimo = (  # emplear max o min
        max(resultados, key=lambda r: r[1])  # r[1] -> Z
        if tipo == "max"
        else min(resultados, key=lambda r: r[1])
    )

    # tetorno de diccionario completo
    return dict(
        estado="optimo",
        all_vertices=all_vertices,
        vertices_factibles=vertices,
        hull=hull,
        optimo=optimo,
        valor_optimo=optimo[1],
        resultados=resultados,
        coeficientes=(a_obj, b_obj),
        tipo=tipo,
    )


# VISUALIZACION


def calcular_limites(vertices, margen=2.0):
    if not vertices:  # fallback
        return -10, 10, -10, 10

    vx, vy = zip(*vertices)  # separacion de coordenadas

    # extremos
    xmin, xmax = min(vx) - margen, max(vx) + margen
    ymin, ymax = min(vy) - margen, max(vy) + margen

    # tamaño minimo -> 4
    xr, yr = max(xmax - xmin, 4.0), max(ymax - ymin, 4.0)
    # centro geometrico
    xm, ym = (xmin + xmax) / 2, (ymin + ymax) / 2
    return xm - xr / 2, xm + xr / 2, ym - yr / 2, ym + yr / 2  # limites finales


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

    ax.set_aspect("equal")  # ejes proporcionales

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
        if v == optimo[0]:
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

            if any(mask):
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
            f"Z = {z:.2f}",
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

    if solucion["estado"] == "infactible":
        print("no hay region factible en este caso")
        return

    fig, ax = plt.subplots(figsize=(12, 10))
    limites = calcular_limites(solucion["vertices_factibles"] or [(0, 0)])
    configurar_ejes(ax, limites)
    graficar_restricciones(ax, restricciones, limites)
    graficar_region(ax, solucion["hull"])
    graficar_vertices(
        ax, solucion["all_vertices"], solucion["vertices_factibles"], solucion["optimo"]
    )
    graficar_Z(
        ax,
        solucion["resultados"],
        *solucion["coeficientes"],
        limites,
        solucion["optimo"],
    )

    graficar_etiquetas(ax, solucion["resultados"], solucion["optimo"])
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    opt = solucion["optimo"][0]
    ax.set_title(
        f"Solución Óptima: ({opt[0]:.2f}, {opt[1]:.2f}) con Z = {solucion['valor_optimo']:.2f}",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )
    plt.tight_layout()
    plt.show()


# TEST
restricciones = [
    # EJES
    (1, 0, 0, ">="),
    (0, 1, 0, ">="),
    # RESTRICCIONES
    (1, 1, 10, "<="),
    (1.0000001, 1, 10, "<="),
    (1, 1, 6, "<="),
    (1, 1, 1, ">="),
]
solucion = resolver_PL(restricciones, a_obj=1, b_obj=1, tipo="max")  # Z
graficar(solucion, restricciones)


"""DEBE CONTENER INPUT NATURAL PARA PROBLEMAS DE PROGRAMACION LINEAL"""
