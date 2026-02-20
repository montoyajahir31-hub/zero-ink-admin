import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="ZERO INK Admin", layout="wide")

# Precios y Costos de Referencia (Tus datos de VS Code)
PRECIO_METRO_DTF = 200
REFERENCIA_COSTOS = {
    "Camisa P/D": 58, "Camisa Algodón": 58, "Camisa Oversize": 120, 
    "Camisa Kiana": 45, "Camisa Polo": 160, "Sudadera sin Gorro": 160, 
    "Sudadera con Gorro": 220, "Lámina Sublimación (20x25)": 75
}

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(pestaña):
    try:
        return conn.read(worksheet=pestaña, ttl=0).dropna(how="all")
    except:
        return pd.DataFrame()

# Cargar datos actuales
df_pedidos = cargar_datos("Ventas")
df_dtf = cargar_datos("DTF")
df_compras = cargar_datos("Compras")

# --- DISEÑO ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; }
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; color: black; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Gestión ZERO INK")

with st.sidebar:
    st.header("🏢 Menú Principal")
    menu = st.radio("Ir a:", ["📝 Registro de Ventas", "🛒 Lista de Compras", "📉 Control de DTF", "💰 Análisis Final"])

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
            
            nuevo_df = pd.concat([df_pedidos, pd.DataFrame(nuevos_registros)], ignore_index=True)
            conn.update(worksheet="Ventas", data=nuevo_df)
            st.success(f"✅ {cant} Venta(s) registrada(s) en Google Sheets")
            st.balloons()
            st.rerun()

    st.markdown("---")
    if not df_pedidos.empty:
        st.write("### Historial de Ventas")
        st.dataframe(df_pedidos, use_container_width=True)

# --- 2. LISTA DE COMPRAS ---
elif menu == "🛒 Lista de Compras":
    st.subheader("🛒 ¿Qué necesito comprar?")
    with st.form("compra_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        cli = c1.text_input("Cliente")
        art = c2.selectbox("Artículo", list(REFERENCIA_COSTOS.keys()))
        tal = c3.text_input("Talla")
        can = c4.number_input("Cant.", min_value=1, value=1)
        
        if st.form_submit_button("➕ AÑADIR A LISTA"):
            nueva_compra = pd.DataFrame([{"Cliente": cli.upper(), "Artículo": art, "Talla": tal.upper(), "Cant": can}])
            df_final_c = pd.concat([df_compras, nueva_compra], ignore_index=True)
            conn.update(worksheet="Compras", data=df_final_c)
            st.success("Añadido a la lista de compras")
            st.rerun()
    
    st.dataframe(df_compras, use_container_width=True)

# --- 3. CONTROL DE DTF ---
elif menu == "📉 Control de DTF":
    st.subheader("📏 Registro de Gasto DTF")
    with st.form("dtf_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        met = f1.number_input("Metros impresos", min_value=0.0, step=0.01)
        if st.form_submit_button("💾 GUARDAR GASTO DTF"):
            costo = met * PRECIO_METRO_DTF
            nuevo_dtf = pd.DataFrame([{"Fecha": datetime.now().strftime("%d-%m-%Y"), "Metros": met, "Costo_Total": costo}])
            df_final_d = pd.concat([df_dtf, nuevo_dtf], ignore_index=True)
            conn.update(worksheet="DTF", data=df_final_d)
            st.success(f"Gasto de L {costo:.2f} registrado")
            st.rerun()
    
    st.dataframe(df_dtf, use_container_width=True)

# --- 4. ANÁLISIS FINAL ---
elif menu == "💰 Análisis Final":
    st.subheader("💹 Resumen Financiero")
    
    inv_r = df_pedidos['Costo'].sum() if not df_pedidos.empty else 0
    ven_b = df_pedidos['Venta'].sum() if not df_pedidos.empty else 0
    inv_d = df_dtf['Costo_Total'].sum() if not df_dtf.empty else 0
    neta = (df_pedidos['Ganancia'].sum() if not df_pedidos.empty else 0) - inv_d
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inversión Ropa", f"L {inv_r:,.2f}")
    c2.metric("Inversión DTF", f"L {inv_d:,.2f}")
    c3.metric("Ventas Totales", f"L {ven_b:,.2f}")
    c4.metric("GANANCIA NETA", f"L {neta:,.2f}")
