# visualizaciones.py

import matplotlib.pyplot as plt
import networkx as nx


def visualizar_grafo_completo(rutas_completas):
    G = nx.Graph()

    for _, ruta in rutas_completas.iterrows():
        G.add_edge(
            ruta["origen"],
            ruta["destino"],
            weight=ruta["peso"],
        )

    plt.figure(figsize=(12, 10))

    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=False,
        node_size=15,
        font_size=8,
    )

    plt.title("Grafo completo de rutas")
    plt.show()


def visualizar_ruta_dijkstra(resultado):
    if resultado is None:
        print("No se puede visualizar la ruta porque no hay resultado.")
        return

    G = nx.Graph()

    ruta = resultado["ruta"]

    for i in range(len(ruta) - 1):
        G.add_edge(
            ruta[i],
            ruta[i + 1],
        )

    plt.figure(figsize=(10, 8))

    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="red",
        node_size=1000,
        font_size=8,
    )

    plt.title(
        f'Ruta óptima hacia {resultado["hospital"]}'
    )

    plt.show()


def visualizar_mst(aristas_mst):
    G = nx.Graph()

    for _, arista in aristas_mst.iterrows():
        G.add_edge(
            arista["origen"],
            arista["destino"],
            weight=arista["costo"],
        )

    plt.figure(figsize=(10, 8))

    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightgreen",
        edge_color="blue",
        node_size=1000,
        font_size=8,
    )

    labels = nx.get_edge_attributes(
        G,
        "weight",
    )

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=labels,
        font_size=7,
    )

    plt.title("Árbol de expansión mínima - Prim")
    plt.show()


def visualizar_hospitales_cercanos(
    hospitales_cercanos,
    emergencia,
):
    plt.figure(figsize=(10, 8))

    plt.scatter(
        emergencia["lon"],
        emergencia["lat"],
        color="red",
        s=150,
        label="Emergencia",
    )

    for hospital in hospitales_cercanos:
        datos = hospital["datos_hospital"]

        plt.scatter(
            datos["lon"],
            datos["lat"],
            color="blue",
            s=100,
        )

        plt.text(
            datos["lon"],
            datos["lat"],
            datos["nombre"],
            fontsize=8,
        )

    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.title("Hospitales dentro del radio")
    plt.legend()
    plt.show()


def imprimir_resultado_dijkstra(resultado):
    print("\n===== RESULTADO DIJKSTRA =====")

    if resultado is None:
        print("No se encontró hospital adecuado")
        return

    print(f'Hospital: {resultado["hospital"]}')
    print(f'Especialidad: {resultado["especialidad"]}')

    print(
        f'Camas disponibles: '
        f'{resultado["camas_disponibles"]}'
    )

    print(
        f'Costo de ruta: '
        f'{round(resultado["costo_ruta"], 3)}'
    )

    print("Ruta:")

    for nodo in resultado["ruta"]:
        print(f" -> {nodo}")


def imprimir_resultado_prim(resultado_prim):
    print("\n===== RESULTADO PRIM =====")

    print(
        f'Costo total MST: '
        f'{round(resultado_prim["costo_total"], 3)}'
    )

    print("\nAristas MST:")
    print(resultado_prim["aristas_mst"])

def visualizar_grafo_rutas_hospitalarias(grafo):
    G = nx.Graph()
    for origen in grafo.getOrigen():
        for destino, peso in grafo.getOrigen()[origen].items():
            G.add_edge(
                origen,
                destino,
                weight=round(
                    peso["costo"],
                    2,
                )
            )
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(
        G,
        seed=42,
    )

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=500,
        font_size=8,
    )

    labels = nx.get_edge_attributes(
        G,
        "weight",
    )

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=labels,
        font_size=7,
    )
    plt.title("Grafo de rutas hospitalarias")
    plt.show()

def visualizar_grafo_hospitales_completo(grafo_hospitales, hospitales):
    G_hospitales = nx.Graph()

    posiciones = {}

    for _, row in hospitales.iterrows():
        id_hospital = row["id_osm"]
        nombre = row["nombre"]

        G_hospitales.add_node(
            id_hospital,
            label=nombre,
        )

        posiciones[id_hospital] = (
            row["lon"],
            row["lat"],
        )

    for origen in grafo_hospitales.getOrigen():
        for destino, peso in grafo_hospitales.getOrigen()[origen].items():
            G_hospitales.add_edge(
                origen,
                destino,
                weight=round(
                    peso["costo"],
                    2,
                ),
            )

    plt.figure(figsize=(12, 8))

    nx.draw(
        G_hospitales,
        posiciones,
        with_labels=False,
        node_size=400,
    )

    labels = nx.get_node_attributes(
        G_hospitales,
        "label",
    )

    nx.draw_networkx_labels(
        G_hospitales,
        posiciones,
        labels=labels,
        font_size=7,
    )

    edge_labels = nx.get_edge_attributes(
        G_hospitales,
        "weight",
    )

    nx.draw_networkx_edge_labels(
        G_hospitales,
        posiciones,
        edge_labels=edge_labels,
        font_size=7,
    )

    plt.title("Grafo completo entre hospitales")
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.show()

def visualizar_mst_geografico(
    padre,
    llave,
    hospitales,
):
    G_mst = nx.Graph()

    posiciones = {}

    for _, row in hospitales.iterrows():

        id_hospital = row["id_osm"]

        posiciones[id_hospital] = (
            row["lon"],
            row["lat"],
        )

        G_mst.add_node(
            id_hospital,
            label=row["nombre"],
        )

    for hijo, papa in padre.items():

        if papa is not None:

            costo = llave[hijo]

            G_mst.add_edge(
                papa,
                hijo,
                weight=round(
                    costo,
                    2,
                ),
            )

    plt.figure(figsize=(12, 8))

    nx.draw(
        G_mst,
        posiciones,
        with_labels=False,
        node_size=500,
    )

    labels = nx.get_node_attributes(
        G_mst,
        "label",
    )

    nx.draw_networkx_labels(
        G_mst,
        posiciones,
        labels=labels,
        font_size=7,
    )

    edge_labels = nx.get_edge_attributes(
        G_mst,
        "weight",
    )

    nx.draw_networkx_edge_labels(
        G_mst,
        posiciones,
        edge_labels=edge_labels,
        font_size=7,
    )

    plt.title(
        "Árbol de expansión mínima con Prim"
    )

    plt.xlabel("Longitud")
    plt.ylabel("Latitud")

    plt.show()