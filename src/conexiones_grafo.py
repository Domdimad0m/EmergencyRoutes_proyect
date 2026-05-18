import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# Función para calcular distancia entre coordenadas (considerando Harvine pues no estamos sobre un plano)

def distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Genera una lista de pesos para cada hora del día, dado una distancia base
def generar_pesos_por_hora(
    distancia,
    highway=None,
):
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


def obtener_highway_nodo(nodos_viales, id_nodo):
    coincidencias = nodos_viales[
        nodos_viales["id_nodo"] == id_nodo
    ]

    if coincidencias.empty:
        return None

    return coincidencias.iloc[0].get("highway")

def cargar_datos_conexiones(
    hospitales_path="datos/hospitales_limpio.csv",
    nodos_viales_path="datos/nodos_viales.csv",
    rutas_viales_path="datos/rutas_viales.csv",
):

    hospitales = pd.read_csv(hospitales_path)
    nodos_viales = pd.read_csv(nodos_viales_path)
    rutas_viales = pd.read_csv(rutas_viales_path)

    return hospitales, nodos_viales, rutas_viales

def conectar_hospitales_a_vialidades(hospitales, nodos_viales, k=3):

    conexiones_hospitales = []

    for _, hospital in hospitales.iterrows():
        distancias = []

        for _, nodo in nodos_viales.iterrows():
            d = distancia_km(
                hospital["lat"],
                hospital["lon"],
                nodo["lat"],
                nodo["lon"],
            )

            distancias.append((nodo["id_nodo"], d))
        cercanos = sorted(distancias, key=lambda x: x[1])[:k]

        for id_nodo, d in cercanos:
            highway = obtener_highway_nodo(
                nodos_viales,
                id_nodo,
            )

            pesos_por_hora = generar_pesos_por_hora(
                d,
                highway,
            )

            fila_ruta = {
                "origen": hospital["id_osm"],
                "destino": id_nodo,
                "distancia_km": round(d, 3),
                "factor_trafico": 1.0,
                "peso": round(d, 3),
                "tipo_ruta": "hospital-vial",
            }

            for hora in range(24):
                fila_ruta[f"peso_h{hora:02d}"] = pesos_por_hora[hora]

            conexiones_hospitales.append(fila_ruta)

    conexiones_hospitales = pd.DataFrame(conexiones_hospitales)

    return conexiones_hospitales

def conectar_nodos_viales_cercanos(nodos_viales, k=8):
    nuevas_rutas = []

    for _, origen in nodos_viales.iterrows():
        distancias = []

        for _, destino in nodos_viales.iterrows():
            if origen["id_nodo"] != destino["id_nodo"]:
                d = distancia_km(
                    origen["lat"],
                    origen["lon"],
                    destino["lat"],
                    destino["lon"],
                )

                distancias.append((destino["id_nodo"], d))
        cercanos = sorted(distancias, key=lambda x: x[1])[:k]

        for id_destino, d in cercanos:
            highway = origen.get("highway")

            pesos_por_hora = generar_pesos_por_hora(
                d,
                highway,
            )

            fila_ruta = {
                "origen": origen["id_nodo"],
                "destino": id_destino,
                "distancia_km": round(d, 3),
                "factor_trafico": 1.0,
                "peso": round(d, 3),
                "tipo_ruta": "conexion-vial-cercana",
            }

            for hora in range(24):
                fila_ruta[f"peso_h{hora:02d}"] = pesos_por_hora[hora]

            nuevas_rutas.append(fila_ruta)

    rutas_extra = pd.DataFrame(nuevas_rutas)

    return rutas_extra

def agregar_tipos_ruta(rutas_viales, conexiones_hospitales):
    
    rutas_viales = rutas_viales.copy()
    conexiones_hospitales = conexiones_hospitales.copy()
    rutas_viales["tipo_ruta"] = "vial-vial"
    conexiones_hospitales["tipo_ruta"] = "hospital-vial"

    return rutas_viales, conexiones_hospitales

def construir_rutas_completas(rutas_viales, conexiones_hospitales, rutas_extra):

    rutas_completas = pd.concat(
        [
            rutas_viales,
            conexiones_hospitales,
            rutas_extra,
        ],
        ignore_index=True,
    )

    return rutas_completas

def guardar_rutas_completas(rutas_completas, output_dir="datos"):

    rutas_completas.to_csv(f"{output_dir}/rutas_completas.csv", index=False)
    rutas_completas.to_excel(f"{output_dir}/rutas_completas.xlsx", index=False)


def ejecutar_conexiones(
    hospitales_path="datos/hospitales_limpio.csv",
    nodos_viales_path="datos/nodos_viales.csv",
    rutas_viales_path="datos/rutas_viales.csv",
    output_dir="datos",
    k_hospitales=3,
    k_viales=50,
):

    hospitales, nodos_viales, rutas_viales = cargar_datos_conexiones(
        hospitales_path,
        nodos_viales_path,
        rutas_viales_path,
    )

    conexiones_hospitales = conectar_hospitales_a_vialidades(
        hospitales,
        nodos_viales,
        k=k_hospitales,
    )

    rutas_extra = conectar_nodos_viales_cercanos(
        nodos_viales,
        k=k_viales,
    )

    rutas_viales, conexiones_hospitales = agregar_tipos_ruta(
        rutas_viales,
        conexiones_hospitales,
    )

    rutas_completas = construir_rutas_completas(
        rutas_viales,
        conexiones_hospitales,
        rutas_extra,
    )

    guardar_rutas_completas(rutas_completas, output_dir)

    return rutas_completas