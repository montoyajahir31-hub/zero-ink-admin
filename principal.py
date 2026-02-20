import streamlit as st
from streamlit_gsheets import GSheetConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ZERO INK Admin", layout="wide")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetConnection)

REFERENCIA_COSTOS = {
    "Camisa P/D": 58, "Camisa Algodón": 58, "Camisa Oversize": 120, 
    "Camisa Kiana": 45, "Camisa Polo": 160, "Sudadera sin Gorro": 160, 
    "Sudadera con Gorro": 220, "Lámina Sublimación (20x25)": 75
}

st.title("📊 ZERO INK | Gestión en la Nube")

menu = st.sidebar.radio("Menú", ["📝 Ventas", "🛒 Compras", "📉 DTF", "💰 Análisis"])

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_datos(worksheet):
    return conn.read(worksheet=worksheet, ttl=0)

def guardar_datos(df, worksheet):
    conn.update(worksheet=worksheet, data=df)
    st.cache_data.clear()

# --- INTERFAZ ---
if menu == "📝 Ventas":
    st.subheader("Registrar Venta Real")
    # Aquí irá el formulario que ya conoces, pero guardando en la nube
    st.info("Conecta tu Google Sheet para empezar a registrar.")

elif menu == "💰 Análisis":
    st.subheader("Resumen Semanal")
    if st.button("🗑️ REINICIAR SEMANA COMPLETA"):
        st.warning("Esto limpiará tu Google Sheet.")

st.sidebar.markdown("---")
st.sidebar.write("🔒 Conectado a Google Drive")