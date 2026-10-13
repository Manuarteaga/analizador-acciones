import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Mi Cartera Consolidada", page_icon="💼", layout="wide")
page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"  # 👈 AÑADIR AQUÍ TAMBIÉN
)
st.title("💼 Simulador Global de Cartera Consolidada")

# Inicializar estados por seguridad si se entra directo a esta página
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

def guardar_en_url():
    try:
        st.query_params["port"] = json.dumps(st.session_state.portfolio)
    except:
        pass

# Diccionarios de perfiles de brókers (necesarios para los cálculos de comisiones)
FUND_BROKER_PROFILES = {
    "MyInvestor (Fondos Indexados / Sin custodia)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Indexa Capital (Cartera / Gestor automatizado)": {"fee_percent": 0.45, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Renta 4 (Banco tradicional / Tarifas altas)": {"fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False},
    "Personalizado (Ajustar manualmente)": {"fee_percent": 0.10, "fee_fixed": 2.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False}
}

ETF_BROKER_PROFILES = {
    "Trade Republic (1€ orden / Planes a 0€)": {"fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "Lightyear (ETFs sin comisión / Transparente)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.35, "supports_free_plans": True},
    "DEGIRO (Bajas comisiones / 1€ por operación)": {"fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False},
    "Interactive Brokers (Ideal internacional)": {"fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False},
    "XTB (0% comisiones hasta 100k€)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.20, "fx_fee_percent": 0.50, "supports_free_plans": False},
    "Trading 212 (Gratis / Fraccionadas)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.15, "fx_fee_percent": 0.15, "supports_free_plans": True},
    "Personalizado (Ajustar manualmente)": {"fee_percent": 0.10, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False}
}

if not st.session_state.portfolio:
    st.info("🛒 Tu cartera está vacía. Explora acciones, fondos o ETFs en el **Analizador** y pulsa el botón **'➕ Añadir a mi Cartera'** para añadirlos aquí.")
else:
    # --- AUDITORÍA DE SOLAPAMIENTO ---
    categories_in_portfolio = [item.get('category', '') for item in st.session_state.portfolio if item.get('category')]
    category_counts = pd.Series(categories_in_portfolio).value_counts()
    duplicated_categories = category_counts[category_counts > 1].index.tolist()

    if duplicated_categories:
        for dup_cat in duplicated_categories:
            st.warning(f"⚠️ **¡Alerta de Activos Duplicados!** Tienes {category_counts[dup_cat]} activos de la categoría **{dup_cat}**.")

    portfolio_tickers = [item.get('ticker', '').lower() for item in st.session_state.portfolio]
    has_broad_market = any(t in portfolio_tickers for t in ['spyl.de', 'vusa.as', 'swda.l', 'vwce.de', 'vwrl.as'])
    has_tech_sector = any(t in portfolio_tickers for t in ['eqqq.de', 'sxrv.de', 'smh.de'])

    if has_broad_market and has_tech_sector:
        st.warning("⚠️ **¡Alerta de Solapamiento Tech!** Combinas índice general con ETF tecnológico.")

    st.markdown("Configura el plazo, la frecuencia y el bróker de cada activo para obtener el desglose anual detallado:")
    
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        anos_cartera = st.slider("Plazo Temporal Consolidado (Años)", min_value=1, max_value=40, value=15, key="anos_cart")
    with c_p2:
        frecuencia_cartera = st.selectbox("Frecuencia de Aportaciones", options=["Mensual", "Anual"], key="freq_cart")

    st.markdown("---")
    st.markdown("### 📋 Desglose y Configuración por Activo")

    total_capital_bruto_acum = 0.0
    total_capital_aportado_acum = 0.0
    total_costes_acum = 0.0
    total_dividendos_brutos_acum = 0.0
    has_dividend_asset = False

    for idx, item in enumerate(st.session_state.portfolio):
        is_etf_or_stock = item['type'] in ["ETF", "Acción"]
        broker_profiles = ETF_BROKER_PROFILES if is_etf_or_stock else FUND_BROKER_PROFILES
        
        if item.get('is_dist', False) or item.get('type') == "Acción":
            has_dividend_asset = True

        currency_act = item.get('currency', 'EUR')
        ter_val = item.get('ter', 0.20)
        est_rent_val = float(item.get('est_rent', 7.5))

        with st.expander(f"{idx+1}. {item['name']} ({item['ticker']}) - [{item['type']}]", expanded=True):
            cm1, cm2, cm3 = st.columns(3)
            cm1.markdown(f"**Categoría:** {item.get('category', 'General')}")
            cm2.markdown(f"**TER:** `{ter_val}%`")
            cm3.markdown(f"**Divisa:** `{currency_act}`")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                sel_broker = st.selectbox(f"Bróker / Entidad", options=list(broker_profiles.keys()), key=f"p_brok_{idx}")
            with col_b2:
                b_data = broker_profiles[sel_broker]
                plan_sc = st.checkbox("Plan de aportación automática a 0€", value=b_data["supports_free_plans"], key=f"p_plan_{idx}")

            col_i1, col_i2, col_i3, col_i4 = st.columns([2, 2, 2, 1])
            with col_i1:
                inv_ini = st.number_input(f"Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key=f"p_ini_{idx}")
            with col_i2:
                app_per = st.number_input(f"Aportación Periódica (€)", min_value=0.0, value=100.0, step=50.0, key=f"p_app_{idx}")
            with col_i3:
                rent_est = st.slider(f"Rentabilidad estimada anual (%)", min_value=0.0, max_value=20.0, value=est_rent_val, step=0.5, key=f"p_rent_{idx}")
            with col_i4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Quitar", key=f"del_{idx}"):
                    st.session_state.portfolio.pop(idx)
                    guardar_en_url()
                    st.rerun()

        # Cálculo matemático simplificado para la tabla de esta posición
        f_pct = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_percent"]
        f_fix = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_fixed"]
        f_spr = b_data["spread_percent"]
        f_fx = 0.0 if currency_act == "EUR" else b_data["fx_fee_percent"]

        periodos_ano = 12 if frecuencia_cartera == "Mensual" else 1
        tasa_neta = rent_est - ter_val
        tasa_periodica = (tasa_neta / 100.0) / periodos_ano
        tot_periodos = anos_cartera * periodos_ano

        c_broker_ini = (inv_ini * (b_data["fee_percent"] / 100.0)) + b_data["fee_fixed"]
        c_spread_ini = inv_ini * (f_spr / 100.0)
        c_fx_ini = inv_ini * (f_fx / 100.0)
        c_tot_ini = c_broker_ini + c_spread_ini + c_fx_ini

        saldo_act = max(0.0, inv_ini - c_tot_ini)
        total_aport_acum = inv_ini
        acum_b, acum_s, acum_f = c_broker_ini, c_spread_ini, c_fx_ini

        for p in range(1, tot_periodos + 1):
            if p > 1:
                cb = (app_per * (f_pct / 100.0)) + f_fix
                cs = app_per * (f_spr / 100.0)
                cf = app_per * (f_fx / 100.0)
                ct = cb + cs + cf
                import_neto = max(0.0, app_per - ct)
                total_aport_acum += app_per
                acum_b += cb
                acum_s += cs
                acum_f += cf
                saldo_act = saldo_act * (1 + tasa_periodica) + import_neto
            else:
                saldo_act = saldo_act * (1 + tasa_periodica)

        total_capital_bruto_acum += saldo_act
        total_capital_aportado_acum += total_aport_acum
        total_costes_acum += (acum_b + acum_s + acum_f)

    # Resumen Global
    capital_neto_aportado = total_capital_aportado_acum - total_costes_acum
    beneficio_bruto_global = max(0.0, total_capital_bruto_acum - capital_neto_aportado)
    impuestos_globales = beneficio_bruto_global * 0.19
    beneficio_neto_global = beneficio_bruto_global - impuestos_globales
    capital_liquido_global = capital_neto_aportado + beneficio_neto_global

    st.markdown("---")
    st.markdown("### 📊 Proyección Total de la Cartera Consolidada")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
    m2.metric("Costes Bróker", f"{total_costes_acum:,.2f} €")
    m3.metric("Beneficio Bruto", f"{beneficio_bruto_global:,.2f} €")
    m4.metric("Impuestos (19%)", f"{impuestos_globales:,.2f} €")
    m5.metric("Beneficio Neto", f"{beneficio_neto_global:,.2f} €")

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #065f46 0%, #047857 100%); border: 2px solid #34d399; padding: 20px; border-radius: 12px; text-align: center; margin-top: 20px;">
        <div style="font-size: 0.95rem; text-transform: uppercase; color: #a7f3d0; font-weight: 600;">💰 Capital Total Líquido Final de tu Cartera (Tras Impuestos)</div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #ffffff;">{capital_liquido_global:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Vaciar Cartera Completa"):
        st.session_state.portfolio = []
        guardar_en_url()
        st.rerun()
