import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="Global vs Indian Sentinel", layout="wide", page_icon="🌎")

# ऑटो-रिफ्रेश: हर 5 मिनट
st_autorefresh(interval=5 * 60 * 1000, key="split_refresh")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background: #0a0b10; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; text-align: center; color: #ff4b4b; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }
    .oil-card { background: #161b22; border-radius: 15px; padding: 15px; border: 1px solid #30363d; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .news-card { background: #161b22; border-radius: 10px; padding: 15px; margin-bottom: 12px; border-left: 4px solid #30363d; transition: 0.3s; }
    .news-card:hover { transform: scale(1.02); background: #1c2128; }
    .global-header { color: #3a7bd5; border-bottom: 2px solid #3a7bd5; padding-bottom: 5px; margin-bottom: 15px; font-family: 'Orbitron', sans-serif; font-size: 1.2rem; }
    .indian-header { color: #ff9933; border-bottom: 2px solid #ff9933; padding-bottom: 5px; margin-bottom: 15px; font-family: 'Orbitron', sans-serif; font-size: 1.2rem; }
    .peace-alert { border-left-color: #00ff88 !important; background: rgba(0, 255, 136, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FETCHING ---

@st.cache_data(ttl=600)
def get_oil_data(symbol="WTI"):
    # API को थोड़ा समय देने के लिए (Rate Limit Fix)
    time.sleep(2) 
    url = f"https://www.alphavantage.co/query?function={symbol}&interval=daily&apikey={OIL_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "data" in data and len(data["data"]) > 0:
            val = float(data["data"][0]["value"])
            chg = val - float(data["data"][1]["value"])
            return {"price": round(val, 2), "change": round(chg, 2)}
        else:
            # अगर 'data' की जगह 'Information' आए तो मतलब लिमिट खत्म
            return "LIMIT"
    except: return None

def fetch_news(lang="en"):
    query = "(Iran AND USA AND (War OR Peace OR Ceasefire OR Diplomacy)) OR (Crude Oil Brent WTI)"
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language={lang}&apiKey={NEWS_API_KEY}"
    try:
        return requests.get(url).json().get("articles", [])[:6]
    except: return []

# --- UI CONTENT ---
st.markdown("<h1 class='main-title'>WAR & PEACE MONITOR</h1>", unsafe_allow_html=True)

# Oil Ticker Row
oc1, oc2 = st.columns(2)

# WTI Fetch
wti = get_oil_data("WTI")
with oc1:
    if wti == "LIMIT":
        st.info("WTI: API की दैनिक सीमा समाप्त (कल सुबह अपडेट होगा)")
    elif wti:
        st.markdown(f'<div class="oil-card">🛢️ WTI Crude: <b style="font-size:1.5rem;">${wti["price"]}</b> <br> <span style="color:{"#00ff88" if wti["change"]>=0 else "#ff3333"}">{"▲" if wti["change"]>=0 else "▼"} {abs(wti["change"])} USD</span></div>', unsafe_allow_html=True)
    else:
        st.warning("WTI डेटा लोड हो रहा है...")

# Brent Fetch
brent = get_oil_data("BRENT")
with oc2:
    if brent == "LIMIT":
        st.info("Brent: API की दैनिक सीमा समाप्त")
    elif brent:
        st.markdown(f'<div class="oil-card">🛢️ Brent Crude: <b style="font-size:1.5rem;">${brent["price"]}</b> <br> <span style="color:{"#00ff88" if brent["change"]>=0 else "#ff3333"}">{"▲" if brent["change"]>=0 else "▼"} {abs(brent["change"])} USD</span></div>', unsafe_allow_html=True)
    else:
        st.warning("Brent डेटा लोड हो रहा है...")

st.markdown("<br>", unsafe_allow_html=True)

# News Side-by-Side
col_global, col_indian = st.columns(2)

with col_global:
    st.markdown("<h3 class='global-header'>🌍 GLOBAL MEDIA (English)</h3>", unsafe_allow_html=True)
    g_news = fetch_news("en")
    for art in g_news:
        is_peace = any(w in art['title'].lower() for w in ["peace", "ceasefire", "deal", "treaty", "diplomacy"])
        st.markdown(f"""
        <div class="news-card {'peace-alert' if is_peace else ''}">
            <p style="font-size:0.75rem; color:#3a7bd5; margin:0; font-weight:bold;">{art['source']['name']} • {art['publishedAt'][11:16]} IST</p>
            <h5 style="margin:5px 0; line-height:1.4;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem; font-weight:bold;">Read More ↗</a>
        </div>
        """, unsafe_allow_html=True)

with col_indian:
    st.markdown("<h3 class='indian-header'>🇮🇳 INDIAN MEDIA (Hindi)</h3>", unsafe_allow_html=True)
    h_news = fetch_news("hi")
    for art in h_news:
        is_peace = any(w in art['title'] for w in ["शान्ति", "समझौता", "युद्धविराम", "राहत", "डिप्लोमेसी"])
        st.markdown(f"""
        <div class="news-card {'peace-alert' if is_peace else ''}">
            <p style="font-size:0.75rem; color:#ff9933; margin:0; font-weight:bold;">{art['source']['name']} • {art['publishedAt'][11:16]} IST</p>
            <h5 style="margin:5px 0; line-height:1.4;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem; font-weight:bold;">पूरा पढ़ें ↗</a>
        </div>
        """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ Sentinel Status")
    st.markdown("---")
    st.write(f"Last Sync: **{datetime.now().strftime('%H:%M:%S')}**")
    if st.button("Force Refresh (Force Update)"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption("नोट: क्रूड डेटा API की दैनिक सीमा (500 रिक्वेस्ट) के अधीन है।")
