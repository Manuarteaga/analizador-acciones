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
        "desc": "Versión de distribución del fondo global MSCI World, ideal para inversores que prefieren 
