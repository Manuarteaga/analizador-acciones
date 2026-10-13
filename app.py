import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cartera Real", page_icon="📊", layout="wide")

st.title("📊 Cartera Real & Seguimiento de Patrimonio")
st.write("Control manual de tus inversiones con precios y variación de mercado.")

# 1. Métricas superiores de resumen
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Valor Total Cartera", value="12,450.00 €", delta="+1,230.00 € (10.9%)")
with col2:
    st.metric(label="Inversión Inicial", value="11,220.00 €")
with col3:
    st.metric(label="Dividendos Previstos (Año)", value="340.00 €", delta="Seguro")

st.divider()

# 2. Datos de ejemplo para tu tabla estilo Excel
data = {
    "Activo / Ticker": ["AAPL", "VWCE"],
    "Tipo": ["Acción", "ETF"],
    "Títulos": [10, 50],
    "Precio Compra Med. (€)": [150.00, 95.20],
    "Precio Actual (€)": [175.50, 98.10],
    "Variación Día": ["+2.34%", "-0.45%"],
    "Valor Total (€)": [1755.00, 4905.00]
}

df = pd.DataFrame(data)

st.subheader("Tus Posiciones Actuales")

# Mostramos la tabla interactiva de Streamlit (estilo Excel)
st.dataframe(df, use_container_width=True)

# 3. Botón para añadir transacciones manuales
with st.expander("➕ Añadir nueva compra / transacción manual"):
    with st.form("form_transaccion"):
        col_a, col_b = st.columns(2)
        with col_a:
            ticker_input = st.text_input("Ticker o Nombre del Activo (ej: MSFT, S&P500)")
            tipo_input = st.selectbox("Tipo de Activo", ["Acción", "ETF", "Fondo"])
            cantidad_input = st.number_input("Número de Títulos / Unidades", min_value=0.01, value=1.0)
        with col_b:
            precio_input = st.text_input("Precio de Compra Unitario (€)")
            fecha_input = st.date_input("Fecha de Compra")
            
        submitted = st.form_submit_button("Guardar Transacción")
        if submitted:
            st.success(f"¡Transacción de {ticker_input} guardada correctamente!")
