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

# CATÁLOGO MAESTRO AMPLIADO
MASTER_CATALOG = {
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
    "🌐 [ETF] Vanguard High Dividend Yield ETF (Distribución) - TER 0.06%": {
        "name": "Vanguard High Dividend VYM", "ticker": "VYM", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 3.0
    },
    "🌐 [ETF] Schwab U.S. Dividend Equity ETF (Distribución) - TER 0.06%": {
        "name": "Schwab Dividend SCHD", "ticker": "SCHD", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 3.4
    },
    "🌐 [ETF] Invesco Physical Gold ETC (Oro Físico) - TER 0.12%": {
        "name": "Invesco Physical Gold SGLD", "ticker": "SGLD.L", "ter": 0.12, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] SPDR Gold Shares (Oro Físico - GLD) - TER 0.40%": {
        "name": "SPDR Gold Shares GLD", "ticker": "GLD", "ter": 0.40, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] United States Oil Fund (Petróleo Crudo - USO) - TER 0.60%": {
        "name": "US Oil Fund USO", "ticker": "USO", "ter": 0.60, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Invesco EQQQ NASDAQ-100 UCITS ETF (Tecnología) - TER 0.30%": {
        "name": "Invesco NASDAQ-100 EQQQ", "ticker": "EQQQ.DE", "ter": 0.30, "type": "ETF", "is_dist": False, "div_yield": 0.0
    }
}

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
    st.markdown(f"Activos analizados: **{num_entries}**")
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
    if st.button("⚔️ Comparador Total (Fondos vs Fondos, ETFs vs ETFs, Fondos vs ETFs)", use_container_width=True, type="primary"):
        st.session_state.stage = "comparator_view"
        st.rerun()

# ----------------------------------------------------
# SECCIÓN COMPARADOR TOTAL
# ----------------------------------------------------
elif st.session_state.stage == 'comparator_view':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()

    st.title("⚔️ Comparador Total: Fondos y ETFs (Catálogo Completo)")
    st.markdown("Compara de 2 a 4 activos simultáneamente seleccionando directamente del desplegable.")

    num_compare = st.slider("Número de activos a comparar:", min_value=2, max_value=4, value=2)
    st.markdown("---")
    cols_sel = st.columns(num_compare)
    selected_assets_config = []
    catalog_keys = list(MASTER_CATALOG.keys())

    for i in range(num_compare):
        with cols_sel[i]:
            st.markdown(f"### 📋 Activo {i+1}")
            chosen_label = st.selectbox(f"Selecciona activo {i+1}", options=catalog_keys, index=i if i < len(catalog_keys) else 0, key=f"cat_sel_{i}")
            asset_data = MASTER_CATALOG[chosen_label]
            st.info(f"**Tipo:** {asset_data['type']} | **TER:** {asset_data['ter']}%")

            inv_ini_i = st.number_input(f"Inv. Inicial (€) [A{i+1}]", min_value=0.0, value=3000.0, step=500.0, key=f"ini_{i}")
            app_per_i = st.number_input(f"Aportación Mensual (€) [A{i+1}]", min_value=0.0, value=200.0, step=50.0, key=f"app_{i}")
            anos_i = st.slider(f"Plazo (Años) [A{i+1}]", min_value=1, max_value=40, value=15, key=f"anos_{i}")
            rent_i = st.slider(f"Rentabilidad Bruta Est. (%) [A{i+1}]", min_value=1.0, max_value=20.0, value=7.5, step=0.5, key=f"rent_{i}")

            selected_assets_config.append({
                "type": asset_data["type"], "name": asset_data["name"], "ticker": asset_data["ticker"],
                "ter": asset_data["ter"], "is_dist": asset_data["is_dist"], "div_yield": asset_data["div_yield"],
                "inv_ini": inv_ini_i, "app_per": app_per_i, "anos": anos_i, "rent": rent_i
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
# SECCIÓN SUBOPCIONES
# ----------------------------------------------------
elif st.session_state.stage == 'sub_options':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()
    st.title(f"Configuración para: {st.session_state.asset_type}")
    if st.button("🔍 Ir al Comparador Directo", type="primary", use_container_width=True):
        st.session_state.stage = "comparator_view"
        st.rerun()

# ----------------------------------------------------
# SECCIÓN FAVORITOS
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

# ----------------------------------------------------
# SECCIÓN CARTERA CONSOLIDADA (COMPLETA CON DESGLOSE DE BRÓKER Y TABLAS)
# ----------------------------------------------------
elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()

    st.title("💼 Simulador Global de Cartera Consolidada")
    
    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía. Añade activos desde el comparador total.")
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
                    sel_broker = st.selectbox(f"Bróker / Entidad [#{idx+1}]", options=list(broker_profiles.keys()), key=f"p_brok_{idx}")
                with col_b2:
                    b_data = broker_profiles[sel_broker]
                    plan_sc = st.checkbox(f"Plan automático a 0€ [#{idx+1}]", value=b_data["supports_free_plans"], key=f"p_plan_{idx}")

                col_i1, col_i2, col_i3, col_i4 = st.columns([2, 2, 2, 1])
                with col_i1:
                    inv_ini = st.number_input(f"Inversión Inicial (€) [#{idx+1}]", min_value=0.0, value=3000.0, step=500.0, key=f"p_ini_{idx}")
                with col_i2:
                    app_per = st.number_input(f"Aportación Periódica (€) [#{idx+1}]", min_value=0.0, value=200.0, step=50.0, key=f"p_app_{idx}")
                with col_i3:
                    rent_est = st.slider(f"Rentabilidad anual (%) [#{idx+1}]", min_value=0.0, max_value=20.0, value=float(item.get('est_rent', 7.5)), step=0.5, key=f"p_rent_{idx}")
                with col_i4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🗑️ Quitar [#{idx+1}]", key=f"del_{idx}"):
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
                            div_bruto_anual = saldo_act * (item.get('div_yield', 2.0) / 100.0)
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
# ANALIZADOR INDIVIDUAL
# ----------------------------------------------------
elif st.session_state.stage == 'analyzer':
    if st.button("← Volver"):
        st.session_state.stage = 'comparator_view'
        st.rerun()
    st.title("📈 Analizador")
    user_input = st.text_input("Introduce Ticker:", value=st.session_state.selected_eval_input).strip()
    if user_input:
        try:
            stock = yf.Ticker(user_input)
            hist = stock.history(period="1mo")
            st.success(f"Datos cargados para {user_input.upper()}")
            if not hist.empty:
                st.line_chart(hist['Close'])
        except Exception as e:
            st.error(f"Error: {e}")
