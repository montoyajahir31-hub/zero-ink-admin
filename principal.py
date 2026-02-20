import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="ZERO INK Admin", layout="wide")
st.title("🚀 ZERO INK - Gestión Profesional")

# 2. DEFINICIÓN DE PRECIOS Y PRODUCTOS (Tu Hoja de Costos interna)
# Aquí he puesto los precios base. Puedes ajustarlos si cambian.
PRECIOS_PRODUCTOS = {
    "Camiseta Algodón (Personalizada)": 250.0,
    "Camiseta Dry-Fit": 300.0,
    "Sudadero (Hoodie)": 550.0,
    "Gorra Trucker": 150.0,
    "Vinil Textil (por metro)": 180.0,
    "DTF (por metro lineal)": 220.0,
    "Otros": 0.0
}

# 3. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar(pestaña):
    try:
        data = conn.read(worksheet=pestaña, ttl=0)
        return data.dropna(how="all")
    except:
        return pd.DataFrame()

df_v = cargar("Ventas")
df_c = cargar("Compras")
df_d = cargar("DTF")

# 4. MENÚ LATERAL
menu = st.sidebar.selectbox("Acción", ["Ventas", "Compras", "DTF", "Reportes"])

# --- SECCIÓN VENTAS (PULIDA CON TUS PRECIOS) ---
if menu == "Ventas":
    st.header("🛒 Registro de Ventas")
    with st.form("form_v"):
        col1, col2 = st.columns(2)
        
        with col1:
            f = st.date_input("Fecha", datetime.now())
            cl = st.text_input("Nombre del Cliente")
            # Lista de tus artículos reales
            ar = st.selectbox("Artículo", list(PRECIOS_PRODUCTOS.keys()))
            ta = st.selectbox("Talla", ["N/A", "S", "M", "L", "XL", "XXL"])
        
        with col2:
            co = st.text_input("Color / Descripción")
            # El precio se sugiere según el artículo, pero puedes editarlo si das descuento
            precio_sugerido = PRECIOS_PRODUCTOS[ar]
            ven = st.number_input("Precio de Venta (Lps)", min_value=0.0, value=float(precio_sugerido))
            cos = st.number_input("Costo de Producción (Lps)", min_value=0.0)
            
        if st.form_submit_button("Guardar Venta"):
            ganancia = ven - cos
            nueva = pd.DataFrame([{
                "Fecha": f.strftime("%d/%m/%Y"), 
                "Cliente": cl, 
                "Artículo": ar, 
                "Talla": ta, 
                "Color": co, 
                "Costo": cos, 
                "Venta": ven, 
                "Ganancia": ganancia
            }])
            df_final = pd.concat([df_v, nueva], ignore_index=True)
            conn.update(worksheet="Ventas", data=df_final)
            st.success(f"✅ Venta de {ar} guardada. Ganancia: L. {ganancia}")
            st.balloons()

# --- SECCIÓN COMPRAS ---
elif menu == "Compras":
    st.header("📦 Registro de Compras e Insumos")
    with st.form("form_c"):
        f = st.date_input("Fecha", datetime.now())
        prov = st.text_input("Proveedor")
        item = st.text_input("Insumo (Ej: Tintas, Rollos DTF, Camisetas Lisas)")
        cant = st.number_input("Cantidad", min_value=0)
        costo_u = st.number_input("Costo Unitario", min_value=0.0)
        
        if st.form_submit_button("Registrar Compra"):
            nueva_c = pd.DataFrame([{
                "Fecha": f.strftime("%d/%m/%Y"),
                "Proveedor": prov,
                "Artículo": item,
                "Cantidad": cant,
                "Costo_Unidad": costo_u,
                "Total": cant * costo_u
            }])
            df_final_c = pd.concat([df_c, nueva_c], ignore_index=True)
            conn.update(worksheet="Compras", data=df_final_c)
            st.success("✅ Compra añadida al historial")

# --- SECCIÓN DTF ---
elif menu == "DTF":
    st.header("🖨️ Control de Impresión DTF")
    with st.form("form_d"):
        f = st.date_input("Fecha", datetime.now())
        me = st.number_input("Metros Impresos", min_value=0.0, step=0.1)
        ct = st.number_input("Costo de Material (Lps)", min_value=0.0)
        if st.form_submit_button("Guardar Registro DTF"):
            nueva_d = pd.DataFrame([{"Fecha": f.strftime("%d/%m/%Y"), "Metros": me, "Costo_Total": ct}])
            df_final_d = pd.concat([df_d, nueva_d], ignore_index=True)
            conn.update(worksheet="DTF", data=df_final_d)
            st.success(f"✅ Se registraron {me} metros de DTF")

# --- SECCIÓN REPORTES ---
elif menu == "Reportes":
    st.header("📊 Resumen General de ZERO INK")
    t1, t2, t3 = st.tabs(["Ventas", "Compras", "DTF"])
    with t1:
        st.dataframe(df_v, use_container_width=True)
        if not df_v.empty:
            st.metric("Ventas Totales", f"L. {df_v['Venta'].sum():,.2f}")
            st.metric("Ganancia Total", f"L. {df_v['Ganancia'].sum():,.2f}")
    with t2:
        st.dataframe(df_c, use_container_width=True)
    with t3:
        st.dataframe(df_d, use_container_width=True)
