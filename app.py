import streamlit as st

st.set_page_config(
    page_title="Plataforma Financiera", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Plataforma Financiera Multifuente")
st.markdown("Bienvenido a tu centro de control de inversiones.")

st.info("👈 Utiliza el **menú lateral izquierdo** para moverte entre tus 3 herramientas principales.")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 📈 1. Analizador")
    st.write("Busca acciones, fondos y ETFs, consulta métricas y gestiona tus favoritos.")
with col2:
    st.markdown("### 💼 2. Mi Cartera (Simulador)")
    st.write("Calcula proyecciones a largo plazo, comisiones de brókers y auditoría de solapamientos.")
with col3:
    st.markdown("### 📊 3. Cartera Real")
    st.write("Sigue tu patrimonio real metiendo compras manuales con precios de cierre y flechitas de mercado.")
