import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io
import json
import urllib.parse

def calcular_score_opcionable(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="3mo")
        if hist.empty:
            return None, "Sin datos de mercado disponibles."
        
        hist['Retornos'] = hist['Close'].pct_change()
        volatilidad_historica = hist['Retornos'].tail(20).std() * np.sqrt(252) * 100
        opciones_disponibles = len(ticker.options) > 0
        
        if not opciones_disponibles:
            return 0, "Esta acción NO tiene mercado de opciones disponible."
            
        score = 50
        if volatilidad_historica > 40:
            score += 30
            diagnostico = "Primas muy altas por alta volatilidad. Ideal para ingresos altos, pero vigila el riesgo."
        elif 20 <= volatilidad_historica <= 40:
            score += 15
            diagnostico = "Volatilidad moderada. Primas decentes con un riesgo controlado."
        else:
            score -= 20
            diagnostico = "Primas muy baratas debido a la baja volatilidad. Puede no valer la pena el riesgo."
            
        score = max(0, min(100, score))
        return int(score), diagnostico
    except Exception as e:
        return None, f"Error al procesar opciones: {str(e)}"
        
st.set_page_config(page_title="Analizador Bursátil Multifuente", page_icon="📈", layout="wide")

if 'stage' not in st.session_state: st.session_state.stage = 'home'
if 'asset_type' not in st.session_state: st.session_state.asset_type = None
if 'portfolio' not in st.session_state: st.session_state.portfolio = []
if 'favorites' not in st.session_state: st.session_state.favorites = []

st.markdown("### 📈 Analizador Bursátil")
st.markdown("---")

if st.session_state.stage == 'home':
    if st.button("📊 Acciones"):
        st.session_state.asset_type = "Acciones"
        st.session_state.stage = "analyzer"
        st.rerun()

elif st.session_state.stage == 'analyzer':
    if st.button("← Volver"):
        st.session_state.stage = 'home'
        st.rerun()
        
    user_input = st.text_input("Introduce el Ticker de la acción (ej. NVDA, AAPL):", "NVDA").upper()
    
    if user_input:
        col_info_actual, col_nota_opciones = st.columns([2, 1])
        
        with col_info_actual:
            st.subheader(f"Información General de {user_input}")
            try:
                stock = yf.Ticker(user_input)
                info = stock.info or {}
                st.write(f"**Nombre:** {info.get('longName', user_input)}")
                st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            except:
                st.write("Cargando información...")
                
        with col_nota_opciones:
            st.subheader("Análisis de Opciones")
            score, mensaje = calcular_score_opcionable(user_input)
            if score is not None:
                color_metrica = "🟢 Alta viabilidad" if score >= 70 else ("🟡 Viabilidad moderada" if score >= 40 else "🔴 Baja viabilidad")
                st.metric(label=f"Score Opcionable ({color_metrica})", value=f"{score} / 100")
                st.info(mensaje)
            else:
                st.error(mensaje)
