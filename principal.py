import streamlit as st
from streamlit_gsheets import GoogleSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ZERO INK Admin", layout="wide")

# Conexión con Google Sheets usando el enlace que me pasaste
url = "https://docs.google.com/spreadsheets/d/1plPWAFs9LsYTqfZqxgiFo9hCOAwtQEtacn05G0kP8YA/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetConnection)

REFERENCIA_COSTOS = {
    "Camisa P/D": 58, "Camisa Algodón": 58, "Camisa Oversize": 120, 
    "Camisa Kiana": 45, "Camisa Polo": 160, "Sudadera sin Gorro": 160, 
    "Sudadera con Gorro": 220, "Lámina Sublimación (20x25)": 75
}

st.title("📊 ZERO INK | Gestión en la Nube")

menu = st.sidebar.radio("Menú", ["📝 Ventas", "🛒 Compras", "📉 DTF", "💰 Análisis"])

# --- FUNCIONES DE LECTURA/ESCRITURA ---
def cargar_datos(sheet_name):
    return conn.read(spreadsheet=url, worksheet=sheet_name, ttl=0)

# --- VISTA DE VENTAS ---
if menu == "📝 Ventas":
    st.subheader("Registrar Venta")
    with st.form("form_ventas", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        cliente = col1.text_input("Cliente")
        articulo = col1.selectbox("Artículo", list(REFERENCIA_COSTOS.keys()))
        tallas = col2.text_input("Tallas (S, M, L)")
        color = col2.text_input("Color")
        precio = col3.number_input("Precio Venta", min_value=0.0)
        cant = col3.number_input("Cantidad", min_value=1, value=1)
        
        if st.form_submit_button("Guardar Venta"):
            df_actual = cargar_datos("Ventas")
            costo_u = REFERENCIA_COSTOS[articulo]
            lista_tallas = [t.strip().upper() for t in tallas.split(",")] if tallas else ["N/A"]
            
            nuevos_registros = []
            for i in range(int(cant)):
                t_act = lista_tallas[i] if i < len(lista_tallas) else lista_tallas[-1]
                nuevos_registros.append({
                    "Fecha": datetime.now().strftime("%d-%m-%Y"),
                    "Cliente": cliente.upper(),
                    "Artículo": articulo,
                    "Talla": t_act,
                    "Color": color.capitalize(),
                    "Costo": costo_u,
                    "Venta": precio,
                    "Ganancia": precio - costo_u
                })
            
            df_final = pd.concat([df_actual, pd.DataFrame(nuevos_registros)], ignore_index=True)
            conn.update(spreadsheet=url, worksheet="Ventas", data=df_final)
            st.success("Venta guardada en Google Sheets")
            st.rerun()

    df_v = cargar_datos("Ventas")
    st.dataframe(df_v)

# --- VISTA DE COMPRAS ---
elif menu == "🛒 Compras":
    st.subheader("Lista de Compras")
    with st.form("form_compras", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        cli = c1.text_input("Cliente")
        art = c2.selectbox("Artículo", list(REFERENCIA_COSTOS.keys()))
        tallas_c = c3.text_input("Tallas")
        if st.form_submit_button("Añadir a Lista"):
            df_actual = cargar_datos("Compras")
            # Lógica similar para guardar...
            st.info("Guardando en pestaña Compras...")

# --- VISTA DE DTF ---
elif menu == "📉 DTF":
    st.subheader("Gasto de DTF")
    # Lógica para la pestaña DTF...

# --- ANÁLISIS ---
elif menu == "💰 Análisis":
    st.subheader("Resumen Financiero")
    df_v = cargar_datos("Ventas")
    st.metric("Venta Total", f"L {df_v['Venta'].sum():,.2f}")

