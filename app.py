import streamlit as st
import pandas as pd
import io
import json

st.set_page_config(page_title="Analizador Bursátil y Legislativo", page_icon="📈", layout="wide")

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
    .note-box { background: #1e293b; border-left: 4px solid #38bdf8; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
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
if 'notes' not in st.session_state:
    st.session_state.notes = []

def cargar_desde_url():
    if 'data_loaded' not in st.session_state:
        if "favs" in st.query_params:
            try: st.session_state.favorites = json.loads(st.query_params["favs"])
            except: st.session_state.favorites = []
        if "port" in st.query_params:
            try: st.session_state.portfolio = json.loads(st.query_params["port"])
            except: st.session_state.portfolio = []
        if "notes" in st.query_params:
            try: st.session_state.notes = json.loads(st.query_params["notes"])
            except: st.session_state.notes = []
        st.session_state.data_loaded = True

cargar_desde_url()

def guardar_en_url():
    try:
        st.query_params["favs"] = json.dumps(st.session_state.favorites)
        st.query_params["port"] = json.dumps(st.session_state.portfolio)
        st.query_params["notes"] = json.dumps(st.session_state.notes)
    except: pass

def reset_navigation():
    st.session_state.stage = 'home'
    st.session_state.asset_type = None
    st.session_state.sub_type = None

TICKER_DB = {
    "inditex": {"ticker": "ITX.MC", "racha": "Muy alta (Décadas cuidando al accionista con pagos estables).", "div_yield": 2.8, "per": 24.0, "beta": 0.95, "payout": 60.0, "nota": "Regla mnemotécnica: INDITEX = Inversión Noble Dividendo Interesante Temporal EXcepcional."},
    "iberdrola": {"ticker": "IBE.MC", "racha": "Impecable (Programa de retribución flexible consolidado).", "div_yield": 4.8, "per": 16.5, "beta": 0.65, "payout": 70.0, "nota": "Regla mnemotécnica: IBERDROLA = Ingresos Beneficios Estables Repartidos Dividendos Ordinarios Ley Acumulada."},
    "microsoft": {"ticker": "MSFT", "racha": "Sólido crecimiento tecnológico.", "div_yield": 0.7, "per": 32.0, "beta": 0.90, "payout": 25.0, "nota": "Regla mnemotécnica: MSFT = Mayor Software Financiero Tecnológico."},
    "procter & gamble": {"ticker": "PG", "racha": "Aristócrata del Dividendo.", "div_yield": 2.4, "per": 25.0, "beta": 0.55, "payout": 60.0, "nota": "Regla mnemotécnica: PG = Pureza Global en dividendos ininterrumpidos."}
}

MASTER_CATALOG = {
    "📁 [Fondo] Vanguard Global Stock Index EUR Acc (Acumulación) - TER 0.18%": {
        "name": "Vanguard Global Stock Acc", "ticker": "IE00B03HD191", "ter": 0.18, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0, "aum": 23000,
        "nota": "Ventaja fiscal de traspasabilidad en España sin tributar en IRPF hasta el reembolso definitivo."
    },
    "📁 [Fondo] Vanguard Global Stock Index EUR Dist (Distribución) - TER 0.18%": {
        "name": "Vanguard Global Stock Dist", "ticker": "IE00B03HD209", "ter": 0.18, "type": "Fondo Indexado", "is_dist": True, "div_yield": 1.8, "aum": 4500,
        "nota": "Reparto periódico de efectivo sujeto a retención del 19% en la base del ahorro."
    },
    "📁 [Fondo] iShares Developed World Index (Acumulación) - TER 0.12%": {
        "name": "iShares Developed World Acc", "ticker": "IE00BD0NCM55", "ter": 0.12, "type": "Fondo Indexado", "is_dist": False, "div_yield": 0.0, "aum": 25000,
        "nota": "Excelente alternativa de bajo coste para replicar mercados desarrollados."
    },
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Acumulación) - TER 0.22%": {
        "name": "Vanguard All-World Acc", "ticker": "VWCE.DE", "ter": 0.22, "type": "ETF", "is_dist": False, "div_yield": 0.0, "aum": 15000,
        "nota": "Diversificación global total en un único título cotizado."
    },
    "🌐 [ETF] Vanguard FTSE All-World UCITS ETF (Distribución) - TER 0.22%": {
        "name": "Vanguard All-World Dist", "ticker": "VWRL.DE", "ter": 0.22, "type": "ETF", "is_dist": True, "div_yield": 2.1, "aum": 8000,
        "nota": "Ideal para inversores que buscan flujo de caja trimestral por dividendos."
    },
    "🌐 [ETF] SPDR S&P 500 UCITS ETF (Acumulación) - TER 0.03%": {
        "name": "SPDR S&P 500 Acc", "ticker": "SPYL.DE", "ter": 0.03, "type": "ETF", "is_dist": False, "div_yield": 0.0, "aum": 12000,
        "nota": "El ETF con menor coste de Europa para replicar el S&P 500."
    },
    "🌐 [ETF] Invesco Physical Gold ETC (Oro Físico) - TER 0.12%": {
        "name": "Invesco Physical Gold SGLD", "ticker": "SGLD.L", "ter": 0.12, "type": "ETF", "is_dist": False, "div_yield": 0.0, "aum": 14000,
        "nota": "Respaldo físico en lingotes de oro custodiados en Londres."
    },
    "🌐 [ETF] United States Oil Fund (Petróleo Crudo - USO) - TER 0.60%": {
        "name": "US Oil Fund USO", "ticker": "USO", "ter": 0.60, "type": "ETF", "is_dist": False, "div_yield": 0.0, "aum": 1200,
        "nota": "Exposición a contratos de futuros de petróleo crudo WTI."
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
notes_count = len(st.session_state.notes)

col_tb1, col_tb2, col_tb3, col_tb4 = st.columns([2, 1, 1, 1])
with col_tb1:
    st.markdown("### 📈 Analizador y Notas Mnemotécnicas")
with col_tb2:
    if st.button(f"⭐ Favoritos ({favorites_count})", use_container_width=True):
        st.session_state.stage = "favorites_view"
        st.rerun()
with col_tb3:
    if st.button(f"📝 Notas ({notes_count})", use_container_width=True):
        st.session_state.stage = "notes_view"
        st.rerun()
with col_tb4:
    if st.button(f"💼 Cartera ({portfolio_count})", use_container_width=True, type="primary"):
        st.session_state.stage = "portfolio_view"
        st.rerun()

st.markdown("---")

with st.sidebar:
    st.header("📊 Menú Principal")
    if st.button("🏠 Inicio", use_container_width=True):
        reset_navigation()
        st.rerun()
    if st.button("⚔️ Comparador Total", use_container_width=True):
        st.session_state.stage = "comparator_view"
        st.rerun()
    if st.button("📊 Analizador Individual", use_container_width=True):
        st.session_state.stage = "sub_options"
        st.rerun()
    if st.button("📝 Mis Notas y Reglas", use_container_width=True):
        st.session_state.stage = "notes_view"
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
# ANALIZADOR INDIVIDUAL (CON TABLAS Y NOTAS MNEMOTÉCNICAS)
# ----------------------------------------------------
elif st.session_state.stage == 'sub_options':
    if st.button("← Volver al Menú"):
        reset_navigation()
        st.rerun()

    st.title("📊 Analizador Individual de Activos")
    
    eval_choice = st.selectbox("Selecciona categoría", options=["Acción", "Fondo Indexado / ETF"])
    
    if eval_choice == "Acción":
        stock_key = st.selectbox("Selecciona empresa", options=list(TICKER_DB.keys()))
        s_data = TICKER_DB[stock_key]
        
        st.markdown(f"### Informe de Acción: {stock_key.title()} ({s_data['ticker']})")
        st.info(f"**Historial / Racha:** {s_data['racha']}")
        
        df_metrics = pd.DataFrame({
            "Métrica Clave": ["Ticker", "PER (Valoración)", "Dividendo Yield", "Beta", "Payout Ratio"],
            "Valor Evaluado": [s_data['ticker'], f"{s_data['per']:.1f}", f"{s_data['div_yield']}%", f"{s_data['beta']}", f"{s_data['payout']}%"]
        })
        st.table(df_metrics)
        
        st.markdown(f"""
        <div class="note-box">
            <strong>📝 Nota / Regla Mnemotécnica Asociada:</strong><br>{s_data['nota']}
        </div>
        """, unsafe_allow_html=True)
        
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("➕ Añadir a Cartera", type="primary", use_container_width=True):
                st.session_state.portfolio.append({
                    "type": "Acción", "name": stock_key.title(), "ticker": s_data['ticker'],
                    "est_rent": 8.0, "ter": 0.0, "currency": "EUR", "is_dist": True
                })
                guardar_en_url()
                st.success("¡Acción añadida a tu Cartera!")
        with col_act2:
            if st.button("📝 Guardar Nota en Mis Notas", use_container_width=True):
                st.session_state.notes.append(f"{stock_key.title()} ({s_data['ticker']}): {s_data['nota']}")
                guardar_en_url()
                st.success("¡Nota guardada con éxito!")

    else:
        fund_label = st.selectbox("Selecciona de la lista de referencia", options=list(MASTER_CATALOG.keys()))
        f_data = MASTER_CATALOG[fund_label]
        
        st.markdown(f"### Informe: {f_data['name']}")
        modalidad_str = "Distribución (Reparto)" if f_data['is_dist'] else "Acumulación"
        
        df_metrics = pd.DataFrame({
            "Métrica del Activo": ["Identificador / ISIN", "Tipo", "Modalidad", "TER Anual (Gastos)", "Patrimonio (AUM)"],
            "Valor Actual": [f_data['ticker'], f_data['type'], modalidad_str, f"{f_data['ter']}%", f"{f_data.get('aum', 10000):,.0f} M€"]
        })
        st.table(df_metrics)
        
        st.markdown(f"""
        <div class="note-box">
            <strong>📝 Nota / Regla Mnemotécnica Asociada:</strong><br>{f_data['nota']}
        </div>
        """, unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.button("➕ Añadir a Cartera", type="primary", use_container_width=True):
                st.session_state.portfolio.append({
                    "type": f_data['type'], "name": f_data['name'], "ticker": f_data['ticker'],
                    "est_rent": 7.5, "ter": f_data['ter'], "currency": "EUR", "is_dist": f_data['is_dist']
                })
                guardar_en_url()
                st.success("¡Activo añadido a tu Cartera!")
        with col_f2:
            if st.button("📝 Guardar Nota en Mis Notas", use_container_width=True):
                st.session_state.notes.append(f"{f_data['name']} ({f_data['ticker']}): {f_data['nota']}")
                guardar_en_url()
                st.success("¡Nota guardada con éxito!")

# ----------------------------------------------------
# SECCIÓN NOTAS MNEMOTÉCNICAS
# ----------------------------------------------------
elif st.session_state.stage == 'notes_view':
    if st.button("← Volver al Menú"):
        reset_navigation()
        st.rerun()

    st.title("📝 Mis Notas y Reglas Mnemotécnicas")
    st.markdown("Aquí puedes consultar y gestionar todas las reglas mnemotécnicas y notas de estudio guardadas:")

    if not st.session_state.notes:
        st.info("No tienes notas guardadas todavía. Explora acciones o fondos y pulsa **'📝 Guardar Nota'** en sus informes.")
    else:
        for idx, note in enumerate(st.session_state.notes):
            col_n1, col_n2 = st.columns([5, 1])
            with col_n1:
                st.markdown(f"**{idx+1}.** {note}")
            with col_n2:
                if st.button("🗑️ Borrar", key=f"del_note_{idx}"):
                    st.session_state.notes.pop(idx)
                    guardar_en_url()
                    st.rerun()

        if st.button("🗑️ Vaciar Todas las Notas"):
            st.session_state.notes = []
            guardar_en_url()
            st.rerun()

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
        st.info("🛒 Tu cartera está vacía. Añade activos desde el comparador o analizador.")
    else:
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            anos_cartera = st.slider("Plazo Temporal Consolidado (Años)", min_value=1, max_value=40, value=15, key="anos_cart")
        with c_p2:
            frecuencia_cartera = st.selectbox("Frecuencia de Aportaciones", options=["Mensual", "Anual"], key="freq_cart")

        st.markdown("---")
        total_capital_bruto_acum = 0.0
        total_capital_aportado_acum = 0.0
        total_costes_acum = 0.0

        for idx, item in enumerate(st.session_state.portfolio):
            is_etf_or_stock = item['type'] in ["ETF", "Acción"]
            broker_profiles = ETF_BROKER_PROFILES if is_etf_or_stock else FUND_BROKER_PROFILES
            
            with st.expander(f"{idx+1}. {item['name']} ({item['ticker']}) - [{item['type']}]", expanded=True):
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    sel_broker = st.selectbox(f"Bróker / Entidad [#{idx+1}]", options=list(broker_profiles.keys()), key=f"p_brok_{idx}")
                with col_b2:
                    b_data = broker_profiles[sel_broker]
                    plan_sc = st.checkbox(f"Plan automático a 0€ [#{idx+1}]", value=b_data["supports_free_plans"], key=f"p_plan_{idx}")

                col_i1, col_i2, col_i3, col_i4 = st.columns([2, 2, 2, 1])
                with col_i1:
                    inv_ini = st.number_input(f"Inversión Inicial (€) [#{idx+1}]", min_value=0.0, value=3000.0, step=500.0, key=f"p_ini_{idx}")
                with col_i2:
                    app_per = st.number_input(f"Aportación Periódica (€) [#{idx+1}]", min_value=0.0, value=200.0, step=50.0, key=f"p_app_{idx}")
                with col_i3:
                    rent_est = st.slider(f"Rentabilidad anual (%) [#{idx+1}]", min_value=0.0, max_value=20.0, value=float(item.get('est_rent', 7.5)), step=0.5, key=f"p_rent_{idx}")
                with col_i4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🗑️ Quitar [#{idx+1}]", key=f"del_{idx}"):
                        st.session_state.portfolio.pop(idx)
                        guardar_en_url()
                        st.rerun()

                f_pct = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_percent"]
                f_fix = 0.0 if (b_data["supports_free_plans"] and plan_sc) else b_data["fee_fixed"]
                f_spr = b_data["spread_percent"]

                ter_val = item.get('ter', 0.20)
                periodos_ano = 12 if frecuencia_cartera == "Mensual" else 1
                tasa_neta = rent_est - ter_val
                tasa_periodica = (tasa_neta / 100.0) / periodos_ano
                tot_periodos = anos_cartera * periodos_ano

                c_broker_ini = (inv_ini * (b_data["fee_percent"] / 100.0)) + b_data["fee_fixed"]
                c_spread_ini = inv_ini * (f_spr / 100.0)
                c_tot_ini = c_broker_ini + c_spread_ini

                saldo_act = max(0.0, inv_ini - c_tot_ini)
                total_aport_acum = inv_ini
                acum_b = c_broker_ini
                acum_s = c_spread_ini

                historial_activo = []

                for p in range(1, tot_periodos + 1):
                    if p > 1:
                        cb = (app_per * (f_pct / 100.0)) + f_fix
                        cs = app_per * (f_spr / 100.0)
                        ct = cb + cs

                        import_neto = max(0.0, app_per - ct)
                        total_aport_acum += app_per
                        acum_b += cb
                        acum_s += cs
                        saldo_act = saldo_act * (1 + tasa_periodica) + import_neto
                    else:
                        saldo_act = saldo_act * (1 + tasa_periodica)

                    if p % periodos_ano == 0:
                        ano_act = p // periodos_ano
                        costes_tot_act = acum_b + acum_s
                        int_brutos = saldo_act - (total_aport_acum - costes_tot_act)

                        historial_activo.append({
                            "Año": f"Año {ano_act}",
                            "Capital Aportado (€)": round(total_aport_acum, 2),
                            "Comisiones Bróker (€)": round(acum_b, 2),
                            "Coste Spread (€)": round(acum_s, 2),
                            "Beneficio Neto (€)": round(max(0.0, int_brutos), 2),
                            "Capital Total (€)": round(saldo_act, 2)
                        })

                st.dataframe(pd.DataFrame(historial_activo), use_container_width=True)

                total_capital_bruto_acum += saldo_act
                total_capital_aportado_acum += total_aport_acum
                total_costes_acum += (acum_b + acum_s)

        if st.session_state.portfolio:
            net_aport = total_capital_aportado_acum - total_costes_acum
            beneficio_bruto = max(0.0, total_capital_bruto_acum - net_aport)
            impuestos = beneficio_bruto * 0.19
            beneficio_neto = beneficio_bruto - impuestos
            liquido_final = net_aport + beneficio_neto

            st.markdown("---")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Capital Invertido", f"{total_capital_aportado_acum:,.2f} €")
            m2.metric("Costes Totales", f"{total_costes_acum:,.2f} €")
            m3.metric("Beneficio Bruto", f"{beneficio_bruto:,.2f} €")
            m4.metric("Impuestos (19%)", f"{impuestos:,.2f} €")
            m5.metric("Beneficio Neto", f"{beneficio_neto:,.2f} €")

            st.markdown(f"""
            <div class="final-net-card">
                <div class="final-net-title">💰 Capital Total Líquido Final de tu Cartera</div>
                <div class="final-net-value">{liquido_final:,.2f} €</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🗑️ Vaciar Cartera Completa"):
                st.session_state.portfolio = []
                guardar_en_url()
                st.rerun()
