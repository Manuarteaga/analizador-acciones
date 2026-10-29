import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json
import urllib.parse

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #0f172a;
        padding: 10px 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ESTADO INICIAL DE LA APLICACIÓN
# ---------------------------------------------------------
if 'custom_assets_a' not in st.session_state:
    st.session_state.custom_assets_a = []
if 'custom_assets_b' not in st.session_state:
    st.session_state.custom_assets_b = []
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "landing"  # "landing" o "app_principal"
if 'selected_asset_query' not in st.session_state:
    st.session_state.selected_asset_query = ""

# Base de datos global unificada de productos (Fondos, ETFs, Monetarios y Bonos)
market_products = {
    "Vanguard S&P 500 ETF (VOO)": {"tipo": "ETF", "isin": "US9229083632", "ter": "0.03%", "rating": "4.9/5", "return": 8.0, "cat": "ETFs & Renta Variable"},
    "iShares Core S&P 500 ETF (IVV)": {"tipo": "ETF", "isin": "US4642872000", "ter": "0.03%", "rating": "4.9/5", "return": 8.0, "cat": "ETFs & Renta Variable"},
    "Vanguard FTSE All-World (Acc)": {"tipo": "Fondo Indexado", "isin": "IE00BK5BQT80", "ter": "0.22%", "rating": "4.8/5", "return": 7.5, "cat": "Fondos Indexados"},
    "Amundi Prime Global UCITS ETF": {"tipo": "ETF", "isin": "LU1931974698", "ter": "0.05%", "rating": "4.7/5", "return": 7.4, "cat": "ETFs & Renta Variable"},
    "Invesco QQQ (Nasdaq 100)": {"tipo": "ETF", "isin": "US46090E1038", "ter": "0.20%", "rating": "4.9/5", "return": 9.2, "cat": "Tecnología & ETFs"},
    "AXA Court Terme AC (Monetario)": {"tipo": "Fondo Monetario", "isin": "FR0000447823", "ter": "0.15%", "rating": "4.8/5", "return": 3.2, "cat": "Fondos Monetarios"},
    "Groupama Trésorerie IC (Monetario)": {"tipo": "Fondo Monetario", "isin": "FR0000989626", "ter": "0.12%", "rating": "4.8/5", "return": 3.3, "cat": "Fondos Monetarios"},
    "PIMCO Euro Short-Term Institutional": {"tipo": "Bonos", "isin": "IE00B11XZB05", "ter": "0.25%", "rating": "4.7/5", "return": 3.8, "cat": "Bonos & Renta Fija"},
    "Vanguard Global Bond Index Fund": {"tipo": "Bonos", "isin": "IE00B18GC888", "ter": "0.15%", "rating": "4.6/5", "return": 3.6, "cat": "Bonos & Renta Fija"}
}

asset_expectations = {name: data["return"] for name, data in market_products.items()}


# =========================================================
# 1. LANDING PAGE / BUSCADOR GENERAL UNIVERSAL
# =========================================================
if st.session_state.pagina_actual == "landing":
    st.title("🔍 Buscador Financiero Global y Acceso Táctico")
    st.write("Busca cualquier fondo, ETF, bono o acción internacional para evaluar su deuda y añadirlo a tus carteras.")
    
    st.markdown("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 3, 1])
    with col_l2:
        busqueda_global = st.text_input("🔎 Búsqueda universal por nombre, ticker o ISIN:", placeholder="Ej. VOO, MSFT, FR0000447823, S&P 500...")
        
        tipo_filtro = st.selectbox("📂 Filtrar por categoría de activo:", ["Todos los activos", "Fondos Indexados", "ETFs & Renta Variable", "Fondos Monetarios", "Bonos & Renta Fija"])
        
        resultados_filtrados = {}
        for nombre, info in market_products.items():
            coincide_texto = (busqueda_global.lower() in nombre.lower()) or (busqueda_global.lower() in info["isin"].lower())
            coincide_categoria = (tipo_filtro == "Todos los activos") or (tipo_filtro.lower() in info["cat"].lower())
            if coincide_texto and coincide_categoria:
                resultados_filtrados[nombre] = info
        
        st.write(f"Se han encontrado **{len(resultados_filtrados)}** activos coincidentes.")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Entrar al Analizador", use_container_width=True):
                st.session_state.pagina_actual = "app_principal"
                st.rerun()
        with col_btn2:
            if st.button("📊 Ir directo al Simulador", use_container_width=True):
                st.session_state.pagina_actual = "app_principal"
                st.rerun()
        
    if busqueda_global:
        st.markdown("### 📋 Resultados de la Búsqueda Rápida")
        if resultados_filtrados:
            for nom, det in resultados_filtrados.items():
                c_res1, c_res2, c_res3 = st.columns([3, 2, 2])
                c_res1.write(f"**{nom}** (`{det['isin']}`)")
                c_res2.caption(f"Categoría: {det['cat']} | TER: {det['ter']}")
                if c_res3.button(f"➕ Añadir a Cartera A", key=f"land_add_{nom}"):
                    st.session_state.custom_assets_a.append((nom, 1000.0, 100.0))
                    st.success(f"¡{nom} añadido a Cartera A!")
        else:
            st.info("No se han encontrado productos exactos en la base de datos interna con ese criterio.")

    st.markdown("---")
    st.markdown("### 🔥 Accesos Directos Populares")
    
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    if col_d1.button("Microsoft (MSFT)", use_container_width=True):
        st.session_state.pagina_actual = "app_principal"
        st.rerun()
    if col_d2.button("Vanguard S&P 500 (VOO)", use_container_width=True):
        st.session_state.pagina_actual = "app_principal"
        st.rerun()
    if col_d3.button("AXA Monetario EUR", use_container_width=True):
        st.session_state.pagina_actual = "app_principal"
        st.rerun()
    if col_d4.button("PIMCO Short-Term", use_container_width=True):
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
                    m2.metric("Gasto de Capital (CapEx)", f"${capex / 1e9:.2f} B" if capex is not None else "N/D")
                    m3.metric("Deuda Total", f"${total_debt / 1e9:.2f} B" if total_debt is not None else "N/D")
                    
                    st.markdown("---")
                    st.subheader("🚦 Sistema de Semáforo de Riesgo")
                    if fcf is not None and capex is not None:
                        if fcf < 0:
                            st.error("🔴 **ROJO (Riesgo Alto):** Caja libre negativa. Dependencia fuerte de emisión de deuda.")
                        elif fcf < capex:
                            st.warning("🟡 **AMARILLO (Precaución):** Positivo pero ajustado para cubrir todo el CapEx.")
                        else:
                            st.success("🟢 **VERDE (Sólido):** Excelente generación de caja libre.")
                    
                    st.markdown("---")
                    st.subheader(f"📦 Alternativas de Inversión Relacionadas con **{ticker_symbol}**")
                    
                    col_c1, col_c2, col_c3 = st.columns(3)
                    with col_c1:
                        st.markdown("### 📊 Fondos (Acumulación)")
                        st.markdown("• **Vanguard FTSE All-World (Acc)**")
                        st.caption("ISIN: `IE00BK5BQT80` | TER: **0.22%**")
                        b1, b2 = st.columns(2)
                        if b1.button("➕ Cartera A", key="ba1"): st.session_state.custom_assets_a.append(("Vanguard FTSE All-World (Acc)", 1000.0, 100.0))
                        if b2.button("➕ Cartera B", key="bb1"): st.session_state.custom_assets_b.append(("Vanguard FTSE All-World (Acc)", 1000.0, 100.0))
                    with col_c2:
                        st.markdown("### 💰 Fondos (Distribución)")
                        st.info("Sin fondos de distribución destacados.")
                    with col_c3:
                        st.markdown("### 🌐 ETFs Equivalentes")
                        st.markdown("• **Vanguard S&P 500 ETF (VOO)**")
                        st.caption("ISIN: `US9229083632` | TER: **0.03%**")
                        b3, b4 = st.columns(2)
                        if b3.button("➕ Cartera A", key="ba2"): st.session_state.custom_assets_a.append(("Vanguard S&P 500 ETF (VOO)", 1000.0, 100.0))
                        if b4.button("➕ Cartera B", key="bb2"): st.session_state.custom_assets_b.append(("Vanguard S&P 500 ETF (VOO)", 1000.0, 100.0))
                except Exception as e:
                    st.error(f"Error: {e}")

    # ---------------------------------------------------------
    # PESTAÑA 2
    # ---------------------------------------------------------
    with tab2:
        st.header("🌍 Comparador Global de Deuda & Fondos Monetarios")
        maturity = st.selectbox("Selecciona Plazo:", ["2 Años", "5 Años", "10 Años (Referencia)", "30 Años"])
        
        st.warning("⚠️ Los bonos de EE.UU. operan principalmente a 10 años, mientras que Europa ofrece Letras a corto plazo.")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1: emisor_a = st.selectbox("Emisor A:", ["EE.UU. (Tesoro)", "España (Bono)", "Alemania (Bund)"])
        with col_d2: emisor_b = st.selectbox("Emisor B:", ["España (Bono)", "Alemania (Bund)", "Microsoft (Corporativo)"])
        
        st.markdown("### 💰 Monetarios Recomendados")
        cm1, cm2 = st.columns(2)
        if cm1.button("➕ Añadir AXA Monetario a A"): st.session_state.custom_assets_a.append(("AXA Court Terme AC (Monetario)", 2000.0, 100.0))
        if cm2.button("➕ Añadir PIMCO Short-Term a B"): st.session_state.custom_assets_b.append(("PIMCO Euro Short-Term Institutional", 2000.0, 100.0))

    # ---------------------------------------------------------
    # PESTAÑA 3
    # ---------------------------------------------------------
    with tab3:
        st.header("📊 Simulador Avanzado de Carteras")
        years = st.slider("Horizonte Temporal (Años):", 1, 10, 5)
        
        def calcular_cartera(lista_activos, anos):
            if not lista_activos: return 0, 0, 0, 0
            val_fin, tot_ap = 0, 0
            meses = anos * 12
            for nombre, ini, mes in lista_activos:
                rent = asset_expectations.get(nombre, 5.0)
                r_m = (1 + rent / 100) ** (1 / 12) - 1
                v, t = ini, ini
                for _ in range(meses):
                    v = (v + mes) * (1 + r_m)
                    t += mes
                val_fin += v
                tot_ap += t
            return val_fin, tot_ap, val_fin - tot_ap, 6.0

        c_a, c_b = st.columns(2)
        with c_a:
            st.subheader("💼 Cartera A")
            for idx, item in enumerate(st.session_state.custom_assets_a):
                st.write(f"• {item[0]}")
                c1, c2, c3 = st.columns([2, 2, 1])
                new_ini = c1.number_input("Inicial", value=float(item[1]), key=f"ia_{idx}")
                new_mes = c2.number_input("Mensual", value=float(item[2]), key=f"ma_{idx}")
                st.session_state.custom_assets_a[idx] = (item[0], new_ini, new_mes)
                if c3.button("🗑️", key=f"da_{idx}"):
                    st.session_state.custom_assets_a.pop(idx)
                    st.rerun()
            
            with st.form("fa", clear_on_submit=True):
                act = st.selectbox("Añadir activo", list(market_products.keys()))
                i_ini = st.number_input("Inversión Inicial", 1000.0)
                i_mes = st.number_input("Aportación Mensual", 100.0)
                if st.form_submit_button("Añadir a Cartera A"):
                    st.session_state.custom_assets_a.append((act, i_ini, i_mes))
                    st.rerun()
            v_a, ta_a, g_a, rp_a = calcular_cartera(st.session_state.custom_assets_a, years)

        with c_b:
            st.subheader("💼 Cartera B")
            for idx, item in enumerate(st.session_state.custom_assets_b):
                st.write(f"• {item[0]}")
                c1, c2, c3 = st.columns([2, 2, 1])
                new_ini = c1.number_input("Inicial", value=float(item[1]), key=f"ib_{idx}")
                new_mes = c2.number_input("Mensual", value=float(item[2]), key=f"mb_{idx}")
                st.session_state.custom_assets_b[idx] = (item[0], new_ini, new_mes)
                if c3.button("🗑️", key=f"db_{idx}"):
                    st.session_state.custom_assets_b.pop(idx)
                    st.rerun()
                    
            with st.form("fb", clear_on_submit=True):
                act = st.selectbox("Añadir activo", list(market_products.keys()), key="actb")
                i_ini = st.number_input("Inversión Inicial", 1000.0, key="inib")
                i_mes = st.number_input("Aportación Mensual", 100.0, key="mesb")
                if st.form_submit_button("Añadir a Cartera B"):
                    st.session_state.custom_assets_b.append((act, i_ini, i_mes))
                    st.rerun()
            v_b, ta_b, g_b, rp_b = calcular_cartera(st.session_state.custom_assets_b, years)

        st.markdown("---")
        ra, rb = st.columns(2)
        ra.metric("Valor Final Cartera A", f"{v_a:,.2f} €", delta=f"+{g_a:,.2f} € Netos")
        rb.metric("Valor Final Cartera B", f"{v_b:,.2f} €", delta=f"+{g_b:,.2f} € Netos")
