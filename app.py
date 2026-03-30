import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import google.generativeai as genai

# --- 1. Page Config & Styling ---
st.set_page_config(page_title="NichePulse AI", page_icon="📈", layout="wide")
st.markdown("""<style>.main { background-color: #0e1117; color: white; }</style>""", unsafe_allow_html=True)

# --- 2. Secure API Key Loading ---
# We use st.secrets for deployment, and a fallback for local testing
YOUTUBE_KEY = st.secrets.get("YOUTUBE_API_KEY", "YOUR_LOCAL_KEY_HERE")
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_LOCAL_KEY_HERE")

# --- 3. The Core Engines ---
def get_outliers(query, threshold=5):
    yt = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    search = yt.search().list(q=query, part='snippet', maxResults=10, type='video').execute()
    
    results = []
    for item in search['items']:
        vid_id = item['id']['videoId']
        chan_id = item['snippet']['channelId']
        
        # Get Stats
        v_stats = yt.videos().list(id=vid_id, part='statistics').execute()
        c_stats = yt.channels().list(id=chan_id, part='statistics').execute()
        
        views = int(v_stats['items'][0]['statistics'].get('viewCount', 0))
        subs = int(c_stats['items'][0]['statistics'].get('subscriberCount', 1))
        mult = views / subs
        
        if mult >= threshold:
            results.append({"Title": item['snippet']['title'], "Views": views, "Subs": subs, "Multiplier": round(mult, 1), "ID": vid_id})
    return results

def get_ai_strategy(title):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-3-flash')
    prompt = f"Analyze the YouTube video title '{title}'. Why is it viral? Give me a 5-point 'Faceless Channel' strategy to beat it."
    return model.generate_content(prompt).text

# --- 4. User Interface ---
st.title("📡 NichePulse AI")
query = st.text_input("What niche are we hunting?", "AI Side Hustles")

if st.button("Scan Market"):
    with st.spinner("Analyzing 2026 Trends..."):
        data = get_outliers(query)
        if data:
            df = pd.DataFrame(data)
            st.success(f"Found {len(df)} Outliers!")
            
            # Show Metrics
            best = df.iloc[df['Multiplier'].idxmax()]
            col1, col2 = st.columns(2)
            col1.metric("Highest Multiplier", f"{best['Multiplier']}x")
            col2.metric("Target Title", best['Title'][:30] + "...")
            
            # Show Data
            st.dataframe(df.drop(columns=['ID']), use_container_width=True)
            
            # AI Strategy
            st.subheader("🤖 AI Content Blueprint")
            strategy = get_ai_strategy(best['Title'])
            st.write(strategy)
        else:
            st.warning("No outliers found. Try a lower threshold or different keyword.")