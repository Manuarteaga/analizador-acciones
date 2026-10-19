import streamlit as st
import yfinance as yf
import pandas as pd
import json

st.set_page_config(page_title="Gestor Integral de Patrimonio y Cuentas", page_icon="💰", layout="wide")

# Estilos CSS personalizados
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
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# BASE DE DATOS ACTUALIZADA DE CUENTAS REMUNERADAS
# ----------------------------------------------------
SAVINGS_ACCOUNTS_DB = {
    "Revolut (Cuenta Remunerada Promocional)": {
        "tae": 3.51, "tin": 3.45, "limit": 25000,
        "desc": "3,51% TAE promocional (4 meses para nuevos clientes). Cobro diario de intereses."
    },
    "Openbank (Cuenta Remunerada)": {
        "tae": 3.25, "tin": 3.20, "limit": 0,  # 0 representa sin límite
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
        "desc": "2,75% TAE para la Cuenta Save sin exigencias adicionales (hasta 3,15% en Cuenta Health)."
    },
    "Banco Sabadell (Cuenta Online)": {
        "tae": 2.75, "tin": 2.72, "limit": 100000,
        "desc": "2,75% TAE durante el primer año hasta 100.000 € + devoluciones en recibos."
    },
    "MyInvestor (Cuenta Remunerada)": {
        "tae": 2.50, "tin": 2.47, "limit": 70000,
        "desc": "2,50% TAE el primer año hasta 70.000 € (o sube a 3,25% TAE si contratas fondos/planes)."
    },
    "Abanca (Cuenta Remunerada)": {
        "tae": 2.00, "tin": 2.00, "limit": 50000,
        "desc": "2,00% TAE durante los primeros 12 meses para saldos hasta 50.000 €."
    },
    "N26 (Cuenta Ahorro Estandar)": {
        "tae": 1.30, "tin": 1.50, "limit": 50000,
        "desc": "1,30% TAE en cuenta estándar sin cuotas mensuales."
    },
    "ING (Cuenta Naranja + Nómina)": {
        "tae": 1.00, "tin": 1.00, "limit": 0,
        "desc": "1,00% TAE combinando la Cuenta Nómina con la Cuenta Naranja sin límite de saldo."
    },
    "Personalizado / Ajuste Manual": {
        "tae": 2.50, "tin": 2.47, "limit": 0,
        "desc": "Permite introducir manualmente la TAE y los límites de tu propia entidad bancaria."
    }
}

st.title("💰 Gestor Integral de Patrimonio y Ahorro Global")

# ----------------------------------------------------
# ESTRUCTURA DE PESTAÑAS PRINCIPALES
# ----------------------------------------------------
tab_summary, tab_portfolio, tab_savings_account, tab_analyzer = st.tabs([
    "📊 PATRIMONIO TOTAL (Resumen)",
    "💼 Simulador de Cartera",
    "🏦 Cuentas Remuneradas (Auto)",
    "🔍 Analizador Individual"
])

# ----------------------------------------------------
# PESTAÑA 2: SIMULADOR DE CARTERA DE INVERSIÓN
# ----------------------------------------------------
with tab_portfolio:
    st.header("💼 Cartera de Inversión (Acciones, Fondos, ETFs, Monetarios)")
    st.markdown("Configura las posiciones de tu cartera de inversión para la proyección global:")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        inv_ini_cartera = st.number_input("Inversión Inicial Cartera (€)", min_value=0.0, value=5000.0, step=500.0, key="cart_ini")
        app_mens_cartera = st.number_input("Aportación Mensual Cartera (€)", min_value=0.0, value=300.0, step=50.0, key="cart_mens")
    with col_p2:
        anos_cartera = st.slider("Plazo Temporal (Años)", min_value=1, max_value=40, value=15, key="cart_anos")
        rent_est_cartera = st.slider("Rentabilidad Anual Estimada (%)", min_value=0.0, max_value=15.0, value=7.5, step=0.5, key="cart_rent")
        ter_cartera = st.slider("Coste Medio de Gestión / TER (%)", min_value=0.0, max_value=2.0, value=0.18, step=0.05, key="cart_ter")

    # Cálculo Cartera
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
# PESTAÑA 3: CUENTA REMUNERADA (AUTOCARGABLE POR BRÓKER)
# ----------------------------------------------------
with tab_savings_account:
    st.header("🏦 Cuenta Remunerada / Fondo de Emergencia")
    st.markdown("Selecciona una entidad bancaria o bróker para cargar sus datos y condiciones oficiales de forma automática:")

    # Selección de Entidad
    sel_account_name = st.selectbox(
        "🏛️ Selecciona tu Banco / Bróker para la Cuenta Remunerada:",
        options=list(SAVINGS_ACCOUNTS_DB.keys()),
        index=2  # Por defecto Trade Republic
    )
    
    account_info = SAVINGS_ACCOUNTS_DB[sel_account_name]

    # Ficha informativa del bróker seleccionado
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
        # Los valores se autocargan por defecto pero son editables por el usuario si lo desea
        tae_cuenta = st.number_input("Interés Anual TAE (% Autocargado)", min_value=0.0, max_value=15.0, value=float(account_info['tae']), step=0.05, key="cr_tae")
        anos_cuenta = st.slider("Plazo de Simulación (Años)", min_value=1, max_value=40, value=anos_cartera, key="cr_anos")

    # Cálculo Cuenta Remunerada (Teniendo en cuenta posibles límites de saldo)
    tasa_mensual_cr = (tae_cuenta / 100.0) / 12.0
    periodos_cr = anos_cuenta * 12
    
    saldo_cr = saldo_ini_cuenta
    total_aportado_cr = saldo_ini_cuenta
    limite_saldo = account_info['limit']
    
    for p in range(1, periodos_cr + 1):
        # Si la entidad tiene límite, solo remuneramos hasta ese saldo tope
        if limite_saldo > 0 and saldo_cr > limite_saldo:
            saldo_remunerable = limite_saldo
        else:
            saldo_remunerable = saldo_cr
            
        interes_mes = saldo_remunerable * tasa_mensual_cr
        saldo_cr = saldo_cr + interes_mes + app_mens_cuenta
        total_aportado_cr += app_mens_cuenta
        
    intereses_brutos_cr = max(0.0, saldo_cr - total_aportado_cr)
    retencion_cr = intereses_brutos_cr * 0.19  # Retención IRPF por rendimientos del capital mobiliario
    intereses_netos_cr = intereses_brutos_cr - retencion_cr
    capital_liquido_cr = total_aportado_cr + intereses_netos_cr

    st.markdown("---")
    cr_m1, cr_m2, cr_m3, cr_m4 = st.columns(4)
    cr_m1.metric("Dinero Depositado Total", f"{total_aportado_cr:,.2f} €")
    cr_m2.metric("Intereses Brutos", f"{intereses_brutos_cr:,.2f} €")
    cr_m3.metric("Retención IRPF (19%)", f"{retencion_cr:,.2f} €")
    cr_m4.metric("Saldo Neto Disponible", f"{capital_liquido_cr:,.2f} €")

# ----------------------------------------------------
# PESTAÑA 1: CONSOLIDACIÓN Y PATRIMONIO TOTAL
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
    st.markdown("### 📋 Desglose Resumen de tus Inversiones")

    df_consolidado = pd.DataFrame([
        {
            "Módulo": "💼 Cartera de Inversión (Fondos/ETFs/Acciones)",
            "Dinero Aportado (€)": round(total_aportado_cartera, 2),
            "Ganancia Neta (€)": round(beneficio_neto_cartera, 2),
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
# PESTAÑA 4: ANALIZADOR DE ACTIVOS INDIVIDUALES
# ----------------------------------------------------
with tab_analyzer:
    st.header("🔍 Analizador Individual de Activos")
    st.info("Utiliza este apartado si deseas consultar métricas en tiempo real de cualquier Acción, Fondo o ETF individual.")
