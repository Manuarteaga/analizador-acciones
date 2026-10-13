import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json
import urllib.parse

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")
page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"  # 👈 AÑADIR AQUÍ TAMBIÉN
)
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

    /* Estilos para barras de desglose visual (Geográfico y Empresas) */
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
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Alphabet Inc. (Google)": 2.3, "Meta Platforms Inc.": 1.6, "Eli Lilly & Co.": 1.0, "Resto del Fondo": 78.2}
    },
    "vanguard global stock dist": {
        "name": "Vanguard Global Stock Index Fund EUR Dist", "ticker": "IE00B03HD209",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 8400, "tracking_error": 0.08, "age_years": 14, "currency": "EUR", "is_dist": True, "return_1y": 16.0, "score": 4.5,
        "desc": "Versión de distribución del fondo global MSCI World, ideal para inversores que prefieren el cobro periódico de dividendos en cuenta.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.5, "Otros": 4.0},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Alphabet Inc. (Google)": 2.3, "Meta Platforms Inc.": 1.6, "Eli Lilly & Co.": 1.0, "Resto del Fondo": 78.2}
    },
    "ishares developed world acc": {
        "name": "iShares Developed World Index Fund (IE) D Acc EUR", "ticker": "IE00BD0NCM55",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.12, "aum": 25000, "tracking_error": 0.05, "age_years": 10, "currency": "EUR", "is_dist": False, "return_1y": 15.8, "score": 4.7,
        "desc": "Fondo indexado de BlackRock enfocado en mercados desarrollados globales con un TER muy competitivo del 0.12%.",
        "geo": {"EE. UU.": 72.0, "Japón": 6.0, "Reino Unido": 3.7, "Europa (Ex-UK)": 14.3, "Otros": 4.0},
        "holdings": {"Apple Inc.": 5.3, "Microsoft Corp.": 4.9, "NVIDIA Corp.": 4.2, "Amazon.com Inc.": 2.5, "Alphabet Inc.": 2.2, "Meta Platforms": 1.5, "Tesla Inc.": 1.1, "Resto del Fondo": 78.3}
    },
    "fidelity msci world acc": {
        "name": "Fidelity MSCI World Index Fund EUR P Acc", "ticker": "IE00BYX5NX33",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.10, "aum": 8500, "tracking_error": 0.06, "age_years": 8, "currency": "EUR", "is_dist": False, "return_1y": 15.9, "score": 4.7,
        "desc": "Uno de los fondos globales más económicos del mercado europeo para replicar el índice MSCI World.",
        "geo": {"EE. UU.": 71.8, "Japón": 6.1, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.4, "Otros": 3.9},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Alphabet Inc.": 2.3, "Meta Platforms": 1.6, "Resto del Fondo": 79.2}
    },
    "vanguard sp 500 acc": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc", "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 17000, "tracking_error": 0.03, "age_years": 22, "currency": "EUR", "is_dist": False, "return_1y": 22.4, "score": 4.8,
        "desc": "Fondo indexado histórico que replica el comportamiento de las 500 empresas más grandes de Estados Unidos.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Meta Platforms": 2.4, "Berkshire Hathaway": 1.7, "Eli Lilly": 1.5, "Resto del Fondo": 67.6}
    },
    "vanguard sp 500 dist": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Dist", "ticker": "IE0032126868",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 5100, "tracking_error": 0.03, "age_years": 20, "currency": "EUR", "is_dist": True, "return_1y": 22.2, "score": 4.7,
        "desc": "Versión de distribución del fondo S&P 500 de Vanguard.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Meta Platforms": 2.4, "Berkshire Hathaway": 1.7, "Resto del Fondo": 69.1}
    },
    "fidelity us index acc": {
        "name": "Fidelity S&P 500 Index Fund EUR P Acc", "ticker": "IE00BYX5MX67",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.06, "aum": 6200, "tracking_error": 0.03, "age_years": 7, "currency": "EUR", "is_dist": False, "return_1y": 22.5, "score": 4.9,
        "desc": "Fondo indexado al S&P 500 con un coste bajísimo del 0.06%.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Meta Platforms": 2.4, "Resto del Fondo": 70.8}
    },
    "ishares us technology acc": {
        "name": "iShares US Technology Index Fund EUR Acc", "ticker": "IE00B1W33F31",
        "category": "Tecnología", "ter": 0.20, "aum": 4300, "tracking_error": 0.09, "age_years": 11, "currency": "EUR", "is_dist": False, "return_1y": 28.5, "score": 4.3,
        "desc": "Fondo sectorial enfocado en gigantes tecnológicos de EE. UU.",
        "geo": {"EE. UU.": 98.0, "Otros": 2.0},
        "holdings": {"Apple Inc.": 16.5, "Microsoft Corp.": 15.8, "NVIDIA Corp.": 14.2, "Broadcom Inc.": 4.5, "Adobe Inc.": 2.2, "Salesforce Inc.": 2.0, "Resto del Fondo": 44.8}
    },
    "vanguard emerging markets acc": {
        "name": "Vanguard Emerging Markets Stock Index Fund EUR Acc", "ticker": "IE0031786696",
        "category": "Mercados Emergentes", "ter": 0.23, "aum": 11200, "tracking_error": 0.12, "age_years": 16, "currency": "EUR", "is_dist": False, "return_1y": 9.4, "score": 4.1,
        "desc": "Exposición diversificada a economías en desarrollo como China, India, Taiwán, Brasil y Corea del Sur.",
        "geo": {"China": 27.5, "India": 18.2, "Taiwán": 17.8, "Corea del Sur": 12.5, "Brasil": 5.0, "Otros": 19.0},
        "holdings": {"Taiwan Semiconductor (TSMC)": 8.5, "Tencent Holdings": 4.2, "Alibaba Group": 2.8, "Samsung Electronics": 3.9, "Reliance Industries": 1.8, "Meituan": 1.1, "Resto del Fondo": 77.7}
    },
    "vanguard emerging markets dist": {
        "name": "Vanguard Emerging Markets Stock Index Fund EUR Dist", "ticker": "IE0031786142",
        "category": "Mercados Emergentes", "ter": 0.23, "aum": 3200, "tracking_error": 0.12, "age_years": 15, "currency": "EUR", "is_dist": True, "return_1y": 9.2, "score": 4.0,
        "desc": "Versión de distribución para mercados emergentes.",
        "geo": {"China": 27.5, "India": 18.2, "Taiwán": 17.8, "Corea del Sur": 12.5, "Brasil": 5.0, "Otros": 19.0},
        "holdings": {"Taiwan Semiconductor (TSMC)": 8.5, "Tencent Holdings": 4.2, "Alibaba Group": 2.8, "Samsung Electronics": 3.9, "Resto del Fondo": 80.6}
    },
    "vanguard european stock acc": {
        "name": "Vanguard European Stock Index Fund EUR Acc", "ticker": "IE0007987690",
        "category": "Renta Variable Europa", "ter": 0.12, "aum": 7800, "tracking_error": 0.06, "age_years": 18, "currency": "EUR", "is_dist": False, "return_1y": 12.1, "score": 4.4,
        "desc": "Fondo indexado enfocado en el mercado europeo (Reino Unido, Francia, Suiza, Alemania, etc.).",
        "geo": {"Reino Unido": 23.0, "Francia": 17.5, "Suiza": 14.5, "Alemania": 13.5, "Otros": 31.5},
        "holdings": {"ASML Holding NV": 3.5, "Nestlé SA": 3.2, "LVMH Moët Hennessy": 2.8, "Novartis AG": 2.6, "Shell PLC": 2.5, "SAP SE": 2.2, "TotalEnergies": 1.9, "Resto del Fondo": 81.3}
    },
    "vanguard global bond index acc": {
        "name": "Vanguard Global Bond Index Fund EUR Hedged Acc", "ticker": "IE00B1FT8033",
        "category": "Renta Fija / Bonos Globales", "ter": 0.15, "aum": 19500, "tracking_error": 0.04, "age_years": 13, "currency": "EUR", "is_dist": False, "return_1y": 4.2, "score": 4.2,
        "desc": "Cartera diversificada de bonos globales cubiertos a euros.",
        "geo": {"EE. UU.": 45.0, "Europa": 30.0, "Japón": 12.0, "Otros": 13.0},
        "holdings": {"US Treasury Bond 3.8%": 4.5, "Japanese Government Bond 0.5%": 3.2, "German Bund 2.4%": 3.0, "UK Treasury Gilt 4.2%": 2.8, "Resto del Fondo": 86.5}
    }
}

ETF_DB = {
    "vwce.de": {
        "name": "Vanguard FTSE All-World UCITS ETF [Acumulación]", "ticker": "VWCE.DE",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.22, "aum": 15000,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 7, "is_dist": False, "return_1y": 16.0, "score": 4.8,
        "desc": "Incluye tanto países desarrollados como mercados emergentes (más de 3.700 valores en todo el mundo).",
        "geo": {"EE. UU.": 62.5, "Mercados Emergentes": 10.5, "Japón": 5.8, "Europa": 15.2, "Otros": 6.0},
        "holdings": {"Apple Inc.": 4.5, "Microsoft Corp.": 4.2, "NVIDIA Corp.": 3.8, "Amazon.com Inc.": 2.3, "Alphabet Inc.": 2.0, "Meta Platforms": 1.4, "Resto del ETF": 81.8}
    },
    "vwrl.as": {
        "name": "Vanguard FTSE All-World UCITS ETF [Distribución]", "ticker": "VWRL.AS",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.22, "aum": 11800,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 12, "is_dist": True, "return_1y": 15.8, "score": 4.7,
        "desc": "Versión de distribución del FTSE All-World.",
        "geo": {"EE. UU.": 62.5, "Mercados Emergentes": 10.5, "Japón": 5.8, "Europa": 15.2, "Otros": 6.0},
        "holdings": {"Apple Inc.": 4.5, "Microsoft Corp.": 4.2, "NVIDIA Corp.": 3.8, "Amazon.com Inc.": 2.3, "Alphabet Inc.": 2.0, "Resto del ETF": 83.2}
    },
    "swda.l": {
        "name": "iShares Core MSCI World UCITS ETF [Acumulación]", "ticker": "SWDA.L",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.20, "aum": 68000,
        "replication": "Física (Muestreo)", "te": 0.03, "currency": "EUR", "age_years": 14, "is_dist": False, "return_1y": 15.7, "score": 4.8,
        "desc": "El ETF de mercados desarrollados globales más líquido y con mayor patrimonio en Europa.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.5, "Otros": 4.0},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Alphabet Inc.": 2.3, "Resto del ETF": 80.8}
    },
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000,
        "replication": "Física (Completa)", "te": 0.01, "currency": "EUR", "age_years": 3, "is_dist": False, "return_1y": 22.3, "score": 4.9,
        "desc": "El ETF del S&P 500 con el coste operativo más bajo de Europa (TER del 0.03%).",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Resto del ETF": 73.2}
    },
    "vusa.as": {
        "name": "Vanguard S&P 500 UCITS ETF [Distribución]", "ticker": "VUSA.AS",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.07, "aum": 34000,
        "replication": "Física (Completa)", "te": 0.02, "currency": "EUR", "age_years": 12, "is_dist": True, "return_1y": 22.1, "score": 4.8,
        "desc": "ETF de distribución que replica el S&P 500.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Resto del ETF": 73.2}
    },
    "exus.de": {
        "name": "iShares MSCI World ex USA UCITS ETF", "ticker": "EXUS.DE",
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.20, "aum": 3400,
        "replication": "Física", "te": 0.04, "currency": "EUR", "age_years": 8, "is_dist": False, "return_1y": 11.4, "score": 4.6,
        "desc": "Ideal para complementar carteras: invierte en países desarrollados **excluyendo totalmente Estados Unidos** (Europa, Japón, Canadá, Australia).",
        "geo": {"Japón": 22.0, "Reino Unido": 13.5, "Europa (Ex-UK)": 51.0, "Canadá": 8.0, "Otros": 5.5},
        "holdings": {"ASML Holding NV": 2.1, "Nestlé SA": 2.0, "Toyota Motor Corp.": 1.8, "LVMH": 1.7, "Shell PLC": 1.6, "Novartis AG": 1.5, "Resto del ETF": 89.3}
    },
    "eqqq.de": {
        "name": "Invesco EQQQ NASDAQ-100 UCITS ETF [Distribución]", "ticker": "EQQQ.DE",
        "category": "Tecnología", "ter": 0.30, "aum": 11500,
        "replication": "Física (Completa)", "te": 0.05, "currency": "EUR", "age_years": 21, "is_dist": True, "return_1y": 26.8, "score": 4.5,
        "desc": "Exposición a las 100 mayores empresas no financieras cotizadas en el Nasdaq.",
        "geo": {"EE. UU.": 98.5, "Otros": 1.5},
        "holdings": {"Microsoft Corp.": 8.8, "Apple Inc.": 8.5, "NVIDIA Corp.": 8.2, "Amazon.com Inc.": 5.1, "Meta Platforms": 4.5, "Broadcom Inc.": 4.2, "Resto del ETF": 60.7}
    },
    "sxrv.de": {
        "name": "iShares NASDAQ 100 UCITS ETF [Acumulación]", "ticker": "SXRV.DE",
        "category": "Tecnología", "ter": 0.33, "aum": 14200,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 14, "is_dist": False, "return_1y": 27.1, "score": 4.6,
        "desc": "Versión de acumulación del Nasdaq 100.",
        "geo": {"EE. UU.": 98.5, "Otros": 1.5},
        "holdings": {"Microsoft Corp.": 8.8, "Apple Inc.": 8.5, "NVIDIA Corp.": 8.2, "Amazon.com Inc.": 5.1, "Meta Platforms": 4.5, "Resto del ETF": 64.9}
    },
    "smh.de": {
        "name": "VanEck Semiconductor UCITS ETF (Semiconductores & IA)", "ticker": "SMH.DE",
        "category": "Tecnología", "ter": 0.35, "aum": 2100,
        "replication": "Física (Completa)", "te": 0.08, "currency": "EUR", "age_years": 4, "is_dist": False, "return_1y": 42.0, "score": 4.4,
        "desc": "Enfocado en empresas de semiconductores, chips y cadena de suministro de IA.",
        "geo": {"EE. UU.": 75.0, "Taiwán": 15.0, "Países Bajos": 8.0, "Otros": 2.0},
        "holdings": {"NVIDIA Corp.": 20.5, "Taiwan Semiconductor (TSMC)": 13.0, "Broadcom Inc.": 8.5, "ASML Holding": 7.8, "AMD": 5.2, "Qualcomm": 4.1, "Resto del ETF": 40.9}
    },
    "4gld.de": {
        "name": "Xtrackers Physical Gold ETC (Oro Físico respaldado)", "ticker": "4GLD.DE",
        "category": "Materias Primas / Metales", "ter": 0.12, "aum": 13500,
        "replication": "Física (Custodia en Bóveda)", "te": 0.01, "currency": "EUR", "age_years": 15, "is_dist": False, "return_1y": 24.5, "score": 4.7,
        "desc": "ETC respaldado por oro físico en bóvedas seguras.",
        "geo": {"Oro Físico": 100.0},
        "holdings": {"Lingotes de Oro Físico (999.9)": 100.0}
    },
    "isln.de": {
        "name": "iShares Physical Silver ETC (Plata Física)", "ticker": "ISLN.DE",
        "category": "Materias Primas / Metales", "ter": 0.20, "aum": 2800,
        "replication": "Física", "te": 0.02, "currency": "EUR", "age_years": 11, "is_dist": False, "return_1y": 29.1, "score": 4.3,
        "desc": "ETC respaldado por plata física.",
        "geo": {"Plata Física": 100.0},
        "holdings": {"Lingotes de Plata Física": 100.0}
    },
    "exxy.de": {
        "name": "iShares Diversified Commodity Swap UCITS ETF (Cesta Materias Primas)", "ticker": "EXXY.DE",
        "category": "Materias Primas / Metales", "ter": 0.19, "aum": 1900,
        "replication": "Sintética", "te": 0.10, "currency": "EUR", "age_years": 8, "is_dist": False, "return_1y": 8.5, "score": 4.1,
        "desc": "Cesta diversificada de materias primas (energía, agricultura, metales industriales).",
        "geo": {"Energía": 40.0, "Agricultura": 30.0, "Metales Industriales": 30.0},
        "holdings": {"Petróleo Crudo WTI / Brent": 22.0, "Cobre y Aluminio": 18.0, "Trigo y Maíz": 15.0, "Oro y Metales Preciosos": 15.0, "Gas Natural": 10.0, "Resto Cesta": 20.0}
    },
    "vhyd.de": {
        "name": "Vanguard FTSE All-World High Dividend Yield UCITS ETF [Distribución]", "ticker": "VHYD.DE",
        "category": "Alto Dividendo", "ter": 0.29, "aum": 4200,
        "replication": "Física", "te": 0.05, "currency": "EUR", "age_years": 10, "is_dist": True, "return_1y": 14.2, "score": 4.5,
        "desc": "Acciones de alta rentabilidad por dividendo a nivel global.",
        "geo": {"EE. UU.": 42.0, "Europa": 28.0, "Reino Unido": 12.0, "Japón": 8.0, "Otros": 10.0},
        "holdings": {"JPMorgan Chase & Co.": 3.2, "Exxon Mobil Corp.": 3.0, "Johnson & Johnson": 2.7, "Procter & Gamble": 2.5, "Chevron Corp.": 2.2, "Pfizer": 1.9, "Resto del ETF": 84.5}
    },
    "emim.l": {
        "name": "iShares Core MSCI Emerging Markets IMI UCITS ETF [Acumulación]", "ticker": "EMIM.L",
        "category": "Mercados Emergentes", "ter": 0.18, "aum": 18000,
        "replication": "Física (Muestreo)", "te": 0.06, "currency": "EUR", "age_years": 10, "is_dist": False, "return_1y": 9.8, "score": 4.4,
        "desc": "Exposición completa a más de 3.000 valores de países emergentes de gran, mediana y pequeña capitalización.",
        "geo": {"China": 26.0, "India": 19.5, "Taiwán": 17.5, "Corea del Sur": 12.0, "Otros": 25.0},
        "holdings": {"Taiwan Semiconductor (TSMC)": 8.8, "Tencent Holdings": 4.5, "Samsung Electronics": 4.0, "Alibaba Group": 2.9, "Reliance Industries": 1.9, "Resto del ETF": 77.9}
    }
}

def render_geo_breakdown(geo_dict):
    st.markdown("**🗺️ Desglose Geográfico Estimado:**")
    colors = {
        "EE. UU.": "#3b82f6", "China": "#ef4444", "India": "#f59e0b", "Taiwán": "#10b981", 
        "Corea del Sur": "#8b5cf6", "Japón": "#ec4899", "Reino Unido": "#6366f1", "Europa": "#14b8a6", 
        "Europa (Ex-UK)": "#06b6d4", "Canadá": "#84cc16", "Mercados Emergentes": "#f97316", 
        "Brasil": "#eab308", "Oro Físico": "#fbbf24", "Plata Física": "#94a3b8", "Energía": "#f97316", 
        "Agricultura": "#84cc16", "Metales Industriales": "#06b6d4", "Francia": "#3b82f6", "Suiza": "#ef4444", 
        "Alemania": "#10b981", "Otros": "#64748b"
    }
    
    bar_html = '<div class="geo-bar-container">'
    legend_html = '<div class="geo-legend">'
    
    for country, pct in geo_dict.items():
        color = colors.get(country, "#94a3b8")
        bar_html += f'<div style="width: {pct}%; background-color: {color}; height: 100%;" title="{country}: {pct}%"></div>'
        legend_html += f'<div class="geo-legend-item"><div class="geo-dot" style="background-color: {color};"></div><span>{country} ({pct}%)</span></div>'
    
    bar_html += '</div>'
    legend_html += '</div>'
    
    st.markdown(bar_html + legend_html, unsafe_allow_html=True)

def render_holdings_breakdown(holdings_dict):
    st.markdown("**🏢 Principales Empresas y Participación en la Cartera:**")
    holding_colors = [
        "#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#fb7185", 
        "#34d399", "#fbbf24", "#fb923c", "#a3e635", "#22d3ee", "#94a3b8"
    ]
    
    bar_html = '<div class="geo-bar-container">'
    legend_html = '<div class="geo-legend">'
    
    for idx, (company, pct) in enumerate(holdings_dict.items()):
        color = "#475569" if "resto" in company.lower() else holding_colors[idx % len(holding_colors)]
        bar_html += f'<div style="width: {pct}%; background-color: {color}; height: 100%;" title="{company}: {pct}%"></div>'
        legend_html += f'<div class="geo-legend-item"><div class="geo-dot" style="background-color: {color};"></div><span>{company} ({pct}%)</span></div>'
    
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

    # 1. RECOMENDADO DEL MES
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
                "ter": top_asset['ter'], "currency": "EUR", "is_dist": top_asset['is_dist'],
                "category": "Renta Variable Global (MSCI World)"
            })
            guardar_en_url()
            st.success(f"¡{top_asset['name']} añadido a tu Cartera!")

    st.markdown("---")

    # 2. CUESTIONARIO INTERACTIVO
    st.markdown("### 🧭 Asistente Interactivo: ¿Qué vehículo elegir (Fondo Indexado o ETF)?")
    with st.expander("💡 Responde a 3 preguntas rápidas para descubrir tu opción ideal", expanded=True):
        q_knowledge = st.radio(
            "0. ¿Tienes conocimientos sobre inversiones?",
            [
                "Sí, me he informado y tengo conocimientos sobre fondos indexados, ETFs e impuestos asociados",
                "No, acabo de conocer este mundo y necesito consejo o información"
            ]
        )
        
        q_goal = st.radio(
            "1. ¿Qué objetivo estás buscando?",
            [
                "Largo plazo sin tocarlo (adecuado para jubilación o ahorro para comprar vivienda)",
                "Corto plazo (para reformas, imprevistos en el hogar o compra de coche)",
                "Híbrido, una mezcla de los dos (jubilación a largo plazo pero con liquidez por si necesito un coche o reforma)"
            ]
        )
        
        q_moves = st.radio(
            "2. ¿Tienes pensado hacer cambios en tus inversiones, rebalanceos o cambiar de activos?",
            [
                "No lo sé, no sé qué es eso ni lo que implicaría",
                "No, quiero comprar y mantener sin tocar nada durante décadas",
                "Sí, es probable que quiera mover posiciones o reestructurar"
            ]
        )
        
        if st.button("🔮 Calcular mi recomendación ideal", type="primary"):
            st.markdown("---")
            
            if "No, acabo" in q_knowledge:
                st.info("ℹ️ **Nota educativa:** Los **Fondos Indexados** permiten traspasar dinero de un fondo a otro en España sin pagar impuestos en ese momento (diferimiento fiscal). Los **ETFs** cotizan como acciones y, cada vez que vendes o cambias, pagas impuestos sobre las ganancias ese año, aunque suelen tener comisiones anuales (TER) un poco más bajas.")

            if "Híbrido" in q_goal:
                st.warning("🎯 **Estrategia Mixta Recomendada (Jubilación + Liquidez):**\n\n- **Parte intocable (Jubilación):** Canalízala mediante un **ETF de bajo coste** (como SPYL.DE al 0.03% TER) para optimizar comisiones al máximo.\n- **Parte flexible (Coche / Casa / Imprevistos):** Utiliza **Fondos Indexados** (ej. MyInvestor) para poder retirar o mover capital sin penalización ni peaje fiscal inmediato en tus transacciones.")
            elif "Corto plazo" in q_goal:
                st.warning("🎯 **Recomendación para Corto Plazo / Liquidez:**\n\nSi el dinero es para metas a corto plazo (coche, reformas, imprevistos), los **Fondos Indexados** son la opción más recomendable por su flexibilidad al reembolsar o cambiar de estrategia sin peaje fiscal inmediato.")
            elif "Largo plazo" in q_goal and "No, quiero comprar" in q_moves:
                st.success("🎯 **Tu mejor opción: ETFs de coste ultra bajo (Ej. SPYL.DE al 0.03% TER)**\n\nPara un horizonte de largo plazo donde no vas a mover el dinero en décadas, la diferencia de comisiones anuales (TER del 0.03% vs 0.18%) compensa con creces cualquier ventaja fiscal de traspaso.")
            elif "Largo plazo" in q_goal and ("Sí, es probable" in q_moves or "No lo sé" in q_moves):
                st.info("🎯 **Tu mejor opción: Fondos Indexados (Ej. en MyInvestor)**\n\nAl querer flexibilidad para cambiar de activos, reestructurar la cartera o por no tener aún clara la estrategia, los fondos te permiten traspasar capital libremente sin tributar en el IRPF en cada movimiento.")

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
        st.info("No tienes ningún activo guardado en favoritos todavía. Explora acciones, fondos o ETFs y pulsa **'⭐ Añadir a Favoritos'** en sus informes.")
    else:
        for idx, fav in enumerate(st.session_state.favorites):
            with st.expander(f"{idx+1}. {fav['name']} ({fav['ticker']}) - [{fav['type']}]", expanded=True):
                col_fav1, col_fav2, col_fav3, col_fav4 = st.columns([2, 1, 1, 1])
                with col_fav1:
                    st.markdown(f"**Categoría / Detalles:** {fav.get('category', 'General')}")
                    st.markdown(f"**TER / Coste anual:** {fav.get('ter', 0.0)}%")
                    st.markdown(f"**Divisa:** {fav.get('currency', 'EUR')}")
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
                        st.success(f"¡{fav['name']} añadido a la Cartera!")
                with col_fav4:
                    if st.button("🗑️ Quitar", key=f"del_fav_{idx}", use_container_width=True):
                        st.session_state.favorites.pop(idx)
                        guardar_en_url()
                        st.rerun()

        if st.button("🗑️ Vaciar Lista de Favoritos"):
            st.session_state.favorites = []
            guardar_en_url()
            st.rerun()
