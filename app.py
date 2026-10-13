import streamlit as st

st.set_page_config(
    page_title="Mi Plataforma Financiera", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="collapsed" # Ocultamos la barra lateral si molesta
)

st.title("📈 Plataforma Financiera Multifuente")

# Creamos un menú de pestañas horizontal en la parte superior
pestana = st.radio(
    "Selecciona una herramienta:",
    ["🏠 Inicio", "📈 1. Analizador", "💼 2. Mi Cartera (Simulador)", "📊 3. Cartera Real"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# Lógica para mostrar una u otra herramienta según la pestaña seleccionada
if pestana == "🏠 Inicio":
    st.subheader("Bienvenido a tu centro de control de inversiones.")
    st.write("Usa las pestañas superiores para navegar entre el Evaluador, el Simulador y tu Cartera Real.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📈 Analizador")
        st.write("Busca acciones, fondos y ETFs, métricas y TER.")
    with col2:
        st.markdown("### 💼 Mi Cartera")
        st.write("Simulador de interés compuesto a largo plazo.")
    with col3:
        st.markdown("### 📊 Cartera Real")
        st.write("Seguimiento de patrimonio con precios de cierre.")

elif pestana == "📈 1. Analizador":
    st.header("🔍 Evaluador de Acciones, Fondos y ETFs")
    # AQUI PEGARIAS TODO EL CÓDIGO DE TU ANALIZADOR ORIGINAL
    st.info("Aquí va el código de tu analizador.")

elif pestana == "💼 2. Mi Cartera (Simulador)":
    st.header("💼 Simulador Global de Cartera Consolidada")
    # AQUI PEGARIAS EL CÓDIGO DEL SIMULADOR DE PROYECCIÓN
    st.info("Aquí va el código de tu simulador de cartera.")

elif pestana == "📊 3. Cartera Real":
    st.header("📊 Seguimiento de Cartera Real y Patrimonio")
    # AQUI PEGARIAS EL CÓDIGO DE LA CARTERA REAL (CON YFINANCE Y FLECHITAS)
    st.info("Aquí va el código de tu cartera real.")
