import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Analizador Bursatil", page_icon="📈", layout="wide")

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
    .progress-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #f8fafc;
        text-align: center;
    }
    .pure-stamp-grade {
        font-family: 'Courier New', Courier, monospace;
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 1;
        color: var(--stamp-color);
        text-transform: uppercase;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.4);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador Bursatil Multifuente")
st.markdown("Compara metricas financieras y evalua proyecciones de crecimiento a corto plazo en tiempo real.")

if 'history' not in st.session_state:
    st.session_state.history = []

TICKER_DB = {
    "inditex": ("ITX.MC", "Muy alta (Pagos estables)."),
    "iberdrola": ("IBE.MC", "Impecable (Sin recortes)."),
    "sabadell": ("SAB.MC", "Ciclica e irregular."),
    "santander": ("SAN.MC", "Ciclica con ajustes."),
    "telefonica": ("TEF.MC", "Irregular con deuda."),
    "microsoft": ("MSFT", "+20 anos subiendo dividendo."),
    "procter": ("PG", "Aristocrata (+65 anos)."),
    "copart": ("CPRT", "Sin historial (Crecimiento)."),
    "caixabank": ("CABK.MC", "Ciclica sectorial.")
