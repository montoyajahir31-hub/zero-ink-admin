import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="ZERO INK Admin", layout="wide")

st.title("🚀 ZERO INK - Gestión de Negocio")

# Conexión con Google Sheets (Toma los datos de los Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para cargar datos
def cargar_datos(nombre_pestaña):
    try:
        return conn.read(worksheet=nombre_pestaña, ttl=0)
    except Exception as e:
        st.error(f"Error al cargar la pestaña {nombre_pestaña}. Revisa que el nombre sea exacto.")
        return pd.DataFrame()

# Cargar las bases de datos
df_v = cargar_datos("Ventas")
df_c = cargar_datos("Compras")
df_d = cargar_datos("DTF")

# Menú principal
menu = st.sidebar.selectbox("Seleccionar Acción", ["Registrar Venta", "Registrar Compra", "Registrar DTF", "Ver Inventario/Reportes"])

if menu == "Registrar Venta":
    st.header("🛒 Registrar Nueva Venta")
    with st.form("form_ventas"):
        fecha = st.date_input("Fecha", datetime.now())
        cliente = st.text_input("Nombre del Cliente")
        producto = st.selectbox("Producto", ["Camiseta Blanca", "Camiseta Negra", "Sudadero", "Gorra"])
        monto = st.number_input("Monto Cobrado", min_value=0.0, step=1.0)
        
        enviar = st.form_submit_button("Guardar Venta")
        
        if enviar:
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Cliente": cliente,
                "Producto": producto,
                "Monto": monto
            }])
            df_actualizado = pd.concat([df_v, nueva_fila], ignore_index=True)
            conn.update(worksheet="Ventas", data=df_actualizado)
            st.success("✅ Venta registrada correctamente")
            st.balloons()

elif menu == "Ver Inventario/Reportes":
    st.header("📊 Resumen de Ventas")
    if not df_v.empty:
        st.dataframe(df_v)
        st.metric("Total Ventas", f"L. {df_v['Monto'].sum():,.2f}")
    else:
        st.info("No hay datos registrados aún.")



