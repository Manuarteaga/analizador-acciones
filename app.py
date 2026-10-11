import streamlit as st
import yfinance as yf
import pandas as pd
import io
import json

st.set_page_config(page_title="Analizador y Comparador Bursátil Total", page_icon="📈", layout="wide")

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
    .compare-box {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
    }
    .final-net-card {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        border: 2px solid #34d399;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Control de Estados
if 'stage' not in st.session_state:
    st.session_state.stage = 'comparator_view'
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'favorites' not in st.session_state:
    st.session_state.favorites = []

FUND_BROKER_PROFILES = {
    "MyInvestor (0% custodia / Fondos)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Renta 4 / Bancos Tradicionales": {"fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False}
}

ETF_BROKER_PROFILES = {
    "Trade Republic (1€ orden / Planes 0€)": {"fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "Interactive Brokers (Bajo coste)": {"fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False},
    "DEGIRO": {"fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False}
}

st.title("⚔️ Comparador Total: Fondos vs ETFs (Buscador Global)")
st.markdown("""
Compara **fondos indexados entre sí**, **ETFs entre sí**, o **mezcla fondos con ETFs** para descubrir cuál te ofrece mayor rentabilidad neta real tras restar el **TER**, las comisiones del bróker/banco y el impacto fiscal (ventaja de traspasabilidad en fondos vs costes de fricción en ETFs).
""")

num_compare = st.slider("Número de activos a comparar simultáneamente:", min_value=2, max_value=4, value=2)

st.markdown("---")
cols_sel = st.columns(num_compare)
selected_assets_config = []

for i in range(num_compare):
    with cols_sel[i]:
        st.markdown(f"### 🔍 Activo {i+1}")
        
        tipo_vehiculo = st.radio("Tipo de Vehículo", options=["Fondo Indexado", "ETF / Accion"], key=f"t_veh_{i}")
        
        search_query_i = st.text_input(
            f"Buscar {tipo_vehiculo} {i+1} (ej. 'MSCI World', 'S&P 500', 'VWCE', 'Gold')",
            value="IE00B03HD191" if i == 0 and tipo_vehiculo == "Fondo Indexado" else ("SPYL.DE" if i == 1 else "SGLD.L"),
            key=f"q_{i}"
        ).strip()

        # Opciones en tiempo real vía Yahoo Finance Search
        slot_options = {}
        try:
            rt_results = yf.Search(search_query_i, max_results=12).quotes
            for item in rt_results:
                sym = item.get('symbol')
                sname = item.get('shortname', item.get('longname', sym))
                ex = item.get('exchange', '')
                if sym:
                    slot_options[f"{sname} ({sym}) [{ex}]"] = {"name": sname, "ticker": sym}
        except:
            pass

        if not slot_options:
            slot_options[f"{search_query_i.upper()}"] = {"name": search_query_i.upper(), "ticker": search_query_i.upper()}

        chosen_label = st.selectbox(f"Selecciona de resultados [A{i+1}]", options=list(slot_options.keys()), key=f"sel_{i}")
        chosen_asset = slot_options[chosen_label]

        # Parámetros financieros del activo
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            ter_i = st.number_input(f"TER Anual (%) [A{i+1}]", min_value=0.0, max_value=2.0, value=0.18 if tipo_vehiculo=="Fondo Indexado" else 0.07, step=0.01, key=f"ter_{i}")
        with col_p2:
            is_dist_i = st.checkbox(f"Distribución (Reparto)", value=False, key=f"dist_{i}")

        div_yield_i = 0.0
        if is_dist_i:
            div_yield_i = st.slider(f"Div. Yield (%) [A{i+1}]", min_value=0.5, max_value=6.0, value=2.0, step=0.1, key=f"dy_{i}")

        inv_ini_i = st.number_input(f"Inv. Inicial (€) [A{i+1}]", min_value=0.0, value=3000.0, step=500.0, key=f"ini_{i}")
        app_per_i = st.number_input(f"Aportación Mensual (€) [A{i+1}]", min_value=0.0, value=200.0, step=50.0, key=f"app_{i}")
        anos_i = st.slider(f"Plazo (Años) [A{i+1}]", min_value=1, max_value=40, value=15, key=f"anos_{i}")
        rent_i = st.slider(f"Rentabilidad Bruta (%) [A{i+1}]", min_value=1.0, max_value=20.0, value=7.5, step=0.5, key=f"rent_{i}")

        selected_assets_config.append({
            "type": tipo_vehiculo,
            "name": chosen_asset["name"],
            "ticker": chosen_asset["ticker"],
            "ter": ter_i,
            "is_dist": is_dist_i,
            "div_yield": div_yield_i,
            "inv_ini": inv_ini_i,
            "app_per": app_per_i,
            "anos": anos_i,
            "rent": rent_i
        })

def simular_activo(cfg):
    periodos = cfg["anos"] * 12
    tasa_neta_anual = max(0.0, cfg["rent"] - cfg["ter"])
    tasa_periodica = (tasa_neta_anual / 100.0) / 12.0
    
    saldo = cfg["inv_ini"]
    total_aportado = cfg["inv_ini"]
    total_div_brutos = 0.0
    total_div_impuestos = 0.0
    
    for p in range(1, periodos + 1):
        if p > 1:
            saldo = saldo * (1 + tasa_periodica) + cfg["app_per"]
            total_aportado += cfg["app_per"]
        else:
            saldo = saldo * (1 + tasa_periodica)
            
        if cfg["is_dist"] and p % 12 == 0:
            div_anual = saldo * (cfg["div_yield"] / 100.0)
            imp_div = div_anual * 0.19 # 19% IRPF España
            total_div_brutos += div_anual
            total_div_impuestos += imp_div
            saldo -= div_anual # Sale en efectivo

    beneficio_bruto = max(0.0, saldo - total_aportado)
    # Los fondos en España tienen ventaja de traspaso sin peaje fiscal. Los ETFs pagan 19% al vender.
    tasa_impuesto_venta = 0.0 if cfg["type"] == "Fondo Indexado" else 0.19
    impuestos_venta = beneficio_bruto * tasa_impuesto_venta
    beneficio_neto = beneficio_bruto - impuestos_venta
    
    capital_liquido = total_aportado + beneficio_neto + (total_div_brutos - total_div_impuestos if cfg["is_dist"] else 0.0)
    
    return total_aportado, saldo, beneficio_bruto, impuestos_venta, total_div_brutos, total_div_impuestos, capital_liquido

st.markdown("---")
st.markdown("## 📊 Resultados de la Comparativa Directa")

cols_res = st.columns(num_compare)

for i, cfg in enumerate(selected_assets_config):
    aport, saldo, b_bruto, imp_venta, div_b, div_imp, liq = simular_activo(cfg)
    
    with cols_res[i]:
        modalidad = "📥 Distribución" if cfg["is_dist"] else "🔄 Acumulación"
        st.markdown(f"""
        <div class="compare-box">
            <h3 style="color: #38bdf8; font-size: 1rem;">{cfg['type']}</h3>
            <h4 style="font-size: 0.95rem; min-height: 40px;">{cfg['name']}</h4>
            <p><strong>Ticker/ISIN:</strong> {cfg['ticker']}</p>
            <p><strong>TER:</strong> {cfg['ter']}% | <strong>Modalidad:</strong> {modalidad}</p>
            <hr style="border-color: #334155;">
            <p>Plazo: <strong>{cfg['anos']} años</strong> | Rent. Bruta: <strong>{cfg['rent']}%</strong></p>
            <p>Capital Invertido: <strong>{aport:,.2f} €</strong></p>
            <p>Valor Cartera Final: <strong>{saldo:,.2f} €</strong></p>
            {"<p>Dividendos Netos Cobrados: <strong>" + f"{(div_b - div_imp):,.2f} €</strong></p>" if cfg["is_dist"] else f"<p>Impuestos Venta (19%): <strong>-{imp_venta:,.2f} €</strong></p>"}
            <h3 style="color: #34d399; margin-top: 15px;">Líquido Total: {liq:,.2f} €</h3>
        </div>
        """, unsafe_allow_html=True)
