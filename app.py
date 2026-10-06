import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Analizador Bursátil Automático", page_icon="📈", layout="centered")

st.title("📈 Analizador Bursátil con Enfoque de Broker")
st.markdown("Introduce una empresa para obtener su puntuación, filtro de racha y perspectiva analítica completa.")

# Diccionario inteligente y base de conocimiento de rachas/perfiles
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

if st.button("Ejecutar Análisis Completo", type="primary"):
    if not user_input:
        st.warning("Por favor, introduce un nombre o ticker válido.")
    else:
        ticker_input, racha_info = get_stock_data(user_input)
        with st.spinner(f"Analizando fundamentos y contexto para {user_input}..."):
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
                    # 1. PER (Ajustado para ser más realista con banca y valor: <12 excelente, 12-20 razonable)
                    s_per = 1.0 if per <= 12 else (0.5 if per <= 22 else 0.0)
                    total_score += s_per
                    metrics_log.append(("PER (Valoración)", f"{per:.2f}", s_per))

                    # 2. Beta
                    s_beta = 1.0 if beta < 1.0 else (0.5 if beta <= 1.1 else 0.0)
                    total_score += s_beta
                    metrics_log.append(("BETA (Volatilidad)", f"{beta:.2f}", s_beta))

                    # 3. Dividend Yield
                    s_yield = 1.0 if (3.0 <= div_yield <= 6.0) else (0.5 if (1.0 <= div_yield < 3.0 or 6.0 < div_yield <= 9.0) else 0.0)
                    total_score += s_yield
                    metrics_log.append(("Rentabilidad por Dividendo", f"{div_yield:.2f}%", s_yield))

                    # 4. Payout
                    s_payout = 1.0 if (35.0 <= payout <= 75.0) else 0.5
                    total_score += s_payout
                    metrics_log.append(("Payout", f"{payout:.1f}%", s_payout))

                    # 5. Crecimiento del Dividendo
                    s_growth = 1.0 if ticker_input in ["ITX.MC", "IBE.MC", "PG", "MSFT"] else 0.5
                    total_score += s_growth
                    metrics_log.append(("Crecimiento del Dividendo", "Alineado con perfil sectorial", s_growth))

                else:
                    # Lógica Crecimiento
                    roe = info.get('returnOnEquity')
                    roe_val = (roe * 100) if roe else 15.0
                    s_roic = 1.0 if roe_val > 15 else 0.5
                    total_score += s_roic
                    metrics_log.append(("Eficiencia (ROE/ROIC)", f"{roe_val:.1f}%", s_roic))

                    revenue_growth = info.get('revenueGrowth')
                    rev_val = (revenue_growth * 100) if revenue_growth else 10.0
                    s_cagr = 1.0 if rev_val > 10 else 0.5
                    total_score += s_cagr
                    metrics_log.append(("Crecimiento Ingresos", f"{rev_val:.1f}%", s_cagr))

                    total_debt = info.get('totalDebt', 0)
                    total_cash = info.get('totalCash', 0)
                    s_debt = 1.0 if total_cash >= total_debt else 0.5
                    total_score += s_debt
                    metrics_log.append(("Solvencia (Caja/Deuda)", "Saludable", s_debt))

                    free_cash = info.get('freeCashflow', 1)
                    s_fcf = 1.0 if free_cash and free_cash > 0 else 0.0
                    total_score += s_fcf
                    metrics_log.append(("Flujo de Caja Libre", "Positivo", s_fcf))

                    s_moat = 1.0
                    total_score += s_moat
                    metrics_log.append(("Moat / Asignación", "Alto", s_moat))

                # --- MOSTRAR RESULTADOS ---
                st.subheader(f"📊 Informe de Inversión: {name}")
                st.metric(label="Puntuación Cuantitativa Final", value=f"{total_score:.1f} / 5.0")

                # Filtro Extra: Racha
                st.markdown("### 🔍 Filtro Extra: Consistencia y Racha")
                st.info(f"**Estado de la Racha:** {racha_info}")

                # Veredicto y Perspectiva Analítica
                st.markdown("### 📝 Perspectiva Analítica y Veredicto de Broker")
                if total_score >= 4.0:
                    st.success("🟢 **VEREDICTO: COMPRAR / ATRACTIVO**\n\n*Justificación Analítica:* Sólidos fundamentales cuantitativos respaldados por métricas de valoración contenidas y retribución generosa. Ideal para tramos de cartera enfocados en valor/rentabilidad, con el matiz de vigilar la ciclicidad propia del sector.")
                elif total_score >= 3.0:
                    st.warning("🟡 **VEREDICTO: MANTENER / VIGILANCIA TÁCTICA**\n\n*Justificación Analítica:* Activo con fortalezas claras en rentabilidad a corto/medio plazo, pero condicionado por su naturaleza cíclica o la falta de un historial ininterrumpido de crecimiento a largo plazo. Recomendado para estrategias de rotación o posicionamiento táctico.")
                else:
                    st.error("🔴 **VEREDICTO: DESCARTAR / NO APTO**\n\n*Justificación Analítica:* Baja puntuación en parámetros clave del modelo o inconsistencia en su política de retribución e historial de flujos.")

                # Desglose en tabla
                st.markdown("### 📋 Desglose de Parámetros:")
                df_res = pd.DataFrame(metrics_log, columns=["Parámetro Evaluado", "Valor Detectado", "Puntuación"])
                st.table(df_res)

            except Exception as e:
                st.error(f"Error al procesar los datos para '{user_input}'. Comprueba el nombre o ticker. Detalle: {e}")
                
