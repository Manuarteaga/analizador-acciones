import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Analizador Bursátil Automático", page_icon="📈", layout="centered")

st.title("📈 Analizador Bursátil Automático")
st.markdown("Introduce el **Ticker** de la acción (ej: `ITX.MC`, `MSFT`, `AAPL`, `IBE.MC`) y el sistema descargará los datos en tiempo real para aplicar tu baremo.")

# Entrada de usuario
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Ticker de Yahoo Finance", value="ITX.MC").upper()
with col2:
    strategy = st.selectbox("Estrategia", ["Dividendo", "Crecimiento / Sin Dividendo"])

if st.button("Analizar Acción", type="primary"):
    if not ticker_input:
        st.warning("Por favor, introduce un ticker válido.")
    else:
        with st.spinner(f"Descargando datos y calculando métricas para {ticker_input}..."):
            try:
                stock = yf.Ticker(ticker_input)
                info = stock.info
                
                # Extracción de datos básicos
                name = info.get('longName', ticker_input)
                per = info.get('trailingPE', None)
                if per is None:
                    per = info.get('forwardPE', 0)
                beta = info.get('beta', 1.0)
                if beta is None:
                    beta = 1.0
                
                div_yield = info.get('dividendYield', 0)
                if div_yield is None:
                    div_yield = 0.0
                else:
                    div_yield = div_yield * 100  # pasar a porcentaje
                
                payout = info.get('payoutRatio', 0)
                if payout is None:
                    payout = 0.0
                else:
                    payout = payout * 100
                
                total_score = 0
                metrics_log = []

                if strategy == "Dividendo":
                    # 1. PER
                    if per > 0 and per < 10:
                        s_per = 1.0
                    elif per >= 10 and per <= 25:
                        s_per = 0.5
                    else:
                        s_per = 0.0
                    total_score += s_per
                    metrics_log.append(("PER", f"{per:.2f}" if per else "N/A", s_per))

                    # 2. Beta
                    if beta < 1.0:
                        s_beta = 1.0
                    elif beta == 1.0:
                        s_beta = 0.5
                    else:
                        s_beta = 0.0
                    total_score += s_beta
                    metrics_log.append(("BETA", f"{beta:.2f}", s_beta))

                    # 3. Dividend Yield
                    if 3.0 <= div_yield <= 5.0:
                        s_yield = 1.0
                    elif (1.0 <= div_yield < 3.0) or (5.0 < div_yield <= 9.0):
                        s_yield = 0.5
                    else:
                        s_yield = 0.0
                    total_score += s_yield
                    metrics_log.append(("Rentabilidad Dividendo", f"{div_yield:.2f}%", s_yield))

                    # 4. Payout
                    if 35.0 <= payout <= 70.0:
                        s_payout = 1.0
                    elif payout > 0:
                        s_payout = 0.5
                    else:
                        s_payout = 0.0
                    total_score += s_payout
                    metrics_log.append(("Payout", f"{payout:.1f}%", s_payout))

                    # 5. Crecimiento (Estimación estándar por datos públicos)
                    s_growth = 0.5  # Valor base por defecto en automático
                    total_score += s_growth
                    metrics_log.append(("Crecimiento Dividendo (Est.)", "Estimado", s_growth))

                else:
                    # Lógica Crecimiento / Sin Dividendo
                    roe = info.get('returnOnEquity', 0)
                    roe_val = (roe * 100) if roe else 10.0
                    s_roic = 1.0 if roe_val > 15 else (0.5 if roe_val >= 8 else 0.0)
                    total_score += s_roic
                    metrics_log.append(("Eficiencia (ROE)", f"{roe_val:.1f}%", s_roic))

                    # Crecimiento ingresos (estimado)
                    revenue_growth = info.get('revenueGrowth', 0)
                    rev_val = (revenue_growth * 100) if revenue_growth else 5.0
                    s_cagr = 1.0 if rev_val > 15 else (0.5 if rev_val >= 5 else 0.0)
                    total_score += s_cagr
                    metrics_log.append(("Crecimiento Ingresos", f"{rev_val:.1f}%", s_cagr))

                    # Deuda / Solvencia
                    total_debt = info.get('totalDebt', 0)
                    total_cash = info.get('totalCash', 0)
                    s_debt = 1.0 if total_cash > total_debt else 0.5
                    total_score += s_debt
                    metrics_log.append(("Solvencia (Caja/Deuda)", "Calculada via Balance", s_debt))

                    # FCF
                    free_cash = info.get('freeCashflow', 1)
                    s_fcf = 1.0 if free_cash and free_cash > 0 else 0.0
                    total_score += s_fcf
                    metrics_log.append(("Flujo de Caja Libre (FCF)", "Positivo" if free_cash and free_cash > 0 else "Negativo", s_fcf))

                    # Moat / Asignación
                    s_moat = 1.0  # Estándar para grandes valores
                    total_score += s_moat
                    metrics_log.append(("Moat / Asignación (Est.)", "Evaluación base", s_moat))

                # Mostrar Resultados
                st.subheader(f"📊 Informe para: {name} ({ticker_input})")
                
                # Tarjeta de puntuación
                st.metric(label="Puntuación Final Automática", value=f"{total_score:.1f} / 5.0")

                # Veredicto de broker
                if total_score >= 4.0:
                    st.success("🟢 **RECOMENDACIÓN: COMPRAR** (Excelente puntuación según fundamentales)")
                elif total_score >= 3.0:
                    st.warning("🟡 **RECOMENDACIÓN: MANTENER / EN VIGILANCIA** (Zona neutral o atractiva con matices)")
                else:
                    st.error("🔴 **RECOMENDACIÓN: DESCARTAR / VENDER** (Baja puntuación en parámetros clave)")

                # Desglose en tabla
                st.markdown("### Desglose de Parámetros:")
                df_res = pd.DataFrame(metrics_log, columns=["Parámetro Evaluado", "Valor Detectado", "Puntuación"])
                st.table(df_res)

            except Exception as e:
                st.error(f"No se han podido recuperar datos automáticos para el ticker '{ticker_input}'. Comprueba que esté bien escrito (ej: usa `ITX.MC` para Inditex en bolsa española o `MSFT` para Microsoft). Error técnico: {e}")
              
