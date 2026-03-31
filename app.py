import streamlit as st
import requests
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION ---
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="War, Peace & Oil Sentinel", layout="wide", page_icon="🕊️")

# ऑटो-रिफ्रेश: हर 5 मिनट (300,000ms) में पूरी ऐप रीलोड होगी
st_autorefresh(interval=5 * 60 * 1000, key="global_refresh")

# --- PREMIUM CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background: radial-gradient(circle at top right, #1a1c2c, #0a0b10); color: #e0e0e0; font-family: 'Inter', sans-serif; }
    
    .main-title { 
        font-family: 'Orbitron', sans-serif; font-size: 2.8rem; font-weight: 700;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5, #ff4b2b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 5px;
    }

    .oil-card { 
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 25px; text-align: center;
        border: 1px solid rgba(255,255,255,0.1); transition: 0.3s;
    }
    .oil-card:hover { border-color: #00d2ff; transform: translateY(-5px); }

    .news-box { 
        background: rgba(30, 31, 48, 0.8); border-radius: 15px; padding: 20px;
        margin-bottom: 20px; border-left: 5px solid #00d2ff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .price-text { font-size: 2rem; font-weight: bold; margin: 5px 0; }
    .status-up { color: #00ff88; text-shadow: 0 0 10px #00ff88; }
    .status-down { color: #ff3333; text-shadow: 0 0 10px #ff3333; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FETCHING LOGIC ---

@st.cache_data(ttl=600) # ऑयल डेटा 10 मिनट के लिए कैशे में रहेगा
def get_oil_data(type="WTI"):
    url = f"https://www.alphavantage.co/query?function={type}&interval=daily&apikey={OIL_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "data" in data and len(data["data"]) > 1:
            today_val = float(data["data"][0]["value"])
            yesterday_val = float(data["data"][1]["value"])
            return {"price": round(today_val, 2), "change": round(today_val - yesterday_val, 2)}
    except: return None
    return None

def fetch_war_and_peace_news():
    # कीवर्ड्स में 'Peace', 'Ceasefire' और ' समझौता' जोड़ा गया है
    query = "(Iran AND USA) OR (Hormuz Strait) OR (Iran War Peace) OR (Crude Oil Price News) OR (युद्धविराम)"
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=hi&apiKey={NEWS_API_KEY}"
    try:
        articles = requests.get(url).json().get("articles", [])
        return articles[:10] # टॉप 10 खबरें
    except: return []

# --- UI LAYOUT ---
st.markdown("<h1 class='main-title'>WAR, PEACE & OIL SENTINEL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>ईरान-अमेरिका संघर्ष, शान्ति समझौता एवं ऑयल मार्केट लाइव</p>", unsafe_allow_html=True)

# Oil Section
st.markdown("### 🛢️ ग्लोबल ऑयल टिकर (10 Min Update)")
c1, c2 = st.columns(2)

wti = get_oil_data("WTI")
with c1:
    if wti:
        style = "status-up" if wti['change'] >= 0 else "status-down"
        st.markdown(f"""
        <div class="oil-card">
            <p style='color:#aaa;'>WTI CRUDE</p>
            <p class="price-text">${wti['price']}</p>
            <p class="{style}">{"▲" if wti['change'] >= 0 else "▼"} {abs(wti['change'])} USD</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("WTI डेटा उपलब्ध नहीं है (API Limit)")

time.sleep(1) # API Rate Limit से बचाव

brent = get_oil_data("BRENT")
with c2:
    if brent:
        style = "status-up" if brent['change'] >= 0 else "status-down"
        st.markdown(f"""
        <div class="oil-card">
            <p style='color:#aaa;'>BRENT CRUDE</p>
            <p class="price-text">${brent['price']}</p>
            <p class="{style}">{"▲" if brent['change'] >= 0 else "▼"} {abs(brent['change'])} USD</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Brent डेटा उपलब्ध नहीं है (API Limit)")

st.markdown("---")

# News Section
st.markdown("### 📰 लाइव अपडेट: युद्ध, शान्ति और कूटनीति (5 Min Update)")
news_list = fetch_war_and_peace_news()

if news_list:
    for art in news_list:
        # अगर खबर में 'शान्ति' या 'समझौता' जैसे शब्द हैं, तो उसे हाइलाइट करें
        border_color = "#00ff88" if any(word in art['title'] for word in ["शान्ति", "समझौता", "Peace", "Ceasefire"]) else "#ff4b4b"
        
        st.markdown(f"""
        <div class="news-box" style="border-left-color: {border_color};">
            <h4 style='margin:0; color:#fff;'>{art['title']}</h4>
            <p style='color:#00d2ff; font-size:0.85rem; font-weight:bold;'>{art['source']['name']} • {art['publishedAt'][11:16]} IST</p>
            <p style='font-size:0.95rem; color:#ccc;'>{art['description'][:250] if art['description'] else 'विवरण के लिए लिंक पर क्लिक करें...'}</p>
            <a href="{art['url']}" target="_blank" style='color:#00ff88; text-decoration:none; font-weight:bold;'>पूरा लेख पढ़ें ↗</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("खबरें लोड नहीं हो पाईं। कृपया रिफ्रेश करें।")

# Sidebar
with st.sidebar:
    st.title("कंट्रोल सेंटर")
    st.write("न्यूज़ रिफ्रेश: **हर 5 मिनट**")
    st.write("ऑयल रिफ्रेश: **हर 10 मिनट**")
    if st.button("Force Refresh (अभी अपडेट करें)"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.info(f"Last Synced: {datetime.now().strftime('%H:%M:%S')}")
