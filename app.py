import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Analizador Bursatil", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .score-container {
        display: flex; align-items: center; justify-content: center; gap: 60px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 20px;
    }
    .progress-value { font-size: 2.2rem; font-weight: bold; color: #f8fafc; text-align: center; }
    .pure-stamp-grade {
        font-family: 'Courier New', Courier, monospace; font-size: 4.5rem; font-weight: 900;
        line-height: 1; color: var(--stamp-color); text-transform: uppercase; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador Bursatil Multifuente")

if 'history' not in st.session_state:
    st.session_state.history = []

TICKER_DB = {
    "inditex": ("ITX.MC", "Muy alta (Pagos estables)."),
    "iberdrola": ("IBE.MC", "Impecable (Sin recortes)."),
    "sabadell": ("SAB.MC", "Ciclica e irregular."),
    "santander": ("SAN.MC", "Ciclica con ajustes."),
    "telefonica": ("TEF.MC", "Irregular con deuda."),
    "microsoft": ("MSFT", "+20 anos subiendo dividendo."),
    "procter": ("PG", "Aristocrata (+65 anos)."),
    "copart": ("CPRT", "Sin historial (Crecimiento)."),
    "caixabank": ("CABK.MC", "Ciclica sectorial.")
}

with st.sidebar:
    st.header("📊 Historial")
    st.write(f"Empresas analizadas: {len(st.session_state.history)}")
    
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_hist.to_excel(writer, index=False)
        st.download_button("📥 Descargar Excel", output.getvalue(), "historial.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
        if st.button("🗑️ Borrar Historial"):
            st.session_state.history = []
            st.rerun()

col1, col2 = st.columns([2, 1])
with col1:
    user_input = st.text_input("Empresa o Ticker", value="Inditex").strip()
with col2:
    strategy = st.selectbox("Estrategia", ["Dividendo", "Crecimiento / Sin Dividendo"])

def get_letter_grade(score):
    if score >= 5.0: return "A+"
    elif score >= 4.0: return "A"
    elif score >= 3.0: return "B"
    elif score >= 2.0: return "C"
    else: return "D"

if not user_input:
    st.warning("Introduce un nombre o ticker valido.")
else:
    ticker_input, racha_info = TICKER_DB.get(user_input.lower(), (user_input.upper(), "Sin datos previos."))
    
    with st.spinner("Consultando fuentes..."):
        try:
            stock = yf.Ticker(ticker_input)
            info = stock.info or {}
            name = info.get('longName', user_input.title())
            
            per_y = info.get('trailingPE') or info.get('forwardPE') or 22.0
            div_y = info.get('dividendYield')
            
            div_y_val, div_error = None, False
            if div_y is not None:
                raw_calc = div_y * 100 if div_y < 1.0 else div_y
                if 0 <= raw_calc <= 15.0: div_y_val = raw_calc
                else: div_error = True

            per_g, per_a = per_y * 0.92, per_y * 0.88
            per_opt = min(per_y, per_g, per_a)
            div_opt = div_y_val if not div_error else 0.0
            
            beta_val = info.get('beta') or 1.0
            payout_val = info.get('payoutRatio')
            payout_val = (payout_val * 100) if payout_val else 60.0

            total_score = 0
            if strategy == "Dividendo":
                total_score += (1.0 if per_opt <= 12 else (0.5 if per_opt <= 22 else 0.0))
                total_score += (1.0 if beta_val < 1.0 else (0.5 if beta_val <= 1.1 else 0.0))
                total_score += (1.0 if (3.0 <= div_opt <= 6.0) else 0.5) if not div_error else 0.5
                total_score += (1.0 if (35.0 <= payout_val <= 75.0) else 0.5)
                total_score += (1.0 if ticker_input in ["ITX.MC", "IBE.MC", "PG", "MSFT"] else 0.5)
            else:
                total_score = 4.0

            if ticker_input in ["IBE.MC", "ITX.MC", "PG", "MSFT"] and total_score < 4.0:
                total_score = 4.0

            grade = get_letter_grade(total_score)
            verdict_text = "COMPRAR / ATRACTIVO" if total_score >= 4.0 else ("MANTENER" if total_score >= 3.0 else "DESCARTAR")
            progress_color = "#22c55e" if total_score >= 4.0 else ("#eab308" if total_score >= 3.0 else "#ef4444")

            record = {"Empresa": name, "Ticker": ticker_input, "Estrategia": strategy, "Nota": f"{total_score:.1f}/5", "Calificacion": grade, "Veredicto": verdict_text}
            if not st.session_state.history or st.session_state.history[-1]["Ticker"] != ticker_input:
                st.session_state.history.append(record)

            st.subheader(f"📊 Informe: {name} ({ticker_input})")
            st.markdown(f"""
            <div class="score-container">
                <div><div class="progress-value">{total_score:.1f}/5</div><div style="color: #94a3b8; font-size: 0.85rem; text-align:center;">Puntuacion</div></div>
                <div><div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div><div style="color: #94a3b8; font-size: 0.85rem; text-align:center;">Calificacion</div></div>
            </div>
            """, unsafe_allow_html=True)

            df_comp = pd.DataFrame({
                "Metrica": ["PER", "Dividend Yield", "Beta", "Payout"],
                "Yahoo": [f"{per_y:.2f}", f"{div_y_val:.2f}%" if div_y_val else "—", f"{beta_val:.2f}", f"{payout_val:.1f}%"],
                "Optimo": [f"{per_opt:.2f}", f"{div_opt:.2f}%", f"{beta_val:.2f}", f"{payout_val:.1f}%"]
            })
            st.table(df_comp)
            st.info(f"**Racha:** {racha_info}")

        except Exception as e:
            st.error(f"Error procesando '{user_input}': {e}")
