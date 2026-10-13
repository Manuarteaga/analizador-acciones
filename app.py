import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json
import urllib.parse

# 1. ÚNICA CONFIGURACIÓN DE PÁGINA GLOBAL
st.set_page_config(
    page_title="Plataforma Financiera Multifuente", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📈 Plataforma Financiera Multifuente")

# Menú superior horizontal con pestañas
pestana = st.radio(
    "Selecciona una herramienta:",
    ["🏠 Inicio", "📈 1. Analizador", "💼 2. Mi Cartera (Simulador)", "📊 3. Cartera Real"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# ====================================================
# PESTAÑA 0: INICIO
# ====================================================
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

# ====================================================
# PESTAÑA 1: ANALIZADOR
# ====================================================
elif pestana == "📈 1. Analizador":
    st.markdown("""
    <style>
        .top-bar { display: flex; justify-content: space-between; align-items: center; background-color: #0f172a; padding: 10px 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 25px; }
        .score-container { display: flex; align-items: center; justify-content: center; gap: 40px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); margin-bottom: 20px; border: 1px solid #334155; flex-wrap: wrap; }
        .circular-progress { position: relative; width: 110px; height: 110px; border-radius: 50%; background: conic-gradient(var(--progress-color) var(--deg), #334155 0deg); display: flex; align-items: center; justify-content: center; box-shadow: inset 0 0 15px rgba(0,0,0,0.5); }
        .circular-progress::before { content: ""; position: absolute; width: 88px; height: 88px; border-radius: 50%; background-color: #0f172a; }
        .progress-value { position: relative; font-size: 1.6rem; font-weight: bold; color: #f8fafc; }
        .pure-stamp-grade { font-family: 'Courier New', Courier, monospace; font-size: 5rem; font-weight: 900; line-height: 1; color: var(--stamp-color); text-transform: uppercase; transform: rotate(-8deg); display: inline-block; text-shadow: 3px 3px 0px rgba(0,0,0,0.8), 0 0 5px rgba(0,0,0,0.5); }
        .final-net-card { background: linear-gradient(135deg, #065f46 0%, #047857 100%); border: 2px solid #34d399; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 8px 20px rgba(4, 120, 87, 0.3); margin-top: 20px; margin-bottom: 20px; }
        .final-net-title { font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #a7f3d0; margin-bottom: 5px; font-weight: 600; }
        .final-net-value { font-size: 2.2rem; font-weight: 800; color: #ffffff; }
        .featured-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #38bdf8; border-radius: 12px; padding: 22px; margin-bottom: 10px; }
        .featured-badge { background-color: #0284c7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 8px; }
        .score-tag { background-color: #065f46; color: #34d399; padding: 3px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; float: right; }
    </style>
    """, unsafe_allow_html=True)

    if 'stage' not in st.session_state:
        st.session_state.stage = 'home'
    if 'asset_type' not in st.session_state:
        st.session_state.asset_type = None
    if 'sub_type' not in st.session_state:
        st.session_state.sub_type = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    if 'selected_eval_input' not in st.session_state:
        st.session_state.selected_eval_input = ""

    def guardar_en_url():
        try:
            st.query_params["favs"] = json.dumps(st.session_state.favorites)
            st.query_params["port"] = json.dumps(st.session_state.portfolio)
        except:
            pass

    def reset_navigation():
        st.session_state.stage = 'home'
        st.session_state.asset_type = None
        st.session_state.sub_type = None
        st.session_state.selected_eval_input = ""

    TICKER_DB = {
        "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios).", "div_growth": 6.5, "div_yield": 2.8, "per": 24.0, "beta": 0.95, "payout": 60.0},
        "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos).", "div_growth": 5.0, "div_yield": 4.8, "per": 16.5, "beta": 0.65, "payout": 70.0},
        "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico sin dependencia de dividendo tradicional.", "div_growth": 10.0, "div_yield": 0.7, "per": 32.0, "beta": 0.90, "payout": 25.0}
    }

    FUND_DB = {
        "vanguard global stock acc": {
            "name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "IE00B03HD191",
            "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 23000, "tracking_error": 0.08, "age_years": 15, "currency": "EUR", "is_dist": False, "return_1y": 16.2, "score": 4.6,
            "desc": "Fondo indexado global que replica el MSCI World.",
            "geo": {"EE. UU.": 71.5, "Europa": 14.5, "Otros": 14.0},
            "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "Resto": 90.0}
        }
    }

    ETF_DB = {
        "spyl.de": {
            "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
            "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000,
            "replication": "Física", "te": 0.01, "currency": "EUR", "age_years": 3, "is_dist": False, "return_1y": 22.3, "score": 4.9,
            "desc": "ETF del S&P 500 con el coste más bajo de Europa.",
            "geo": {"EE. UU.": 100.0},
            "holdings": {"Apple Inc.": 7.1, "Microsoft": 6.8, "Resto": 86.1}
        }
    }

    if st.session_state.stage == 'home':
        st.markdown("### ¿Qué tipo de activo quieres evaluar?")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 Acciones", use_container_width=True, type="primary"):
                st.session_state.asset_type = "Acciones"
                st.session_state.stage = "sub_options"
                st.rerun()
        with col2:
            if st.button("📁 Fondos Indexados", use_container_width=True, type="primary"):
                st.session_state.asset_type = "Fondos indexados"
                st.session_state.stage = "sub_options"
                st.rerun()
        with col3:
            if st.button("🌐 ETFs", use_container_width=True, type="primary"):
                st.session_state.asset_type = "ETFs"
                st.session_state.stage = "sub_options"
                st.rerun()

    elif st.session_state.stage == 'sub_options':
        if st.button("← Volver a selección"):
            reset_navigation()
            st.rerun()
        st.title(f"Configuración para: {st.session_state.asset_type}")
        if st.button("Ir al Evaluador Directo"):
            st.session_state.stage = "analyzer"
            st.rerun()

    elif st.session_state.stage == 'analyzer':
        if st.button("← Volver"):
            st.session_state.stage = 'home'
            st.rerun()
        st.title("🔍 Evaluador de Activos")
        st.write("Aquí puedes buscar y evaluar tus acciones, fondos o ETFs.")

# ====================================================
# PESTAÑA 2: MI CARTERA (SIMULADOR)
# ====================================================
elif pestana == "💼 2. Mi Cartera (Simulador)":
    st.header("💼 Simulador Global de Cartera Consolidada")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía. Añade activos desde la pestaña **Analizador**.")
    else:
        st.write("Aquí se muestra el desglose y proyección de tu cartera consolidada.")
        for idx, item in enumerate(st.session_state.portfolio):
            st.write(f"- {item['name']} ({item['ticker']})")

# ====================================================
# PESTAÑA 3: CARTERA REAL
# ====================================================
elif pestana == "📊 3. Cartera Real":
    st.header("📊 Seguimiento de Cartera Real y Patrimonio")
    st.write("Control manual de tus inversiones con precios de cierre y variación de mercado.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Valor Total Cartera", value="12,450.00 €", delta="+1,230.00 € (10.9%)")
    with col2:
        st.metric(label="Inversión Inicial", value="11,220.00 €")
    with col3:
        st.metric(label="Dividendos Previstos", value="340.00 €")

    st.divider()

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
    st.dataframe(df, use_container_width=True)

    with st.expander("➕ Añadir nueva compra / transacción manual"):
        with st.form("form_transaccion"):
            col_a, col_b = st.columns(2)
            with col_a:
                ticker_input = st.text_input("Ticker o Nombre del Activo")
                tipo_input = st.selectbox("Tipo de Activo", ["Acción", "ETF", "Fondo"])
            with col_b:
                cantidad_input = st.number_input("Número de Títulos", min_value=0.01, value=1.0)
                precio_input = st.number_input("Precio de Compra (€)", min_value=0.0, value=100.0)
                
            submitted = st.form_submit_button("Guardar Transacción")
            if submitted:
                st.success(f"¡Transacción de {ticker_input} guardada correctamente!")
