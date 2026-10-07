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

# Base de datos ampliada de fondos indexados con información de categoría y TER
FUND_DB = {
    "vanguard global stock": {"name": "Vanguard Global Stock Index Fund EUR Acc", "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 4500, "tracking_error": 0.08, "age_years": 8},
    "vanguard s&p 500": {"name": "Vanguard S&P 500 UCITS ETF (Acc)", "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.07, "aum": 35000, "tracking_error": 0.03, "age_years": 12},
    "amundi msci world": {"name": "Amundi Index MSCI World AE-C", "category": "Renta Variable Global (MSCI World)", "ter": 0.30, "aum": 3200, "tracking_error": 0.12, "age_years": 7},
    "ishares developed world": {"name": "iShares Developed World Index Fund", "category": "Renta Variable Global Desarrollada", "ter": 0.22, "aum": 2800, "tracking_error": 0.10, "age_years": 6},
    "amundi index msci emerging markets": {"name": "Amundi Index MSCI Emerging Markets AE-C", "category": "Renta Variable Emergente", "ter": 0.45, "aum": 1800, "tracking_error": 0.15, "age_years": 8},
    "fidelity msci world": {"name": "Fidelity Index World P EUR Acc", "category": "Renta Variable Global (MSCI World)", "ter": 0.12, "aum": 2100, "tracking_error": 0.05, "age_years": 6},
    "allianz european equity div": {"name": "Allianz European Equity Div AT EUR", "category": "Renta Variable Europa (Dividendos)", "ter": 0.75, "aum": 850, "tracking_error": 0.25, "age_years": 10}
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
            if st.button("✍️ Evaluar un Fondo por Nombre / ISIN", use_container_width=True):
                st.session_state.sub_type = "Acumulación" # Por defecto acumulación
                st.session_state.stage = "analyzer"
                st.rerun()

    elif st.session_state.asset_type == "ETFs":
        st.markdown("### Selecciona la categoría del ETF:")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("Renta variable", use_container_width=True):
                st.session_state.sub_type = "Renta variable"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c2:
            if st.button("Fija", use_container_width=True):
                st.session_state.sub_type = "Fija"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c3:
            if st.button("Materias primas", use_container_width=True):
                st.session_state.sub_type = "Materias primas"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c4:
            if st.button("Sectoriales", use_container_width=True):
                st.session_state.sub_type = "Sectoriales"
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

    # Si el usuario seleccionó ver el ranking de fondos
    if st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
        st.title("🏆 Ranking de Fondos Indexados (Ordenados por menor TER / Comisiones)")
        st.markdown("Aquí tienes una selección de los fondos indexados más populares del mercado ordenados de **menor a mayor coste anual (TER)** para ayudarte a elegir los más eficientes:")

        # Crear DataFrame ordenado por TER ascendente
        ranking_data = []
        for key, data in FUND_DB.items():
            ranking_data.append({
                "Fondo": data["name"],
                "Categoría": data["category"],
                "TER Anual (%)": data["ter"],
                "Patrimonio (M€)": data["aum"],
                "Antigüedad (Años)": data["age_years"]
            })
        
        df_ranking = pd.DataFrame(ranking_data)
        df_ranking = df_ranking.sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True)
        
        # Mostrar tabla estilizada
        st.dataframe(df_ranking, use_container_width=True)

        st.info("💡 **Consejo:** Los fondos con un TER inferior al 0.20% (como los de Fidelity o Vanguard) son extremadamente eficientes para carteras a largo plazo.")

        if st.button("← Volver al menú de fondos"):
            st.session_state.sub_type = None
            st.rerun()

    else:
        st.title(f"📈 Analizador: {st.session_state.asset_type} ({st.session_state.sub_type})")

        if st.session_state.asset_type == "Acciones":
            user_input = st.text_input("Nombre de empresa o Ticker", value="", placeholder="Escribe el nombre de la acción").strip()
        elif st.session_state.asset_type == "Fondos indexados":
            user_input = st.text_input("Nombre del fondo o ISIN", value="", placeholder="Ej. Vanguard Global Stock o Fidelity World").strip()
        else:
            user_input = st.text_input("Nombre del ETF o Ticker", value="", placeholder="Escribe el ETF").strip()

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
            st.info("👆 Introduce el nombre del activo, fondo o su código en el cuadro superior para comenzar el análisis.")
        else:
            # ----------------------------------------------------
            # CASO A: EVALUACIÓN DE ACCIONES
            # ----------------------------------------------------
            if st.session_state.asset_type == "Acciones":
                stock_result = get_stock_data(user_input)
                if isinstance(stock_result, tuple) and len(stock_result) == 4:
                    ticker_input, racha_info, est_div_growth, db_div_yield = stock_result
                else:
                    ticker_input, racha_info, est_div_growth, db_div_yield = user_input.upper(), "Sin datos", 3.0, None
                
                try:
                    stock = yf.Ticker(ticker_input)
                    
                    hist_price = stock.history(period="5d")
                    current_price = None
                    if not hist_price.empty:
                        current_price = hist_price['Close'].iloc[-1]

                    try:
                        info = stock.info
                    except:
                        info = {}

                    name = info.get('longName', user_input.title())
                    
                    currency_symbol = info.get('currency', '€')
                    if currency_symbol == 'USD':
                        currency_symbol = '$'
                    elif currency_symbol == 'EUR':
                        currency_symbol = '€'

                    price_display = f"{current_price:,.2f} {currency_symbol}" if current_price is not None else "—"

                    per_y = info.get('trailingPE') or info.get('forwardPE') or 20.0
                    pfcf_y = info.get('priceToFreeCashflow') or 18.0
                    pb_y = info.get('priceToBook') or 3.0
                    roe_y = info.get('returnOnEquity')
                    roe_val = (roe_y * 100) if roe_y else 15.0
                    
                    div_y = info.get('dividendYield')
                    div_y_val = (div_y * 100 if div_y < 1.0 else div_y) if div_y else (db_div_yield or 0.0)
                    
                    bpa_y = info.get('trailingEps') or 2.0
                    beta_val = info.get('beta') or 1.0
                    payout_val = info.get('payoutRatio')
                    payout_val = (payout_val * 100) if payout_val else 50.0

                    net_income_y = info.get('netIncomeToCommon') or info.get('netIncome')
                    if not net_income_y:
                        try:
                            fin = stock.financials
                            if not fin.empty:
                                for row_name in ['Net Income', 'Net Income Common Stockholders', 'Net Income From Continuing Operation']:
                                    if row_name in fin.index:
                                        net_income_y = fin.loc[row_name].iloc[0]
                                        break
                        except:
                            pass
                    net_income_m = (net_income_y / 1e6) if net_income_y else 0.0

                    ebitda_y = info.get('ebitda')
                    if not ebitda_y:
                        try:
                            fin = stock.financials
                            if not fin.empty:
                                for row_name in ['EBITDA', 'Normalized EBITDA', 'Operating Income']:
                                    if row_name in fin.index:
                                        ebitda_y = fin.loc[row_name].iloc[0]
                                        break
                        except:
                            pass
                    ebitda_m = (ebitda_y / 1e6) if ebitda_y else 0.0

                    growth_1y = info.get('earningsGrowth')
                    growth_1y_val = f"{(growth_1y * 100):.2f}%" if growth_1y is not None else f"{est_div_growth:.1f}% (est.)"
                    
                    growth_5y = info.get('revenueGrowth')
                    growth_5y_val = f"{(growth_5y * 100):.2f}%" if growth_5y is not None else "N/D"

                    total_score = 0
                    
                    if st.session_state.sub_type == "Con dividendos":
                        total_score += (1.0 if per_y <= 10 else (0.5 if per_y <= 25 else 0.0))
                        total_score += (1.0 if beta_val < 1.0 else (0.5 if beta_val <= 1.1 else 0.0))
                        total_score += (1.0 if (0 <= div_y_val <= 6.0) else (0.5 if (6.0 < div_y_val <= 9.0) else 0.0))
                        total_score += (1.0 if (35.0 <= payout_val <= 75.0) else 0.0)
                        total_score += (1.0 if est_div_growth > 3.0 else (0.5 if est_div_growth == 3.0 else 0.0))
                    else:
                        total_score += (1.0 if per_y <= 25 else (0.5 if per_y <= 40 else 0.0))
                        total_score += (1.0 if pfcf_y <= 20 else (0.5 if pfcf_y <= 35 else 0.0))
                        total_score += (1.0 if pb_y <= 4.0 else (0.5 if pb_y <= 8.0 else 0.0))
                        total_score += (1.0 if roe_val >= 15.0 else (0.5 if roe_val >= 8.0 else 0.0))
                        total_score += (1.0 if bpa_y > 0 else 0.0)

                    grade = get_letter_grade(total_score)
                    deg = int((total_score / 5.0) * 360)

                    if total_score >= 4.0:
                        verdict_text = "COMPRAR / ATRACTIVO"
                        progress_color = "#22c55e"
                    elif total_score >= 3.0:
                        verdict_text = "MANTENER / VIGILANCIA TÁCTICA"
                        progress_color = "#eab308"
                    else:
                        verdict_text = "DESCARTAR / NO APTO"
                        progress_color = "#ef4444"

                    session_record = {
                        "Activo": f"{st.session_state.asset_type} ({st.session_state.sub_type})",
                        "Empresa": name,
                        "Ticker": ticker_input,
                        "Precio": price_display,
                        "Nota": f"{total_score:.1f} / 5",
                        "Calificación": grade,
                        "Veredicto": verdict_text,
                        "Racha": racha_info
                    }
                    if not st.session_state.history or st.session_state.history[-1]["Ticker"] != ticker_input:
                        st.session_state.history.append(session_record)

                    st.subheader(f"📊 Informe: {name} ({ticker_input})")

                    st.markdown(f"""
                    <div class="score-container">
                        <div style="text-align: center;">
                            <div class="circular-progress" style="--deg: {deg}deg; --progress-color: {progress_color};">
                                <div class="progress-value">{total_score:.1f}/5</div>
                            </div>
                            <div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación Óptima</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación Oficial</div>
                            <div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio Actual</div>
                            <div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("### 📋 Tabla de Parámetros Clave")
                    
                    if st.session_state.sub_type == "Sin dividendos":
                        comparison_data = {
                            "Parámetro": [
                                "PER (Precio / Beneficio)", 
                                "P/FCF (Precio / Free Cash Flow)", 
                                "P/B (Precio / Valor Contable)", 
                                "ROE (Rentabilidad sobre Fondos Propios)", 
                                "Beneficio Neto (Millones)", 
                                "EBITDA (Millones)", 
                                "BPA (Beneficio por Acción)",
                                "Previsión Crecimiento (1 Año)",
                                "Previsión Crecimiento (5 Años)"
                            ],
                            "Valor Actual": [
                                f"{per_y:.2f}",
                                f"{pfcf_y:.2f}",
                                f"{pb_y:.2f}",
                                f"{roe_val:.2f}%",
                                f"{net_income_m:,.2f} M {currency_symbol}" if net_income_m != 0 else "N/D",
                                f"{ebitda_m:,.2f} M {currency_symbol}" if ebitda_m != 0 else "N/D",
                                f"{bpa_y:.2f} {currency_symbol}",
                                growth_1y_val,
                                growth_5y_val
                            ]
                        }
                    else:
                        comparison_data = {
                            "Métrica Financiera": [
                                "PER (Precio/Beneficio)", 
                                "Dividend Yield (%)", 
                                "Beta (Volatilidad)", 
                                "Payout Ratio (%)", 
                                "Crecimiento Div. vs Inflación",
                                "Previsión Crecimiento (1 Año)",
                                "Previsión Crecimiento (5 Años)"
                            ],
                            "Valor Seleccionado": [
                                f"{per_y:.2f}", 
                                f"{div_y_val:.2f}%", 
                                f"{beta_val:.2f}", 
                                f"{payout_val:.1f}%", 
                                f"{est_div_growth:.1f}% anual",
                                growth_1y_val,
                                growth_5y_val
                            ]
                        }
                        
                    df_comparison = pd.DataFrame(comparison_data)
                    st.table(df_comparison)

                    st.markdown("### 🔍 Filtro Extra: Consistencia y Racha")
                    st.info(f"**Estado de la Racha:** {racha_info}")

                    st.markdown("### 📝 Perspectiva Analítica y Veredicto")
                    if total_score >= 4.0:
                        st.success(f"🟢 **VEREDICTO: {verdict_text}**\n\n*Justificación:* Excelentes métricas fundamentales en los indicadores clave seleccionados.")
                    elif total_score >= 3.0:
                        st.warning(f"🟡 **VEREDICTO: {verdict_text}**\n\n*Justificación:* Parámetros mixtos; se aconseja vigilancia táctica.")
                    else:
                        st.error(f"🔴 **VEREDICTO: {verdict_text}**\n\n*Justificación:* El perfil fundamental no cumple con los umbrales mínimos establecidos.")

                except Exception as e:
                    st.error(f"Error al procesar los datos para '{user_input}': {e}")

            # ----------------------------------------------------
            # CASO B: EVALUACIÓN DE FONDOS INDEXADOS
            # ----------------------------------------------------
            elif st.session_state.asset_type == "Fondos indexados":
                q_lower = user_input.lower().strip()
                
                if q_lower in FUND_DB:
                    f_data = FUND_DB[q_lower]
                    fund_name = f_data["name"]
                    ter_val = f_data["ter"]
                    aum_val = f_data["aum"]
                    te_val = f_data["tracking_error"]
                    age_val = f_data["age_years"]
                else:
                    fund_name = user_input.title()
                    ter_val = 0.20
                    aum_val = 1500
                    te_val = 0.09
                    age_val = 6

                score_fund = 0
                score_fund += (1.0 if ter_val <= 0.20 else (0.5 if ter_val <= 0.50 else 0.0))
                score_fund += (1.0 if aum_val > 500 else (0.5 if aum_val >= 100 else 0.0))
                score_fund += (1.0 if te_val <= 0.10 else (0.5 if te_val <= 0.30 else 0.0))
                score_fund += (1.0 if st.session_state.sub_type == "Acumulación" else 0.5)
                score_fund += (1.0 if age_val > 5 else (0.5 if age_val >= 3 else 0.0))

                grade_fund = get_letter_grade(score_fund)
                deg_fund = int((score_fund / 5.0) * 360)

                if score_fund >= 4.0:
                    verdict_fund = "FONDO ALTAMENTE RECOMENDABLE / PASIVO ÓPTIMO"
                    color_fund = "#22c55e"
                elif score_fund >= 3.0:
                    verdict_fund = "FONDO ADECUADO / CUMPLE ESTÁNDARES"
                    color_fund = "#eab308"
                else:
                    verdict_fund = "COSTES ELEVADOS / NO RECOMENDADO"
                    color_fund = "#ef4444"

                session_record = {
                    "Activo": f"Fondo Indexado ({st.session_state.sub_type})",
                    "Empresa": fund_name,
                    "Ticker": user_input.upper(),
                    "Precio": "N/D (Aportaciones periódicas)",
                    "Nota": f"{score_fund:.1f} / 5",
                    "Calificación": grade_fund,
                    "Veredicto": verdict_fund,
                    "Racha": f"Antigüedad: {age_val} años"
                }
                if not st.session_state.history or st.session_state.history[-1]["Ticker"] != user_input.upper():
                    st.session_state.history.append(session_record)

                st.subheader(f"📊 Informe de Fondo: {fund_name}")

                st.markdown(f"""
                <div class="score-container">
                    <div style="text-align: center;">
                        <div class="circular-progress" style="--deg: {deg_fund}deg; --progress-color: {color_fund};">
                            <div class="progress-value">{score_fund:.1f}/5</div>
                        </div>
                        <div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación Pasiva</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación Oficial</div>
                        <div class="pure-stamp-grade" style="--stamp-color: {color_fund};">{grade_fund}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Antigüedad / Track Record</div>
                        <div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{age_val} Años</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### 📋 Parámetros Clave de Gestión Pasiva")
                df_fund_data = {
                    "Métrica del Fondo": [
                        "TER (Gastos Corrientes / Comisiones)", 
                        "Patrimonio bajo Gestión (AUM)", 
                        "Tracking Error (Error de Réplica)", 
                        "Política de Reinversión", 
                        "Antigüedad (Track Record)"
                    ],
                    "Valor Actual": [
                        f"{ter_val:.2f}% anual",
                        f"{aum_val:,.0f} M€",
                        f"{te_val:.2f}%",
                        st.session_state.sub_type,
                        f"{age_val} años"
                    ]
                }
                st.table(pd.DataFrame(df_fund_data))

                st.markdown("### 📝 Perspectiva Analítica y Veredicto")
                if score_fund >= 4.0:
                    st.success(f"🟢 **VEREDICTO: {verdict_fund}**\n\n*Justificación:* Excelente estructura de costes reducidos, alta capitalización y réplica muy eficiente.")
                elif score_fund >= 3.0:
                    st.warning(f"🟡 **VEREDICTO: {verdict_fund}**\n\n*Justificación:* Fondo sólido para cartera pasiva, aunque con margen de mejora en comisiones o tamaño.")
                else:
                    st.error(f"🔴 **VEREDICTO: {verdict_fund}**\n\n*Justificación:* Los costes o las características del fondo penalizan su rentabilidad a largo plazo.")

            # ----------------------------------------------------
            # CASO C: EVALUACIÓN DE ETFS
            # ----------------------------------------------------
            else:
                st.info("🌐 Analizador de ETFs configurado. Selecciona un ETF para evaluar sus gastos y liquidez en mercado.")
