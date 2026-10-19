import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json

st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

# CSS para ocultar completamente la barra lateral y su botón de apertura
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
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

# Estados para Cuenta Remunerada
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
    "fidelity msci world acc": {
        "name": "Fidelity MSCI World Index Fund EUR P Acc", "ticker": "IE00BYX5NX33",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.10, "aum": 8500, "tracking_error": 0.06, "age_years": 8, "currency": "EUR", "is_dist": False, "return_1y": 15.9, "score": 4.7,
        "desc": "Uno de los fondos globales más económicos del mercado europeo para replicar el índice MSCI World.",
        "geo": {"EE. UU.": 71.8, "Japón": 6.1, "Reino Unido": 3.8, "Europa (Ex-UK)": 14.4, "Otros": 3.9},
        "holdings": {"Apple Inc.": 5.2, "Microsoft Corp.": 4.8, "NVIDIA Corp.": 4.3, "Amazon.com Inc.": 2.6, "Resto del Fondo": 79.2}
    }
}

ETF_DB = {
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000,
        "replication": "Física (Completa)", "te": 0.01, "currency": "EUR", "age_years": 3, "is_dist": False, "return_1y": 22.3, "score": 4.9,
        "desc": "El ETF del S&P 500 con el coste operativo más bajo de Europa (TER del 0.03%).",
        "geo": {"EE. UU.": 100.0},
        "holdings": {"Apple Inc.": 7.1, "Microsoft Corp.": 6.8, "NVIDIA Corp.": 6.0, "Resto del ETF": 73.2}
    }
}

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
# PESTAÑA 1: SIMULADOR DE INTERÉS COMPUESTO
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
            ticker_actual = "FR0000447823"

    st.markdown("---")
    
    col_ci1, col_ci2 = st.columns(2)
    with col_ci1:
        inv_inicial = st.number_input("Inversión Inicial (€)", min_value=0.0, value=1000.0, step=500.0, key="ic_ini")
        aportacion_per = st.number_input("Aportación Periódica (€)", min_value=0.0, value=150.0, step=50.0, key="ic_app")
    with col_ci2:
        plazo_anos = st.slider("Plazo Temporal (Años)", min_value=1, max_value=40, value=15, key="ic_anos")
        rentabilidad_est = st.slider("Rentabilidad Anual Estimada (%)", min_value=0.0, max_value=20.0, value=7.5, step=0.5, key="ic_rent")

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
        st.info("🛒 Tu cartera está vacía. Añade activos desde el simulador o créalos aquí abajo.")
        
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
# PESTAÑA 3: SIMULADOR DE CUENTA REMUNERADA
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

    val_remunerada_neto = st.session_state.remunerada_capital + ((st.session_state.remunerada_capital * (st.session_state.remunerada_interes / 100.0)) * 0.81)

    val_cartera_global = sum([item.get('capital_final', 5000.0) for item in st.session_state.portfolio])
    if not st.session_state.portfolio:
        val_cartera_global = 12500.0

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
