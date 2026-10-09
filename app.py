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

FUND_BROKER_PROFILES = {
    "MyInvestor (Fondos Indexados / Sin custodia)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True
    },
    "Indexa Capital (Cartera / Gestor automatizado)": {
        "fee_percent": 0.45, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True
    },
    "Renta 4 (Banco tradicional / Tarifas altas)": {
        "fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False
    },
    "Personalizado (Ajustar manualmente las comisiones)": {
        "fee_percent": 0.10, "fee_fixed": 2.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False
    }
}

ETF_BROKER_PROFILES = {
    "Trade Republic (1€ orden suelta / Planes de ahorro a 0€)": {
        "fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True
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
    "eToro (Social Trading / Acciones y ETFs)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.50, "fx_fee_percent": 0.50, "supports_free_plans": False
    },
    "Renta 4 (Banco tradicional / Tarifas altas)": {
        "fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False
    },
    "Personalizado (Ajustar manualmente las comisiones)": {
        "fee_percent": 0.10, "fee_fixed": 2.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False
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
    st.markdown("### ¿Qué tipo de activo quieres evaluar?")
    st.markdown("")

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
# ETAPA 2: ANALIZADOR (MOTOR DE EVALUACIÓN Y EXPLORADOR)
# ----------------------------------------------------
elif st.session_state.stage == 'analyzer':
    if st.button("← Cambiar categoría / Volver"):
        st.session_state.stage = 'sub_options'
        st.session_state.sub_type = None
        st.rerun()

    if st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
        st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
        ranking_data = [{"Fondo": data["name"], "Categoría": data["category"], "TER Anual (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Antigüedad (Años)": data["age_years"]} for data in FUND_DB.values()]
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_ranking, use_container_width=True)
        st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER (gastos corrientes) de la gestora. Recuerda consultar y añadir las comisiones de compraventa, custodia o cambio de divisa que aplique tu entidad.")
        if st.button("← Volver al menú de fondos"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
        st.title("🏆 Ranking de ETFs (Ordenados por menor TER)")
        ranking_etfs = [{"ETF": data["name"], "Ticker": data["ticker"], "Categoría": data["category"], "TER (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Réplica": data["replication"]} for data in ETF_DB.values()]
        df_etf_ranking = pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_etf_ranking, use_container_width=True)
        st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER (gastos corrientes) de la gestora. Recuerda consultar y añadir las comisiones de compraventa, custodia o cambio de divisa que aplique tu bróker.")
        if st.button("← Volver al menú de ETFs"):
            st.session_state.sub_type = None
            st.rerun()

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

        st.markdown("---")
        if st.button("← Volver al menú principal de ETFs"):
            st.session_state.sub_type = None
            st.rerun()

    else:
        st.title(f"📈 Analizador: {st.session_state.asset_type} ({st.session_state.sub_type})")

        if st.session_state.asset_type == "Acciones":
            user_input = st.text_input("Nombre de empresa o Ticker", value="", placeholder="Escribe el nombre de la acción (ej. Inditex, Iberdrola, Microsoft...)").strip()
        elif st.session_state.asset_type == "Fondos indexados":
            fund_options = ["-- Selecciona o escribe un fondo --"] + [data["name"] for data in FUND_DB.values()]
            selected_fund_option = st.selectbox("🔍 Buscador predictivo de Fondos Indexados", options=fund_options)
            user_input = "" if selected_fund_option == "-- Selecciona o escribe un fondo --" else selected_fund_option
        elif st.session_state.asset_type == "ETFs":
            etf_options = ["-- Selecciona un ETF (Global, Tecnología, Renovables, Materias Primas, Dividendos...) --"] + [f"{data['name']} [{data['category']}] ({data['ticker']})" for data in ETF_DB.values()]
            selected_etf_option = st.selectbox("🌐 Buscador predictivo de ETFs", options=etf_options)
            user_input = "" if selected_etf_option.startswith("--") else selected_etf_option.split("(")[-1].replace(")", "").strip()

        def get_stock_data(query):
            q_lower = query.lower().strip()
            if q_lower in TICKER_DB:
                data = TICKER_DB[q_lower]
                return data.get("ticker", query.upper()), data.get("racha", "Sin datos"), data.get("div_growth", 3.0), data.get("div_yield", None)
            return query.upper(), "Sin datos de racha previos (Evaluación estándar).", 3.0, None

        def get_letter_grade(score):
            if score >= 4.5: return "A+"
            elif score >= 4.0: return "A"
            elif score >= 3.0: return "B"
            elif score >= 2.0: return "C"
            else: return "D"

        if not user_input:
            st.info("👆 Selecciona o introduce un activo en el cuadro superior para comenzar el análisis.")
        else:
            # ----------------------------------------------------
            # CASO A: ACCIONES
            # ----------------------------------------------------
            if st.session_state.asset_type == "Acciones":
                stock_result = get_stock_data(user_input)
                ticker_input, racha_info, est_div_growth, db_div_yield = stock_result if isinstance(stock_result, tuple) else (user_input.upper(), "Sin datos", 3.0, None)
                
                try:
                    stock = yf.Ticker(ticker_input)
                    hist_price = stock.history(period="5d")
                    current_price = hist_price['Close'].iloc[-1] if not hist_price.empty else None
                    info = stock.info or {}

                    name = info.get('longName', user_input.title())
                    currency_symbol = '$' if info.get('currency') == 'USD' else '€'
                    price_display = f"{current_price:,.2f} {currency_symbol}" if current_price is not None else "—"

                    per_y = info.get('trailingPE') or info.get('forwardPE') or 20.0
                    pfcf_y = info.get('priceToFreeCashflow') or 18.0
                    pb_y = info.get('priceToBook') or 3.0
                    roe_val = (info.get('returnOnEquity', 0.15) * 100)
                    div_y_val = (info.get('dividendYield', 0) * 100) if info.get('dividendYield') else (db_div_yield or 0.0)
                    bpa_y = info.get('trailingEps') or 2.0
                    beta_val = info.get('beta') or 1.0
                    payout_val = (info.get('payoutRatio', 0.5) * 100)

                    total_score = 0
                    if st.session_state.sub_type == "Con dividendos":
                        total_score += (1.0 if per_y <= 10 else (0.5 if per_y <= 25 else 0.0))
                        total_score += (1.0 if beta_val < 1.0 else (0.5 if beta_val <= 1.1 else 0.0))
                        total_score += (1.0 if (0 <= div_y_val <= 6.0) else (0.5 if (6.0 < div_y_val <= 9.0) else 0.0))
                        total_score += (1.0 if (35.0 <= payout_val <= 75.0) else 0.0)
                        total_score += (1.0 if est_div_growth > 3.0 else 0.5)
                    else:
                        total_score += (1.0 if per_y <= 25 else 0.5)
                        total_score += (1.0 if pfcf_y <= 20 else 0.5)
                        total_score += (1.0 if pb_y <= 4.0 else 0.5)
                        total_score += (1.0 if roe_val >= 15.0 else 0.5)
                        total_score += (1.0 if bpa_y > 0 else 0.0)

                    grade = get_letter_grade(total_score)
                    deg = int((total_score / 5.0) * 360)
                    progress_color = "#22c55e" if total_score >= 4.0 else ("#eab308" if total_score >= 3.0 else "#ef4444")

                    st.subheader(f"📊 Informe: {name} ({ticker_input})")
                    st.markdown(f"""
                    <div class="score-container">
                        <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg}deg; --progress-color: {progress_color};"><div class="progress-value">{total_score:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio Actual</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    df_metrics = pd.DataFrame({
                        "Métrica Clave": ["PER (Valoración)", "Precio / FCF", "Precio / Valor Contable (P/B)", "ROE (Rentabilidad)", "Dividendo Yield", "Payout Ratio", "Beta (Volatilidad)"],
                        "Valor Evaluado": [f"{per_y:.2f}", f"{pfcf_y:.2f}", f"{pb_y:.2f}", f"{roe_val:.2f}%", f"{div_y_val:.2f}%", f"{payout_val:.1f}%", f"{beta_val:.2f}"]
                    })
                    st.table(df_metrics)

                    st.markdown("### 📝 Conclusiones y Perspectiva Analítica")
                    if st.session_state.sub_type == "Con dividendos":
                        st.markdown(f"- **Historial de Dividendos y Racha:** {racha_info}")
                        st.markdown(f"- **Sostenibilidad del Payout:** Un payout del {payout_val:.1f}% indica el porcentaje del beneficio destinado a retribuir al accionista.")
                    else:
                        st.markdown(f"- **Perfil de Crecimiento:** Empresa evaluada bajo criterios estrictos de valoración y eficiencia operativa (ROE del {roe_val:.2f}%).")

                    if total_score >= 4.0:
                        st.success(f"🟢 **VEREDICTO POSITIVO:** Activo con excelentes fundamentales y calificación alta ({grade}).")
                    elif total_score >= 3.0:
                        st.warning(f"🟡 **VEREDICTO MODERADO:** Activo aceptable pero con ciertos puntos de atención en valoración o riesgo.")
                    else:
                        st.error(f"🔴 **VEREDICTO DESFAVORABLE:** Métricas actuales poco atractivas bajo los criterios de selección.")

                except Exception as e:
                    st.error(f"Error al procesar los datos de la acción: {e}")

            # ----------------------------------------------------
            # CASO B: FONDOS INDEXADOS
            # ----------------------------------------------------
            elif st.session_state.asset_type == "Fondos indexados":
                matched_fund = next((data for key, data in FUND_DB.items() if data["name"] == user_input or key in user_input.lower()), None)
                
                ter_val = matched_fund["ter"] if matched_fund else 0.20
                aum_val = matched_fund["aum"] if matched_fund else 1500
                te_val = matched_fund["tracking_error"] if matched_fund else 0.09
                age_val = matched_fund["age_years"] if matched_fund else 6
                fund_name = matched_fund["name"] if matched_fund else user_input

                score_fund = 0
                score_fund += (1.0 if ter_val <= 0.20 else (0.5 if ter_val <= 0.50 else 0.0))
                score_fund += (1.0 if aum_val > 500 else 0.5)
                score_fund += (1.0 if te_val <= 0.10 else 0.5)
                score_fund += (1.0 if st.session_state.sub_type == "Acumulación" else 0.5)
                score_fund += (1.0 if age_val > 5 else 0.5)

                grade_fund = get_letter_grade(score_fund)
                deg_fund = int((score_fund / 5.0) * 360)
                color_fund = "#22c55e" if score_fund >= 4.0 else ("#eab308" if score_fund >= 3.0 else "#ef4444")

                st.subheader(f"📊 Informe de Fondo: {fund_name}")
                st.markdown(f"""
                <div class="score-container">
                    <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg_fund}deg; --progress-color: {color_fund};"><div class="progress-value">{score_fund:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación Pasiva</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {color_fund};">{grade_fund}</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Antigüedad</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{age_val} Años</div></div>
                </div>
                """, unsafe_allow_html=True)

                df_fund_data = {
                    "Métrica del Fondo": ["TER (Gastos Corrientes)", "Patrimonio (AUM)", "Tracking Error", "Política", "Antigüedad"],
                    "Valor Actual": [f"{ter_val:.2f}% anual", f"{aum_val:,.0f} M€", f"{te_val:.2f}%", st.session_state.sub_type, f"{age_val} años"]
                }
                st.table(pd.DataFrame(df_fund_data))
                st.info("⚠️ **Aviso de Comisiones:** El TER indicado corresponde exclusivamente a los gastos corrientes de la gestora. No olvides añadir las posibles comisiones de custodia de tu entidad.")

                # CALCULADORA DE INTERÉS COMPUESTO PARA FONDOS
                st.markdown("---")
                st.subheader(f"🧮 Simulador de Interés Compuesto con Comisiones e Impuestos: {fund_name}")
                
                activar_calc_fondo = st.toggle("Activar calculadora de interés compuesto con comisiones para este fondo", value=False, key="toggle_fondo")

                if activar_calc_fondo:
                    selected_broker = st.selectbox("Selecciona tu Entidad o Comercializador de Fondos", options=list(FUND_BROKER_PROFILES.keys()), key="broker_fondo")
                    broker_data = FUND_BROKER_PROFILES[selected_broker]

                    plan_sin_comision_f = st.checkbox("🚀 Plan de aportación periódica automatizada sin comisión (0 € por compra recurrente)", value=broker_data["supports_free_plans"], key="plan_sc_f")

                    col_fb1, col_fb2 = st.columns(2)
                    with col_fb1:
                        inversion_inicial_f = st.number_input("Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key="inv_ini_f")
                        aportacion_periodica_f = st.number_input("Aportación Periódica (€)", min_value=0.0, value=150.0, step=50.0, key="app_per_f")
                        frecuencia_f = st.selectbox("Frecuencia de aportación", options=["Mensual", "Anual"], key="freq_f")
                    
                    with col_fb2:
                        anos_f = st.slider("Plazo temporal (Años)", min_value=1, max_value=40, value=15, key="anos_f")
                        rentabilidad_anual_f = st.slider("Rentabilidad anual estimada del fondo (%)", min_value=0.0, max_value=20.0, value=7.5, step=0.5, key="rent_f")

                    if selected_broker.startswith("Personalizado"):
                        fee_percent_val = st.number_input("Comisión sobre operación (%)", min_value=0.0, max_value=2.0, value=0.0, step=0.05, key="f_perc")
                        fee_fixed_val = st.number_input("Comisión fija por operación (€)", min_value=0.0, max_value=20.0, value=0.0, step=0.5, key="f_fix")
                        spread_percent_val = st.number_input("Spread (%)", min_value=0.0, max_value=1.0, value=0.05, step=0.05, key="f_spr")
                        fx_fee_percent_val = st.number_input("Comisión cambio divisa / FX (%)", min_value=0.0, max_value=1.0, value=0.30, step=0.05, key="f_fx")
                    else:
                        fee_percent_val = broker_data["fee_percent"]
                        fee_fixed_val = broker_data["fee_fixed"]
                        spread_percent_val = broker_data["spread_percent"]
                        fx_fee_percent_val = broker_data["fx_fee_percent"]

                    # Lógica inteligente por bróker: solo 0€ si el bróker soporta planes gratuitos Y el usuario activa la casilla
                    can_have_free_plan_f = broker_data["supports_free_plans"] and plan_sin_comision_f
                    fee_fixed_per_efectiva = 0.0 if can_have_free_plan_f else fee_fixed_val
                    fee_percent_per_efectiva = 0.0 if can_have_free_plan_f else fee_percent_val
                    fx_fee_efectiva = fx_fee_percent_val

                    periodos_por_ano_f = 12 if frecuencia_f == "Mensual" else 1
                    tasa_neta_anual = rentabilidad_anual_f - ter_val
                    tasa_periodica_f = (tasa_neta_anual / 100.0) / periodos_por_ano_f
                    total_periodos_f = anos_f * periodos_por_ano_f

                    coste_broker_ini = (inversion_inicial_f * (fee_percent_val / 100.0)) + fee_fixed_val
                    coste_spread_ini = inversion_inicial_f * (spread_percent_val / 100.0)
                    coste_fx_ini = inversion_inicial_f * (fx_fee_percent_val / 100.0)
                    coste_total_ini = coste_broker_ini + coste_spread_ini + coste_fx_ini

                    saldo_actual_f = max(0.0, inversion_inicial_f - coste_total_ini)
                    total_aportado_acumulado = inversion_inicial_f
                    
                    acum_broker = coste_broker_ini
                    acum_spread = coste_spread_ini
                    acum_fx = coste_fx_ini
                    
                    historial_crecimiento_f = []

                    for periodo in range(1, total_periodos_f + 1):
                        if periodo > 1:
                            c_broker = (aportacion_periodica_f * (fee_percent_per_efectiva / 100.0)) + fee_fixed_per_efectiva
                            c_spread = aportacion_periodica_f * (spread_percent_val / 100.0)
                            c_fx = aportacion_periodica_f * (fx_fee_efectiva / 100.0)
                            c_total_op = c_broker + c_spread + c_fx
                            
                            import_neto_aportado = max(0.0, aportacion_periodica_f - c_total_op)
                            total_aportado_acumulado += aportacion_periodica_f
                            
                            acum_broker += c_broker
                            acum_spread += c_spread
                            acum_fx += c_fx
                            
                            saldo_actual_f = saldo_actual_f * (1 + tasa_periodica_f) + import_neto_aportado
                        else:
                            saldo_actual_f = saldo_actual_f * (1 + tasa_periodica_f)

                        if periodo % periodos_por_ano_f == 0:
                            ano_actual = periodo // periodos_por_ano_f
                            total_costes_acumulados = acum_broker + acum_spread + acum_fx
                            intereses_brutos = saldo_actual_f - (total_aportado_acumulado - total_costes_acumulados)
                            
                            historial_crecimiento_f.append({
                                "Año": f"Año {ano_actual}",
                                "Capital Aportado Bruto (€)": round(total_aportado_acumulado, 2),
                                "Comisiones Bróker (€)": round(acum_broker, 2),
                                "Coste Spread (€)": round(acum_spread, 2),
                                "Coste Cambio Divisa (€)": round(acum_fx, 2),
                                "Beneficio Neto (€)": round(max(0.0, intereses_brutos), 2),
                                "Capital Total Neto (€)": round(saldo_actual_f, 2)
                            })

                    if historial_crecimiento_f:
                        final_res_f = historial_crecimiento_f[-1]
                        coste_unitario_op = (aportacion_periodica_f * (fee_percent_per_efectiva / 100.0)) + fee_fixed_per_efectiva + (aportacion_periodica_f * (spread_percent_val / 100.0)) + (aportacion_periodica_f * (fx_fee_efectiva / 100.0))
                        
                        beneficio_bruto_final = final_res_f['Beneficio Neto (€)']
                        impuestos_finales = beneficio_bruto_final * 0.19
                        beneficio_neto_impuestos = beneficio_bruto_final - impuestos_finales
                        
                        capital_neto_aportado_real = final_res_f['Capital Aportado Bruto (€)'] - (final_res_f['Comisiones Bróker (€)'] + final_res_f['Coste Spread (€)'] + final_res_f['Coste Cambio Divisa (€)'])
                        capital_total_liquido = capital_neto_aportado_real + beneficio_neto_impuestos

                        st.markdown("### 📊 Resultados de la Simulación (Neto de Comisiones e Impuestos)")
                        st.info(f"💡 **Costes por operación periódica:** Estás pagando aprox. **{coste_unitario_op:,.2f} €** en cada aportación.")

                        fm1, fm2, fm3, fm4, fm5 = st.columns(5)
                        fm1.metric("Capital Bruto Acumulado", f"{final_res_f['Capital Total Neto (€)']:,.2f} €")
                        fm2.metric("Total Aportado", f"{final_res_f['Capital Aportado Bruto (€)']:,.2f} €")
                        fm3.metric("Total de Costes Acumulados", f"{(final_res_f['Comisiones Bróker (€)'] + final_res_f['Coste Spread (€)'] + final_res_f['Coste Cambio Divisa (€)']):,.2f} €")
                        fm4.metric("Beneficio Bruto", f"{beneficio_bruto_final:,.2f} €")
                        fm5.metric("Beneficio Neto", f"{beneficio_neto_impuestos:,.2f} €")

                        st.markdown(f"""
                        <div class="final-net-card">
                            <div class="final-net-title">💰 Capital Total Líquido (Ahorro Real Tras Pagar a Hacienda)</div>
                            <div class="final-net-value">{capital_total_liquido:,.2f} €</div>
                        </div>
                        """, unsafe_allow_html=True)

                        df_sim_f = pd.DataFrame(historial_crecimiento_f)
                        with st.expander("Ver desglose anual detallado con comisiones y spreads separados", expanded=True):
                            st.dataframe(df_sim_f, use_container_width=True)
                            if can_have_free_plan_f:
                                st.caption("ℹ️ *Nota: En el primer depósito de la inversión inicial (Año 1), se aplica la comisión fija correspondiente de 1 € (orden suelta); el resto de aportaciones periódicas van a 0 € gracias al plan automatizado del bróker.*")

            # ----------------------------------------------------
            # CASO C: ETFS
            # ----------------------------------------------------
            elif st.session_state.asset_type == "ETFs":
                matched_etf = next((data for key, data in ETF_DB.items() if data["ticker"] == user_input or data["name"] in user_input), None)
                
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
                    etf_name = user_input.upper()
                    etf_ticker = user_input.upper()
                    etf_cat = "Sectorial / Especializado"
                    ter_etf = 0.35
                    aum_etf = 800
                    repl_etf = "Física (Completa)"
                    te_etf = 0.10
                    curr_etf = "EUR"
                    age_etf = 4

                etf_price = None
                try:
                    etf_stock = yf.Ticker(etf_ticker)
                    etf_hist = etf_stock.history(period="5d")
                    if not etf_hist.empty:
                        etf_price = etf_hist['Close'].iloc[-1]
                except:
                    pass

                price_display_etf = f"{etf_price:,.2f} €" if etf_price is not None else "—"

                score_etf = 0
                max_ter_threshold = 0.50 if "Renovables" in etf_cat or "Tecnología" in etf_cat else 0.15
                score_etf += (1.0 if ter_etf <= max_ter_threshold else (0.5 if ter_etf <= 0.70 else 0.0))
                score_etf += (1.0 if aum_etf > 1000 else (0.5 if aum_etf >= 200 else 0.0))
                score_etf += (1.0 if "Física" in repl_etf and te_etf <= 0.10 else 0.5)
                score_etf += (1.0 if curr_etf == "EUR" else 0.5)
                score_etf += (1.0 if age_etf > 5 else (0.5 if age_etf >= 2 else 0.0))

                grade_etf = get_letter_grade(score_etf)
                deg_etf = int((score_etf / 5.0) * 360)
                color_etf = "#22c55e" if score_etf >= 4.0 else ("#eab308" if score_etf >= 3.0 else "#ef4444")
                verdict_etf = "ETF ALTAMENTE EFICIENTE / ÓPTIMO" if score_etf >= 4.0 else "ETF ADECUADO"

                st.subheader(f"🌐 Informe de ETF: {etf_name} ({etf_ticker})")
                st.markdown(f"""
                <div class="score-container">
                    <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg_etf}deg; --progress-color: {color_etf};"><div class="progress-value">{score_etf:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación ETF</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {color_etf};">{grade_etf}</div></div>
                    <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio en Mercado</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display_etf}</div></div>
                </div>
                """, unsafe_allow_html=True)

                df_etf_data = {
                    "Métrica del ETF": ["Categoría Temática", "TER (Gastos Anuales)", "Patrimonio (AUM)", "Tipo de Réplica", "Tracking Error", "Divisa", "Antigüedad"],
                    "Valor Actual": [etf_cat, f"{ter_etf:.2f}% anual", f"{aum_etf:,.0f} M€", repl_etf, f"{te_etf:.2f}%", curr_etf, f"{age_etf} años"]
                }
                st.table(pd.DataFrame(df_etf_data))
                st.info(f"⚠️ **Aviso de Divisa y Comisiones:** Este ETF cotiza en divisa **{curr_etf}**. Si operas en una divisa diferente, ten en cuenta el recargo por cambio de divisa de tu bróker.")

                st.markdown("### 📝 Perspectiva Analítica y Veredicto")
                if score_etf >= 4.0:
                    st.success(f"🟢 **VEREDICTO: {verdict_etf}**\n\n*Justificación:* Excelente combinación en su categoría temática, adecuada capitalización y sólida estructura de réplica.")
                elif score_etf >= 3.0:
                    st.warning(f"🟡 **VEREDICTO: {verdict_etf}**\n\n*Justificación:* ETF sectorial/temático apto para satélites de cartera, con ligera penalización en costes o volatilidad.")
                else:
                    st.error(f"🔴 **VEREDICTO: {verdict_etf}**\n\n*Justificación:* Los costes elevados o el escaso patrimonio penalizan la eficiencia de este fondo sectorial.")

                # CALCULADORA DE INTERÉS COMPUESTO PARA ETFS
                st.markdown("---")
                st.subheader(f"🧮 Simulador de Interés Compuesto con Comisiones e Impuestos: {etf_name}")
                
                activar_calculadora = st.toggle("Activar calculadora de interés compuesto con comisiones para este ETF", value=False, key="toggle_etf")

                if activar_calculadora:
                    selected_broker_etf = st.selectbox("Selecciona tu Bróker de la lista", options=list(ETF_BROKER_PROFILES.keys()), key="broker_etf")
                    broker_data_etf = ETF_BROKER_PROFILES[selected_broker_etf]

                    plan_sin_comision_e = st.checkbox("🚀 Plan de aportación periódica automatizada sin comisión (0 € por compra recurrente)", value=broker_data_etf["supports_free_plans"], key="plan_sc_e")

                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        inversion_inicial = st.number_input("Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key="inv_ini_e")
                        aportacion_periodica = st.number_input("Aportación Periódica (€)", min_value=0.0, value=150.0, step=50.0, key="app_per_e")
                        frecuencia = st.selectbox("Frecuencia de aportación", options=["Mensual", "Anual"], key="freq_e")
                    
                    with col_c2:
                        anos = st.slider("Plazo temporal (Años)", min_value=1, max_value=40, value=15, key="anos_e")
                        default_rentabilidad = 7.0 if "Global" in etf_cat or "S&P" in etf_cat else (5.0 if "Materias" in etf_cat or "Utilities" in etf_cat else 8.5)
                        rentabilidad_anual = st.slider("Rentabilidad anual estimada (%)", min_value=0.0, max_value=20.0, value=default_rentabilidad, step=0.5, key="rent_e")

                    if selected_broker_etf.startswith("Personalizado"):
                        fee_percent_val_e = st.number_input("Comisión sobre operación (%)", min_value=0.0, max_value=2.0, value=0.0, step=0.05, key="e_perc")
                        fee_fixed_val_e = st.number_input("Comisión fija por operación (€)", min_value=0.0, max_value=20.0, value=1.0, step=0.5, key="e_fix")
                        spread_percent_val_e = st.number_input("Spread (%)", min_value=0.0, max_value=1.0, value=0.10, step=0.05, key="e_spr")
                        fx_fee_percent_val_e = st.number_input("Comisión cambio divisa / FX (%)", min_value=0.0, max_value=1.0, value=0.25, step=0.05, key="e_fx")
                    else:
                        fee_percent_val_e = broker_data_etf["fee_percent"]
                        fee_fixed_val_e = broker_data_etf["fee_fixed"]
                        spread_percent_val_e = broker_data_etf["spread_percent"]
                        fx_fee_percent_val_e = broker_data_etf["fx_fee_percent"]

                    # Lógica inteligente por bróker: solo 0€ si el bróker soporta planes gratuitos Y el usuario activa la casilla
                    can_have_free_plan_e = broker_data_etf["supports_free_plans"] and plan_sin_comision_e
                    fee_fixed_e_efectiva = 0.0 if can_have_free_plan_e else fee_fixed_val_e
                    fee_percent_e_efectiva = 0.0 if can_have_free_plan_e else fee_percent_val_e
                    fx_fee_e_efectiva = fx_fee_percent_val_e

                    periodos_por_ano = 12 if frecuencia == "Mensual" else 1
                    tasa_neta_anual_e = rentabilidad_anual - ter_etf
                    tasa_periodica = (tasa_neta_anual_e / 100.0) / periodos_por_ano
                    total_periodos = anos * periodos_por_ano

                    coste_broker_ini_e = (inversion_inicial * (fee_percent_val_e / 100.0)) + fee_fixed_val_e
                    coste_spread_ini_e = inversion_inicial * (spread_percent_val_e / 100.0)
                    coste_fx_ini_e = inversion_inicial * (fx_fee_percent_val_e / 100.0)
                    coste_total_ini_e = coste_broker_ini_e + coste_spread_ini_e + coste_fx_ini_e

                    saldo_actual = max(0.0, inversion_inicial - coste_total_ini_e)
                    total_aportado_acumulado_e = inversion_inicial
                    
                    acum_broker_e = coste_broker_ini_e
                    acum_spread_e = coste_spread_ini_e
                    acum_fx_e = coste_fx_ini_e
                    
                    historial_crecimiento = []

                    for periodo in range(1, total_periodos + 1):
                        if periodo > 1:
                            c_broker_e = (aportacion_periodica * (fee_percent_e_efectiva / 100.0)) + fee_fixed_e_efectiva
                            c_spread_e = aportacion_periodica * (spread_percent_val_e / 100.0)
                            c_fx_e = aportacion_periodica * (fx_fee_e_efectiva / 100.0)
                            c_total_op_e = c_broker_e + c_spread_e + c_fx_e
                            
                            import_neto_aportado_e = max(0.0, aportacion_periodica - c_total_op_e)
                            total_aportado_acumulado_e += aportacion_periodica
                            
                            acum_broker_e += c_broker_e
                            acum_spread_e += c_spread_e
                            acum_fx_e += c_fx_e
                            
                            saldo_actual = saldo_actual * (1 + tasa_periodica) + import_neto_aportado_e
                        else:
                            saldo_actual = saldo_actual * (1 + tasa_periodica)

                        if periodo % periodos_por_ano == 0:
                            ano_actual = periodo // periodos_por_ano
                            total_costes_acumulados_e = acum_broker_e + acum_spread_e + acum_fx_e
                            intereses_brutos_e = saldo_actual - (total_aportado_acumulado_e - total_costes_acumulados_e)
                            
                            historial_crecimiento.append({
                                "Año": f"Año {ano_actual}",
                                "Capital Aportado Bruto (€)": round(total_aportado_acumulado_e, 2),
                                "Comisiones Bróker (€)": round(acum_broker_e, 2),
                                "Coste Spread (€)": round(acum_spread_e, 2),
                                "Coste Cambio Divisa (€)": round(acum_fx_e, 2),
                                "Beneficio Neto (€)": round(max(0.0, intereses_brutos_e), 2),
                                "Capital Total Neto (€)": round(saldo_actual, 2)
                            })

                    if historial_crecimiento:
                        final_result = historial_crecimiento[-1]
                        coste_unitario_op_e = (aportacion_periodica * (fee_percent_e_efectiva / 100.0)) + fee_fixed_e_efectiva + (aportacion_periodica * (spread_percent_val_e / 100.0)) + (aportacion_periodica * (fx_fee_e_efectiva / 100.0))
                        
                        beneficio_bruto_final_e = final_result['Beneficio Neto (€)']
                        impuestos_finales_e = beneficio_bruto_final_e * 0.19
                        beneficio_neto_impuestos_e = beneficio_bruto_final_e - impuestos_finales_e
                        
                        capital_neto_aportado_real_e = final_result['Capital Aportado Bruto (€)'] - (final_result['Comisiones Bróker (€)'] + final_result['Coste Spread (€)'] + final_result['Coste Cambio Divisa (€)'])
                        capital_total_liquido_e = capital_neto_aportado_real_e + beneficio_neto_impuestos_e

                        st.markdown("### 📊 Resultados de la Simulación (Neto de Comisiones e Impuestos)")
                        st.info(f"💡 **Costes por operación periódica:** Estás pagando aprox. **{coste_unitario_op_e:,.2f} €** en cada aportación.")

                        m1, m2, m3, m4, m5 = st.columns(5)
                        m1.metric("Capital Bruto Acumulado", f"{final_result['Capital Total Neto (€)']:,.2f} €")
                        m2.metric("Total Aportado", f"{final_result['Capital Aportado Bruto (€)']:,.2f} €")
                        m3.metric("Total de Costes Acumulados", f"{(final_result['Comisiones Bróker (€)'] + final_result['Coste Spread (€)'] + final_result['Coste Cambio Divisa (€)']):,.2f} €")
                        m4.metric("Beneficio Bruto", f"{beneficio_bruto_final_e:,.2f} €")
                        m5.metric("Beneficio Neto", f"{beneficio_neto_impuestos_e:,.2f} €")

                        st.markdown(f"""
                        <div class="final-net-card">
                            <div class="final-net-title">💰 Capital Total Líquido (Ahorro Real Tras Pagar a Hacienda)</div>
                            <div class="final-net-value">{capital_total_liquido_e:,.2f} €</div>
                        </div>
                        """, unsafe_allow_html=True)

                        df_simulacion = pd.DataFrame(historial_crecimiento)
                        with st.expander("Ver desglose anual detallado con comisiones y spreads separados", expanded=True):
                            st.dataframe(df_simulacion, use_container_width=True)
                            if can_have_free_plan_e:
                                st.caption("ℹ️ *Nota: En el primer depósito de la inversión inicial (Año 1), se aplica la comisión fija correspondiente de 1 € (orden suelta); el resto de aportaciones periódicas van a 0 € gracias al plan automatizado del bróker.*")
