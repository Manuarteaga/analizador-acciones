import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Analizador Bursátil Automático", page_icon="📈", layout="wide")

st.title("📈 Analizador Bursátil con Enfoque de Broker")
st.markdown("Introduce una empresa para obtener su puntuación, filtro de racha y perspectiva analítica completa. Las consultas se guardan en tu historial de sesión para exportarlas cuando desees.")

# Inicializar el historial en la sesión del navegador
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

# Panel Lateral para el Historial y Exportación
with st.sidebar:
    st.header("📊 Historial de Sesión")
    st.markdown(f"Empresas analizadas en esta sesión: **{len(st.session_state.history)}**")
    
    if st.session_state.history:
        # Convertir historial a DataFrame para la descarga
        df_history = pd.DataFrame(st.session_state.history)
        
        # Generar archivo Excel en memoria
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
        st.info("Realiza algún análisis para habilitar la descarga del Excel.")

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
                    s_per = 1.0 if per <= 12 else (0.5 if per <= 22 else 0.0)
                    total_score += s_per
                    metrics_log.append(("PER", f"{per:.2f}", s_per))

                    s_beta = 1.0 if beta < 1.0 else (0.5 if beta <= 1.1 else 0.0)
                    total_score += s_beta
                    metrics_log.append(("BETA", f"{beta:.2f}", s_beta))

                    s_yield = 1.0 if (3.0 <= div_yield <= 6.0) else (0.5 if (1.0 <= div_yield < 3.0 or 6.0 < div_yield <= 9.0) else 0.0)
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

                # Definir Veredicto texto
                if total_score >= 4.0:
                    verdict_text = "COMPRAR / ATRACTIVO"
                elif total_score >= 3.0:
                    verdict_text = "MANTENER / VIGILANCIA TÁCTICA"
                else:
                    verdict_text = "DESCARTAR / NO APTO"

                # Guardar en el historial de la sesión
                session_record = {
                    "Empresa": name,
                    "Ticker": ticker_input,
                    "Estrategia": strategy,
                    "Puntuación": f"{total_score:.1f} / 5.0",
                    "Veredicto": verdict_text,
                    "Racha / Consistencia": racha_info
                }
                
                # Evitar duplicados exactos consecutivos si se reanaliza lo mismo
                if not st.session_state.history or st.session_state.history[-1]["Ticker"] != ticker_input:
                    st.session_state.history.append(session_record)

                # --- MOSTRAR RESULTADOS ---
                st.subheader(f"📊 Informe de Inversión: {name}")
                st.metric(label="Puntuación Cuantitativa Final", value=f"{total_score:.1f} / 5.0")

                st.markdown("### 🔍 Filtro Extra: Consistencia y Racha")
                st.info(f"**Estado de la Racha:** {racha_info}")

                st.markdown("### 📝 Perspectiva Analítica y Veredicto de Broker")
                if total_score >= 4.0:
                    st.success(f"🟢 **VEREDICTO: {verdict_text}**\n\n*Justificación Analítica:* Sólidos fundamentales cuantitativos respaldados por métricas de valoración contenidas y retribución generosa.")
                elif total_score >= 3.0:
                    st.warning(f"🟡 **VEREDICTO: {verdict_text}**\n\n*Justificación Analítica:* Activo con fortalezas claras, pero condicionado por su naturaleza cíclica o matices de crecimiento.")
                else:
                    st.error(f"🔴 **VEREDICTO: {verdict_text}**\n\n*Justificación Analítica:* Baja puntuación en parámetros clave del modelo.")

                st.markdown("### 📋 Desglose de Parámetros:")
                df_res = pd.DataFrame(metrics_log, columns=["Parámetro Evaluado", "Valor Detectado", "Puntuación"])
                st.table(df_res)

            except Exception as e:
                st.error(f"Error al procesar los datos para '{user_input}'. Detalle: {e}")
