import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Buscador Financiero Global & Simulador",
    page_icon="🔍",
    layout="wide"
)

# Inicializar Session State para las carteras y la navegación
if "custom_assets_a" not in st.session_state:
    st.session_state.custom_assets_a = []
if "custom_assets_b" not in st.session_state:
    st.session_state.custom_assets_b = []
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "landing"  # "landing" o "app_principal"

# Base de datos global de productos
market_products = {
    "Vanguard S&P 500 ETF (VOO)": {"tipo": "ETF", "isin": "US9229083632", "ter": "0.03%", "rating": "4.9/5", "return": 8.0},
    "iShares Core S&P 500 ETF (IVV)": {"tipo": "ETF", "isin": "US4642872000", "ter": "0.03%", "rating": "4.9/5", "return": 8.0},
    "Vanguard FTSE All-World (Acc)": {"tipo": "Fondo Indexado", "isin": "IE00BK5BQT80", "ter": "0.22%", "rating": "4.8/5", "return": 7.5},
    "Amundi Prime Global UCITS ETF": {"tipo": "ETF", "isin": "LU1931974698", "ter": "0.05%", "rating": "4.7/5", "return": 7.4},
    "Invesco QQQ (Nasdaq 100)": {"tipo": "ETF", "isin": "US46090E1038", "ter": "0.20%", "rating": "4.9/5", "return": 9.2},
    "AXA Court Terme AC (Monetario)": {"tipo": "Fondo Monetario", "isin": "FR0000447823", "ter": "0.15%", "rating": "4.8/5", "return": 3.2},
    "Groupama Trésorerie IC (Monetario)": {"tipo": "Fondo Monetario", "isin": "FR0000989626", "ter": "0.12%", "rating": "4.8/5", "return": 3.3},
    "PIMCO Euro Short-Term Institutional": {"tipo": "Bonos", "isin": "IE00B11XZB05", "ter": "0.25%", "rating": "4.7/5", "return": 3.8},
    "Vanguard Global Bond Index Fund": {"tipo": "Bonos", "isin": "IE00B18GC888", "ter": "0.15%", "rating": "4.6/5", "return": 3.6}
}

asset_expectations = {name: data["return"] for name, data in market_products.items()}


# =========================================================
# 1. LANDING PAGE / BUSCADOR GENERAL PREVIO
# =========================================================
if st.session_state.pagina_actual == "landing":
    st.markdown("<h1 style='text-align: center;'>🔍 Buscador Financiero Global</h1>", unsafe_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Explora cualquier activo, acción internacional, fondo, ETF o bono antes de entrar al evaluador de carteras.</p>", unsafe_html=True)
    
    st.markdown("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        busqueda_global = st.text_input("Introduce el nombre, ticker o ISIN a buscar:", placeholder="Ej. AAPL, VOO, MSFT, SP500...")
        tipo_filtro = st.selectbox("Filtrar por categoría:", ["Todos los activos", "Acciones / Big Tech", "Fondos Indexados & ETFs", "Bonos & Monetarios"])
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Buscar y Analizar", use_container_width=True):
                st.session_state.pagina_actual = "app_principal"
                st.rerun()
        with col_btn2:
            if st.button("📊 Ir directo al Simulador", use_container_width=True):
                st.session_state.pagina_actual = "app_principal"
                st.rerun()
                
    st.markdown("---")
    st.markdown("### 🔥 Accesos Directos Populares")
    
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    if col_d1.button("Microsoft (MSFT)", use_container_width=True):
        st.session_state.pagina_actual = "app_principal"
        st.rerun()
    if col_d2.button("Apple (AAPL)", use_container_width=True):
        st.session_state.pagina_actual = "app_principal"
        st.rerun()
    if col_d3.button("S&P 500 (VOO)", use_container_width=True):
        st.session_state.pagina_actual = "app_principal"
        st.rerun()
    if col_d4.button("Fondos Monetarios", use_container_width=True):
        st.session_state.pagina_actual = "app_principal"
        st.rerun()

# =========================================================
# 2. APLICACIÓN PRINCIPAL (LAS TRES PESTAÑAS)
# =========================================================
else:
    if st.button("⬅️ Volver al Buscador General (Landing)"):
        st.session_state.pagina_actual = "landing"
        st.rerun()
        
    st.title("⚖️ Evaluador Bursátil, Deuda Global y Simulador Avanzado")
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "🏢 Buscador, Semáforo & Alternativas", 
        "🌍 Comparador de Deuda & Monetarios", 
        "📊 Simulador Avanzado de Carteras"
    ])

    # ---------------------------------------------------------
    # PESTAÑA 1
    # ---------------------------------------------------------
    with tab1:
        st.header("🏢 Analizador de Salud Financiera & Alternativas Equivalentes")
        
        modo_busqueda = st.radio("Origen de la empresa:", ["Big Tech (Predefinidas)", "Buscador Libre por Ticker (Global)"], key="mod_b1")
        
        if modo_busqueda == "Big Tech (Predefinidas)":
            ticker_dict = {
                "Microsoft (MSFT)": "MSFT",
                "Alphabet / Google (GOOGL)": "GOOGL",
                "Meta (META)": "META",
                "Amazon (AMZN)": "AMZN",
                "Oracle (ORCL)": "ORCL",
                "Apple (AAPL)": "AAPL",
                "Nvidia (NVDA)": "NVDA"
            }
            selected_name = st.selectbox("Selecciona empresa:", list(ticker_dict.keys()))
            ticker_symbol = ticker_dict[selected_name]
        else:
            ticker_symbol = st.text_input("Introduce el Ticker de Yahoo Finance (ej. TSLA, SAN.MC):", "TSLA").upper().strip()
        
        if ticker_symbol:
            with st.spinner(f"Consultando datos en tiempo real para {ticker_symbol}..."):
                try:
                    ticker = yf.Ticker(ticker_symbol)
                    cashflow = ticker.cashflow
                    balance = ticker.balance_sheet
                    
                    fcf, capex, total_debt = None, None, None
                    if cashflow is not None and not cashflow.empty:
                        if 'Free Cash Flow' in cashflow.index:
                            fcf = cashflow.loc['Free Cash Flow'].iloc[0]
                        if 'Capital Expenditure' in cashflow.index:
                            capex = abs(cashflow.loc['Capital Expenditure'].iloc[0])
                    if balance is not None and not balance.empty:
                        if 'Total Debt' in balance.index:
                            total_debt = balance.loc['Total Debt'].iloc[0]

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Flujo de Caja Libre (FCF)", f"${fcf / 1e9:.2f} B" if fcf is not None else "N/D")
                    m2.metric("Gasto de Capital (CapEx)", f"${capex / 1e9:.2f} B" if capex is not None else "N/D
