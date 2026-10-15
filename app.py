import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json
from supabase import create_client, Client

# --- CONFIGURACIÓN DE SUPABASE (NUBE) ---
SUPABASE_URL = "AQUÍ_PEGAS_TU_URL_DE_SUPABASE"
SUPABASE_KEY = "AQUÍ_PEGAS_TU_CLAVE_ANON_DE_SUPABASE"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    supabase = None

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

# Control de Estados
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
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

def sincronizar_con_nube():
    if supabase and st.session_state.user_email:
        try:
            data = {
                "email": st.session_state.user_email.strip().lower(),
                "favorites": st.session_state.favorites,
                "portfolio": st.session_state.portfolio
            }
            supabase.table("user_portfolios").upsert(data, on_conflict="email").execute()
        except Exception as e:
            st.error(f"Error al sincronizar con la nube: {e}")

def cargar_desde_nube(email):
    if supabase and email:
        try:
            res = supabase.table("user_portfolios").select("*").eq("email", email.strip().lower()).execute()
            if res.data:
                st.session_state.favorites = res.data[0].get("favorites", [])
                st.session_state.portfolio = res.data[0].get("portfolio", [])
                return True
        except Exception:
            pass
        return False

def reset_navigation():
    st.session_state.stage = 'home'
    st.session_state.asset_type = None
    st.session_state.sub_type = None
    st.session_state.selected_eval_input = ""

# --- BBDD DE ACCIONES, FONDOS Y ETFS AMPLIADA CON DIVIDENDOS ---
TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables).", "div_yield": 2.8, "per": 24.0, "beta": 0.95},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado).", "div_yield": 4.8, "per": 16.5, "beta": 0.65},
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular.", "div_yield": 5.5, "per": 8.0, "beta": 1.25},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica.", "div_yield": 4.0, "per": 7.5, "beta": 1.30},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sólida.", "div_yield": 6.2, "per": 8.5, "beta": 1.10}
}

FUND_DB = {
    "vanguard global stock acc": {
        "name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "IE00B03HD191",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 23000, "tracking_error": 0.08, "age_years": 15, "currency": "EUR", "is_dist": False, "return_1y": 16.2, "score": 4.6,
        "desc": "Fondo indexado global que replica el índice MSCI World.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Europa (Ex-UK)": 14.5, "Otros": 7.8},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Resto del Fondo": 85.7}
    },
    "vanguard global stock dist": {
        "name": "Vanguard Global Stock Index Fund EUR Dist", "ticker": "IE00B03HD209",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 8400, "tracking_error": 0.08, "age_years": 14, "currency": "EUR", "is_dist": True, "return_1y": 16.0, "score": 4.5,
        "desc": "Versión de distribución del fondo global MSCI World, ideal para cobro periódico de dividendos.",
        "geo": {"EE. UU.": 71.5, "Japón": 6.2, "Europa (Ex-UK)": 14.5, "Otros": 7.8},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Resto del Fondo": 85.7}
    },
    "axa court terme ac": {
        "name": "AXA Court Terme AC (Fondo Monetario Euro)", "ticker": "FR0000447823",
        "category": "Fondos Monetarios", "ter": 0.15, "aum": 6500, "tracking_error": 0.01, "age_years": 25, "currency": "EUR", "is_dist": False, "return_1y": 3.5, "score": 4.8,
        "desc": "Fondo monetario de corto plazo en euros.",
        "geo": {"Zona Euro": 100.0},
        "holdings": {"Letras del Tesoro Francés y Alemán": 60.0, "Pagarés Bancarios AAA": 40.0}
    }
}

ETF_DB = {
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000,
        "replication": "Física", "te": 0.01, "currency": "EUR", "age_years": 3, "is_dist": False, "return_1y": 22.3, "score": 4.9,
        "desc": "El ETF del S&P 500 más económico de Europa.",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Resto del ETF": 80.1}
    },
    "vhyd.de": {
        "name": "Vanguard FTSE All-World High Dividend Yield UCITS ETF [Distribución]", "ticker": "VHYD.DE",
        "category": "Alto Dividendo", "ter": 0.29, "aum": 4200,
        "replication": "Física", "te": 0.05, "currency": "EUR", "age_years": 10, "is_dist": True, "return_1y": 14.2, "score": 4.5,
        "desc": "Acciones de alta rentabilidad por dividendo a nivel global con reparto periódico.",
        "geo": {"EE. UU.": 42.0, "Europa": 28.0, "Reino Unido": 12.0, "Japón": 8.0, "Otros": 10.0},
        "holdings": {"JPMorgan Chase": 3.2, "Exxon Mobil": 3.0, "Johnson & Johnson": 2.7, "Resto del ETF": 91.1}
    },
    "ie00byyhsm20": {
        "name": "iShares MSCI Europe Quality Dividend UCITS ETF", "ticker": "IE00BYYHSM20",
        "category": "Alto Dividendo", "ter": 0.28, "aum": 1500,
        "replication": "Física", "te": 0.04, "currency": "EUR", "age_years": 6, "is_dist": True, "return_1y": 13.5, "score": 4.6,
        "desc": "Selecciona compañías europeas con dividendos sostenibles, alta calidad crediticio e incluye gran peso de grandes empresas de España y la Eurozona.",
        "geo": {"Francia": 22.0, "Reino Unido": 18.5, "España": 14.0, "Alemania": 12.0, "Suiza": 11.5, "Otros": 22.0},
        "holdings": {"Nestlé SA": 4.5, "Novartis": 4.1, "Iberdrola SA": 3.8, "TotalEnergies": 3.5, "Banco Bilbao Vizcaya Argentaria (BBVA)": 3.2, "Resto del ETF": 80.9}
    },
    "ie00b5m1wj87": {
        "name": "SPDR S&P Euro Dividend Aristocrats UCITS ETF", "ticker": "IE00B5M1WJ87",
        "category": "Alto Dividendo", "ter": 0.30, "aum": 2100,
        "replication": "Física", "te": 0.05, "currency": "EUR", "age_years": 11, "is_dist": True, "return_1y": 12.8, "score": 4.7,
        "desc": "Invierte en empresas de la Eurozona que llevan más de 10 años consecutivos aumentando o manteniendo su dividendo.",
        "geo": {"Francia": 28.0, "Alemania": 22.0, "España": 15.0, "Italia": 14.0, "Otros": 21.0},
        "holdings": {"Enagás": 3.9, "Iberdrola": 3.7, "TotalEnergies": 3.5, "Sanofi": 3.4, "Resto del ETF": 85.5}
    },
    "fr0010251744": {
        "name": "Amundi IBEX 35 UCITS ETF Dist", "ticker": "FR0010251744",
        "category": "Renta Variable España", "ter": 0.30, "aum": 350,
        "replication": "Física", "te": 0.03, "currency": "EUR", "age_years": 18, "is_dist": True, "return_1y": 18.5, "score": 4.3,
        "desc": "ETF de distribución que replica el índice bursátil español IBEX 35, caracterizado por una alta rentabilidad media por dividendo.",
        "geo": {"España": 100.0},
        "holdings": {"Banco Santander": 15.2, "BBVA": 14.8, "Iberdrola": 14.5, "Inditex": 12.1, "Telefónica": 5.4, "CaixaBank": 5.0, "Resto del ETF": 33.0}
    }
}

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("👤 Sincronización en la Nube")
    email_input = st.text_input("Introduce tu email:", value=st.session_state.user_email, placeholder="tu_correo@gmail.com")
    
    if email_input:
        if email_input != st.session_state.user_email:
            st.session_state.user_email = email_input
            if cargar_desde_nube(email_input):
                st.success("¡Datos cargados de la nube!")
            else:
                st.info("Nuevo perfil en la nube iniciado.")
        st.caption("✅ Sincronizado automáticamente entre móvil y PC.")
    else:
        st.warning("Escribe tu email arriba para sincronizar favoritos y cartera en todos tus dispositivos.")

    st.markdown("---")
    st.header("📊 Historial de Sesión")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_history.to_excel(writer, sheet_name='Evaluaciones', index=False)
        st.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="historial.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
        if st.button("🗑️ Borrar Historial"):
            st.session_state.history = []
            st.rerun()

    if st.session_state.stage != 'home':
        st.markdown("---")
        if st.button("🏠 Volver al Menú Principal"):
            reset_navigation()
            st.rerun()

# --- INTERFAZ PRINCIPAL ---
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
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📊 Acciones", use_container_width=True, type="primary"):
            st.session_state.asset_type = "Acciones"
            st.session_state.stage = "sub_options"
            st.rerun()
    with c2:
        if st.button("📁 Fondos Indexados", use_container_width=True, type="primary"):
            st.session_state.asset_type = "Fondos indexados"
            st.session_state.stage = "sub_options"
            st.rerun()
    with c3:
        if st.button("🌐 ETFs", use_container_width=True, type="primary"):
            st.session_state.asset_type = "ETFs"
            st.session_state.stage = "sub_options"
            st.rerun()
    with c4:
        if st.button("🏦 Fondos Monetarios", use_container_width=True, type="primary"):
            st.session_state.asset_type = "Fondos Monetarios"
            st.session_state.stage = "analyzer"
            st.session_state.sub_type = "Biblioteca Monetarios"
            st.rerun()

elif st.session_state.stage == 'favorites_view':
    if st.button("← Volver"):
        st.session_state.stage = 'home'
        st.rerun()
    st.title("⭐ Mis Activos Favoritos")
    if not st.session_state.favorites:
        st.info("No tienes favoritos guardados.")
    else:
        for idx, fav in enumerate(st.session_state.favorites):
            with st.expander(f"{fav['name']} ({fav['ticker']})"):
                if st.button("🗑️ Quitar", key=f"del_fav_{idx}"):
                    st.session_state.favorites.pop(idx)
                    sincronizar_con_nube()
                    st.rerun()

elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver"):
        st.session_state.stage = 'home'
        st.rerun()
    st.title("💼 Mi Cartera Consolidada")
    if not st.session_state.portfolio:
        st.info("Tu cartera está vacía.")
    else:
        for idx, item in enumerate(st.session_state.portfolio):
            with st.expander(f"{item['name']} ({item['ticker']})"):
                if st.button("🗑️ Quitar", key=f"del_port_{idx}"):
                    st.session_state.portfolio.pop(idx)
                    sincronizar_con_nube()
                    st.rerun()
