import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION ---
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="War & Oil Sentinel", layout="wide", page_icon="⚡")

# --- ADVANCED CSS FOR PREMIUM LOOK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #1a1c2c, #0a0b10);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff4b2b, #ff416c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }

    .oil-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .oil-card:hover {
        transform: translateY(-5px);
        border-color: #ff4b2b;
    }

    .news-box {
        background: rgba(30, 31, 48, 0.7);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #ff416c;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .price-up { color: #00ff88; text-shadow: 0 0 10px #00ff88; font-weight: bold; font-size: 1.5rem; }
    .price-down { color: #ff3333; text-shadow: 0 0 10px #ff3333; font-weight: bold; font-size: 1.5rem; }
    
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ---
def get_oil_price(type="wti"):
    url = f"https://www.alphavantage.co/query?function={type.upper()}&interval=daily&apikey={OIL_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "data" in data and len(data["data"]) > 1:
            val_today = float(data["data"][0]["value"])
            val_yesterday = float(data["data"][1]["value"])
            # दशमलव के बाद केवल 2 अंक रखने के लिए round() का उपयोग
            change = round(val_today - val_yesterday, 2)
            return {"price": round(val_today, 2), "change": change}
    except: return None
    return None

def fetch_war_news():
    url = f"https://newsapi.org/v2/everything?q=(Iran AND USA AND War) OR (Hormuz Strait) OR (Crude Oil)&sortBy=publishedAt&language=hi&apiKey={NEWS_API_KEY}"
    try:
        return requests.get(url).json().get("articles", [])[:10]
    except: return []

# --- UI CONTENT ---
st.markdown("<h1 class='main-title'>WAR & OIL SENTINEL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>ईरान-अमेरिका संघर्ष एवं वैश्विक ऊर्जा बाजार की लाइव ट्रैकिंग</p>", unsafe_allow_html=True)

# Oil Prices Row
st.markdown("### 🛢️ लाइव क्रूड ऑयल टिकर")
c1, c2 = st.columns(2)

wti = get_oil_price("wti")
with c1:
    if wti:
        color_class = "price-up" if wti['change'] >= 0 else "price-down"
        arrow = "▲" if wti['change'] >= 0 else "▼"
        st.markdown(f"""
        <div class="oil-card">
            <p style='color:#aaa; font-size:0.9rem;'>WTI CRUDE (OIL)</p>
            <h2 style='margin:0;'>${wti['price']}</h2>
            <p class="{color_class}">{arrow} {abs(wti['change'])} USD</p>
        </div>
        """, unsafe_allow_html=True)

time.sleep(1) # API Rate limit से बचने के लिए

brent = get_oil_price("brent")
with c2:
    if brent:
        color_class = "price-up" if brent['change'] >= 0 else "price-down"
        arrow = "▲" if brent['change'] >= 0 else "▼"
        st.markdown(f"""
        <div class="oil-card">
            <p style='color:#aaa; font-size:0.9rem;'>BRENT CRUDE (OIL)</p>
            <h2 style='margin:0;'>${brent['price']}</h2>
            <p class="{color_class}">{arrow} {abs(brent['change'])} USD</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# News Section
st.markdown("### 📰 युद्ध एवं भू-राजनीतिक अपडेट")
news = fetch_war_news()

if news:
    for art in news:
        st.markdown(f"""
        <div class="news-box">
            <h4 style='margin-bottom:5px; color:#fff;'>{art['title']}</h4>
            <p style='font-size:0.85rem; color:#ff416c;'>{art['source']['name']} • {art['publishedAt'][:10]}</p>
            <p style='font-size:0.95rem; color:#ccc;'>{art['description'][:250] if art['description'] else 'खबर का विवरण देखने के लिए नीचे क्लिक करें...'}</p>
            <a href="{art['url']}" target="_blank" style='color:#00ff88; text-decoration:none; font-weight:bold;'>पूरा पढ़ें ↗</a>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("वर्तमान में कोई नई खबर उपलब्ध नहीं है। कृपया रिफ्रेश करें।")

# Sidebar for controls
with st.sidebar:
    st.title("कंट्रोल पैनल")
    if st.button('🔄 डेटा रिफ्रेश करें'):
        st.rerun()
    st.markdown("---")
    st.write("**बाज़ार की स्थिति:**")
    st.write("ईरान-अमेरिका तनाव के कारण तेल की कीमतों में अस्थिरता बनी हुई है।")
    st.info(f"अंतिम अपडेट: {datetime.now().strftime('%H:%M:%S')}")
