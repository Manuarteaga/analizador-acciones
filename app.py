import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json

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
    .arrow-item-up { position: absolute; left: 50%; transform: translateX(-50%); font-size: 1.6rem; font-weight: 900; color: #22c55e; animation: slideUpStream 2.6s infinite linear; }
    .arrow-item-down { position: absolute; left: 50%; transform: translateX(-50%); font-size: 1.6rem; font-weight: 900; color: #ef4444; animation: slideDownStream 2.6s infinite linear; }
    .arrow-item-side { position: absolute; top: 50%; transform: translateY(-50%); font-size: 1.5rem; font-weight: 900; color: #eab308; animation: slideRightStream 2.8s infinite linear; }
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
    .final-net-title { font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #a7f3d0; margin-bottom: 5px; font-weight: 600; }
    .final-net-value { font-size: 2.2rem; font-weight: 800; color: #ffffff; }
    .featured-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #38bdf8; border-radius: 12px; padding: 22px; margin-bottom: 10px; }
    .featured-badge { background-color: #0284c7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 8px; }
    .score-tag { background-color: #065f46; color: #34d399; padding: 3px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; float: right; }
    .compare-box { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 12px; }
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
    except: pass

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

# CATÁLOGO MAESTRO AMPLIADO (TODOS LOS FONDOS Y ETFS DISPONIBLES EN DESPLEGABLE)
MASTER_CATALOG = {
    # --- RENTA VARIABLE GLOBAL Y DESARROLLADA ---
    "📁 [Fondo] Vanguard Global Stock Index EUR Acc (Acumulación) - TER 0.18%": {
        "name": "Vanguard Global Stock Acc", "ticker": "IE00B03HD191", "ter": 0.18, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Vanguard Global Stock Index EUR Dist (Distribución) - TER 0.18%": {
        "name": "Vanguard Global Stock Dist", "ticker": "IE00B03HD209", "ter": 0.18, "type": "Fondo Indexado", "is_dist": True, "div_yield": 1.8
    },
    "📁 [Fondo] iShares Developed World Index (Acumulación) - TER 0.12%": {
        "name": "iShares Developed World Acc", "ticker": "IE00BD0NCM55", "ter": 0.12, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Fidelity MSCI World Index Fund (Acumulación) - TER 0.10%": {
        "name": "Fidelity MSCI World Acc", "ticker": "IE00BYX5NX33", "ter": 0.10, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Acumulación) - TER 0.22%": {
        "name": "Vanguard All-World Acc", "ticker": "VWCE.DE", "ter": 0.22, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Distribución) - TER 0.22%": {
        "name": "Vanguard All-World Dist", "ticker": "VWRL.DE", "ter": 0.22, "type": "ETF", "is_dist": True, "div_yield": 2.1
    },
    "🌐 [ETF] iShares Core MSCI World UCITS ETF (Acumulación) - TER 0.20%": {
        "name": "iShares Core MSCI World Acc", "ticker": "SWDA.L", "ter": 0.20, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard FTSE Developed World UCITS ETF (Acumulación) - TER 0.12%": {
        "name": "Vanguard Developed World Acc", "ticker": "VEVE.DE", "ter": 0.12, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },

    # --- S&P 500 Y EE.UU. ---
    "📁 [Fondo] Vanguard U.S. 500 Stock Index EUR Acc (Acumulación) - TER 0.10%": {
        "name": "Vanguard S&P 500 Acc", "ticker": "IE0032126645", "ter": 0.10, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Fidelity S&P 500 Index EUR P Acc (Acumulación) - TER 0.06%": {
        "name": "Fidelity S&P 500 Acc", "ticker": "IE00BYX5MX67", "ter": 0.06, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] SPDR S&P 500 UCITS ETF (Acumulación) - TER 0.03%": {
        "name": "SPDR S&P 500 Acc", "ticker": "SPYL.DE", "ter": 0.03, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] iShares S&P 500 UCITS ETF (Acumulación) - TER 0.07%": {
        "name": "iShares S&P 500 Acc", "ticker": "SXR4.DE", "ter": 0.07, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },

    # --- DIVIDENDOS Y REPARTO ---
    "🌐 [ETF] Vanguard High Dividend Yield ETF (Distribución) - TER 0.06%": {
        "name": "Vanguard High Dividend VYM", "ticker": "VYM", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 3.0
    },
    "🌐 [ETF] Schwab U.S. Dividend Equity ETF (Distribución) - TER 0.06%": {
        "name": "Schwab Dividend SCHD", "ticker": "SCHD", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 3.4
    },
    "🌐 [ETF] Vanguard Dividend Appreciation ETF (Distribución) - TER 0.06%": {
        "name": "Vanguard Dividend VIG", "ticker": "VIG", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 1.9
    },
    "🌐 [ETF] Vanguard FTSE All-World High Dividend Yield (Distribución) - TER 0.29%": {
        "name": "Vanguard All-World High Div VHYL", "ticker": "VHYL.L", "ter": 0.29, "type": "ETF", "is_dist": True, "div_yield": 3.6
    },

    # --- ORO Y MATERIAS PRIMAS ---
    "🌐 [ETF] Invesco Physical Gold ETC (Oro Físico) - TER 0.12%": {
        "name": "Invesco Physical Gold SGLD", "ticker": "SGLD.L", "ter": 0.12, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] SPDR Gold Shares (Oro Físico - GLD) - TER 0.40%": {
        "name": "SPDR Gold Shares GLD", "ticker": "GLD", "ter": 0.40, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] iShares Physical Gold ETC (Oro Físico - SGLN) - TER 0.15%": {
        "name": "iShares Physical Gold SGLN", "ticker": "SGLN.L", "ter": 0.15, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] iShares Gold Trust (Oro Físico - IAU) - TER 0.25%": {
        "name": "iShares Gold Trust IAU", "ticker": "IAU", "ter": 0.25, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] United States Oil Fund (Petróleo Crudo - USO) - TER 0.60%": {
        "name": "US Oil Fund USO", "ticker": "USO", "ter": 0.60, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Invesco DB Commodity Index Tracking Fund (Materias Primas - DBC) - TER 0.85%": {
        "name": "Invesco DB Commodity DBC", "ticker": "DBC", "ter": 0.85, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },

    # --- TECNOLOGÍA ---
    "🌐 [ETF] Invesco EQQQ NASDAQ-100 UCITS ETF (Tecnología) - TER 0.30%": {
        "name": "Invesco NASDAQ-100 EQQQ", "ticker": "EQQQ.DE", "ter": 0.30, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Invesco QQQ Trust (Nasdaq 100 - QQQ) - TER 0.20%": {
        "name": "Invesco QQQ Trust", "ticker": "QQQ", "ter": 0.20, "type": "ETF", "is_dist": False, "div_yield": 0.6
    }
}

def get_best_single_monthly_recommendation():
    return {
        "type_label": "ETF del Mes", "asset_type": "ETFs", "sub_type": "Evaluación ETF",
        "name": "SPDR S&P 500 UCITS ETF (Acc)", "ticker": "SPYL.DE",
        "desc": "Ticker: SPYL.DE | TER ultra bajo: 0.03% (Renta Variable EE.UU.)",
        "score": 4.7, "grade": "A+", "ter": 0.03, "is_dist": False
    }

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
    if st.button("⚔️ Comparador Total (Fondos vs Fondos, ETFs vs ETFs, Fondos vs ETFs)", use_container_width=True):
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
                "type": "ETF", "name": top_asset['name'], "ticker": top_asset['ticker'], "est_rent": 8.0,
                "ter": top_asset['ter'], "currency": "EUR", "is_dist": top_asset['is_dist']
            })
            guardar_en_url()
            st.success(f"¡{top_asset['name']} añadido a tu Cartera!")

    st.markdown("---")
    st.markdown("### 🧭 Asistente Interactivo: ¿Qué vehículo elegir (Fondo Indexado o ETF)?")
    with st.expander("💡 Responde a 3 preguntas rápidas para descubrir tu opción ideal", expanded=True):
        q_knowledge = st.radio("0. ¿Tienes conocimientos sobre inversiones?", ["Sí, conozco fondos, ETFs e impuestos asociados", "No, acabo de empezar"])
        q_goal = st.radio("1. ¿Qué objetivo estás buscando?", ["Largo plazo (jubilación / vivienda)", "Corto plazo (coche / reformas)", "Híbrido (largo plazo con liquidez flexible)"])
        q_moves = st.radio("2. ¿Tienes pensado hacer cambios o rebalanceos?", ["No, comprar y mantener por décadas", "Sí, quiero mover posiciones o reestructurar"])
        
        if st.button("🔮 Calcular mi recomendación ideal", type="primary"):
            st.markdown("---")
            if "Largo plazo" in q_goal and "No, comprar" in q_moves:
                st.success("🎯 **Tu mejor opción: ETFs de coste ultra bajo (Ej. SPYL.DE al 0.03% TER)** para maximizar rentabilidad a largo plazo sin tocar posiciones.")
            else:
                st.info("🎯 **Tu mejor opción: Fondos Indexados** para aprovechar el diferimiento fiscal (traspasos sin peaje en el IRPF).")

# ----------------------------------------------------
# SECCIÓN COMPARADOR TOTAL (Fondo vs Fondo, ETF vs ETF, Fondo vs ETF)
# ----------------------------------------------------
elif st.session_state.stage == 'comparator_view':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()

    st.title("⚔️ Comparador Total: Fondos y ETFs (Catálogo Completo)")
    st.markdown("""
    Compara **fondos entre sí**, **ETFs entre sí**, o **mezcla fondos con ETFs** seleccionando directamente del desplegable. Analiza el impacto del **TER**, la modalidad de acumulación frente a distribución (dividendos de oro, crudo, aristócratas) y la fiscalidad.
    """)

    num_compare = st.slider("Número de activos a comparar simultáneamente:", min_value=2, max_value=4, value=2)

    st.markdown("---")
    cols_sel = st.columns(num_compare)
    selected_assets_config = []
    catalog_keys = list(MASTER_CATALOG.keys())

    for i in range(num_compare):
        with cols_sel[i]:
            st.markdown(f"### 📋 Activo {i+1}")
            
            chosen_label = st.selectbox(
                f"Selecciona activo {i+1}",
                options=catalog_keys,
                index=i if i < len(catalog_keys) else 0,
                key=f"cat_sel_{i}"
            )
            
            asset_data = MASTER_CATALOG[chosen_label]
            st.info(f"**Tipo:** {asset_data['type']} | **TER:** {asset_data['ter']}%")

            inv_ini_i = st.number_input(f"Inv. Inicial (€) [A{i+1}]", min_value=0.0, value=3000.0, step=500.0, key=f"ini_{i}")
            app_per_i = st.number_input(f"Aportación Mensual (€) [A{i+1}]", min_value=0.0, value=200.0, step=50.0, key=f"app_{i}")
            anos_i = st.slider(f"Plazo (Años) [A{i+1}]", min_value=1, max_value=40, value=15, key=f"anos_{i}")
            rent_i = st.slider(f"Rentabilidad Bruta Est. (%) [A{i+1}]", min_value=1.0, max_value=20.0, value=7.5, step=0.5, key=f"rent_{i}")

            selected_assets_config.append({
                "type": asset_data["type"],
                "name": asset_data["name"],
                "ticker": asset_data["ticker"],
                "ter": asset_data["ter"],
                "is_dist": asset_data["is_dist"],
                "div_yield": asset_data["div_yield"],
                "inv_ini": inv_ini_i,
                "app_per": app_per_i,
                "anos": anos_i,
                "rent": rent_i
            })

    def simular_activo(cfg):
        periodos = cfg["anos"] * 12
        tasa_neta_anual = max(0.0, cfg["rent"] - cfg["ter"])
        tasa_periodica = (tasa_neta_anual / 100.0) / 12.0
        
        saldo = cfg["inv_ini"]
        total_aportado = cfg["inv_ini"]
        total_div_brutos = 0.0
        total_div_impuestos = 0.0
        
        for p in range(1, periodos + 1):
            if p > 1:
                saldo = saldo * (1 + tasa_periodica) + cfg["app_per"]
                total_aportado += cfg["app_per"]
            else:
                saldo = saldo * (1 + tasa_periodica)
                
            if cfg["is_dist"] and p % 12 == 0:
                div_anual = saldo * (cfg["div_yield"] / 100.0)
                imp_div = div_anual * 0.19
                total_div_brutos += div_anual
                total_div_impuestos += imp_div
                saldo -= div_anual

        beneficio_bruto = max(0.0, saldo - total_aportado)
        tasa_impuesto_venta = 0.0 if cfg["type"] == "Fondo Indexado" else 0.19
        impuestos_venta = beneficio_bruto * tasa_impuesto_venta
        beneficio_neto = beneficio_bruto - impuestos_venta
        capital_liquido = total_aportado + beneficio_neto + (total_div_brutos - total_div_impuestos if cfg["is_dist"] else 0.0)
        
        return total_aportado, saldo, beneficio_bruto, impuestos_venta, total_div_brutos, total_div_impuestos, capital_liquido

    st.markdown("---")
    st.markdown("## 📊 Resultados de la Comparativa Directa")

    cols_res = st.columns(num_compare)

    for i, cfg in enumerate(selected_assets_config):
        aport, saldo, b_bruto, imp_venta, div_b, div_imp, liq = simular_activo(cfg)
        
        with cols_res[i]:
            modalidad = f"📥 Distribución ({cfg['div_yield']}%)" if cfg["is_dist"] else "🔄 Acumulación"
            st.markdown(f"""
            <div class="compare-box">
                <h3 style="color: #38bdf8; font-size: 1rem;">{cfg['type']}</h3>
                <h4 style="font-size: 0.95rem; min-height: 40px;">{cfg['name']}</h4>
                <p><strong>Identificador:</strong> {cfg['ticker']}</p>
                <p><strong>TER:</strong> {cfg['ter']}% | <strong>Modalidad:</strong> {modalidad}</p>
                <hr style="border-color: #334155;">
                <p>Plazo: <strong>{cfg['anos']} años</strong> | Rent. Bruta: <strong>{cfg['rent']}%</strong></p>
                <p>Capital Invertido: <strong>{aport:,.2f} €</strong></p>
                <p>Valor Cartera Final: <strong>{saldo:,.2f} €</strong></p>
                {"<p>Dividendos Netos Cobrados: <strong>" + f"{(div_b - div_imp):,.2f} €</strong></p>" if cfg["is_dist"] else f"<p>Impuestos Venta (19%): <strong>-{imp_venta:,.2f} €</strong></p>"}
                <h3 style="color: #34d399; margin-top: 15px;">Líquido Total: {liq:,.2f} €</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"➕ Añadir a mi Cartera [A{i+1}]", key=f"add_c_{i}", use_container_width=True):
                st.session_state.portfolio.append({
                    "type": cfg['type'], "name": cfg['name'], "ticker": cfg['ticker'],
                    "est_rent": cfg['rent'], "ter": cfg['ter'], "currency": "EUR", "is_dist": cfg['is_dist']
                })
                guardar_en_url()
                st.success(f"¡{cfg['name']} añadido a Cartera!")

# ----------------------------------------------------
# SECCIÓN SUBOPCIONES (ACCIONES, FONDOS, ETFS)
# ----------------------------------------------------
elif st.session_state.stage == 'sub_options':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()

    st.title(f"Configuración para: {st.session_state.asset_type}")
    
    if st.session_state.asset_type == "Acciones":
        st.markdown("### Selecciona la modalidad:")
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
        if st.button("🔍 Evaluar Fondo Específico", use_container_width=True, type="primary"):
            st.session_state.sub_type = "Acumulación"
            st.session_state.stage = "analyzer"
            st.rerun()
    elif st.session_state.asset_type == "ETFs":
        if st.button("🔍 Evaluar ETF Específico", use_container_width=True, type="primary"):
            st.session_state.sub_type = "Evaluación ETF"
            st.session_state.stage = "analyzer"
            st.rerun()

# ----------------------------------------------------
# SECCIÓN FAVORITOS Y CARTERA CONSOLIDADA
# ----------------------------------------------------
elif st.session_state.stage == 'favorites_view':
    if st.button("← Volver"):
        reset_navigation()
        st.rerun()
    st.title("⭐ Mis Activos Favoritos")
    if not st.session_state.favorites:
        st.info("No hay favoritos guardados.")
    else:
        for idx, fav in enumerate(st.session_state.favorites):
            st.markdown(f"- **{fav['name']}** ({fav['ticker']}) - [{fav['type']}]")

elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver"):
        reset_navigation()
        st.rerun()
    st.title("💼 Cartera Consolidada")
    if not st.session_state.portfolio:
        st.info("Tu cartera está vacía. Añade activos desde el comparador o los informes.")
    else:
        for idx, item in enumerate(st.session_state.portfolio):
            st.markdown(f"- **{item['name']}** ({item['ticker']}) | Tipo: {item['type']} | TER: {item['ter']}%")

# ----------------------------------------------------
# SECCIÓN ANALIZADOR INDIVIDUAL
# ----------------------------------------------------
elif st.session_state.stage == 'analyzer':
    if st.button("← Volver"):
        st.session_state.stage = 'sub_options'
        st.rerun()
    st.title(f"📈 Analizador Individual: {st.session_state.asset_type}")
    user_input = st.text_input("Introduce Ticker o Nombre (ej. ITX.MC, SGLD.L, VWCE.DE):").strip()
    if user_input:
        try:
            stock = yf.Ticker(user_input)
            hist = stock.history(period="1mo")
            st.success(f"Datos cargados correctamente para {user_input.upper()}")
            if not hist.empty:
                st.line_chart(hist['Close'])
        except Exception as e:
            st.error(f"No se pudieron cargar datos: {e}")
