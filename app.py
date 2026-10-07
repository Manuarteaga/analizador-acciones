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
    "vanguard emerging markets acc": {"name": "Vanguard Emerging Markets Stock Index Fund EUR Acc", "category": "Renta Variable Emergente", "ter": 0.23, "aum": 2900, "tracking_error": 0.12, "age_years": 9},
    "amundi msci world acc": {"name": "Amundi Index MSCI World AE-C", "category": "Renta Variable Global (MSCI World)", "ter": 0.30, "aum": 3200, "tracking_error": 0.12, "age_years": 7},
    "fidelity msci world acc": {"name": "Fidelity Index World P EUR Acc", "category": "Renta Variable Global (MSCI World)", "ter": 0.12, "aum": 2100, "tracking_error": 0.05, "age_years": 6}
}

ETF_DB = {
    "vwce.de": {"name": "Vanguard FTSE All-World UCITS ETF (Acc)", "ticker": "VWCE.DE", "category": "Renta Variable Global", "ter": 0.22, "aum": 12500, "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 6},
    "spyl.de": {"name": "SPDR S&P 500 UCITS ETF (Acc)", "ticker": "SPYL.DE", "category": "Renta Variable EE.UU.", "ter": 0.03, "aum": 8200, "replication": "Física (Completa)", "te": 0.02, "currency": "EUR", "age_years": 3},
    "eunl.de": {"name": "iShares Core MSCI World UCITS ETF USD (Acc)", "ticker": "EUNL.DE", "category": "Renta Variable Global", "ter": 0.20, "aum": 65000, "replication": "Física (Muestreo)", "te": 0.05, "currency": "EUR", "age_years": 14},
    "eem.mi": {"name": "iShares Core MSCI EM IMI UCITS ETF", "ticker": "EEM.MI", "category": "Renta Variable Emergente", "ter": 0.18, "aum": 15000, "replication": "Física (Completa)", "te": 0.08, "currency": "EUR", "age_years": 12},
    "iglo.de": {"name": "iShares € Corp Bond UCITS ETF", "ticker": "IEAC.DE", "category": "Renta Fija Corporativa", "ter": 0.20, "aum": 14000, "replication": "Física (Muestreo)", "te": 0.03, "currency": "EUR", "age_years": 15}
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
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏆 Ver Ranking de ETFs por Menor TER", use_container_width=True, type="primary"):
                st.session_state.sub_type = "Ranking ETFs"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c2:
            if st.button("🔍 Evaluar un ETF por Ticker", use_container_width=True):
                st.session_state.sub_type = "Evaluación ETF"
                st.session_state.stage = "analyzer"
                st.rerun()

# ----------------------------------------------------
# ETAPA 2: ANALIZADOR (MOTOR DE EVALUACIÓN)
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
        st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER (gastos corrientes) de la gestora. Recuerda consultar y añadir las comisiones de compraventa, custodia o cambio de divisa que aplique tu bróker.")
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

    else:
        st.title(f"📈 Analizador: {st.session_state.asset_type} ({st.session_state.sub_type})")

        if st.session_state.asset_type == "Acciones":
            user_input = st.text_input("Nombre de empresa o Ticker", value="", placeholder="Escribe el nombre de la acción").strip()
        elif st.session_state.asset_type == "Fondos indexados":
            fund_options = ["-- Selecciona o escribe un fondo --"] + [data["name"] for data in FUND_DB.values()]
            selected_fund_option = st.selectbox("🔍 Buscador predictivo de Fondos Indexados", options=fund_options)
            user_input = "" if selected_fund_option == "-- Selecciona o escribe un fondo --" else selected_fund_option
        elif st.session_state.asset_type == "ETFs":
            etf_options = ["-- Selecciona un ETF --"] + [f"{data['name']} ({data['ticker']})" for data in ETF_DB.values()]
            selected_etf_option = st.selectbox("🌐 Selecciona un ETF de referencia", options=etf_options)
            user_input = "" if selected_etf_option == "-- Selecciona un ETF --" else selected_etf_option.split("(")[-1].replace(")", "").strip()

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

                    net_income_m = ((info.get('netIncomeToCommon') or 0) / 1e6)
                    ebitda_m = ((info.get('ebitda') or 0) / 1e6)

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
                    verdict_text = "COMPRAR / ATRACTIVO" if total_score >= 4.0 else ("MANTENER" if total_score >= 3.0 else "DESCARTAR")

                    st.subheader(f"📊 Informe: {name} ({ticker_input})")
                    st.markdown(f"""
                    <div class="score-container">
                        <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg}deg; --progress-color: {progress_color};"><div class="progress-value">{total_score:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio Actual</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error al procesar los datos: {e}")

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
                verdict_fund = "FONDO ALTAMENTE RECOMENDABLE" if score_fund >= 4.0 else "FONDO ADECUADO"

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
                st.info("⚠️ **Aviso de Comisiones:** El TER indicado corresponde exclusivamente a los gastos corrientes de la gestora. No olvides añadir las posibles comisiones de custodia o intermediación de tu bróker habitual.")

            # ----------------------------------------------------
            # CASO C: ETFs
            # ----------------------------------------------------
            elif st.session_state.asset_type == "ETFs":
                matched_etf = ETF_DB.get(user_input.lower())
                
                if matched_etf:
                    etf_name = matched_etf["name"]
                    etf_ticker = matched_etf["ticker"]
                    ter_etf = matched_etf["ter"]
                    aum_etf = matched_etf["aum"]
                    repl_etf = matched_etf["replication"]
                    te_etf = matched_etf["te"]
                    curr_etf = matched_etf["currency"]
                    age_etf = matched_etf["age_years"]
                else:
                    etf_name = user_input.upper()
                    etf_ticker = user_input.upper()
                    ter_etf = 0.20
                    aum_etf = 1000
                    repl_etf = "Física (Completa)"
                    te_etf = 0.05
                    curr_etf = "EUR"
                    age_etf = 5

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
                score_etf += (1.0 if ter_etf <= 0.15 else (0.5 if ter_etf <= 0.45 else 0.0))
                score_etf += (1.0 if aum_etf > 1000 else (0.5 if aum_etf >= 200 else 0.0))
                score_etf += (1.0 if "Física" in repl_etf and te_etf <= 0.05 else (0.5 if te_etf <= 0.20 else 0.0))
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
                    "Métrica del ETF": ["TER (Gastos Anuales)", "Patrimonio (AUM)", "Tipo de Réplica", "Tracking Error", "Divisa de Cotización", "Antigüedad"],
                    "Valor Actual": [f"{ter_etf:.2f}% anual", f"{aum_etf:,.0f} M€", repl_etf, f"{te_etf:.2f}%", curr_etf, f"{age_etf} años"]
                }
                st.table(pd.DataFrame(df_etf_data))
                st.info("⚠️ **Aviso de Comisiones:** El TER indicado corresponde exclusivamente a los gastos corrientes de la gestora. No olvides tener en cuenta las comisiones de compraventa de tu bróker y posibles diferenciales de cambio de divisa (spreads).")

                st.markdown("### 📝 Perspectiva Analítica y Veredicto")
                if score_etf >= 4.0:
                    st.success(f"🟢 **VEREDICTO: {verdict_etf}**\n\n*Justificación:* Excelente combinación de costes reducidos, alta liquidez en mercado y réplica física directa.")
                elif score_etf >= 3.0:
                    st.warning(f"🟡 **VEREDICTO: {verdict_etf}**\n\n*Justificación:* ETF sólido para operativa bursátil, aunque con ligera penalización en costes o tamaño.")
                else:
                    st.error(f"🔴 **VEREDICTO: {verdict_etf}**\n\n*Justificación:* Los costes o las características estructurales del ETF no cumplen con los estándares óptimos.")
