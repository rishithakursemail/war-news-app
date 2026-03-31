import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
NEWS_API_KEY = "be07c5b9437448cbb365fcd80b336f01"
OIL_API_KEY = "WEJSMD3L9T43WZOB"

st.set_page_config(page_title="Iran-US War & Oil Tracker", layout="wide", page_icon="🚀")

# --- CSS FOR STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    .news-card { padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; background: #262730; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_oil_data(symbol="WTI"):
    # Alpha Vantage API call for Crude Oil
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={OIL_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()["Global Quote"]
        return data
    except:
        return None

def fetch_war_news():
    # NewsAPI call for Iran-US Conflict
    url = f"https://newsapi.org/v2/everything?q=Iran+USA+War+OR+Hormuz&sortBy=publishedAt&language=hi&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url)
        return r.json()["articles"][:10] # Top 10 news
    except:
        return []

# --- UI LAYOUT ---
st.title("🛡️ ईरान-अमेरिका युद्ध एवं क्रूड ऑयल लाइव न्यूज़फीड")
st.write(f"अंतिम अपडेट: {datetime.now().strftime('%d %B, %Y | %H:%M')}")

# --- OIL PRICE SECTION ---
st.header("🛢️ वैश्विक क्रूड ऑयल मार्केट")
col1, col2 = st.columns(2)

wti_data = get_oil_data("WTI")
if wti_data:
    col1.metric("WTI Crude", f"${wti_data['05. price']}", wti_data['09. change'])
else:
    col1.warning("WTI डेटा लोड नहीं हो सका")

# Brent के लिए सिंबल आमतौर पर 'BRENT' होता है Alpha Vantage में
brent_data = get_oil_data("BRENT")
if brent_data:
    col2.metric("Brent Crude", f"${brent_data['05. price']}", brent_data['09. change'])
else:
    col2.info("Brent डेटा उपलब्ध हो रहा है...")

st.markdown("---")

# --- NEWS SECTION ---
st.header("📰 ताज़ा न्यूज़ अलर्ट (War Updates)")
news_articles = fetch_war_news()

if not news_articles:
    st.write("वर्तमान में कोई ताज़ा न्यूज़ नहीं मिली। कृपया कुछ देर बाद प्रयास करें।")
else:
    for art in news_articles:
        with st.container():
            st.markdown(f"""
                <div class="news-card">
                    <h3>{art['title']}</h3>
                    <p style="color: #aaa;">स्रोत: {art['source']['name']} | समय: {art['publishedAt'][:10]}</p>
                    <p>{art['description'] if art['description'] else 'विवरण उपलब्ध नहीं है'}</p>
                    <a href="{art['url']}" target="_blank">पूरा पढ़ें ↗️</a>
                </div>
            """, unsafe_allow_html=True)

# --- REFRESH BUTTON ---
if st.button('🔄 डेटा रिफ्रेश करें'):
    st.rerun()
