import streamlit as st
import yfinance as yf
import pandas as pd
import io

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
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 40px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        margin-bottom: 20px;
        border: 1px solid #334155;
        flex-wrap: wrap;
    }
    .circular-progress {
        position: relative;
        width: 110px;
        height: 110px;
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
        width: 88px;
        height: 88px;
        border-radius: 50%;
        background-color: #0f172a;
    }
    .progress-value {
        position: relative;
        font-size: 1.6rem;
        font-weight: bold;
        color: #f8fafc;
    }
    .pure-stamp-grade {
        font-family: 'Courier New', Courier, monospace;
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
        color: var(--stamp-color);
        text-transform: uppercase;
        transform: rotate(-8deg);
        display: inline-block;
        text-shadow: 3px 3px 0px rgba(0,0,0,0.8), 0 0 5px rgba(0,0,0,0.5);
        animation: stampPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    @keyframes stampPop {
        0% { transform: scale(2.2) rotate(-20deg); opacity: 0; }
        100% { transform: scale(1) rotate(-8deg); opacity: 0.95; }
    }

    /* Animación de Cadena Deslizante Suave y Despacio */
    .neon-stream-vertical {
        position: relative;
        width: 40px;
        height: 50px;
        overflow: hidden;
        display: inline-block;
        margin: 0 auto;
    }
    .neon-stream-horizontal {
        position: relative;
        width: 70px;
        height: 30px;
        overflow: hidden;
        display: inline-block;
        margin: 0 auto;
    }

    @keyframes slideUpStream {
        0% { top: 45px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #22c55e; }
        50% { opacity: 1; filter: blur(0px); text-shadow: 0 0 12px #22c55e, 0 0 22px #22c55e; }
        100% { top: -15px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #22c55e; }
    }
    @keyframes slideDownStream {
        0% { top: -15px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #ef4444; }
        50% { opacity: 1; filter: blur(0px); text-shadow: 0 0 12px #ef4444, 0 0 22px #ef4444; }
        100% { top: 45px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #ef4444; }
    }
    @keyframes slideRightStream {
        0% { left: -15px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #eab308; }
        50% { opacity: 1; filter: blur(0px); text-shadow: 0 0 12px #eab308, 0 0 22px #eab308; }
        100% { left: 70px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #eab308; }
    }

    .arrow-item-up {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.6rem;
        font-weight: 900;
        color: #22c55e;
        animation: slideUpStream 2.6s infinite linear;
    }
    .arrow-item-down {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.6rem;
        font-weight: 900;
        color: #ef4444;
        animation: slideDownStream 2.6s infinite linear;
    }
    .arrow-item-side {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        font-weight: 900;
        color: #eab308;
        animation: slideRightStream 2.8s infinite linear;
    }

    .st-1 { animation-delay: 0.0s; }
    .st-2 { animation-delay: 0.8s; }
    .st-3 { animation-delay: 1.6s; }

    .final-net-card {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        border: 2px solid #34d399;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(4, 120, 87, 0.3);
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .final-net-title {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #a7f3d0;
        margin-bottom: 5px;
        font-weight: 600;
    }
    .final-net-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Control de Estados de Navegación y Cartera
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

def reset_navigation():
    st.session_state.stage = 'home'
    st.session_state.asset_type = None
    st.session_state.sub_type = None

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios).", "div_growth": 6.5, "div_yield": 2.8, "per": 24.0, "beta": 0.95, "payout": 60.0},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos).", "div_growth": 5.0, "div_yield": 4.8, "per": 16.5, "beta": 0.65, "payout": 70.0},
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5, "per": 8.0, "beta": 1.25, "payout": 50.0},
    "sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5, "per": 8.0, "beta": 1.25, "payout": 50.0},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0, "per": 7.5, "beta": 1.30, "payout": 40.0},
    "santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0, "per": 7.5, "beta": 1.30, "payout": 40.0},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5, "per": 12.0, "beta": 0.85, "payout": 85.0},
    "telefónica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5, "per": 12.0, "beta": 0.85, "payout": 85.0},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico sin dependencia de dividendo tradicional.", "div_growth": 10.0, "div_yield": 0.7, "per": 32.0, "beta": 0.90, "payout": 25.0},
    "procter & gamble": {"ticker": "PG", "racha": "Excepcional. Aristócrata del Dividendo con más de 65 años de subidas ininterrumpidas.", "div_growth": 6.0, "div_yield": 2.4, "per": 25.0, "beta": 0.55, "payout": 60.0},
    "copart": {"ticker": "CPRT", "racha": "Empresa pura de crecimiento orientada a reinvestigación.", "div_growth": 0.0, "div_yield": 0.0, "per": 28.0, "beta": 1.05, "payout": 0.0},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sensible al ciclo económico y a los planes de consolidación bancaria.", "div_growth": 4.5, "div_yield": 6.2, "per": 8.5, "beta": 1.10, "payout": 60.0}
}

FUND_DB = {
    "vanguard global stock acc": {"name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "Vanguard Global Stock", "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 4500, "tracking_error": 0.08, "age_years": 8},
    "vanguard s&p 500 acc": {"name": "Vanguard S&P 500 Stock Index Fund EUR Acc", "ticker": "Vanguard S&P 500", "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 38000, "tracking_error": 0.03, "age_years": 12},
    "amundi msci world acc": {"name": "Amundi Index MSCI World AE-C", "ticker": "Amundi MSCI World", "category": "Renta Variable Global (MSCI World)", "ter": 0.30, "aum": 3200, "tracking_error": 0.12, "age_years": 7}
}

ETF_DB = {
    "vwce.de": {"name": "Vanguard FTSE All-World UCITS ETF (Acc)", "ticker": "VWCE.DE", "category": "Renta Variable Global", "ter": 0.22, "aum": 12500, "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 6},
    "spyl.de": {"name": "SPDR S&P 500 UCITS ETF (Acc)", "ticker": "SPYL.DE", "category": "Renta Variable EE.UU.", "ter": 0.03, "aum": 8200, "replication": "Física (Completa)", "te": 0.02, "currency": "EUR", "age_years": 3},
    "sgld.l": {"name": "iShares Physical Gold ETC", "ticker": "SGLD.L", "category": "Materias Primas (Oro Físico)", "ter": 0.15, "aum": 14500, "replication": "Física (Lingotes)", "te": 0.01, "currency": "USD", "age_years": 11},
    "IEMG": {"name": "iShares Core MSCI Emerging Markets IMI ETF", "ticker": "IEMG", "category": "Empresas Emergentes", "ter": 0.09, "aum": 78000, "replication": "Física (Muestreo)", "te": 0.06, "currency": "USD", "age_years": 12},
    "qdve.de": {"name": "iShares S&P 500 Information Technology Sector ETF", "ticker": "QDVE.DE", "category": "Tecnología", "ter": 0.15, "aum": 4200, "replication": "Física (Completa)", "te": 0.05, "currency": "EUR", "age_years": 6},
    "INRG.MI": {"name": "iShares Global Clean Energy UCITS ETF", "ticker": "INRG.MI", "category": "Energías Renovables", "ter": 0.65, "aum": 2800, "replication": "Física (Completa)", "te": 0.18, "currency": "EUR", "age_years": 15},
    "EXV1.DE": {"name": "iShares STOXX Europe 600 Utilities UCITS ETF", "ticker": "EXV1.DE", "category": "Eléctricas y Utilities", "ter": 0.46, "aum": 1100, "replication": "Física (Completa)", "te": 0.08, "currency": "EUR", "age_years": 20},
    "VHYL.DE": {"name": "Vanguard FTSE All-World High Dividend Yield ETF", "ticker": "VHYL.DE", "category": "Dividendos Globales", "ter": 0.29, "aum": 4100, "replication": "Física (Completa)", "te": 0.05, "currency": "EUR", "age_years": 10}
}

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

# --- BARRA SUPERIOR CON ICONO DE CARTERA ---
portfolio_count = len(st.session_state.portfolio)
col_tb1, col_tb2 = st.columns([3, 1])
with col_tb1:
    st.markdown("### 📈 Analizador Bursátil Multifuente")
with col_tb2:
    if st.button(f"💼 Mi Cartera ({portfolio_count})", use_container_width=True, type="primary"):
        st.session_state.stage = "portfolio_view"
        st.rerun()

st.markdown("---")

# BARRA LATERAL (HISTORIAL)
with st.sidebar:
    st.header("📊 Historial de Sesión")
    num_entries = len(st.session_state.history)
    st.markdown(f"Activos / Entradas analizadas: **{num_entries}**")
    
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
        st.info("Analiza algún activo para habilitar la exportación.")

    if st.session_state.stage != 'home':
        st.markdown("---")
        if st.button("🏠 Volver al Menú Principal"):
            reset_navigation()
            st.rerun()

# ----------------------------------------------------
# ETAPA 0: LANDING / PANTALLA INICIAL
# ----------------------------------------------------
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

# ----------------------------------------------------
# ETAPA 1: SUBOPCIONES SEGÚN EL ACTIVO SELECCIONADO
# ----------------------------------------------------
elif st.session_state.stage == 'sub_options':
    if st.button("← Volver a selección de activos"):
        reset_navigation()
        st.rerun()

    st.title(f"Configuración para: {st.session_state.asset_type}")
    
    if st.session_state.asset_type == "Acciones":
        st.markdown("### Selecciona la modalidad de las acciones:")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Con dividendos", use_container_width=True):
                st.session_state.sub_type = "Con dividendos"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c2:
            if st.button("Sin dividendos", use_container_width=True):
                st.session_state.sub_type = "Sin dividendos"
                st.session_state.stage = "analyzer"
                st.rerun()

    elif st.session_state.asset_type == "Fondos indexados":
        st.markdown("### Selecciona qué deseas hacer:")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 Ver Ranking de Fondos por Menor TER", use_container_width=True, type="primary"):
                st.session_state.sub_type = "Ranking TER"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c2:
            if st.button("✍️ Evaluar un Fondo con Buscador Predictivo", use_container_width=True):
                st.session_state.sub_type = "Acumulación"
                st.session_state.stage = "analyzer"
                st.rerun()

    elif st.session_state.asset_type == "ETFs":
        st.markdown("### Selecciona qué deseas hacer con los ETFs:")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🗺️ Explorar Tipos de ETFs (Guía)", use_container_width=True, type="primary"):
                st.session_state.sub_type = "Explorador ETFs"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c2:
            if st.button("🏆 Ver Ranking por Menor TER", use_container_width=True):
                st.session_state.sub_type = "Ranking ETFs"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c3:
            if st.button("🔍 Evaluar un ETF Específico", use_container_width=True):
                st.session_state.sub_type = "Evaluación ETF"
                st.session_state.stage = "analyzer"
                st.rerun()

# ----------------------------------------------------
# ETAPA DE CARTERA CONSOLIDADA (MI CARTERA) CON TABLAS ANUALES DESGLOSADAS
# ----------------------------------------------------
elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver al Analizador"):
        st.session_state.stage = 'analyzer' if st.session_state.asset_type else 'home'
        st.rerun()

    st.title("💼 Simulador Global de Cartera Consolidada")
    
    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía. Explora acciones, fondos o ETFs y pulsa el botón **'➕ Añadir a mi Cartera'** para añadirlos a este simulador conjunto.")
    else:
        st.markdown("Configura el plazo, la frecuencia y el bróker de cada activo para obtener el desglose anual detallado y el rendimiento neto final:")
        
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

        for idx, item in enumerate(st.session_state.portfolio):
            is_etf_or_stock = item['type'] in ["ETF", "Acción"]
            broker_profiles = ETF_BROKER_PROFILES if is_etf_or_stock else FUND_BROKER_PROFILES
            
            with st.expander(f"{idx+1}. {item['name']} ({item['ticker']}) - [{item['type']}]", expanded=True):
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
                    rent_est = st.slider(f"Rentabilidad estimada anual (%)", min_value=0.0, max_value=20.0, value=float(item.get('est_rent', 7.5)), step=0.5, key=f"p_rent_{idx}")
                with col_i4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Quitar", key=f"del_{idx}"):
                        st.session_state.portfolio.pop(idx)
                        st.rerun()

                f_pct = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_percent"]
                f_fix = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_fixed"]
                f_spr = b_data["spread_percent"]
                f_fx = b_data["fx_fee_percent"]

                ter_val = item.get('ter', 0.20)
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
                acum_b = c_broker_ini
                acum_s = c_spread_ini
                acum_f = c_fx_ini

                historial_activo = []

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

                    if p % periodos_ano == 0:
                        ano_act = p // periodos_ano
                        costes_tot_act = acum_b + acum_s + acum_f
                        int_brutos = saldo_act - (total_aport_acum - costes_tot_act)
                        
                        historial_activo.append({
                            "Año": f"Año {ano_act}",
                            "Capital Aportado Bruto (€)": round(total_aport_acum, 2),
                            "Comisiones Bróker (€)": round(acum_b, 2),
                            "Coste Spread (€)": round(acum_s, 2),
                            "Coste Cambio Divisa (€)": round(acum_f, 2),
                            "Beneficio Neto (€)": round(max(0.0, int_brutos), 2),
                            "Capital Total Neto (€)": round(saldo_act, 2)
                        })

                df_act = pd.DataFrame(historial_activo)
                st.markdown("##### 📊 Desglose de crecimiento anual para este activo:")
                st.dataframe(df_act, use_container_width=True)

                total_capital_bruto_acum += saldo_act
                total_capital_aportado_acum += total_aport_acum
                total_costes_acum += (acum_b + acum_s + acum_f)

        if st.session_state.portfolio:
            capital_neto_aportado = total_capital_aportado_acum - total_costes_acum
            beneficio_bruto_global = max(0.0, total_capital_bruto_acum - capital_neto_aportado)
            impuestos_globales = beneficio_bruto_global * 0.19
            beneficio_neto_global = beneficio_bruto_global - impuestos_globales
            capital_liquido_global = capital_neto_aportado + beneficio_neto_global

            st.markdown("---")
            st.markdown("### 📊 Proyección Total de la Cartera Consolidada")

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Capital Invertido Bruto", f"{total_capital_aportado_acum:,.2f} €")
            m2.metric("Total Costes Bróker", f"{total_costes_acum:,.2f} €")
            m3.metric("Beneficio Bruto Consolidado", f"{beneficio_bruto_global:,.2f} €")
            m4.metric("Impuestos Estimados (19%)", f"{impuestos_globales:,.2f} €")
            m5.metric("Beneficio Neto Libre de Impuestos", f"{beneficio_neto_global:,.2f} €")

            st.markdown(f"""
            <div class="final-net-card">
                <div class="final-net-title">💰 Capital Total Líquido Final de tu Cartera (Tras Impuestos)</div>
                <div class="final-net-value">{capital_liquido_global:,.2f} €</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🗑️ Vaciar Cartera Completa"):
                st.session_state.portfolio = []
                st.rerun()

# ----------------------------------------------------
# ETAPA 2: ANALIZADOR
# ----------------------------------------------------
elif st.session_state.stage == 'analyzer':
    if st.button("← Cambiar categoría / Volver"):
        st.session_state.stage = 'sub_options'
        st.session_state.sub_type = None
        st.rerun()

    def get_trend_chain_stream(hist_df):
        if hist_df is None or len(hist_df) < 2:
            return '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Lateral</div>'
        
        closes = hist_df['Close'].dropna()
        if len(closes) < 2:
            return '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Lateral</div>'

        first_p = float(closes.iloc[0])
        last_p = float(closes.iloc[-1])
        pct_change = ((last_p - first_p) / first_p) * 100

        if pd.isna(pct_change):
            return '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Lateral</div>'

        if pct_change >= 1.0:
            return f'<div class="neon-stream-vertical"><span class="arrow-item-up st-1">▲</span><span class="arrow-item-up st-2">▲</span><span class="arrow-item-up st-3">▲</span></div><div style="font-size: 0.75rem; color: #22c55e; margin-top: 4px;">+{pct_change:.1f}%</div>'
        elif pct_change <= -1.0:
            return f'<div class="neon-stream-vertical"><span class="arrow-item-down st-1">▼</span><span class="arrow-item-down st-2">▼</span><span class="arrow-item-down st-3">▼</span></div><div style="font-size: 0.75rem; color: #ef4444; margin-top: 4px;">{pct_change:.1f}%</div>'
        else:
            return f'<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">{pct_change:+.1f}%</div>'

    if st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
        st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
        ranking_data = [{"Fondo": data["name"], "Categoría": data["category"], "TER Anual (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Antigüedad (Años)": data["age_years"]} for data in FUND_DB.values()]
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_ranking, use_container_width=True)
        st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER de la gestora.")
        if st.button("← Volver al menú de fondos"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
        st.title("🏆 Ranking de ETFs (Ordenados por menor TER)")
        ranking_etfs = [{"ETF": data["name"], "Ticker": data["ticker"], "Categoría": data["category"], "TER (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Réplica": data["replication"]} for data in ETF_DB.values()]
        df_etf_ranking = pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_etf_ranking, use_container_width=True)
        st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER.")
        if st.button("← Volver al menú de ETFs"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Explorador ETFs":
        st.title("🗺️ Guía y Tipos de ETFs Disponibles")
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🌍 Globales", "💰 Dividendos", "🥇 Materias Primas", "💻 Tecnología", "⚡ Renovables & Eléctricas", "🚀 Emergentes"])
        
        with tab1:
            st.subheader("Renta Variable Global")
            st.markdown("- **Objetivo:** Diversificación global en países desarrollados.")
        with tab2:
            st.subheader("Alto Dividendo")
            st.markdown("- **Objetivo:** Empresas maduras con pagos estables.")
        with tab3:
            st.subheader("Materias Primas")
            st.markdown("- **Objetivo:** Exposición física a oro y commodities.")
        with tab4:
            st.subheader("Tecnología")
            st.markdown("- **Objetivo:** Innovación, IA y software.")
        with tab5:
            st.subheader("Renovables y Utilities")
            st.markdown("- **Objetivo:** Transición energética y eléctricas defensivas.")
        with tab6:
            st.subheader("Emergentes")
            st.markdown("- **Objetivo:** Crecimiento en economías en desarrollo.")

        st.markdown("---")
        if st.button("← Volver al menú de ETFs"):
            st.session_state.sub_type = None
            st.rerun()

    else:
        st.title(f"📈 Analizador: {st.session_state.asset_type} ({st.session_state.sub_type})")

        if st.session_state.asset_type == "Acciones":
            stock_options = ["-- Selecciona una acción o escribe abajo --"] + [f"{data.get('ticker')} ({key.title()})" for key, data in TICKER_DB.items()]
            selected_stock_option = st.selectbox("📊 Buscador predictivo de Acciones", options=stock_options)
            custom_stock_input = st.text_input("O introduce Ticker (ej. AAPL, TSLA, ITX.MC):", value="").strip()
            user_input = custom_stock_input.upper() if custom_stock_input else ("" if selected_stock_option.startswith("--") else selected_stock_option.split("(")[0].strip())

        elif st.session_state.asset_type == "Fondos indexados":
            fund_options = ["-- Selecciona un fondo o escribe abajo --"] + [f"{data['name']} ({data['category']})" for data in FUND_DB.values()]
            selected_fund_option = st.selectbox("🔍 Buscador predictivo de Fondos", options=fund_options)
            custom_fund_input = st.text_input("O introduce nombre de fondo:", value="").strip()
            user_input = custom_fund_input if custom_fund_input else ("" if selected_fund_option.startswith("--") else selected_fund_option.split("(")[0].strip())

        elif st.session_state.asset_type == "ETFs":
            etf_options = ["-- Selecciona un ETF o escribe abajo --"] + [f"{data['name']} [{data['category']}] ({data['ticker']})" for data in ETF_DB.values()]
            selected_etf_option = st.selectbox("🌐 Buscador predictivo de ETFs", options=etf_options)
            custom_etf_input = st.text_input("O introduce Ticker de ETF (ej. CSPX.AS, QQQ):", value="").strip()
            user_input = custom_etf_input.upper() if custom_etf_input else ("" if selected_etf_option.startswith("--") else selected_etf_option.split("(")[-1].replace(")", "").strip())

        def get_stock_data(query):
            q_lower = query.lower().strip()
            for key, data in TICKER_DB.items():
                if key in q_lower or data["ticker"].lower() == q_lower:
                    return data.get("ticker", query.upper()), data.get("racha", "Sin datos"), data.get("div_growth", 3.0), data.get("div_yield", 4.0), data.get("per", 18.0), data.get("beta", 1.0), data.get("payout", 50.0)
            return query.upper(), "Sin datos de racha previos.", 3.0, 4.0, 18.0, 1.0, 50.0

        def get_letter_grade(score):
            if score >= 4.5: return "A+"
            elif score >= 4.0: return "A"
            elif score >= 3.0: return "B"
            elif score >= 2.0: return "C"
            else: return "D"

        if not user_input:
            st.info("👆 Selecciona un activo en el buscador para comenzar.")
        else:
            # ----------------------------------------------------
            # CASO A: ACCIONES
            # ----------------------------------------------------
            if st.session_state.asset_type == "Acciones":
                stock_result = get_stock_data(user_input)
                ticker_input, racha_info, est_div_growth, db_div_yield, db_per, db_beta, db_payout = stock_result
                
                try:
                    stock = yf.Ticker(ticker_input)
                    hist_price = stock.history(period="3mo")
                    
                    current_price = None
                    if not hist_price.empty and 'Close' in hist_price.columns:
                        valid_closes = hist_price['Close'].dropna()
                        if not valid_closes.empty:
                            current_price = float(valid_closes.iloc[-1])

                    last_volume = int(hist_price['Volume'].iloc[-1]) if not hist_price.empty and 'Volume' in hist_price.columns and not pd.isna(hist_price['Volume'].iloc[-1]) else None
                    avg_monthly_volume = int(hist_price['Volume'].tail(20).mean()) if not hist_price.empty and 'Volume' in hist_price.columns else None
                    info = stock.info or {}

                    name = info.get('longName', user_input.title())
                    currency_symbol = '$' if info.get('currency') == 'USD' else '€'
                    price_display = f"{current_price:,.2f} {currency_symbol}" if current_price is not None else "—"
                    trend_html = get_trend_chain_stream(hist_price)

                    per_y = info.get('trailingPE') or info.get('forwardPE') or db_per
                    pfcf_y = info.get('priceToFreeCashflow') or 18.0
                    pb_y = info.get('priceToBook') or 3.0
                    roe_val = (info.get('returnOnEquity', 0.15) * 100) if info.get('returnOnEquity') else 15.0
                    div_y_val = (info.get('dividendYield', 0) * 100) if info.get('dividendYield') else db_div_yield
                    beta_val = info.get('beta') or db_beta
                    raw_payout = info.get('payoutRatio')
                    payout_val = (raw_payout * 100) if raw_payout is not None else db_payout

                    total_score = 4.0
                    grade = get_letter_grade(total_score)
                    deg = int((total_score / 5.0) * 360)
                    progress_color = "#22c55e"

                    col_n1, col_n2 = st.columns([3, 1])
                    with col_n1:
                        st.subheader(f"📊 Informe: {name} ({ticker_input})")
                    with col_n2:
                        if st.button("➕ Añadir a mi Cartera", type="primary", use_container_width=True):
                            st.session_state.portfolio.append({
                                "type": "Acción",
                                "name": name,
                                "ticker": ticker_input,
                                "est_rent": 8.0,
                                "ter": 0.0
                            })
                            st.success(f"¡{name} añadido a tu Cartera!")

                    st.markdown(f"""
                    <div class="score-container">
                        <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg}deg; --progress-color: {progress_color};"><div class="progress-value">{total_score:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Tendencia en Cadena</div><div style="margin-top: 15px;">{trend_html}</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio Actual</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    df_metrics = pd.DataFrame({
                        "Métrica Clave": ["PER (Valoración)", "Precio / FCF", "ROE", "Dividendo Yield", "Payout Ratio", "Beta"],
                        "Valor Evaluado": [f"{per_y:.2f}", f"{pfcf_y:.2f}", f"{roe_val:.2f}%", f"{div_y_val:.2f}%", f"{payout_val:.1f}%", f"{beta_val:.2f}"]
                    })
                    st.table(df_metrics)

                except Exception as e:
                    st.error(f"Error al obtener datos: {e}")

            # ----------------------------------------------------
            # CASO B: FONDOS INDEXADOS (CON SIMULADOR INDIVIDUAL)
            # ----------------------------------------------------
            elif st.session_state.asset_type == "Fondos indexados":
                matched_fund = next((data for key, data in FUND_DB.items() if data["name"].lower() in user_input.lower() or key in user_input.lower()), None)
                
                if matched_fund:
                    fund_name = matched_fund["name"]
                    ter_val = matched_fund["ter"]
                    aum_val = matched_fund["aum"]
                    te_val = matched_fund["tracking_error"]
                    age_val = matched_fund["age_years"]
                else:
                    fund_name = user_input
                    ter_val = 0.20
                    aum_val = 2000
                    te_val = 0.08
                    age_val = 5

                score_fund = 4.2
                grade_fund = get_letter_grade(score_fund)
                deg_fund = int((score_fund / 5.0) * 360)
                color_fund = "#22c55e"
                trend_html_fund = '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Pasivo</div>'

                col_f1, col_f2 = st.columns([3, 1])
                with col_f1:
                    st.subheader(f"📊 Informe de Fondo: {fund_name}")
                with col_f2:
                    if st.button("➕ Añadir a mi Cartera", type="primary", use_container_width=True, key="add_fund"):
                        st.session_state.portfolio.append({
                            "type": "Fondo Indexado",
                            "name": fund_name,
                            "ticker": "FONDO",
                            "est_rent": 7.5,
                            "ter": ter_val
                        })
                        st.success(f"¡{fund_name} añadido a tu Cartera!")

                st.markdown(f"""
                <div class="score-container">
                    <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg_fund}deg; --progress-color: {color_fund};"><div class="progress-value">{score_fund:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación Pasiva</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Tendencia en Cadena</div><div style="margin-top: 15px;">{trend_html_fund}</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {color_fund};">{grade_fund}</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Antigüedad</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{age_val} Años</div></div>
                </div>
                """, unsafe_allow_html=True)

                df_fund_data = {
                    "Métrica del Fondo": ["TER (Gastos Corrientes)", "Patrimonio (AUM)", "Tracking Error"],
                    "Valor Actual": [f"{ter_val:.2f}% anual", f"{aum_val:,.0f} M€", f"{te_val:.2f}%"]
                }
                st.table(pd.DataFrame(df_fund_data))

                # SIMULADOR INDIVIDUAL DE FONDO
                st.markdown("---")
                st.subheader(f"🧮 Simulador de Interés Compuesto para: {fund_name}")
                toggle_f_sim = st.toggle("Activar calculadora individual de este fondo", value=False, key="tg_f_sim")

                if toggle_f_sim:
                    sel_b_f = st.selectbox("Selecciona tu Entidad Comercializadora", options=list(FUND_BROKER_PROFILES.keys()), key="sel_b_f")
                    b_f_data = FUND_BROKER_PROFILES[sel_b_f]
                    plan_f_free = st.checkbox("Plan de aportación automática sin comisión", value=b_f_data["supports_free_plans"], key="plan_f_free")

                    cf1, cf2 = st.columns(2)
                    with cf1:
                        inv_i_f = st.number_input("Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key="inv_i_f")
                        app_p_f = st.number_input("Aportación Periódica (€)", min_value=0.0, value=150.0, step=50.0, key="app_p_f")
                        freq_f = st.selectbox("Frecuencia", options=["Mensual", "Anual"], key="freq_f")
                    with cf2:
                        anos_f = st.slider("Plazo (Años)", min_value=1, max_value=40, value=15, key="anos_f")
                        rent_f = st.slider("Rentabilidad anual estimada (%)", min_value=0.0, max_value=20.0, value=7.5, step=0.5, key="rent_f")

                    fpct = 0.0 if (b_f_data["supports_free_plans"] and plan_f_free) else b_f_data["fee_percent"]
                    ffix = 0.0 if (b_f_data["supports_free_plans"] and plan_f_free) else b_f_data["fee_fixed"]
                    fspr = b_f_data["spread_percent"]
                    ffx = b_f_data["fx_fee_percent"]

                    per_ano_f = 12 if freq_f == "Mensual" else 1
                    t_neta_f = rent_f - ter_val
                    t_per_f = (t_neta_f / 100.0) / per_ano_f
                    tot_per_f = anos_f * per_ano_f

                    c_broker_i_f = (inv_i_f * (b_f_data["fee_percent"] / 100.0)) + b_f_data["fee_fixed"]
                    c_spread_i_f = inv_i_f * (fspr / 100.0)
                    c_fx_i_f = inv_i_f * (ffx / 100.0)
                    c_ini_f = c_broker_i_f + c_spread_i_f + c_fx_i_f

                    saldo_f = max(0.0, inv_i_f - c_ini_f)
                    aport_f = inv_i_f
                    a_broker_f = c_broker_i_f
                    a_spread_f = c_spread_i_f
                    a_fx_f = c_fx_i_f

                    historial_f = []

                    for p in range(1, tot_per_f + 1):
                        if p > 1:
                            cb = (app_p_f * (fpct / 100.0)) + ffix
                            cs = app_p_f * (fspr / 100.0)
                            cf = app_p_f * (ffx / 100.0)
                            ct = cb + cs + cf

                            net_app_f = max(0.0, app_p_f - ct)
                            aport_f += app_p_f
                            a_broker_f += cb
                            a_spread_f += cs
                            a_fx_f += cf
                            saldo_f = saldo_f * (1 + t_per_f) + net_app_f
                        else:
                            saldo_f = saldo_f * (1 + t_per_f)

                        if p % per_ano_f == 0:
                            ano_act_f = p // per_ano_f
                            c_tot_f = a_broker_f + a_spread_f + a_fx_f
                            int_b_f = saldo_f - (aport_f - c_tot_f)
                            
                            historial_f.append({
                                "Año": f"Año {ano_act_f}",
                                "Capital Aportado Bruto (€)": round(aport_f, 2),
                                "Comisiones Bróker (€)": round(a_broker_f, 2),
                                "Coste Spread (€)": round(a_spread_f, 2),
                                "Coste Cambio Divisa (€)": round(a_fx_f, 2),
                                "Beneficio Neto (€)": round(max(0.0, int_b_f), 2),
                                "Capital Total Neto (€)": round(saldo_f, 2)
                            })

                    df_sim_f = pd.DataFrame(historial_f)
                    with st.expander("Ver desglose anual detallado con comisiones y spreads", expanded=True):
                        st.dataframe(df_sim_f, use_container_width=True)

                    c_tot_acum_f = a_broker_f + a_spread_f + a_fx_f
                    net_aport_f = aport_f - c_tot_acum_f
                    bruto_f = max(0.0, saldo_f - net_aport_f)
                    imp_f = bruto_f * 0.19
                    neto_f = bruto_f - imp_f
                    liquido_f = net_aport_f + neto_f

                    fm1, fm2, fm3, fm4 = st.columns(4)
                    fm1.metric("Capital Invertido Neto", f"{net_aport_f:,.2f} €")
                    fm2.metric("Costes Totales", f"{c_tot_acum_f:,.2f} €")
                    fm3.metric("Beneficio Bruto", f"{bruto_f:,.2f} €")
                    fm4.metric("Beneficio Neto (Tras 19% Impuestos)", f"{neto_f:,.2f} €")

                    st.markdown(f"""
                    <div class="final-net-card">
                        <div class="final-net-title">💰 Capital Total Líquido Final del Fondo</div>
                        <div class="final-net-value">{liquido_f:,.2f} €</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ----------------------------------------------------
            # CASO C: ETFS (CON SIMULADOR INDIVIDUAL Y DESGLOSE)
            # ----------------------------------------------------
            elif st.session_state.asset_type == "ETFs":
                matched_etf = next((data for key, data in ETF_DB.items() if data["ticker"].upper() == user_input.upper() or data["name"].lower() in user_input.lower()), None)
                
                if matched_etf:
                    etf_name = matched_etf["name"]
                    etf_ticker = matched_etf["ticker"]
                    etf_cat = matched_etf["category"]
                    ter_etf = matched_etf["ter"]
                    aum_etf = matched_etf["aum"]
                    repl_etf = matched_etf["replication"]
                    te_etf = matched_etf["te"]
                    curr_etf = matched_etf["currency"]
                    age_etf = matched_etf["age_years"]
                else:
                    etf_ticker = user_input.upper()
                    try:
                        live_ticker = yf.Ticker(etf_ticker)
                        info_live = live_ticker.info or {}
                        etf_name = info_live.get('longName', etf_ticker)
                        curr_etf = info_live.get('currency', 'EUR')
                    except:
                        etf_name = etf_ticker
                        curr_etf = 'EUR'
                    
                    etf_cat = "Personalizado"
                    ter_etf = 0.20
                    aum_etf = 1000
                    repl_etf = "Física"
                    te_etf = 0.05
                    age_etf = 5

                etf_price = None
                last_volume = None
                avg_monthly_volume = None
                etf_hist = None
                try:
                    etf_stock = yf.Ticker(etf_ticker)
                    etf_hist = etf_stock.history(period="3mo")
                    if not etf_hist.empty and 'Close' in etf_hist.columns:
                        valid_c = etf_hist['Close'].dropna()
                        if not valid_c.empty:
                            etf_price = float(valid_c.iloc[-1])
                        last_volume = int(etf_hist['Volume'].iloc[-1]) if 'Volume' in etf_hist.columns and not pd.isna(etf_hist['Volume'].iloc[-1]) else None
                        avg_monthly_volume = int(etf_hist['Volume'].tail(20).mean()) if 'Volume' in etf_hist.columns else None
                except:
                    pass

                price_display_etf = f"{etf_price:,.2f} {curr_etf}" if etf_price is not None else "—"
                last_vol_display = f"{last_volume:,.0f} títulos" if last_volume is not None else "—"
                avg_vol_display = f"{avg_monthly_volume:,.0f} títulos/día" if avg_monthly_volume is not None else "—"
                trend_html_etf = get_trend_chain_stream(etf_hist)

                score_etf = 4.2
                grade_etf = get_letter_grade(score_etf)
                deg_etf = int((score_etf / 5.0) * 360)
                color_etf = "#22c55e"

                col_e1, col_e2 = st.columns([3, 1])
                with col_e1:
                    st.subheader(f"🌐 Informe de ETF: {etf_name} ({etf_ticker})")
                with col_e2:
                    if st.button("➕ Añadir a mi Cartera", type="primary", use_container_width=True, key="add_etf"):
                        st.session_state.portfolio.append({
                            "type": "ETF",
                            "name": etf_name,
                            "ticker": etf_ticker,
                            "est_rent": 7.5,
                            "ter": ter_etf
                        })
                        st.success(f"¡{etf_name} añadido a tu Cartera!")

                st.markdown(f"""
                <div class="score-container">
                    <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg_etf}deg; --progress-color: {color_etf};"><div class="progress-value">{score_etf:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación ETF</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Tendencia en Cadena</div><div style="margin-top: 15px;">{trend_html_etf}</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {color_etf};">{grade_etf}</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio Actual</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display_etf}</div></div>
                </div>
                """, unsafe_allow_html=True)

                df_etf_data = {
                    "Métrica del ETF": ["Volumen Última Sesión", "Volumen Medio Mensual", "TER (Gastos Anuales)", "Patrimonio (AUM)", "Tipo de Réplica", "Tracking Error", "Divisa", "Antigüedad"],
                    "Valor Actual": [last_vol_display, avg_vol_display, f"{ter_etf:.2f}% anual", f"{aum_etf:,.0f} M€", repl_etf, f"{te_etf:.2f}%", curr_etf, f"{age_etf} años"]
                }
                st.table(pd.DataFrame(df_etf_data))

                # SIMULADOR INDIVIDUAL DE ETF
                st.markdown("---")
                st.subheader(f"🧮 Simulador de Interés Compuesto para: {etf_name}")
                toggle_e_sim = st.toggle("Activar calculadora individual de este ETF", value=False, key="tg_e_sim")

                if toggle_e_sim:
                    sel_b_e = st.selectbox("Selecciona tu Bróker", options=list(ETF_BROKER_PROFILES.keys()), key="sel_b_e")
                    b_e_data = ETF_BROKER_PROFILES[sel_b_e]
                    plan_e_free = st.checkbox("Plan de aportación automática sin comisión", value=b_e_data["supports_free_plans"], key="plan_e_free")

                    ce1, ce2 = st.columns(2)
                    with ce1:
                        inv_i_e = st.number_input("Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key="inv_i_e")
                        app_p_e = st.number_input("Aportación Periódica (€)", min_value=0.0, value=150.0, step=50.0, key="app_p_e")
                        freq_e = st.selectbox("Frecuencia", options=["Mensual", "Anual"], key="freq_e")
                    with ce2:
                        anos_e = st.slider("Plazo (Años)", min_value=1, max_value=40, value=15, key="anos_e")
                        rent_e = st.slider("Rentabilidad anual estimada (%)", min_value=0.0, max_value=20.0, value=7.5, step=0.5, key="rent_e")

                    epct = 0.0 if (b_e_data["supports_free_plans"] and plan_e_free) else b_e_data["fee_percent"]
                    efix = 0.0 if (b_e_data["supports_free_plans"] and plan_e_free) else b_e_data["fee_fixed"]
                    espr = b_e_data["spread_percent"]
                    efx = b_e_data["fx_fee_percent"]

                    per_ano_e = 12 if freq_e == "Mensual" else 1
                    t_neta_e = rent_e - ter_etf
                    t_per_e = (t_neta_e / 100.0) / per_ano_e
                    tot_per_e = anos_e * per_ano_e

                    c_broker_i_e = (inv_i_e * (b_e_data["fee_percent"] / 100.0)) + b_e_data["fee_fixed"]
                    c_spread_i_e = inv_i_e * (espr / 100.0)
                    c_fx_i_e = inv_i_e * (efx / 100.0)
                    c_ini_e = c_broker_i_e + c_spread_i_e + c_fx_i_e

                    saldo_e = max(0.0, inv_i_e - c_ini_e)
                    aport_e = inv_i_e
                    a_broker_e = c_broker_i_e
                    a_spread_e = c_spread_i_e
                    a_fx_e = c_fx_i_e

                    historial_e = []

                    for p in range(1, tot_per_e + 1):
                        if p > 1:
                            cb = (app_p_e * (epct / 100.0)) + efix
                            cs = app_p_e * (espr / 100.0)
                            cf = app_p_e * (efx / 100.0)
                            ct = cb + cs + cf

                            net_app_e = max(0.0, app_p_e - ct)
                            aport_e += app_p_e
                            a_broker_e += cb
                            a_spread_e += cs
                            a_fx_e += cf
                            saldo_e = saldo_e * (1 + t_per_e) + net_app_e
                        else:
                            saldo_e = saldo_e * (1 + t_per_e)

                        if p % per_ano_e == 0:
                            ano_act_e = p // per_ano_e
                            c_tot_e = a_broker_e + a_spread_e + a_fx_e
                            int_b_e = saldo_e - (aport_e - c_tot_e)
                            
                            historial_e.append({
                                "Año": f"Año {ano_act_e}",
                                "Capital Aportado Bruto (€)": round(aport_e, 2),
                                "Comisiones Bróker (€)": round(a_broker_e, 2),
                                "Coste Spread (€)": round(a_spread_e, 2),
                                "Coste Cambio Divisa (€)": round(a_fx_e, 2),
                                "Beneficio Neto (€)": round(max(0.0, int_b_e), 2),
                                "Capital Total Neto (€)": round(saldo_e, 2)
                            })

                    df_sim_e = pd.DataFrame(historial_e)
                    with st.expander("Ver desglose anual detallado con comisiones y spreads", expanded=True):
                        st.dataframe(df_sim_e, use_container_width=True)

                    c_tot_acum_e = a_broker_e + a_spread_e + a_fx_e
                    net_aport_e = aport_e - c_tot_acum_e
                    bruto_e = max(0.0, saldo_e - net_aport_e)
                    imp_e = bruto_e * 0.19
                    neto_e = bruto_e - imp_e
                    liquido_e = net_aport_e + neto_e

                    em1, em2, em3, em4 = st.columns(4)
                    em1.metric("Capital Invertido Neto", f"{net_aport_e:,.2f} €")
                    em2.metric("Costes Totales", f"{c_tot_acum_e:,.2f} €")
                    em3.metric("Beneficio Bruto", f"{bruto_e:,.2f} €")
                    em4.metric("Beneficio Neto (Tras 19% Impuestos)", f"{neto_e:,.2f} €")

                    st.markdown(f"""
                    <div class="final-net-card">
                        <div class="final-net-title">💰 Capital Total Líquido Final del ETF</div>
                        <div class="final-net-value">{liquido_e:,.2f} €</div>
                    </div>
                    """, unsafe_allow_html=True)
