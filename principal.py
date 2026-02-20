import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de estilo
st.set_page_config(page_title="ZERO INK Admin", layout="wide")
st.title("🚀 ZERO INK - Gestión de Negocio")

# Conexión automática (Usa los Secrets de Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para cargar datos de forma segura
def cargar(pestaña):
    try:
        return conn.read(worksheet=pestaña, ttl=0)
    except:
        return pd.DataFrame()

# Cargar las tablas actuales
df_v = cargar("Ventas")
df_c = cargar("Compras")
df_d = cargar("DTF")

menu = st.sidebar.selectbox("Acción", ["Ventas", "Compras", "DTF", "Reportes"])

if menu == "Ventas":
    st.header("🛒 Registro de Ventas")
    with st.form("v"):
        f = st.date_input("Fecha", datetime.now())
        cl = st.text_input("Cliente")
        ar = st.text_input("Artículo")
        ta = st.selectbox("Talla", ["S", "M", "L", "XL", "N/A"])
        co = st.text_input("Color")
        cos = st.number_input("Costo", min_value=0.0)
        ven = st.number_input("Venta", min_value=0.0)
        
        if st.form_submit_button("Guardar"):
            nueva = pd.DataFrame([{"Fecha": f.strftime("%d/%m/%Y"), "Cliente": cl, "Artículo": ar, 
                                   "Talla": ta, "Color": co, "Costo": cos, "Venta": ven, "Ganancia": ven - cos}])
            # Unir y guardar
            df_final = pd.concat([df_v, nueva], ignore_index=True)
            conn.update(worksheet="Ventas", data=df_final)
            st.success("¡Venta Guardada!")
            st.balloons()

elif menu == "DTF":
    st.header("🖨️ Registro de DTF")
    with st.form("d"):
        f = st.date_input("Fecha", datetime.now())
        me = st.number_input("Metros", min_value=0.0)
        ct = st.number_input("Costo Total", min_value=0.0)
        if st.form_submit_button("Guardar DTF"):
            nueva = pd.DataFrame([{"Fecha": f.strftime("%d/%m/%Y"), "Metros": me, "Costo_Total": ct}])
            df_final = pd.concat([df_d, nueva], ignore_index=True)
            conn.update(worksheet="DTF", data=df_final)
            st.success("¡DTF Guardado!")

elif menu == "Reportes":
    st.header("📊 Resumen")
    st.subheader("Ventas Recientes")
    st.dataframe(df_v)
