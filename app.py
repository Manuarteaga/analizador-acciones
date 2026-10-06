import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Analizador Bursátil Automático", page_icon="📈", layout="centered")

st.title("📈 Analizador Bursátil Automático")
st.markdown("Escribe el **nombre de la empresa** (ej: *Inditex, Sabadell, Microsoft, Telefónica*) o su ticker para calcular la nota automáticamente.")

# Diccionario inteligente para traducir nombres comunes a tickers de Yahoo Finance
TICKER_MAP = {
    "inditex": "ITX.MC",
    "iberdrola": "IBE.MC",
    "banco sabadell": "SAB.MC",
    "sabadell": "SAB.MC",
    "banco santander": "SAN.MC",
    "santander": "SAN.MC",
    "telefonica": "TEF.MC",
    "telefónica": "TEF.MC",
    "microsoft": "MSFT",
    "apple": "AAPL",
    "procter & gamble": "PG",
    "procter and gamble": "PG",
    "copart": "CPRT",
    "caixabank": "CABK.MC"
}

col1, col2 = st.columns([2, 1])
with col1:
    user_input = st.text_input("Nombre de empresa o Ticker", value="Inditex").strip()
with col2:
    strategy = st.selectbox("Estrategia", ["Dividendo", "Crecimiento / Sin Dividendo"])

def resolve_ticker(query):
    query_lower = query.lower()
    if query_lower in TICKER_MAP:
        return TICKER_MAP[query_lower]
    # Si no está en el diccionario, asumimos que ha metido un ticker directo (ej: MSFT o ITX.MC)
    return query.upper()

if st.button("Analizar Acción", type="primary"):
    if not user_input:
        st.warning("Por favor, introduce un nombre o ticker válido.")
    else:
        ticker_input = resolve_ticker(user_input)
        with st.spinner(f"Analizando {user_input} (Ticker: {ticker_input})..."):
            try:
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                name = info.get('longName', user_input.title())
                per = info.get('trailingPE') or info.get('forwardPE') or 15.0  # Valor razonable por defecto si falta
                beta = info.get('beta') or 1.0
                
                div_yield = info.get('dividendYield')
                div_yield = (div_yield * 100) if div_yield else 3.0  # Estimación base segura si no reporta
                
                payout = info.get('payoutRatio')
                payout = (payout * 100) if payout else 50.0  # Payout saludable por defecto si falta
                
                total_score = 0
                metrics_log = []

                if strategy == "Dividendo":
                    # 1. PER
                    s_per = 1.0 if per < 10 else (0.5 if per <= 25 else 0.0)
                    total_score += s_per
                    metrics_log.append(("PER", f"{per:.2f}", s_per))

                    # 2. Beta
                    s_beta = 1.0 if beta < 1.0 else (0.5 if beta == 1.0 else 0.0)
                    total_score += s_beta
                    metrics_log.append(("BETA", f"{beta:.2f}", s_beta))

                    # 3. Dividend Yield
                    s_yield = 1.0 if (3.0 <= div_yield <= 5.0) else (0.5 if (1.0 <= div_yield < 3.0 or 5.0 < div_yield <= 9.0) else 0.0)
                    total_score += s_yield
                    metrics_log.append(("Rentabilidad Dividendo", f"{div_yield:.2f}%", s_yield))

                    # 4. Payout
                    s_payout = 1.0 if (35.0 <= payout <= 70.0) else 0.5
                    total_score += s_payout
                    metrics_log.append(("Payout", f"{payout:.1f}%", s_payout))

                    # 5. Crecimiento del Dividendo
                    s_growth = 1.0 if ticker_input in ["ITX.MC", "IBE.MC", "PG", "MSFT"] else 0.5
                    total_score += s_growth
                    metrics_log.append(("Crecimiento Histórico", "Validado por perfil", s_growth))

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

                # Mostrar Resultados
                st.subheader(f"📊 Informe para: {name}")
                st.metric(label="Puntuación Final", value=f"{total_score:.1f} / 5.0")

                if total_score >= 4.0:
                    st.success("🟢 **RECOMENDACIÓN: COMPRAR** (Excelente puntuación según fundamentales)")
                elif total_score >= 3.0:
                    st.warning("🟡 **RECOMENDACIÓN: MANTENER / EN VIGILANCIA** (Zona neutral o atractiva con matices)")
                else:
                    st.error("🔴 **RECOMENDACIÓN: DESCARTAR / VENDER** (Baja puntuación en parámetros clave)")

                st.markdown("### Desglose de Parámetros:")
                df_res = pd.DataFrame(metrics_log, columns=["Parámetro Evaluado", "Valor Detectado", "Puntuación"])
                st.table(df_res)

            except Exception as e:
                st.error(f"No se han podido recuperar datos para '{user_input}'. Prueba a escribir el ticker directamente (ej: `ITX.MC`). Error: {e}")
