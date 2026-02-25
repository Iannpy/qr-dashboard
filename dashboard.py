import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Dashboard QR",
    layout="wide"
)


st_autorefresh(interval=5000, key="qr_refresh")

API_BASE = "https://qr-production-73d6.up.railway.app"

st.title("📊 Dashboard de Escaneos QR")
lista_qrs = ["ANATO_BAQ", "WSP_DIXY"]
slug = st.selectbox("Slug del QR", options=lista_qrs)

if slug:
    url = f"{API_BASE}/stats/{slug}"
    
    try:
        r = requests.get(url)
        r.raise_for_status()
    except:
        st.error("No se pudo conectar con la API.")
        st.stop()

    data = r.json()
    df = pd.DataFrame(data["clicks"])

    if df.empty:
        st.warning("Aún no hay escaneos.")
        st.stop()

    # Convertir a datetime
    df["fecha"] = pd.to_datetime(df["fecha"], utc=True)

    # Convertir de UTC a hora de Bogotá
    df["fecha"] = df["fecha"].dt.tz_convert("America/Bogota")

    # Extraer hora ya convertida
    df["hora"] = df["fecha"].dt.hour

    def detectar_dispositivo(ua):
        if "Android" in ua:
            return "Android"
        elif "iPhone" in ua:
            return "iPhone"
        else:
            return "Otro"

    df["dispositivo"] = df["navegador"].apply(detectar_dispositivo)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total escaneos", len(df))
    col2.metric("Hora pico", df["hora"].mode()[0])
    col3.metric("Último escaneo", df["fecha"].max().strftime("%H:%M"))

    st.divider()
    st.subheader("Escaneos por hora")
 
    st.line_chart(df["hora"].value_counts().sort_index(),
                    x_label="Hora del día", y_label="Número de escaneos",
                    use_container_width=True
                    )



    st.divider()

    st.subheader("Últimos escaneos")
    st.dataframe(
        df.sort_values("fecha", ascending=False)[["fecha", "dispositivo"]],
        use_container_width=True
    )