import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

# Estilos CSS avanzados
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

# Bases de datos completas y detalladas con métricas, geo y holdings
TICKER_DB = {
    "itx.mc": {"ticker": "ITX.MC", "name": "Inditex S.A.", "ter": 0.0, "category": "Acciones ES", "score": 4.5, "return_1y": 18.4, "desc": "Líder mundial en distribución de moda rápida."},
    "ibe.mc": {"ticker": "IBE.MC", "name": "Iberdrola S.A.", "ter": 0.0, "category": "Acciones ES", "score": 4.3, "return_1y": 12.1, "desc": "Compañía energética global y líder en renovables."},
    "msft": {"ticker": "MSFT", "name": "Microsoft Corp.", "ter": 0.0, "category": "Acciones US", "score": 4.9, "return_1y": 24.5, "desc": "Gigante tecnológico de software, nube e inteligencia artificial."},
    "aapl": {"ticker": "AAPL", "name": "Apple Inc.", "ter": 0.0, "category": "Acciones US", "score": 4.8, "return_1y": 20.2, "desc": "Diseñador de electrónica de consumo, software y servicios en línea."}
}

FUND_DB = {
    "ie00b03hd191": {
        "name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "IE00B03HD191",
        "category": "Renta Variable Global", "ter": 0.18, "aum": 28000, "tracking_error": 0.04, "age_years": 15, "currency": "EUR", "is_dist": False, "return_1y": 15.5, "score": 4.8,
        "desc": "Fondo indexado global que replica el índice MSCI World.",
        "geo": {"EE. UU.": 68.0, "Europa": 16.0, "Japón": 6.0, "Otros": 10.0},
        "holdings": {"Apple Inc.": 5.1, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.2, "Amazon.com Inc.": 2.5, "Resto del Fondo": 83.4}
    },
    "ie0032126645": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc", "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU.", "ter": 0.10, "aum": 45000, "tracking_error": 0.03, "age_years": 18, "currency": "EUR", "is_dist": False, "return_1y": 22.0, "score": 4.9,
        "desc": "Fondo indexado que replica el S&P 500 con bajo coste.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Resto del Fondo": 76.4}
    }
}

ETF_DB = {
    "vwce.de": {
        "name": "Vanguard FTSE All-World UCITS ETF [Acumulación]", "ticker": "VWCE.DE",
        "category": "Renta Variable Global (All-World)", "ter": 0.22, "aum": 15000, "tracking_error": 0.04, "age_years": 7, "currency": "EUR", "is_dist": False, "return_1y": 16.0, "score": 4.8,
        "desc": "Incluye tanto países desarrollados como mercados emergentes (más de 3.700 valores).",
        "geo": {"EE. UU.": 62.5, "Mercados Emergentes": 10.5, "Japón": 5.8, "Europa": 15.2, "Otros": 6.0},
        "holdings": {"Apple Inc.": 4.5, "Microsoft Corp.": 4.2, "NVIDIA Corp.": 3.8, "Amazon.com Inc.": 2.3, "Resto del ETF": 85.2}
    },
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000, "tracking_error": 0.01, "age_years": 3, "currency": "EUR", "is_dist": False, "return_1y": 22.3, "score": 4.9,
        "desc": "El ETF del S&P 500 con el coste operativo más bajo de Europa (TER del 0.03%).",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Resto del ETF": 76.4}
    }
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
        st.info("🔍 **Analizar Activos**\nConsulta puntuaciones, métricas avanzadas, TER, desglose geográfico y precios en directo.")
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
            
            # Datos locales o estimados de respaldo
            score = found_data.get("score", 4.5) if found_data else 4.5
            ter = found_data.get("ter", 0.0) if found_data else 0.0
            category = found_data.get("category", info.get('sector', 'General')) if found_data else info.get('sector', 'General')
            desc = found_data.get("desc", info.get('longBusinessSummary', 'Sin descripción detallada.')) if found_data else 'Sin descripción.'
            return_1y = found_data.get("return_1y", 10.0) if found_data else 10.0
            aum = found_data.get("aum", 10000) if found_data else 10000
            tracking_error = found_data.get("tracking_error", 0.05) if found_data else 0.05
            age_years = found_data.get("age_years", 5) if found_data else 5
            geo = found_data.get("geo", {"Global / Diversificado": 100.0}) if found_data else {"Global / Diversificado": 100.0}
            holdings = found_data.get("holdings", {"Principales Posiciones": 100.0}) if found_data else {"Principales Posiciones": 100.0}

            st.success(f"¡Activo encontrado: **{long_name}**!")

            # Tarjeta de Puntuación y Métricas Principales
            st.markdown(f"""
            <div class="score-container">
                <div>
                    <h2 style="color: #38bdf8; margin: 0;">Puntuación Global</h2>
                    <p style="font-size: 2rem; font-weight: bold; color: #facc15; margin: 0;">⭐ {score} / 5.0</p>
                </div>
                <div>
                    <h3 style="color: #cbd5e1; margin: 0;">{long_name}</h3>
                    <p style="color: #94a3b8; margin: 0;">Categoría: <b>{category}</b></p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Métricas en columnas con indicadores visuales
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric("Precio / VL", f"{price:,.2f} {currency}" if price else "N/D")
            c_m2.metric("Rentabilidad 1 Año", f"{return_1y:+.2f}%", delta=f"{return_1y:+.2f}%")
            c_m3.metric("Gastos (TER)", f"{ter:.2f}%")
            c_m4.metric("Patrimonio (AUM)", f"{aum:,.0f} M€" if asset_type != "Acciones" else "N/D")

            with st.expander("📊 Ver Ficha Técnica y Métricas Avanzadas", expanded=True):
                st.write(f"**Descripción:** {desc}")
                col_f1, col_f2, col_f3 = st.columns(3)
                col_f1.metric("Tracking Error", f"{tracking_error}%")
                col_f2.metric("Antigüedad", f"{age_years} años")
                col_f3.metric("Moneda", currency)

            # Desglose Geográfico y Pesos (si aplica a fondos/ETFs)
            if asset_type in ["Fondos Indexados", "ETFs"]:
                col_geo, col_hold = st.columns(2)
                with col_geo:
                    st.markdown("#### 🌍 Desglose Geográfico")
                    for pais, pct in geo.items():
                        st.write(f"**{pais}**: {pct}%")
                        st.progress(int(pct) if pct <= 100 else 100)
                with col_hold:
                    st.markdown("#### 🏢 Principales Posiciones (Holdings)")
                    for emp, pct in holdings.items():
                        st.write(f"**{emp}**: {pct}%")
                        st.progress(int(pct) if pct <= 100 else 100)

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
                st.warning(f"No se pudo conectar con Yahoo Finance, mostrando datos locales de la base de datos.")
                st.markdown(f"**Nombre:** {found_data['name']}")
                st.markdown(f"**Puntuación:** ⭐ {found_data.get('score', 4.5)}")
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
