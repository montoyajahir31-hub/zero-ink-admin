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
        # Intentamos leer la pestaña
        data = conn.read(worksheet=pestaña, ttl=0)
        # Limpiamos filas vacías para evitar errores
        return data.dropna(how="all")
    except:
        return pd.DataFrame()

# Cargar las tablas actuales
df_v = cargar("Ventas")
df_c = cargar("Compras")
df_d = cargar("DTF")

menu = st.sidebar.selectbox("Acción", ["Ventas", "Compras", "DTF", "Reportes"])

# --- SECCIÓN VENTAS ---
if menu == "Ventas":
    st.header("🛒 Registro de Ventas")
    with st.form("form_v"):
        f = st.date_input("Fecha", datetime.now())
        cl = st.text_input("Cliente")
        ar = st.text_input("Artículo")
        ta = st.selectbox("Talla", ["S", "M", "L", "XL", "N/A"])
        co = st.text_input("Color")
        cos = st.number_input("Costo", min_value=0.0)
        ven = st.number_input("Venta", min_value=0.0)
        
        if st.form_submit_button("Guardar Venta"):
            nueva = pd.DataFrame([{"Fecha": f.strftime("%d/%m/%Y"), "Cliente": cl, "Artículo": ar, 
                                   "Talla": ta, "Color": co, "Costo": cos, "Venta": ven, "Ganancia": ven - cos}])
            df_final = pd.concat([df_v, nueva], ignore_index=True)
            conn.update(worksheet="Ventas", data=df_final)
            st.success("¡Venta Guardada!")
            st.balloons()

# --- SECCIÓN COMPRAS (¡ARREGLADO!) ---
elif menu == "Compras":
    st.header("📦 Registro de Compras (Inventario)")
    with st.form("form_c"):
        f = st.date_input("Fecha de Compra", datetime.now())
        prov = st.text_input("Proveedor / Tienda")
        item = st.text_input("¿Qué compraste? (Ej: Camisetas negras)")
        cant = st.number_input("Cantidad", min_value=0)
        costo_u = st.number_input("Costo por Unidad", min_value=0.0)
        total = cant * costo_u
        st.write(f"**Total de la compra:** L. {total}")

        if st.form_submit_button("Guardar Compra"):
            nueva_compra = pd.DataFrame([{
                "Fecha": f.strftime("%d/%m/%Y"),
                "Proveedor": prov,
                "Artículo": item,
                "Cantidad": cant,
                "Costo_Unidad": costo_u,
                "Total": total
            }])
            df_final_c = pd.concat([df_c, nueva_compra], ignore_index=True)
            conn.update(worksheet="Compras", data=df_final_c)
            st.success("¡Compra registrada en el inventario!")

# --- SECCIÓN DTF ---
elif menu == "DTF":
    st.header("🖨️ Registro de DTF")
    with st.form("form_d"):
        f = st.date_input("Fecha", datetime.now())
        me = st.number_input("Metros", min_value=0.0)
        ct = st.number_input("Costo Total", min_value=0.0)
        if st.form_submit_button("Guardar DTF"):
            nueva_d = pd.DataFrame([{"Fecha": f.strftime("%d/%m/%Y"), "Metros": me, "Costo_Total": ct}])
            df_final_d = pd.concat([df_d, nueva_d], ignore_index=True)
            conn.update(worksheet="DTF", data=df_final_d)
            st.success("¡DTF Guardado!")

# --- SECCIÓN REPORTES ---
elif menu == "Reportes":
    st.header("📊 Resumen General")
    tab1, tab2, tab3 = st.tabs(["Ventas", "Compras", "DTF"])
    
    with tab1:
        st.subheader("Historial de Ventas")
        st.dataframe(df_v, use_container_width=True)
    with tab2:
        st.subheader("Historial de Compras")
        st.dataframe(df_c, use_container_width=True)
    with tab3:
        st.subheader("Historial de DTF")
        st.dataframe(df_d, use_container_width=True)
