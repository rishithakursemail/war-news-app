import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="War & Oil Sentinel", layout="wide", page_icon="⚡")

# ऑटो-रिफ्रेश: हर 5 मिनट (300,000ms) में ऐप रीलोड होगी
st_autorefresh(interval=5 * 60 * 1000, key="global_refresh")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background: #0e1117; color: white; }
    .oil-card { background: #1e2130; border-radius: 15px; padding: 20px; border: 1px solid #333; text-align: center; }
    .news-box { background: #262730; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 5px solid #ff4b4b; }
    .price { font-size: 2rem; font-weight: bold; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC WITH CACHING ---

@st.cache_data(ttl=600) # ऑयल डेटा 10 मिनट के लिए स्टोर रहेगा
def get_oil_data(type="WTI"):
    # Commodities API का उपयोग जो अधिक स्थिर है
    url = f"https://www.alphavantage.co/query?function={type}&interval=daily&apikey={OIL_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "data" in data and len(data["data"]) > 0:
            price = float(data["data"][0]["value"])
            prev = float(data["data"][1]["value"])
            return {"price": round(price, 2), "change": round(price - prev, 2)}
    except: return None
    return None

def fetch_news():
    url = f"https://newsapi.org/v2/everything?q=(Iran AND USA AND War) OR (Hormuz Strait) OR (Crude Oil)&sortBy=publishedAt&language=hi&apiKey={NEWS_API_KEY}"
    try:
        return requests.get(url).json().get("articles", [])[:8]
    except: return []

# --- UI CONTENT ---
st.markdown("<h1 style='text-align:center; color:#ff4b4b;'>WAR & OIL SENTINEL</h1>", unsafe_allow_html=True)

# Oil Prices
st.markdown("### 🛢️ ग्लोबल ऑयल टिकर (10 Min Update)")
c1, c2 = st.columns(2)

with c1:
    wti = get_oil_data("WTI")
    if wti:
        st.markdown(f'<div class="oil-card"><p>WTI CRUDE</p><p class="price">${wti["price"]}</p><p>{"▲" if wti["change"]>=0 else "▼"} {abs(wti["change"])} USD</p></div>', unsafe_allow_html=True)
    else:
        st.error("WTI डेटा फिलहाल उपलब्ध नहीं है।")

time.sleep(1) # API Rate limit protection

with c2:
    brent = get_oil_data("BRENT")
    if brent:
        st.markdown(f'<div class="oil-card"><p>BRENT CRUDE</p><p class="price">${brent["price"]}</p><p>{"▲" if brent["change"]>=0 else "▼"} {abs(brent["change"])} USD</p></div>', unsafe_allow_html=True)
    else:
        st.error("Brent डेटा फिलहाल उपलब्ध नहीं है।")

st.markdown("---")

# News Section
st.markdown("### 📰 लाइव न्यूज़ अपडेट (5 Min Update)")
news = fetch_news()
for art in news:
    st.markdown(f"""
    <div class="news-box">
        <h4 style='margin:0;'>{art['title']}</h4>
        <p style='color:#ff4b4b; font-size:0.8rem;'>{art['source']['name']} • {art['publishedAt'][11:16]} IST</p>
        <p>{art['description'][:200] if art['description'] else ''}</p>
        <a href="{art['url']}" target="_blank" style='color:#00ff88;'>पूरा पढ़ें ↗</a>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("सेंट्रलाइज्ड कंट्रोल")
    if st.button("Force Refresh (अभी अपडेट करें)"):
        st.cache_data.clear()
        st.rerun()
    st.info(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")
