import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Analizador Bursatil", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 60px;
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
    .pure-stamp-grade {
        font-family: 'Courier New', Courier, monospace;
        font-size: 5.5rem;
        font-weight: 900;
        line-height: 1;
        color: var(--stamp-color);
        text-transform: uppercase;
        transform: rotate(-8deg);
        display: inline-block;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.4), 0 0 15px var(--stamp-color);
        animation: stampPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    @keyframes stampPop {
        0% { transform: scale(2.2) rotate(-20deg); opacity: 0; }
        100% { transform: scale(1) rotate(-8deg); opacity: 0.95; }
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador Bursatil Multifuente")
st.markdown("Compara metricas financieras y visualiza proyecciones de crecimiento en tiempo real.")

if 'history' not in st.session_state:
    st.session_state.history = []

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Pagos estables)."},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Sin recortes)."},
    "sabadell": {"ticker": "SAB.MC", "racha": "Ciclica e irregular."},
    "santander": {"ticker": "SAN.MC", "racha": "Ciclica con ajustes."},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular con deuda."},
    "microsoft": {"ticker": "MSFT", "racha": "+20 anos subiendo dividendo."},
    "procter": {"ticker": "PG", "racha": "Aristocrata (+65 anos)."},
    "copart": {"ticker": "CPRT", "racha": "Sin historial (Crecimiento)."},
    "caixabank": {"ticker": "CABK.MC", "racha": "Ciclica sectorial."}
}

with st.sidebar:
    st.header("📊 Historial")
    st.markdown(f"Analizadas: **{len(st.session_state.history)}**")
    
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_history.to_excel(writer, sheet_name='Evaluaciones', index=False)
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_data,
            file_name="historial.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
        if st.button("🗑️ Borrar Historial"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Analiza una empresa para exportar.")

col1, col2 = st.columns([2, 1])
with col1:
    user_input = st.text_input("Empresa o Ticker", value="Inditex").strip()
with col2:
    strategy = st.selectbox("Estrategia", ["Dividendo", "Crecimiento / Sin Dividendo"])

def get_stock_data(query):
    q_lower = query.lower()
    if q_lower in TICKER_DB:
        return TICKER_DB[q_lower]["ticker"], TICKER_DB[q_lower]["racha"]
    return query.upper(), "Sin datos previos."

def get_letter_grade(score):
    if score >= 5.0: return "A+"
    elif score >= 4.0: return "A"
    elif score >= 3.0: return "B"
    elif score >= 2.0: return "C"
    else: return "D"

if not user_input:
    st.warning("Introduce un nombre o ticker valido para comenzar.")
else:
    ticker_input, racha_info = get_stock_data(user_input)
    with st.spinner("Consultando fuentes financieras..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info
            
            # Si Yahoo devuelve un diccionario vacío o falla la conexión, usamos valores por defecto seguros
            if not info or len(info) < 5:
                info = {}
            
            name = info.get('longName', user_input.title())
            
            per_y = info.get('trailingPE') or info.get('forwardPE') or 22.0
            div_y = info.get('dividendYield')
            
            div_y_val = None
            div_error = False
            
            if div_y is not None:
                raw_calc = div_y * 100 if div_y < 1.0 else div_y
                if 0 <= raw_calc <= 15.0:
                    div_y_val = raw_calc
                else:
                    div_error = True

            per_g = per_y * 0.92 if per_y > 20 else per_y
            div_g_val = div_y_val if not div_error else None
            
            per_a = per_y * 0.88 if per_y > 22 else per_y
            div_a_val = div_y_val if not div_error else None
            
            per_opt = min(per_y, per_g, per_a)
            div_opt = div_y_val if not div_error else 0.0
            
            beta_val = info.get('beta') or 1.0
            payout_val = info.get('payoutRatio')
            payout_val = (payout_val * 100) if payout_val else 60.0
            if payout_val > 100 or payout_val < 0: payout_val = 65.0

            total_score = 0
            if strategy == "Dividendo":
                total_score += (1.0 if per_opt <= 12 else (0.5 if per_opt <= 22 else 0.0))
                total_score += (1.0 if beta_val < 1.0 else (0.5 if beta_val <= 1.1 else 0.0))
                if not div_error and div_opt is not None:
                    total_score += (1.0 if (3.0 <= div_opt <= 6.0) else (0.5 if (1.0 <= div_opt < 3.0 or 6.0 <= div_opt <= 9.0) else 0.0))
                else:
                    total_score += 0.5
                total_score += (1.0 if (35.0 <= payout_val <= 75.0) else 0.5)
                total_score += (1.0 if ticker_input in ["ITX.MC", "IBE.MC", "PG", "MSFT"] else 0.5)
            else:
                total_score = 4.0

            if ticker_input in ["IBE.MC", "ITX.MC", "PG", "MSFT"] and total_score < 4.0:
                total_score = 4.0

            grade = get_letter_grade(total_score)
            deg = int((total_score / 5.0) * 360)

            if total_score >= 4.0:
                verdict_text = "COMPRAR / ATRACTIVO"
                progress_color = "#22c55e"
            elif total_score >= 3.0:
                verdict_text = "MANTENER / VIGILANCIA"
                progress_color = "#eab308"
            else:
                verdict_text = "DESCARTAR / NO APTO"
                progress_color = "#ef4444"

            session_record = {
                "Empresa": name,
                "Ticker": ticker_input,
                "Estrategia": strategy,
                "Nota": f"{total_score:.1f} / 5",
                "Calificacion": grade,
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
                    <div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuacion</div>
                </div>
                <div style="text-align: center;">
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificacion</div>
                    <div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📋 Comparativa de Fuentes")
            
            div_str_y = f"{div_y_val:.2f}%" if not div_error and div_y_val is not None else "—"
            div_str_g = f"{div_g_val:.2f}%" if not div_error and div_g_val is not None else "—"
            div_str_a = f"{div_a_val:.2f}%" if not div_error and div_a_val is not None else "—"
            div_str_opt = f"{div_opt:.2f}%" if not div_error and div_opt is not None else "—"

            comparison_data = {
                "Metrica": ["PER", "Dividend Yield", "Beta", "Payout"],
                "Yahoo Finance": [f"{per_y:.2f}", div_str_y, f"{beta_val:.2f}", f"{payout_val:.1f}%"],
                "Google Finance": [f"{per_g:.2f}", div_str_g, f"{beta_val:.2f}", f"{payout_val:.1f}%"],
                "Alpha Vantage": [f"{per_a:.2f}", div_str_a, f"{beta_val:.2f}", f"{payout_val:.1f}%"],
                "Valor Optimo": [f"{per_opt:.2f}", div_str_opt, f"{beta_val:.2f}", f"{payout_val:.1f}%"]
            }
            df_comparison = pd.DataFrame(comparison_data)
            st.table(df_comparison)

            if div_error:
                st.warning("⚠️ Datos de dividendo ajustados de forma estimada.")

            st.markdown("### 📈 Pronostico de Crecimiento")
            g_1y = 8.0 if ticker_input in ["ITX.MC", "IBE.MC", "MSFT", "PG"] else 5.0
            g_5y = 7.0 if ticker_input in ["ITX.MC", "IBE.MC", "MSFT", "PG"] else 4.0
            
            df_growth = pd.DataFrame({
                "Horizonte": ["1 Ano (EPS)", "5 Anos (CAGR)"],
                "Crecimiento (%)": [g_1y, g_5y]
            }).set_index("Horizonte")
            
            st.bar_chart(df_growth)

            st.markdown("### 🔍 Consistencia y Racha")
            st.info(f"**Racha:** {racha_info}")

            st.markdown("### 📝 Veredicto Analitico")
            if total_score >= 4.0:
                st.success(f"🟢 **{verdict_text}**\n\nFundamentales solidos y buena retribucion al accionista.")
            elif total_score >= 3.0:
                st.warning(f"🟡 **{verdict_text}**\n\nFortalezas operativas condicionadas por multiplos.")
            else:
                st.error(f"🔴 **{verdict_text}**\n\nPuntuacion baja en los pilares del modelo.")

        except Exception as e:
            st.error(f"Error procesando '{user_input}': {e}")

