import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

# Estilos CSS
st.markdown("""
<style>
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 40px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    .final-net-card {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        border: 2px solid #34d399;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .final-net-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        color: #a7f3d0;
        font-weight: 600;
    }
    .final-net-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Control de Estados
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'real_portfolio' not in st.session_state:
    st.session_state.real_portfolio = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# Bases de datos completas
TICKER_DB = {
    "itx.mc": {"ticker": "ITX.MC", "name": "Inditex S.A.", "ter": 0.0, "category": "Acciones ES"},
    "ibe.mc": {"ticker": "IBE.MC", "name": "Iberdrola S.A.", "ter": 0.0, "category": "Acciones ES"},
    "msft": {"ticker": "MSFT", "name": "Microsoft Corp.", "ter": 0.0, "category": "Acciones US"},
    "aapl": {"ticker": "AAPL", "name": "Apple Inc.", "ter": 0.0, "category": "Acciones US"}
}

FUND_DB = {
    "ie00b03hd191": {"name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "IE00B03HD191", "ter": 0.18, "category": "Renta Variable Global", "return_1y": 15.5},
    "ie0032126645": {"name": "Vanguard U.S. 500 Stock Index Fund EUR Acc", "ticker": "IE0032126645", "ter": 0.10, "category": "Renta Variable EE.UU.", "return_1y": 22.0},
    "ie00byx5mx67": {"name": "Fidelity S&P 500 Index Fund EUR P Acc", "ticker": "IE00BYX5MX67", "ter": 0.06, "category": "Renta Variable EE.UU.", "return_1y": 22.5}
}

ETF_DB = {
    "vwce.de": {"name": "Vanguard FTSE All-World UCITS ETF", "ticker": "VWCE.DE", "ter": 0.22, "category": "Renta Variable Global", "return_1y": 16.0},
    "spyl.de": {"name": "SPDR S&P 500 UCITS ETF", "ticker": "SPYL.DE", "ter": 0.03, "category": "Renta Variable EE.UU.", "return_1y": 22.3},
    "swda.l": {"name": "iShares Core MSCI World UCITS ETF", "ticker": "SWDA.L", "ter": 0.20, "category": "Renta Variable Global", "return_1y": 15.7}
}

# Encabezado principal
st.title("📈 Analizador Bursátil & Gestor de Inversiones")

# Landing Principal mediante Pestañas (Tabs)
tab_inicio, tab_analizador, tab_cartera_real, tab_simulador, tab_favoritos = st.tabs([
    "🏠 Inicio / Orientación", 
    "🔍 Buscador / Analizador (Yahoo)", 
    "💼 Mi Cartera Real", 
    "🧮 Simulador Proyección", 
    "⭐ Favoritos"
])

# ----------------------------------------------------
# 1. PESTAÑA: INICIO / ORIENTACIÓN
# ----------------------------------------------------
with tab_inicio:
    st.markdown("### Bienvenido al Centro de Análisis Financiero")
    st.write("Selecciona lo que deseas hacer a través de las pestañas superiores o utiliza el asistente rápido.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🔍 **Analizar Activos**\nConsulta métricas, precios en directo de Yahoo Finance y desglose de fondos o ETFs.")
    with col2:
        st.success("💼 **Cartera Real**\nLleva el seguimiento de tus posiciones reales, ganancias/pérdidas no realizadas y rentabilidad.")
    with col3:
        st.warning("🧮 **Simulador Proyectado**\nCalcula el crecimiento futuro de tu cartera considerando comisiones, inflación e impuestos.")

    st.markdown("---")
    st.markdown("### 🧭 Asistente Rápido de Elección")
    q_goal = st.radio(
        "¿Cuál es tu horizonte principal de inversión?",
        ["Largo plazo (Jubilación / Independencia Financiera)", "Corto/Medio plazo (Vivienda, coche, imprevistos)"]
    )
    if q_goal.startswith("Largo"):
        st.success("💡 **Sugerencia:** Para horizontes a largo plazo, considera **ETFs o Fondos Indexados de bajo coste (TER < 0.20%)** orientados a índices globales o al S&P 500.")
    else:
        st.info("💡 **Sugerencia:** Para horizontes a menor plazo, prioriza **Fondos Indexados** por su flexibilidad para traspasar capital sin peaje fiscal inmediato en España.")

# ----------------------------------------------------
# 2. PESTAÑA: ANALIZADOR / BÚSQUEDA MULTIFUENTE Y YAHOO FINANCE
# ----------------------------------------------------
with tab_analizador:
    st.subheader("🔍 Buscador y Analizador Multifuente")
    
    asset_type = st.radio("Tipo de activo:", ["Acciones", "Fondos Indexados", "ETFs"], horizontal=True)
    user_query = st.text_input("Escribe el Ticker, ISIN o Nombre del activo:", placeholder="Ej. AAPL, ITX.MC, VWCE.DE, IE00B03HD191").strip().lower()

    if user_query:
        found_data = None
        ticker_to_fetch = user_query.upper()
        
        # Búsqueda en bases de datos locales
        if asset_type == "Acciones":
            for k, v in TICKER_DB.items():
                if user_query in k or user_query in v["name"].lower() or user_query == v["ticker"].lower():
                    found_data = v
                    ticker_to_fetch = v["ticker"]
                    break
        elif asset_type == "Fondos Indexados":
            for k, v in FUND_DB.items():
                if user_query in k or user_query in v["name"].lower() or user_query == v["ticker"].lower():
                    found_data = v
                    ticker_to_fetch = v["ticker"]
                    break
        elif asset_type == "ETFs":
            for k, v in ETF_DB.items():
                if user_query in k or user_query in v["name"].lower() or user_query == v["ticker"].lower():
                    found_data = v
                    ticker_to_fetch = v["ticker"]
                    break

        st.markdown(f"**Buscando activo:** `{ticker_to_fetch}`")
        
        try:
            yf_obj = yf.Ticker(ticker_to_fetch)
            info = yf_obj.info or {}
            hist = yf_obj.history(period="1mo")
            
            price = hist['Close'].iloc[-1] if not hist.empty else info.get('regularMarketPrice', 0.0)
            currency = info.get('currency', 'EUR')
            long_name = info.get('longName') or (found_data["name"] if found_data else ticker_to_fetch)
            ter = found_data.get("ter", 0.0) if found_data else 0.0
            category = found_data.get("category", info.get('sector', 'General')) if found_data else info.get('sector', 'General')

            st.success(f"¡Activo encontrado: **{long_name}**!")

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Precio / Valor Liquidativo", f"{price:,.2f} {currency}" if price else "N/D")
            col_m2.metric("Categoría", category)
            col_m3.metric("Gastos (TER)", f"{ter:.2f}%")
            col_m4.metric("PER", f"{info.get('trailingPE', 0.0):.2f}" if info.get('trailingPE') else "N/D")

            if not hist.empty:
                st.markdown("#### Evolución Reciente (1 Mes)")
                st.line_chart(hist['Close'])

            c_btn1, c_btn2, c_btn3 = st.columns(3)
            with c_btn1:
                if st.button("➕ Añadir a Cartera Real", use_container_width=True):
                    st.session_state.real_portfolio.append({
                        "ticker": ticker_to_fetch,
                        "name": long_name,
                        "shares": 1.0,
                        "buy_price": float(price) if price else 10.0,
                        "current_price": float(price) if price else 10.0,
                        "currency": currency
                    })
                    st.success(f"Añadido {long_name} a Cartera Real.")
            with c_btn2:
                if st.button("➕ Añadir a Cartera Simulada", use_container_width=True):
                    st.session_state.portfolio.append({
                        "ticker": ticker_to_fetch,
                        "name": long_name,
                        "shares": 1.0,
                        "price": float(price) if price else 10.0
                    })
                    st.success(f"Añadido {long_name} a Cartera Simulada.")
            with c_btn3:
                if st.button("⭐ Guardar en Favoritos", use_container_width=True):
                    st.session_state.favorites.append({"ticker": ticker_to_fetch, "name": long_name, "type": asset_type})
                    st.success(f"Añadido {long_name} a Favoritos.")

        except Exception as e:
            if found_data:
                st.warning(f"No se pudo conectar con Yahoo Finance para cotización en vivo, mostrando datos de registro local.")
                st.markdown(f"**Nombre:** {found_data['name']}")
                st.markdown(f"**Categoría:** {found_data['category']}")
                st.markdown(f"**TER:** {found_data['ter']}%")
            else:
                st.error(f"No se ha encontrado ningún activo con el término `{user_query}` ni en la base de datos local ni en Yahoo Finance.")

# ----------------------------------------------------
# 3. PESTAÑA: MI CARTERA REAL
# ----------------------------------------------------
with tab_cartera_real:
    st.subheader("💼 Gestión y Seguimiento de Cartera Real")
    
    if not st.session_state.real_portfolio:
        st.info("Aún no tienes posiciones reales añadidas. Usa el buscador o añádelas manualmente abajo.")
    
    with st.expander("➕ Añadir posición manualmente", expanded=False):
        with st.form("manual_add"):
            c1, c2, c3, c4 = st.columns(4)
            in_ticker = c1.text_input("Ticker / ISIN", "ITX.MC")
            in_name = c2.text_input("Nombre del Activo", "Inditex")
            in_shares = c3.number_input("Número de Títulos", min_value=0.01, value=10.0, step=1.0)
            in_buy_price = c4.number_input("Precio Medio de Compra (€)", min_value=0.01, value=35.0, step=0.5)
            
            submitted = st.form_submit_button("Añadir a Cartera Real")
            if submitted:
                st.session_state.real_portfolio.append({
                    "ticker": in_ticker.upper(),
                    "name": in_name,
                    "shares": in_shares,
                    "buy_price": in_buy_price,
                    "current_price": in_buy_price,
                    "currency": "EUR"
                })
                st.rerun()

    if st.session_state.real_portfolio:
        total_invertido = 0.0
        total_valor_actual = 0.0
        
        rows = []
        for pos in st.session_state.real_portfolio:
            try:
                t_data = yf.Ticker(pos["ticker"])
                h = t_data.history(period="1d")
                if not h.empty:
                    pos["current_price"] = float(h['Close'].iloc[-1])
            except:
                pass

            val_inv = pos["shares"] * pos["buy_price"]
            val_act = pos["shares"] * pos["current_price"]
            pnl = val_act - val_inv
            pnl_pct = (pnl / val_inv * 100) if val_inv > 0 else 0.0

            total_invertido += val_inv
            total_valor_actual += val_act

            rows.append({
                "Ticker": pos["ticker"],
                "Nombre": pos["name"],
                "Títulos": pos["shares"],
                "Precio Compra": f"{pos['buy_price']:,.2f} €",
                "Precio Actual": f"{pos['current_price']:,.2f} €",
                "Valor Invertido": f"{val_inv:,.2f} €",
                "Valor Actual": f"{val_act:,.2f} €",
                "Ganancia / Pérdida": f"{pnl:+,.2f} € ({pnl_pct:+.2f}%)"
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        pnl_total = total_valor_actual - total_invertido
        pnl_total_pct = (pnl_total / total_invertido * 100) if total_invertido > 0 else 0.0

        st.markdown(f"""
        <div class="final-net-card">
            <div class="final-net-title">Patrimonio Total en Cartera Real</div>
            <div class="final-net-value">{total_valor_actual:,.2f} €</div>
            <p style="color: #a7f3d0; margin-top: 5px;">
                Invertido: {total_invertido:,.2f} € | Resultado: <b>{pnl_total:+,.2f} € ({pnl_total_pct:+.2f}%)</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Vaciar Cartera Real"):
            st.session_state.real_portfolio = []
            st.rerun()

# ----------------------------------------------------
# 4. PESTAÑA: SIMULADOR DE INTERÉS COMPUESTO
# ----------------------------------------------------
with tab_simulador:
    st.subheader("🧮 Simulador Proyectado de Cartera")
    
    if st.session_state.portfolio:
        st.markdown("#### Activos en Cartera Simulada:")
        st.dataframe(pd.DataFrame(st.session_state.portfolio), use_container_width=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        inv_inicial = st.number_input("Inversión Inicial (€)", min_value=0, value=5000, step=500)
        aportacion_mensual = st.number_input("Aportación Mensual (€)", min_value=0, value=300, step=50)
    with col_s2:
        anos = st.slider("Plazo de Inversión (Años)", min_value=1, max_value=40, value=20)
        rentabilidad_anual = st.slider("Rentabilidad Anual Estimada (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.5)

    meses = anos * 12
    r_mensual = (rentabilidad_anual / 100) / 12
    
    saldo = float(inv_inicial)
    total_aportado = float(inv_inicial)
    
    for _ in range(meses):
        saldo = saldo * (1 + r_mensual) + aportacion_mensual
        total_aportado += aportacion_mensual
        
    beneficio_bruto = saldo - total_aportado
    impuestos_estimados = beneficio_bruto * 0.19
    saldo_neto = saldo - impuestos_estimados

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Aportado", f"{total_aportado:,.2f} €")
    m2.metric("Beneficio Bruto", f"{beneficio_bruto:,.2f} €")
    m3.metric("Impuestos Estimados (19%)", f"{impuestos_estimados:,.2f} €")

    st.markdown(f"""
    <div class="final-net-card">
        <div class="final-net-title">Capital Final Líquido Estimado</div>
        <div class="final-net-value">{saldo_neto:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# 5. PESTAÑA: FAVORITOS
# ----------------------------------------------------
with tab_favoritos:
    st.subheader("⭐ Lista de Activos Favoritos")
    
    if not st.session_state.favorites:
        st.info("No tienes ningún activo guardado en favoritos.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.favorites), use_container_width=True)
        if st.button("🗑️ Borrar Favoritos"):
            st.session_state.favorites = []
            st.rerun()
