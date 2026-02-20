import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="ZERO INK Admin", layout="wide")

st.title("🚀 ZERO INK - Gestión de Negocio")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(pestaña):
    try:
        return conn.read(worksheet=pestaña, ttl=0)
    except:
        return pd.DataFrame()

# Cargar datos
df_v = cargar_datos("Ventas")

menu = st.sidebar.selectbox("Seleccionar Acción", ["Registrar Venta", "Ver Reportes"])

if menu == "Registrar Venta":
    st.header("🛒 Registrar Nueva Venta")
    with st.form("form_ventas"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", datetime.now())
            cliente = st.text_input("Cliente")
            articulo = st.text_input("Artículo")
            talla = st.selectbox("Talla", ["S", "M", "L", "XL", "N/A"])
        with col2:
            color = st.text_input("Color")
            costo = st.number_input("Costo", min_value=0.0)
            venta = st.number_input("Venta", min_value=0.0)
            ganancia = venta - costo
            st.write(f"**Ganancia calculada:** L. {ganancia}")

        if st.form_submit_button("Guardar Venta"):
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Cliente": cliente,
                "Artículo": articulo,
                "Talla": talla,
                "Color": color,
                "Costo": costo,
                "Venta": venta,
                "Ganancia": ganancia
            }])
            df_actualizado = pd.concat([df_v, nueva_fila], ignore_index=True)
            conn.update(worksheet="Ventas", data=df_actualizado)
            st.success("✅ Venta guardada")
            st.balloons()

elif menu == "Ver Reportes":
    st.header("📊 Resumen de Ventas")
    if not df_v.empty:
        st.dataframe(df_v)




