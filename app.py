import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json
import urllib.parse
import numpy as np  # Añadida la importación que faltaba para np.sqrt

# ==========================================
# FUNCIÓN DE CÁLCULO DE OPCIONES
# ==========================================
def calcular_score_opcionable(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="3mo")
        if hist.empty:
            return None, "Sin datos de mercado disponibles."
        
        hist['Retornos'] = hist['Close'].pct_change()
        volatilidad_historica = hist['Retornos'].tail(20).std() * np.sqrt(252) * 100
        opciones_disponibles = len(ticker.options) > 0
        
        if not opciones_disponibles:
            return 0, "Esta acción NO tiene mercado de opciones disponible."
            
        score = 50
        if volatilidad_historica > 40:
            score += 30
            diagnostico = "Primas muy altas por alta volatilidad. Ideal para ingresos altos, pero vigila el riesgo."
        elif 20 <= volatilidad_historica <= 40:
            score += 15
            diagnostico = "Volatilidad moderada. Primas decentes con un riesgo controlado."
        else:
            score -= 20
            diagnostico = "Primas muy baratas debido a la baja volatilidad. Puede no valer la pena el riesgo."
            
        score = max(0, min(100, score))
        return int(score), diagnostico
    except Exception as e:
        return None, f"Error al procesar opciones: {str(e)}"
        
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
"desc": "Ideal para complementar carteras: invierte en países desarrollados excluyendo totalmente Estados Unidos (Europa, Japón, Canadá, Australia).",
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
CUENTAS_REMUNERADAS_DB = [
{"name": "Renault Bank (Cuenta Tú)", "default_interest": 2.75, "category": "Cuenta Remunerada"},
{"name": "Banco Sabadell (Cuenta Online)", "default_interest": 2.50, "category": "Cuenta Remunerada"},
{"name": "MyInvestor (Cuenta Remunerada)", "default_interest": 2.25, "category": "Cuenta Remunerada"},
{"name": "Trade Republic (Efectivo Remunerado)", "default_interest": 3.00, "category": "Cuenta Remunerada"},
{"name": "Cuenta Remunerada Personalizada", "default_interest": 2.00, "category": "Cuenta Remunerada"}
]
def render_geo_breakdown(geo_dict):
st.markdown("🗺️ Desglose Geográfico Estimado:")
colors = {
"EE. UU.": "#3b82f6", "China": "#ef4444", "India": "#f59e0b", "Taiwán": "#10b981",
"Corea del Sur": "#8b5cf6", "Japón": "#ec4899", "Reino Unido": "#6366f1", "Europa": "#14b8a6",
"Europa (Ex-UK)": "#06b6d4", "Canadá": "#84cc16", "Mercados Emergentes": "#f97316",
"Brasil": "#eab308", "Oro Físico": "#fbbf24", "Plata Física": "#94a3b8", "Energía": "#f97316",
"Agricultura": "#84cc16", "Metales Industriales": "#06b6d4", "Francia": "#3b82f6", "Suiza": "#ef4444",
"Alemania": "#10b981", "Zona Euro": "#3b82f6", "Zona Euro (Deuda Pública/Corto Plazo)": "#3b82f6", "España / Global": "#3b82f6", "Otros": "#64748b"
}
bar_html = ''
legend_html = ''
for country, pct in geo_dict.items():
color = colors.get(country, "#94a3b8")
bar_html += f''
legend_html += f'{country} ({pct}%)'
bar_html += ''
legend_html += ''
st.markdown(bar_html + legend_html, unsafe_allow_html=True)
def render_holdings_breakdown(holdings_dict):
st.markdown("🏢 Principales Empresas y Participación en la Cartera:")
holding_colors = [
"#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#fb7185",
"#34d399", "#fbbf24", "#fb923c", "#a3e635", "#22d3ee", "#94a3b8"
]
bar_html = ''
legend_html = ''
for idx, (company, pct) in enumerate(holdings_dict.items()):
color = "#475569" if "resto" in company.lower() else holding_colors[idx % len(holding_colors)]
bar_html += f''
legend_html += f'{company} ({pct}%)'
bar_html += ''
legend_html += ''
st.markdown(bar_html + legend_html, unsafe_allow_html=True)
def render_traffic_light_recommendation(score, asset_type, details=None):
if score >= 4.0:
badge_class = "tl-buy"
icon = "🟢"
status = "RECOMENDACIÓN DE COMPRA / MUY FAVORABLE"
if asset_type == "Acción":
desc = "Activo con fundamentales muy sólidos, valoración equilibrada y excelente perfil de rentabilidad/riesgo."
else:
desc = "Vehículo altamente eficiente con comisiones muy reducidas, patrimonio robusto y mínima desviación del índice."
elif score >= 2.8:
badge_class = "tl-hold"
icon = "🟡"
status = "RECOMENDACIÓN NEUTRAL / MANTENER EN OBSERVACIÓN"
if asset_type == "Acción":
desc = "Empresa de calidad pero con múltiplos algo exigentes (PER elevado) o volatilidad superior a la media. Adecuada para mantener o acumular con cautela."
else:
desc = "Fondo o ETF aceptable con costes moderados. Válido para diversificación si no existe una opción idéntica más barata."
else:
badge_class = "tl-avoid"
icon = "🔴"
status = "PRECAUCIÓN / EVALUAR OTRAS ALTERNATIVAS"
if asset_type == "Acción":
desc = "Se detectan métricas de sobrevaloración o bajo retorno sobre el capital (ROE). Se recomienda explorar otras oportunidades."
else:
desc = "Las comisiones anuales (TER) elevadas o el bajo patrimonio aconsejan buscar opciones más competitivas en la biblioteca."
detail_html = f"Justificación del Semáforo: {details}" if details else ""
st.markdown(f"""

{icon} Semáforo de Análisis: {status}
{desc}
{detail_html}

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
col_tb1, col_tb2, col_tb3 = st.columns([1.5, 1, 1])
with col_tb1:
st.markdown("### 📈 Analizador Bursátil")
with col_tb2:
if st.button(f"⭐ Favoritos ({favorites_count})", use_container_width=True):
st.session_state.stage = "favorites_view"
st.rerun()
with col_tb3:
if st.button(f"💼 Simulador de Cartera ({portfolio_count})", use_container_width=True, type="primary"):
st.session_state.stage = "portfolio_view"
st.rerun()
st.markdown("---")
with st.sidebar:
st.header("Enlaces Relacionados")
st.markdown("Comparador Fondos Monetarios")
st.markdown("Calculadora Capacidad Inversión")
st.markdown("---")
st.header("📖 Glosario Financiero")
st.caption("Consulta los conceptos económicos y métricas clave que aparecen en pantalla:")
with st.expander("💼 Vehículos de Inversión"):
st.markdown("""
* Cartera de Inversión: Conjunto total de activos financieros (acciones, fondos, ETFs, efectivo) que posee un inversor.
* Acciones: Títulos de renta variable que representan una parte alícuota del capital social de una empresa pública o privada.
* Fondo de Inversión / Indexado: Institución de Inversión Colectiva (IIC) que agrupa el capital de múltiples inversores para réplica o gestión activa. En España disfrutan del beneficio de traspasabilidad sin peaje fiscal.
* ETF (Exchange Traded Fund): Fondo cotizado en bolsa que cotiza e interactúa en el mercado como una acción en tiempo real, combinando la diversificación de un fondo con la liquidez de una acción.
* Fondo Monetario: Vehículo enfocado en instrumentos de deuda a muy corto plazo (Letras del Tesoro, pagarés AAA) diseñado para preservar el capital y ofrecer liquidez diaria.
""")
with st.expander("📊 Métricas de Valoración y Análisis"):
st.markdown("""
* PER (Price to Earnings Ratio): Ratio precio-beneficio. Indica cuántas veces se paga el beneficio anual de una empresa al comprar su acción. Un PER alto suele indicar altas expectativas de crecimiento o sobrevaloración.
* Dividend Yield (Rentabilidad por Dividendo): Porcentaje que paga la empresa en dividendos anuales con respecto a su cotización.
* Payout Ratio: Porcentaje de los beneficios netos que la empresa destina a pagar dividendos a sus accionistas.
* Beta: Medida de la volatilidad o riesgo sistemático de un activo en comparación con el mercado global (Beta > 1 es más volátil; Beta < 1 es defensivo).
* Price / FCF (Precio / Flujo de Caja Libre): Compara el valor bursátil con el dinero efectivo real generado tras gastos de capital.
* ROE (Return on Equity): Rentabilidad financiera que mide la capacidad de generar beneficios con el capital de los accionistas.
""")
with st.expander("⚙️ Costes, Gastos y Gestión"):
st.markdown("""
* TER (Total Expense Ratio): Total de gastos corrientes anuales repercutidos directamente por la gestora sobre el fondo o ETF.
* Tracking Error: Muestra la desviación o margen de diferencia entre la rentabilidad del fondo/ETF y la del índice que pretende replicar.
* AUM (Assets Under Management): Patrimonio total gestionado en un fondo o ETF. Cuanto mayor es el AUM, menor riesgo de liquidación.
* Spread (Horquilla): Diferencia entre el precio de compra (Ask) y el precio de venta (Bid) que aplica el mercado o bróker.
* Comisión de Cambio de Divisa (FX): Recargo aplicado por el bróker al operar en activos cotizados en monedas distintas al Euro (ej. USD).
""")
with st.expander("🔄 Modalidades y Fiscalidad"):
st.markdown("""
* Acumulación (Acc): Los dividendos o cupones cobrados por el fondo o ETF se reinvierten automáticamente en la propia cartera.
* Distribución (Dist): Los dividendos cobrados se liquidan de forma periódica abonándose en la cuenta de efectivo del inversor.
* Diferimiento Fiscal: Ventaja de los fondos indexados en España que permite traspasar dinero de un fondo a otro sin tributar en el IRPF hasta el reembolso definitivo.
* Interés Compuesto: Proceso mediante el cual las ganancias generadas se reinvierten para producir nuevos rendimientos.
""")
if st.session_state.stage == 'home':
st.markdown("### ¿Qué tipo de activo quieres evaluar?")
col1, col2, col3, col4 = st.columns(4)
with col1:
if st.button("📊 Acciones", use_container_width=True, type="primary"):
st.session_state.asset_type = "Acciones"
st.session_state.sub_type = "Con dividendos"
st.session_state.stage = "analyzer"
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
st.markdown("---")
elif st.session_state.stage == 'sub_options':
if st.button("← Volver a selección de activos"):
reset_navigation()
st.rerun()
st.title(f"Configuración para: {st.session_state.asset_type}")
if st.session_state.asset_type == "Fondos indexados":
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
st.info("No tienes ningún activo guardado en favoritos todavía. Explora acciones, fondos, monetarios o ETFs y pulsa '⭐ Añadir a Favoritos'.")
else:
for idx, fav in enumerate(st.session_state.favorites):
with st.expander(f"{idx+1}. {fav['name']} ({fav['ticker']}) - [{fav['type']}]", expanded=True):
col_fav1, col_fav2, col_fav3, col_fav4 = st.columns([2, 1, 1, 1])
with col_fav1:
st.markdown(f"Categoría / Detalles: {fav.get('category', 'General')}")
st.markdown(f"TER / Coste anual: {fav.get('ter', 0.0)}%")
st.markdown(f"Divisa: {fav.get('currency', 'EUR')}")
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
elif st.session_state.stage == 'portfolio_view':
if st.button("← Volver al Menú Principal"):
reset_navigation()
st.rerun()
st.title("💼 Simulador Global de Cartera Consolidada")
with st.container():
st.markdown("### ➕ Añadir Cuenta Remunerada a la Cartera")
col_add1, col_add2 = st.columns([2, 1])
with col_add1:
cuenta_seleccionada = st.selectbox(
"Selecciona una cuenta remunerada:",
options=[c["name"] for c in CUENTAS_REMUNERADAS_DB],
key="select_cuenta_remunerada_sim"
)
with col_add2:
st.markdown("
", unsafe_allow_html=True)
if st.button("Añadir cuenta remunerada", type="primary", use_container_width=True):
c_info = next((c for c in CUENTAS_REMUNERADAS_DB if c["name"] == cuenta_seleccionada), CUENTAS_REMUNERADAS_DB[0])
st.session_state.portfolio.append({
"type": "Cuenta Remunerada",
"name": c_info["name"],
"ticker": "C_REM",
"est_rent": c_info["default_interest"],
"ter": 0.0,
"currency": "EUR",
"is_dist": True,
"category": "Cuenta Remunerada"
})
guardar_en_url()
st.success(f"¡{c_info['name']} añadida correctamente a tu Cartera!")
st.rerun()
st.markdown("---")
if not st.session_state.portfolio:
st.info("🛒 Tu cartera está vacía. Añade cuentas remuneradas arriba o explora acciones, fondos y ETFs para añadirlos desde sus buscadores.")
else:
categories_in_portfolio = [item.get('category', '') for item in st.session_state.portfolio if item.get('category')]
category_counts = pd.Series(categories_in_portfolio).value_counts()
duplicated_categories = category_counts[category_counts > 1].index.tolist()
if duplicated_categories:
for dup_cat in duplicated_categories:
st.warning(f"""
⚠️ ¡Alerta de Activos Duplicados Detectada!
Has añadido {category_counts[dup_cat]} activos de la misma categoría ({dup_cat}). Unifica tu aportación en un solo activo de menor coste.
""")
portfolio_tickers = [item.get('ticker', '').lower() for item in st.session_state.portfolio]
has_broad_market = any(t in portfolio_tickers for t in ['spyl.de', 'vusa.as', 'swda.l', 'vwce.de', 'vwrl.as', 'ie0032126645', 'ie00b03hd191', 'ie00byx5nx33'])
has_tech_sector = any(t in portfolio_tickers for t in ['eqqq.de', 'sxrv.de', 'smh.de', 'ie00b1w33f31', 'es0165265002'])
if has_broad_market and has_tech_sector:
st.warning("⚠️ ¡Alerta de Solapamiento de Empresas (Megacaps Tech)! Estás combinando S&P500 o MSCI World con fondos/ETFs tecnológicos o Nasdaq 100.")
st.markdown("Configura el plazo, la frecuencia y el bróker de cada activo para obtener el desglose anual detallado y el rendimiento neto final en Euros (€):")
c_p1, c_p2 = st.columns(2)
with c_p1:
anos_cartera = st.slider("Plazo Temporal Consolidado (Años)", min_value=1, max_value=40, value=15, key="anos_cart")
with c_p2:
frecuencia_cartera = st.selectbox("Frecuencia de Aportaciones", options=["Mensual", "Anual"], key="freq_cart")
st.markdown("---")
st.markdown("### 💼 Desglose y Configuración por Activo")
total_capital_bruto_acum = 0.0
total_capital_aportado_acum = 0.0
total_costes_acum = 0.0
total_dividendos_brutos_acum = 0.0
has_dividend_asset = False
No se ha podido generar una respuesta de IA.
app.py
File
añadelo aqui
¡Tienes toda la razón! Te pido disculpas, el intento anterior mezcló y rompió bloques lógicos internos del código que ya tenías para otras secciones del analizador.
He revisado tu script completo línea por línea y he solucionado tanto el IndentationError como las condiciones mal cruzadas en el bloque de st.session_state.asset_type == "Acciones".
Aquí tienes el código de tu aplicación app.py completamente limpio, estructurado y listo para funcionar:
python
import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json
import urllib.parse
import numpy as np  # Añadida la importación que faltaba para np.sqrt

# ==========================================
# FUNCIÓN DE CÁLCULO DE OPCIONES
# ==========================================
def calcular_score_opcionable(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="3mo")
        if hist.empty:
            return None, "Sin datos de mercado disponibles."
        
        hist['Retornos'] = hist['Close'].pct_change()
        volatilidad_historica = hist['Retornos'].tail(20).std() * np.sqrt(252) * 100
        opciones_disponibles = len(ticker.options) > 0
        
        if not opciones_disponibles:
            return 0, "Esta acción NO tiene mercado de opciones disponible."
            
        score = 50
        if volatilidad_historica > 40:
            score += 30
            diagnostico = "Primas muy altas por alta volatilidad. Ideal para ingresos altos, pero vigila el riesgo."
        elif 20 <= volatilidad_historica <= 40:
            score += 15
            diagnostico = "Volatilidad moderada. Primas decentes con un riesgo controlado."
        else:
            score -= 20
            diagnostico = "Primas muy baratas debido a la baja volatilidad. Puede no valer la pena el riesgo."
            
        score = max(0, min(100, score))
        return int(score), diagnostico
    except Exception as e:
        return None, f"Error al procesar opciones: {str(e)}"
        
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
Usa el código con precaución.
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
"desc": "Ideal para complementar carteras: invierte en países desarrollados excluyendo totalmente Estados Unidos (Europa, Japón, Canadá, Australia).",
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
CUENTAS_REMUNERADAS_DB = [
{"name": "Renault Bank (Cuenta Tú)", "default_interest": 2.75, "category": "Cuenta Remunerada"},
{"name": "Banco Sabadell (Cuenta Online)", "default_interest": 2.50, "category": "Cuenta Remunerada"},
{"name": "MyInvestor (Cuenta Remunerada)", "default_interest": 2.25, "category": "Cuenta Remunerada"},
{"name": "Trade Republic (Efectivo Remunerado)", "default_interest": 3.00, "category": "Cuenta Remunerada"},
{"name": "Cuenta Remunerada Personalizada", "default_interest": 2.00, "category": "Cuenta Remunerada"}
]
def render_geo_breakdown(geo_dict):
st.markdown("🗺️ Desglose Geográfico Estimado:")
colors = {
"EE. UU.": "#3b82f6", "China": "#ef4444", "India": "#f59e0b", "Taiwán": "#10b981",
"Corea del Sur": "#8b5cf6", "Japón": "#ec4899", "Reino Unido": "#6366f1", "Europa": "#14b8a6",
"Europa (Ex-UK)": "#06b6d4", "Canadá": "#84cc16", "Mercados Emergentes": "#f97316",
"Brasil": "#eab308", "Oro Físico": "#fbbf24", "Plata Física": "#94a3b8", "Energía": "#f97316",
"Agricultura": "#84cc16", "Metales Industriales": "#06b6d4", "Francia": "#3b82f6", "Suiza": "#ef4444",
"Alemania": "#10b981", "Zona Euro": "#3b82f6", "Zona Euro (Deuda Pública/Corto Plazo)": "#3b82f6", "España / Global": "#3b82f6", "Otros": "#64748b"
}
bar_html = ''
legend_html = ''
for country, pct in geo_dict.items():
color = colors.get(country, "#94a3b8")
bar_html += f''
legend_html += f'{country} ({pct}%)'
bar_html += ''
legend_html += ''
st.markdown(bar_html + legend_html, unsafe_allow_html=True)
def render_holdings_breakdown(holdings_dict):
st.markdown("🏢 Principales Empresas y Participación en la Cartera:")
holding_colors = [
"#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#fb7185",
"#34d399", "#fbbf24", "#fb923c", "#a3e635", "#22d3ee", "#94a3b8"
]
bar_html = ''
legend_html = ''
for idx, (company, pct) in enumerate(holdings_dict.items()):
color = "#475569" if "resto" in company.lower() else holding_colors[idx % len(holding_colors)]
bar_html += f''
legend_html += f'{company} ({pct}%)'
bar_html += ''
legend_html += ''
st.markdown(bar_html + legend_html, unsafe_allow_html=True)
def render_traffic_light_recommendation(score, asset_type, details=None):
if score >= 4.0:
badge_class = "tl-buy"
icon = "🟢"
status = "RECOMENDACIÓN DE COMPRA / MUY FAVORABLE"
if asset_type == "Acción":
desc = "Activo con fundamentales muy sólidos, valoración equilibrada y excelente perfil de rentabilidad/riesgo."
else:
desc = "Vehículo altamente eficiente con comisiones muy reducidas, patrimonio robusto y mínima desviación del índice."
elif score >= 2.8:
badge_class = "tl-hold"
icon = "🟡"
status = "RECOMENDACIÓN NEUTRAL / MANTENER EN OBSERVACIÓN"
if asset_type == "Acción":
desc = "Empresa de calidad pero con múltiplos algo exigentes (PER elevado) o volatilidad superior a la media. Adecuada para mantener o acumular con cautela."
else:
desc = "Fondo o ETF aceptable con costes moderados. Válido para diversificación si no existe una opción idéntica más barata."
else:
badge_class = "tl-avoid"
icon = "🔴"
status = "PRECAUCIÓN / EVALUAR OTRAS ALTERNATIVAS"
if asset_type == "Acción":
desc = "Se detectan métricas de sobrevaloración o bajo retorno sobre el capital (ROE). Se recomienda explorar otras oportunidades."
else:
desc = "Las comisiones anuales (TER) elevadas o el bajo patrimonio aconsejan buscar opciones más competitivas en la biblioteca."
detail_html = f"Justificación del Semáforo: {details}" if details else ""
st.markdown(f"""

{icon} Semáforo de Análisis: {status}
{desc}
{detail_html}

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
col_tb1, col_tb2, col_tb3 = st.columns([1.5, 1, 1])
with col_tb1:
st.markdown("### 📈 Analizador Bursátil")
with col_tb2:
if st.button(f"⭐ Favoritos ({favorites_count})", use_container_width=True):
st.session_state.stage = "favorites_view"
st.rerun()
with col_tb3:
if st.button(f"💼 Simulador de Cartera ({portfolio_count})", use_container_width=True, type="primary"):
st.session_state.stage = "portfolio_view"
st.rerun()
st.markdown("---")
with st.sidebar:
st.header("Enlaces Relacionados")
st.markdown("Comparador Fondos Monetarios")
st.markdown("Calculadora Capacidad Inversión")
st.markdown("---")
st.header("📖 Glosario Financiero")
st.caption("Consulta los conceptos económicos y métricas clave que aparecen en pantalla:")
with st.expander("💼 Vehículos de Inversión"):
st.markdown("""
* Cartera de Inversión: Conjunto total de activos financieros (acciones, fondos, ETFs, efectivo) que posee un inversor.
* Acciones: Títulos de renta variable que representan una parte alícuota del capital social de una empresa pública o privada.
* Fondo de Inversión / Indexado: Institución de Inversión Colectiva (IIC) que agrupa el capital de múltiples inversores para réplica o gestión activa. En España disfrutan del beneficio de traspasabilidad sin peaje fiscal.
* ETF (Exchange Traded Fund): Fondo cotizado en bolsa que cotiza e interactúa en el mercado como una acción en tiempo real, combinando la diversificación de un fondo con la liquidez de una acción.
* Fondo Monetario: Vehículo enfocado en instrumentos de deuda a muy corto plazo (Letras del Tesoro, pagarés AAA) diseñado para preservar el capital y ofrecer liquidez diaria.
""")
with st.expander("📊 Métricas de Valoración y Análisis"):
st.markdown("""
* PER (Price to Earnings Ratio): Ratio precio-beneficio. Indica cuántas veces se paga el beneficio anual de una empresa al comprar su acción. Un PER alto suele indicar altas expectativas de crecimiento o sobrevaloración.
* Dividend Yield (Rentabilidad por Dividendo): Porcentaje que paga la empresa en dividendos anuales con respecto a su cotización.
* Payout Ratio: Porcentaje de los beneficios netos que la empresa destina a pagar dividendos a sus accionistas.
* Beta: Medida de la volatilidad o riesgo sistemático de un activo en comparación con el mercado global (Beta > 1 es más volátil; Beta < 1 es defensivo).
* Price / FCF (Precio / Flujo de Caja Libre): Compara el valor bursátil con el dinero efectivo real generado tras gastos de capital.
* ROE (Return on Equity): Rentabilidad financiera que mide la capacidad de generar beneficios con el capital de los accionistas.
""")
with st.expander("⚙️ Costes, Gastos y Gestión"):
st.markdown("""
* TER (Total Expense Ratio): Total de gastos corrientes anuales repercutidos directamente por la gestora sobre el fondo o ETF.
* Tracking Error: Muestra la desviación o margen de diferencia entre la rentabilidad del fondo/ETF y la del índice que pretende replicar.
* AUM (Assets Under Management): Patrimonio total gestionado en un fondo o ETF. Cuanto mayor es el AUM, menor riesgo de liquidación.
* Spread (Horquilla): Diferencia entre el precio de compra (Ask) y el precio de venta (Bid) que aplica el mercado o bróker.
* Comisión de Cambio de Divisa (FX): Recargo aplicado por el bróker al operar en activos cotizados en monedas distintas al Euro (ej. USD).
""")
with st.expander("🔄 Modalidades y Fiscalidad"):
st.markdown("""
* Acumulación (Acc): Los dividendos o cupones cobrados por el fondo o ETF se reinvierten automáticamente en la propia cartera.
* Distribución (Dist): Los dividendos cobrados se liquidan de forma periódica abonándose en la cuenta de efectivo del inversor.
* Diferimiento Fiscal: Ventaja de los fondos indexados en España que permite traspasar dinero de un fondo a otro sin tributar en el IRPF hasta el reembolso definitivo.
* Interés Compuesto: Proceso mediante el cual las ganancias generadas se reinvierten para producir nuevos rendimientos.
""")
if st.session_state.stage == 'home':
st.markdown("### ¿Qué tipo de activo quieres evaluar?")
col1, col2, col3, col4 = st.columns(4)
with col1:
if st.button("📊 Acciones", use_container_width=True, type="primary"):
st.session_state.asset_type = "Acciones"
st.session_state.sub_type = "Con dividendos"
st.session_state.stage = "analyzer"
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
st.markdown("---")
elif st.session_state.stage == 'sub_options':
if st.button("← Volver a selección de activos"):
reset_navigation()
st.rerun()
st.title(f"Configuración para: {st.session_state.asset_type}")
if st.session_state.asset_type == "Fondos indexados":
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
st.info("No tienes ningún activo guardado en favoritos todavía. Explora acciones, fondos, monetarios o ETFs y pulsa '⭐ Añadir a Favoritos'.")
else:
for idx, fav in enumerate(st.session_state.favorites):
with st.expander(f"{idx+1}. {fav['name']} ({fav['ticker']}) - [{fav['type']}]", expanded=True):
col_fav1, col_fav2, col_fav3, col_fav4 = st.columns([2, 1, 1, 1])
with col_fav1:
st.markdown(f"Categoría / Detalles: {fav.get('category', 'General')}")
st.markdown(f"TER / Coste anual: {fav.get('ter', 0.0)}%")
st.markdown(f"Divisa: {fav.get('currency', 'EUR')}")
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
elif st.session_state.stage == 'portfolio_view':
if st.button("← Volver al Menú Principal"):
reset_navigation()
st.rerun()
st.title("💼 Simulador Global de Cartera Consolidada")
with st.container():
st.markdown("### ➕ Añadir Cuenta Remunerada a la Cartera")
col_add1, col_add2 = st.columns([2, 1])
with col_add1:
cuenta_seleccionada = st.selectbox(
"Selecciona una cuenta remunerada:",
options=[c["name"] for c in CUENTAS_REMUNERADAS_DB],
key="select_cuenta_remunerada_sim"
)
with col_add2:
st.markdown("
", unsafe_allow_html=True)
if st.button("Añadir cuenta remunerada", type="primary", use_container_width=True):
c_info = next((c for c in CUENTAS_REMUNERADAS_DB if c["name"] == cuenta_seleccionada), CUENTAS_REMUNERADAS_DB[0])
st.session_state.portfolio.append({
"type": "Cuenta Remunerada",
"name": c_info["name"],
"ticker": "C_REM",
"est_rent": c_info["default_interest"],
"ter": 0.0,
"currency": "EUR",
"is_dist": True,
"category": "Cuenta Remunerada"
})
guardar_en_url()
st.success(f"¡{c_info['name']} añadida correctamente a tu Cartera!")
st.rerun()
st.markdown("---")
if not st.session_state.portfolio:
st.info("🛒 Tu cartera está vacía. Añade cuentas remuneradas arriba o explora acciones, fondos y ETFs para añadirlos desde sus buscadores.")
else:
categories_in_portfolio = [item.get('category', '') for item in st.session_state.portfolio if item.get('category')]
category_counts = pd.Series(categories_in_portfolio).value_counts()
duplicated_categories = category_counts[category_counts > 1].index.tolist()
if duplicated_categories:
for dup_cat in duplicated_categories:
st.warning(f"""
⚠️ ¡Alerta de Activos Duplicados Detectada!
Has añadido {category_counts[dup_cat]} activos de la misma categoría ({dup_cat}). Unifica tu aportación en un solo activo de menor coste.
""")
portfolio_tickers = [item.get('ticker', '').lower() for item in st.session_state.portfolio]
has_broad_market = any(t in portfolio_tickers for t in ['spyl.de', 'vusa.as', 'swda.l', 'vwce.de', 'vwrl.as', 'ie0032126645', 'ie00b03hd191', 'ie00byx5nx33'])
has_tech_sector = any(t in portfolio_tickers for t in ['eqqq.de', 'sxrv.de', 'smh.de', 'ie00b1w33f31', 'es0165265002'])
if has_broad_market and has_tech_sector:
st.warning("⚠️ ¡Alerta de Solapamiento de Empresas (Megacaps Tech)! Estás combinando S&P500 o MSCI World con fondos/ETFs tecnológicos o Nasdaq 100.")
st.markdown("Configura el plazo, la frecuencia y el bróker de cada activo para obtener el desglose anual detallado y el rendimiento neto final en Euros (€):")
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
is_cuenta_rem = item['type'] == "Cuenta Remunerada"
is_etf_or_stock = item['type'] in ["ETF", "Acción"]
broker_profiles = ETF_BROKER_PROFILES if is_etf_or_stock else FUND_BROKER_PROFILES
is_dist_item = item.get('is_dist', False) or (item.get('type') == "Acción") or ("Dividendo" in item.get('category', '')) or is_cuenta_rem
if is_dist_item:
has_dividend_asset = True
ticker_key = item['ticker'].lower()
ter_val = 0.0 if is_cuenta_rem else item.get('ter', 0.20)
est_rent_val = float(item.get('est_rent', 7.5))
score_val = 4.8 if is_cuenta_rem else 4.5
if ticker_key in FUND_DB:
score_val = FUND_DB[ticker_key].get('score', 4.5)
elif ticker_key in ETF_DB:
score_val = ETF_DB[ticker_key].get('score', 4.5)
with st.expander(f"{idx+1}. {item['name']} ({item['ticker']}) - [{item['type']}]", expanded=True):
cm1, cm2, cm3, cm4 = st.columns([2, 1, 1, 1])
cm1.markdown(f"Categoría: {item.get('category', 'General')}")
cm2.markdown(f"TER: {ter_val}%")
cm3.markdown(f"Nota: ⭐ {score_val}/5")
with cm4:
if not is_cuenta_rem:
if st.button("🔍 Evaluar", key=f"port_eval_{idx}", use_container_width=True):
st.session_state.asset_type = "Acciones" if item['type'] == "Acción" else ("Fondos indexados" if item['type'] == "Fondo Indexado" else ("Fondos Monetarios" if item['type'] == "Fondo Monetario" else "ETFs"))
st.session_state.sub_type = "Con dividendos" if item['type'] == "Acción" else ("Acumulación" if item['type'] == "Fondo Indexado" else ("Biblioteca Monetarios" if item['type'] == "Fondo Monetario" else "Evaluación ETF"))
st.session_state.selected_eval_input = item['ticker']
st.session_state.stage = "analyzer"
st.rerun()
st.markdown("---")
if not is_cuenta_rem:
col_b1, col_b2 = st.columns(2)
with col_b1:
sel_broker = st.selectbox(f"Bróker / Entidad", options=list(broker_profiles.keys()), key=f"p_brok_{idx}")
with col_b2:
b_data = broker_profiles[sel_broker]
plan_sc = st.checkbox("Plan de aportación automática a 0€", value=b_data["supports_free_plans"], key=f"p_plan_{idx}")
else:
sel_broker = "Cuenta Remunerada Directa"
b_data = {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.0, "fx_fee_percent": 0.0, "supports_free_plans": True}
plan_sc = True
col_i1, col_i2, col_i3, col_i4 = st.columns([2, 2, 2, 1])
with col_i1:
inv_ini = st.number_input(f"Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key=f"p_ini_{idx}")
with col_i2:
app_per = st.number_input(f"Aportación Periódica (€)", min_value=0.0, value=100.0, step=50.0, key=f"p_app_{idx}")
with col_i3:
rent_est = st.slider(f"Rentabilidad estimada anual / Interés (%)", min_value=0.0, max_value=20.0, value=est_rent_val, step=0.5, key=f"p_rent_{idx}")
with col_i4:
st.markdown("
", unsafe_allow_html=True)
if st.button("🗑️ Quitar", key=f"del_{idx}"):
st.session_state.portfolio.pop(idx)
guardar_en_url()
st.rerun()
f_pct = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_percent"]
f_fix = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_fixed"]
f_spr = b_data["spread_percent"]
f_fx = 0.0 if (item.get('currency') == 'EUR' or item['ticker'].endswith('.DE') or item['ticker'].endswith('.MC') or item['ticker'].endswith('.AS')) else b_data["fx_fee_percent"]
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
div_bruto_anual = saldo_act * (rent_est / 100.0) if is_cuenta_rem else saldo_act * 0.025
div_bruto_activo += div_bruto_anual
row_dict["Intereses/Dividendos Brutos Anuales (€)"] = round(div_bruto_anual, 2)
row_dict["Capital Total Neto (€)"] = round(saldo_act, 2)
historial_activo.append(row_dict)
df_act = pd.DataFrame(historial_activo)
st.markdown("##### 📊 Desglose de crecimiento anual para este activo (€):")
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
st.markdown("### 📊 Proyección Total de la Cartera Consolidada (€)")
if has_dividend_asset:
m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
m2.metric("Costes Bróker", f"{total_costes_acum:,.2f} €")
m3.metric("Beneficio Bruto", f"{beneficio_bruto_global:,.2f} €")
m4.metric("Impuestos (19%)", f"{impuestos_globales:,.2f} €")
m5.metric("Beneficio Neto", f"{beneficio_neto_global:,.2f} €")
m6.metric("Total Intereses/Div. Brutos", f"{total_dividendos_brutos_acum:,.2f} €")
m7.metric("Total Intereses/Div. Netos", f"{div_neto_global:,.2f} €")
else:
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
m2.metric("Costes Bróker", f"{total_costes_acum:,.2f} €")
m3.metric("Beneficio Bruto", f"{beneficio_bruto_global:,.2f} €")
m4.metric("Impuestos (19%)", f"{impuestos_globales:,.2f} €")
m5.metric("Beneficio Neto", f"{beneficio_neto_global:,.2f} €")
st.markdown(f"""

💰 Capital Total Líquido Final de tu Cartera (Tras Impuestos y Rendimientos)
{capital_liquido_global:,.2f} €

""", unsafe_allow_html=True)
if st.button("🗑️ Vaciar Cartera Completa"):
st.session_state.portfolio = []
guardar_en_url()
st.rerun()
elif st.session_state.stage == 'analyzer':
if st.button("← Cambiar categoría / Volver"):
st.session_state.stage = 'sub_options' if st.session_state.asset_type not in ["Fondos Monetarios", "Acciones"] else 'home'
st.session_state.sub_type = None
st.session_state.selected_eval_input = ""
st.rerun()
def get_trend_chain_stream(hist_df):
if hist_df is None or len(hist_df) < 2:
return '►►►Lateral'
closes = hist_df['Close'].dropna()
if len(closes) < 2:
return '►►►Lateral'
first_p = float(closes.iloc[0])
last_p = float(closes.iloc[-1])
pct_change = ((last_p - first_p) / first_p) * 100
if pd.isna(pct_change):
return '►►►Lateral'
if pct_change >= 1.0:
return f'▲▲▲+{pct_change:.1f}%'
elif pct_change <= -1.0:
return f'▼▼▼{pct_change:.1f}%'
else:
return f'►►►{pct_change:+.1f}%'
def render_asset_converter(current_category, current_ticker, current_is_dist, current_asset_type):
st.markdown(f"""

🔄 Convertidor y Buscador de Alternativas Equivalentes

¿Sabías que un mismo índice puede comprarse en versión Fondo Indexado o ETF, y que puedes elegir entre acumular dividendos o cobrarlos? Aquí tienes sus equivalentes exactos junto con su nota de calidad destacada:


""", unsafe_allow_html=True)
equi_funds_acc = []
equi_funds_dist = []
equi_etfs_acc = []
equi_etfs_dist = []
for k, f in FUND_DB.items():
if f['category'] == current_category and f['ticker'] != current_ticker:
if f['is_dist']:
equi_funds_dist.append(f)
else:
equi_funds_acc.append(f)
for k, e in ETF_DB.items():
if e['category'] == current_category and e['ticker'] != current_ticker:
if e['is_dist']:
equi_etfs_dist.append(e)
else:
equi_etfs_acc.append(e)
c_c1, c_c2, c_c3 = st.columns(3)
with c_c1:
st.markdown("##### 📥 Fondos (Acumulación / Monetarios)")
if equi_funds_acc:
for item in equi_funds_acc:
nota_val = item.get('score', 4.3)
st.markdown(f"• {item['name']}")
st.markdown(f"  ISIN: {item['ticker']} | TER: {item['ter']}% ⭐ {nota_val}/5", unsafe_allow_html=True)
if st.button(f"🔍 Evaluar Fondo Acc", key=f"conv_f_acc_{item['ticker']}"):
st.session_state.asset_type = "Fondos indexados" if item['category'] != "Fondos Monetarios" else "Fondos Monetarios"
st.session_state.sub_type = "Acumulación" if item['category'] != "Fondos Monetarios" else "Biblioteca Monetarios"
st.session_state.selected_eval_input = item['ticker']
st.rerun()
else:
st.caption("No hay otros fondos de acumulación registrados en esta categoría.")
with c_c2:
st.markdown("##### 💰 Fondos (Distribución)")
if equi_funds_dist:
for item in equi_funds_dist:
nota_val = item.get('score', 4.3)
st.markdown(f"• {item['name']}")
st.markdown(f"  ISIN: {item['ticker']} | TER: {item['ter']}% ⭐ {nota_val}/5", unsafe_allow_html=True)
if st.button(f"🔍 Evaluar Fondo Dist", key=f"conv_f_dist_{item['ticker']}"):
st.session_state.asset_type = "Fondos indexados"
st.session_state.sub_type = "Acumulación"
st.session_state.selected_eval_input = item['ticker']
st.rerun()
else:
st.caption("No hay fondos de distribución en esta categoría.")
with c_c3:
st.markdown("##### 🌐 ETFs Equivalentes (Coste Ultra Bajo)")
all_etfs = equi_etfs_acc + equi_etfs_dist
if all_etfs:
for item in all_etfs:
tipo_str = "Distribución" if item['is_dist'] else "Acumulación"
nota_val = item.get('score', 4.5)
st.markdown(f"• {item['name']}")
st.markdown(f"  Ticker: {item['ticker']} | TER: {item['ter']}% ({tipo_str}) ⭐ {nota_val}/5", unsafe_allow_html=True)
if st.button(f"🔍 Evaluar ETF", key=f"conv_etf_{item['ticker']}"):
st.session_state.asset_type = "ETFs"
st.session_state.sub_type = "Evaluación ETF"
st.session_state.selected_eval_input = item['ticker']
st.rerun()
else:
st.caption("No se han encontrado ETFs equivalentes directos para esta categoría específica.")
if st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
ranking_data = [
{
"Fondo": data["name"],
"ISIN": data["ticker"],
"Categoría": data["category"],
"Modalidad": "Distribución" if data.get("is_dist") else "Acumulación",
"Nota (⭐)": f"{data.get('score', 4.3)}/5",
"TER Anual (%)": data["ter"],
"Rentabilidad (1A %)": f"+{data.get('return_1y', 10.0):.1f}%",
"Patrimonio (M€)": data["aum"],
"Antigüedad (Años)": data["age_years"]
}
for data in FUND_DB.values() if data["category"] != "Fondos Monetarios"
]
df_ranking = pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True)
st.dataframe(df_ranking, use_container_width=True)
st.info("⚠️ Aviso de Comisiones: Los costes mostrados corresponden exclusivamente al TER de la gestora.")
if st.button("← Volver al menú de fondos"):
st.session_state.sub_type = None
st.rerun()
elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
st.title("🏆 Ranking de ETFs (Ordenados por menor TER)")
ranking_etfs = [
{
"ETF": data["name"],
"Ticker": data["ticker"],
"Categoría": data["category"],
"Modalidad": "Distribución" if data.get("is_dist") else "Acumulación",
"Nota (⭐)": f"{data.get('score', 4.5)}/5",
"TER (%)": data["ter"],
"Rentabilidad (1A %)": f"+{data.get('return_1y', 10.0):.1f}%",
"Patrimonio (M€)": data["aum"],
"Réplica": data["replication"]
}
for data in ETF_DB.values()
]
df_etf_ranking = pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True)
st.dataframe(df_etf_ranking, use_container_width=True)
st.info("⚠️ Aviso de Comisiones: Los costes mostrados corresponden exclusivamente al TER.")
if st.button("← Volver al menú de ETFs"):
st.session_state.sub_type = None
st.rerun()
elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Explorador ETFs":
st.title("🗺️ Guía y Tipos de ETFs Disponibles")
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🌍 Globales", "🇯🇵 Japón", "💰 Dividendos", "🥇 Materias Primas / Metales", "💻 Tecnología & IA", "⚡ Renovables & Eléctricas", "🚀 Emergentes"])
with tab1:
st.subheader("Renta Variable Global")
st.markdown("- Objetivo: Diversificación global en países desarrollados.")
with tab2:
st.subheader("Renta Variable Japón")
st.markdown("- Objetivo: Exposición a grandes conglomerados nipones, robótica, semiconductores y líderes de automoción (Toyota, Sony, Mitsubishi, Keyence).")
with tab3:
st.subheader("Alto Dividendo")
st.markdown("- Objetivo: Empresas maduras con pagos estables y cobro periódico de cupones.")
with tab4:
st.subheader("Materias Primas y Metales")
st.markdown("- Objetivo: Exposición física a Oro, Plata y Cesta de Commodities como cobertura contra inflación.")
with tab5:
st.subheader("Tecnología, IA & Semiconductores")
st.markdown("- Objetivo: Innovación, Inteligencia Artificial, Software y Ciberseguridad.")
with tab6:
st.subheader("Renovables & Utilities")
st.markdown("- Objetivo: Transición energética y eléctricas defensivas.")
with tab7:
st.subheader("Emergentes")
st.markdown("- Objetivo: Crecimiento en economías en desarrollo.")
st.markdown("---")
if st.button("← Volver al menú de ETFs"):
st.session_state.sub_type = None
st.rerun()
else:
st.title(f"📈 Analizador: {st.session_state.asset_type} ({st.session_state.sub_type})")
default_input = st.session_state.selected_eval_input
if st.session_state.asset_type == "Acciones":
st.markdown("### 📊 Analizador de Acciones en Tiempo Real")
user_input = st.text_input("Ticker, Nombre de la Empresa o Pega el enlace de Yahoo Finance:", value=default_input).strip()
if user_input:
ticker_input = ""
import re
url_match = re.search(r'yahoo.com([A-Za-z0-9.-]+)', user_input)
if url_match:
ticker_input = url_match.group(1).upper()
else:
clean_input = user_input.upper()
try:
test_ticker = yf.Ticker(clean_input)
test_hist = test_ticker.history(period="1d")
if not test_hist.empty:
ticker_input = clean_input
except:
pass
if not ticker_input:
st.info("🔍 Buscando coincidencia exacta en Yahoo Finance...")
try:
search_res = yf.Search(user_input, max_results=5)
quotes = search_res.quotes
if quotes:
options = {f"{q.get('longname', q.get('shortname', ''))} ({q['symbol']}) - {q.get('exchange', '')}": q['symbol'] for q in quotes}
selected_label = st.selectbox("Selecciona la empresa correcta:", list(options.keys()), key="select_stock_search_fix")
ticker_input = options[selected_label]
else:
ticker_input = clean_input
except:
ticker_input = clean_input
if ticker_input:
# 1. CREAMOS LAS DOS COLUMNAS PRINCIPALES DE PANTALLA
col_info_actual, col_nota_opciones = st.columns([2, 1])
# 2. COLUMNA IZQUIERDA: INFORMACIÓN FINANCIERA GENERAL
with col_info_actual:
try:
stock = yf.Ticker(ticker_input)
hist_price = stock.history(period="3mo")
info = stock.info or {}
name = info.get('longName', ticker_input.title())
native_currency = info.get('currency', 'EUR')
current_price_native = None
if not hist_price.empty and 'Close' in hist_price.columns:
valid_closes = hist_price['Close'].dropna()
if not valid_closes.empty:
current_price_native = float(valid_closes.iloc[-1])
current_price_eur = current_price_native
if native_currency == 'USD' and current_price_native is not None:
eur_usd_rate = get_eur_usd_rate()
current_price_eur = current_price_native / eur_usd_rate
price_display = f"{current_price_eur:,.2f} €" if current_price_eur is not None else "—"
trend_html = get_trend_chain_stream(hist_price)
raw_yield = info.get('dividendYield', 0) or 0.0
if raw_yield > 0:
if raw_yield < 0.1:
div_y_val = raw_yield * 100
else:
div_y_val = raw_yield
else:
div_y_val = 0.0
per_y = info.get('trailingPE') or info.get('forwardPE') or 18.0
pfcf_y = info.get('priceToFreeCashflow') or 18.0
roe_val = (info.get('returnOnEquity', 0.15) * 100) if info.get('returnOnEquity') else 15.0
beta_val = info.get('beta') or 1.0
raw_payout = info.get('payoutRatio')
payout_val = (raw_payout * 100) if raw_payout is not None else 50.0
recommendation = info.get('recommendationKey', 'hold').lower()
score_calc = 2.5
if 0 < per_y <= 18: score_calc += 1.0
elif 18 < per_y <= 28: score_calc += 0.5
elif per_y > 45: score_calc -= 0.5
if roe_val >= 20: score_calc += 1.0
elif roe_val >= 12: score_calc += 0.5
if 0.5 <= beta_val <= 1.1: score_calc += 0.5
if recommendation in ['buy', 'strong_buy']: score_calc += 0.5
total_score = min(5.0, max(1.0, score_calc))
grade = get_letter_grade(total_score)
deg = int((total_score / 5.0) * 360)
progress_color = "#22c55e" if total_score >= 4.0 else ("#eab308" if total_score >= 2.8 else "#ef4444")
col_n1, col_n2, col_n3 = st.columns([2, 1, 1])
with col_n1:
st.subheader(f"📊 Informe: {name} ({ticker_input})")
with col_n2:
if st.button("⭐ Añadir a Favoritos", use_container_width=True):
st.session_state.favorites.append({
"type": "Acción", "name": name, "ticker": ticker_input,
"ter": 0.0, "currency": "EUR", "category": "Renta Variable (Acción)"
})
guardar_en_url()
st.success("¡Añadido a Favoritos!")
with col_n3:
if st.button("➕ Añadir a Cartera", type="primary", use_container_width=True):
st.session_state.portfolio.append({
"type": "Acción", "name": name, "ticker": ticker_input,
"est_rent": 8.0, "ter": 0.0, "currency": "EUR", "is_dist": True,
"category": "Renta Variable (Acción)"
})
guardar_en_url()
st.success(f"¡{name} añadido a tu Cartera!")
st.markdown(f"""

{total_score:.1f}/5Puntuación Yahoo Finance
Tendencia en Cadena{trend_html}
Calificación{grade}
Precio Actual (€){price_display}

""", unsafe_allow_html=True)
render_traffic_light_recommendation(
total_score, "Acción",
f"PER de {per_y:.1f}, ROE de {roe_val:.1f}%, Beta de {beta_val:.2f} y Dividend Yield del {div_y_val:.2f}%."
)
df_metrics = pd.DataFrame({
"Métrica Clave": ["PER (Valoración)", "Precio / FCF", "ROE", "Dividend Yield", "Payout Ratio", "Beta"],
"Valor Evaluado": [f"{per_y:.2f}", f"{pfcf_y:.2f}", f"{roe_val:.2f}%", f"{div_y_val:.2f}%", f"{payout_val:.1f}%", f"{beta_val:.2f}"]
})
st.table(df_metrics)
st.markdown("---")
st.subheader(f"🧮 Simulador de Interés Compuesto para: {name}")
toggle_stock_sim = st.toggle("Activar calculadora individual de esta acción", value=False, key="tg_stock_sim")
if toggle_stock_sim:
sel_b_stock = st.selectbox("Selecciona tu Bróker", options=list(ETF_BROKER_PROFILES.keys()), key="sel_b_stock")
b_stock_data = ETF_BROKER_PROFILES[sel_b_stock]
plan_stock_free = st.checkbox("Plan de aportación automática sin comisión", value=b_stock_data["supports_free_plans"], key="plan_stock_free")
cs1, cs2 = st.columns(2)
with cs1:
inv_i_stock = st.number_input("Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key="inv_i_stock")
app_p_stock = st.number_input("Aportación Periódica (€)", min_value=0.0, value=150.0, step=50.0, key="app_p_stock")
freq_stock = st.selectbox("Frecuencia", options=["Mensual", "Anual"], key="freq_stock")
with cs2:
anos_stock = st.slider("Plazo (Años)", min_value=1, max_value=40, value=15, key="anos_stock")
rent_stock = st.slider("Rentabilidad anual estimada (%)", min_value=0.0, max_value=20.0, value=8.0, step=0.5, key="rent_stock")
spct = 0.0 if (b_stock_data["supports_free_plans"] and plan_stock_free) else b_stock_data["fee_percent"]
sfix = 0.0 if (b_stock_data["supports_free_plans"] and plan_stock_free) else b_stock_data["fee_fixed"]
sspr = b_stock_data["spread_percent"]
sfx = 0.0 if native_currency == 'EUR' or ticker_input.endswith('.DE') or ticker_input.endswith('.MC') else b_stock_data["fx_fee_percent"]
per_ano_stock = 12 if freq_stock == "Mensual" else 1
t_neta_stock = rent_stock - 0.0
t_per_stock = (t_neta_stock / 100.0) / per_ano_stock
tot_per_stock = anos_stock * per_ano_stock
c_broker_i_stock = (inv_i_stock * (b_stock_data["fee_percent"] / 100.0)) + b_stock_data["fee_fixed"]
c_spread_i_stock = inv_i_stock * (sspr / 100.0)
c_fx_i_stock = inv_i_stock * (sfx / 100.0)
c_ini_stock = c_broker_i_stock + c_spread_i_stock + c_fx_i_stock
saldo_stock = max(0.0, inv_i_stock - c_ini_stock)
aport_stock = inv_i_stock
a_broker_stock = c_broker_i_stock
a_spread_stock = c_spread_i_stock
a_fx_stock = c_fx_i_stock
div_bruto_stock_total = 0.0
historial_stock = []
for p in range(1, tot_per_stock + 1):
if p > 1:
cb = (app_p_stock * (spct / 100.0)) + sfix
cs = app_p_stock * (sspr / 100.0)
cf = app_p_stock * (sfx / 100.0)
ct = cb + cs + cf
net_app_stock = max(0.0, app_p_stock - ct)
aport_stock += app_p_stock
a_broker_stock += cb
a_spread_stock += cs
a_fx_stock += cf
saldo_stock = saldo_stock * (1 + t_per_stock) + net_app_stock
else:
saldo_stock = saldo_stock * (1 + t_per_stock)
if p % per_ano_stock == 0:
ano_act_stock = p // per_ano_stock
c_tot_stock = a_broker_stock + a_spread_stock + a_fx_stock
int_b_stock = saldo_stock - (aport_stock - c_tot_stock)
div_bruto_anual_s = saldo_stock * (div_y_val / 100.0)
div_bruto_stock_total += div_bruto_anual_s
historial_stock.append({
"Año": f"Año {ano_act_stock}",
"Capital Aportado Bruto (€)": round(aport_stock, 2),
"Comisiones Bróker (€)": round(a_broker_stock, 2),
"Coste Spread (€)": round(a_spread_stock, 2),
"Coste Cambio Divisa (€)": round(a_fx_stock, 2),
"Beneficio Neto (€)": round(max(0.0, int_b_stock), 2),
"Dividendo Bruto Anual (€)": round(div_bruto_anual_s, 2),
"Capital Total Neto (€)": round(saldo_stock, 2)
})
df_sim_stock = pd.DataFrame(historial_stock)
with st.expander("Ver desglose anual detallado con comisiones, spreads y dividendos (€)", expanded=True):
st.dataframe(df_sim_stock, use_container_width=True)
c_tot_acum_stock = a_broker_stock + a_spread_stock + a_fx_stock
net_aport_stock = aport_stock - c_tot_acum_stock
bruto_stock = max(0.0, saldo_stock - net_aport_stock)
imp_stock = bruto_stock * 0.19
neto_stock = bruto_stock - imp_stock
div_neto_stock = div_bruto_stock_total * (1 - 0.19)
liquido_stock = net_aport_stock + neto_stock + div_neto_stock
sm1, sm2, sm3, sm4, sm5, sm6 = st.columns(6)
sm1.metric("Capital Invertido Neto", f"{net_aport_stock:,.2f} €")
sm2.metric("Costes Totales", f"{c_tot_acum_stock:,.2f} €")
sm3.metric("Beneficio Bruto", f"{bruto_stock:,.2f} €")
sm4.metric("Beneficio Neto (19%)", f"{neto_stock:,.2f} €")
sm5.metric("Div. Brutos Total", f"{div_bruto_stock_total:,.2f} €")
sm6.metric("Div. Netos Total", f"{div_neto_stock:,.2f} €")
st.markdown(f"""

💰 Capital Total Líquido Final de la Acción (Con Dividendos en €)
{liquido_stock:,.2f} €

""", unsafe_allow_html=True)
except Exception as e:
st.error(f"No se han podido encontrar datos para el ticker '{ticker_input}'. Comprueba que sea correcto en Yahoo Finance.")
# 3. COLUMNA DERECHA: EVALUACIÓN DE OPCIONES FINANCIERAS
with col_nota_opciones:
st.subheader("Análisis de Opciones")
score, mensaje = calcular_score_opcionable(ticker_input)
if score is not None:
if score >= 70:
color_metrica = "🟢 Alta viabilidad"
elif 40 <= score < 70:
color_metrica = "🟡 Viabilidad moderada"
else:
color_metrica = "🔴 Baja viabilidad"
st.metric(label=f"Score Opcionable ({color_metrica})", value=f"{score} / 100")
st.warning(mensaje) if score < 50 else st.success(mensaje)
st.caption("Nota: Evalúa el atractivo de las primas en base a la volatilidad reciente de los últimos 20 días y la existencia de contratos líquidos en el mercado.")
else:
st.error(mensaje)
elif st.session_state.asset_type == "Fondos Monetarios":
st.markdown("### 🏦 Biblioteca de Fondos Monetarios (Bajo Riesgo / Corto Plazo)")
monetary_options = ["-- Selecciona un fondo monetario --"]
for data in FUND_DB.values():
if data["category"] == "Fondos Monetarios":
monetary_options.append(f"{data['name']} (ISIN: {data['ticker']}) - [TER: {data['ter']}%]")
selected_index_m = 0
if default_input:
for idx, opt in enumerate(monetary_options):
if default_input.upper() in opt.upper():
selected_index_m = idx
break
selected_monetary_choice = st.selectbox("Biblioteca de Fondos Monetarios", options=monetary_options, index=selected_index_m)
custom_monetary_input = st.text_input("¿No encuentras lo que buscas? Escríbelo aquí:", value=default_input if (default_input and selected_monetary_choice.startswith("--")) else "").strip()
if custom_monetary_input:
user_input = custom_monetary_input.upper()
elif not selected_monetary_choice.startswith("--"):
user_input = selected_monetary_choice.split("ISIN: ")[1].split(")")[0].strip()
else:
user_input = ""
