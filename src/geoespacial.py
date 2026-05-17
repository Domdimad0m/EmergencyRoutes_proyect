# geoespacial.py

from kdtree import (
    construir_kdtree_hospitales,
    buscar_hospitales_en_radio,
)


def obtener_hospitales_cercanos(
    hospitales,
    emergencia,
    radio_km=5,
):

    kdtree = construir_kdtree_hospitales(
        hospitales
    )

    hospitales_cercanos = (
        buscar_hospitales_en_radio(
            kdtree,
            emergencia,
            radio_km,
        )
    )

    return hospitales_cercanos


def obtener_ids_hospitales_cercanos(
    hospitales_cercanos
):

    ids = []

    for hospital in hospitales_cercanos:

        ids.append(
            hospital["id_hospital"]
        )

    return ids


def filtrar_capacidades_por_radio(
    capacidades,
    hospitales_cercanos,
):

    ids_cercanos = (
        obtener_ids_hospitales_cercanos(
            hospitales_cercanos
        )
    )

    capacidades_filtradas = capacidades[
        capacidades["id_hospital"].isin(
            ids_cercanos
        )
    ].copy()

    return capacidades_filtradas


def filtrar_hospitales_por_radio(
    hospitales,
    emergencia,
    radio_km=5,
):

    hospitales_cercanos = (
        obtener_hospitales_cercanos(
            hospitales,
            emergencia,
            radio_km,
        )
    )

    ids_cercanos = (
        obtener_ids_hospitales_cercanos(
            hospitales_cercanos
        )
    )

    hospitales_filtrados = hospitales[
        hospitales["id_osm"].isin(
            ids_cercanos
        )
    ].copy()

    return hospitales_filtrados


def preparar_candidatos_geoespaciales(
    hospitales,
    capacidades,
    emergencia,
    radio_km=5,
):

    hospitales_cercanos = (
        obtener_hospitales_cercanos(
            hospitales,
            emergencia,
            radio_km,
        )
    )

    capacidades_filtradas = (
        filtrar_capacidades_por_radio(
            capacidades,
            hospitales_cercanos,
        )
    )

    return (
        hospitales_cercanos,
        capacidades_filtradas,
    )