"""
Aqui se busca calcular la ruta óptima y la selección
del hospital adecuado.
"""

import numpy as np

from grafo import MinHeap, NodoHeap


def dijkstra_costo(grafo, nodo_origen):

    origenes = grafo.getOrigen()

    if nodo_origen not in origenes:
        raise KeyError(
            f"El nodo inicial {nodo_origen} no existe en el grafo"
        )

    padre = {}
    llave = {}
    visitado = {}

    for nodo in origenes:
        padre[nodo] = None
        llave[nodo] = np.inf
        visitado[nodo] = False

    llave[nodo_origen] = 0

    heap = MinHeap()

    heap.insertar(
        NodoHeap(nodo_origen, 0)
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
                and llave[u] + costo_arista < llave[vecino]
            ):

                llave[vecino] = (
                    llave[u] + costo_arista
                )

                padre[vecino] = u

                heap.insertar(
                    NodoHeap(
                        vecino,
                        llave[vecino]
                    )
                )

    return padre, llave


def reconstruir_ruta(
    padre,
    origen,
    destino
):

    ruta = []

    actual = destino

    while actual is not None:

        ruta.append(actual)

        actual = padre[actual]

    ruta.reverse()

    if len(ruta) == 0 or ruta[0] != origen:
        return []

    return ruta


def calcular_camas_disponibles(capacidades):

    capacidades = capacidades.copy()

    capacidades["camas_disponibles"] = (
        capacidades["camas_totales"]
        - capacidades["camas_ocupadas"]
    )

    return capacidades


def filtrar_hospitales_candidatos(
    capacidades,
    especialidad
):

    capacidades = calcular_camas_disponibles(
        capacidades
    )

    candidatos = capacidades[
        capacidades["especialidad"]
        == especialidad
    ].copy()

    candidatos = candidatos[
        candidatos["camas_disponibles"] > 0
    ]

    return candidatos


def buscar_hospital_adecuado(
    grafo,
    emergencia,
    capacidades
):

    especialidad = emergencia[
        "especialidad_requerida"
    ]

    nodo_origen = emergencia[
        "id_nodo_origen"
    ]

    candidatos = filtrar_hospitales_candidatos(
        capacidades,
        especialidad,
    )

    if candidatos.empty:
        return None

    padre, distancias = dijkstra_costo(
        grafo,
        nodo_origen,
    )

    mejor_hospital = None

    mejor_distancia = float("inf")

    for _, candidato in candidatos.iterrows():

        id_hospital = candidato[
            "id_hospital"
        ]

        if (
            id_hospital in distancias
            and distancias[id_hospital]
            < mejor_distancia
        ):

            mejor_distancia = (
                distancias[id_hospital]
            )

            mejor_hospital = candidato

    if mejor_hospital is None:
        return None

    ruta = reconstruir_ruta(
        padre,
        nodo_origen,
        mejor_hospital["id_hospital"],
    )

    return {

        "id_hospital":
            mejor_hospital["id_hospital"],

        "hospital":
            mejor_hospital["hospital"],

        "especialidad":
            especialidad,

        "camas_disponibles":
            mejor_hospital[
                "camas_disponibles"
            ],

        "costo_ruta":
            mejor_distancia,

        "ruta":
            ruta,
    }