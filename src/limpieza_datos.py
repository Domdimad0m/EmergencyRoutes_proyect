# limpieza_datos.py

"""
Se preparan los CSVs para trabajar sobre los datos limpios
de los hospitales en Álvaro Obregón.

Se limpian los datos de los hospitales y se añaden datos
artificiales sobre especialidades y capacidad de camas.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import random
from math import radians, sin, cos, sqrt, atan2


def distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# Genera 24 pesos por hora para simular tráfico durante el día.
def generar_pesos_por_hora(
    distancia,
    highway=None,
):
    """
    Genera 24 pesos por hora para simular tráfico durante el día.

    Cada peso representa el costo de recorrer una arista en una hora específica.
    El costo base es la distancia y se multiplica por un factor de tráfico.

    El patrón de tráfico depende del tipo de vialidad.
    """

    if highway == "motorway":
        factores_trafico = [
            1.2, 1.2, 1.1, 1.1,
            1.3, 1.5, 1.8, 2.0,
            2.0, 1.8, 1.5, 1.4,
            1.5, 1.6, 1.7, 1.9,
            2.0, 2.0, 1.9, 1.7,
            1.5, 1.4, 1.3, 1.2,
        ]

    elif highway == "primary":
        factores_trafico = [
            1.1, 1.1, 1.1, 1.1,
            1.2, 1.3, 1.6, 1.8,
            1.7, 1.5, 1.3, 1.2,
            1.3, 1.4, 1.5, 1.7,
            1.9, 2.0, 1.8, 1.6,
            1.4, 1.3, 1.2, 1.1,
        ]

    elif highway == "secondary":
        factores_trafico = [
            1.0, 1.0, 1.0, 1.0,
            1.1, 1.2, 1.4, 1.6,
            1.5, 1.3, 1.2, 1.1,
            1.2, 1.3, 1.4, 1.5,
            1.7, 1.8, 1.6, 1.4,
            1.2, 1.1, 1.1, 1.0,
        ]

    else:
        factores_trafico = [
            1.0, 1.0, 1.0, 1.0,
            1.0, 1.1, 1.2, 1.3,
            1.3, 1.2, 1.1, 1.1,
            1.1, 1.2, 1.2, 1.3,
            1.4, 1.5, 1.4, 1.3,
            1.2, 1.1, 1.0, 1.0,
        ]

    pesos_por_hora = []

    for factor in factores_trafico:
        pesos_por_hora.append(
            round(distancia * factor, 3)
        )

    return pesos_por_hora


def cargar_hospitales(path_hospitales):
    gdf = gpd.read_file(path_hospitales)
    return gdf


def limpiar_hospitales(gdf):
    hospitales = gdf[
        [
            "id",
            "name",
            "healthcare:speciality",
            "emergency",
            "operator:short",
            "geometry",
        ]
    ].copy()

    hospitales["lat"] = hospitales.geometry.y
    hospitales["lon"] = hospitales.geometry.x

    hospitales = hospitales.rename(
        columns={
            "id": "id_osm",
            "name": "nombre",
            "healthcare:speciality": "especialidades_osm",
            "operator:short": "institucion",
            "emergency": "emergencias",
        }
    )

    hospitales = hospitales[
        [
            "id_osm",
            "nombre",
            "lat",
            "lon",
            "especialidades_osm",
            "emergencias",
            "institucion",
        ]
    ]

    return hospitales


def asignar_datos_artificiales_hospitales(hospitales):
    hospitales["emergencias"] = hospitales["emergencias"].fillna("yes")

    hospitales.loc[0, "especialidades_osm"] = "general;trauma;urgencias"

    hospitales.loc[1, "especialidades_osm"] = (
        "general;cardiologia;pediatria;ginecologia;emergencia;"
        "cirugia;cardiologia;oncologia;cardiologia;radiologia;"
        "intensivo;interno"
    )

    hospitales.loc[2, "especialidades_osm"] = "pediatria;urgencias;cirugia"
    hospitales.loc[3, "especialidades_osm"] = "general;trauma;neurologia;urgencias"
    hospitales.loc[4, "especialidades_osm"] = "general;cardiologia;radiologia;intensivo"
    hospitales.loc[5, "especialidades_osm"] = "pediatria;ginecologia;urgencias"
    hospitales.loc[6, "especialidades_osm"] = "general;cirugia;oncologia;radiologia"
    hospitales.loc[7, "especialidades_osm"] = "trauma;ortopedia;urgencias;cirugia"
    hospitales.loc[8, "especialidades_osm"] = "general;neurologia;cardiologia;intensivo"
    hospitales.loc[9, "especialidades_osm"] = "pediatria;general;urgencias;interno"
    hospitales.loc[10, "especialidades_osm"] = "general;ginecologia;maternidad;cirugia"
    hospitales.loc[11, "especialidades_osm"] = "trauma;urgencias;radiologia;intensivo"
    hospitales.loc[12, "especialidades_osm"] = "general;cardiologia;oncologia;neurologia"

    return hospitales


def generar_capacidades(hospitales):
    filas = []

    for _, row in hospitales.iterrows():
        especialidades = row["especialidades_osm"].split(";")

        for esp in especialidades:
            filas.append(
                {
                    "id_hospital": row["id_osm"],
                    "hospital": row["nombre"],
                    "especialidad": esp.strip(),
                    "camas_totales": random.randint(1, 15),
                    "camas_ocupadas": random.randint(0, 10),
                }
            )

    capacidades = pd.DataFrame(filas)

    return capacidades


def generar_nodos_hospitales(hospitales):
    nodos = hospitales[
        [
            "id_osm",
            "nombre",
            "lat",
            "lon",
        ]
    ].copy()

    nodos = nodos.rename(
        columns={
            "id_osm": "id_nodo",
            "nombre": "nombre_nodo",
        }
    )

    nodos["tipo"] = "hospital"

    return nodos


def cargar_vialidades(path_vialidades):
    vialidades = gpd.read_file(path_vialidades)
    vias = vialidades[vialidades["highway"].notna()].copy()

    return vias


def generar_nodos_y_rutas_viales(vias):
    nodos = []
    rutas = []

    for i, row in vias.iterrows():
        coords = list(row.geometry.coords)

        if len(coords) < 2:
            continue

        indices = np.linspace(
            0,
            len(coords) - 1,
            3,
            dtype=int,
        )

        ids_via = []

        for k, idx in enumerate(indices):
            lon, lat = coords[idx]
            id_nodo = f"V{i}_{k}"

            nodos.append(
                {
                    "id_nodo": id_nodo,
                    "nombre_nodo": row.get(
                        "name",
                        "vialidad_sin_nombre",
                    ),
                    "tipo": "vial",
                    "lat": lat,
                    "lon": lon,
                    "highway": row.get("highway"),
                }
            )

            ids_via.append(id_nodo)

        for a, b in zip(ids_via, ids_via[1:]):
            nodo_a = nodos[-3 + ids_via.index(a)]
            nodo_b = nodos[-3 + ids_via.index(b)]

            d = distancia_km(
                nodo_a["lat"],
                nodo_a["lon"],
                nodo_b["lat"],
                nodo_b["lon"],
            )

            pesos_por_hora = generar_pesos_por_hora(
                d,
                row.get("highway"),
            )

            fila_ruta = {
                "origen": a,
                "destino": b,
                "distancia_km": round(d, 3),
                "factor_trafico": 1.0,
                "peso": round(d, 3),
            }

            for hora in range(24):
                fila_ruta[f"peso_h{hora:02d}"] = pesos_por_hora[hora]

            rutas.append(fila_ruta)

    nodos_viales = pd.DataFrame(nodos)
    rutas_viales = pd.DataFrame(rutas)

    return nodos_viales, rutas_viales


def generar_emergencias(nodos_viales):
    nodos_emergencia = nodos_viales.sample(
        n=9,
        random_state=42,
    ).copy()

    especialidades = [
        "urgencias",
        "trauma",
        "cardiologia",
        "urgencias",
        "trauma",
        "cardiologia",
        "urgencias",
        "trauma",
        "cardiologia",
    ]

    prioridades = [
        "ROJO",
        "AMARILLO",
        "VERDE",
        "ROJO",
        "VERDE",
        "AMARILLO",
        "AMARILLO",
        "ROJO",
        "VERDE",
    ]

    emergencias = pd.DataFrame(
        {
            "id_emergencia": [
                f"E{i + 1:02d}"
                for i in range(len(nodos_emergencia))
            ],
            "id_nodo_origen": nodos_emergencia["id_nodo"].values,
            "nombre_origen": nodos_emergencia["nombre_nodo"].values,
            "lat": nodos_emergencia["lat"].values,
            "lon": nodos_emergencia["lon"].values,
            "especialidad_requerida": especialidades,
            "prioridad": prioridades,
        }
    )

    return emergencias


def guardar_archivos_limpieza(
    hospitales,
    capacidades,
    nodos_hospitales,
    nodos_viales,
    rutas_viales,
    emergencias,
    output_dir="datos",
):
    hospitales.to_csv(
        f"{output_dir}/hospitales_limpio.csv",
        index=False,
    )

    hospitales.to_excel(
        f"{output_dir}/hospitales_limpio.xlsx",
        index=False,
    )

    capacidades.to_csv(
        f"{output_dir}/capacidades.csv",
        index=False,
    )

    capacidades.to_excel(
        f"{output_dir}/capacidades.xlsx",
        index=False,
    )

    nodos_hospitales.to_csv(
        f"{output_dir}/nodos.csv",
        index=False,
    )

    nodos_hospitales.to_excel(
        f"{output_dir}/nodos.xlsx",
        index=False,
    )

    nodos_viales.to_csv(
        f"{output_dir}/nodos_viales.csv",
        index=False,
    )

    rutas_viales.to_csv(
        f"{output_dir}/rutas_viales.csv",
        index=False,
    )

    emergencias.to_csv(
        f"{output_dir}/emergencias.csv",
        index=False,
    )

    emergencias.to_excel(
        f"{output_dir}/emergencias.xlsx",
        index=False,
    )


def ejecutar_limpieza(
    path_hospitales="datos/hospitales.geojson",
    path_vialidades="datos/vialidades.geojson",
    output_dir="datos",
):
    gdf_hospitales = cargar_hospitales(
        path_hospitales
    )

    hospitales = limpiar_hospitales(
        gdf_hospitales
    )

    hospitales = asignar_datos_artificiales_hospitales(
        hospitales
    )

    capacidades = generar_capacidades(
        hospitales
    )

    nodos_hospitales = generar_nodos_hospitales(
        hospitales
    )

    vias = cargar_vialidades(
        path_vialidades
    )

    nodos_viales, rutas_viales = generar_nodos_y_rutas_viales(
        vias
    )

    emergencias = generar_emergencias(
        nodos_viales
    )

    guardar_archivos_limpieza(
        hospitales,
        capacidades,
        nodos_hospitales,
        nodos_viales,
        rutas_viales,
        emergencias,
        output_dir,
    )

    return {
        "hospitales": hospitales,
        "capacidades": capacidades,
        "nodos_hospitales": nodos_hospitales,
        "nodos_viales": nodos_viales,
        "rutas_viales": rutas_viales,
        "emergencias": emergencias,
    }