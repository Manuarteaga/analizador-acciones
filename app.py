import streamlit as st

st.set_page_config(
    page_title="Mi Plataforma Financiera",
    # MENÚ LATERAL FORZADO MANUALMENTE
with st.sidebar:
    st.image("https://img.icons8.com/color/96/stocks.png", width=60)
    st.header("Navegación")
    
    # Enlaces manuales a tus páginas
    st.page_link("app.py", label="🏠 Inicio", icon="🏠")
    st.page_link("pages/1_📈_Analizador.py", label="Analizador Bursátil", icon="📈")
    st.page_link("pages/2_💼_Mi_Cartera.py", label="Mi Cartera Consolidada", icon="💼")
    )
    st.divider()

st.title("📈 Mi Plataforma Financiera")
st.write("Bienvenido a tu centro de control de inversiones.")

st.info("👈 Utiliza el menú lateral izquierdo para navegar entre el Evaluador, la Proyección de Cartera y tu Cartera Real.")

# Resumen rápido o bienvenida visual opcional
st.markdown("### ¿Qué deseas hacer hoy?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔍 Evaluador")
    st.write("Busca y analiza acciones, fondos y ETFs con tus métricas.")

with col2:
    st.markdown("#### 🔮 Proyección")
    st.write("Simula cuánto dinero ganarás a largo plazo.")

with col3:
    st.markdown("#### 📊 Cartera Real")
    st.write("Haz el seguimiento manual de tu patrimonio y dividendos.")
