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
    .converter-box {
        background: #1e293b;
        border: 1px solid #38bdf8;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
    }
    .note-analysis-box {
        background: #0f172a;
        border-left: 4px solid #38bdf8;
        padding: 18px;
        border-radius: 8px;
        margin-top: 20px;
        margin-bottom: 20px;
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
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios).", "div_growth": 6.5, "div_yield": 2.8, "per": 24.0, "beta": 0.95, "payout": 60.0, "comment": "💡 **Análisis de Valoración:** Excelente salud financiera con caja neta positiva. Payout sostenible que permite combinar dividendo con crecimiento de canal online."},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos).", "div_growth": 5.0, "div_yield": 4.8, "per": 16.5, "beta": 0.65, "payout": 70.0, "comment": "💡 **Análisis de Valoración:** Activo defensivo ideal para carteras de dividendos. Su fuerte exposición a redes eléctricas y renovables garantiza visibilidad de ingresos."},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico sin dependencia de dividendo tradicional.", "div_growth": 10.0, "div_yield": 0.7, "per": 32.0, "beta": 0.90, "payout": 25.0, "comment": "💡 **Análisis de Valoración:** Liderazgo en IA y Cloud (Azure). Su bajo rendimiento por dividendo se compensa con un crecimiento compuesto de capital excepcional."}
}

FUND_DB = {
    "vanguard global stock acc": {
        "name": "Vanguard Global Stock Index Fund EUR Acc",
        "ticker": "IE00B03HD191",
        "category": "Renta Variable Global (MSCI World)",
        "ter": 0.18,
        "aum": 23000,
        "tracking_error": 0.08,
        "age_years": 15,
        "currency": "EUR",
        "is_dist": False,
        "return_1y": 16.2,
        "equiv_dist_isin": "IE0007987690 (Vanguard Global Stock Dist)",
        "equiv_etf_ticker": "SWDA.L (iShares MSCI World ETF)",
        "comment": "💡 **Evaluación del Fondo:** Referente mundial de gestión pasiva. Excelente eficiencia fiscal al acumular dividendos sin peaje en el IRPF español."
    },
    "vanguard sp 500 acc": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc",
        "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU. (S&P 500)",
        "ter": 0.10,
        "aum": 17000,
        "tracking_error": 0.03,
        "age_years": 22,
        "currency": "EUR",
        "is_dist": False,
        "return_1y": 22.4,
        "equiv_dist_isin": "IE0032126868 (Vanguard U.S. 500 Dist)",
        "equiv_etf_ticker": "SPYL.DE (SPDR S&P 500 ETF Acc) / VUSA.DE (Dist)",
        "comment": "💡 **Evaluación del Fondo:** Máxima liquidez y seguimiento ultratransparente del S&P 500 con comisiones mínimas."
    }
}

ETF_DB = {
    "vwce.de": {
        "name": "Vanguard FTSE All-World UCITS ETF (Acc)",
        "ticker": "VWCE.DE",
        "category": "Renta Variable Global (All-World)",
        "ter": 0.22,
        "aum": 15000,
        "replication": "Física (Completa)",
        "te": 0.04,
        "currency": "EUR",
        "age_years": 7,
        "is_dist": False,
        "return_1y": 16.0,
        "equiv_dist_ticker": "VWRD.L (Vanguard FTSE All-World Dist)",
        "equiv_fund_isin": "IE00B03HD191 (Vanguard Global Stock Fund Acc)",
        "comment": "💡 **Evaluación del ETF:** Diversificación total en más de 3.600 empresas globales. Ideal como núcleo de cartera intocable de largo plazo."
    },
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF (Acc)",
        "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)",
        "ter": 0.03,
        "aum": 12000,
        "replication": "Física (Completa)",
        "te": 0.01,
        "currency": "EUR",
        "age_years": 3,
        "is_dist": False,
        "return_1y": 22.3,
        "equiv_dist_ticker": "SPYD.DE (SPDR S&P 500 Dist)",
        "equiv_fund_isin": "IE00BYX5MX67 (Fidelity S&P 500 Fund Acc)",
        "comment": "💡 **Evaluación del ETF:** Opción imbatible en comisiones (TER 0.03%). Minimiza la fricción de costes al máximo sobre el S&P 500."
    }
}

FUND_BROKER_PROFILES = {
    "MyInvestor (0% custodia)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Renta 4": {"fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False}
}

ETF_BROKER_PROFILES = {
    "Trade Republic (Planes 0€)": {"fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "Interactive Brokers": {"fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False}
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
    st.header("📊 Menú Navegación")
    if st.button("🏠 Inicio", use_container_width=True):
        reset_navigation()
        st.rerun()
    if st.button("🔄 Convertidor de Equivalencias", use_container_width=True):
        st.session_state.stage = "converter_view"
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
    if st.button("🔄 Convertidor de Equivalencias (Acumulación/Distribución y Fondo/ETF)", use_container_width=True):
        st.session_state.stage = "converter_view"
        st.rerun()

# ----------------------------------------------------
# NUEVA SECCIÓN: CONVERTIDOR DE EQUIVALENCIAS
# ----------------------------------------------------
elif st.session_state.stage == 'converter_view':
    if st.button("← Volver al Menú Principal"):
        reset_navigation()
        st.rerun()

    st.title("🔄 Convertidor de Activos Equivalentes")
    st.markdown("Introduce un Fondo o ETF y encuentra de forma automática su versión **equivalente de Acumulación/Distribución** o su réplica **entre Fondo Indexado y ETF**.")

    conv_type = st.radio("Tipo de Convertidor:", ["📁 Convertidor de Fondos Indexados", "🌐 Convertidor de ETFs"])

    if conv_type == "📁 Convertidor de Fondos Indexados":
        fund_choice = st.selectbox("Selecciona un Fondo del catálogo para convertir:", list(FUND_DB.keys()))
        f_data = FUND_DB[fund_choice]
        
        st.markdown(f"""
        <div class="converter-box">
            <h3>📁 Fondo Seleccionado: {f_data['name']}</h3>
            <p><strong>ISIN Actual:</strong> {f_data['ticker']} | <strong>Modalidad:</strong> {'Distribución (Cobro de dividendos)' if f_data['is_dist'] else 'Acumulación (Reinversión automática)'}</p>
            <hr>
            <h4>🔄 Equivalencias Directas Encontradas:</h4>
            <ul>
                <li><strong>Modalidad Opuesta ({'Acumulación' if f_data['is_dist'] else 'Distribución'}):</strong> {f_data.get('equiv_dist_isin', 'Consulte versión en comercializadora')}</li>
                <li><strong>Réplica Equivalente en ETF:</strong> {f_data.get('equiv_etf_ticker', 'Disponible en mercado cotizado')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    else:
        etf_choice = st.selectbox("Selecciona un ETF del catálogo para convertir:", list(ETF_DB.keys()))
        e_data = ETF_DB[etf_choice]
        
        st.markdown(f"""
        <div class="converter-box">
            <h3>🌐 ETF Seleccionado: {e_data['name']}</h3>
            <p><strong>Ticker Actual:</strong> {e_data['ticker']} | <strong>Modalidad:</strong> {'Distribución (Pago periódico)' if e_data['is_dist'] else 'Acumulación (Crecimiento)'}</p>
            <hr>
            <h4>🔄 Equivalencias Directas Encontradas:</h4>
            <ul>
                <li><strong>Modalidad Opuesta ({'Acumulación' if e_data['is_dist'] else 'Distribución'}):</strong> {e_data.get('equiv_dist_ticker', 'Consulte versión distribuida')}</li>
                <li><strong>Réplica Equivalente en Fondo Indexado:</strong> {e_data.get('equiv_fund_isin', 'Traspasable en España')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------
# SUBOPCIONES / EVALUACIÓN CON NOTAS RESTAURADAS
# ----------------------------------------------------
elif st.session_state.stage == 'sub_options':
    if st.button("← Volver al Menú"):
        reset_navigation()
        st.rerun()

    st.title(f"Configuración para: {st.session_state.asset_type}")
    st.session_state.stage = "analyzer"
    st.rerun()

elif st.session_state.stage == 'analyzer':
    if st.button("← Volver"):
        reset_navigation()
        st.rerun()

    if st.session_state.asset_type == "Acciones":
        stock_key = st.selectbox("Selecciona la Acción a evaluar:", list(TICKER_DB.keys()))
        s_data = TICKER_DB[stock_key]

        st.subheader(f"📊 Informe Completo: {stock_key.title()} ({s_data['ticker']})")
        
        df_metrics = pd.DataFrame({
            "Métrica": ["PER", "Dividendo Yield", "Beta", "Payout Ratio"],
            "Valor": [f"{s_data['per']}", f"{s_data['div_yield']}%", f"{s_data['beta']}", f"{s_data['payout']}%"]
        })
        st.table(df_metrics)

        # RESTAURACIÓN DE COMENTARIOS TRAS EVALUACIÓN
        st.markdown(f"""
        <div class="note-analysis-box">
            <h4>📝 Notas y Observaciones tras Evaluación</h4>
            <p><strong>Comportamiento Histórico:</strong> {s_data['racha']}</p>
            <p>{s_data['comment']}</p>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.asset_type == "Fondos indexados":
        fund_key = st.selectbox("Selecciona Fondo Indexado:", list(FUND_DB.keys()))
        f_data = FUND_DB[fund_key]

        st.subheader(f"📊 Informe de Fondo: {f_data['name']}")
        
        df_f_metrics = pd.DataFrame({
            "Métrica del Fondo": ["ISIN / Ticker", "TER (Gastos Anuales)", "Rentabilidad (1A)", "Patrimonio (AUM)"],
            "Valor Actual": [f_data["ticker"], f"{f_data['ter']}%", f"+{f_data['return_1y']}%", f"{f_data['aum']} M€"]
        })
        st.table(df_f_metrics)

        # RESTAURACIÓN DE COMENTARIOS TRAS EVALUACIÓN
        st.markdown(f"""
        <div class="note-analysis-box">
            <h4>📝 Notas y Observaciones tras Evaluación</h4>
            <p>{f_data['comment']}</p>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.asset_type == "ETFs":
        etf_key = st.selectbox("Selecciona ETF:", list(ETF_DB.keys()))
        e_data = ETF_DB[etf_key]

        st.subheader(f"🌐 Informe de ETF: {e_data['name']}")
        
        df_e_metrics = pd.DataFrame({
            "Métrica del ETF": ["Ticker", "TER (Gastos Anuales)", "Rentabilidad (1A)", "Réplica"],
            "Valor Actual": [e_data["ticker"], f"{e_data['ter']}%", f"+{e_data['return_1y']}%", e_data["replication"]]
        })
        st.table(df_e_metrics)

        # RESTAURACIÓN DE COMENTARIOS TRAS EVALUACIÓN
        st.markdown(f"""
        <div class="note-analysis-box">
            <h4>📝 Notas y Observaciones tras Evaluación</h4>
            <p>{e_data['comment']}</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------
# SECCIONES FAVORITOS Y CARTERA
# ----------------------------------------------------
elif st.session_state.stage == 'favorites_view':
    if st.button("← Volver"):
        reset_navigation()
        st.rerun()
    st.title("⭐ Mis Activos Favoritos")

elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver al Menú"):
        reset_navigation()
        st.rerun()
    st.title("💼 Cartera Consolidada")
