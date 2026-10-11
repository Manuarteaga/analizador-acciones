import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json
import urllib.parse

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

    .featured-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #38bdf8;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 10px;
    }
    .featured-badge {
        background-color: #0284c7;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
    }
    .score-tag {
        background-color: #065f46;
        color: #34d399;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: bold;
        float: right;
    }
    .compare-box {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Control de Estados y Persistencia en URL Nativa
if 'stage' not in st.session_state:
    st.session_state.stage = 'home'
if 'asset_type' not in st.session_state:
    st.session_state.asset_type = None
if 'sub_type' not in st.session_state:
    st.session_state.sub_type = None
if 'history' not in st.session_state:
    st.session_state.history = []
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

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios).", "div_growth": 6.5, "div_yield": 2.8, "per": 24.0, "beta": 0.95, "payout": 60.0},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos).", "div_growth": 5.0, "div_yield": 4.8, "per": 16.5, "beta": 0.65, "payout": 70.0},
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5, "per": 8.0, "beta": 1.25, "payout": 50.0},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0, "per": 7.5, "beta": 1.30, "payout": 40.0},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5, "per": 12.0, "beta": 0.85, "payout": 85.0},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico sin dependencia de dividendo tradicional.", "div_growth": 10.0, "div_yield": 0.7, "per": 32.0, "beta": 0.90, "payout": 25.0},
    "procter & gamble": {"ticker": "PG", "racha": "Excepcional. Aristócrata del Dividendo con más de 65 años de subidas ininterrumpidas.", "div_growth": 6.0, "div_yield": 2.4, "per": 25.0, "beta": 0.55, "payout": 60.0},
    "copart": {"ticker": "CPRT", "racha": "Empresa pura de crecimiento orientada a reinvestigación.", "div_growth": 0.0, "div_yield": 0.0, "per": 28.0, "beta": 1.05, "payout": 0.0},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sensible al ciclo económico y a los planes de consolidación bancaria.", "div_growth": 4.5, "div_yield": 6.2, "per": 8.5, "beta": 1.10, "payout": 60.0}
}

FUND_DB = {
    "vanguard global stock acc": {
        "name": "Vanguard Global Stock Index Fund EUR Acc",
        "ticker": "IE00B03HD191",
        "category": "Renta Variable Global (MSCI World) - Acumulación",
        "ter": 0.18,
        "aum": 23000,
        "tracking_error": 0.08,
        "age_years": 15,
        "currency": "EUR",
        "is_dist": False,
        "div_yield": 0.0,
    },
    "vanguard global stock dist": {
        "name": "Vanguard Global Stock Index Fund EUR Dist",
        "ticker": "IE00B03HD209",
        "category": "Renta Variable Global (MSCI World) - Distribución",
        "ter": 0.18,
        "aum": 4500,
        "tracking_error": 0.08,
        "age_years": 12,
        "currency": "EUR",
        "is_dist": True,
        "div_yield": 1.8,
    },
    "ishares developed world acc": {
        "name": "iShares Developed World Index Fund (IE) D Acc EUR",
        "ticker": "IE00BD0NCM55",
        "category": "Renta Variable Global (MSCI World) - Acumulación",
        "ter": 0.12,
        "aum": 25000,
        "tracking_error": 0.05,
        "age_years": 10,
        "currency": "EUR",
        "is_dist": False,
        "div_yield": 0.0,
    },
    "vanguard sp 500 acc": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc",
        "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU. (S&P 500) - Acumulación",
        "ter": 0.10,
        "aum": 17000,
        "tracking_error": 0.03,
        "age_years": 22,
        "currency": "EUR",
        "is_dist": False,
        "div_yield": 0.0,
    },
}

ETF_DB = {
    "vwce.de": {
        "name": "Vanguard FTSE All-World UCITS ETF (Acc)",
        "ticker": "VWCE.DE",
        "category": "Renta Variable Global (All-World) - Acumulación",
        "ter": 0.22,
        "aum": 15000,
        "replication": "Física (Completa)",
        "te": 0.04,
        "currency": "EUR",
        "age_years": 7,
        "is_dist": False,
        "div_yield": 0.0,
    },
    "vwrl.de": {
        "name": "Vanguard FTSE All-World UCITS ETF (Dist)",
        "ticker": "VWRL.DE",
        "category": "Renta Variable Global (All-World) - Distribución",
        "ter": 0.22,
        "aum": 8000,
        "replication": "Física (Completa)",
        "te": 0.04,
        "currency": "EUR",
        "age_years": 12,
        "is_dist": True,
        "div_yield": 2.1,
    },
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF (Acc)",
        "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500) - Acumulación",
        "ter": 0.03,
        "aum": 12000,
        "replication": "Física (Completa)",
        "te": 0.01,
        "currency": "EUR",
        "age_years": 3,
        "is_dist": False,
        "div_yield": 0.0,
    },
    "vanguard high dividend yield etf": {
        "name": "Vanguard High Dividend Yield ETF (VYM - Dist)",
        "ticker": "VYM",
        "category": "Renta Variable Dividendos (EE.UU.) - Distribución",
        "ter": 0.06,
        "aum": 55000,
        "replication": "Física",
        "te": 0.02,
        "currency": "USD",
        "is_dist": True,
        "div_yield": 3.0,
    },
    "sgld.l": {
        "name": "Invesco Physical Gold ETC",
        "ticker": "SGLD.L",
        "category": "Materias Primas (Oro)",
        "ter": 0.12,
        "aum": 14000,
        "replication": "Física (Oro)",
        "te": 0.01,
        "currency": "USD",
        "is_dist": False,
        "div_yield": 0.0,
    },
    "uso": {
        "name": "United States Oil Fund, LP (Crudo)",
        "ticker": "USO",
        "category": "Materias Primas (Petróleo Crudo)",
        "ter": 0.60,
        "aum": 1200,
        "replication": "Futuros",
        "te": 0.15,
        "currency": "USD",
        "is_dist": False,
        "div_yield": 0.0,
    }
}

def get_best_single_monthly_recommendation():
    candidates = []
    best_stock_key = max(TICKER_DB.keys(), key=lambda k: TICKER_DB[k]['div_yield'] + (50 / TICKER_DB[k]['per']))
    stock_data = TICKER_DB[best_stock_key]
    candidates.append({
        "type_label": "Acción del Mes", "asset_type": "Acciones", "sub_type": "Con dividendos",
        "name": best_stock_key.title() + " S.A.", "ticker": stock_data["ticker"],
        "desc": stock_data["racha"], "score": 4.3, "grade": "A", "ter": 0.0, "is_dist": True, "div_yield": stock_data["div_yield"]
    })

    best_fund_key = min(FUND_DB.keys(), key=lambda k: FUND_DB[k]['ter'])
    fund_data = FUND_DB[best_fund_key]
    candidates.append({
        "type_label": "Fondo del Mes", "asset_type": "Fondos indexados", "sub_type": "Acumulación",
        "name": fund_data["name"], "ticker": fund_data["ticker"],
        "desc": f"ISIN: {fund_data['ticker']} | TER ultra bajo: {fund_data['ter']}% ({fund_data['category']})",
        "score": 4.6, "grade": "A+", "ter": fund_data["ter"], "is_dist": False, "div_yield": 0.0
    })

    best_etf_key = min(ETF_DB.keys(), key=lambda k: ETF_DB[k]['ter'])
    etf_data = ETF_DB[best_etf_key]
    candidates.append({
        "type_label": "ETF del Mes", "asset_type": "ETFs", "sub_type": "Evaluación ETF",
        "name": etf_data["name"], "ticker": etf_data["ticker"],
        "desc": f"Ticker: {etf_data['ticker']} | TER: {etf_data['ter']}% ({etf_data['category']})",
        "score": 4.7, "grade": "A+", "ter": etf_data["ter"], "is_dist": False, "div_yield": 0.0
    })
    return max(candidates, key=lambda c: c["score"])

top_asset = get_best_single_monthly_recommendation()

FUND_BROKER_PROFILES = {
    "MyInvestor (Fondos Indexados / Sin custodia)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Indexa Capital (Cartera / Gestor automatizado)": {"fee_percent": 0.45, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Renta 4 (Banco tradicional / Tarifas altas)": {"fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False},
    "Personalizado (Ajustar manualmente)": {"fee_percent": 0.10, "fee_fixed": 2.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False}
}

ETF_BROKER_PROFILES = {
    "Trade Republic (1€ orden / Planes a 0€)": {"fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "Lightyear (ETFs sin comisión / Transparente)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.35, "supports_free_plans": True},
    "DEGIRO (Bajas comisiones / 1€ por operación)": {"fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False},
    "Interactive Brokers (Ideal internacional)": {"fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False},
    "XTB (0% comisiones hasta 100k€)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.20, "fx_fee_percent": 0.50, "supports_free_plans": False},
    "Trading 212 (Gratis / Fraccionadas)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.15, "fx_fee_percent": 0.15, "supports_free_plans": True},
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

with st.sidebar:
    st.header("📊 Historial de Sesión")
    num_entries = len(st.session_state.history)
    st.markdown(f"Activos / Entradas analizadas: **{num_entries}**")
    
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
# LANDING PAGE
# ----------------------------------------------------
if st.session_state.stage == 'home':
    st.markdown("### ¿Qué tipo de activo quieres evaluar?")
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

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚔️ Comparador Multiactivo Global (Fondos Acc/Dist, ETFs Reparto y Materias Primas)", use_container_width=True):
        st.session_state.stage = "comparator_view"
        st.rerun()

    st.markdown("---")

    st.markdown("### 🌟 Recomendado del Mes")
    st.markdown(f"""
    <div class="featured-card">
        <span class="featured-badge">Top Inversión Global del Mes • {top_asset['type_label']}</span>
        <span class="score-tag">⭐ {top_asset['score']}/5 ({top_asset['grade']})</span>
        <h3 style="margin: 10px 0 6px 0; color: #f8fafc;">{top_asset['name']}</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 15px;">{top_asset['desc']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_top_a, col_top_b = st.columns(2)
    with col_top_a:
        if st.button(f"🔍 Evaluar {top_asset['name']}", key="rec_eval_single_top", use_container_width=True, type="primary"):
            st.session_state.asset_type = top_asset['asset_type']
            st.session_state.sub_type = top_asset['sub_type']
            st.session_state.selected_eval_input = top_asset['ticker']
            st.session_state.stage = "analyzer"
            st.rerun()
    with col_top_b:
        if st.button("➕ Añadir a mi Cartera", key="rec_add_single_top", use_container_width=True):
            st.session_state.portfolio.append({
                "type": top_asset['asset_type'][:-1] if top_asset['asset_type'].endswith('s') else top_asset['asset_type'],
                "name": top_asset['name'], "ticker": top_asset['ticker'], "est_rent": 8.0,
                "ter": top_asset['ter'], "currency": "EUR", "is_dist": top_asset['is_dist']
            })
            guardar_en_url()
            st.success(f"¡{top_asset['name']} añadido a tu Cartera!")

# ----------------------------------------------------
# SECCIÓN COMPARADOR MULTIACTIVO GLOBAL (1 A 4) CON DISTRIBUCIÓN
# ----------------------------------------------------
elif st.session_state.stage == 'comparator_view':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()

    st.title("⚔️ Comparador Multiactivo Global (Fondos Acc/Dist & ETFs de Reparto)")
    st.markdown("Compara de 1 a 4 activos simultáneamente en tiempo real. Configura fondos de acumulación, **fondos de distribución**, **ETFs de dividendos/reparto**, oro o crudo, y analiza el impacto fiscal anual en los repartos.")

    num_compare = st.slider("Número de activos a comparar:", min_value=1, max_value=4, value=2)

    st.markdown("---")
    st.markdown("### 🔍 Configuración de Activos y Modalidad (Acumulación vs Distribución)")

    selected_assets_config = []
    cols_sel = st.columns(num_compare)

    for i in range(num_compare):
        with cols_sel[i]:
            st.markdown(f"#### Activo {i+1}")
            
            search_query_i = st.text_input(
                f"Busca activo {i+1} (ej. 'VWRL', 'dist', 'gold', 'SPYL')",
                value="VWCE.DE" if i == 0 else ("VWRL.DE" if i == 1 else "SGLD.L"),
                key=f"comp_query_{i}"
            ).strip()

            slot_options = {}
            for k, d in ETF_DB.items():
                if search_query_i.lower() in d['name'].lower() or search_query_i.lower() in d['ticker'].lower():
                    tag_d = " [Distribución]" if d['is_dist'] else " [Acumulación]"
                    slot_options[f"✨{tag_d} {d['name']} ({d['ticker']})"] = {
                        "name": d['name'], "ticker": d['ticker'], "ter": d['ter'], "type": "ETF", "is_dist": d['is_dist'], "div_yield": d['div_yield']
                    }
            for k, d in FUND_DB.items():
                if search_query_i.lower() in d['name'].lower() or search_query_i.lower() in d['ticker'].lower():
                    tag_d = " [Distribución]" if d['is_dist'] else " [Acumulación]"
                    slot_options[f"📁{tag_d} {d['name']} ({d['ticker']})"] = {
                        "name": d['name'], "ticker": d['ticker'], "ter": d['ter'], "type": "Fondo Indexado", "is_dist": d['is_dist'], "div_yield": d['div_yield']
                    }

            try:
                rt_results = yf.Search(search_query_i, max_results=12).quotes
                for item in rt_results:
                    sym = item.get('symbol')
                    sname = item.get('shortname', item.get('longname', sym))
                    ex = item.get('exchange', '')
                    if sym and sym not in [v['ticker'] for v in slot_options.values()]:
                        slot_options[f"🌐 [Mercado Real] {sname} ({sym}) [{ex}]"] = {
                            "name": sname, "ticker": sym, "ter": 0.20, "type": "ETF / Activo", "is_dist": False, "div_yield": 0.0
                        }
            except:
                pass

            if not slot_options:
                slot_options[f"⚡ [Directo] {search_query_i.upper()}"] = {
                    "name": search_query_i.upper(), "ticker": search_query_i.upper(), "ter": 0.20, "type": "Activo", "is_dist": False, "div_yield": 0.0
                }

            chosen_label = st.selectbox(f"Selecciona activo [A{i+1}]", options=list(slot_options.keys()), key=f"comp_slot_sel_{i}")
            chosen_asset = slot_options[chosen_label]

            # Si es de distribución, permitir configurar la rentabilidad por dividendo estimada
            def_div_yield = float(chosen_asset.get("div_yield", 2.0 if chosen_asset.get("is_dist") else 0.0))
            
            inv_ini_i = st.number_input(f"Inv. Inicial (€) [A{i+1}]", min_value=0.0, value=2000.0, step=500.0, key=f"comp_ini_{i}")
            app_per_i = st.number_input(f"Aportación Mensual (€) [A{i+1}]", min_value=0.0, value=150.0, step=50.0, key=f"comp_app_{i}")
            anos_i = st.slider(f"Plazo (Años) [A{i+1}]", min_value=1, max_value=40, value=20, key=f"comp_anos_{i}")
            rent_i = st.slider(f"Rentabilidad Anual (%) [A{i+1}]", min_value=1.0, max_value=25.0, value=7.5, step=0.5, key=f"comp_rent_{i}")
            
            div_yield_i = def_div_yield
            if chosen_asset["is_dist"] or st.checkbox(f"Simular como Distribución / Reparto [A{i+1}]", value=chosen_asset["is_dist"], key=f"chk_dist_{i}"):
                chosen_asset["is_dist"] = True
                div_yield_i = st.slider(f"Rentabilidad Dividendos Yield (%) [A{i+1}]", min_value=0.5, max_value=6.0, value=max(1.0, def_div_yield), step=0.1, key=f"div_y_slider_{i}")

            selected_assets_config.append({
                "name": chosen_asset["name"],
                "ticker": chosen_asset["ticker"],
                "ter": chosen_asset["ter"],
                "type": chosen_asset["type"],
                "is_dist": chosen_asset["is_dist"],
                "div_yield": div_yield_i,
                "inv_ini": inv_ini_i,
                "app_per": app_per_i,
                "anos": anos_i,
                "rent": rent_i
            })

    def calc_multisim_advanced(cfg):
        periodos = cfg["anos"] * 12
        tasa_neta_anual = max(0.0, cfg["rent"] - cfg["ter"])
        tasa_periodica = (tasa_neta_anual / 100.0) / 12.0
        
        saldo = cfg["inv_ini"]
        total_aportado = cfg["inv_ini"]
        total_dividendos_brutos = 0.0
        total_impuestos_dividendos = 0.0
        
        for p in range(1, periodos + 1):
            if p > 1:
                saldo = saldo * (1 + tasa_periodica) + cfg["app_per"]
                total_aportado += cfg["app_per"]
            else:
                saldo = saldo * (1 + tasa_periodica)
                
            # Si es de distribución, cada año (mes 12, 24, etc.) se reparte el dividendo en efectivo
            if cfg["is_dist"] and p % 12 == 0:
                div_anual_bruto = saldo * (cfg["div_yield"] / 100.0)
                div_anual_neto = div_anual_bruto * (1 - 0.19) # 19% IRPF en base del ahorro en España
                total_dividendos_brutos += div_anual_bruto
                total_impuestos_dividendos += (div_anual_bruto - div_anual_neto)
                # En distribución, el dividendo sale del fondo al bolsillo, por lo que no se acumula dentro del saldo compuesto
                saldo -= div_anual_bruto

        beneficio_bruto = max(0.0, saldo - total_aportado)
        impuestos_venta = beneficio_bruto * 0.19 if not cfg["is_dist"] else 0.0
        beneficio_neto = beneficio_bruto - impuestos_venta
        capital_liquido = total_aportado + beneficio_neto + (total_dividendos_brutos - total_impuestos_dividendos if cfg["is_dist"] else 0.0)
        
        return total_aportado, saldo, beneficio_bruto, beneficio_neto, total_dividendos_brutos, total_impuestos_dividendos, capital_liquido

    st.markdown("---")
    st.markdown("### 📊 Resultados Comparativos Detallados")

    cols_res = st.columns(num_compare)

    for i, cfg in enumerate(selected_assets_config):
        aport, saldo, b_bruto, b_neto, div_b, div_imp, liq = calc_multisim_advanced(cfg)
        modalidad_str = f"📥 Distribución (Div: {cfg['div_yield']:.1f}%)" if cfg["is_dist"] else "🔄 Acumulación"
        
        with cols_res[i]:
            st.markdown(f"""
            <div class="compare-box">
                <h3 style="color: #38bdf8; font-size: 1.1rem;">{cfg['type']}</h3>
                <h4 style="font-size: 0.95rem; min-height: 45px;">{cfg['name']}</h4>
                <p><strong>Ticker:</strong> {cfg['ticker']} | <strong>TER:</strong> {cfg['ter']}%</p>
                <p style="color: #34d399; font-weight: bold;">{modalidad_str}</p>
                <hr style="border-color: #334155;">
                <p>Plazo: <strong>{cfg['anos']} años</strong> | Rent: <strong>{cfg['rent']}%</strong></p>
                <p>Capital Invertido: <strong>{aport:,.2f} €</strong></p>
                <p>Valor Cartera Final: <strong>{saldo:,.2f} €</strong></p>
                {"<p>Dividendos Brutos Cobrados: <strong>" + f"{div_b:,.2f} €</strong></p><p>Impuestos Dividendos (19%): <strong>-{div_imp:,.2f} €</strong></p>" if cfg["is_dist"] else "<p>Beneficio Neto (Venta): <strong>" + f"{b_neto:,.2f} €</strong></p>"}
                <h3 style="color: #34d399; margin-top: 15px;">Líquido Total: {liq:,.2f} €</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"➕ Añadir a Cartera [A{i+1}]", key=f"add_comp_cartera_{i}", use_container_width=True):
                st.session_state.portfolio.append({
                    "type": cfg['type'], "name": cfg['name'], "ticker": cfg['ticker'],
                    "est_rent": cfg['rent'], "ter": cfg['ter'], "currency": "EUR", "is_dist": cfg['is_dist']
                })
                guardar_en_url()
                st.success(f"¡{cfg['name']} añadido a tu Cartera!")

# ----------------------------------------------------
# SECCIÓN SUBOPCIONES
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
            if st.button("✍️ Evaluar un Fondo", use_container_width=True):
                st.session_state.sub_type = "Acumulación"
                st.session_state.stage = "analyzer"
                st.rerun()

    elif st.session_state.asset_type == "ETFs":
        st.markdown("### Selecciona qué deseas hacer con los ETFs:")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🗺️ Explorar Tipos de ETFs (Guía)", use_container_width=True, type="primary"):
                st.session_state.sub_type = "Explorador ETFs"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c2:
            if st.button("🏆 Ver Ranking por Menor TER", use_container_width=True):
                st.session_state.sub_type = "Ranking ETFs"
                st.session_state.stage = "analyzer"
                st.rerun()
        with c3:
            if st.button("🔍 Evaluar un ETF Específico", use_container_width=True):
                st.session_state.sub_type = "Evaluación ETF"
                st.session_state.stage = "analyzer"
                st.rerun()

# ----------------------------------------------------
# SECCIÓN FAVORITOS Y CARTERA
# ----------------------------------------------------
elif st.session_state.stage == 'favorites_view':
    if st.button("← Volver al Analizador"):
        st.session_state.stage = 'analyzer' if st.session_state.asset_type else 'home'
        st.rerun()

    st.title("⭐ Mis Activos Favoritos")

    if not st.session_state.favorites:
        st.info("No tienes ningún activo guardado en favoritos todavía.")
    else:
        for idx, fav in enumerate(st.session_state.favorites):
            with st.expander(f"{idx+1}. {fav['name']} ({fav['ticker']}) - [{fav['type']}]", expanded=True):
                col_fav1, col_fav2, col_fav3, col_fav4 = st.columns([2, 1, 1, 1])
                with col_fav1:
                    st.markdown(f"**Categoría:** {fav.get('category', 'General')}")
                    st.markdown(f"**TER:** {fav.get('ter', 0.0)}%")
                with col_fav2:
                    if st.button("🔍 Evaluar", key=f"fav_eval_{idx}", use_container_width=True):
                        st.session_state.asset_type = "Acciones" if fav['type'] == "Acción" else ("Fondos indexados" if fav['type'] == "Fondo Indexado" else "ETFs")
                        st.session_state.sub_type = "Con dividendos" if fav['type'] == "Acción" else ("Acumulación" if fav['type'] == "Fondo Indexado" else "Evaluación ETF")
                        st.session_state.selected_eval_input = fav['ticker']
                        st.session_state.stage = "analyzer"
                        st.rerun()
                with col_fav3:
                    if st.button("➕ A Cartera", key=f"fav_to_port_{idx}", type="primary", use_container_width=True):
                        st.session_state.portfolio.append({
                            "type": fav['type'], "name": fav['name'], "ticker": fav['ticker'],
                            "est_rent": 7.5, "ter": fav.get('ter', 0.20), "currency": fav.get('currency', 'EUR'), "is_dist": fav.get('is_dist', False)
                        })
                        guardar_en_url()
                        st.success("¡Añadido!")
                with col_fav4:
                    if st.button("🗑️ Quitar", key=f"del_fav_{idx}", use_container_width=True):
                        st.session_state.favorites.pop(idx)
                        guardar_en_url()
                        st.rerun()

elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver al Analizador"):
        st.session_state.stage = 'analyzer' if st.session_state.asset_type else 'home'
        st.rerun()

    st.title("💼 Simulador Global de Cartera Consolidada")
    
    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía. Añade activos desde los informes o el comparador.")
    else:
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            anos_cartera = st.slider("Plazo Temporal Consolidado (Años)", min_value=1, max_value=40, value=15, key="anos_cart")
        with c_p2:
            frecuencia_cartera = st.selectbox("Frecuencia de Aportaciones", options=["Mensual", "Anual"], key="freq_cart")

        st.markdown("---")
        total_capital_bruto_acum = 0.0
        total_capital_aportado_acum = 0.0
        total_costes_acum = 0.0
        total_dividendos_brutos_acum = 0.0
        has_dividend_asset = False

        for idx, item in enumerate(st.session_state.portfolio):
            is_etf_or_stock = item['type'] in ["ETF", "Acción"]
            broker_profiles = ETF_BROKER_PROFILES if is_etf_or_stock else FUND_BROKER_PROFILES
            
            if item.get('is_dist', False) or item.get('type') == "Acción":
                has_dividend_asset = True

            currency_act = item.get('currency', 'EUR')
            
            with st.expander(f"{idx+1}. {item['name']} ({item['ticker']}) - [{item['type']}]", expanded=True):
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    sel_broker = st.selectbox(f"Bróker / Entidad", options=list(broker_profiles.keys()), key=f"p_brok_{idx}")
                with col_b2:
                    b_data = broker_profiles[sel_broker]
                    plan_sc = st.checkbox("Plan automático a 0€", value=b_data["supports_free_plans"], key=f"p_plan_{idx}")

                col_i1, col_i2, col_i3, col_i4 = st.columns([2, 2, 2, 1])
                with col_i1:
                    inv_ini = st.number_input(f"Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key=f"p_ini_{idx}")
                with col_i2:
                    app_per = st.number_input(f"Aportación Periódica (€)", min_value=0.0, value=100.0, step=50.0, key=f"p_app_{idx}")
                with col_i3:
                    rent_est = st.slider(f"Rentabilidad estimada anual (%)", min_value=0.0, max_value=20.0, value=float(item.get('est_rent', 7.5)), step=0.5, key=f"p_rent_{idx}")
                with col_i4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Quitar", key=f"del_{idx}"):
                        st.session_state.portfolio.pop(idx)
                        guardar_en_url()
                        st.rerun()

                f_pct = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_percent"]
                f_fix = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_fixed"]
                f_spr = b_data["spread_percent"]
                f_fx = 0.0 if currency_act == "EUR" else b_data["fx_fee_percent"]

                ter_val = item.get('ter', 0.20)
                periodos_ano = 12 if frecuencia_cartera == "Mensual" else 1
                tasa_neta = rent_est - ter_val
                tasa_periodica = (tasa_neta / 100.0) / periodos_ano
                tot_periodos = anos_cartera * periodos_ano

                c_broker_ini = (inv_ini * (b_data["fee_percent"] / 100.0)) + b_data["fee_fixed"]
                c_spread_ini = inv_ini * (f_spr / 100.0)
                c_fx_ini = inv_ini * (f_fx / 100.0)
                c_tot_ini = c_broker_ini + c_spread_ini + c_fx_ini

                saldo_act = max(0.0, inv_ini - c_tot_ini)
                total_aport_acum = inv_ini
                acum_b = c_broker_ini
                acum_s = c_spread_ini
                acum_f = c_fx_ini

                div_bruto_activo = 0.0
                historial_activo = []

                for p in range(1, tot_periodos + 1):
                    if p > 1:
                        cb = (app_per * (f_pct / 100.0)) + f_fix
                        cs = app_per * (f_spr / 100.0)
                        cf = app_per * (f_fx / 100.0)
                        ct = cb + cs + cf

                        import_neto = max(0.0, app_per - ct)
                        total_aport_acum += app_per
                        acum_b += cb
                        acum_s += cs
                        acum_f += cf
                        saldo_act = saldo_act * (1 + tasa_periodica) + import_neto
                    else:
                        saldo_act = saldo_act * (1 + tasa_periodica)

                    if p % periodos_ano == 0:
                        ano_act = p // periodos_ano
                        costes_tot_act = acum_b + acum_s + acum_f
                        int_brutos = saldo_act - (total_aport_acum - costes_tot_act)
                        
                        if item.get('is_dist', False) or item.get('type') == "Acción":
                            div_bruto_anual = saldo_act * 0.025
                            div_bruto_activo += div_bruto_anual

                        historial_activo.append({
                            "Año": f"Año {ano_act}",
                            "Capital Aportado Bruto (€)": round(total_aport_acum, 2),
                            "Comisiones Bróker (€)": round(acum_b, 2),
                            "Coste Spread (€)": round(acum_s, 2),
                            "Coste Divisa (€)": round(acum_f, 2),
                            "Beneficio Neto (€)": round(max(0.0, int_brutos), 2),
                            "Capital Total Neto (€)": round(saldo_act, 2)
                        })

                st.dataframe(pd.DataFrame(historial_activo), use_container_width=True)

                total_capital_bruto_acum += saldo_act
                total_capital_aportado_acum += total_aport_acum
                total_costes_acum += (acum_b + acum_s + acum_f)
                total_dividendos_brutos_acum += div_bruto_activo

        if st.session_state.portfolio:
            capital_neto_aportado = total_capital_aportado_acum - total_costes_acum
            beneficio_bruto_global = max(0.0, total_capital_bruto_acum - capital_neto_aportado)
            impuestos_globales = beneficio_bruto_global * 0.19
            beneficio_neto_global = beneficio_bruto_global - impuestos_globales
            capital_liquido_global = capital_neto_aportado + beneficio_neto_global

            st.markdown("---")
            if has_dividend_asset:
                div_neto_global = total_dividendos_brutos_acum * (1 - 0.19)
                m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
                m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
                m2.metric("Costes", f"{total_costes_acum:,.2f} €")
                m3.metric("Beneficio Bruto", f"{beneficio_bruto_global:,.2f} €")
                m4.metric("Impuestos", f"{impuestos_globales:,.2f} €")
                m5.metric("Beneficio Neto", f"{beneficio_neto_global:,.2f} €")
                m6.metric("Div. Brutos", f"{total_dividendos_brutos_acum:,.2f} €")
                m7.metric("Div. Netos", f"{div_neto_global:,.2f} €")
            else:
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
                m2.metric("Costes", f"{total_costes_acum:,.2f} €")
                m3.metric("Beneficio Bruto", f"{beneficio_bruto_global:,.2f} €")
                m4.metric("Impuestos", f"{impuestos_globales:,.2f} €")
                m5.metric("Beneficio Neto", f"{beneficio_neto_global:,.2f} €")

            st.markdown(f"""
            <div class="final-net-card">
                <div class="final-net-title">💰 Capital Total Líquido Final de tu Cartera</div>
                <div class="final-net-value">{capital_liquido_global:,.2f} €</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🗑️ Vaciar Cartera Completa"):
                st.session_state.portfolio = []
                guardar_en_url()
                st.rerun()

# ----------------------------------------------------
# SECCIÓN ANALIZADOR
# ----------------------------------------------------
elif st.session_state.stage == 'analyzer':
    if st.button("← Cambiar categoría / Volver"):
        st.session_state.stage = 'sub_options'
        st.session_state.sub_type = None
        st.session_state.selected_eval_input = ""
        st.rerun()

    def get_trend_chain_stream(hist_df):
        if hist_df is None or len(hist_df) < 2:
            return '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Lateral</div>'
        
        closes = hist_df['Close'].dropna()
        if len(closes) < 2:
            return '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Lateral</div>'

        first_p = float(closes.iloc[0])
        last_p = float(closes.iloc[-1])
        pct_change = ((last_p - first_p) / first_p) * 100

        if pct_change >= 1.0:
            return f'<div class="neon-stream-vertical"><span class="arrow-item-up st-1">▲</span><span class="arrow-item-up st-2">▲</span><span class="arrow-item-up st-3">▲</span></div><div style="font-size: 0.75rem; color: #22c55e; margin-top: 4px;">+{pct_change:.1f}%</div>'
        elif pct_change <= -1.0:
            return f'<div class="neon-stream-vertical"><span class="arrow-item-down st-1">▼</span><span class="arrow-item-down st-2">▼</span><span class="arrow-item-down st-3">▼</span></div><div style="font-size: 0.75rem; color: #ef4444; margin-top: 4px;">{pct_change:.1f}%</div>'
        else:
            return f'<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span><span class="arrow-item-side st-2">►</span><span class="arrow-item-side st-3">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">{pct_change:+.1f}%</div>'

    if st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
        st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
        ranking_data = [{"Fondo": data["name"], "ISIN": data["ticker"], "Categoría": data["category"], "TER Anual (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Antigüedad (Años)": data["age_years"]} for data in FUND_DB.values()]
        st.dataframe(pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True), use_container_width=True)
        if st.button("← Volver"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
        st.title("🏆 Ranking de ETFs (Menor TER)")
        ranking_etfs = [{"ETF": data["name"], "Ticker": data["ticker"], "Categoría": data["category"], "TER (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Réplica": data["replication"]} for data in ETF_DB.values()]
        st.dataframe(pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True), use_container_width=True)
        if st.button("← Volver"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Explorador ETFs":
        st.title("🗺️ Guía y Tipos de ETFs Disponibles")
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🌍 Globales", "💰 Dividendos", "🥇 Materias Primas", "💻 Tecnología", "⚡ Renovables", "🚀 Emergentes"])
        with tab1: st.markdown("- Diversificación global en desarrollados.")
        with tab2: st.markdown("- ETFs de reparto de dividendos (Aristócratas).")
        with tab3: st.markdown("- Oro, petróleo y materias primas.")
        with tab4: st.markdown("- Innovación e Inteligencia Artificial.")
        with tab5: st.markdown("- Transición energética y utilities.")
        with tab6: st.markdown("- Mercados en desarrollo.")
        if st.button("← Volver"):
            st.session_state.sub_type = None
            st.rerun()

    else:
        st.title(f"📈 Analizador: {st.session_state.asset_type}")
        default_input = st.session_state.selected_eval_input

        if st.session_state.asset_type == "Acciones":
            stock_options = ["-- Selecciona --"] + [f"{data.get('ticker')} ({key.title()})" for key, data in TICKER_DB.items()]
            selected_stock_option = st.selectbox("Acciones", options=stock_options)
            custom_stock_input = st.text_input("O introduce Ticker:", value=default_input).strip()
            user_input = custom_stock_input.upper() if custom_stock_input else ("" if selected_stock_option.startswith("--") else selected_stock_option.split("(")[0].strip())

        elif st.session_state.asset_type in ["Fondos indexados", "ETFs"]:
            search_query = st.text_input("Buscador de Fondos o ETFs (ej. 'dist', 'gold', 'VWRL'):", value=default_input).strip()
            user_input = search_query.upper()

        if user_input:
            st.success(f"Activo analizado: {user_input}")
