import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
NEWS_API_KEY = "d794da4aaff244d29f314e9728b4aed0" #"be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "0UVKFY63ZM2ZWTSK"   #"WEJSMD3L9T43WZOB"

st.set_page_config(page_title="War & Oil Sentinel Pro", layout="wide", page_icon="📡")

# ऑटो-रिफ्रेश: हर 5 मिनट (300,000ms)
st_autorefresh(interval=5 * 60 * 1000, key="sentinel_refresh")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #0a0b10; color: #ffffff; }
    .main-title { text-align: center; color: #ff4b4b; font-family: 'serif'; font-size: 2.2rem; margin-bottom: 20px; }
    .oil-card { background: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; text-align: center; }
    .news-card { background: #161b22; border-radius: 8px; padding: 15px; margin-bottom: 15px; border-left: 5px solid #ff4b4b; min-height: 120px; }
    .source-tag { color: #00d2ff; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; }
    .emergency-banner { background: #4a0e0e; border: 1px solid #ff0000; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FUNCTIONS ---

@st.cache_data(ttl=600)
def get_oil_data(symbol="WTI"):
    # API Rate Limit से बचने के लिए छोटा गैप
    time.sleep(2) 
    url = f"https://www.alphavantage.co/query?function={symbol}&interval=daily&apikey={OIL_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "data" in data and len(data["data"]) > 0:
            val = float(data["data"][0]["value"])
            prev = float(data["data"][1]["value"])
            return {"price": val, "change": round(val - prev, 2)}
        return "LIMIT"
    except: return None

def fetch_verified_news(lang="en"):
    # विश्वसनीय स्रोतों और सटीक कीवर्ड्स का मिश्रण (अखबार की कटिंग के आधार पर)
    # हम 'Everything' API का उपयोग करेंगे ताकि गहराई से न्यूज़ मिले
    keywords = "(Iran AND (attack OR USA OR strike OR war)) OR (Crude Oil price) OR (Strait of Hormuz)"
    
    # सोर्सेज की लिस्ट (BBC, CNN, Reuters, ANI, PTI प्रभाव वाले भारतीय न्यूज़)
    url = f"https://newsapi.org/v2/everything?q={keywords}&language={lang}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url).json()
        articles = response.get("articles", [])
        # केवल वे खबरें जो बहुत छोटी नहीं हैं (ताकि Clickbaits कम हों)
        return [a for a in articles if len(a.get('title', '')) > 40][:6]
    except: return []

# --- DASHBOARD UI ---

st.markdown("<h1 class='main-title'>STRATEGIC MARKET SENTINEL</h1>", unsafe_allow_html=True)

# इमरजेंसी हेडलाइन (Static Alert)
st.markdown("<div class='emergency-banner'>⚠️ LIVE UPDATE: मिडिल ईस्ट तनाव और वैश्विक तेल आपूर्ति पर निगरानी जारी</div>", unsafe_allow_html=True)

# Oil Prices
c1, c2 = st.columns(2)
with c1:
    wti = get_oil_data("WTI")
    if wti == "LIMIT": st.error("Oil API Limit Reached")
    elif wti:
        color = "#00ff88" if wti['change'] >= 0 else "#ff4b4b"
        st.markdown(f'<div class="oil-card">WTI Crude Price<br><b style="font-size:1.8rem;">${wti["price"]}</b><br><span style="color:{color}">{"▲" if wti["change"]>=0 else "▼"} {abs(wti["change"])} USD</span></div>', unsafe_allow_html=True)

with c2:
    brent = get_oil_data("BRENT")
    if brent == "LIMIT": st.error("Oil API Limit Reached")
    elif brent:
        color = "#00ff88" if brent['change'] >= 0 else "#ff4b4b"
        st.markdown(f'<div class="oil-card">Brent Crude Price<br><b style="font-size:1.8rem;">${brent["price"]}</b><br><span style="color:{color}">{"▲" if brent["change"]>=0 else "▼"} {abs(brent["change"])} USD</span></div>', unsafe_allow_html=True)

st.divider()

# News Columns
col_g, col_i = st.columns(2)

with col_g:
    st.markdown("### 🌎 GLOBAL: BBC, CNN, REUTERS")
    g_news = fetch_verified_news(lang="en")
    if not g_news: st.info("न्यूज़ लोड हो रही है या API लिमिट खत्म हो गई है।")
    for art in g_news:
        st.markdown(f"""
        <div class="news-card">
            <span class="source-tag">{art['source']['name']}</span>
            <h5 style="margin:5px 0;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem; font-weight:bold;">READ FULL ANALYSIS ↗</a>
        </div>
        """, unsafe_allow_html=True)

with col_i:
    st.markdown("### 🇮🇳 INDIA: ANI, PTI, HINDI FEED")
    h_news = fetch_verified_news(lang="hi")
    if not h_news: st.info("भारतीय न्यूज़ फीड वर्तमान में अनुपलब्ध है।")
    for art in h_news:
        st.markdown(f"""
        <div class="news-card" style="border-left-color: #ff9933;">
            <span class="source-tag">{art['source']['name']}</span>
            <h5 style="margin:5px 0;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem; font-weight:bold;">पूरी खबर पढ़ें ↗</a>
        </div>
        """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ Control Panel")
    st.write(f"Last Sync: **{datetime.now().strftime('%H:%M:%S')}**")
    if st.button("Manual Force Refresh"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption("नोट: डेटा हर 5 मिनट में अपने आप अपडेट होता है।")
