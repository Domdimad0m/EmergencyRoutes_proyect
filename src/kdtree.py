# kdtree.py

from conexiones_grafo import distancia_km


class KDNode:
    def __init__(self, punto, hospital, eje, izquierda=None, derecha=None):
        self.punto = punto
        self.hospital = hospital
        self.eje = eje
        self.izquierda = izquierda
        self.derecha = derecha


class KDTree:
    def __init__(self, hospitales):
        puntos = self.preparar_puntos(hospitales)
        self.raiz = self.construir_arbol(puntos, profundidad=0)

    def preparar_puntos(self, hospitales):
        puntos = []

        for _, hospital in hospitales.iterrows():
            puntos.append(
                {
                    "punto": (
                        hospital["lat"],
                        hospital["lon"],
                    ),
                    "hospital": hospital.to_dict(),
                }
            )

        return puntos

    def construir_arbol(self, puntos, profundidad):
        if not puntos:
            return None

        dimensiones = 2
        eje = profundidad % dimensiones

        puntos = sorted(
            puntos,
            key=lambda x: x["punto"][eje],
        )

        mediana = len(puntos) // 2

        return KDNode(
            punto=puntos[mediana]["punto"],
            hospital=puntos[mediana]["hospital"],
            eje=eje,
            izquierda=self.construir_arbol(
                puntos[:mediana],
                profundidad + 1,
            ),
            derecha=self.construir_arbol(
                puntos[mediana + 1 :],
                profundidad + 1,
            ),
        )

    def buscar_en_radio(self, lat, lon, radio_km):
        resultados = []

        self._buscar_en_radio(
            self.raiz,
            punto_objetivo=(lat, lon),
            radio_km=radio_km,
            resultados=resultados,
        )

        resultados = sorted(
            resultados,
            key=lambda x: x["distancia_km"],
        )

        return resultados

    def _buscar_en_radio(
        self,
        nodo,
        punto_objetivo,
        radio_km,
        resultados,
    ):
        if nodo is None:
            return

        lat_obj, lon_obj = punto_objetivo
        lat_nodo, lon_nodo = nodo.punto

        distancia = distancia_km(
            lat_obj,
            lon_obj,
            lat_nodo,
            lon_nodo,
        )

        if distancia <= radio_km:
            resultados.append(
                {
                    "id_hospital": nodo.hospital["id_osm"],
                    "hospital": nodo.hospital["nombre"],
                    "lat": lat_nodo,
                    "lon": lon_nodo,
                    "distancia_km": round(distancia, 3),
                    "datos_hospital": nodo.hospital,
                }
            )

        eje = nodo.eje
        diferencia = punto_objetivo[eje] - nodo.punto[eje]

        if diferencia <= 0:
            self._buscar_en_radio(
                nodo.izquierda,
                punto_objetivo,
                radio_km,
                resultados,
            )

            self._buscar_en_radio(
                nodo.derecha,
                punto_objetivo,
                radio_km,
                resultados,
            )

        else:
            self._buscar_en_radio(
                nodo.derecha,
                punto_objetivo,
                radio_km,
                resultados,
            )

            self._buscar_en_radio(
                nodo.izquierda,
                punto_objetivo,
                radio_km,
                resultados,
            )


def construir_kdtree_hospitales(hospitales):
    return KDTree(hospitales)


def buscar_hospitales_en_radio(kdtree, emergencia, radio_km):
    return kdtree.buscar_en_radio(
        emergencia["lat"],
        emergencia["lon"],
        radio_km,
    )