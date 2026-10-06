import streamlit as st
import yfinance as yf
import pandas as pd
import io

st.set_page_config(page_title="Analizador Bursátil Automático", page_icon="📈", layout="wide")

# Estilos CSS con el sello oficial circular y banda central estilo "Credit Note"
st.markdown("""
<style>
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 50px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        margin-bottom: 20px;
        border: 1px solid #334155;
    }
    .circular-progress {
        position: relative;
        width: 120px;
        height: 120px;
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
        width: 96px;
        height: 96px;
        border-radius: 50%;
        background-color: #0f172a;
    }
    .progress-value {
        position: relative;
        font-size: 1.8rem;
        font-weight: bold;
        color: #f8fafc;
    }
    
    /* Estilo Sello Circular con Banda Central (Inspirado en sellos oficiales) */
    .rubber-stamp {
        position: relative;
        width: 155px;
        height: 155px;
        border: 3px dashed var(--stamp-color);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--stamp-color);
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        transform: rotate(-8deg);
        background: rgba(0, 0, 0, 0.15);
        opacity: 0.95;
        animation: stampEffect 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stamp-border {
        position: relative;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
    }
    .stamp-top-text, .stamp-bottom-text {
        font-size: 0.5rem;
        letter-spacing: 1.5px;
        font-weight: bold;
        text-align: center;
        opacity: 0.85;
    }
    .stamp-banner {
        position: absolute;
        top: 50%;
        left: -14px;
        right: -14px;
        transform: translateY(-50%);
        background: #0f172a;
        border: 3px solid var(--stamp-color);
        padding: 4px 0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .stamp-grade-text {
        font-size: 2.2rem;
        font-weight: 900;
        line-height: 1;
        letter-spacing: 3
