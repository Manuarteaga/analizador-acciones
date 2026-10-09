import streamlit as st
import yfinance as yf
import pandas as pd
import io

# ----------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------
st.set_page_config(
    page_title="Analizador Bursátil Multifuente",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# BASES DE DATOS Y PERFILES
# ----------------------------------------------------
TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables y extraordinarios).", "div_growth": 6.5, "div_yield": 2.8},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado sin recortes históricos).", "div_growth": 5.0, "div_yield": 4.8},
    "banco sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5},
    "sabadell": {"ticker": "SAB.MC", "racha": "Cíclica / Irregular (Sujeta a los altibajos históricos del sector financiero).", "div_growth": 2.0, "div_yield": 5.5},
    "banco santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0},
    "santander": {"ticker": "SAN.MC", "racha": "Cíclica / Con antecedentes de ajuste en crisis pasadas.", "div_growth": 2.5, "div_yield": 4.0},
    "telefonica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5},
    "telefónica": {"ticker": "TEF.MC", "racha": "Irregular / Con recortes históricos y reestructuraciones de deuda.", "div_growth": 1.0, "div_yield": 6.5},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico sin dependencia de dividendo tradicional.", "div_growth": 10.0, "div_yield": 0.7},
    "procter & gamble": {"ticker": "PG", "racha": "Excepcional. Aristócrata del Dividendo con más de 65 años de subidas ininterrumpidas.", "div_growth": 6.0, "div_yield": 2.4},
    "copart": {"ticker": "CPRT", "racha": "Empresa pura de crecimiento orientada a reinvestigación.", "div_growth": 0.0, "div_yield": 0.0},
    "caixabank": {"ticker": "CABK.MC", "racha": "Cíclica / Sensible al ciclo económico y a los planes de consolidación bancaria.", "div_growth": 4.5, "div_yield": 6.2}
}

FUND_DB = {
    "vanguard global stock acc": {"name": "Vanguard Global Stock Index Fund EUR Acc", "category": "Renta Variable Global (MSCI World)", "ter": 0.18, "aum": 4500, "tracking_error": 0.08, "age_years": 8},
    "vanguard s&p 500 acc": {"name": "Vanguard S&P 500 Stock Index Fund EUR Acc", "category": "Renta Variable EE.UU. (S&P 500)", "ter": 0.10, "aum": 38000, "tracking_error": 0.03, "age_years": 12},
    "amundi msci world acc": {"name": "Amundi Index MSCI World AE-C", "category": "Renta Variable Global (MSCI World)", "ter": 0.30, "aum": 3200, "tracking_error": 0.12, "age_years": 7}
}

ETF_DB = {
    "vwce.de": {"name": "Vanguard FTSE All-World UCITS ETF (Acc)", "ticker": "VWCE.DE", "category": "Renta Variable Global", "ter": 0.22, "aum": 12500, "replication": "Física (Completa)", "te": 0.04, "currency": "EUR", "age_years": 6},
    "spyl.de": {"name": "SPDR S&P 500 UCITS ETF (Acc)", "ticker": "SPYL.DE", "category": "Renta Variable EE.UU.", "ter": 0.03, "aum": 8200, "replication": "Física (Completa)", "te": 0.02, "currency": "EUR", "age_years": 3},
    "sgld.l": {"name": "iShares Physical Gold ETC", "ticker": "SGLD.L", "category": "Materias Primas (Oro Físico)", "ter": 0.15, "aum": 14500, "replication": "Física (Lingotes)", "te": 0.01, "currency": "USD", "age_years": 11},
    "IEMG": {"name": "iShares Core MSCI Emerging Markets IMI ETF", "ticker": "IEMG", "category": "Empresas Emergentes", "ter": 0.09, "aum": 78000, "replication": "Física (Muestreo)", "te": 0.06, "currency": "USD", "age_years": 12},
    "qdve.de": {"name": "iShares S&P 500 Information Technology Sector ETF", "ticker": "QDVE.DE", "category": "Tecnología", "ter": 0.15, "aum": 4200, "replication": "Física (Completa)", "te": 0.05, "currency": "EUR", "age_years": 6},
    "INRG.MI": {"name": "iShares Global Clean Energy UCITS ETF", "ticker": "INRG.MI", "category": "Energías Renovables", "ter": 0.65, "aum": 2800, "replication": "Física (Completa)", "te": 0.18, "currency": "EUR", "age_years": 15},
    "EXV1.DE": {"name": "iShares STOXX Europe 600 Utilities UCITS ETF", "ticker": "EXV1.DE", "category": "Eléctricas y Utilities", "ter": 0.46, "aum": 1100, "replication": "Física (Completa)", "te": 0.08, "currency": "EUR", "age_years": 20},
    "VHYL.DE": {"name": "Vanguard FTSE All-World High Dividend Yield ETF", "ticker": "VHYL.DE", "category": "Dividendos Globales", "ter": 0.29, "aum": 4100, "replication": "Física (Completa)", "te": 0.05, "currency": "EUR", "age_years": 10}
}

ALL_BROKER_PROFILES = {
    "0% / Sin comisiones (Ej. XTB, Lightyear, Trading 212)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.15, "supports_free_plans": True
    },
    "MyInvestor (Fondos Indexados / Sin custodia)": {
        "fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True
    },
    "Indexa Capital (Cartera / Gestor automatizado)": {
        "fee_percent": 0.45, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True
    },
    "Trade Republic (1€ orden suelta / Planes a 0€)": {
        "fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True
    },
    "DEGIRO (Bajas comisiones / 1€ por operación)": {
        "fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False
    },
    "Interactive Brokers (Ideal internacional)": {
        "fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False
    },
    "Renta 4 (Banco tradicional / Tarifas altas)": {
        "fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False
    }
}

# ----------------------------------------------------
# FUNCIÓN PRINCIPAL DE LA APLICACIÓN
# ----------------------------------------------------
def main():
    # Control de Estados de Navegación
    if 'stage' not in st.session_state:
        st.session_state.stage = 'home'
    if 'asset_type' not in st.session_state:
        st.session_state.asset_type = None
    if 'sub_type' not in st.session_state:
        st.session_state.sub_type = None
    if 'history' not in st.session_state:
        st.session_state.history = []

    def reset_navigation():
        st.session_state.stage = 'home'
        st.session_state.asset_type = None
        st.session_state.sub_type = None

    # Sidebar profesional
    with st.sidebar:
        st.markdown("### 📊 Panel de Control")
        st.markdown(f"**Activos analizados:** `{len(st.session_state.history)}`")
        st.markdown("---")
        
        if st.session_state.history:
            df_history = pd.DataFrame(st.session_state.history)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_history.to_excel(writer, sheet_name='Evaluaciones', index=False)
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Exportar Excel de Sesión",
                data=excel_data,
                file_name="analisis_bursatil.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
            
            if st.button("🗑️ Limpiar Historial", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        else:
            st.info("Realiza una simulación para exportar los datos.")

        if st.session_state.stage != 'home':
            st.markdown("---")
            if st.button("🏠 Menú Principal", use_container_width=True):
                reset_navigation()
                st.rerun()

    # ----------------------------------------------------
    # ETAPA 0: LANDING / PANTALLA INICIAL
    # ----------------------------------------------------
    if st.session_state.stage == 'home':
        st.title("📈 Analizador Bursátil Multifuente")
        st.markdown("#### Selecciona el instrumento financiero que deseas evaluar:")
        st.markdown("")

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
            if st.button("💼 Cartera Multi-Activo", use_container_width=True, type="primary"):
                st.session_state.asset_type = "Cartera Multi-Activo"
                st.session_state.stage = "analyzer"
                st.rerun()

    # ----------------------------------------------------
    # ETAPA 1: SUBOPCIONES SEGÚN EL ACTIVO SELECCIONADO
    # ----------------------------------------------------
    elif st.session_state.stage == 'sub_options':
        if st.button("← Volver"):
            reset_navigation()
            st.rerun()

        st.title(f"Configuración: {st.session_state.asset_type}")
        
        if st.session_state.asset_type == "Acciones":
            st.markdown("### Selecciona la modalidad:")
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
            st.markdown("### Selecciona el tipo de análisis:")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔍 Ranking de Fondos por Menor TER", use_container_width=True, type="primary"):
                    st.session_state.sub_type = "Ranking TER"
                    st.session_state.stage = "analyzer"
                    st.rerun()
            with c2:
                if st.button("✍️ Evaluar con Buscador Predictivo", use_container_width=True):
                    st.session_state.sub_type = "Acumulación"
                    st.session_state.stage = "analyzer"
                    st.rerun()

        elif st.session_state.asset_type == "ETFs":
            st.markdown("### Selecciona la herramienta ETF:")
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🗺️ Guía y Tipos de ETFs", use_container_width=True, type="primary"):
                    st.session_state.sub_type = "Explorador ETFs"
                    st.session_state.stage = "analyzer"
                    st.rerun()
            with c2:
                if st.button("🏆 Ranking por Menor TER", use_container_width=True):
                    st.session_state.sub_type = "Ranking ETFs"
                    st.session_state.stage = "analyzer"
                    st.rerun()
            with c3:
                if st.button("🔍 Evaluar ETF Específico", use_container_width=True):
                    st.session_state.sub_type = "Evaluación ETF"
                    st.session_state.stage = "analyzer"
                    st.rerun()

    # ----------------------------------------------------
    # ETAPA 2: ANALIZADOR Y CARTERA MULTI-ACTIVO
    # ----------------------------------------------------
    elif st.session_state.stage == 'analyzer':
        if st.button("← Volver al selector"):
            reset_navigation()
            st.rerun()

        if st.session_state.asset_type == "Cartera Multi-Activo":
            st.title("💼 Simulador de Cartera Multi-Activo")
            st.markdown("Configura tu distribución de activos, costes de bróker y proyecciones a largo plazo.")
            
            st.markdown("---")
            st.subheader("1️⃣ Parámetros Generales")
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                anos_cartera = st.slider("Plazo temporal (Años)", min_value=1, max_value=40, value=20, key="cartera_anos")
                frecuencia_cartera = st.selectbox("Frecuencia de aportación", options=["Mensual", "Anual"], key="cartera_freq")
            with col_g2:
                num_activos = st.slider("Número de activos en cartera", min_value=1, max_value=6, value=4, step=1, key="num_act")

            st.markdown("---")
            st.subheader("2️⃣ Configuración de Activos (Fondos y ETFs)")

            lista_opciones_activos = [
                "📁 [Fondo] Vanguard S&P 500 Stock Index Fund EUR Acc (Acumulación)",
                "📁 [Fondo] Vanguard Global Stock Index Fund EUR Acc (MSCI World - Acumulación)",
                "📁 [Fondo] Amundi Index MSCI World AE-C (Acumulación)",
                "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Acumulación)",
                "🌐 [ETF] Vanguard FTSE All-World High Dividend Yield ETF (Distribución - Paga Dividendos)",
                "🌐 [ETF] iShares Physical Gold ETC",
                "🌐 [ETF] iShares Core MSCI Emerging Markets IMI ETF",
                "🌐 [ETF] iShares S&P 500 Information Technology Sector ETF",
                "✍️ Personalizado / Otro activo"
            ]
            
            activos_config = []
            hay_activo_distribucion = False
            
            for i in range(num_activos):
                default_idx = i if i < len(lista_opciones_activos) else 0
                with st.expander(f"📌 Activo {i+1}", expanded=(i < 2)):
                    selected_asset_option = st.selectbox(f"Selecciona el Activo {i+1}", options=lista_opciones_activos, index=default_idx, key=f"sel_asset_{i}")
                    
                    es_distribucion = "Distribución" in selected_asset_option or "Dividend" in selected_asset_option
                    if es_distribucion:
                        hay_activo_distribucion = True

                    default_ter, default_rent = 0.15, 7.0
                    if "S&P 500" in selected_asset_option:
                        default_ter, default_rent = 0.10, 8.0
                    elif "World" in selected_asset_option or "All-World" in selected_asset_option:
                        default_ter, default_rent = 0.18, 7.0
                    elif "Gold" in selected_asset_option:
                        default_ter, default_rent = 0.15, 5.5
                    elif "Dividend" in selected_asset_option:
                        default_ter, default_rent = 0.29, 6.5
                    elif "Fondo" in selected_asset_option:
                        default_ter = 0.18

                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        inv_ini_act = st.number_input(f"Inversión Inicial (€) - {i+1}", min_value=0.0, value=100.0, step=50.0, key=f"ini_{i}")
                        app_per_act = st.number_input(f"Aportación Periódica (€) - {i+1}", min_value=0.0, value=50.0, step=25.0, key=f"app_{i}")
                    with col_i2:
                        rent_act = st.slider(f"Rentabilidad anual estimada (%) - {i+1}", min_value=0.0, max_value=15.0, value=default_rent, step=0.5, key=f"rent_{i}")
                        ter_act = st.slider(f"TER anual del activo (%) - {i+1}", min_value=0.0, max_value=1.0, value=default_ter, step=0.05, key=f"ter_{i}")
                    
                    st.markdown(f"**Bróker o Gestora:**")
                    broker_choice_i = st.selectbox(f"Bróker {i+1}", options=list(ALL_BROKER_PROFILES.keys()), key=f"broker_{i}", label_visibility="collapsed")
                    broker_data_i = ALL_BROKER_PROFILES[broker_choice_i]
                    
                    plan_gratis_i = st.checkbox(f"🚀 Plan de aportación periódica a 0 €", value=broker_data_i["supports_free_plans"], key=f"plan_sc_{i}")

                    activos_config.append({
                        "nombre": selected_asset_option,
                        "inicial": inv_ini_act,
                        "aportacion": app_per_act,
                        "rentabilidad": rent_act,
                        "ter": ter_act,
                        "broker_data": broker_data_i,
                        "plan_gratis": plan_gratis_i,
                        "es_distribucion": es_distribucion
                    })

            # SIMULACIÓN GLOBAL ACUMULADA
            periodos_por_ano = 12 if frecuencia_cartera == "Mensual" else 1
            total_periodos = anos_cartera * periodos_por_ano

            total_aportado_acumulado = 0.0
            acum_broker_global = 0.0
            acum_spread_global = 0.0
            acum_fx_global = 0.0
            saldo_global_neto = 0.0
            
            acum_dividendos_brutos = 0.0

            for act in activos_config:
                ini = act["inicial"]
                b_data = act["broker_data"]
                
                c_broker_ini = (ini * (b_data["fee_percent"] / 100.0)) + b_data["fee_fixed"]
                c_spread_ini = ini * (b_data["spread_percent"] / 100.0)
                c_fx_ini = ini * (b_data["fx_fee_percent"] / 100.0)
                coste_ini_total = c_broker_ini + c_spread_ini + c_fx_ini

                saldo_global_neto += max(0.0, ini - coste_ini_total)
                total_aportado_acumulado += ini
                acum_broker_global += c_broker_ini
                acum_spread_global += c_spread_ini
                acum_fx_global += c_fx_ini

            historial_cartera_indiv = []

            for periodo in range(1, total_periodos + 1):
                neto_total_periodo = 0.0
                
                if periodo > 1:
                    for act in activos_config:
                        app = act["aportacion"]
                        b_data = act["broker_data"]
                        is_free = act["plan_gratis"]
                        
                        f_fix = 0.0 if is_free else b_data["fee_fixed"]
                        f_perc = 0.0 if is_free else b_data["fee_percent"]
                        
                        cb = (app * (f_perc / 100.0)) + f_fix
                        cs = app * (b_data["spread_percent"] / 100.0)
                        cfx = app * (b_data["fx_fee_percent"] / 100.0)
                        c_op_total = cb + cs + cfx

                        neto_aportado = max(0.0, app - c_op_total)
                        total_aportado_acumulado += app
                        
                        acum_broker_global += cb
                        acum_spread_global += cs
                        acum_fx_global += cfx
                        
                        neto_total_periodo += neto_aportado

                rent_media_pond = sum([a["rentabilidad"] - a["ter"] for a in activos_config]) / len(activos_config)
                tasa_periodica_global = (rent_media_pond / 100.0) / periodos_por_ano

                if periodo > 1:
                    saldo_global_neto = saldo_global_neto * (1 + tasa_periodica_global) + neto_total_periodo
                else:
                    saldo_global_neto = saldo_global_neto * (1 + tasa_periodica_global)

                if hay_activo_distribucion and periodo % periodos_por_ano == 0:
                    pesos_dist = sum([1 for a in activos_config if a["es_distribucion"]]) / len(activos_config)
                    dividendo_periodo_bruto = (saldo_global_neto * pesos_dist) * 0.03
                    acum_dividendos_brutos += dividendo_periodo_bruto

                if periodo % periodos_por_ano == 0:
                    ano_actual = periodo // periodos_por_ano
                    total_costes_acum = acum_broker_global + acum_spread_global + acum_fx_global
                    intereses_brutos = saldo_global_neto - (total_aportado_acumulado - total_costes_acum)

                    fila_historial = {
                        "Año": f"Año {ano_actual}",
                        "Capital Aportado Bruto (€)": round(total_aportado_acumulado, 2),
                        "Comisiones Bróker (€)": round(acum_broker_global, 2),
                        "Coste Spread / Divisa (€)": round(acum_spread_global + acum_fx_global, 2),
                        "Beneficio Bruto (€)": round(max(0.0, intereses_brutos), 2),
                        "Capital Total Bruto (€)": round(saldo_global_neto, 2)
                    }
                    if hay_activo_distribucion:
                        fila_historial["Dividendos Brutos Acumulados (€)"] = round(acum_dividendos_brutos, 2)
                    
                    historial_cartera_indiv.append(fila_historial)

            if historial_cartera_indiv:
                final_c = historial_cartera_indiv[-1]
                beneficio_bruto_f = final_c['Beneficio Bruto (€)']
                
                impuestos_plusvalia = beneficio_bruto_f * 0.19
                impuestos_dividendos = acum_dividendos_brutos * 0.19 if hay_activo_distribucion else 0.0
                dividendos_netos = acum_dividendos_brutos - impuestos_dividendos

                capital_neto_aportado_real = final_c['Capital Aportado Bruto (€)'] - (final_c['Comisiones Bróker (€)'] + final_c['Coste Spread / Divisa (€)'])
                capital_total_liquido_f = capital_neto_aportado_real + (beneficio_bruto_f - impuestos_plusvalia) + dividendos_netos

                st.markdown("---")
                st.subheader("📊 Resultados Globales")

                # Métricas nativas de Streamlit
                col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                
                with col_m1:
                    st.metric("Capital Acumulado", f"{final_c['Capital Total Bruto (€)']:,.0f} €")
                with col_m2:
                    st.metric("Aportado Bruto", f"{final_c['Capital Aportado Bruto (€)']:,.0f} €")
                with col_m3:
                    st.metric("Total Costes", f"{(final_c['Comisiones Bróker (€)'] + final_c['Coste Spread / Divisa (€)']):,.2f} €")
                with col_m4:
                    st.metric("Beneficio Bruto", f"{beneficio_bruto_f:,.0f} €")
                with col_m5:
                    st.metric("Impuestos (19%)", f"{(impuestos_plusvalia + impuestos_dividendos):,.2f} €")

                if hay_activo_distribucion:
                    st.info("ℹ️ Activo de **Distribución** detectado: Los dividendos netos cobrados se han integrado al saldo líquido total.")
                    dm1, dm2 = st.columns(2)
                    with dm1:
                        st.metric("💰 Dividendos Brutos", f"{acum_dividendos_brutos:,.2f} €")
                    with dm2:
                        st.metric("💵 Dividendos Netos (19%)", f"{dividendos_netos:,.2f} €")

                # Contenedor Destacado Principal para el Ahorro Líquido
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #065f46 0%, #047857 100%); border: 2px solid #34d399; padding: 24px; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px rgba(4, 120, 87, 0.4); margin: 25px 0px;">
                    <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; color: #a7f3d0; margin-bottom: 6px; font-weight: 700;">
                        💰 Capital Total Líquido (Ahorro Real Neto Tras Impuestos y Costes)
                    </div>
                    <div style="font-size: 2.4rem; font-weight: 900; color: #ffffff;">
                        {capital_total_liquido_f:,.2f} €
                    </div>
                </div>
                """, unsafe_allow_html=True)

                df_res_cartera = pd.DataFrame(historial_cartera_indiv)
                with st.expander("📈 Ver desglose temporal detallado por año", expanded=False):
                    st.dataframe(df_res_cartera, use_container_width=True)

        # ----------------------------------------------------
        # RESTO DE APARTADOS (ACCIONES, FONDOS, ETFS)
        # ----------------------------------------------------
        elif st.session_state.asset_type == "Fondos indexados" and st.session_state.sub_type == "Ranking TER":
            st.title("🏆 Ranking de Fondos Indexados (Menor TER)")
            ranking_data = [{"Fondo": data["name"], "Categoría": data["category"], "TER Anual (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Antigüedad (Años)": data["age_years"]} for data in FUND_DB.values()]
            df_ranking = pd.DataFrame(ranking_data).sort_values(by="TER Anual (%)", ascending=True).reset_index(drop=True)
            st.dataframe(df_ranking, use_container_width=True)
            st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER (gastos corrientes) de la gestora.")

        elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Ranking ETFs":
            st.title("🏆 Ranking de ETFs (Menor TER)")
            ranking_etfs = [{"ETF": data["name"], "Ticker": data["ticker"], "Categoría": data["category"], "TER (%)": data["ter"], "Patrimonio (M€)": data["aum"], "Réplica": data["replication"]} for data in ETF_DB.values()]
            df_etf_ranking = pd.DataFrame(ranking_etfs).sort_values(by="TER (%)", ascending=True).reset_index(drop=True)
            st.dataframe(df_etf_ranking, use_container_width=True)
            st.info("⚠️ **Aviso de Comisiones:** Los costes mostrados corresponden exclusivamente al TER (gastos corrientes) de la gestora.")

        elif st.session_state.asset_type == "ETFs" and st.session_state.sub_type == "Explorador ETFs":
            st.title("🗺️ Guía y Tipos de ETFs Disponibles")
            st.markdown("Selecciona una categoría para examinar su objetivo y perfil de riesgo:")
            
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🌍 Globales", "💰 Dividendos", "🥇 Materias Primas", "💻 Tecnología", "⚡ Renovables & Utilities", "🚀 Emergentes"])
            
            with tab1:
                st.subheader("Renta Variable Global (Ej: MSCI World / FTSE All-World)")
                st.markdown("- **Objetivo:** Inversión diversificada en miles de empresas globales.")
                st.markdown("- **Perfil de riesgo:** Moderado-Alto.")
                st.markdown("- *Ejemplo en BD:* `Vanguard FTSE All-World UCITS ETF (Acc)`")
                
            with tab2:
                st.subheader("Empresas de Alto Dividendo")
                st.markdown("- **Objetivo:** Empresas maduras con flujos de caja estables enfocadas en retribución al accionista.")
                st.markdown("- **Perfil de riesgo:** Moderado (defensivo).")
                st.markdown("- *Ejemplo en BD:* `Vanguard FTSE All-World High Dividend Yield ETF`")

            with tab3:
                st.subheader("Materias Primas (Commodities / ETCs)")
                st.markdown("- **Objetivo:** Exposición directa a activos físicos como oro o metales.")
                st.markdown("- **Perfil de riesgo:** Medio-Alto (refugio contra inflación).")
                st.markdown("- *Ejemplo en BD:* `iShares Physical Gold ETC`")

            with tab4:
                st.subheader("Sector Tecnológico")
                st.markdown("- **Objetivo:** Gigantes de la innovación y software.")
                st.markdown("- **Perfil de riesgo:** Alto.")
                st.markdown("- *Ejemplo en BD:* `iShares S&P 500 Information Technology Sector ETF`")

            with tab5:
                st.subheader("Energías Renovables y Utilities")
                st.markdown("- **Objetivo:** Transición energética y compañías eléctricas reguladas.")
                st.markdown("- **Perfil de riesgo:** Variable.")
                st.markdown("- *Ejemplos en BD:* `iShares Global Clean Energy` / `iShares STOXX Europe 600 Utilities`")

            with tab6:
                st.subheader("Empresas Emergentes")
                st.markdown("- **Objetivo:** Economías en rápido desarrollo (Asia, Latinoamérica).")
                st.markdown("- **Perfil de riesgo:** Alto.")
                st.markdown("- *Ejemplo en BD:* `iShares Core MSCI Emerging Markets IMI ETF`")

if __name__ == '__main__':
    main()
