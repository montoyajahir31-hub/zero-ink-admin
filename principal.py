import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ZERO INK Admin", layout="wide")

REFERENCIA_COSTOS = {
    "Camisa P/D": 58, "Camisa Algodón": 58, "Camisa Oversize": 120, 
    "Camisa Kiana": 45, "Camisa Polo": 160, "Sudadera sin Gorro": 160, 
    "Sudadera con Gorro": 220, "Lámina Sublimación (20x25)": 75
}

# --- CONEXIÓN ---
# Mantenemos esta para leer, que es muy rápida
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(pestaña):
    try:
        return conn.read(worksheet=pestaña, ttl=0).dropna(how="all")
    except:
        return pd.DataFrame()

df_pedidos = cargar_datos("Ventas")
df_dtf = cargar_datos("DTF")
df_compras = cargar_datos("Compras")

st.title("📊 Gestión ZERO INK")

menu = st.sidebar.radio("Ir a:", ["📝 Registro de Ventas", "🛒 Lista de Compras", "📉 Control de DTF", "💰 Análisis Final"])

# --- 1. REGISTRO DE VENTAS ---
if menu == "📝 Registro de Ventas":
    st.subheader("Registrar Nueva Venta")
    with st.form("venta_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            cliente = st.text_input("Cliente")
            articulo = st.selectbox("Artículo", list(REFERENCIA_COSTOS.keys()))
        with col2:
            talla_in = st.text_input("Talla (S, M, L)")
            color = st.text_input("Color")
        with col3:
            precio_v = st.number_input("Precio Venta (Lps)", min_value=0.0)
            cant = st.number_input("Cantidad", min_value=1, value=1)
        
        if st.form_submit_button("📥 GUARDAR VENTA"):
            costo_unitario = REFERENCIA_COSTOS[articulo]
            tallas = [t.strip().upper() for t in talla_in.split(",")] if talla_in else ["N/A"]
            
            nuevos_registros = []
            for i in range(int(cant)):
                t_act = tallas[i] if i < len(tallas) else tallas[-1]
                nuevos_registros.append({
                    "Fecha": datetime.now().strftime("%d-%m-%Y"),
                    "Cliente": cliente.upper(),
                    "Artículo": articulo,
                    "Talla": t_act,
                    "Color": color.capitalize(),
                    "Costo": costo_unitario,
                    "Venta": precio_v,
                    "Ganancia": precio_v - costo_unitario
                })
            
            # UNIÓN DE DATOS
            nuevo_df = pd.concat([df_pedidos, pd.DataFrame(nuevos_registros)], ignore_index=True)
            
            # EL TRUCO PARA EVITAR EL ERROR:
            try:
                conn.update(worksheet="Ventas", data=nuevo_df)
                st.success(f"✅ {cant} Venta(s) guardada(s)!")
                st.balloons()
            except Exception as e:
                st.error("Error de permisos. Asegúrate de que el Excel esté compartido como 'Editor' con CUALQUIER PERSONA que tenga el enlace.")
                st.info("Si ya está como Editor, intenta dar clic en el botón de 'Reboot' en el menú de la derecha de Streamlit.")

# El resto de las secciones (Compras, DTF, Análisis) se mantienen igual...
# (Copia el resto del código del bloque anterior para no perderlo)
