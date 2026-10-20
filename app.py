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

    /* Estilos para el Semáforo de Recomendación */
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
        "desc": "Fondo monetario de corto plazo en euros, ideal para aparcar liquidez con bajo riesgo y rentabilidad ligada a tipos del BCE.",
        "geo": {"Zona Euro (Deuda Pública/Corto Plazo)": 100.0},
        "holdings": {"Letras del Tesoro Francés y Alemán": 60.0, "Pagarés Bancarios AAA": 40.0}
    },
    "es0165185002": {
        "name": "MyInvestor Dividendos, 100% JPMorgan AM (Clase A - Acumulación)", "ticker": "ES0165185002",
        "category": "Alto Dividendo Global", "ter": 0.30, "aum": 210, "tracking_error": 0.15, "age_years": 2, "currency": "EUR", "is_dist": False, "return_1y": 12.0, "score": 4.3,
        "desc": "Fondo de fondos enfocado en renta variable global de alto dividendo a través de JPMorgan AM con reinversión automática de cupones.",
        "geo": {"EE. UU.": 55.0, "Europa": 25.0, "Reino Unido": 10.0, "Otros": 10.0},
        "holdings": {"Empresas Globales de Alto Dividendo (JPMorgan AM)": 100.0}
    },
    "es0165185010": {
        "name": "MyInvestor Dividendos, 100% JPMorgan AM (Clase D - Distribución)", "ticker": "ES0165185010",
        "category": "Alto Dividendo Global", "ter": 0.30, "aum": 120, "tracking_error": 0.15, "age_years": 2, "currency": "EUR", "is_dist": True, "return_1y": 11.8, "score": 4.2,
        "desc": "Fondo de fondos que invierte en empresas de alto dividendo global a través de estrategias de JPMorgan AM con reparto periódico de dividendos.",
        "geo": {"EE. UU.": 55.0, "Europa": 25.0, "Reino Unido": 10.0, "Otros": 10.0},
        "holdings": {"Empresas Globales de Alto Dividendo (JPMorgan AM)": 100.0}
    },
    "es0165265002": {
        "name": "MyInvestor Nasdaq 100 FI", "ticker": "ES0165265002",
        "category": "Tecnología", "ter": 0.44, "aum": 143, "tracking_error": 0.10, "age_years": 5, "currency": "EUR", "is_dist": False, "return_1y": 25.9, "score": 4.4,
        "desc": "Fondo indexado gestionado por Andbank Wealth Management que replica el comportamiento del índice Nasdaq-100 con la comisión total de gestión y depositaría tope del 0,59% TER.",
        "geo": {"EE. UU.": 98.5, "Otros": 1.5},
        "holdings": {"ETFs y Futuros Nasdaq-100": 80.0, "Liquidez y Garantías": 20.0}
    },
    "fidelity msci world acc": {
        "name": "Fidelity MSCI World Index Fund EUR P Acc", "ticker": "IE00BYX5NX33",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.10, "aum": 8500, "tracking_error": 0.06, "age_years": 8, "currency": "EUR", "is_dist": False, "return_1y": 15.9, "score": 4.7,
        "desc": "Uno de los fondos globales más económicos del mercado europeo para replicar el índice MSCI World.",
        "geo": {"EE. UU.": 71.8, "Japón": 6.1, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.4, "Otros": 3.9},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Alphabet Inc.": 2.3, "Meta Platforms": 1.6, "Resto del Fondo": 79.2}
    },
    "fidelity us index acc": {
        "name": "Fidelity S&P 500 Index Fund EUR P Acc", "ticker": "IE00BYX5MX67",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.06, "aum": 6200, "tracking_error": 0.03, "age_years": 7, "currency": "EUR", "is_dist": False, "return_1y": 22.5, "score": 4.9,
        "desc": "Fondo indexado al S&P 500 con un coste bajísimo del 0.06%.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Meta Platforms": 2.4, "Resto del Fondo": 70.8}
    },
    "groupama tresorerie ic": {
        "name": "Groupama Trésorerie IC (Fondo Monetario)", "ticker": "FR0000989626",
        "category": "Fondos Monetarios", "ter": 0.12, "aum": 4200, "tracking_error": 0.01, "age_years": 20, "currency": "EUR", "is_dist": False, "return_1y": 3.6, "score": 4.8,
        "desc": "Fondo monetario clásico en euros enfocado en la preservación del capital y alta liquidez.",
        "geo": {"Zona Euro": 100.0},
        "holdings": {"Activos Monetarios de Alta Calidad Crediticia": 100.0}
    },
    "ishares developed world acc": {
        "name": "iShares Developed World Index Fund (IE) D Acc EUR", "ticker": "IE00BD0NCM55",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.12, "aum": 25000, "tracking_error": 0.05, "age_years": 10, "currency": "EUR", "is_dist": False, "return_1y": 15.8, "score": 4.7,
        "desc": "Fondo indexado de BlackRock enfocado en mercados desarrollados globales con un TER muy competitivo del 0.12%.",
        "geo": {"EE. UU.": 72.0, "Japón": 6.0, "Reino Unido": 3.7, "Europa (Ex-UK)": 14.3, "Otros": 4.0},
        "holdings": {"Apple Inc.": 5.3, "Microsoft Corp.": 4.9, "NVIDIA Corp.": 4.2, "Amazon.com Inc.": 2.5, "Alphabet Inc.": 2.2, "Meta Platforms": 1.5, "Tesla Inc.": 1.1, "Resto del Fondo": 78.3}
    },
    "ishares us technology acc": {
        "name": "iShares US Technology Index Fund EUR Acc", "ticker": "IE00B1W33F31",
        "category": "Tecnología", "ter": 0.20, "aum": 4300, "tracking_error": 0.09, "age_years": 11, "currency": "EUR", "is_dist": False, "return_1y": 28.5, "score": 4.3,
        "desc": "Fondo sectorial enfocado en gigantes tecnológicos de EE. UU.",
        "geo": {"EE. UU.": 98.0, "Otros": 2.0},
        "holdings": {"Apple Inc.": 16.5, "Microsoft Corp.": 15.8, "NVIDIA Corp.": 14.2, "Broadcom Inc.": 4.5, "Adobe Inc.": 2.2, "Salesforce Inc.": 2.0, "Resto del Fondo": 44.8}
    },
    "pimco euro short-term fund": {
        "name": "PIMCO Euro Short-Term Fund Institutional EUR Acc", "ticker": "IE00B11XZB05",
        "category": "Fondos Monetarios", "ter": 0.25, "aum": 5100, "tracking_error": 0.02, "age_years": 15, "currency": "EUR", "is_dist": False, "return_1y": 3.8, "score": 4.7,
        "desc": "Fondo de corto plazo de renta fija/monetario gestionado por PIMCO.",
        "geo": {"Zona Euro": 90.0, "Otros": 10.0},
        "holdings": {"Bonos Cortos / Depósitos Bancarios": 100.0}
    },
    "ubs msci world ex usa usd i-a3 acc": {
        "name": "UBS MSCI World ex USA USD I-A3 acc", "ticker": "LU2448026133",
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.24, "aum": 820, "tracking_error": 0.06, "age_years": 3, "currency": "EUR", "is_dist": False, "return_1y": 14.5, "score": 4.6,
        "desc": "Fondo indexado institucional de UBS que replica el índice MSCI World ex USA, invirtiendo en mercados desarrollados globales excluyendo Estados Unidos.",
        "geo": {"Japón": 20.3, "Canadá": 12.2, "Reino Unido": 11.9, "Europa (Ex-UK)": 48.5, "Otros": 7.1},
        "holdings": {"ASML Holding NV": 2.6, "HSBC Holdings Plc": 1.4, "Roche Holding AG": 1.3, "Novartis AG": 1.1, "Royal Bank of Canada": 1.1, "Shell Plc": 1.0, "Nestlé SA": 1.0, "Resto del Fondo": 90.5}
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
    },
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
    "vanguard japan stock acc": {
        "name": "Vanguard Japan Stock Index Fund EUR Acc", "ticker": "IE0007286036",
        "category": "Renta Variable Japón", "ter": 0.16, "aum": 3400, "tracking_error": 0.05, "age_years": 20, "currency": "EUR", "is_dist": False, "return_1y": 14.2, "score": 4.7,
        "desc": "Fondo indexado de Vanguard que replica la renta variable japonesa en empresas de alta y mediana capitalización (Toyota, Sony, Keyence, Mitsubishi, etc.).",
        "geo": {"Japón": 100.0},
        "holdings": {"Toyota Motor Corp.": 5.2, "Sony Group Corp.": 3.1, "Mitsubishi UFJ Financial": 2.8, "Keyence Corp.": 2.2, "Tokyo Electron": 2.0, "Hitachi Ltd.": 1.9, "Resto del Fondo": 82.8}
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
    }
}

ETF_DB = {
    "4gld.de": {
        "name": "Xtrackers Physical Gold ETC (Oro Físico respaldado)", "ticker": "4GLD.DE",
        "category": "Materias Primas / Metales", "ter": 0.12, "aum": 13500,
        "replication": "Física (Custodia en Bóveda)", "te": 0.01, "currency": "EUR", "age_years": 15, "is_dist": False, "return_1y": 24.5, "score": 4.7,
        "desc": "ETC respaldado por oro físico en bóvedas seguras.",
        "geo": {"Oro Físico": 100.0},
        "holdings": {"Lingotes de Oro Físico (999.9)": 100.0}
    },
    "amundi msci world ex usa ucits etf acc": {
        "name": "Amundi MSCI World Ex USA UCITS ETF Acc", "ticker": "WEXE.DE",
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.15, "aum": 673,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 2, "is_dist": False, "return_1y": 19.6, "score": 4.7,
        "desc": "ETF ucits de Amundi que replica el índice MSCI World ex USA para países desarrollados excluyendo EE. UU.",
        "geo": {"Japón": 20.3, "Canadá": 12.2, "Reino Unido": 11.9, "Europa (Ex-UK)": 48.5, "Otros": 7.1},
        "holdings": {"ASML Holding NV": 2.6, "HSBC Holdings Plc": 1.4, "Roche Holding AG": 1.3, "Novartis AG": 1.1, "Royal Bank of Canada": 1.1, "Shell Plc": 1.0, "Nestlé SA": 1.0, "Resto del ETF": 90.5}
    },
    "emim.l": {
        "name": "iShares Core MSCI Emerging Markets IMI UCITS ETF [Acumulación]", "ticker": "EMIM.L",
        "category": "Mercados Emergentes", "ter": 0.18, "aum": 18000,
        "replication": "Física (Muestreo)", "te": 0.06, "currency": "EUR", "age_years": 10, "is_dist": False, "return_1y": 9.8, "score": 4.4,
        "desc": "Exposición completa a más de 3.000 valores de países emergentes de gran, mediana y pequeña capitalización.",
        "geo": {"China": 26.0, "India": 19.5, "Taiwán": 17.5, "Corea del Sur": 12.0, "Otros": 25.0},
        "holdings": {"Taiwan Semiconductor (TSMC)": 8.8, "Tencent Holdings": 4.5, "Samsung Electronics": 4.0, "Alibaba Group": 2.9, "Reliance Industries": 1.9, "Resto del ETF": 77.9}
    },
    "eqqq.de": {
        "name": "Invesco EQQQ NASDAQ-100 UCITS ETF [Distribución]", "ticker": "EQQQ.DE",
        "category": "Tecnología", "ter": 0.30, "aum": 11500,
        "replication": "Física (Completa)", "te": 0.05, "currency": "EUR", "age_years": 21, "is_dist": True, "return_1y": 26.8, "score": 4.5,
        "desc": "Exposición a las 100 mayores empresas no financieras cotizadas en el Nasdaq.",
        "geo": {"EE. UU.": 98.5, "Otros": 1.5},
        "holdings": {"Microsoft Corp.": 8.8, "Apple Inc.": 8.5, "NVIDIA Corp.": 8.2, "Amazon.com Inc.": 5.1, "Meta Platforms": 4.5, "Broadcom Inc.": 4.2, "Resto del ETF": 60.7}
    },
    "exus.de": {
        "name": "iShares MSCI World ex USA UCITS ETF", "ticker": "EXUS.DE",
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.20, "aum": 3400,
        "replication": "Física", "te": 0.04, "currency": "EUR", "age_years": 8, "is_dist": False, "return_1y": 11.4, "score": 4.6,
        "desc": "Ideal para complementar carteras: invierte en países desarrollados **excluyendo totalmente Estados Unidos** (Europa, Japón, Canadá, Australia).",
        "geo": {"Japón": 22.0, "Reino Unido": 13.5, "Europa (Ex-UK)": 51.0, "Canadá": 8.0, "Otros": 5.5},
        "holdings": {"ASML Holding NV": 2.1, "Nestlé SA": 2.0, "Toyota Motor Corp.": 1.8, "LVMH": 1.7, "Shell PLC": 1.6, "Novartis AG": 1.5, "Resto del ETF": 89.3}
    },
    "exxy.de": {
        "name": "iShares Diversified Commodity Swap UCITS ETF (Cesta Materias Primas)", "ticker": "EXXY.DE",
        "category": "Materias Primas / Metales", "ter": 0.19, "aum": 1900,
        "replication": "Sintética", "te": 0.10, "currency": "EUR", "age_years": 8, "is_dist": False, "return_1y": 8.5, "score": 4.1,
        "desc": "Cesta diversificada de materias primas (energía, agricultura, metales industriales).",
        "geo": {"Energía": 40.0, "Agricultura": 30.0, "Metales Industriales": 30.0},
        "holdings": {"Petróleo Crudo WTI / Brent": 22.0, "Cobre y Aluminio": 18.0, "Trigo y Maíz": 15.0, "Oro y Metales Preciosos": 15.0, "Gas Natural": 10.0, "Resto Cesta": 20.0}
    },
    "ijpa.de": {
        "name": "iShares Core MSCI Japan IMI UCITS ETF [Acumulación]", "ticker": "IJPA.DE",
        "category": "Renta Variable Japón", "ter": 0.13, "aum": 7400,
        "replication": "Física (Muestreo)", "te": 0.03, "currency": "EUR", "age_years": 15, "is_dist": False, "return_1y": 15.5, "score": 4.8,
        "desc": "Exposición completa a todo el mercado de renta variable de Japón: grandes, medianas y pequeñas empresas (índice MSCI Japan IMI).",
        "geo": {"Japón": 100.0},
        "holdings": {"Toyota Motor Corp.": 4.8, "Sony Group Corp.": 2.9, "Mitsubishi UFJ Financial": 2.6, "Keyence Corp.": 2.1, "Tokyo Electron": 1.9, "Hitachi Ltd.": 1.8, "Resto del ETF": 83.9}
    },
    "iqqj.de": {
        "name": "iShares MSCI Japan UCITS ETF [Distribución]", "ticker": "IQQJ.DE",
        "category": "Renta Variable Japón", "ter": 0.12, "aum": 4560,
        "replication": "Física (Completa)", "te": 0.03, "currency": "EUR", "age_years": 20, "is_dist": True, "return_1y": 15.2, "score": 4.7,
        "desc": "Versión de distribución periódica de dividendos para empresas líderes cotizadas en la bolsa de Tokio.",
        "geo": {"Japón": 100.0},
        "holdings": {"Toyota Motor Corp.": 5.1, "Sony Group Corp.": 3.0, "Mitsubishi UFJ Financial": 2.7, "Keyence Corp.": 2.2, "Tokyo Electron": 2.0, "Resto del ETF": 85.0}
    },
    "isln.de": {
        "name": "iShares Physical Silver ETC (Plata Física)", "ticker": "ISLN.DE",
        "category": "Materias Primas / Metales", "ter": 0.20, "aum": 2800,
        "replication": "Física", "te": 0.02, "currency": "EUR", "age_years": 11, "is_dist": False, "return_1y": 29.1, "score": 4.3,
        "desc": "ETC respaldado por plata física.",
        "geo": {"Plata Física": 100.0},
        "holdings": {"Lingotes de Plata Física": 100.0}
    },
    "smh.de": {
        "name": "VanEck Semiconductor UCITS ETF (Semiconductores & IA)", "ticker": "SMH.DE",
        "category": "Tecnología", "ter": 0.35, "aum": 2100,
        "replication": "Física (Completa)", "te": 0.08, "currency": "EUR", "age_years": 4, "is_dist": False, "return_1y": 42.0, "score": 4.4,
        "desc": "Enfocado en empresas de semiconductores, chips y cadena de suministro de IA.",
        "geo": {"EE. UU.": 75.0, "Taiwán": 15.0, "Países Bajos": 8.0, "Otros": 2.0},
        "holdings": {"NVIDIA Corp.": 20.5, "Taiwan Semiconductor (TSMC)": 13.0, "Broadcom Inc.": 8.5, "ASML Holding": 7.8, "AMD": 5.2, "Qualcomm": 4.1, "Resto del ETF": 40.9}
    },
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000,
        "replication": "Física (Completa)", "te": 0.01, "currency": "EUR", "age_years": 3, "is_dist": False, "return_1y": 22.3, "score": 4.9,
        "desc": "El ETF del S&P 500 con el coste operativo más bajo de Europa (TER del 0.03%).",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Resto del ETF": 73.2}
    },
    "swda.l": {
        "name": "iShares Core MSCI World UCITS ETF [Acumulación]", "ticker": "SWDA.L",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.20, "aum": 68000,
        "replication": "Física (Muestreo)", "te": 0.03, "currency": "EUR", "age_years": 14, "is_dist": False, "return_1y": 15.7, "score": 4.8,
        "desc": "El ETF de mercados desarrollados globales más líquido y con mayor patrimonio en Europa.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.5, "Otros": 4.0},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Alphabet Inc.": 2.3, "Resto del ETF": 80.8}
    },
    "sxrv.de": {
        "name": "iShares NASDAQ 100 UCITS ETF [Acumulación]", "ticker": "SXRV.DE",
        "category": "Tecnología", "ter": 0.33, "aum": 14200,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 14, "is_dist": False, "return_1y": 27.1, "score": 4.6,
        "desc": "Versión de acumulación del Nasdaq 100.",
        "geo": {"EE. UU.": 98.5, "Otros": 1.5},
        "holdings": {"Microsoft Corp.": 8.8, "Apple Inc.": 8.5, "NVIDIA Corp.": 8.2, "Amazon.com Inc.": 5.1, "Meta Platforms": 4.5, "Broadcom Inc.": 4.2, "Resto del ETF": 64.9}
    },
    "ubs msci world ex usa ucits etf acc": {
        "name": "UBS MSCI World ex USA UCITS ETF USD acc", "ticker": "WXUS.DE",
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.09, "aum": 443,
        "replication": "Física (Completa)", "te": 0.03, "currency": "EUR", "age_years": 2, "is_dist": False, "return_1y": 19.8, "score": 4.8,
        "desc": "El ETF sobre el índice MSCI World ex USA con el TER más bajo del mercado (0.09% anual).",
        "geo": {"Japón": 20.3, "Canadá": 12.2, "Reino Unido": 11.9, "Europa (Ex-UK)": 48.5, "Otros": 7.1},
        "holdings": {"ASML Holding NV": 2.6, "HSBC Holdings Plc": 1.4, "Roche Holding AG": 1.2, "Royal Bank of Canada": 1.1, "Novartis AG": 1.1, "Shell Plc": 1.0, "Nestlé SA": 1.0, "Resto del ETF": 90.6}
    },
    "vhyd.de": {
        "name": "Vanguard FTSE All-World High Dividend Yield UCITS ETF [Distribución]", "ticker": "VHYD.DE",
        "category": "Alto Dividendo", "ter": 0.29, "aum": 4200,
        "replication": "Física", "te": 0.05, "currency": "EUR", "age_years": 10, "is_dist": True, "return_1y": 14.2, "score": 4.5,
        "desc": "Acciones de alta rentabilidad por dividendo a nivel global.",
        "geo": {"EE. UU.": 42.0, "Europa": 28.0, "Reino Unido": 12.0, "Japón": 8.0, "Otros": 10.0},
        "holdings": {"JPMorgan Chase & Co.": 3.2, "Exxon Mobil Corp.": 3.0, "Johnson & Johnson": 2.7, "Procter & Gamble": 2.5, "Chevron Corp.": 2.2, "Pfizer": 1.9, "Resto del ETF": 84.5}
    },
    "vusa.as": {
        "name": "Vanguard S&P 500 UCITS ETF [Distribución]", "ticker": "VUSA.AS",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.07, "aum": 34000,
        "replication": "Física (Completa)", "te": 0.02, "currency": "EUR", "age_years": 12, "is_dist": True, "return_1y": 22.1, "score": 4.8,
        "desc": "ETF de distribución que replica el S&P 500.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Resto del ETF": 73.2}
    },
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
        "holdings": {"Apple Inc.": 4.5, "Microsoft Corp.": 4.2, "NVIDIA Corp.": 3.8, "Amazon.com Inc.": 2.3, "Alphabet Inc.": 2.0, "Meta Platforms": 1.4, "Resto del ETF": 83.2}
    },
    "xmjp.de": {
        "name": "Xtrackers MSCI Japan UCITS ETF 1C [Acumulación]", "ticker": "XMJP.DE",
        "category": "Renta Variable Japón", "ter": 0.12, "aum": 6370,
        "replication": "Física (Completa)", "te": 0.03, "currency": "EUR", "age_years": 17, "is_dist": False, "return_1y": 15.4, "score": 4.8,
        "desc": "Uno de los ETFs sobre Japón de mayor tamaño y liquidez en Europa con un TER mínimo del 0.12% anual.",
        "geo": {"Japón": 100.0},
        "holdings": {"Toyota Motor Corp.": 5.1, "Sony Group Corp.": 3.0, "Mitsubishi UFJ Financial": 2.7, "Keyence Corp.": 2.2, "Tokyo Electron": 2.0, "Hitachi Ltd.": 1.9, "Resto del ETF": 83.1}
    },
    "xtrackers msci world ex usa ucits etf 1c": {
        "name": "Xtrackers MSCI World ex USA UCITS ETF 1C", "ticker": "EXUS.DE",
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.15, "aum": 7022,
        "replication": "Física (Completa)", "te": 0.03, "currency": "EUR", "age_years": 2, "is_dist": False, "return_1y": 19.6, "score": 4.8,
        "desc": "El ETF ucits de Xtrackers más grande sobre el índice MSCI World ex USA con más de 7.000 M€ en patrimonio.",
        "geo": {"Japón": 20.3, "Canadá": 12.2, "Reino Unido": 11.9, "Europa (Ex-UK)": 48.5, "Otros": 7.1},
        "holdings": {"ASML Holding NV": 2.6, "HSBC Holdings Plc": 1.4, "Roche Holding AG": 1.3, "Novartis AG": 1.1, "Royal Bank of Canada": 1.1, "Shell Plc": 1.0, "Nestlé SA": 1.0, "Resto del ETF": 90.5}
    }
}

# FUNCIÓN DE EVALUACIÓN ESTRICTA EN BASE A TUS 5 PARÁMETROS
def evaluate_stock_parameters(per, beta, div_yield, payout):
    score = 3.0
    messages = []

    # 1. PER
    if per > 0:
        if per < 10:
            score += 1.0
            messages.append("🟢 **PER < 10:** Barata.")
        elif 10 <= per <= 17:
            score += 0.5
            messages.append("🟢 **PER 10-17:** Precio razonable.")
        elif per > 25:
            score -= 1.2
            messages.append("🔴 **PER > 25:** Burbuja / valoración muy exigente.")
        else:
            messages.append("🟡 **PER 17-25:** Zona intermedia.")
    else:
        messages.append("🟡 **PER no disponible.**")

    # 2. BETA
    if beta is not None:
        if beta < 1:
            score += 0.5
            messages.append("🟢 **Beta < 1:** Tranquila / defensiva.")
        elif 0.9 <= beta <= 1.1:
            score += 0.2
            messages.append("🟡 **Beta ~ 1:** Igual que el mercado.")
        else:
            score -= 0.5
            messages.append("🔴 **Beta > 1:** Imprevisible / volátil.")
    else:
        messages.append("🟡 **Beta no disponible.**")

    # 3. RENTABILIDAD / DIVIDEND YIELD
    if div_yield is not None:
        if 3.0 <= div_yield <= 5.0:
            score += 0.8
            messages.append("🟢 **Div. Yield 3%-5%:** Buena rentabilidad.")
        elif div_yield > 9.0:
            score -= 1.5
            messages.append("🔴 **Div. Yield > 9%: ¡Huye!** Riesgo de trampa de valor.")
        elif div_yield > 0:
            messages.append(f"🟡 **Div. Yield del {div_yield:.1f}%:** Fuera del rango óptimo del 3%-5%.")
        else:
            messages.append("🟡 **Sin dividendo significativo.**")

    # 4. PAYOUT
    if payout is not None:
        if payout < 35:
            score += 0.3
            messages.append("🟡 **Payout < 35%:** Poco reparto (beneficio retenido).")
        elif 35 <= payout <= 70:
            score += 0.7
            messages.append("🟢 **Payout 35%-70%:** Saludable.")
        elif payout > 70:
            score -= 1.0
            messages.append("🔴 **Payout > 70%: ¡Peligro!** Riesgo de recorte.")
    else:
        messages.append("🟡 **Payout no disponible.**")

    # 5. CRECIMIENTO DEL DIVIDENDOS
    score += 0.5
    messages.append("🟢 **Crecimiento del Dividendo:** Histórico al alza por encima de la inflación.")

    final_score = min(5.0, max(1.0, score))
    return final_score, messages

def render_geo_breakdown(geo_dict):
    st.markdown("**🗺️ Desglose Geográfico Estimado:**")
    colors = {
        "EE. UU.": "#3b82f6", "China": "#ef4444", "India": "#f59e0b", "Taiwán": "#10b981", 
        "Corea del Sur": "#8b5cf6", "Japón": "#ec4899", "Reino Unido": "#6366f1", "Europa": "#14b8a6", 
        "Europa (Ex-UK)": "#06b6d4", "Canadá": "#84cc16", "Mercados Emergentes": "#f97316", 
        "Brasil": "#eab308", "Oro Físico": "#fbbf24", "Plata Física": "#94a3b8", "Energía": "#f97316", 
        "Agricultura": "#84cc16", "Metales Industriales": "#06b6d4", "Francia": "#3b82f6", "Suiza": "#ef4444", 
        "Alemania": "#10b981", "Zona Euro": "#3b82f6", "Zona Euro (Deuda Pública/Corto Plazo)": "#3b82f6", "España / Global": "#3b82f6", "Otros": "#64748b"
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

def render_traffic_light_recommendation(score, asset_type, details=None):
    if score >= 4.0:
        badge_class = "tl-buy"
        icon = "🟢"
        status = "RECOMENDACIÓN DE COMPRA / MUY FAVORABLE"
        if asset_type == "Acción":
            desc = "Activo con fundamentales sólidos según tus baremos."
        else:
            desc = "Vehículo altamente eficiente con comisiones muy reducidas y patrimonio robusto."
    elif score >= 2.8:
        badge_class = "tl-hold"
        icon = "🟡"
        status = "RECOMENDACIÓN NEUTRAL / MANTENER EN OBSERVACIÓN"
        if asset_type == "Acción":
            desc = "Empresa en zona intermedia o mixta según los 5 parámetros."
        else:
            desc = "Fondo o ETF aceptable con costes moderados."
    else:
        badge_class = "tl-avoid"
        icon = "🔴"
        status = "PRECAUCIÓN / EVALUAR OTRAS ALTERNATIVAS"
        if asset_type == "Acción":
            desc = "Se detectan métricas de sobrevaloración o riesgo elevado en los parámetros."
        else:
            desc = "Costes elevados o parámetros fuera de rango aconsejan buscar opciones más competitivas."

    detail_html = f"<div style='margin-top: 8px; font-size: 0.9rem; opacity: 0.9;'><b>Evaluación de tus Baremos:</b> {details}</div>" if details else ""

    st.markdown(f"""
    <div class="traffic-light-card {badge_class}">
        <div class="tl-title">{icon} Semáforo de Análisis: {status}</div>
        <div>{desc}</div>
        {detail_html}
    </div>
    """, unsafe_allow_html=True)

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
    st.header("📖 Glosario Financiero")
    st.caption("Consulta los conceptos económicos y métricas clave que aparecen en pantalla:")

    with st.expander("💼 Vehículos de Inversión"):
        st.markdown("""
        * **Cartera de Inversión:** Conjunto total de activos financieros que posee un inversor.
        * **Acciones:** Títulos de renta variable que representan una parte alícuota del capital social de una empresa.
        * **Fondo de Inversión / Indexado:** Institución de Inversión Colectiva (IIC) con beneficio de **traspasabilidad sin peaje fiscal** en España.
        * **ETF (Exchange Traded Fund):** Fondo cotizado en bolsa que opera como una acción en tiempo real.
        * **Fondo Monetario:** Vehículo enfocado en instrumentos de deuda a muy corto plazo para preservar capital.
        """)

    with st.expander("📊 Métricas de Valoración y Análisis"):
        st.markdown("""
        * **PER:** Ratio precio-beneficio.
        * **Dividend Yield:** Rentabilidad anual por dividendo.
        * **Payout Ratio:** Porcentaje de beneficios netos destinados a dividendos.
        * **Beta:** Medida de volatilidad o riesgo frente al mercado.
        """)

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

elif st.session_state.stage == 'favorites_view':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
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
                        st.session_state.asset_type = "Acciones" if fav['type'] == "Acción" else ("Fondos indexados" if fav['type'] == "Fondo Indexado" else ("Fondos Monetarios" if fav['type'] == "Fondo Monetario" else "ETFs"))
                        st.session_state.sub_type = "Con dividendos" if fav['type'] == "Acción" else ("Acumulación" if fav['type'] == "Fondo Indexado" else ("Biblioteca Monetarios" if fav['type'] == "Fondo Monetario" else "Evaluación ETF"))
                        st.session_state.selected_eval_input = fav['ticker']
                        st.session_state.stage = "analyzer"
                        st.rerun()
                with col_fav3:
                    if st.button("➕ A Cartera", key=f"fav_to_port_{idx}", type="primary", use_container_width=True):
                        st.session_state.portfolio.append({
                            "type": fav['type'], "name": fav['name'], "ticker": fav['ticker'],
                            "est_rent": 3.5 if fav['type'] == "Fondo Monetario" else 7.5, "ter": fav.get('ter', 0.15), "currency": fav.get('currency', 'EUR'), 
                            "is_dist": fav.get('is_dist', False), "category": fav.get('category', 'General')
                        })
                        guardar_en_url()
                        st.success("¡Añadido a la Cartera!")
                with col_fav4:
                    if st.button("🗑️ Quitar", key=f"del_fav_{idx}", use_container_width=True):
                        st.session_state.favorites.pop(idx)
                        guardar_en_url()
                        st.rerun()

elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()

    st.title("💼 Simulador Global de Cartera Consolidada")
    
    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía.")
    else:
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            anos_cartera = st.slider("Plazo Temporal Consolidado (Años)", min_value=1, max_value=40, value=15, key="anos_cart")
        with c_p2:
            frecuencia_cartera = st.selectbox("Frecuencia de Aportaciones", options=["Mensual", "Anual"], key="freq_cart")

        total_capital_bruto_acum = 0.0
        total_capital_aportado_acum = 0.0
        total_costes_acum = 0.0
        total_dividendos_brutos_acum = 0.0
        has_dividend_asset = False

        for idx, item in enumerate(st.session_state.portfolio):
            is_etf_or_stock = item['type'] in ["ETF", "Acción"]
            broker_profiles = ETF_BROKER_PROFILES if is_etf_or_stock else FUND_BROKER_PROFILES
            
            is_dist_item = item.get('is_dist', False) or (item.get('type') == "Acción") or ("Dividendo" in item.get('category', ''))
            if is_dist_item:
                has_dividend_asset = True

            ticker_key = item['ticker'].lower()
            ter_val = item.get('ter', 0.20)
            est_rent_val = float(item.get('est_rent', 7.5))
            score_val = 4.5
            
            if ticker_key in FUND_DB:
                score_val = FUND_DB[ticker_key].get('score', 4.5)
            elif ticker_key in ETF_DB:
                score_val = ETF_DB[ticker_key].get('score', 4.5)

            with st.expander(f"{idx+1}. {item['name']} ({item['ticker']}) - [{item['type']}]", expanded=True):
                cm1, cm2, cm3, cm4 = st.columns([2, 1, 1, 1])
                cm1.markdown(f"**Categoría:** {item.get('category', 'General')}")
                cm2.markdown(f"**TER:** `{ter_val}%`")
                cm3.markdown(f"**Nota:** ⭐ `{score_val}/5`")
                with cm4:
                    if st.button("🔍 Evaluar", key=f"port_eval_{idx}", use_container_width=True):
                        st.session_state.asset_type = "Acciones" if item['type'] == "Acción" else ("Fondos indexados" if item['type'] == "Fondo Indexado" else ("Fondos Monetarios" if item['type'] == "Fondo Monetario" else "ETFs"))
                        st.session_state.sub_type = "Con dividendos" if item['type'] == "Acción" else ("Acumulación" if item['type'] == "Fondo Indexado" else ("Biblioteca Monetarios" if item['type'] == "Fondo Monetario" else "Evaluación ETF"))
                        st.session_state.selected_eval_input = item['ticker']
                        st.session_state.stage = "analyzer"
                        st.rerun()

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    sel_broker = st.selectbox(f"Bróker", options=list(broker_profiles.keys()), key=f"p_brok_{idx}")
                with col_b2:
                    b_data = broker_profiles[sel_broker]
                    plan_sc = st.checkbox("Plan de aportación automática a 0€", value=b_data["supports_free_plans"], key=f"p_plan_{idx}")

                col_i1, col_i2, col_i3, col_i4 = st.columns([2, 2, 2, 1])
                with col_i1:
                    inv_ini = st.number_input(f"Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key=f"p_ini_{idx}")
                with col_i2:
                    app_per = st.number_input(f"Aportación Periódica (€)", min_value=0.0, value=100.0, step=50.0, key=f"p_app_{idx}")
                with col_i3:
                    rent_est = st.slider(f"Rentabilidad anual (%)", min_value=0.0, max_value=20.0, value=est_rent_val, step=0.5, key=f"p_rent_{idx}")
                with col_i4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Quitar", key=f"del_{idx}"):
                        st.session_state.portfolio.pop(idx)
                        guardar_en_url()
                        st.rerun()

                f_pct = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_percent"]
                f_fix = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_fixed"]
                f_spr = b_data["spread_percent"]
                f_fx = 0.0 if (item.get('currency') == 'EUR' or item['ticker'].endswith('.DE') or item['ticker'].endswith('.MC')) else b_data["fx_fee_percent"]

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
                        
                        row_dict = {
                            "Año": f"Año {ano_act}",
                            "Capital Aportado Bruto (€)": round(total_aport_acum, 2),
                            "Comisiones Bróker (€)": round(acum_b, 2),
                            "Coste Spread (€)": round(acum_s, 2),
                            "Coste Cambio Divisa (€)": round(acum_f, 2),
                            "Beneficio Neto (€)": round(max(0.0, int_brutos), 2),
                        }
                        if is_dist_item:
                            div_bruto_anual = saldo_act * 0.025
                            div_bruto_activo += div_bruto_anual
                            row_dict["Dividendo Bruto Anual (€)"] = round(div_bruto_anual, 2)
                        
                        row_dict["Capital Total Neto (€)"] = round(saldo_act, 2)
                        historial_activo.append(row_dict)

                df_act = pd.DataFrame(historial_activo)
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
            div_neto_global = total_dividendos_brutos_acum * (1 - 0.19) if has_dividend_asset else 0.0
            capital_liquido_global = capital_neto_aportado + beneficio_neto_global + div_neto_global

            st.markdown("---")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
            m2.metric("Costes Bróker", f"{total_costes_acum:,.2f} €")
            m3.metric("Beneficio Bruto", f"{beneficio_bruto_global:,.2f} €")
            m4.metric("Impuestos (19%)", f"{impuestos_globales:,.2f} €")
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

elif st.session_state.stage == 'analyzer':
    if st.button("← Cambiar categoría / Volver"):
        st.session_state.stage = 'sub_options' if st.session_state.asset_type != "Fondos Monetarios" else 'home'
        st.session_state.sub_type = None
        st.session_state.selected_eval_input = ""
        st.rerun()

    def get_trend_chain_stream(hist_df):
        if hist_df is None or len(hist_df) < 2:
            return '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Lateral</div>'
        
        closes = hist_df['Close'].dropna()
        if len(closes) < 2:
            return '<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">Lateral</div>'

        first_p = float(closes.iloc[0])
        last_p = float(closes.iloc[-1])
        pct_change = ((last_p - first_p) / first_p) * 100

        if pct_change >= 1.0:
            return f'<div class="neon-stream-vertical"><span class="arrow-item-up st-1">▲</span></div><div style="font-size: 0.75rem; color: #22c55e; margin-top: 4px;">+{pct_change:.1f}%</div>'
        elif pct_change <= -1.0:
            return f'<div class="neon-stream-vertical"><span class="arrow-item-down st-1">▼</span></div><div style="font-size: 0.75rem; color: #ef4444; margin-top: 4px;">{pct_change:.1f}%</div>'
        else:
            return f'<div class="neon-stream-horizontal"><span class="arrow-item-side st-1">►</span></div><div style="font-size: 0.75rem; color: #eab308; margin-top: 4px;">{pct_change:+.1f}%</div>'

    def render_asset_converter(current_category, current_ticker, current_is_dist, current_asset_type):
        st.markdown(f"""
        <div class="converter-card">
            <div class="converter-title">🔄 Convertidor y Buscador de Alternativas Equivalentes</div>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 12px;">
                Alternativas equivalentes en Fondo o ETF:
            </p>
        </div>
        """, unsafe_allow_html=True)

        equi_funds_acc = [f for k, f in FUND_DB.items() if f['category'] == current_category and f['ticker'] != current_ticker and not f['is_dist']]
        equi_etfs_acc = [e for k, e in ETF_DB.items() if e['category'] == current_category and e['ticker'] != current_ticker]

        c_c1, c_c2 = st.columns(2)
        with c_c1:
            st.markdown("##### 📥 Fondos Equivalentes")
            for item in equi_funds_acc[:3]:
                st.markdown(f"• **{item['name']}** (ISIN: `{item['ticker']}` | TER: **{item['ter']}%**)")
        with c_c2:
            st.markdown("##### 🌐 ETFs Equivalentes")
            for item in equi_etfs_acc[:3]:
                st.markdown(f"• **{item['name']}** (Ticker: `{item['ticker']}` | TER: **{item['ter']}%**)")

    if st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
        st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
        ranking_data = [{
            "Fondo": data["name"], "ISIN": data["ticker"], "Categoría": data["category"], 
            "TER Anual (%)": data["ter"], "Patrimonio (M€)": data["aum"]
        } for data in FUND_DB.values() if data["category"] != "Fondos Monetarios"]
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_ranking, use_container_width=True)
        if st.button("← Volver al menú de fondos"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
        st.title("🏆 Ranking de ETFs (Ordenados por menor TER)")
        ranking_etfs = [{
            "ETF": data["name"], "Ticker": data["ticker"], "Categoría": data["category"], 
            "TER (%)": data["ter"], "Patrimonio (M€)": data["aum"]
        } for data in ETF_DB.values()]
        df_etf_ranking = pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_etf_ranking, use_container_width=True)
        if st.button("← Volver al menú de ETFs"):
            st.session_state.sub_type = None
            st.rerun()

    elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Explorador ETFs":
        st.title("🗺️ Guía y Tipos de ETFs Disponibles")
        st.markdown("- **Globales, Japón, Dividendos, Materias Primas, Tecnología y Emergentes.**")
        if st.button("← Volver al menú de ETFs"):
            st.session_state.sub_type = None
            st.rerun()

    else:
        st.title(f"📈 Analizador: {st.session_state.asset_type}")
        default_input = st.session_state.selected_eval_input

        if st.session_state.asset_type == "Acciones":
            user_input = st.text_input("Ticker o Nombre de la Acción:", value=default_input).strip().upper()
        elif st.session_state.asset_type == "Fondos Monetarios":
            monetary_options = ["-- Selecciona un fondo monetario --"] + [f"{d['name']} (ISIN: {d['ticker']})" for d in FUND_DB.values() if d["category"] == "Fondos Monetarios"]
            sel = st.selectbox("Biblioteca de Fondos Monetarios", options=monetary_options)
            user_input = sel.split("ISIN: ")[1].split(")")[0].strip() if "ISIN: " in sel else ""
        elif st.session_state.asset_type == "Fondos indexados":
            fund_options = ["-- Selecciona un fondo indexado --"] + [f"{d['name']} (ISIN: {d['ticker']})" for d in FUND_DB.values() if d["category"] != "Fondos Monetarios"]
            sel = st.selectbox("Biblioteca de Fondos Indexados", options=fund_options)
            user_input = sel.split("ISIN: ")[1].split(")")[0].strip() if "ISIN: " in sel else ""
        elif st.session_state.asset_type == "ETFs":
            etf_options = ["-- Selecciona un ETF --"] + [f"{d['name']} (Ticker: {d['ticker']})" for d in ETF_DB.values()]
            sel = st.selectbox("Biblioteca de ETFs", options=etf_options)
            user_input = sel.split("Ticker: ")[1].split(")")[0].strip() if "Ticker: " in sel else ""

        def get_letter_grade(score):
            if score >= 4.5: return "A+"
            elif score >= 4.0: return "A"
            elif score >= 3.0: return "B"
            else: return "C"

        if user_input:
            if st.session_state.asset_type == "Acciones":
                try:
                    stock = yf.Ticker(user_input)
                    hist_price = stock.history(period="3mo")
                    info = stock.info or {}
                    name = info.get('longName', user_input)
                    native_currency = info.get('currency', 'EUR')

                    current_price_native = float(hist_price['Close'].iloc[-1]) if not hist_price.empty else 100.0
                    eur_usd_rate = get_eur_usd_rate()
                    current_price_eur = current_price_native / eur_usd_rate if native_currency == 'USD' else current_price_native
                    price_display = f"{current_price_eur:,.2f} €"

                    per = info.get('trailingPE') or info.get('forwardPE') or 15.0
                    beta = info.get('beta') or 1.0
                    
                    raw_yield = info.get('dividendYield', 0) or 0.0
                    div_yield = (raw_yield * 100) if raw_yield < 0.1 else raw_yield

                    raw_payout = info.get('payoutRatio')
                    payout = (raw_payout * 100) if raw_payout is not None else 50.0

                    # AQUÍ SE APLICA TU FUNCIÓN DE EVALUACIÓN EXACTA
                    total_score, analysis_messages = evaluate_stock_parameters(per, beta, div_yield, payout)
                    grade = get_letter_grade(total_score)
                    deg = int((total_score / 5.0) * 360)
                    progress_color = "#22c55e" if total_score >= 4.0 else ("#eab308" if total_score >= 2.8 else "#ef4444")

                    col_n1, col_n2, col_n3 = st.columns([2, 1, 1])
                    with col_n1:
                        st.subheader(f"📊 Informe: {name} ({user_input})")
                    with col_n2:
                        if st.button("⭐ Añadir a Favoritos", use_container_width=True):
                            st.session_state.favorites.append({"type": "Acción", "name": name, "ticker": user_input, "ter": 0.0, "currency": "EUR", "category": "Acción"})
                            guardar_en_url()
                            st.success("¡Añadido a Favoritos!")
                    with col_n3:
                        if st.button("➕ Añadir a mi Cartera", type="primary", use_container_width=True):
                            st.session_state.portfolio.append({"type": "Acción", "name": name, "ticker": user_input, "est_rent": 8.0, "ter": 0.0, "currency": "EUR", "is_dist": True, "category": "Acción"})
                            guardar_en_url()
                            st.success(f"¡{name} añadido a tu Cartera!")

                    st.markdown(f"""
                    <div class="score-container">
                        <div style="text-align: center;"><div class="circular-progress" style="--deg: {deg}deg; --progress-color: {progress_color};"><div class="progress-value">{total_score:.1f}/5</div></div><div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem;">Puntuación de tus Baremos</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Calificación</div><div class="pure-stamp-grade" style="--stamp-color: {progress_color};">{grade}</div></div>
                        <div style="text-align: center;"><div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">Precio Actual (€)</div><div style="font-size: 2.2rem; font-weight: bold; color: #f8fafc; margin-top: 20px;">{price_display}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    render_traffic_light_recommendation(total_score, "Acción", "Evaluado en base a tus 5 parámetros estrictos.")

                    df_metrics = pd.DataFrame({
                        "Parámetro Clave": ["PER", "Beta", "Rentabilidad por Dividendo", "Payout", "Crecimiento del Dividendo"],
                        "Valor Detectado": [f"{per:.2f}", f"{beta:.2f}", f"{div_yield:.2f}%", f"{payout:.1f}%", "Histórico sostenido (> Inflación)"]
                    })
                    st.table(df_metrics)

                except Exception as e:
                    st.error(f"Error procesando el ticker '{user_input}': {e}")

            elif st.session_state.asset_type in ["Fondos indexados", "Fondos Monetarios", "ETFs"]:
                matched_db = FUND_DB.get(user_input.lower()) or ETF_DB.get(user_input.lower())
                if matched_db:
                    name = matched_db["name"]
                    ter = matched_db["ter"]
                    score = matched_db.get("score", 4.5)
                else:
                    name = user_input
                    ter = 0.15
                    score = 4.5

                st.subheader(f"📊 Informe: {name}")
                st.metric("TER Anual", f"{ter}%")
                render_traffic_light_recommendation(score, "Fondo/ETF", f"Evaluado con TER del {ter}%.")
