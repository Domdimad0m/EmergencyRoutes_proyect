import numpy as np
import pandas as pd

from grafo import Grafo, MinHeap, NodoHeap
from conexiones_grafo import distancia_km


def construir_grafo_hospitales(hospitales, k=3):
    grafo_hospitales = Grafo()

    for _, origen in hospitales.iterrows():
        distancias = []

        for _, destino in hospitales.iterrows():
            if origen["id_osm"] != destino["id_osm"]:
                d = distancia_km(
                    origen["lat"],
                    origen["lon"],
                    destino["lat"],
                    destino["lon"],
                )

                distancias.append(
                    (
                        destino["id_osm"],
                        d,
                    )
                )

        cercanos = sorted(
            distancias,
            key=lambda x: x[1],
        )[:k]

        for id_destino, d in cercanos:
            peso = {
                "distancia": round(d, 3),
                "trafico": 1.0,
                "costo": round(d, 3),
            }

            grafo_hospitales.inserta_no_dirigido(
                origen["id_osm"],
                id_destino,
                peso,
            )

    return grafo_hospitales


def prim_costo(grafo, nodo_inicio):
    origenes = grafo.getOrigen()

    padre = {}
    llave = {}
    visitado = {}

    for nodo in origenes:
        padre[nodo] = None
        llave[nodo] = np.inf
        visitado[nodo] = False

    llave[nodo_inicio] = 0

    heap = MinHeap()

    heap.insertar(
        NodoHeap(nodo_inicio, 0)
    )

    while not heap.estaVacio():
        actual = heap.eliminarMinimo()
        u = actual.nodo

        if visitado[u]:
            continue

        visitado[u] = True

        for vecino, peso in origenes[u].items():
            costo_arista = peso["costo"]

            if (
                not visitado[vecino]
                and costo_arista < llave[vecino]
            ):
                llave[vecino] = costo_arista
                padre[vecino] = u

                heap.insertar(
                    NodoHeap(
                        vecino,
                        llave[vecino],
                    )
                )

    return padre, llave


def calcular_costo_total_mst(llave):
    total = 0

    for valor in llave.values():
        if valor != np.inf:
            total += valor

    return total


def obtener_aristas_mst(padre, llave):
    aristas = []

    for nodo in padre:
        if padre[nodo] is not None:
            aristas.append(
                {
                    "origen": padre[nodo],
                    "destino": nodo,
                    "costo": llave[nodo],
                }
            )

    return pd.DataFrame(aristas)


def ejecutar_prim(hospitales, k=3):
    grafo_hospitales = construir_grafo_hospitales(
        hospitales,
        k=k,
    )

    nodo_inicio = hospitales.iloc[0]["id_osm"]

    padre, llave = prim_costo(
        grafo_hospitales,
        nodo_inicio,
    )

    costo_total = calcular_costo_total_mst(
        llave
    )

    aristas_mst = obtener_aristas_mst(
        padre,
        llave,
    )

    return {
        "grafo_hospitales": grafo_hospitales,
        "padre": padre,
        "llave": llave,
        "costo_total": costo_total,
        "aristas_mst": aristas_mst,
    }