import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Dashboard QR",
    layout="wide"
)


st_autorefresh(interval=10000, key="qr_refresh")

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
    # Extraer dia    
    df["dia"] = df["fecha"].dt.day
    dias = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
    }
    # Extraer dia de la semana    df["dia_semana"] = df["fecha"].dt.day_name()
    df["dia_semana"] = df["fecha"].dt.day_name().map(dias)
    
    

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
    col3.metric("Día pico", df["dia_semana"].mode()[0])
    col4.metric("Último escaneo", df["fecha"].max().strftime("%H:%M"))

    st.divider()
    st.subheader("Escaneos por hora")
 
    dias_semana=df["dia_semana"].unique()
    dias_selected = st.selectbox("Selecciona los días de la semana", options=dias_semana)
    
    df_filtrado = df[df["dia_semana"].isin([dias_selected])]
    st.line_chart(df_filtrado["hora"].value_counts().sort_index(),
                    x_label="Hora del día", y_label="Número de escaneos",
                    use_container_width=True
                    )
    
    st.divider()
    st.subheader("Escaneos por día de la semana")
    dias_semana_counts = df["dia_semana"].value_counts().reindex(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
    st.bar_chart(dias_semana_counts, x_label="Día de la semana", y_label="Número de escaneos", use_container_width=True)
    st.divider()
    

    st.subheader("Últimos escaneos")
    st.dataframe(
        df.sort_values("fecha", ascending=False)[["fecha", "dispositivo"]],
        use_container_width=True
    )