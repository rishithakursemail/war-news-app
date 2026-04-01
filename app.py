import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
# अपनी API Keys यहाँ बदलें
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="Strategic News & Oil Sentinel", layout="wide", page_icon="📡")

# ऑटो-रिफ्रेश: हर 5 मिनट
st_autorefresh(interval=5 * 60 * 1000, key="final_refresh")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: #0e1117; color: #ffffff; }
    .main-title { text-align: center; color: #ff4b4b; font-family: 'serif'; border-bottom: 2px solid #ff4b4b; padding-bottom: 10px; }
    .oil-card { background: #1a1c24; border-radius: 10px; padding: 15px; border: 1px solid #3e4451; text-align: center; }
    .news-card { background: #1a1c24; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    .source-tag { color: #00d2ff; font-weight: bold; font-size: 0.8rem; }
    .emergency-alert { background: #4a0e0e; border: 1px solid #ff0000; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; animation: blinker 2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.6; } }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---

@st.cache_data(ttl=600)
def get_oil_data(symbol="WTI"):
    time.sleep(2) # Rate limit protection
    url = f"https://www.alphavantage.co/query?function={symbol}&interval=daily&apikey={OIL_API_KEY}"
    try:
        data = requests.get(url).json()
        if "data" in data:
            val = float(data["data"][0]["value"])
            chg = val - float(data["data"][1]["value"])
            return {"price": val, "change": round(chg, 2)}
        return "LIMIT"
    except: return None

def fetch_trusted_news(lang="en", category="Global"):
    # विश्वसनीय स्रोतों की सूची (ANI, PTI, BBC, CNN, Reuters, Moneycontrol)
    sources = "bbc-news,reuters,cnn,the-hindu,the-times-of-india,google-news-in"
    
    # अधिक सटीक सर्च टर्म्स (अखबार की कटिंग के आधार पर)
    query = "(Iran attack Google Apple) OR (Strait of Hormuz news) OR (Iran US War Crisis)"
    
    if lang == "hi":
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=hi&apiKey={NEWS_API_KEY}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?q=Iran&sources={sources if category=='Global' else ''}&apiKey={NEWS_API_KEY}"
        if category != "Global":
             url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"

    try:
        articles = requests.get(url).json().get("articles", [])
        return articles[:7]
    except: return []

# --- DISPLAY ---
st.markdown("<h1 class='main-title'>STRATEGIC MARKET MONITOR</h1>", unsafe_allow_html=True)

# इमरजेंसी अलर्ट सेक्शन (अगर कोई बहुत बड़ी खबर हो)
st.markdown("<div class='emergency-alert'>⚠️ LIVE: ईरान-अमेरिका संघर्ष और तेल आपूर्ति पर पैनी नज़र</div>", unsafe_allow_html=True)

# Oil Prices
c1, c2 = st.columns(2)
with c1:
    wti = get_oil_data("WTI")
    if wti == "LIMIT": st.error("Oil API Limit Reached")
    elif wti:
        st.markdown(f'<div class="oil-card">WTI Crude: <b>${wti["price"]}</b> <br> <span style="color:{"#00ff88" if wti["change"]>=0 else "#ff4b4b"}">{"▲" if wti["change"]>=0 else "▼"} {abs(wti["change"])} USD</span></div>', unsafe_allow_html=True)

with c2:
    brent = get_oil_data("BRENT")
    if brent == "LIMIT": st.error("Oil API Limit Reached")
    elif brent:
        st.markdown(f'<div class="oil-card">Brent Crude: <b>${brent["price"]}</b> <br> <span style="color:{"#00ff88" if brent["change"]>=0 else "#ff4b4b"}">{"▲" if brent["change"]>=0 else "▼"} {abs(brent["change"])} USD</span></div>', unsafe_allow_html=True)

st.divider()

# News Side-by-Side
col_world, col_india = st.columns(2)

with col_world:
    st.markdown("### 🌎 BBC, CNN & GLOBAL FEED")
    g_news = fetch_trusted_news(lang="en", category="Global")
    for art in g_news:
        st.markdown(f"""
        <div class="news-card">
            <span class="source-tag">{art['source']['name']}</span>
            <h5 style="margin:5px 0;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem;">Read More ↗</a>
        </div>
        """, unsafe_allow_html=True)

with col_india:
    st.markdown("### 🇮🇳 ANI, PTI & HINDI FEED")
    h_news = fetch_trusted_news(lang="hi")
    for art in h_news:
        st.markdown(f"""
        <div class="news-card" style="border-left-color: #ff9933;">
            <span class="source-tag">{art['source']['name']}</span>
            <h5 style="margin:5px 0;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem;">खबर पढ़ें ↗</a>
        </div>
        """, unsafe_allow_html=True)

with st.sidebar:
    st.title("System Status")
    st.info(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("Force Refresh All Data"):
        st.cache_data.clear()
        st.rerun()
