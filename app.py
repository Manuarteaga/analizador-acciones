import streamlit as st

st.set_page_config(
    page_title="Plataforma Financiera", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Contenido de la página de inicio (app.py)
st.title("📈 Plataforma Financiera Multifuente")
st.markdown("Bienvenido a tu centro de control de inversiones.")

st.info("👈 Utiliza el **menú lateral izquierdo** que aparece arriba para moverte entre el **Analizador** y tu **Cartera Consolidada**.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📈 1. Analizador Bursátil")
    st.write("Busca acciones, fondos y ETFs, consulta métricas, evalúa el TER y descubre recomendaciones.")
with col2:
    st.markdown("### 💼 2. Cartera Consolidada")
    st.write("Gestiona tus activos añadidos, configura plazos, brókers y analiza el desglose anual y fiscal.")
