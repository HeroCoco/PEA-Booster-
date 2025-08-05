
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objs as go

st.set_page_config(page_title="PEA Booster", layout="centered")
st.title("📈 PEA Booster – Analyse d'actions")

ticker = st.text_input("Entrez un ticker (ex: AAPL, AIR.PA)", "AAPL").upper()
years = st.slider("Années d'historique à afficher", 1, 5, 2)
future_years = st.slider("Projection EPS (années)", 1, 5, 2)

if ticker:
    data = yf.Ticker(ticker)
    hist = data.history(period=f"{years}y")
    info = data.info

    hist["SMA50"] = hist["Close"].rolling(50).mean()
    hist["SMA200"] = hist["Close"].rolling(200).mean()
    hist["RSI"] = ta.rsi(hist["Close"], length=14)

    st.subheader("📊 Cours de l'action")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Clôture"))
    fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA50"], name="SMA 50"))
    fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA200"], name="SMA 200"))
    fig.update_layout(xaxis_title="Date", yaxis_title="Prix")
    st.plotly_chart(fig)

    st.subheader("📉 Indicateurs fondamentaux")
    eps = info.get("trailingEps", None)
    per = info.get("trailingPE", None)
    roe = info.get("returnOnEquity", None)
    growth = info.get("earningsQuarterlyGrowth", 0)

    eps_future = None
    if eps and growth:
        eps_future = eps * (1 + growth) ** future_years

    st.write(f"• **EPS actuel** : {eps}")
    st.write(f"• **PER** : {per}")
    st.write(f"• **ROE** : {roe}")
    if eps_future:
        st.write(f"• **EPS projeté ({future_years} ans)** : {eps_future:.2f}")

    st.subheader("📌 Diagnostic")
    score = 0
    if per and per < 20: score += 1
    if "RSI" in hist.columns and 30 < hist["RSI"].iloc[-1] < 70: score += 1
    if hist["Close"].iloc[-1] > hist["SMA50"].iloc[-1]: score += 1
    if hist["Close"].iloc[-1] > hist["SMA200"].iloc[-1]: score += 1
    if growth and growth > 0: score += 1

    result = {
        5: "👍 Opportunité (fort potentiel)",
        3: "🟡 Juste prix (valeur raisonnable)",
        0: "⚠️ Risqué (prudence)"
    }.get(score, "🟡 Juste prix")

    st.write(f"**Score :** {score}/5")
    st.success(result)
