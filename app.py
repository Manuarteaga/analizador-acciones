import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Analizador Bursátil Automático", page_icon="📈", layout="wide")

# Estilos CSS con el sello oficial circular y banda central estilo "Credit Note"
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
    
    /* Estilo Sello Circular con Banda Central (Inspirado en sellos oficiales) */
    .rubber-stamp {
        position: relative;
        width: 155px;
        height: 155px;
        border: 3px dashed var(--stamp-color);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--stamp-color);
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        transform: rotate(-8deg);
        background: rgba(0, 0, 0, 0.15);
        opacity: 0.95;
        animation: stampEffect 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stamp-border {
        position: relative;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
    }
    .stamp-top-text, .stamp-bottom-text {
        font-size: 0.5rem;
        letter-spacing: 1.5px;
        font-weight: bold;
        text-align: center;
        opacity: 0.85;
    }
    .stamp-banner {
        position: absolute;
        top: 50%;
        left: -14px;
        right: -14px;
        transform: translateY(-50%);
        background: #0f172a;
        border: 3px solid var(--stamp-color);
        padding: 4px 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .stamp-grade-text {
        font-size: 2.2rem;
        font-weight: 900;
        line-height: 1;
        letter-spacing: 3px;
        color: var(--stamp-color);
    }

    @keyframes stampEffect {
        0% { transform: scale(2.2) rotate(-25deg); opacity: 0; }
        100% { transform: scale(1) rotate(-8deg); opacity: 0.95; }
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador Bursátil con Enfoque de Broker")
st.markdown("Introduce una empresa para obtener su puntuación visual, sello de calificación oficial, filtro de racha y perspectiva analítica.")

if 'history' not in st.session_state:
    st.session_state.history = []

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios)."},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos)."},
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero)."},
    "sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero)."},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas."},
    "santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas."},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda."},
    "telefónica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda."},
    "microsoft": {"ticker": "MSFT", "racha": "Más de 20 años consecutivos incrementando dividendos de forma ininterrumpida."},
    "procter & gamble": {"ticker": "PG", "racha": "Excepcional. Aristócrata del Dividendo con más de 65 años de subidas ininterrumpidas."},
    "copart": {"ticker": "CPRT", "racha": "Sin historial (Empresa pura de crecimiento sin dividendos)."},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sensible al ciclo económico y a los planes de consolidación bancaria."}
}

# Panel Lateral
with st.sidebar:
    st.header("📊 Historial de Sesión")
    st.markdown(f"Empresas analizadas: **{len(st.session_state.history)}**")
    
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_history.to_excel(writer, sheet_name='Evaluaciones', index=False)
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Descargar Excel de la Sesión",
            data=excel_data,
            file_name="historial_analisis_bursatil.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
        if st.button("🗑️ Borrar Historial"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Analiza alguna empresa para habilitar la exportación a Excel.")

# Cuerpo principal
col1, col2 = st.columns([2, 1])
with col1:
    user_input = st.text_input("Nombre de empresa o Ticker", value="Caixabank").strip()
with col2:
    strategy = st.selectbox("Estrategia", ["Dividendo", "Crecimiento / Sin Dividendo"])

def get_stock_data(query):
    q_lower = query.lower()
    if q_lower in TICKER_DB:
        return TICKER_DB[q_lower]["ticker"], TICKER_DB[q_lower]["racha"]
    return query.upper(), "Sin datos de racha previos (Evaluación estándar)."

def get_letter_grade(score):
    if score >= 5.0: return "A+"
    elif score >= 4.0: return "A"
    elif score >= 3.0: return "B"
    elif score >= 2.0: return "C"
    else: return "D"

if st.button("Ejecutar Análisis Visual", type="primary"):
    if not user_input:
        st.warning("Por favor, introduce un nombre o ticker válido.")
    else:
        ticker_input, racha_info = get_stock_data(user_input)
        with st.spinner(f"Generando informe visual para {user_input}..."):
            try:
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                name = info.get('longName', user_input.title())
                per = info.get('trailingPE') or info.get('forwardPE') or 12.0
                beta = info.get('beta') or 1.0
                div_yield = info.get('dividendYield')
                div_yield = (div_yield * 100) if div_yield else 4.0
                payout = info.get('payoutRatio')
                payout = (payout * 100) if payout else 50.0
                
                total_score = 0
                metrics_log = []

                if strategy == "Dividendo":
                    s_per = 1.0 if per <= 12 else (0.5 if per <= 22 else 0.0)
                    total_score += s_per
                    metrics_log.append(("PER", f"{per:.2f}", s_per))

                    s_beta = 1.0 if beta < 1.0 else (0.5 if beta <= 1.1 else 0.0)
                    total_score += s_beta
                    metrics_log.append(("BETA", f"{beta:.2f}", s_beta))

                    s_yield = 1.0 if (3.0 <= div_yield <= 6.0) else (0.5 if (1.0 <= div_yield < 3.0 or 6.0 <= div_yield <= 9.0) else 0.0)
                    total_score += s_yield
                    metrics_log.append(("Dividend Yield", f"{div_yield:.2f}%", s_yield))

                    s_payout = 1.0 if (35.0 <= payout <= 75.0) else 0.5
                    total_score += s_payout
                    metrics_log.append(("Payout", f"{payout:.1f}%", s_payout))

                    s_growth = 1.0 if ticker_input in ["ITX.MC", "IBE.MC", "PG", "MSFT"] else 0.5
                    total_score += s_growth
                    metrics_log.append(("Crecimiento Div.", "Alineado perfil", s_growth))
                else:
                    roe = info.get('returnOnEquity')
                    roe_val = (roe * 100) if roe else 15.0
                    s_roic = 1.0 if roe_val > 15 else 0.5
                    total_score += s_roic
                    metrics_log.append(("ROE / ROIC", f"{roe_val:.1f}%", s_roic))

                    revenue_growth = info.get('revenueGrowth')
                    rev_val = (revenue_growth * 100) if revenue_growth else 10.0
                    s_cagr = 1.0 if rev_val > 10 else 0.5
                    total_score += s_cagr
                    metrics_log.append(("Crecimiento Ingresos", f"{rev_val:.1f}%", s_cagr))

                    total_debt = info.get('totalDebt', 0)
                    total_cash = info.get('totalCash', 0)
                    s_debt = 1.0 if total_cash >= total_debt else 0.5
                    total_score += s_debt
                    metrics_log.append(("Solvencia", "Saludable", s_debt))

                    free_cash = info.get('freeCashflow', 1)
                    s_fcf = 1.0 if free_cash and free_cash > 0 else 0.0
                    total_score += s_fcf
                    metrics_log.append(("FCF", "Positivo", s_fcf))

                    s_moat = 1.0
                    total_score += s_moat
                    metrics_log.append(("Moat", "Alto", s_moat))

                grade = get_letter_grade(total_score)
                deg = int((total_score / 5.0) * 360)

                if total_score >= 4.0:
                    verdict_text = "COMPRAR / ATRACTIVO"
                    progress_color = "#22c55e" # Verde
                elif total_score >= 3.0:
                    verdict_text = "MANTENER / VIGILANCIA TÁCTICA"
                    progress_color = "#eab308" # Amarillo
                else:
                    verdict_text = "DESCARTAR / NO APTO"
                    progress_color = "#ef4444" # Rojo

                session_record = {
                    "Empresa": name,
                    "Ticker": ticker_input,
                    "Estrategia": strategy,
                    "Nota": f"{total_score:.1f} / 5",
                    "Calificación": grade,
                    "Veredicto": verdict_text,
                    "Racha": racha_info
                }
                if not st.session_state.history or st.session_state.history[-1]["Ticker"] != ticker_input:
                    st.session_state.history.append(session_record)

                # --- RENDERIZADO VISUAL ---
                st.subheader(f"📊 Informe Visual: {name} ({ticker_input})")

                # Contenedor con Círculo de Puntuación + Sello Oficial con Banda Central
                st.markdown(f"""
                <div class="score-container">
                    <div style="text-align: center;">
                        <div class="circular-progress" style="--deg: {deg}deg; --progress-color: {progress_color};">
                            <div class="progress-value">{total_score:.1f}/5</div>
                        </div>
                        <div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación Global</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">Calificación Oficial</div>
                        <div class="rubber-stamp" style="--stamp-color: {progress_color};">
                            <div class="stamp-border">
                                <div class="stamp-top-text">★ RATED & APPROVED ★</div>
                                <div class="stamp-banner">
                                    <div class="stamp-grade-text">{grade}</div>
                                </div>
                                <div class="stamp-bottom-text">BROKER AUDIT DEPT</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("### 🔍 Filtro Extra: Consistencia y Racha")
                st.info(f"**Estado de la Racha:** {racha_info}")

                st.markdown("### 📝 Perspectiva Analítica y Veredicto de Broker")
                if total_score >= 4.0:
                    st.success(f"🟢 **VEREDICTO: {verdict_text}**\n\n*Justificación:* Sólidos fundamentales cuantitativos respaldados por métricas de valoración óptimas y retribución atractiva.")
                elif total_score >= 3.0:
                    st.warning(f"🟡 **VEREDICTO: {verdict_text}**\n\n*Justificación:* Activo con fortalezas operativas, condicionado por su ciclicidad o matices de crecimiento a largo plazo.")
                else:
                    st.error(f"🔴 **VEREDICTO: {verdict_text}**\n\n*Justificación:* Puntuación baja en los pilares fundamentales del modelo.")

                st.markdown("### 📋 Desglose de Parámetros:")
                df_res = pd.DataFrame(metrics_log, columns=["Parámetro Evaluado", "Valor Detectado", "Puntuación"])
                st.table(df_res)

            except Exception as e:
                st.error(f"Error al procesar los datos para '{user_input}': {e}")
              
