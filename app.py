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
        gap: 50px;
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
        text-shadow: 3px 3px 0px rgba(0,0,0,0.8), 0 0 5px rgba(0,0,0,0.5);
        animation: stampPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    @keyframes stampPop {
        0% { transform: scale(2.2) rotate(-20deg); opacity: 0; }
        100% { transform: scale(1) rotate(-8deg); opacity: 0.95; }
    }
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

# Control de Estados de Navegación
if 'stage' not in st.session_state:
    st.session_state.stage = 'home'
if 'asset_type' not in st.session_state:
    st.session_state.asset_type = None
if 'sub_type' not in st.session_state:
    st.session_state.sub_type = None
if 'history' not in st.session_state:
    st.session_state.history = []

def reset_navigation():
    st.session_state.stage = 'home'
    st.session_state.asset_type = None
    st.session_state.sub_type = None

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios).", "div_growth": 6.5, "div_yield": 2.8},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos).", "div_growth": 5.0, "div_yield": 4.8},
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5},
    "sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0},
    "santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5},
    "telefónica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico sin dependencia de dividendo tradicional.", "div_growth": 10.0, "div_yield": 0.7},
    "procter & gamble": {"ticker": "PG", "racha": "Excepcional. Aristócrata del Dividendo con más de 65 años de subidas ininterrumpidas.", "div_growth": 6.0, "div_yield": 2.4},
    "copart": {"ticker": "CPRT", "racha": "Empresa pura de crecimiento orientada a reinvestigación.", "div_growth": 0.0, "div_yield": 0.0},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sensible al ciclo económico y a los planes de consolidación bancaria.", "div_growth": 4.5, "div_yield": 6.2}
}

FUND_DB = {
    "vanguard global stock acc": {"name": "Vanguard Global Stock Index Fund EUR Acc", "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 4500, "tracking_error": 0.08, "age_years": 8},
    "vanguard s&p 500 acc": {"name": "Vanguard S&P 500 Stock Index Fund EUR Acc", "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 38000, "tracking_error": 0.03, "age_years": 12},
    "amundi msci world acc": {"name": "Amundi Index MSCI World AE-C", "category": "Renta Variable Global (MSCI World)", "ter": 0.30, "aum": 3200, "tracking_error": 0.12, "age_years": 7}
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

ALL_BROKER_PROFILES = {
    "MyInvestor (Fondos Indexados / Sin custodia)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True
    },
    "Indexa Capital (Cartera / Gestor automatizado)": {
        "fee_percent": 0.45, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True
    },
    "Trade Republic (1€ orden suelta / Planes de ahorro a 0€)": {
        "fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True
    },
    "Lightyear (ETFs sin comisión de ejecución / Muy transparente)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.35, "supports_free_plans": True
    },
    "DEGIRO (Bajas comisiones / 1€ por operación en ETFs)": {
        "fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False
    },
    "Interactive Brokers (Ideal internacional / Tipo de cambio real)": {
        "fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False
    },
    "XTB (0% comisiones hasta 100k€ / Ojo al cambio de divisa)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.20, "fx_fee_percent": 0.50, "supports_free_plans": False
    },
    "Trading 212 (Planes de ahorro y acciones fraccionadas gratis)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.15, "fx_fee_percent": 0.15, "supports_free_plans": True
    },
    "Renta 4 (Banco tradicional / Tarifas altas)": {
        "fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False
    }
}

# Sidebar común para historial
with st.sidebar:
    st.header("📊 Historial de Sesión")
    st.markdown(f"Activos analizados: **{len(st.session_state.history)}**")
    
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
    st.title("📈 Analizador Bursátil Multifuente")
    st.markdown("### ¿Qué deseas hacer hoy?")
    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)
    
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

    with col4:
        if st.button("💼 Cartera Multi-Activo", use_container_width=True, type="primary"):
            st.session_state.asset_type = "Cartera Multi-Activo"
            st.session_state.stage = "analyzer"
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
# ETAPA 2: ANALIZADOR (MOTOR DE EVALUACIÓN Y CARTERA MULTI-ACTIVO)
# ----------------------------------------------------
elif st.session_state.stage == 'analyzer':
    if st.button("← Cambiar categoría / Volver"):
        reset_navigation()
        st.rerun()

    # NUEVO APARTADO: CARTERA MULTI-ACTIVO CON CÁLCULO DE COMISIONES CORREGIDO
    if st.session_state.asset_type == "Cartera Multi-Activo":
        st.title("💼 Simulador de Cartera Multi-Activo Personalizada")
        st.markdown("Configura tu cartera seleccionando Fondos Indexados o ETFs en cada activo, asigna su bróker correspondiente y calcula el ahorro real a largo plazo.")
        
        st.markdown("---")
        st.subheader("1️⃣ Plazo General de la Cartera")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            anos_cartera = st.slider("Plazo temporal global (Años)", min_value=1, max_value=40, value=20, key="cartera_anos")
            frecuencia_cartera = st.selectbox("Frecuencia de aportación", options=["Mensual", "Anual"], key="cartera_freq")
        with col_g2:
            num_activos = st.slider("Número de activos diferentes en tu cartera", min_value=1, max_value=6, value=4, step=1, key="num_act")

        st.markdown("---")
        st.subheader("2️⃣ Configuración Independiente de Cada Activo (Fondos y ETFs)")

        lista_opciones_activos = [
            "📁 [Fondo] Vanguard S&P 500 Stock Index Fund EUR Acc",
            "📁 [Fondo] Vanguard Global Stock Index Fund EUR Acc (MSCI World)",
            "📁 [Fondo] Amundi Index MSCI World AE-C",
            "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Acc)",
            "🌐 [ETF] Vanguard FTSE All-World High Dividend Yield ETF",
            "🌐 [ETF] iShares Physical Gold ETC",
            "🌐 [ETF] iShares Core MSCI Emerging Markets IMI ETF",
            "🌐 [ETF] iShares S&P 500 Information Technology Sector ETF",
            "✍️ Personalizado / Otro activo"
        ]
        
        activos_config = []
        
        for i in range(num_activos):
            default_idx = i if i < len(lista_opciones_activos) else 0
            with st.expander(f"📌 Activo {i+1}", expanded=(i < 2)):
                selected_asset_option = st.selectbox(f"Selecciona el Activo {i+1}", options=lista_opciones_activos, index=default_idx, key=f"sel_asset_{i}")
                
                default_ter, default_rent = 0.15, 7.0
                if "S&P 500" in selected_asset_option:
                    default_ter, default_rent = 0.10, 8.0
                elif "World" in selected_asset_option or "All-World" in selected_asset_option:
                    default_ter, default_rent = 0.18, 7.0
                elif "Gold" in selected_asset_option:
                    default_ter, default_rent = 0.15, 5.5
                elif "Dividend" in selected_asset_option:
                    default_ter, default_rent = 0.29, 6.5
                elif "Fondo" in selected_asset_option:
                    default_ter = 0.18

                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    inv_ini_act = st.number_input(f"Inversión Inicial (€) - {i+1}", min_value=0.0, value=100.0, step=50.0, key=f"ini_{i}")
                    app_per_act = st.number_input(f"Aportación Periódica (€) - {i+1}", min_value=0.0, value=50.0, step=25.0, key=f"app_{i}")
                with col_i2:
                    rent_act = st.slider(f"Rentabilidad anual estimada (%) - {i+1}", min_value=0.0, max_value=15.0, value=default_rent, step=0.5, key=f"rent_{i}")
                    ter_act = st.slider(f"TER anual del activo (%) - {i+1}", min_value=0.0, max_value=1.0, value=default_ter, step=0.05, key=f"ter_{i}")
                
                st.markdown(f"**Bróker o Gestora para este activo:**")
                broker_choice_i = st.selectbox(f"Bróker {i+1}", options=list(ALL_BROKER_PROFILES.keys()), key=f"broker_{i}", label_visibility="collapsed")
                broker_data_i = ALL_BROKER_PROFILES[broker_choice_i]
                
                plan_gratis_i = st.checkbox(f"🚀 Plan de aportación periódica a 0 € (sin comisión por compra recurrente)", value=broker_data_i["supports_free_plans"], key=f"plan_sc_{i}")

                activos_config.append({
                    "nombre": selected_asset_option,
                    "inicial": inv_ini_act,
                    "aportacion": app_per_act,
                    "rentabilidad": rent_act,
                    "ter": ter_act,
                    "broker_data": broker_data_i,
                    "plan_gratis": plan_gratis_i
                })

        # SIMULACIÓN GLOBAL ACUMULADA (CORREGIDA: COMISIÓN PERIÓDICA CERO SI PLAN ACTIVO)
        periodos_por_ano = 12 if frecuencia_cartera == "Mensual" else 1
        total_periodos = anos_cartera * periodos_por_ano

        total_aportado_acumulado = 0.0
        acum_broker_global = 0.0
        acum_spread_global = 0.0
        acum_fx_global = 0.0
        saldo_global_neto = 0.0

        # Costes y saldo de la inversión inicial (mes 0)
        for act in activos_config:
            ini = act["inicial"]
            b_data = act["broker_data"]
            
            c_broker_ini = (ini * (b_data["fee_percent"] / 100.0)) + b_data["fee_fixed"]
            c_spread_ini = ini * (b_data["spread_percent"] / 100.0)
            c_fx_ini = ini * (b_data["fx_fee_percent"] / 100.0)
            coste_ini_total = c_broker_ini + c_spread_ini + c_fx_ini

            saldo_global_neto += max(0.0, ini - coste_ini_total)
            total_aportado_acumulado += ini
            acum_broker_global += c_broker_ini
            acum_spread_global += c_spread_ini
            acum_fx_global += c_fx_ini

        historial_cartera_indiv = []

        for periodo in range(1, total_periodos + 1):
            neto_total_periodo = 0.0
            
            if periodo > 1:
                for act in activos_config:
                    app = act["aportacion"]
                    b_data = act["broker_data"]
                    is_free = act["plan_gratis"]
                    
                    # Si el plan gratuito está activado, la comisión fija y porcentual periódica es 0 €
                    f_fix = 0.0 if is_free else b_data["fee_fixed"]
                    f_perc = 0.0 if is_free else b_data["fee_percent"]
                    
                    cb = (app * (f_perc / 100.0)) + f_fix
                    cs = app * (b_data["spread_percent"] / 100.0)
                    cfx = app * (b_data["fx_fee_percent"] / 100.0)
                    c_op_total = cb + cs + cfx

                    neto_aportado = max(0.0, app - c_op_total)
                    total_aportado_acumulado += app
                    
                    acum_broker_global += cb
                    acum_spread_global += cs
                    acum_fx_global += cfx
                    
                    neto_total_periodo += neto_aportado

            rent_media_pond = sum([a["rentabilidad"] - a["ter"] for a in activos_config]) / len(activos_config)
            tasa_periodica_global = (rent_media_pond / 100.0) / periodos_por_ano

            if periodo > 1:
                saldo_global_neto = saldo_global_neto * (1 + tasa_periodica_global) + neto_total_periodo
            else:
                saldo_global_neto = saldo_global_neto * (1 + tasa_periodica_global)

            if periodo % periodos_por_ano == 0:
                ano_actual = periodo // periodos_por_ano
                total_costes_acum = acum_broker_global + acum_spread_global + acum_fx_global
                intereses_brutos = saldo_global_neto - (total_aportado_acumulado - total_costes_acum)

                historial_cartera_indiv.append({
                    "Año": f"Año {ano_actual}",
                    "Capital Aportado Bruto (€)": round(total_aportado_acumulado, 2),
                    "Comisiones Bróker (€)": round(acum_broker_global, 2),
                    "Coste Spread / Divisa (€)": round(acum_spread_global + acum_fx_global, 2),
                    "Beneficio Bruto (€)": round(max(0.0, intereses_brutos), 2),
                    "Capital Total Bruto (€)": round(saldo_global_neto, 2)
                })

        if historial_cartera_indiv:
            final_c = historial_cartera_indiv[-1]
            beneficio_bruto_f = final_c['Beneficio Bruto (€)']
            impuestos_f = beneficio_bruto_f * 0.19
            beneficio_neto_impuestos_f = beneficio_bruto_f - impuestos_f

            capital_neto_aportado_real = final_c['Capital Aportado Bruto (€)'] - (final_c['Comisiones Bróker (€)'] + final_c['Coste Spread / Divisa (€)'])
            capital_total_liquido_f = capital_neto_aportado_real + beneficio_neto_impuestos_f

            st.markdown("---")
            st.subheader("📊 Resultados Globales de tu Cartera Personalizada")

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Capital Acumulado", f"{final_c['Capital Total Bruto (€)']:,.2f} €")
            m2.metric("Total Aportado Bruto", f"{final_c['Capital Aportado Bruto (€)']:,.2f} €")
            m3.metric("Total Costes", f"{(final_c['Comisiones Bróker (€)'] + final_c['Coste Spread / Divisa (€)']):,.2f} €")
            m4.metric("Beneficio Bruto", f"{beneficio_bruto_f:,.2f} €")
            m5.metric("Impuestos (19%)", f"{impuestos_f:,.2f} €")

            st.markdown(f"""
            <div class="final-net-card">
                <div class="final-net-title">💰 Capital Total Líquido (Ahorro Real Tras Pagar a Hacienda)</div>
                <div class="final-net-value">{capital_total_liquido_f:,.2f} €</div>
            </div>
            """, unsafe_allow_html=True)

            df_res_cartera = pd.DataFrame(historial_cartera_indiv)
            with st.expander("Ver desglose anual detallado de la cartera multi-activo", expanded=True):
                st.dataframe(df_res_cartera, use_container_width=True)

    # ----------------------------------------------------
    # RESTO DE APARTADOS (ACCIONES, FONDOS, ETFS)
    # ----------------------------------------------------
    elif st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
        st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
        ranking_data = [{"Fondo": data["name"], "Categoría": data["category"], "TER Anual (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Antigüedad (Años)": data["age_years"]} for data in FUND_DB.values()]
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_ranking, use_container_width=True)
        st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER (gastos corrientes) de la gestora. Recuerda consultar y añadir las comisiones de custodia de tu entidad.")

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
        st.title("🏆 Ranking de ETFs (Ordenados por menor TER)")
        ranking_etfs = [{"ETF": data["name"], "Ticker": data["ticker"], "Categoría": data["category"], "TER (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Réplica": data["replication"]} for data in ETF_DB.values()]
        df_etf_ranking = pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_etf_ranking, use_container_width=True)
        st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER (gastos corrientes) de la gestora. Recuerda consultar y añadir las comisiones de compraventa, custodia o cambio de divisa que aplique tu bróker.")

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Explorador ETFs":
        st.title("🗺️ Guía y Tipos de ETFs Disponibles")
        st.markdown("Selecciona una categoría para entender su objetivo, nivel de riesgo y ver ejemplos destacados:")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🌍 Globales", "💰 Dividendos", "🥇 Materias Primas", "💻 Tecnología", "⚡ Renovables & Eléctricas", "🚀 Emergentes"])
        
        with tab1:
            st.subheader("Renta Variable Global (Ej: MSCI World / FTSE All-World)")
            st.markdown("- **Objetivo:** Invertir de forma diversificada en miles de empresas de países desarrollados o de todo el mundo.")
            st.markdown("- **Perfil de riesgo:** Moderado-Alto (renta variable a largo plazo).")
            st.markdown("- **Ideal para:** La columna vertebral o núcleo (*core*) de cualquier cartera de inversión a largo plazo.")
            st.markdown("- *Ejemplo en BD:* `Vanguard FTSE All-World UCITS ETF (Acc)`")
            
        with tab2:
            st.subheader("Empresas de Alto Dividendo (High Dividend Yield)")
            st.markdown("- **Objetivo:** Seleccionar empresas maduras con flujos de caja estables que reparten una parte importante de sus beneficios en dividendos.")
            st.markdown("- **Perfil de riesgo:** Moderado (empresas menos volátiles y más defensivas).")
            st.markdown("- **Ideal para:** Inversores que buscan generar ingresos periódicos o rentas complementarias.")
            st.markdown("- *Ejemplo en BD:* `Vanguard FTSE All-World High Dividend Yield ETF`")

        with tab3:
            st.subheader("Materias Primas (Commodities / ETCs)")
            st.markdown("- **Objetivo:** Exposición directa a activos físicos como oro, plata, energía o metales industriales.")
            st.markdown("- **Perfil de riesgo:** Medio-Alto (actúan como refugio ante la inflación, pero con altibajos cíclicos).")
            st.markdown("- **Ideal para:** Descorrelacionar la cartera y proteger el poder adquisitivo frente a crisis o inflación.")
            st.markdown("- *Ejemplo en BD:* `iShares Physical Gold ETC`")

        with tab4:
            st.subheader("Sector Tecnológico")
            st.markdown("- **Objetivo:** Invertir en los gigantes de la innovación, software, semiconductores e inteligencia artificial.")
            st.markdown("- **Perfil de riesgo:** Alto (gran potencial de revalorización pero también mayor volatilidad y caídas puntuales).")
            st.markdown("- **Ideal para:** Dar un sesgo de crecimiento (*growth*) a una parte de la cartera.")
            st.markdown("- *Ejemplo en BD:* `iShares S&P 500 Information Technology Sector ETF`")

        with tab5:
            st.subheader("Energías Renovables y Eléctricas (Utilities)")
            st.markdown("- **Objetivo:** Empresas dedicadas a la transición energética (solar, eólica) o compañías eléctricas tradicionales reguladas.")
            st.markdown("- **Perfil de riesgo:** Variable (las eléctricas son muy defensivas y estables; las renovables puras son muy cíclicas y sensibles a los tipos de interés).")
            st.markdown("- **Ideal para:** Apostar por macrotendencias de sostenibilidad o buscar flujos defensivos estables.")
            st.markdown("- *Ejemplos en BD:* `iShares Global Clean Energy` / `iShares STOXX Europe 600 Utilities`")

        with tab6:
            st.subheader("Empresas Emergentes (Emerging Markets)")
            st.markdown("- **Objetivo:** Exposición a economías en rápido desarrollo como Asia (China, India), Latinoamérica o Europa del Este.")
            st.markdown("- **Perfil de riesgo:** Alto (mayor exposición a riesgos geopolíticos, divisas volátiles y ciclos económicos diferentes a Occidente).")
            st.markdown("- **Ideal para:** Complementar la cartera global buscando mayor diversificación geográfica y crecimiento demográfico.")
            st.markdown("- *Ejemplo en BD:* `iShares Core MSCI Emerging Markets IMI ETF`")
