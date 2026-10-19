import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json

st.set_page_config(page_title="Gestor Integral de Patrimonio y Ahorro", page_icon="💰", layout="wide")

# CSS personalizado para diseño moderno
st.markdown("""
<style>
    .global-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2px solid #38bdf8;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    .global-title {
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #38bdf8;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .global-value {
        font-size: 2.8rem;
        font-weight: 900;
        color: #ffffff;
    }
    .sub-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }
    .broker-badge {
        background-color: #1e293b;
        border: 1px solid #38bdf8;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
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
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# CONTROL DE ESTADOS DE SESIÓN
# ----------------------------------------------------
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# ----------------------------------------------------
# BASES DE DATOS DE ACTIVOS Y CUENTAS
# ----------------------------------------------------
SAVINGS_ACCOUNTS_DB = {
    "Revolut (Cuenta Remunerada Promocional)": {
        "tae": 3.51, "tin": 3.45, "limit": 25000,
        "desc": "3,51% TAE promocional (4 meses para nuevos clientes). Cobro diario de intereses."
    },
    "Openbank (Cuenta Remunerada)": {
        "tae": 3.25, "tin": 3.20, "limit": 0,
        "desc": "3,25% TAE durante el primer año trayendo Bizum y ahorros. Sin límite de saldo."
    },
    "Trade Republic (Cuenta de Efectivo)": {
        "tae": 3.04, "tin": 3.00, "limit": 50000,
        "desc": "3,04% TAE sin condiciones para los primeros 50.000 €. Liquidación mensual e IBAN español."
    },
    "Bankinter (Cuenta Digital)": {
        "tae": 3.00, "tin": 2.96, "limit": 100000,
        "desc": "3,00% TAE garantizado hasta un máximo de 100.000 € para nuevos clientes digitales."
    },
    "B100 / Abanca Health (Cuenta Save)": {
        "tae": 2.75, "tin": 2.72, "limit": 50000,
        "desc": "2,75% TAE para la Cuenta Save sin exigencias adicionales."
    },
    "Banco Sabadell (Cuenta Online)": {
        "tae": 2.75, "tin": 2.72, "limit": 100000,
        "desc": "2,75% TAE durante el primer año hasta 100.000 €."
    },
    "MyInvestor (Cuenta Remunerada)": {
        "tae": 2.50, "tin": 2.47, "limit": 70000,
        "desc": "2,50% TAE el primer año hasta 70.000 €."
    },
    "Personalizado / Ajuste Manual": {
        "tae": 2.50, "tin": 2.47, "limit": 0,
        "desc": "Permite introducir manualmente la TAE y los límites de tu propia entidad."
    }
}

TICKER_DB = {
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular", "div_yield": 5.5, "per": 8.0, "beta": 1.25},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica", "div_yield": 4.0, "per": 7.5, "beta": 1.30},
    "caixabank": {"ticker": "CABK.MC", "racha": "Sensible al ciclo económico", "div_yield": 6.2, "per": 8.5, "beta": 1.10},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable retribución flexible", "div_yield": 4.8, "per": 16.5, "beta": 0.65},
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta estabilidad", "div_yield": 2.8, "per": 24.0, "beta": 0.95},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico", "div_yield": 0.7, "per": 32.0, "beta": 0.90},
    "procter & gamble": {"ticker": "PG", "racha": "Aristócrata del Dividendo", "div_yield": 2.4, "per": 25.0, "beta": 0.55}
}

FUND_DB = {
    "axa court terme ac": {
        "name": "AXA Court Terme AC (Monetario Euro)", "ticker": "FR0000447823",
        "category": "Fondos Monetarios", "ter": 0.15, "aum": 6500, "currency": "EUR", "is_dist": False, "score": 4.8
    },
    "vanguard global stock acc": {
        "name": "Vanguard Global Stock Index Fund EUR Acc", "ticker": "IE00B03HD191",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 23000, "currency": "EUR", "is_dist": False, "score": 4.6
    },
    "vanguard japan stock acc": {
        "name": "Vanguard Japan Stock Index Fund EUR Acc", "ticker": "IE0007286036",
        "category": "Renta Variable Japón", "ter": 0.16, "aum": 3400, "currency": "EUR", "is_dist": False, "score": 4.7
    },
    "vanguard sp 500 acc": {
        "name": "Vanguard U.S. 500 Stock Index Fund EUR Acc", "ticker": "IE0032126645",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 17000, "currency": "EUR", "is_dist": False, "score": 4.8
    }
}

ETF_DB = {
    "swda.l": {
        "name": "iShares Core MSCI World UCITS ETF [Acumulación]", "ticker": "SWDA.L",
        "category": "Renta Variable Global (MSCI World)", "ter": 0.20, "aum": 68000, "currency": "EUR", "is_dist": False, "score": 4.8
    },
    "spyl.de": {
        "name": "SPDR S&P 500 UCITS ETF [Acumulación]", "ticker": "SPYL.DE",
        "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.03, "aum": 12000, "currency": "EUR", "is_dist": False, "score": 4.9
    },
    "ijpa.de": {
        "name": "iShares Core MSCI Japan IMI UCITS ETF [Acumulación]", "ticker": "IJPA.DE",
        "category": "Renta Variable Japón", "ter": 0.13, "aum": 7400, "currency": "EUR", "is_dist": False, "score": 4.8
    }
}

ETF_BROKER_PROFILES = {
    "Trade Republic (1€ orden / Planes a 0€)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "Interactive Brokers (Ideal internacional)": {"fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False},
    "XTB (0% comisiones hasta 100k€)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.20, "fx_fee_percent": 0.50, "supports_free_plans": False}
}

FUND_BROKER_PROFILES = {
    "MyInvestor (Fondos Indexados / Sin custodia)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Renta 4 (Banco tradicional)": {"fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False}
}

def get_letter_grade(score):
    if score >= 4.5: return "A+"
    elif score >= 4.0: return "A"
    elif score >= 3.0: return "B"
    else: return "C"

# ----------------------------------------------------
# ESTRUCTURA PRINCIPAL DE PESTAÑAS (SIN MENÚ LATERAL)
# ----------------------------------------------------
st.title("💰 Gestor Integral de Patrimonio y Ahorro Global")

tab_summary, tab_portfolio, tab_savings_account, tab_analyzer = st.tabs([
    "📊 PATRIMONIO TOTAL (Resumen)",
    "💼 Simulador de Cartera",
    "🏦 Cuentas Remuneradas (Auto)",
    "🔍 Analizador & Buscador de Activos"
])

# Variables para acumular resultados en la pestaña resumen
capital_liquido_cartera = 0.0
total_aportado_cartera = 0.0
capital_liquido_cr = 0.0
total_aportado_cr = 0.0
sel_account_name = "Ninguna"

# ----------------------------------------------------
# PESTAÑA 2: SIMULADOR DE CARTERA
# ----------------------------------------------------
with tab_portfolio:
    st.header("💼 Cartera de Inversión (Acciones, Fondos, ETFs, Monetarios)")
    
    if st.session_state.portfolio:
        st.markdown(f"Tienes **{len(st.session_state.portfolio)} activos** añadidos a tu cartera:")
        for idx, item in enumerate(st.session_state.portfolio):
            c_i1, c_i2, c_i3 = st.columns([3, 2, 1])
            c_i1.markdown(f"**{idx+1}. {item['name']}** (`{item['ticker']}`) - [{item['type']}]")
            c_i2.markdown(f"Categoría: {item.get('category', 'General')} | TER: {item.get('ter', 0.18)}%")
            if c_i3.button("🗑️ Quitar", key=f"del_port_{idx}"):
                st.session_state.portfolio.pop(idx)
                st.rerun()
        st.markdown("---")
    else:
        st.info("🛒 Tu cartera está vacía. Añade activos desde la pestaña **'🔍 Analizador & Buscador de Activos'**.")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        inv_ini_cartera = st.number_input("Inversión Inicial Cartera (€)", min_value=0.0, value=5000.0, step=500.0, key="cart_ini")
        app_mens_cartera = st.number_input("Aportación Mensual Cartera (€)", min_value=0.0, value=300.0, step=50.0, key="cart_mens")
    with col_p2:
        anos_cartera = st.slider("Plazo Temporal (Años)", min_value=1, max_value=40, value=15, key="cart_anos")
        rent_est_cartera = st.slider("Rentabilidad Anual Estimada (%)", min_value=0.0, max_value=15.0, value=7.5, step=0.5, key="cart_rent")
        ter_cartera = st.slider("Coste Medio de Gestión / TER (%)", min_value=0.0, max_value=2.0, value=0.18, step=0.05, key="cart_ter")

    tasa_neta_cartera = (rent_est_cartera - ter_cartera) / 100.0 / 12.0
    periodos_cartera = anos_cartera * 12
    
    saldo_cartera = inv_ini_cartera
    total_aportado_cartera = inv_ini_cartera
    for p in range(1, periodos_cartera + 1):
        saldo_cartera = saldo_cartera * (1 + tasa_neta_cartera) + app_mens_cartera
        total_aportado_cartera += app_mens_cartera
        
    beneficio_bruto_cartera = max(0.0, saldo_cartera - total_aportado_cartera)
    impuestos_cartera = beneficio_bruto_cartera * 0.19
    beneficio_neto_cartera = beneficio_bruto_cartera - impuestos_cartera
    capital_liquido_cartera = total_aportado_cartera + beneficio_neto_cartera

    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric("Capital Invertido", f"{total_aportado_cartera:,.2f} €")
    c_m2.metric("Beneficio Bruto", f"{beneficio_bruto_cartera:,.2f} €")
    c_m3.metric("Impuestos IRPF (19%)", f"{impuestos_cartera:,.2f} €")
    c_m4.metric("Capital Líquido Final", f"{capital_liquido_cartera:,.2f} €")

# ----------------------------------------------------
# PESTAÑA 3: CUENTA REMUNERADA (AUTOCARGABLE)
# ----------------------------------------------------
with tab_savings_account:
    st.header("🏦 Cuenta Remunerada / Fondo de Emergencia")
    
    sel_account_name = st.selectbox(
        "🏛️ Selecciona tu Banco / Bróker para la Cuenta Remunerada:",
        options=list(SAVINGS_ACCOUNTS_DB.keys()),
        index=2
    )
    account_info = SAVINGS_ACCOUNTS_DB[sel_account_name]
    limite_str = f"{account_info['limit']:,.0f} €" if account_info['limit'] > 0 else "Sin límite de saldo"
    
    st.markdown(f"""
    <div class="broker-badge">
        <h4 style="margin:0 0 5px 0; color:#38bdf8;">📌 {sel_account_name}</h4>
        <p style="margin:0; color:#cbd5e1; font-size:0.95rem;"><b>Condiciones:</b> {account_info['desc']}</p>
        <p style="margin:5px 0 0 0; color:#94a3b8; font-size:0.85rem;"><b>Rentabilidad Autocargada:</b> {account_info['tae']}% TAE | <b>Tope Remunerado:</b> {limite_str}</p>
    </div>
    """, unsafe_allow_html=True)

    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        saldo_ini_cuenta = st.number_input("Saldo Inicial en la Cuenta (€)", min_value=0.0, value=3000.0, step=500.0, key="cr_ini")
        app_mens_cuenta = st.number_input("Ahorro Mensual Adicional (€)", min_value=0.0, value=100.0, step=50.0, key="cr_mens")
    with col_cr2:
        tae_cuenta = st.number_input("Interés Anual TAE (% Autocargado)", min_value=0.0, max_value=15.0, value=float(account_info['tae']), step=0.05, key="cr_tae")
        anos_cuenta = st.slider("Plazo de Simulación (Años)", min_value=1, max_value=40, value=15, key="cr_anos")

    tasa_mensual_cr = (tae_cuenta / 100.0) / 12.0
    periodos_cr = anos_cuenta * 12
    saldo_cr = saldo_ini_cuenta
    total_aportado_cr = saldo_ini_cuenta
    limite_saldo = account_info['limit']
    
    for p in range(1, periodos_cr + 1):
        saldo_remunerable = limite_saldo if (limite_saldo > 0 and saldo_cr > limite_saldo) else saldo_cr
        interes_mes = saldo_remunerable * tasa_mensual_cr
        saldo_cr = saldo_cr + interes_mes + app_mens_cuenta
        total_aportado_cr += app_mens_cuenta
        
    intereses_brutos_cr = max(0.0, saldo_cr - total_aportado_cr)
    retencion_cr = intereses_brutos_cr * 0.19
    intereses_netos_cr = intereses_brutos_cr - retencion_cr
    capital_liquido_cr = total_aportado_cr + intereses_netos_cr

    st.markdown("---")
    cr_m1, cr_m2, cr_m3, cr_m4 = st.columns(4)
    cr_m1.metric("Dinero Depositado Total", f"{total_aportado_cr:,.2f} €")
    cr_m2.metric("Intereses Brutos", f"{intereses_brutos_cr:,.2f} €")
    cr_m3.metric("Retención IRPF (19%)", f"{retencion_cr:,.2f} €")
    cr_m4.metric("Saldo Neto Disponible", f"{capital_liquido_cr:,.2f} €")

# ----------------------------------------------------
# PESTAÑA 1: PATRIMONIO TOTAL (RESUMEN)
# ----------------------------------------------------
with tab_summary:
    st.header("📊 Consolidado de Patrimonio Global")
    
    total_patrimonio_liquido = capital_liquido_cartera + capital_liquido_cr
    total_dinero_aportado_global = total_aportado_cartera + total_aportado_cr
    total_ganancias_netas_global = total_patrimonio_liquido - total_dinero_aportado_global

    st.markdown(f"""
    <div class="global-card">
        <div class="global-title">💰 PATRIMONIO GLOBAL ESTIMADO TRAS IMPUESTOS</div>
        <div class="global-value">{total_patrimonio_liquido:,.2f} €</div>
    </div>
    """, unsafe_allow_html=True)

    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.markdown(f"""
        <div class="sub-card">
            <span style="color: #94a3b8; font-size: 0.9rem;">Total Capital Invertido / Ahorrado</span>
            <h2 style="color: #f8fafc; margin: 5px 0 0 0;">{total_dinero_aportado_global:,.2f} €</h2>
        </div>
        """, unsafe_allow_html=True)
    with c_g2:
        st.markdown(f"""
        <div class="sub-card">
            <span style="color: #34d399; font-size: 0.9rem;">Ganancia Neta Total Generada (Plusvalías + Intereses)</span>
            <h2 style="color: #34d399; margin: 5px 0 0 0;">+{total_ganancias_netas_global:,.2f} €</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Desglose Resumen de tus Inversiones y Ahorro")

    df_consolidado = pd.DataFrame([
        {
            "Módulo": "💼 Cartera de Inversión (Fondos/ETFs/Acciones)",
            "Dinero Aportado (€)": round(total_aportado_cartera, 2),
            "Ganancia Neta (€)": round(capital_liquido_cartera - total_aportado_cartera, 2),
            "Capital Líquido Final (€)": round(capital_liquido_cartera, 2),
            "Peso en Patrimonio (%)": round((capital_liquido_cartera / total_patrimonio_liquido) * 100, 1) if total_patrimonio_liquido > 0 else 0
        },
        {
            "Módulo": f"🏦 Cuenta Remunerada ({sel_account_name.split('(')[0].strip()})",
            "Dinero Aportado (€)": round(total_aportado_cr, 2),
            "Ganancia Neta (€)": round(intereses_netos_cr, 2),
            "Capital Líquido Final (€)": round(capital_liquido_cr, 2),
            "Peso en Patrimonio (%)": round((capital_liquido_cr / total_patrimonio_liquido) * 100, 1) if total_patrimonio_liquido > 0 else 0
        }
    ])

    st.table(df_consolidado)

# ----------------------------------------------------
# PESTAÑA 4: ANALIZADOR & BUSCADOR DE ACTIVOS
# ----------------------------------------------------
with tab_analyzer:
    st.header("🔍 Analizador & Buscador de Activos")
    st.markdown("Busca y evalúa acciones, fondos indexados, ETFs y monetarios, y añádelos directamente a tu cartera:")

    tipo_activo_sel = st.selectbox("Selecciona el tipo de activo a evaluar:", ["Acciones", "Fondos Indexados", "ETFs", "Fondos Monetarios"])

    if tipo_activo_sel == "Acciones":
        acc_choice = st.selectbox("Selecciona una acción:", list(TICKER_DB.keys()))
        data = TICKER_DB[acc_choice]
        st.markdown(f"### Acciones de {acc_choice.title()} (`{data['ticker']}`)")
        st.markdown(f"**Racha / Perfil:** {data['racha']} | **PER:** {data['per']} | **Dividend Yield:** {data['div_yield']}%")
        
        if st.button("➕ Añadir a mi Cartera", key="add_acc"):
            st.session_state.portfolio.append({
                "type": "Acción", "name": acc_choice.title(), "ticker": data["ticker"],
                "ter": 0.0, "currency": "EUR", "category": "Renta Variable (Acción)"
            })
            st.success(f"¡{acc_choice.title()} añadido a tu cartera!")

    elif tipo_activo_sel == "Fondos Indexados":
        fund_choice = st.selectbox("Selecciona un fondo:", list(FUND_DB.keys()))
        fdata = FUND_DB[fund_choice]
        st.markdown(f"### {fdata['name']}")
        st.markdown(f"**ISIN:** `{fdata['ticker']}` | **TER:** {fdata['ter']}% | **Patrimonio:** {fdata['aum']} M€")
        
        if st.button("➕ Añadir a mi Cartera", key="add_fund"):
            st.session_state.portfolio.append({
                "type": "Fondo Indexado", "name": fdata['name'], "ticker": fdata['ticker'],
                "ter": fdata['ter'], "currency": fdata['currency'], "category": fdata['category']
            })
            st.success(f"¡{fdata['name']} añadido a tu cartera!")

    elif tipo_activo_sel == "ETFs":
        etf_choice = st.selectbox("Selecciona un ETF:", list(ETF_DB.keys()))
        edata = ETF_DB[etf_choice]
        st.markdown(f"### {edata['name']}")
        st.markdown(f"**Ticker:** `{edata['ticker']}` | **TER:** {edata['ter']}% | **Categoría:** {edata['category']}")
        
        if st.button("➕ Añadir a mi Cartera", key="add_etf"):
            st.session_state.portfolio.append({
                "type": "ETF", "name": edata['name'], "ticker": edata['ticker'],
                "ter": edata['ter'], "currency": edata['currency'], "category": edata['category']
            })
            st.success(f"¡{edata['name']} añadido a tu cartera!")

    elif tipo_activo_sel == "Fondos Monetarios":
        mon_choice = [k for k, v in FUND_DB.items() if v["category"] == "Fondos Monetarios"]
        if mon_choice:
            mdata = FUND_DB[mon_choice[0]]
            st.markdown(f"### {mdata['name']}")
            st.markdown(f"**ISIN:** `{mdata['ticker']}` | **TER:** {mdata['ter']}% | **Perfil:** Seguridad y Corto Plazo")
            
            if st.button("➕ Añadir a mi Cartera", key="add_mon"):
                st.session_state.portfolio.append({
                    "type": "Fondo Monetario", "name": mdata['name'], "ticker": mdata['ticker'],
                    "ter": mdata['ter'], "currency": mdata['currency'], "category": mdata['category']
                })
                st.success(f"¡{mdata['name']} añadido a tu cartera!")
