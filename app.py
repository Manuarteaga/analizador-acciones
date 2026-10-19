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
    }
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

# Control de Estados y Persistencia
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

# Nuevo estado para Cuenta Remunerada
if 'remunerada_capital' not in st.session_state:
    st.session_state.remunerada_capital = 10000.0
if 'remunerada_interes' not in st.session_state:
    st.session_state.remunerada_interes = 2.5

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
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5, "per": 8.0, "beta": 1.25, "payout": 50.0},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0, "per": 7.5, "beta": 1.30, "payout": 40.0},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sensible al ciclo económico y a los planes de consolidación bancaria.", "div_growth": 4.5, "div_yield": 6.2, "per": 8.5, "beta": 1.10, "payout": 60.0},
    "copart": {"ticker": "CPRT", "racha": "Empresa pura de crecimiento orientada a reinvestigación.", "div_growth": 0.0, "div_yield": 0.0, "per": 28.0, "beta": 1.05, "payout": 0.0},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos).", "div_growth": 5.0, "div_yield": 4.8, "per": 16.5, "beta": 0.65, "payout": 70.0},
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios).", "div_growth": 6.5, "div_yield": 2.8, "per": 24.0, "beta": 0.95, "payout": 60.0},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico sin dependencia de dividendo tradicional.", "div_growth": 10.0, "div_yield": 0.7, "per": 32.0, "beta": 0.90, "payout": 25.0},
    "nike": {"ticker": "NKE", "racha": "Sólida trayectoria de crecimiento e incremento de dividendo sostenido durante más de 20 años.", "div_growth": 9.5, "div_yield": 1.8, "per": 28.5, "beta": 1.10, "payout": 45.0},
    "procter & gamble": {"ticker": "PG", "racha": "Excepcional. Aristócrata del Dividendo con más de 65 años de subidas ininterrumpidas.", "div_growth": 6.0, "div_yield": 2.4, "per": 25.0, "beta": 0.55, "payout": 60.0},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5, "per": 12.0, "beta": 0.85, "payout": 85.0}
}

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
        "category": "Renta Variable Desarrollada Ex-EEUU", "ter": 0.24, "aum": 820, "tracking_error": 0.06, "age_years": 3, "currency": "USD", "is_dist": False, "return_1y": 14.5, "score": 4.6,
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
    "vanguard european stock acc": {
        "name": "Vanguard European Stock Index Fund EUR Acc", "ticker": "IE0007987690",
        "category": "Renta Variable Europa", "ter": 0.12, "aum": 7800, "tracking_error": 0.06, "age_years": 18, "currency": "EUR", "is_dist": False, "return_1y": 12.1, "score": 4.4,
        "desc": "Fondo indexado enfocado en el mercado europeo (Reino Unido, Francia, Suiza, Alemania, etc.).",
        "geo": {"Reino Unido": 23.0, "Francia": 17.5, "Suiza": 14.5, "Alemania": 13.5, "Otros": 31.5},
        "holdings": {"ASML Holding NV": 3.5, "Nestlé SA": 3.2, "LVMH Moët Hennessy": 2.8, "Novartis AG": 2.6, "Shell PLC": 2.5, "SAP SE": 2.2, "TotalEnergies": 1.9, "Resto del Fondo": 81.3}
    },
    "vanguard global stock acc": {
        "name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "IE00B03HD191",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 23000, "tracking_error": 0.08, "age_years": 15, "currency": "EUR", "is_dist": False, "return_1y": 16.2, "score": 4.6,
        "desc": "Fondo indexado de referencia global que replica el índice MSCI World, invirtiendo en más de 1.500 empresas de gran y mediana capitalización en países desarrollados.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.5, "Otros": 4.0},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Alphabet Inc. (Google)": 2.3, "Meta Platforms Inc.": 1.6, "Eli Lilly & Co.": 1.0, "Resto del Fondo": 78.2}
    },
    "vanguard sp 500 acc": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc", "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 17000, "tracking_error": 0.03, "age_years": 22, "currency": "EUR", "is_dist": False, "return_1y": 22.4, "score": 4.8,
        "desc": "Fondo indexado histórico que replica el comportamiento de las 500 empresas más grandes de Estados Unidos.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Amazon.com Inc.": 3.7, "Alphabet Inc.": 3.2, "Meta Platforms": 2.4, "Berkshire Hathaway": 1.7, "Eli Lilly": 1.5, "Resto del Fondo": 67.6}
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
    "vwce.de": {
        "name": "Vanguard FTSE All-World UCITS ETF [Acumulación]", "ticker": "VWCE.DE",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.22, "aum": 15000,
        "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 7, "is_dist": False, "return_1y": 16.0, "score": 4.8,
        "desc": "Incluye tanto países desarrollados como mercados emergentes (más de 3.700 valores en todo el mundo).",
        "geo": {"EE. UU.": 62.5, "Mercados Emergentes": 10.5, "Japón": 5.8, "Europa": 15.2, "Otros": 6.0},
        "holdings": {"Apple Inc.": 4.5, "Microsoft Corp.": 4.2, "NVIDIA Corp.": 3.8, "Amazon.com Inc.": 2.3, "Alphabet Inc.": 2.0, "Meta Platforms": 1.4, "Resto del ETF": 81.8}
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

def render_geo_breakdown(geo_dict):
    st.markdown("**🗺️ Desglose Geográfico Estimado:**")
    colors = {
        "EE. UU.": "#3b82f6", "China": "#ef4444", "India": "#f59e0b", "Taiwán": "#10b981", 
        "Corea del Sur": "#8b5cf6", "Japón": "#ec4899", "Reino Unido": "#6366f1", "Europa": "#14b8a6", 
        "Europa (Ex-UK)": "#06b6d4", "Canadá": "#84cc16", "Mercados Emergentes": "#f97316", 
        "Brasil": "#eab308", "Oro Físico": "#fbbf24", "Zona Euro": "#3b82f6", "Otros": "#64748b"
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
    holding_colors = ["#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#fb7185", "#34d399", "#fbbf24"]
    bar_html = '<div class="geo-bar-container">'
    legend_html = '<div class="geo-legend">'
    for idx, (company, pct) in enumerate(holdings_dict.items()):
        color = "#475569" if "resto" in company.lower() else holding_colors[idx % len(holding_colors)]
        bar_html += f'<div style="width: {pct}%; background-color: {color}; height: 100%;" title="{company}: {pct}%"></div>'
        legend_html += f'<div class="geo-legend-item"><div class="geo-dot" style="background-color: {color};"></div><span>{company} ({pct}%)</span></div>'
    bar_html += '</div>'
    legend_html += '</div>'
    st.markdown(bar_html + legend_html, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# SISTEMA DE PESTAÑAS PRINCIPALES (ACCESO DIRECTO SIN MENÚS)
# -------------------------------------------------------------------------
tab_analizador, tab_cartera, tab_remunerada, tab_resumen = st.tabs([
    "📈 Simulador Interés Compuesto", 
    "💼 Simulador Cartera", 
    "🏦 Simulador Cuenta Remunerada", 
    "⭐ Resumen Global"
])

# -------------------------------------------------------------------------
# PESTAÑA 1: SIMULADOR DE INTERÉS COMPUESTO (ANALIZADOR)
# -------------------------------------------------------------------------
with tab_analizador:
    st.title("📈 Simulador de Interés Compuesto & Analizador")
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        tipo_activo_sel = st.selectbox("Tipo de Activo", ["Acciones", "Fondos Indexados", "ETFs", "Fondos Monetarios"])
    with col_sel2:
        if tipo_activo_sel == "Acciones":
            accion_busqueda = st.selectbox("Selecciona Acción", list(TICKER_DB.keys()))
            ticker_actual = TICKER_DB[accion_busqueda]["ticker"]
        elif tipo_activo_sel == "Fondos Indexados":
            fondo_busqueda = st.selectbox("Selecciona Fondo", list(FUND_DB.keys()))
            ticker_actual = FUND_DB[fondo_busqueda]["ticker"]
        elif tipo_activo_sel == "ETFs":
            etf_busqueda = st.selectbox("Selecciona ETF", list(ETF_DB.keys()))
            ticker_actual = ETF_DB[etf_busqueda]["ticker"]
        else:
            ticker_actual = "FR0000447823" # AXA Court Terme

    st.markdown("---")
    
    # Renderizado simplificado de la calculadora de interés compuesto
    col_ci1, col_ci2 = st.columns(2)
    with col_ci1:
        inv_inicial = st.number_input("Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key="ic_ini")
        aportacion_per = st.number_input("Aportación Periódica (€)", min_value=0.0, value=150.0, step=50.0, key="ic_app")
    with col_ci2:
        plazo_anos = st.slider("Plazo Temporal (Años)", min_value=1, max_value=40, value=15, key="ic_anos")
        rentabilidad_est = st.slider("Rentabilidad Anual Estimada (%)", min_value=0.0, max_value=20.0, value=7.5, step=0.5, key="ic_rent")

    # Cálculo simple de interés compuesto
    tasa_mensual = (rentabilidad_est / 100.0) / 12
    meses = plazo_anos * 12
    saldo = inv_inicial
    total_aportado = inv_inicial

    for m in range(1, meses + 1):
        if m > 1:
            saldo += aportacion_per
            total_aportado += aportacion_per
        saldo *= (1 + tasa_mensual)

    beneficio_bruto = max(0.0, saldo - total_aportado)
    impuestos = beneficio_bruto * 0.19
    capital_neto_final = total_aportado + (beneficio_bruto - impuestos)

    st.markdown(f"""
    <div class="final-net-card">
        <div class="final-net-title">💰 Capital Total Líquido Final (Interés Compuesto)</div>
        <div class="final-net-value">{capital_neto_final:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕ Añadir este cálculo a mi Cartera Global"):
        st.session_state.portfolio.append({
            "type": tipo_activo_sel, "name": f"Simulación {tipo_activo_sel}", "ticker": ticker_actual,
            "est_rent": rentabilidad_est, "ter": 0.20, "currency": "EUR", "is_dist": False,
            "category": tipo_activo_sel, "capital_final": capital_neto_final
        })
        guardar_en_url()
        st.success("¡Añadido con éxito a la Cartera!")

# -------------------------------------------------------------------------
# PESTAÑA 2: SIMULADOR DE CARTERA
# -------------------------------------------------------------------------
with tab_cartera:
    st.title("💼 Simulador de Cartera Multiactivo")
    
    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía. Añade activos desde el simulador de interés compuesto o configúralos aquí.")
        
        col_nc1, col_nc2, col_nc3 = st.columns(3)
        with col_nc1:
            nombre_nuevo = st.text_input("Nombre del activo", value="Mi ETF Global")
        with col_nc2:
            capital_nuevo = st.number_input("Capital invertido (€)", value=5000.0)
        with col_nc3:
            rent_nueva = st.number_input("Rentabilidad estimada (%)", value=7.0)
            
        if st.button("➕ Crear e incluir activo en Cartera"):
            st.session_state.portfolio.append({
                "type": "ETF", "name": nombre_nuevo, "ticker": "CUSTOM",
                "est_rent": rent_nueva, "ter": 0.15, "currency": "EUR", "is_dist": False,
                "category": "Renta Variable", "capital_final": capital_nuevo * (1 + rent_nueva/100)**5
            })
            guardar_en_url()
            st.success("¡Activo añadido a la cartera!")
            st.rerun()
    else:
        total_valor_cartera = 0.0
        for idx, item in enumerate(st.session_state.portfolio):
            val_act = item.get('capital_final', 5000.0)
            total_valor_cartera += val_act
            with st.expander(f"{idx+1}. {item['name']} - [{item['type']}]"):
                st.markdown(f"**Rentabilidad estimada:** {item.get('est_rent', 7.0)}%")
                st.markdown(f"**Valor estimado:** {val_act:,.2f} €")
                if st.button("🗑️ Eliminar de Cartera", key=f"del_port_{idx}"):
                    st.session_state.portfolio.pop(idx)
                    guardar_en_url()
                    st.rerun()

        st.markdown(f"""
        <div class="final-net-card">
            <div class="final-net-title">💼 Valor Total Acumulado de la Cartera</div>
            <div class="final-net-value">{total_valor_cartera:,.2f} €</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Vaciar Cartera Completa"):
            st.session_state.portfolio = []
            guardar_en_url()
            st.rerun()

# -------------------------------------------------------------------------
# PESTAÑA 3: SIMULADOR DE CUENTA REMUNERADA (NUEVO AÑADIDO)
# -------------------------------------------------------------------------
with tab_remunerada:
    st.title("🏦 Simulador de Cuenta Remunerada")
    st.markdown("Calcula de forma independiente los rendimientos de tu liquidez en cuentas remuneradas (restando la retención fiscal del 19% en España).")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.session_state.remunerada_capital = st.number_input("Capital depositado en la cuenta (€)", min_value=0.0, value=st.session_state.remunerada_capital, step=1000.0)
        st.session_state.remunerada_interes = st.slider("Tipo de interés anual (TAE %)", min_value=0.0, max_value=6.0, value=st.session_state.remunerada_interes, step=0.1)
    with col_r2:
        plazo_meses = st.slider("Plazo de depósito (Meses)", min_value=1, max_value=60, value=12)

    # Cálculos cuenta remunerada
    interes_bruto_anual = st.session_state.remunerada_capital * (st.session_state.remunerada_interes / 100.0)
    interes_bruto_periodo = interes_bruto_anual * (plazo_meses / 12.0)
    impuestos_remunerada = interes_bruto_periodo * 0.19
    interes_neto_periodo = interes_bruto_periodo - impuestos_remunerada
    capital_final_remunerada = st.session_state.remunerada_capital + interes_neto_periodo

    rm1, rm2, rm3 = st.columns(3)
    rm1.metric("Intereses Brutos", f"{interes_bruto_periodo:,.2f} €")
    rm2.metric("Retención IRPF (19%)", f"-{impuestos_remunerada:,.2f} €")
    rm3.metric("Intereses Netos", f"{interes_neto_periodo:,.2f} €")

    st.markdown(f"""
    <div class="final-net-card">
        <div class="final-net-title">💰 Capital Total Disponible en Cuenta Remunerada (Neto)</div>
        <div class="final-net-value">{capital_final_remunerada:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# PESTAÑA 4: RESUMEN GLOBAL (SUMA DE TODO EN UN SOLO LUGAR)
# -------------------------------------------------------------------------
with tab_resumen:
    st.title("⭐ Resumen Global de Ahorros")
    st.markdown("Control consolidado que suma de forma independiente tus simuladores de **Interés Compuesto**, tu **Cartera** y tu **Cuenta Remunerada**.")

    # 1. Valor cuenta remunerada
    val_remunerada_neto = st.session_state.remunerada_capital + ((st.session_state.remunerada_capital * (st.session_state.remunerada_interes / 100.0)) * 0.81)

    # 2. Valor cartera / inversiones
    val_cartera_global = sum([item.get('capital_final', 5000.0) for item in st.session_state.portfolio])
    if not st.session_state.portfolio:
        val_cartera_global = 12500.0 # Valor por defecto ilustrativo si no hay elementos

    # Suma total global
    ahorro_total_global = val_remunerada_neto + val_cartera_global

    rg1, rg2, rg3 = st.columns(3)
    rg1.metric("🏦 Cuenta Remunerada (Neta)", f"{val_remunerada_neto:,.2f} €")
    rg2.metric("💼 Inversiones / Cartera", f"{val_cartera_global:,.2f} €")
    rg3.metric("🎯 Ahorro Total Consolidado", f"{ahorro_total_global:,.2f} €")

    st.markdown(f"""
    <div class="final-net-card">
        <div class="final-net-title">🌐 PATRIMONIO GLOBAL CONSOLIDADO</div>
        <div class="final-net-value">{ahorro_total_global:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 Este panel te permite supervisar de un vistazo la liquidez segura de tus cuentas remuneradas junto con el crecimiento a largo plazo de tus carteras e inversiones.")
