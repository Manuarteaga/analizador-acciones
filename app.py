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

    .converter-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        border: 1px solid #6366f1;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 25px;
    }
    .converter-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #a5b4fc;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .converter-score-tag {
        background-color: #065f46;
        color: #34d399;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 800;
        display: inline-block;
        border: 1px solid #059669;
        margin-left: 4px;
    }

    /* Estilos para barras de desglose geográfico y holdings */
    .geo-bar-container {
        display: flex;
        width: 100%;
        height: 26px;
        border-radius: 8px;
        overflow: hidden;
        margin: 12px 0 8px 0;
        border: 1px solid #334155;
    }
    .geo-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        font-size: 0.85rem;
        color: #cbd5e1;
        margin-bottom: 15px;
    }
    .geo-legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .geo-dot {
        width: 12px;
        height: 12px;
        border-radius: 3px;
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
        "name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "IE00B03HD191",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 23000, "tracking_error": 0.08, "age_years": 15, "currency": "EUR", "is_dist": False, "return_1y": 16.2, "score": 4.6,
        "desc": "Fondo indexado de referencia global que replica el índice MSCI World, invirtiendo en más de 1.500 empresas de gran y mediana capitalización en países desarrollados.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.5, "Otros": 4.0},
        "holdings": [{"name": "Apple", "weight": 4.8}, {"name": "Microsoft", "weight": 4.5}, {"name": "NVIDIA", "weight": 3.6}, {"name": "Amazon", "weight": 2.6}, {"name": "Alphabet (Google)", "weight": 2.2}]
    },
    "vanguard global stock dist": {
        "name": "Vanguard Global Stock Index Fund EUR Dist", "ticker": "IE00B03HD209",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 8400, "tracking_error": 0.08, "age_years": 14, "currency": "EUR", "is_dist": True, "return_1y": 16.0, "score": 4.5,
        "desc": "Versión de distribución del fondo global MSCI World, ideal para inversores que prefieren el cobro periódico de dividendos en cuenta.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.5, "Otros": 4.0},
        "holdings": [{"name": "Apple", "weight": 4.8}, {"name": "Microsoft", "weight": 4.5}, {"name": "NVIDIA", "weight": 3.6}, {"name": "Amazon", "weight": 2.6}, {"name": "Alphabet (Google)", "weight": 2.2}]
    },
    "ishares developed world acc": {
        "name": "iShares Developed World Index Fund (IE) D Acc EUR", "ticker": "IE00BD0NCM55",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.12, "aum": 25000, "tracking_error": 0.05, "age_years": 10, "currency": "EUR", "is_dist": False, "return_1y": 15.8, "score": 4.7,
        "desc": "Fondo indexado de BlackRock enfocado en mercados desarrollados globales con un TER muy competitivo del 0.12%.",
        "geo": {"EE. UU.": 72.0, "Japón": 6.0, "Reino Unido": 3.7, "Europa (Ex-UK)": 14.3, "Otros": 4.0},
        "holdings": [{"name": "Apple", "weight": 4.9}, {"name": "Microsoft", "weight": 4.6}, {"name": "NVIDIA", "weight": 3.5}, {"name": "Amazon", "weight": 2.5}, {"name": "Meta", "weight": 1.7}]
    },
    "fidelity msci world acc": {
        "name": "Fidelity MSCI World Index Fund EUR P Acc", "ticker": "IE00BYX5NX33",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.10, "aum": 8500, "tracking_error": 0.06, "age_years": 8, "currency": "EUR", "is_dist": False, "return_1y": 15.9, "score": 4.7,
        "desc": "Uno de los fondos globales más económicos del mercado europeo para replicar el índice MSCI World.",
        "geo": {"EE. UU.": 71.8, "Japón": 6.1, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.4, "Otros": 3.9},
        "holdings": [{"name": "Apple", "weight": 4.8}, {"name": "Microsoft", "weight": 4.5}, {"name": "NVIDIA", "weight": 3.6}, {"name": "Amazon", "weight": 2.6}, {"name": "Alphabet", "weight": 2.2}]
    },
    "vanguard sp 500 acc": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc", "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 17000, "tracking_error": 0.03, "age_years": 22, "currency": "EUR", "is_dist": False, "return_1y": 22.4, "score": 4.8,
        "desc": "Fondo indexado histórico que replica el comportamiento de las 500 empresas más grandes de Estados Unidos.",
        "geo": {"EE. UU.": 100.0},
        "holdings": [{"name": "Apple", "weight": 6.5}, {"name": "Microsoft", "weight": 6.2}, {"name": "NVIDIA", "weight": 5.0}, {"name": "Amazon", "weight": 3.7}, {"name": "Alphabet", "weight": 3.1}]
    },
    "vanguard emerging markets acc": {
        "name": "Vanguard Emerging Markets Stock Index Fund EUR Acc", "ticker": "IE0031786696",
        "category": "Mercados Emergentes", "ter": 0.23, "aum": 11200, "tracking_error": 0.12, "age_years": 16, "currency": "EUR", "is_dist": False, "return_1y": 9.4, "score": 4.1,
        "desc": "Exposición diversificada a economías en desarrollo como China, India, Taiwán, Brasil y Corea del Sur.",
        "geo": {"China": 27.5, "India": 18.2, "Taiwán": 17.8, "Corea del Sur": 12.5, "Brasil": 5.0, "Otros": 19.0},
        "holdings": [{"name": "Taiwan Semiconductor (TSMC)", "weight": 8.5}, {"name": "Tencent Holdings", "weight": 4.2}, {"name": "Alibaba Group", "weight": 2.8}, {"name": "Samsung Electronics", "weight": 3.5}, {"name": "Reliance Industries", "weight": 1.5}]
    }
}

ETF_DB = {
    "vwce.de": {
        "name": "Vanguard FTSE All-World UCITS ETF [Acumulación]", "ticker": "VWCE.DE",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.22, "aum": 15000,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 7, "is_dist": False, "return_1y": 16.0, "score": 4.8,
        "desc": "Incluye tanto países desarrollados como mercados emergentes (más de 3.700 valores en todo el mundo).",
        "geo": {"EE. UU.": 62.5, "Mercados Emergentes": 10.5, "Japón": 5.8, "Europa": 15.2, "Otros": 6.0},
        "holdings": [{"name": "Apple", "weight": 4.2}, {"name": "Microsoft", "weight": 4.0}, {"name": "NVIDIA", "weight": 3.2}, {"name": "Amazon", "weight": 2.3}, {"name": "Alphabet", "weight": 1.9}]
    },
    "swda.l": {
        "name": "iShares Core MSCI World UCITS ETF [Acumulación]", "ticker": "SWDA.L",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.20, "aum": 68000,
        "replication": "Física (Muestreo)", "te": 0.03, "currency": "EUR", "age_years": 14, "is_dist": False, "return_1y": 15.7, "score": 4.8,
        "desc": "El ETF de mercados desarrollados globales más líquido y con mayor patrimonio en Europa.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.5, "Otros": 4.0},
        "holdings": [{"name": "Apple", "weight": 4.8}, {"name": "Microsoft", "weight": 4.5}, {"name": "NVIDIA", "weight": 3.6}, {"name": "Amazon", "weight": 2.6}, {"name": "Alphabet", "weight": 2.2}]
    },
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000,
        "replication": "Física (Completa)", "te": 0.01, "currency": "EUR", "age_years": 3, "is_dist": False, "return_1y": 22.3, "score": 4.9,
        "desc": "El ETF del S&P 500 con el coste operativo más bajo de Europa (TER del 0.03%).",
        "geo": {"EE. UU.": 100.0},
        "holdings": [{"name": "Apple", "weight": 6.5}, {"name": "Microsoft", "weight": 6.2}, {"name": "NVIDIA", "weight": 5.0}, {"name": "Amazon", "weight": 3.7}, {"name": "Alphabet", "weight": 3.1}]
    },
    "exus.de": {
        "name": "iShares MSCI World ex USA UCITS ETF", "ticker": "EXUS.DE",
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.20, "aum": 3400,
        "replication": "Física", "te": 0.04, "currency": "EUR", "age_years": 8, "is_dist": False, "return_1y": 11.4, "score": 4.6,
        "desc": "Ideal para complementar carteras: invierte en países desarrollados **excluyendo totalmente Estados Unidos** (Europa, Japón, Canadá, Australia).",
        "geo": {"Japón": 22.0, "Reino Unido": 13.5, "Europa (Ex-UK)": 51.0, "Canadá": 8.0, "Otros": 5.5},
        "holdings": [{"name": "ASML Holding", "weight": 2.2}, {"name": "Nestlé", "weight": 1.8}, {"name": "Toyota Motor", "weight": 1.6}, {"name": "Shell", "weight": 1.5}, {"name": "AstraZeneca", "weight": 1.4}]
    },
    "emim.l": {
        "name": "iShares Core MSCI Emerging Markets IMI UCITS ETF [Acumulación]", "ticker": "EMIM.L",
        "category": "Mercados Emergentes", "ter": 0.18, "aum": 18000,
        "replication": "Física (Muestreo)", "te": 0.06, "currency": "EUR", "age_years": 10, "is_dist": False, "return_1y": 9.8, "score": 4.4,
        "desc": "Exposición completa a más de 3.000 valores de países emergentes de gran, mediana y pequeña capitalización.",
        "geo": {"China": 26.0, "India": 19.5, "Taiwán": 17.5, "Corea del Sur": 12.0, "Otros": 25.0},
        "holdings": [{"name": "Taiwan Semiconductor (TSMC)", "weight": 8.8}, {"name": "Tencent Holdings", "weight": 4.4}, {"name": "Alibaba Group", "weight": 2.9}, {"name": "Samsung Electronics", "weight": 3.6}, {"name": "Reliance Industries", "weight": 1.6}]
    }
}

def render_geo_breakdown(geo_dict):
    st.markdown("**🗺️ Desglose Geográfico Estimado:**")
    colors = {"EE. UU.": "#3b82f6", "China": "#ef4444", "India": "#f59e0b", "Taiwán": "#10b981", "Corea del Sur": "#8b5cf6", "Japón": "#ec4899", "Reino Unido": "#6366f1", "Europa": "#14b8a6", "Europa (Ex-UK)": "#06b6d4", "Canadá": "#84cc16", "Mercados Emergentes": "#f97316", "Brasil": "#eab308", "Otros": "#64748b"}
    
    bar_html = '<div class="geo-bar-container">'
    legend_html = '<div class="geo-legend">'
    
    for country, pct in geo_dict.items():
        color = colors.get(country, "#94a3b8")
        bar_html += f'<div style="width: {pct}%; background-color: {color}; height: 100%;" title="{country}: {pct}%"></div>'
        legend_html += f'<div class="geo-legend-item"><div class="geo-dot" style="background-color: {color};"></div><span>{country} ({pct}%)</span></div>'
    
    bar_html += '</div>'
    legend_html += '</div>'
    
    st.markdown(bar_html + legend_html, unsafe_allow_html=True)

def render_holdings_breakdown(holdings_list):
    st.markdown("**🏢 Principales Empresas Participadas (*Top Holdings*) y su Peso:**")
    st.caption("ℹ️ El porcentaje representa qué proporción del patrimonio total del fondo o ETF está invertido en esa compañía específica.")
    
    colors_holdings = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
    
    bar_html = '<div class="geo-bar-container">'
    legend_html = '<div class="geo-legend">'
    
    for idx, item in enumerate(holdings_list):
        name = item["name"]
        weight = item["weight"]
        color = colors_holdings[idx % len(colors_holdings)]
        bar_html += f'<div style="width: {weight * 5}%; background-color: {color}; height: 100%;" title="{name}: {weight}%"></div>'
        legend_html += f'<div class="geo-legend-item"><div class="geo-dot" style="background-color: {color};"></div><span>{name} ({weight}%)</span></div>'
    
    bar_html += '</div>'
    legend_html += '</div>'
    
    st.markdown(bar_html + legend_html, unsafe_allow_html=True)

def get_best_single_monthly_recommendation():
    candidates = []
    best_stock_key = max(TICKER_DB.keys(), key=lambda k: TICKER_DB[k]['div_yield'] + (50 / TICKER_DB[k]['per']))
    stock_data = TICKER_DB[best_stock_key]
    candidates.append({
        "type_label": "Acción del Mes", "asset_type": "Acciones", "sub_type": "Con dividendos",
        "name": best_stock_key.title() + " S.A.", "ticker": stock_data["ticker"],
        "desc": stock_data["racha"], "score": 4.3, "grade": "A", "ter": 0.0, "is_dist": True
    })

    best_fund_key = min(FUND_DB.keys(), key=lambda k: FUND_DB[k]['ter'])
    fund_data = FUND_DB[best_fund_key]
    candidates.append({
        "type_label": "Fondo del Mes", "asset_type": "Fondos indexados", "sub_type": "Acumulación",
        "name": fund_data["name"], "ticker": fund_data["ticker"],
        "desc": f"ISIN: {fund_data['ticker']} | TER ultra bajo: {fund_data['ter']}% ({fund_data['category']})",
        "score": 4.6, "grade": "A+", "ter": fund_data["ter"], "is_dist": False
    })

    best_etf_key = min(ETF_DB.keys(), key=lambda k: ETF_DB[k]['ter'])
    etf_data = ETF_DB[best_etf_key]
    candidates.append({
        "type_label": "ETF del Mes", "asset_type": "ETFs", "sub_type": "Evaluación ETF",
        "name": etf_data["name"], "ticker": etf_data["ticker"],
        "desc": f"Ticker: {etf_data['ticker']} | TER: {etf_data['ter']}% ({etf_data['category']})",
        "score": 4.7, "grade": "A+", "ter": etf_data["ter"], "is_dist": False
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

    st.markdown("---")

    st.markdown("### 🌟 Recomendado del Mes")
    st.markdown(f"""
    <div class="featured-card">
        <span class="featured-badge">Top Inversión Global del Mes • {top_asset['type_label']}</span>
        <span style="background-color: #065f46; color: #34d399; padding: 3px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; float: right;">⭐ {top_asset['score']}/5 ({top_asset['grade']})</span>
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
                "ter": top_asset['ter'], "currency": "EUR", "is_dist": top_asset['is_dist'],
                "category": "Renta Variable Global (MSCI World)"
            })
            guardar_en_url()
            st.success(f"¡{top_asset['name']} añadido a tu Cartera!")

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
# SECCIÓN FAVORITOS
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
                            "est_rent": 7.5, "ter": fav.get('ter', 0.20), "currency": fav.get('currency', 'EUR'),
                            "is_dist": fav.get('is_dist', False), "category": fav.get('category', 'General')
                        })
                        guardar_en_url()
                        st.success("¡Añadido a la Cartera!")
                with col_fav4:
                    if st.button("🗑️ Quitar", key=f"del_fav_{idx}", use_container_width=True):
                        st.session_state.favorites.pop(idx)
                        guardar_en_url()
                        st.rerun()

# ----------------------------------------------------
# SECCIÓN CARTERA CONSOLIDADA CON AUDITORÍA DE SOLAPAMIENTO
# ----------------------------------------------------
elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver al Analizador"):
        st.session_state.stage = 'analyzer' if st.session_state.asset_type else 'home'
        st.rerun()

    st.title("💼 Simulador Global de Cartera Consolidada")
    
    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía. Añade fondos o ETFs desde sus informes para simularlos y detectar solapamientos geográficos.")
    else:
        categories_in_portfolio = [item.get('category', '') for item in st.session_state.portfolio]
        has_msci_world = any("Global" in cat for cat in categories_in_portfolio)
        has_sp500 = any("EE.UU. (S&P 500)" in cat for cat in categories_in_portfolio)

        if has_msci_world and has_sp500:
            st.warning("""
            ⚠️ **¡Alerta de Solapamiento Geográfico Detectado!**  
            Has incluido en tu cartera un fondo/ETF de **Renta Variable Global (MSCI World)** y al mismo tiempo un fondo/ETF de **EE. UU. (S&P 500)**.  
            * **El problema:** El índice MSCI World ya invierte un **70% de su capital en EE. UU.** Al sumar el S&P 500, estarás sobreponderando EE. UU. por encima del 85-90%, duplicando posiciones en los mismos gigantes tecnológicos (Apple, Microsoft, Nvidia, etc.).
            * **💡 Alternativa recomendada:** Para diversificar correctamente sin repetir EE. UU., te sugerimos sustituir el S&P 500 o equilibrar tu cartera añadiendo un ETF de **Países Desarrollados Ex-EE. UU.** (como *iShares MSCI World ex USA - EXUS.DE*) para capturar Europa, Japón y Pacífico sin solapar tu fondo global.
            """)
        elif has_msci_world and len(categories_in_portfolio) > 1 and not has_sp500:
            st.success("✅ **Buena diversificación:** Tu cartera combina activos globales sin duplicidades críticas en EE. UU.")

        st.markdown("Configura el plazo, la frecuencia y el bróker de cada activo para obtener el desglose anual detallado y el rendimiento neto final:")
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            anos_cartera = st.slider("Plazo Temporal Consolidado (Años)", min_value=1, max_value=40, value=15, key="anos_cart")
        with c_p2:
            frecuencia_cartera = st.selectbox("Frecuencia de Aportaciones", options=["Mensual", "Anual"], key="freq_cart")

        st.markdown("---")
        st.markdown("### 📋 Desglose y Configuración por Activo")

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
                    plan_sc = st.checkbox("Plan de aportación automática a 0€", value=b_data["supports_free_plans"], key=f"p_plan_{idx}")

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
                            "Coste Cambio Divisa (€)": round(acum_f, 2),
                            "Beneficio Neto (€)": round(max(0.0, int_brutos), 2),
                            "Capital Total Neto (€)": round(saldo_act, 2)
                        })

                df_act = pd.DataFrame(historial_activo)
                st.markdown("##### 📊 Desglose de crecimiento anual para este activo:")
                st.dataframe(df_act, use_container_width=True)

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
            st.markdown("### 📊 Proyección Total de la Cartera Consolidada")

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
            m2.metric("Costes Bróker", f"{total_costes_acum:,.2f} €")
            m3.metric("Beneficio Bruto", f"{beneficio_bruto_global:,.2f} €")
            m4.metric("Impuestos (19%)", f"{impuestos_globales:,.2f} €")
            m5.metric("Beneficio Neto", f"{beneficio_neto_global:,.2f} €")

            st.markdown(f"""
            <div class="final-net-card">
                <div class="final-net-title">💰 Capital Total Líquido Final de tu Cartera (Tras Impuestos)</div>
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

    def render_asset_converter(current_category, current_ticker):
        st.markdown(f"""
        <div class="converter-card">
            <div class="converter-title">🔄 Convertidor y Buscador de Alternativas Equivalentes</div>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 12px;">
                Alternativas exactas para este índice junto con su nota de calidad destacada:
            </p>
        </div>
        """, unsafe_allow_html=True)

        equi_funds = [f for f in FUND_DB.values() if f['category'] == current_category and f['ticker'] != current_ticker]
        equi_etfs = [e for e in ETF_DB.values() if e['category'] == current_category and e['ticker'] != current_ticker]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 📁 Fondos Indexados Equivalentes")
            if equi_funds:
                for item in equi_funds:
                    st.markdown(f"• **{item['name']}**")
                    st.markdown(f"  ISIN: `{item['ticker']}` | TER: **{item['ter']}%** <span class='converter-score-tag'>⭐ {item.get('score', 4.3)}/5</span>", unsafe_allow_html=True)
            else:
                st.caption("No hay más fondos en esta categoría.")
        with c2:
            st.markdown("##### 🌐 ETFs Equivalentes")
            if equi_etfs:
                for item in equi_etfs:
                    st.markdown(f"• **{item['name']}**")
                    st.markdown(f"  Ticker: `{item['ticker']}` | TER: **{item['ter']}%** <span class='converter-score-tag'>⭐ {item.get('score', 4.5)}/5</span>", unsafe_allow_html=True)
            else:
                st.caption("No hay ETFs directos en esta categoría.")

    if st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
        st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
        ranking_data = [{"Fondo": data["name"], "ISIN": data["ticker"], "Categoría": data["category"], "Nota (⭐)": f"{data.get('score', 4.3)}/5", "TER Anual (%)": data["ter"]} for data in FUND_DB.values()]
        st.dataframe(pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True), use_container_width=True)
        if st.button("← Volver al menú de fondos"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
        st.title("🏆 Ranking de ETFs (Menor TER)")
        ranking_etfs = [{"ETF": data["name"], "Ticker": data["ticker"], "Categoría": data["category"], "Nota (⭐)": f"{data.get('score', 4.5)}/5", "TER (%)": data["ter"]} for data in ETF_DB.values()]
        st.dataframe(pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True), use_container_width=True)
        if st.button("← Volver al menú de ETFs"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Explorador ETFs":
        st.title("🗺️ Guía y Tipos de ETFs Disponibles")
        st.markdown("- **Globales:** Diversificación total en países desarrollados y emergentes.")
        st.markdown("- **Ex-EE. UU. (Desarrollados):** Clave para evitar la sobrediversificación si ya tienes el S&P 500.")
        if st.button("← Volver"):
            st.session_state.sub_type = None
            st.rerun()

    else:
        st.title(f"📈 Analizador: {st.session_state.asset_type} ({st.session_state.sub_type})")
        default_input = st.session_state.selected_eval_input

        if st.session_state.asset_type == "Fondos indexados":
            fund_options = ["-- Selecciona un fondo indexado --"] + [f"{data['name']} (ISIN: {data['ticker']})" for data in FUND_DB.values()]
            sel_idx = 0
            if default_input:
                for idx, opt in enumerate(fund_options):
                    if default_input.upper() in opt.upper(): sel_idx = idx; break
            chosen = st.selectbox("Biblioteca de Fondos", options=fund_options, index=sel_idx)
            user_input = chosen.split("ISIN: ")[1].split(")")[0].strip() if not chosen.startswith("--") else ""
        elif st.session_state.asset_type == "ETFs":
            etf_options = ["-- Selecciona un ETF --"] + [f"{data['name']} (Ticker: {data['ticker']})" for data in ETF_DB.values()]
            sel_idx_e = 0
            if default_input:
                for idx, opt in enumerate(etf_options):
                    if default_input.upper() in opt.upper(): sel_idx_e = idx; break
            chosen_etf = st.selectbox("Biblioteca de ETFs", options=etf_options, index=sel_idx_e)
            user_input = chosen_etf.split("Ticker: ")[1].split(")")[0].strip() if not chosen_etf.startswith("--") else ""
        else:
            user_input = st.text_input("Introduce Ticker (ej. AAPL, ITX.MC):", value=default_input).strip().upper()

        if not user_input:
            st.info("👆 Selecciona un activo para ver su ficha técnica, desglose geográfico, principales empresas y alternativas.")
        else:
            if st.session_state.asset_type == "Fondos indexados":
                matched = next((d for d in FUND_DB.values() if d["ticker"].upper() == user_input.upper()), None)
            elif st.session_state.asset_type == "ETFs":
                matched = next((d for d in ETF_DB.values() if d["ticker"].upper() == user_input.upper()), None)
            else:
                matched = None

            if matched:
                st.subheader(f"📊 Ficha Técnica: {matched['name']}")
                st.markdown(f"**Descripción / Qué incluye:** {matched.get('desc', 'Sin descripción detallada.')}")
                
                if "geo" in matched:
                    render_geo_breakdown(matched["geo"])
                
                if "holdings" in matched:
                    render_holdings_breakdown(matched["holdings"])

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⭐ Añadir a Favoritos", use_container_width=True):
                        st.session_state.favorites.append({"type": st.session_state.asset_type[:-1], "name": matched['name'], "ticker": matched['ticker'], "ter": matched['ter'], "currency": matched['currency'], "category": matched['category']})
                        guardar_en_url()
                        st.success("¡Añadido a Favoritos!")
                with col2:
                    if st.button("➕ Añadir a Cartera", type="primary", use_container_width=True):
                        st.session_state.portfolio.append({"type": "Fondo Indexado" if st.session_state.asset_type=="Fondos indexados" else "ETF", "name": matched['name'], "ticker": matched['ticker'], "est_rent": 7.5, "ter": matched['ter'], "currency": matched['currency'], "is_dist": matched.get('is_dist', False), "category": matched['category']})
                        guardar_en_url()
                        st.success("¡Añadido a la Cartera!")

                render_asset_converter(matched['category'], matched['ticker'])
            else:
                st.info(f"Mostrando datos estándar para el activo {user_input}.")
