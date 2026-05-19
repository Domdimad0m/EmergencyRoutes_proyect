import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import folium

from grafo import construir_grafo_desde_rutas
from dijkstra import buscar_hospital_adecuado
from kdtree import construir_kdtree_hospitales, buscar_hospitales_en_radio
from conexiones_grafo import distancia_km

# ─────────────────────────────────────────────
# Página
# ─────────────────────────────────────────────
st.set_page_config(page_title="Sistema hospitalario", page_icon="🚑", layout="wide")
st.title("🚑 Sistema de despacho hospitalario")
st.caption("Álvaro Obregón · KDTree + Dijkstra")

# ─────────────────────────────────────────────
# Datos (cacheados, no se recargan en reruns)
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    return (
        pd.read_csv("datos/hospitales_limpio.csv"),
        pd.read_csv("datos/capacidades.csv"),
        pd.read_csv("datos/nodos_viales.csv"),
        pd.read_csv("datos/rutas_completas.csv"),
    )

@st.cache_resource
def cargar_grafo_y_kdtree(_rutas, _hospitales):
    return (
        construir_grafo_desde_rutas(_rutas),
        construir_kdtree_hospitales(_hospitales),
    )

try:
    hospitales, capacidades, nodos_viales, rutas = cargar_datos()
    grafo, kdtree = cargar_grafo_y_kdtree(rutas, hospitales)
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

# ─────────────────────────────────────────────
# Session state — se inicializa solo la primera vez
# ─────────────────────────────────────────────
_defaults = dict(
    fase="esperando",   # "esperando" | "calculando" | "listo" | "error"
    resultado=None,
    hospitales_cercanos=[],
    emergencia=None,
    nodo_origen=None,
    distancia_nodo=None,
    mapa_html=None,
    error_msg=None,
    # parámetros guardados para que el cálculo los use en el rerun
    p_lat=19.360000,
    p_lon=-99.200000,
    p_esp="urgencias",
    p_urg="ROJO",
    p_hora=12,
    p_radio=5,
)
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def nodo_mas_cercano(lat, lon):
    mejor, dist = None, float("inf")
    for _, n in nodos_viales.iterrows():
        d = distancia_km(lat, lon, n["lat"], n["lon"])
        if d < dist:
            dist, mejor = d, n["id_nodo"]
    return mejor, dist

def coords_de_nodo(nodo_id):
    h = hospitales[hospitales["id_osm"] == nodo_id]
    if not h.empty:
        return h.iloc[0]["lat"], h.iloc[0]["lon"]
    v = nodos_viales[nodos_viales["id_nodo"] == nodo_id]
    if not v.empty:
        return v.iloc[0]["lat"], v.iloc[0]["lon"]
    return None

def construir_mapa_html(lat, lon, hospitales_cercanos, resultado):
    m = folium.Map(location=[lat, lon], zoom_start=14)
    folium.Marker([lat, lon], popup="Emergencia", tooltip="🚨 Emergencia",
                  icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
    for h in hospitales_cercanos:
        folium.Marker([h["lat"], h["lon"]], popup=h["hospital"],
                      tooltip=f"🏥 {h['hospital']} ({round(h['distancia_km'],2)} km)",
                      icon=folium.Icon(color="green", icon="plus-sign")).add_to(m)
    if resultado:
        coords = [c for nid in resultado["ruta"]
                  if (c := coords_de_nodo(nid)) is not None]
        if len(coords) >= 2:
            folium.PolyLine([[c[0],c[1]] for c in coords],
                color="blue", weight=6, opacity=0.85,
                tooltip="Ruta óptima Dijkstra").add_to(m)
            lats, lons = [c[0] for c in coords], [c[1] for c in coords]
            m.fit_bounds([[min(lats),min(lons)],[max(lats),max(lons)]])
        hosp = hospitales[hospitales["id_osm"] == resultado["id_hospital"]]
        if not hosp.empty:
            r = hosp.iloc[0]
            folium.Marker([r["lat"], r["lon"]],
                popup=f"<b>{resultado['hospital']}</b>",
                tooltip=f"⭐ {resultado['hospital']}",
                icon=folium.Icon(color="blue", icon="star")).add_to(m)
    leyenda = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:9999;
         background:white;padding:10px 14px;border-radius:8px;
         border:1px solid #bbb;font-size:13px;line-height:1.9">
      <b>Leyenda</b><br>🔴 Emergencia<br>🟢 Hospitales KDTree<br>
      🔵 Hospital elegido<br><span style="color:blue">── Ruta Dijkstra</span>
    </div>"""
    m.get_root().html.add_child(folium.Element(leyenda))
    return m._repr_html_()

# ─────────────────────────────────────────────
# FASE: calculando
# Se ejecuta en el rerun posterior al submit.
# El form ya no existe en este rerun: los parámetros
# vienen de session_state, no de widgets.
# ─────────────────────────────────────────────
if st.session_state.fase == "calculando":
    with st.spinner("Calculando ruta óptima…"):
        try:
            lat  = st.session_state.p_lat
            lon  = st.session_state.p_lon
            esp  = st.session_state.p_esp
            urg  = st.session_state.p_urg
            hora = st.session_state.p_hora
            radio= st.session_state.p_radio

            nodo_origen, distancia_nodo = nodo_mas_cercano(lat, lon)

            emergencia = {
                "id_emergencia":          "E001",
                "lat":                    lat,
                "lon":                    lon,
                "especialidad_requerida": esp,
                "prioridad":              urg,
                "hora":                   hora,
                "id_nodo_origen":         nodo_origen,
            }

            hospitales_cercanos = buscar_hospitales_en_radio(kdtree, emergencia, radio)
            resultado           = buscar_hospital_adecuado(grafo, emergencia, capacidades, hora=hora)
            mapa_html           = construir_mapa_html(lat, lon, hospitales_cercanos, resultado)

            st.session_state.resultado           = resultado
            st.session_state.hospitales_cercanos = hospitales_cercanos
            st.session_state.emergencia          = emergencia
            st.session_state.nodo_origen         = nodo_origen
            st.session_state.distancia_nodo      = distancia_nodo
            st.session_state.mapa_html           = mapa_html
            st.session_state.error_msg           = None
            st.session_state.fase                = "listo"   # ← cambiar fase ANTES de rerun

        except Exception as e:
            st.session_state.error_msg = str(e)
            st.session_state.fase      = "error"

    # Forzar rerun limpio ahora que session_state está completo.
    # Este rerun llega con fase="listo" o fase="error" y sin ningún
    # widget pendiente — los resultados se muestran y ya no hay más reruns.
    st.rerun()

# ─────────────────────────────────────────────
# Sidebar: form de entrada
# Cuando se hace submit, solo guardamos los parámetros
# en session_state y cambiamos la fase a "calculando",
# luego st.rerun() dispara el bloque de arriba.
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("📋 Parámetros")
    with st.form("form_emergencia"):
        latitud      = st.number_input("Latitud",   value=st.session_state.p_lat,  format="%.6f")
        longitud     = st.number_input("Longitud",  value=st.session_state.p_lon,  format="%.6f")
        especialidad = st.selectbox("Tipo de emergencia",
                           ["urgencias","trauma","cardiologia","pediatria","general"],
                           index=["urgencias","trauma","cardiologia","pediatria","general"].index(st.session_state.p_esp))
        urgencia     = st.selectbox("Nivel de urgencia", ["ROJO","AMARILLO","VERDE"],
                           index=["ROJO","AMARILLO","VERDE"].index(st.session_state.p_urg))
        hora         = st.slider("Hora del día", 0, 23, st.session_state.p_hora)
        radio_km     = st.slider("Radio de búsqueda (km)", 1, 10, st.session_state.p_radio)
        submitted    = st.form_submit_button("🔍 Buscar hospital",
                           use_container_width=True, type="primary")

    if submitted:
        # Solo guardamos parámetros y cambiamos la fase.
        # El cálculo ocurre en el siguiente rerun (bloque "calculando" de arriba).
        st.session_state.p_lat  = latitud
        st.session_state.p_lon  = longitud
        st.session_state.p_esp  = especialidad
        st.session_state.p_urg  = urgencia
        st.session_state.p_hora = hora
        st.session_state.p_radio= radio_km
        st.session_state.fase   = "calculando"
        st.rerun()   # ← rerun inmediato, controlado; evita el rerun "de limpieza" del form

# ─────────────────────────────────────────────
# Pantalla principal según la fase
# ─────────────────────────────────────────────
fase = st.session_state.fase

if fase == "esperando":
    st.info("👈 Completa los parámetros y presiona **Buscar hospital**.")

elif fase == "error":
    st.error(f"❌ Error en el cálculo: {st.session_state.error_msg}")

elif fase == "listo":
    resultado           = st.session_state.resultado
    hospitales_cercanos = st.session_state.hospitales_cercanos
    emergencia          = st.session_state.emergencia

    # 1. Emergencia
    st.header("1. 📍 Emergencia registrada")
    c1, c2 = st.columns(2)
    with c1:
        st.json(emergencia)
    with c2:
        st.metric("Nodo vial más cercano", st.session_state.nodo_origen)
        st.metric("Distancia al nodo", f"{round(st.session_state.distancia_nodo, 3)} km")

    # 2. KDTree
    st.header("2. 🏥 Hospitales cercanos (KDTree)")
    if hospitales_cercanos:
        df = pd.DataFrame(hospitales_cercanos)
        cols = [c for c in ["id_hospital","hospital","distancia_km"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True)
    else:
        st.warning("No se encontraron hospitales en ese radio.")

    # 3. Dijkstra
    st.header("3. 📊 Resultado Dijkstra")
    if resultado is None:
        st.error("No se encontró hospital disponible para esa especialidad.")
    else:
        st.success(f"✅ Hospital elegido: **{resultado['hospital']}**")
        st.dataframe(pd.DataFrame([{
            "hospital":          resultado["hospital"],
            "id_hospital":       resultado["id_hospital"],
            "especialidad":      resultado["especialidad"],
            "camas_disponibles": resultado["camas_disponibles"],
            "costo_ruta":        round(resultado["costo_ruta"], 3),
            "hora":              resultado["hora"],
        }]), use_container_width=True)
        with st.expander("Ver nodos de la ruta"):
            st.write(resultado["ruta"])

    # 4. Mapa — HTML puro, sin streamlit-folium, cero reruns
    st.header("4. 🗺️ Mapa")
    if st.session_state.mapa_html:
        components.html(st.session_state.mapa_html, height=650, scrolling=False)