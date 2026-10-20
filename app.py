import streamlit as st
import yfinance as yf
import pandas as pd
import json

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #0f172a;
        padding: 10px 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 25px;
    }
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
        animation: stampPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    @keyframes stampPop {
        0% { transform: scale(2.2) rotate(-20deg); opacity: 0; }
        100% { transform: scale(1) rotate(-8deg); opacity: 0.95; }
    }

    .traffic-light-card {
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        border-left: 8px solid;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .tl-buy {
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
        border-color: #10b981;
        color: #ecfdf5;
    }
    .tl-hold {
        background: linear-gradient(135deg, #713f12 0%, #451a03 100%);
        border-color: #f59e0b;
        color: #fef3c7;
    }
    .tl-avoid {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%);
        border-color: #ef4444;
        color: #fef2f2;
    }
    .tl-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .neon-stream-vertical {
        position: relative;
        width: 40px;
        height: 50px;
        overflow: hidden;
        display: inline-block;
        margin: 0 auto;
    }
    .neon-stream-horizontal {
        position: relative;
        width: 70px;
        height: 30px;
        overflow: hidden;
        display: inline-block;
        margin: 0 auto;
    }

    @keyframes slideUpStream {
        0% { top: 45px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #22c55e; }
        50% { opacity: 1; filter: blur(0px); text-shadow: 0 0 12px #22c55e, 0 0 22px #22c55e; }
        100% { top: -15px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #22c55e; }
    }
    @keyframes slideDownStream {
        0% { top: -15px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #ef4444; }
        50% { opacity: 1; filter: blur(0px); text-shadow: 0 0 12px #ef4444, 0 0 22px #ef4444; }
        100% { top: 45px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #ef4444; }
    }
    @keyframes slideRightStream {
        0% { left: -15px; opacity: 0; filter: blur(2px); text-shadow: 0 0 2px #eab308; }
        50% { opacity: 1; filter: blur(0px); text-shadow: 0 0 12px #eab308, 0 0 22px #eab308; }
        100% { left: 70px; opacity: 0; filter: blur(2px); text-shadow: 0 0 12px #eab308; }
    }

    .arrow-item-up {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.6rem;
        font-weight: 900;
        color: #22c55e;
        animation: slideUpStream 2.6s infinite linear;
    }
    .arrow-item-down {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.6rem;
        font-weight: 900;
        color: #ef4444;
        animation: slideDownStream 2.6s infinite linear;
    }
    .arrow-item-side {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        font-weight: 900;
        color: #eab308;
        animation: slideRightStream 2.8s infinite linear;
    }

    .st-1 { animation-delay: 0.0s; }
    .st-2 { animation-delay: 0.8s; }
    .st-3 { animation-delay: 1.6s; }

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
    .final-net-title {
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #a7f3d0;
        margin-bottom: 5px;
        font-weight: 600;
    }
    .final-net-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

if 'stage' not in st.session_state:
    st.session_state.stage = 'home'
if 'asset_type' not in st.session_state:
    st.session_state.asset_type = None
if 'sub_type' not in st.session_state:
    st.session_state.sub_type = None
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'selected_eval_input' not in st.session_state:
    st.session_state.selected_eval_input = ""

def cargar_desde_url():
    if 'data_loaded' not in st.session_state:
        if "favs" in st.query_params:
            try:
                st.session_state.favorites = json.loads(st.query_params["favs"])
            except:
                st.session_state.favorites = []
        if "port" in st.query_params:
            try:
                st.session_state.portfolio = json.loads(st.query_params["port"])
            except:
                st.session_state.portfolio = []
        st.session_state.data_loaded = True

def guardar_en_url():
    try:
        st.query_params["favs"] = json.dumps(st.session_state.favorites)
        st.query_params["port"] = json.dumps(st.session_state.portfolio)
    except:
        pass

cargar_desde_url()

def reset_navigation():
    st.session_state.stage = 'home'
    st.session_state.asset_type = None
    st.session_state.sub_type = None
    st.session_state.selected_eval_input = ""

@st.cache_data(ttl=3600)
def get_eur_usd_rate():
    try:
        fx = yf.Ticker("EURUSD=X")
        rate = fx.history(period="1d")['Close'].iloc[-1]
        return float(rate) if rate > 0 else 1.08
    except:
        return 1.08

FUND_DB = {
    "axa court terme ac": {
        "name": "AXA Court Terme AC (Fondo Monetario Euro)", "ticker": "FR0000447823",
        "category": "Fondos Monetarios", "ter": 0.15, "aum": 6500, "tracking_error": 0.01, "age_years": 25, "currency": "EUR", "is_dist": False, "return_1y": 3.5, "score": 4.8,
        "desc": "Fondo monetario de corto plazo en euros, ideal para aparcar liquidez con bajo riesgo y rentabilidad ligada a tipos del BCE."
    },
    "fidelity msci world acc": {
        "name": "Fidelity MSCI World Index Fund EUR P Acc", "ticker": "IE00BYX5NX33",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.10, "aum": 8500, "tracking_error": 0.06, "age_years": 8, "currency": "EUR", "is_dist": False, "return_1y": 15.9, "score": 4.7,
        "desc": "Uno de los fondos globales más económicos del mercado europeo para replicar el índice MSCI World."
    },
    "vanguard sp 500 acc": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc", "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 17000, "tracking_error": 0.03, "age_years": 22, "currency": "EUR", "is_dist": False, "return_1y": 22.4, "score": 4.8,
        "desc": "Fondo indexado histórico que replica el comportamiento de las 500 empresas más grandes de Estados Unidos."
    }
}

ETF_DB = {
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000,
        "replication": "Física (Completa)", "te": 0.01, "currency": "EUR", "age_years": 3, "is_dist": False, "return_1y": 22.3, "score": 4.9,
        "desc": "El ETF del S&P 500 con el coste operativo más bajo de Europa (TER del 0.03%)."
    },
    "vwce.de": {
        "name": "Vanguard FTSE All-World UCITS ETF [Acumulación]", "ticker": "VWCE.DE",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.22, "aum": 15000,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 7, "is_dist": False, "return_1y": 16.0, "score": 4.8,
        "desc": "Incluye tanto países desarrollados como mercados emergentes (más de 3.700 valores en todo el mundo)."
    }
}

# FUNCIÓN PARA EL SEMÁFORO BASADO EN TUS 5 PARÁMETROS
def evaluate_stock_parameters(per, beta, div_yield, payout):
    score = 3.0
    messages = []

    # 1. PER
    if per > 0:
        if per < 10:
            score += 1.0
            messages.append("🟢 **PER < 10:** Empresa barata.")
        elif 10 <= per <= 17:
            score += 0.5
            messages.append("🟢 **PER 10-17:** Precio razonable.")
        elif per > 25:
            score -= 1.0
            messages.append("🔴 **PER > 25:** Posible burbuja o valoración muy exigente.")
        else:
            messages.append("🟡 **PER 17-25:** Valoración moderada o alta.")
    else:
        messages.append("🟡 **PER no disponible o negativo.**")

    # 2. BETA
    if beta is not None:
        if beta < 1:
            score += 0.5
            messages.append("🟢 **Beta < 1:** Acción tranquila / defensiva.")
        elif 0.9 <= beta <= 1.1:
            score += 0.2
            messages.append("🟡 **Beta ~ 1:** Se mueve igual que el mercado.")
        else:
            score -= 0.5
            messages.append("🔴 **Beta > 1:** Acción más imprevisible / volátil.")
    else:
        messages.append("🟡 **Beta no disponible.**")

    # 3. RENTABILIDAD / DIVIDEND YIELD
    if div_yield is not None:
        if 3.0 <= div_yield <= 5.0:
            score += 0.8
            messages.append("🟢 **Div. Yield 3% - 5%:** Buena rentabilidad por dividendo.")
        elif div_yield > 9.0:
            score -= 1.5
            messages.append("🔴 **Div. Yield > 9%: ¡Huye!** Riesgo elevado de trampa de valor o dividendo insostenible.")
        elif div_yield > 0:
            messages.append(f"🟡 **Div. Yield del {div_yield:.1f}%:** Fuera del rango óptimo del 3%-5%.")
        else:
            messages.append("🟡 **Sin dividendo o 0%.**")

    # 4. PAYOUT
    if payout is not None:
        if payout < 35:
            score += 0.3
            messages.append("🟡 **Payout < 35%:** Poco reparto (mucho beneficio retenido para crecer).")
        elif 35 <= payout <= 70:
            score += 0.7
            messages.append("🟢 **Payout 35% - 70%:** Saludable y sostenible.")
        elif payout > 70:
            score -= 1.0
            messages.append("🔴 **Payout > 70%: ¡Peligro!** Poco margen ante caídas de beneficios.")
    else:
        messages.append("🟡 **Payout no disponible.**")

    final_score = min(5.0, max(1.0, score))
    return final_score, messages

def render_traffic_light_recommendation(score, details_list):
    if score >= 4.0:
        badge_class = "tl-buy"
        icon = "🟢"
        status = "RECOMENDACIÓN DE COMPRA / MUY FAVORABLE"
    elif score >= 2.8:
        badge_class = "tl-hold"
        icon = "🟡"
        status = "RECOMENDACIÓN NEUTRAL / MANTENER EN OBSERVACIÓN"
    else:
        badge_class = "tl-avoid"
        icon = "🔴"
        status = "PRECAUCIÓN / EVALUAR OTRAS ALTERNATIVAS"

    bullet_html = "".join([f"<li>{msg}</li>" for msg in details_list])

    st.markdown(f"""
    <div class="traffic-light-card {badge_class}">
        <div class="tl-title">{icon} Semáforo de Análisis: {status}</div>
        <ul style="margin: 0; padding-left: 20px; font-size: 0.95rem;">
            {bullet_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

ETF_BROKER_PROFILES = {
    "Trade Republic (1€ orden / Planes a 0€)": {"fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "DEGIRO (Bajas comisiones / 1€ por operación)": {"fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False},
    "Personalizado (Ajustar manualmente)": {"fee_percent": 0.10, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False}
}

portfolio_count = len(st.session_state.portfolio)
favorites_count = len(st.session_state.favorites)

col_tb1, col_tb2, col_tb3 = st.columns([2, 1, 1])
with col_tb1:
    st.markdown("### 📈 Analizador Bursátil Multifuente")
with col_tb2:
    if st.button(f"⭐ Favoritos ({favorites_count})", use_container_width=True):
        st.session_state.stage = "favorites_view"
        st.rerun()
with col_tb3:
    if st.button(f"💼 Mi Cartera ({portfolio_count})", use_container_width=True, type="primary"):
        st.session_state.stage = "portfolio_view"
        st.rerun()

st.markdown("---")

if st.session_state.stage == 'home':
    st.markdown("### ¿Qué tipo de activo quieres evaluar?")
    col1, col2, col3, col4 = st.columns(4)
    
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
    with col4:
        if st.button("🏦 Fondos Monetarios", use_container_width=True, type="primary"):
            st.session_state.asset_type = "Fondos Monetarios"
            st.session_state.stage = "analyzer"
            st.session_state.sub_type = "Biblioteca Monetarios"
            st.rerun()

elif st.session_state.stage == 'sub_options':
    if st.button("← Volver a selección de activos"):
        reset_navigation()
        st.rerun()

    st.title(f"Configuración para: {st.session_state.asset_type}")
    if st.session_state.asset_type == "Acciones":
        if st.button("Continuar al Analizador", use_container_width=True, type="primary"):
            st.session_state.stage = "analyzer"
            st.rerun()
    else:
        if st.button("Ver Biblioteca / Evaluar", use_container_width=True, type="primary"):
            st.session_state.stage = "analyzer"
            st.rerun()

elif st.session_state.stage == 'analyzer':
    if st.button("← Volver"):
        reset_navigation()
        st.rerun()

    st.title("📈 Analizador Bursátil en Euros (€)")
    user_input = st.text_input("Introduce Ticker de Acción (ej. SAN.MC, AAPL, TEF.MC):", value=st.session_state.selected_eval_input).strip().upper()

    if user_input:
        try:
            stock = yf.Ticker(user_input)
            hist_price = stock.history(period="3mo")
            info = stock.info or {}
            name = info.get('longName', user_input)
            native_currency = info.get('currency', 'EUR')

            current_price_native = None
            if not hist_price.empty and 'Close' in hist_price.columns:
                valid_closes = hist_price['Close'].dropna()
                if not valid_closes.empty:
                    current_price_native = float(valid_closes.iloc[-1])

            eur_usd_rate = get_eur_usd_rate()
            if native_currency == 'USD' and current_price_native is not None:
                current_price_eur = current_price_native / eur_usd_rate
            else:
                current_price_eur = current_price_native

            price_display = f"{current_price_eur:,.2f} €" if current_price_eur is not None else "—"

            per = info.get('trailingPE') or info.get('forwardPE') or 15.0
            beta = info.get('beta') or 1.0
            
            raw_yield = info.get('dividendYield', 0) or 0.0
            div_yield = (raw_yield * 100) if raw_yield < 0.1 else raw_yield

            raw_payout = info.get('payoutRatio')
            payout = (raw_payout * 100) if raw_payout is not None else 50.0

            total_score, analysis_messages = evaluate_stock_parameters(per, beta, div_yield, payout)
            grade = "A+" if total_score >= 4.5 else ("A" if total_score >= 4.0 else ("B" if total_score >= 3.0 else "C"))
            deg = int((total_score / 5.0) * 360)
            progress_color = "#22c55e" if total_score >= 4.0 else ("#eab308" if total_score >= 2.8 else "#ef4444")

            st.subheader(f"📊 Informe: {name} ({user_input})")
            st.markdown(f"""
            <div class="score-container">
                <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg}deg; --progress-color: {progress_color};"><div class="progress-value">{total_score:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación Algorítmica</div></div>
                <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div></div>
                <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio Actual (€)</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display}</div></div>
            </div>
            """, unsafe_allow_html=True)

            render_traffic_light_recommendation(total_score, analysis_messages)

            df_metrics = pd.DataFrame({
                "Parámetro Clave": ["PER", "Beta", "Rentabilidad por Dividendo", "Payout", "Crecimiento del Dividendo"],
                "Valor Detectado": [f"{per:.2f}", f"{beta:.2f}", f"{div_yield:.2f}%", f"{payout:.1f}%", "Histórico sostenido (> Inflación)"],
                "Evaluación según tus Baremos": [
                    "Barata (<10)" if per < 10 else ("Razonable (10-17)" if per <= 17 else "Burbuja (>25)"),
                    "Tranquila (<1)" if beta < 1 else ("Igual al mercado (~1)" if 0.9 <= beta <= 1.1 else "Imprevisible (>1)"),
                    "Buena (3%-5%)" if 3 <= div_yield <= 5 else ("¡Huye! (>9%)" if div_yield > 9 else "Moderada"),
                    "Poco reparto (<35%)" if payout < 35 else ("Saludable (35%-70%)" if payout <= 70 else "Peligro (>70%)"),
                    "Favorable"
                ]
            })
            st.table(df_metrics)

        except Exception as e:
            st.error(f"No se han podido procesar los datos para '{user_input}'. Verifica que sea un ticker válido en Yahoo Finance (ej. BBVA.MC o SAN.MC). Error: {e}")
