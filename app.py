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
    .final-net-title { font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; color: #a7f3d0; margin-bottom: 5px; font-weight: 600; }
    .final-net-value { font-size: 2.2rem; font-weight: 800; color: #ffffff; }
    .featured-card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #38bdf8; border-radius: 12px; padding: 22px; margin-bottom: 10px; }
    .featured-badge { background-color: #0284c7; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 8px; }
    .score-tag { background-color: #065f46; color: #34d399; padding: 3px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; float: right; }
    .compare-box { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# Control de Estados
if 'stage' not in st.session_state:
    st.session_state.stage = 'home'
if 'asset_type' not in st.session_state:
    st.session_state.asset_type = None
if 'sub_type' not in st.session_state:
    st.session_state.sub_type = None
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

cargar_desde_url()

def guardar_en_url():
    try:
        st.query_params["favs"] = json.dumps(st.session_state.favorites)
        st.query_params["port"] = json.dumps(st.session_state.portfolio)
    except: pass

def reset_navigation():
    st.session_state.stage = 'home'
    st.session_state.asset_type = None
    st.session_state.sub_type = None
    st.session_state.selected_eval_input = ""

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas de pagos estables).", "div_yield": 2.8, "per": 24.0},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Retribución flexible consolidada).", "div_yield": 4.8, "per": 16.5},
    "microsoft": {"ticker": "MSFT", "racha": "Crecimiento tecnológico.", "div_yield": 0.7, "per": 32.0},
    "procter & gamble": {"ticker": "PG", "racha": "Aristócrata del Dividendo.", "div_yield": 2.4, "per": 25.0}
}

MASTER_CATALOG = {
    "📁 [Fondo] Vanguard Global Stock Index EUR Acc (Acumulación) - TER 0.18%": {
        "name": "Vanguard Global Stock Acc", "ticker": "IE00B03HD191", "ter": 0.18, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Vanguard Global Stock Index EUR Dist (Distribución) - TER 0.18%": {
        "name": "Vanguard Global Stock Dist", "ticker": "IE00B03HD209", "ter": 0.18, "type": "Fondo Indexado", "is_dist": True, "div_yield": 1.8
    },
    "📁 [Fondo] iShares Developed World Index (Acumulación) - TER 0.12%": {
        "name": "iShares Developed World Acc", "ticker": "IE00BD0NCM55", "ter": 0.12, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Fidelity MSCI World Index Fund (Acumulación) - TER 0.10%": {
        "name": "Fidelity MSCI World Acc", "ticker": "IE00BYX5NX33", "ter": 0.10, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Acumulación) - TER 0.22%": {
        "name": "Vanguard All-World Acc", "ticker": "VWCE.DE", "ter": 0.22, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Distribución) - TER 0.22%": {
        "name": "Vanguard All-World Dist", "ticker": "VWRL.DE", "ter": 0.22, "type": "ETF", "is_dist": True, "div_yield": 2.1
    },
    "🌐 [ETF] iShares Core MSCI World UCITS ETF (Acumulación) - TER 0.20%": {
        "name": "iShares Core MSCI World Acc", "ticker": "SWDA.L", "ter": 0.20, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Vanguard U.S. 500 Stock Index EUR Acc (Acumulación) - TER 0.10%": {
        "name": "Vanguard S&P 500 Acc", "ticker": "IE0032126645", "ter": 0.10, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "📁 [Fondo] Fidelity S&P 500 Index EUR P Acc (Acumulación) - TER 0.06%": {
        "name": "Fidelity S&P 500 Acc", "ticker": "IE00BYX5MX67", "ter": 0.06, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] SPDR S&P 500 UCITS ETF (Acumulación) - TER 0.03%": {
        "name": "SPDR S&P 500 Acc", "ticker": "SPYL.DE", "ter": 0.03, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Vanguard High Dividend Yield ETF (Distribución) - TER 0.06%": {
        "name": "Vanguard High Dividend VYM", "ticker": "VYM", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 3.0
    },
    "🌐 [ETF] Schwab U.S. Dividend Equity ETF (Distribución) - TER 0.06%": {
        "name": "Schwab Dividend SCHD", "ticker": "SCHD", "ter": 0.06, "type": "ETF", "is_dist": True, "div_yield": 3.4
    },
    "🌐 [ETF] Invesco Physical Gold ETC (Oro Físico) - TER 0.12%": {
        "name": "Invesco Physical Gold SGLD", "ticker": "SGLD.L", "ter": 0.12, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] SPDR Gold Shares (Oro Físico - GLD) - TER 0.40%": {
        "name": "SPDR Gold Shares GLD", "ticker": "GLD", "ter": 0.40, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] United States Oil Fund (Petróleo Crudo - USO) - TER 0.60%": {
        "name": "US Oil Fund USO", "ticker": "USO", "ter": 0.60, "type": "ETF", "is_dist": False, "div_yield": 0.0
    },
    "🌐 [ETF] Invesco EQQQ NASDAQ-100 UCITS ETF (Tecnología) - TER 0.30%": {
        "name": "Invesco NASDAQ-100 EQQQ", "ticker": "EQQQ.DE", "ter": 0.30, "type": "ETF", "is_dist": False, "div_yield": 0.0
    }
}

FUND_BROKER_PROFILES = {
    "MyInvestor (0% custodia)": {"fee_percent": 0.0, "fee_fixed": 0.0, "spread_percent": 0.05, "fx_fee_percent": 0.30, "supports_free_plans": True},
    "Renta 4": {"fee_percent": 0.25, "fee_fixed": 8.00, "spread_percent": 0.30, "fx_fee_percent": 0.50, "supports_free_plans": False}
}

ETF_BROKER_PROFILES = {
    "Trade Republic (Planes 0€)": {"fee_percent": 0.0, "fee_fixed": 0.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": True},
    "Interactive Brokers": {"fee_percent": 0.0, "fee_fixed": 1.50, "spread_percent": 0.02, "fx_fee_percent": 0.03, "supports_free_plans": False},
    "DEGIRO": {"fee_percent": 0.0, "fee_fixed": 1.00, "spread_percent": 0.10, "fx_fee_percent": 0.25, "supports_free_plans": False}
}

portfolio_count = len(st.session_state.portfolio)
favorites_count = len(st.session_state.favorites)

col_tb1, col_tb2, col_tb3 = st.columns([2, 1, 1])
with col_tb1:
    st.markdown("### 📈 Analizador Bursátil Total")
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
    st.header("📊 Menú de Navegación")
    if st.button("🏠 Inicio", use_container_width=True):
        reset_navigation()
        st.rerun()
    if st.button("⚔️ Comparador Total", use_container_width=True):
        st.session_state.stage = "comparator_view"
        st.rerun()
    if st.button("📊 Analizador Individual", use_container_width=True):
        st.session_state.stage = "sub_options"
        st.rerun()

# ----------------------------------------------------
# HOME
# ----------------------------------------------------
if st.session_state.stage == 'home':
    st.markdown("### ¿Qué deseas hacer hoy?")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚔️ Comparador de Fondos y ETFs", use_container_width=True, type="primary"):
            st.session_state.stage = "comparator_view"
            st.rerun()
    with c2:
        if st.button("📊 Analizar Activo Individual", use_container_width=True, type="primary"):
            st.session_state.stage = "sub_options"
            st.rerun()
    with c3:
        if st.button("💼 Ver Cartera Consolidada", use_container_width=True, type="primary"):
            st.session_state.stage = "portfolio_view"
            st.rerun()

    st.markdown("---")
    st.markdown("### 🌟 Recomendado del Mes")
    st.markdown("""
    <div class="featured-card">
        <span class="featured-badge">Top Inversión Global • ETF</span>
        <span class="score-tag">⭐ 4.7/5 (A+)</span>
        <h3 style="margin: 10px 0 6px 0; color: #f8fafc;">SPDR S&P 500 UCITS ETF (Acc)</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 15px;">Ticker: SPYL.DE | TER ultra bajo: 0.03% (Máxima eficiencia en costes para renta variable americana)</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# COMPARADOR TOTAL
# ----------------------------------------------------
elif st.session_state.stage == 'comparator_view':
    if st.button("← Volver al Menú"):
        reset_navigation()
        st.rerun()

    st.title("⚔️ Comparador Total: Fondos y ETFs (Catálogo Completo)")
    st.markdown("Selecciona de 2 a 4 activos directamente del desplegable para comparar comisiones, fiscalidad y rendimiento.")

    num_compare = st.slider("Número de activos:", min_value=2, max_value=4, value=2)
    st.markdown("---")
    cols_sel = st.columns(num_compare)
    selected_assets_config = []
    catalog_keys = list(MASTER_CATALOG.keys())

    for i in range(num_compare):
        with cols_sel[i]:
            st.markdown(f"### 📋 Activo {i+1}")
            chosen_label = st.selectbox(f"Selecciona activo {i+1}", options=catalog_keys, index=i if i < len(catalog_keys) else 0, key=f"cat_sel_{i}")
            asset_data = MASTER_CATALOG[chosen_label]
            st.info(f"**Tipo:** {asset_data['type']} | **TER:** {asset_data['ter']}%")

            inv_ini_i = st.number_input(f"Inv. Inicial (€) [A{i+1}]", min_value=0.0, value=3000.0, step=500.0, key=f"ini_{i}")
            app_per_i = st.number_input(f"Aportación Mensual (€) [A{i+1}]", min_value=0.0, value=200.0, step=50.0, key=f"app_{i}")
            anos_i = st.slider(f"Plazo (Años) [A{i+1}]", min_value=1, max_value=40, value=15, key=f"anos_{i}")
            rent_i = st.slider(f"Rentabilidad Est. (%) [A{i+1}]", min_value=1.0, max_value=20.0, value=7.5, step=0.5, key=f"rent_{i}")

            selected_assets_config.append({
                "type": asset_data["type"], "name": asset_data["name"], "ticker": asset_data["ticker"],
                "ter": asset_data["ter"], "is_dist": asset_data["is_dist"], "div_yield": asset_data["div_yield"],
                "inv_ini": inv_ini_i, "app_per": app_per_i, "anos": anos_i, "rent": rent_i
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
                imp_div = div_anual * 0.19
                total_div_brutos += div_anual
                total_div_impuestos += imp_div
                saldo -= div_anual

        beneficio_bruto = max(0.0, saldo - total_aportado)
        tasa_impuesto_venta = 0.0 if cfg["type"] == "Fondo Indexado" else 0.19
        impuestos_venta = beneficio_bruto * tasa_impuesto_venta
        beneficio_neto = beneficio_bruto - impuestos_venta
        capital_liquido = total_aportado + beneficio_neto + (total_div_brutos - total_div_impuestos if cfg["is_dist"] else 0.0)
        return total_aportado, saldo, beneficio_bruto, impuestos_venta, total_div_brutos, total_div_impuestos, capital_liquido

    st.markdown("---")
    st.markdown("## 📊 Resultados de la Comparativa")
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
                <p>Plazo: <strong>{cfg['anos']} años</strong> | Rent: <strong>{cfg['rent']}%</strong></p>
                <p>Capital Invertido: <strong>{aport:,.2f} €</strong></p>
                <p>Valor Cartera Final: <strong>{saldo:,.2f} €</strong></p>
                {"<p>Dividendos Netos: <strong>" + f"{(div_b - div_imp):,.2f} €</strong></p>" if cfg["is_dist"] else f"<p>Impuestos Venta (19%): <strong>-{imp_venta:,.2f} €</strong></p>"}
                <h3 style="color: #34d399; margin-top: 15px;">Líquido Total: {liq:,.2f} €</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"➕ Añadir a Cartera [A{i+1}]", key=f"add_c_{i}", use_container_width=True):
                st.session_state.portfolio.append({
                    "type": cfg['type'], "name": cfg['name'], "ticker": cfg['ticker'],
                    "est_rent": cfg['rent'], "ter": cfg['ter'], "currency": "EUR", "is_dist": cfg['is_dist']
                })
                guardar_en_url()
                st.success(f"¡{cfg['name']} añadido a Cartera!")

# ----------------------------------------------------
# SUBOPCIONES / ANALIZADOR INDIVIDUAL
# ----------------------------------------------------
elif st.session_state.stage == 'sub_options':
    if st.button("← Volver"):
        reset_navigation()
        st.rerun()
    st.title("📊 Analizador Individual de Activos")
    
    asset_choice = st.selectbox("Selecciona categoría a analizar", options=["Acciones", "Fondos Indexados / ETFs"])
    ticker_eval = st.text_input("Introduce Ticker o ISIN (ej. ITX.MC, SPYL.DE, SGLD.L):", value="SPYL.DE").strip()

    if ticker_eval:
        try:
            stock = yf.Ticker(ticker_eval)
            hist = stock.history(period="3mo")
            info = stock.info or {}
            name = info.get('longName', ticker_eval)
            price = hist['Close'].iloc[-1] if not hist.empty else 0.0

            st.markdown(f"### Informe para: {name}")
            st.metric("Precio Actual", f"{price:,.2f} {info.get('currency', 'EUR')}")
            if not hist.empty:
                st.line_chart(hist['Close'])
        except Exception as e:
            st.error(f"No se pudieron cargar datos para {ticker_eval}: {e}")

# ----------------------------------------------------
# FAVORITOS Y CARTERA CONSOLIDADA
# ----------------------------------------------------
elif st.session_state.stage == 'favorites_view':
    if st.button("← Volver"):
        reset_navigation()
        st.rerun()
    st.title("⭐ Mis Activos Favoritos")
    if not st.session_state.favorites:
        st.info("No hay favoritos guardados.")
    else:
        for fav in st.session_state.favorites:
            st.markdown(f"- **{fav['name']}** ({fav['ticker']})")

elif st.session_state.stage == 'portfolio_view':
    if st.button("← Volver al Menú"):
        reset_navigation()
        st.rerun()

    st.title("💼 Simulador Global de Cartera Consolidada")
    if not st.session_state.portfolio:
        st.info("🛒 Tu cartera está vacía. Añade activos desde el comparador.")
    else:
        for idx, item in enumerate(st.session_state.portfolio):
            with st.expander(f"{idx+1}. {item['name']} ({item['ticker']})"):
                st.markdown(f"**Tipo:** {item['type']} | **TER:** {item['ter']}%")
                if st.button("🗑️ Quitar", key=f"del_p_{idx}"):
                    st.session_state.portfolio.pop(idx)
                    guardar_en_url()
                    st.rerun()
