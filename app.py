import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 60px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    .circular-progress {
        position: relative;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(var(--progress-color) var(--deg), #334155 0deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
    }
    .circular-progress::before {
        content: "";
        position: absolute;
        width: 96px;
        height: 96px;
        border-radius: 50%;
        background-color: #0f172a;
    }
    .progress-value {
        position: relative;
        font-size: 1.8rem;
        font-weight: bold;
        color: #f8fafc;
    }
    .pure-stamp-grade {
        font-family: 'Courier New', Courier, monospace;
        font-size: 5.5rem;
        font-weight: 900;
        line-height: 1;
        color: var(--stamp-color);
        text-transform: uppercase;
        transform: rotate(-8deg);
        display: inline-block;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.4), 0 0 15px var(--stamp-color);
        animation: stampPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    @keyframes stampPop {
        0% { transform: scale(2.2) rotate(-20deg); opacity: 0; }
        100% { transform: scale(1) rotate(-8deg); opacity: 0.95; }
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador Bursátil Multifuente (Yahoo Finance)")
st.markdown("Compara las métricas financieras con control de dividendos y pronósticos visuales.")

if 'history' not in st.session_state:
    st.session_state.history = []

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Pagos estables y extraordinarios)."},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Sin recortes históricos)."},
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular."},
    "sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular."},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con ajustes en crisis pasadas."},
    "santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con ajustes en crisis pasadas."},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular / Reestructuraciones de deuda."},
    "telefónica": {"ticker": "TEF.MC", "racha": "Irregular / Reestructuraciones de deuda."},
    "microsoft": {"ticker": "MSFT", "racha": "Más de 20 años incrementando dividendo."},
    "procter & gamble": {"ticker": "PG", "racha": "Aristócrata del Dividendo (+65 años)."},
    "copart": {"ticker": "CPRT", "racha": "Sin historial (Pura de crecimiento)."},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sensible al sector bancario."}
}

with st.sidebar:
    st.header("📊 Historial de Sesión")
    st.markdown(f"Empresas analizadas: **{len(st.session_state.history)}**")
    
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_history.to_excel(writer, sheet_name='Evaluaciones', index=False)
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Descargar Excel de la Sesión",
            data=excel_data,
            file_name="historial_multifuente.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
        if st.button("🗑️ Borrar Historial"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Analiza alguna empresa para habilitar la exportación.")

col1, col2 = st.columns([2, 1])
with col1:
    user_input = st.text_input("Nombre de empresa o Ticker", value="Inditex").strip()
with col2:
    strategy = st.selectbox("Estrategia", ["Dividendo", "Crecimiento / Sin Dividendo"])

def get_stock_data(query):
    q_lower = query.lower()
    if q_lower in TICKER_DB:
        return TICKER_DB[q_lower]["ticker"], TICKER_DB[q_lower]["racha"]
    return query.upper(), "Sin datos de racha previos (Evaluación estándar)."

def get_letter_grade(score):
    if score >= 5.0: return "A+"
    elif score >= 4.0: return "A"
    elif score >= 3.0: return "B"
    elif score >= 2.0: return "C"
    else: return "D"

if st.button("Ejecutar Análisis Multifuente", type="primary"):
    if not user_input:
        st.warning("Por favor, introduce un nombre o ticker

