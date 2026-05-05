import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# CONFIG
st.set_page_config(page_title="Dashboard Vencimientos", layout="wide")

# CONEXIÓN DB
@st.cache_resource
def get_engine():
    return create_engine(
        st.secrets["DB_URL"],
        connect_args={"sslmode": "require"}
    )

engine = get_engine()

# LEER DATOS
try:
    df = pd.read_sql("SELECT * FROM equipos", engine)
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.stop()

# PROCESAMIENTO
df["fecha_vencimiento"] = pd.to_datetime(df["fecha_vencimiento"], errors='coerce')

hoy = pd.to_datetime(datetime.now().date())

df["dias_restantes"] = (df["fecha_vencimiento"] - hoy).dt.days
# =========================
# SIDEBAR
# =========================
st.sidebar.title("📊 Menú")
opcion = st.sidebar.selectbox("Navegación", ["Dashboard", "Registros"])

# =========================
# DASHBOARD
# =========================
if opcion == "Dashboard":

    st.title("📊 Dashboard de Vencimientos")

    # KPIs
    total = len(df)
    por_vencer = len(df[df["dias_restantes"].between(0, 20)])
    vencidos = len(df[df["dias_restantes"] < 0])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total registros", total)
    col2.metric("Por vencer (20 dias)", por_vencer)
    col3.metric("Vencidos", vencidos)

    # GRÁFICA
    st.subheader("📈 Vencimientos por días restantes")
    st.bar_chart(df["dias_restantes"])

    # ALERTAS
    st.subheader("🚨 Alerta para vencer (20 días)")
    alertas = (df[df["dias_restantes"].between(0, 20)])

    if not alertas.empty:
        st.error("Hay elementos próximos a vencer")
        st.dataframe(alertas)
    else:
        st.success("Todo bajo control")

    
    # VENCIDOS
    st.subheader("Vencidos")
    vencidos = (df[df["dias_restantes"] <= 0])

    if vencidos.empty:
        st.success("Todo bajo control")
        
    else:
        st.error("Elementos Vencidos")
        st.dataframe(vencidos)

# =========================
# TABLA COMPLETA
# =========================
elif opcion == "Registros":

    st.title("📋 Lista de registros")
    st.dataframe(df)
