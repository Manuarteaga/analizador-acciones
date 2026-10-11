import streamlit as st
import pandas as pd
import io
import json

st.set_page_config(page_title="Analizador y Comparador Bursátil Total", page_icon="📈", layout="wide")

st.markdown("""
<style>
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

# Catálogo completo unificado de referencia (Fondos y ETFs de Acumulación y Distribución)
MASTER_CATALOG = {
    # FONDOS INDEXADOS
    "📁 [Fondo] Vanguard Global Stock Index EUR Acc (Acumulación) - TER 0.18%": {
        "name": "Vanguard Global Stock Acc", "ticker": "IE00B03HD191", "ter": 0.18, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Vanguard Global Stock Index EUR Dist (Distribución) - TER 0.18%": {
        "name": "Vanguard Global Stock Dist", "ticker": "IE00B03HD209", "ter": 0.18, "type": "Fondo Indexado", "is_dist": True, "div_yield": 1.8
    },
    "📁 [Fondo] iShares Developed World Index (Acumulación) - TER 0.12%": {
        "name": "iShares Developed World Acc", "ticker": "IE00BD0NCM55", "ter": 0.12, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Vanguard U.S. 500 Stock Index EUR Acc (Acumulación) - TER 0.10%": {
        "name": "Vanguard S&P 500 Acc", "ticker": "IE0032126645", "ter": 0.10, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Fidelity S&P 500 Index EUR P Acc (Acumulación) - TER 0.06%": {
        "name": "Fidelity S&P 500 Acc", "ticker": "IE00BYX5MX67", "ter": 0.06, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },

    # ETFS
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Acumulación) - TER 0.22%": {
        "name": "Vanguard FTSE All-World Acc", "ticker": "VWCE.DE", "ter": 0.22, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Distribución) - TER 0.22%": {
        "name": "Vanguard FTSE All-World Dist", "ticker": "VWRL.DE", "ter": 0.22, "type": "ETF", "is_dist": True, "div_yield": 2.1
    },
    "🌐 [ETF] iShares Core MSCI World UCITS ETF (Acumulación) - TER 0.20%": {
        "name": "iShares Core MSCI World Acc", "ticker": "SWDA.L", "ter": 0.20, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] SPDR S&P 500 UCITS ETF (Acumulación) - TER 0.03%": {
        "name": "SPDR S&P 500 Acc", "ticker": "SPYL.DE", "ter": 0.03, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard High Dividend Yield ETF (Distribución) - TER 0.06%": {
        "name": "Vanguard High Dividend Yield", "ticker": "VYM", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 3.0
    },
    "🌐 [ETF] Invesco Physical Gold ETC (Materias Primas - Oro) - TER 0.12%": {
        "name": "Invesco Physical Gold", "ticker": "SGLD.L", "ter": 0.12, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] United States Oil Fund (Materias Primas - Crudo) - TER 0.60%": {
        "name": "US Oil Fund (Crudo)", "ticker": "USO", "ter": 0.60, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Invesco EQQQ NASDAQ-100 UCITS ETF (Tecnología) - TER 0.30%": {
        "name": "Invesco NASDAQ-100", "ticker": "EQQQ.DE", "ter": 0.30, "type": "ETF", "is_dist": False, "div_yield": 0.0
    }
}

st.title("⚔️ Comparador Directo de Fondos y ETFs")
st.markdown("""
Selecciona cuántos activos quieres comparar y **elije directamente del desplegable** cualquier fondo (acumulación o distribución) o ETF (bajo coste, reparto de dividendos, oro, crudo, tecnología) para contrastar comisiones de TER, fiscalidad y rendimiento neto.
""")

num_compare = st.slider("Número de activos a comparar simultáneamente:", min_value=2, max_value=4, value=2)

st.markdown("---")
cols_sel = st.columns(num_compare)
selected_assets_config = []

catalog_keys = list(MASTER_CATALOG.keys())

for i in range(num_compare):
    with cols_sel[i]:
        st.markdown(f"### 📋 Activo {i+1}")
        
        # Único selector directo con todo el catálogo
        chosen_label = st.selectbox(
            f"Selecciona activo {i+1}",
            options=catalog_keys,
            index=i if i < len(catalog_keys) else 0,
            key=f"cat_sel_{i}"
        )
        
        asset_data = MASTER_CATALOG[chosen_label]
        
        st.info(f"**Tipo:** {asset_data['type']} | **TER:** {asset_data['ter']}%")

        # Permitir ajustar parámetros de simulación personalizados
        inv_ini_i = st.number_input(f"Inv. Inicial (€) [A{i+1}]", min_value=0.0, value=3000.0, step=500.0, key=f"ini_{i}")
        app_per_i = st.number_input(f"Aportación Mensual (€) [A{i+1}]", min_value=0.0, value=200.0, step=50.0, key=f"app_{i}")
        anos_i = st.slider(f"Plazo (Años) [A{i+1}]", min_value=1, max_value=40, value=15, key=f"anos_{i}")
        rent_i = st.slider(f"Rentabilidad Bruta Est. (%) [A{i+1}]", min_value=1.0, max_value=20.0, value=7.5, step=0.5, key=f"rent_{i}")

        selected_assets_config.append({
            "type": asset_data["type"],
            "name": asset_data["name"],
            "ticker": asset_data["ticker"],
            "ter": asset_data["ter"],
            "is_dist": asset_data["is_dist"],
            "div_yield": asset_data["div_yield"],
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
            imp_div = div_anual * 0.19 # 19% IRPF base del ahorro en España
            total_div_brutos += div_anual
            total_div_impuestos += imp_div
            saldo -= div_anual

    beneficio_bruto = max(0.0, saldo - total_aportado)
    # Los fondos indexados en España permiten traspasos sin peaje fiscal. Los ETFs tributan al vender.
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
        modalidad = f"📥 Distribución ({cfg['div_yield']}%)" if cfg["is_dist"] else "🔄 Acumulación"
        st.markdown(f"""
        <div class="compare-box">
            <h3 style="color: #38bdf8; font-size: 1rem;">{cfg['type']}</h3>
            <h4 style="font-size: 0.95rem; min-height: 40px;">{cfg['name']}</h4>
            <p><strong>Identificador:</strong> {cfg['ticker']}</p>
            <p><strong>TER:</strong> {cfg['ter']}% | <strong>Modalidad:</strong> {modalidad}</p>
            <hr style="border-color: #334155;">
            <p>Plazo: <strong>{cfg['anos']} años</strong> | Rent. Bruta: <strong>{cfg['rent']}%</strong></p>
            <p>Capital Invertido: <strong>{aport:,.2f} €</strong></p>
            <p>Valor Cartera Final: <strong>{saldo:,.2f} €</strong></p>
            {"<p>Dividendos Netos Cobrados: <strong>" + f"{(div_b - div_imp):,.2f} €</strong></p>" if cfg["is_dist"] else f"<p>Impuestos Venta (19%): <strong>-{imp_venta:,.2f} €</strong></p>"}
            <h3 style="color: #34d399; margin-top: 15px;">Líquido Total: {liq:,.2f} €</h3>
        </div>
        """, unsafe_allow_html=True)
