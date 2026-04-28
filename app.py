import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector

# CONFIG
st.set_page_config(page_title="Dashboard Vencimientos", layout="wide")

# CONEXIÓN DB
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kevinmoreno31416",
        database="vencimientos_db"
    )

mydb = get_connection()

# LEER DATOS
try:
    df = pd.read_sql("SELECT * FROM equipos", mydb)
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
    por_vencer = len(df[df["dias_restantes"].between(0, 5)])
    vencidos = len(df[df["dias_restantes"] < 0])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total registros", total)
    col2.metric("Por vencer (5 dias)", por_vencer)
    col3.metric("Vencidos", vencidos)

    # GRÁFICA
    st.subheader("📈 Vencimientos por días restantes")
    st.bar_chart(df["dias_restantes"])

    # ALERTAS
    st.subheader("🚨 Alerta para vencer (5 días)")
    alertas = (df[df["dias_restantes"].between(0, 5)])

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
