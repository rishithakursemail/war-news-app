
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="War & Oil Sentinel", layout="wide", page_icon="⚡")

# ऑटो-रिफ्रेश: हर 5 मिनट (5 * 60 * 1000 ms) में ऐप अपने आप रिफ्रेश होगी
st_autorefresh(interval=5 * 60 * 1000, key="news_auto_refresh")

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1a1c2c, #0a0b10); color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; font-size: 2.8rem; background: linear-gradient(90deg, #ff4b2b, #ff416c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom:0; }
    .oil-card { background: rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }
    .news-box { background: rgba(30, 31, 48, 0.8); border-radius: 15px; padding: 20px; margin-bottom: 20px; border-left: 5px solid #ff416c; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .price-up { color: #00ff88; text-shadow: 0 0 10px #00ff88; font-weight: bold; font-size: 1.5rem; }
    .price-down { color: #ff3333; text-shadow: 0 0 10px #ff3333; font-weight: bold; font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- CACHED OIL DATA (10 MINS) ---
@st.cache_data(ttl=600)
def get_oil_price_cached(type="wti"):
    url = f"https://www.alphavantage.co/query?function={type.upper()}&interval=daily&apikey={OIL_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "data" in data and len(data["data"]) > 1:
            v_today = float(data["data"][0]["value"])
            v_yesterday = float(data["data"][1]["value"])
            return {"price": round(v_today, 2), "change": round(v_today - v_yesterday, 2)}
    except: return None
    return None

# --- LIVE NEWS DATA (EVERY REFRESH) ---
def fetch_news_live():
    # युद्ध और क्रूड ऑयल से संबंधित ताजा खबरें
    url = f"https://newsapi.org/v2/everything?q=(Iran AND USA AND War) OR (Hormuz Strait) OR (Crude Oil)&sortBy=publishedAt&language=hi&apiKey={NEWS_API_KEY}"
    try:
        return requests.get(url).json().get("articles", [])[:10]
    except: return []

# --- UI CONTENT ---
st.markdown("<h1 class='main-title'>WAR & OIL SENTINEL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>ऑटो-रिफ्रेश मोड: न्यूज़ (5 Min) | क्रूड (10 Min)</p>", unsafe_allow_html=True)

# Oil Row
st.markdown("### 🛢️ ग्लोबल ऑयल टिकर")
c1, c2 = st.columns(2)

wti = get_oil_price_cached("wti")
with c1:
    if wti:
        cl = "price-up" if wti['change'] >= 0 else "price-down"
        st.markdown(f'<div class="oil-card"><p style="color:#aaa;">WTI CRUDE</p><h2>${wti["price"]}</h2><p class="{cl}">{"▲" if wti["change"]>=0 else "▼"} {abs(wti["change"])} USD</p></div>', unsafe_allow_html=True)

time.sleep(1) # API Safety Delay

brent = get_oil_price_cached("brent")
with c2:
    if brent:
        cl = "price-up" if brent['change'] >= 0 else "price-down"
        st.markdown(f'<div class="oil-card"><p style="color:#aaa;">BRENT CRUDE</p><h2>${brent["price"]}</h2><p class="{cl}">{"▲" if brent["change"]>=0 else "▼"} {abs(brent["change"])} USD</p></div>', unsafe_allow_html=True)

st.markdown("---")

# News Feed
st.markdown("### 📰 लाइव न्यूज़ एवं वॉर अपडेट")
news = fetch_news_live()

if news:
    for art in news:
        st.markdown(f"""
        <div class="news-box">
            <h4 style="margin:0; color:#fff;">{art['title']}</h4>
            <p style="font-size:0.85rem; color:#ff416c; font-weight:bold;">{art['source']['name']} • {art['publishedAt'][11:16]} IST</p>
            <p style="font-size:0.95rem; color:#ccc;">{art['description'][:250] if art['description'] else 'विवरण के लिए लिंक पर क्लिक करें...'}</p>
            <a href="{art['url']}" target="_blank" style="color:#00ff88; text-decoration:none; font-weight:bold;">पूरा लेख पढ़ें ↗</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("नई खबरें लोड हो रही हैं...")

# Sidebar
with st.sidebar:
    st.title("सेंट्रलाइज्ड कंट्रोल")
    st.write(f"अगला ऑटो-रिफ्रेश: **5 मिनट में**")
    if st.button("Force Refresh (अभी अपडेट करें)"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.info(f"Last Synced: {datetime.now().strftime('%H:%M:%S')}")
