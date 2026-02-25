import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Dashboard QR",
    layout="wide"
)

API_BASE = "https://qr-production-73d6.up.railway.app"

st.title("📊 Dashboard de Escaneos QR")

slug = st.text_input("Slug del QR", value="ANATO_BAQ")

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

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["hora"] = df["fecha"].dt.hour

    def detectar_dispositivo(ua):
        if "Android" in ua:
            return "Android"
        elif "iPhone" in ua:
            return "iPhone"
        else:
            return "Otro"

    df["dispositivo"] = df["navegador"].apply(detectar_dispositivo)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total escaneos", len(df))
    col2.metric("Hora pico", df["hora"].mode()[0])
    col3.metric("Dispositivo top", df["dispositivo"].mode()[0])
    col4.metric("Último escaneo", df["fecha"].max().strftime("%H:%M"))

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Escaneos por hora")
        st.bar_chart(df["hora"].value_counts().sort_index())

    with c2:
        st.subheader("Dispositivos")
        st.bar_chart(df["dispositivo"].value_counts())

    st.divider()

    st.subheader("Últimos escaneos")
    st.dataframe(
        df.sort_values("fecha", ascending=False)[["fecha", "dispositivo"]],
        use_container_width=True
    )