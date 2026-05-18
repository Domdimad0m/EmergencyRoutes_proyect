# visualizaciones.py

import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import LineString


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


def visualizar_ruta_dijkstra(
    resultado,
    grafo=None,
    nodos_viales=None,
    hospitales=None,
    hora=None,
):
    if resultado is None:
        print("No se puede visualizar la ruta porque no hay resultado.")
        return

    ruta = resultado["ruta"]

    G = nx.Graph()

    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i + 1]

        peso_arista = None

        if grafo is not None:
            datos_grafo = grafo.getOrigen()

            if origen in datos_grafo and destino in datos_grafo[origen]:
                peso = datos_grafo[origen][destino]

                if hora is not None:
                    columna_hora = f"peso_h{hora:02d}"

                    if columna_hora in peso:
                        peso_arista = peso[columna_hora]
                    else:
                        peso_arista = peso["costo"]
                else:
                    peso_arista = peso["costo"]

        if peso_arista is None:
            G.add_edge(origen, destino)
        else:
            G.add_edge(
                origen,
                destino,
                weight=round(peso_arista, 2),
            )

    posiciones = {}
    etiquetas = {}

    if nodos_viales is not None:
        for _, row in nodos_viales.iterrows():
            id_nodo = row["id_nodo"]

            if id_nodo in ruta:
                posiciones[id_nodo] = (
                    row["lon"],
                    row["lat"],
                )
                etiquetas[id_nodo] = id_nodo

    if hospitales is not None:
        for _, row in hospitales.iterrows():
            id_hospital = row["id_osm"]

            if id_hospital in ruta:
                posiciones[id_hospital] = (
                    row["lon"],
                    row["lat"],
                )
                etiquetas[id_hospital] = row["nombre"]

    usar_posiciones_reales = all(
        nodo in posiciones
        for nodo in ruta
    )

    if usar_posiciones_reales:
        pos = posiciones
    else:
        pos = nx.spring_layout(
            G,
            seed=42,
        )
        etiquetas = {
            nodo: nodo
            for nodo in G.nodes()
        }

    plt.figure(figsize=(12, 8))

    nx.draw(
        G,
        pos,
        with_labels=False,
        node_color="lightblue",
        edge_color="red",
        node_size=800,
        font_size=8,
    )

    nx.draw_networkx_labels(
        G,
        pos,
        labels=etiquetas,
        font_size=8,
    )

    edge_labels = nx.get_edge_attributes(
        G,
        "weight",
    )

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=7,
    )

    titulo = f'Ruta óptima hacia {resultado["hospital"]}'

    if hora is not None:
        titulo += f" - Hora {hora:02d}:00"

    plt.title(titulo)
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
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
    print("\nRESULTADO DIJKSTRA:")

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
    print("\nRESULTADO PRIM:")

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
                ),
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


def visualizar_grafo_trafico_por_hora(
    grafo,
    hora,
    nodos_viales=None,
    hospitales=None,
    mostrar_pesos=False,
):
    if hora < 0 or hora > 23:
        raise ValueError(
            "La hora debe estar entre 0 y 23"
        )

    columna_hora = f"peso_h{hora:02d}"

    G = nx.Graph()

    for origen in grafo.getOrigen():
        for destino, peso in grafo.getOrigen()[origen].items():
            if columna_hora in peso:
                costo = peso[columna_hora]
            else:
                costo = peso["costo"]

            G.add_edge(
                origen,
                destino,
                weight=round(costo, 2),
            )

    pos = nx.spring_layout(
        G,
        seed=42,
        k=0.35,
        iterations=100,
    )

    plt.figure(figsize=(14, 10))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=350,
        font_size=7,
        width=0.6,
    )

    if mostrar_pesos:
        for origen, destino, datos_arista in G.edges(data=True):
            if origen in pos and destino in pos:
                x1, y1 = pos[origen]
                x2, y2 = pos[destino]

                x_medio = (x1 + x2) / 2
                y_medio = (y1 + y2) / 2

                plt.text(
                    x_medio,
                    y_medio,
                    str(datos_arista["weight"]),
                    fontsize=6,
                    ha="center",
                    va="center",
                )

    plt.title(
        f"Grafo con tráfico - Hora {hora:02d}:00"
    )


    plt.show()


def visualizar_ruta_en_mapa_si(resultado, nodos_viales, hospitales=None):

    ruta = resultado["ruta"]

    nodos_ruta = nodos_viales[
        nodos_viales["id_nodo"].isin(ruta)
    ].copy()

    nodos_ruta["orden"] = nodos_ruta["id_nodo"].apply(
        lambda x: ruta.index(x)
    )

    nodos_ruta = nodos_ruta.sort_values("orden")

    gdf_puntos = gpd.GeoDataFrame(
        nodos_ruta,
        geometry=gpd.points_from_xy(
            nodos_ruta["longitud"],
            nodos_ruta["latitud"]
        ),
        crs="EPSG:4326"
    )

    linea = LineString(gdf_puntos.geometry.tolist())

    gdf_linea = gpd.GeoDataFrame(
        {"tipo": ["ruta"]},
        geometry=[linea],
        crs="EPSG:4326"
    )

    gdf_puntos = gdf_puntos.to_crs(epsg=3857)
    gdf_linea = gdf_linea.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(12, 12))

    gdf_linea.plot(
        ax=ax,
        linewidth=4,
        color="red",
        zorder=3
    )

    gdf_puntos.plot(
        ax=ax,
        markersize=35,
        color="yellow",
        edgecolor="black",
        zorder=4
    )

    xmin, ymin, xmax, ymax = gdf_linea.total_bounds
    ax.set_xlim(xmin - 1000, xmax + 1000)
    ax.set_ylim(ymin - 1000, ymax + 1000)

    ctx.add_basemap(
        ax,
        source=ctx.providers.CartoDB.Positron
    )

    ax.set_axis_off()
    ax.set_title("Ruta óptima sobre mapa real", fontsize=15)

    plt.show()