import streamlit as st
import yfinance as yf
import pandas as pd
import json
import re

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 40px;
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
        width: 110px;
        height: 110px;
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
        width: 88px;
        height: 88px;
        border-radius: 50%;
        background-color: #0f172a;
    }
    .progress-value {
        position: relative;
        font-size: 1.6rem;
        font-weight: bold;
        color: #f8fafc;
    }
    .pure-stamp-grade {
        font-family: 'Courier New', Courier, monospace;
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
        color: var(--stamp-color);
        text-transform: uppercase;
        transform: rotate(-8deg);
        display: inline-block;
        text-shadow: 3px 3px 0px rgba(0,0,0,0.8), 0 0 5px rgba(0,0,0,0.5);
    }
    .traffic-light-card {
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        border-left: 8px solid;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .tl-buy { background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); border-color: #10b981; color: #ecfdf5; }
    .tl-hold { background: linear-gradient(135deg, #713f12 0%, #451a03 100%); border-color: #f59e0b; color: #fef3c7; }
    .tl-avoid { background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); border-color: #ef4444; color: #fef2f2; }
    .tl-title { font-size: 1.25rem; font-weight: 800; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
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
    .final-net-title { font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #a7f3d0; margin-bottom: 5px; font-weight: 600; }
    .final-net-value { font-size: 2.2rem; font-weight: 800; color: #ffffff; }
</style>
""", unsafe_allow_html=True)

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

def cargar_desde_url():
    if 'data_loaded' not in st.session_state:
        if "favs" in st.query_params:
            try: st.session_state.favorites = json.loads(st.query_params["favs"])
            except: st.session_state.favorites = []
        if "port" in st.query_params:
            try: st.session_state.portfolio = json.loads(st.query_params["port"])
            except: st.session_state.portfolio = []
        st.session_state.data_loaded = True

def guardar_en_url():
    try:
        st.query_params["favs"] = json.dumps(st.session_state.favorites)
        st.query_params["port"] = json.dumps(st.session_state.portfolio)
    except:
        pass

cargar_desde_url()

@st.cache_data(ttl=3600)
def get_eur_usd_rate():
    try:
        fx = yf.Ticker("EURUSD=X")
        rate = fx.history(period="1d")['Close'].iloc[-1]
        return float(rate) if rate > 0 else 1.08
    except:
        return 1.08

def extraer_ticker_de_url(texto_o_url):
    texto_o_url = texto_o_url.strip()
    yahoo_match = re.search(r'finance\.yahoo\.com/quote/([A-Za-z0-9\.\-]+)', texto_o_url, re.IGNORECASE)
    if yahoo_match:
        return yahoo_match.group(1).upper()
    investing_match = re.search(r'investing\.com/equities/([A-Za-z0-9\-]+)', texto_o_url, re.IGNORECASE)
    if investing_match:
        return investing_match.group(1).split('/')[0].upper()
    return texto_o_url

FUND_DB = {
    "axa court terme ac": {"name": "AXA Court Terme AC", "ticker": "FR0000447823", "category": "Fondos Monetarios", "ter": 0.15, "aum": 6500, "is_dist": False, "score": 4.8},
    "es0165185002": {"name": "MyInvestor Dividendos (Acc)", "ticker": "ES0165185002", "category": "Alto Dividendo Global", "ter": 0.30, "aum": 210, "is_dist": False, "score": 4.3},
    "fidelity msci world acc": {"name": "Fidelity MSCI World Index Fund", "ticker": "IE00BYX5NX33", "category": "Renta Variable Global", "ter": 0.10, "aum": 8500, "is_dist": False, "score": 4.7},
    "vanguard sp 500 acc": {"name": "Vanguard U.S. 500 Stock Index Fund", "ticker": "IE0032126645", "category": "Renta Variable EE.UU.", "ter": 0.10, "aum": 17000, "is_dist": False, "score": 4.8}
}

ETF_DB = {
    "spyl.de": {"name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE", "category": "Renta Variable EE.UU.", "ter": 0.03, "aum": 12000, "replication": "Física", "is_dist": False, "score": 4.9},
    "vwce.de": {"name": "Vanguard FTSE All-World UCITS ETF", "ticker": "VWCE.DE", "category": "Renta Variable Global", "ter": 0.22, "aum": 15000, "replication": "Física", "is_dist": False, "score": 4.8}
}

ETF_BROKER_PROFILES = {
    "Trade Republic (1€ orden / Planes a 0€)": {"fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "Degiro (Bajas comisiones)": {"fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False}
}

portfolio_count = len(st.session_state.portfolio)
favorites_count = len(st.session_state.favorites)

col_tb1, col_tb2, col_tb3 = st.columns([1.5, 1, 1])
with col_tb1:
    st.markdown("### 📈 Analizador Bursátil")
with col_tb2:
    if st.button(f"⭐ Favoritos ({favorites_count})", use_container_width=True):
        st.session_state.view_mode = "favorites"
        st.rerun()
with col_tb3:
    if st.button(f"💼 Simulador de Cartera ({portfolio_count})", use_container_width=True, type="primary"):
        st.session_state.view_mode = "portfolio"
        st.rerun()

st.markdown("---")

# VISTA DE FAVORITOS
if st.session_state.get("view_mode") == "favorites":
    if st.button("← Volver al Buscador"):
        st.session_state.view_mode = "home"
        st.rerun()
    st.title("⭐ Mis Activos Favoritos")
    if not st.session_state.favorites:
        st.info("No tienes favoritos guardados.")
    else:
        for idx, fav in enumerate(st.session_state.favorites):
            st.write(f"- {fav['name']} ({fav['ticker']})")

# VISTA DE CARTERA
elif st.session_state.get("view_mode") == "portfolio":
    if st.button("← Volver al Buscador"):
        st.session_state.view_mode = "home"
        st.rerun()
    st.title("💼 Simulador Global de Cartera")
    if not st.session_state.portfolio:
        st.info("Tu cartera está vacía.")

# VISTA PRINCIPAL (LANDING ÚNICA)
else:
    st.title("Analizador Bursátil")
    
    input_bruto = st.text_input("escribe el ticker, nombre o el ISIN que deseas analizar", value="").strip()
    user_input = extraer_ticker_de_url(input_bruto)

    def get_letter_grade(score):
        if score >= 4.5: return "A+"
        elif score >= 4.0: return "A"
        elif score >= 3.0: return "B"
        elif score >= 2.0: return "C"
        else: return "D"

    def render_traffic_light_recommendation(score, asset_type, details=None):
        if score >= 4.0:
            badge_class, icon, status = "tl-buy", "🟢", "RECOMENDACIÓN DE COMPRA / MUY FAVORABLE"
            desc = "Activo con fundamentales sólidos y excelente tendencia."
        elif score >= 2.8:
            badge_class, icon, status = "tl-hold", "🟡", "RECOMENDACIÓN NEUTRAL / MANTENER"
            desc = "Empresa o fondo aceptable con métricas moderadas."
        else:
            badge_class, icon, status = "tl-avoid", "🔴", "PRECAUCIÓN"
            desc = "Se detectan debilidades técnicas o fundamentales."
        
        detail_html = f"<div style='margin-top: 8px; font-size: 0.9rem;'><b>Detalles:</b> {details}</div>" if details else ""
        st.markdown(f"""
        <div class="traffic-light-card {badge_class}">
            <div class="tl-title">{icon} Semáforo de Análisis: {status}</div>
            <div>{desc}</div>
            {detail_html}
        </div>
        """, unsafe_allow_html=True)

    if user_input:
        # Detectar si es Fondo, ETF o Acción
        matched_fund = next((data for k, data in FUND_DB.items() if data["ticker"].upper() == user_input.upper() or k in user_input.lower()), None)
        matched_etf = next((data for k, data in ETF_DB.items() if data["ticker"].upper() == user_input.upper() or k in user_input.lower()), None)

        if matched_fund or matched_etf:
            item = matched_fund if matched_fund else matched_etf
            score = item.get('score', 4.5)
            grade = get_letter_grade(score)
            deg = int((score / 5.0) * 360)
            color = "#22c55e" if score >= 4.0 else "#eab308"

            st.subheader(f"📊 Informe: {item['name']} ({item['ticker']})")
            st.markdown(f"""
            <div class="score-container">
                <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg}deg; --progress-color: {color};"><div class="progress-value">{score:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8;">Puntuación</div></div>
                <div style="text-align: center;"><div style="color: #94a3b8;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {color};">{grade}</div></div>
            </div>
            """, unsafe_allow_html=True)
            render_traffic_light_recommendation(score, "Fondo/ETF", f"TER: {item['ter']}% | Patrimonio: {item['aum']} M€")
        else:
            try:
                stock = yf.Ticker(user_input)
                hist_price = stock.history(period="6mo")
                info = stock.info or {}
                name = info.get('longName', user_input.title())
                native_currency = info.get('currency', 'EUR')

                if hist_price.empty:
                    st.error(f"No se han encontrado datos para '{user_input}'.")
                else:
                    current_price_native = float(hist_price['Close'].iloc[-1])
                    cur_rate = get_eur_usd_rate()
                    current_price_eur = current_price_native / cur_rate if native_currency == 'USD' else current_price_native
                    
                    per_y = info.get('trailingPE') or 18.0
                    roe_val = (info.get('returnOnEquity', 0.15) * 100) if info.get('returnOnEquity') else 15.0
                    
                    score_calc = 2.5
                    if 0 < per_y <= 18: score_calc += 1.0
                    if roe_val >= 15: score_calc += 1.0
                    total_score = min(5.0, max(1.0, score_calc))

                    grade = get_letter_grade(total_score)
                    deg = int((total_score / 5.0) * 360)
                    color = "#22c55e" if total_score >= 4.0 else "#eab308"

                    st.subheader(f"📊 Informe de Acción: {name} ({user_input})")
                    st.markdown(f"""
                    <div class="score-container">
                        <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg}deg; --progress-color: {color};"><div class="progress-value">{total_score:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8;">Puntuación</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {color};">{grade}</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8;">Precio Actual</div><div style="font-size: 2rem; font-weight: bold; color: white;">{current_price_eur:,.2f} €</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    render_traffic_light_recommendation(total_score, "Acción", f"PER: {per_y:.1f} | ROE: {roe_val:.1f}%")
                    st.markdown("### 📈 Evolución Gráfica (Últimos 6 meses)")
                    st.line_chart(hist_price['Close'])
            except Exception as e:
                st.error(f"Error al analizar el activo: {e}")
