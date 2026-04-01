import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="Professional War & Oil Monitor", layout="wide", page_icon="📈")

# ऑटो-रिफ्रेश: हर 5 मिनट
st_autorefresh(interval=5 * 60 * 1000, key="pro_refresh")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background: #0a0b10; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; text-align: center; color: #ff4b4b; margin-bottom: 25px; letter-spacing: 1px; }
    .oil-card { background: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; text-align: center; }
    .news-card { background: #1c2128; border-radius: 10px; padding: 15px; margin-bottom: 12px; border-left: 4px solid #30363d; transition: 0.2s; }
    .news-card:hover { border-left-color: #00d2ff; background: #21262d; }
    .global-header { color: #3a7bd5; border-bottom: 2px solid #3a7bd5; font-family: 'Orbitron', sans-serif; padding-bottom: 5px; }
    .indian-header { color: #ff9933; border-bottom: 2px solid #ff9933; font-family: 'Orbitron', sans-serif; padding-bottom: 5px; }
    .peace-alert { border-left-color: #00ff88 !important; background: rgba(0, 255, 136, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- CORE FUNCTIONS ---

@st.cache_data(ttl=600)
def get_oil_data(symbol="WTI"):
    time.sleep(1.5) # API Rate Limit protection
    url = f"https://www.alphavantage.co/query?function={symbol}&interval=daily&apikey={OIL_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "data" in data and len(data["data"]) > 0:
            val = float(data["data"][0]["value"])
            chg = val - float(data["data"][1]["value"])
            return {"price": round(val, 2), "change": round(chg, 2)}
        return "LIMIT"
    except: return None

def fetch_clean_news(lang="en"):
    # अधिक गंभीर सर्च क्वेरी
    query = "(Iran AND USA AND diplomacy) OR (Persian Gulf security) OR (Crude oil analysis) OR (Peace treaty)"
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language={lang}&apiKey={NEWS_API_KEY}"
    
    # Clickbait और सनसनीखेज शब्दों की लिस्ट
    blacklisted_words = ["धड़ाम", "हड़कंप", "खलबली", "बड़ी चेतावनी", "होश उड़", "धमाका", "सबक", "shocking", "crash", "destroyed"]
    
    try:
        articles = requests.get(url).json().get("articles", [])
        cleaned = []
        for art in articles:
            title = art.get('title', '').lower()
            # फ़िल्टर: अगर टाइटल में ब्लैकलिस्ट शब्द न हो और टाइटल 35 अक्षर से बड़ा हो
            if not any(word in title for word in blacklisted_words) and len(title) > 35:
                cleaned.append(art)
        return cleaned[:6]
    except: return []

# --- UI DISPLAY ---
st.markdown("<h1 class='main-title'>STRATEGIC MARKET SENTINEL</h1>", unsafe_allow_html=True)

# Oil Prices Row
c1, c2 = st.columns(2)
with c1:
    wti = get_oil_data("WTI")
    if wti == "LIMIT": st.info("WTI API Limit reached")
    elif wti:
        color = "#00ff88" if wti['change'] >= 0 else "#ff3333"
        st.markdown(f'<div class="oil-card">WTI Crude: <b style="font-size:1.4rem;">${wti["price"]}</b> <br> <span style="color:{color}">{"▲" if wti["change"]>=0 else "▼"} {abs(wti["change"])}</span></div>', unsafe_allow_html=True)

with c2:
    brent = get_oil_data("BRENT")
    if brent == "LIMIT": st.info("Brent API Limit reached")
    elif brent:
        color = "#00ff88" if brent['change'] >= 0 else "#ff3333"
        st.markdown(f'<div class="oil-card">Brent Crude: <b style="font-size:1.4rem;">${brent["price"]}</b> <br> <span style="color:{color}">{"▲" if brent["change"]>=0 else "▼"} {abs(brent["change"])}</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Side-by-Side News
col_g, col_i = st.columns(2)

with col_g:
    st.markdown("<h3 class='global-header'>🌍 GLOBAL STRATEGIC NEWS</h3>", unsafe_allow_html=True)
    g_news = fetch_clean_news("en")
    for art in g_news:
        is_peace = any(w in art['title'].lower() for w in ["peace", "ceasefire", "treaty", "diplomacy"])
        st.markdown(f"""
        <div class="news-card {'peace-alert' if is_peace else ''}">
            <p style="font-size:0.7rem; color:#3a7bd5; margin:0; font-weight:bold;">{art['source']['name']} • {art['publishedAt'][11:16]} IST</p>
            <h5 style="margin:5px 0;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem;">Read Analysis ↗</a>
        </div>
        """, unsafe_allow_html=True)

with col_i:
    st.markdown("<h3 class='indian-header'>🇮🇳 INDIAN MEDIA UPDATES</h3>", unsafe_allow_html=True)
    h_news = fetch_clean_news("hi")
    for art in h_news:
        is_peace = any(w in art['title'] for w in ["शान्ति", "समझौता", "युद्धविराम", "राहत"])
        st.markdown(f"""
        <div class="news-card {'peace-alert' if is_peace else ''}">
            <p style="font-size:0.7rem; color:#ff9933; margin:0; font-weight:bold;">{art['source']['name']} • {art['publishedAt'][11:16]} IST</p>
            <h5 style="margin:5px 0;">{art['title']}</h5>
            <a href="{art['url']}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:0.8rem;">पूरा पढ़ें ↗</a>
        </div>
        """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ System Control")
    st.markdown(f"Status: **Monitoring Live**")
    st.markdown(f"Last Update: **{datetime.now().strftime('%H:%M:%S')}**")
    if st.button("Force Clear Cache & Sync"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption("Filtering active: Exaggerated headlines are hidden.")
