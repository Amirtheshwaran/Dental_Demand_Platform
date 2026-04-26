"""
Demo launcher: pre-loads CDC PLACES County Data 2025 so the browser agent
can test all tabs without a manual file upload.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import io
import anthropic

from data_processing import load_and_clean_data, calculate_demand_index
from model import run_clustering, run_anomaly_detection, get_recommendation_reasoning

DEMO_CSV = r"C:\Users\Amirthesh\Downloads\PLACES__Local_Data_for_Better_Health,_County_Data,_2025_release_20260426.csv"

# --- Page Configuration ---
st.set_page_config(
    page_title="Dental Demand AI Platform",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Dark Theme CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp {
        background-color: #0b0f19;
        background-image: radial-gradient(circle at top right, #1e1b4b 0%, transparent 40%),
                          radial-gradient(circle at bottom left, #0f172a 0%, transparent 40%);
        background-attachment: fixed;
    }
    .hero-banner {
        background: linear-gradient(135deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%);
        padding: 2.5rem 2rem; border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4); margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden;
    }
    .hero-banner::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    }
    .hero-title {
        font-size: 2.5rem; font-weight: 700;
        background: linear-gradient(90deg, #60a5fa, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;
    }
    .hero-subtitle { color: #94a3b8; font-size: 1.1rem; font-weight: 400; }
    div[data-testid="metric-container"] {
        background: rgba(30,41,59,0.5); backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08); padding: 1.5rem; border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5);
        border: 1px solid rgba(139,92,246,0.3);
    }
    div[data-testid="stMetricValue"] { color: #f8fafc !important; }
    div[data-testid="stMetricLabel"] { color: #94a3b8 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 1rem; padding-bottom: 0.5rem; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: transparent; border-radius: 0.5rem;
        padding: 0.5rem 1.5rem; font-weight: 600; font-size: 1.05rem; color: #94a3b8;
        transition: all 0.2s ease; border: 1px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover { background-color: rgba(255,255,255,0.05); color: #60a5fa; }
    .stTabs [aria-selected="true"] {
        background-color: rgba(30,41,59,0.8); color: #60a5fa !important;
        border: 1px solid rgba(255,255,255,0.1); border-bottom-color: #8b5cf6 !important;
        border-bottom-width: 3px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); color: white !important;
        border: none; border-radius: 0.5rem; font-weight: 600; padding: 0.5rem 1.5rem;
        transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(59,130,246,0.4);
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 6px 15px rgba(139,92,246,0.5); }
    .premium-container {
        background: rgba(15,23,42,0.6); padding: 1.5rem; border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05);
        margin-top: 1rem; backdrop-filter: blur(5px);
    }
    h1, h2, h3, .stMarkdown p { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🦷 Dental Setup")
st.sidebar.caption("Provide context dataset to begin analysis.")
uploaded_file = st.sidebar.file_uploader("Upload CDC Data (CSV)", type=["csv"])

@st.cache_data(show_spinner=False)
def get_cleaned_data_v2(file_obj):
    return load_and_clean_data(file_obj)

@st.cache_data(show_spinner=False)
def get_demo_data():
    return load_and_clean_data(DEMO_CSV)

if not uploaded_file:
    st.sidebar.info("🔬 Demo mode: CDC PLACES County Data 2025 pre-loaded.")
    with st.spinner("Loading CDC PLACES demo data..."):
        df_raw = get_demo_data()
else:
    with st.spinner("Processing Data Pipeline..."):
        df_raw = get_cleaned_data_v2(uploaded_file)

if df_raw.empty:
    st.error("No data loaded.")
    st.stop()

st.sidebar.success(f"Loaded {len(df_raw):,} records.")

st.sidebar.divider()
st.sidebar.header("Global Weights")
weight_prev = st.sidebar.slider("Prevalence Weight", 0.0, 1.0, 0.4, 0.1)
weight_pop  = st.sidebar.slider("Pop 65+ Weight",    0.0, 1.0, 0.3, 0.1)
weight_inc  = st.sidebar.slider("Income Weight",      0.0, 1.0, 0.2, 0.1)
weight_dens = st.sidebar.slider("Density Weight",     0.0, 1.0, 0.1, 0.1)
weights = {'prevalence': weight_prev, 'pop65': weight_pop, 'income': weight_inc, 'density': weight_dens}
min_prev = st.sidebar.slider("Min Prevalence Filter (%)", 0.0, 50.0, 10.0, 1.0)
st.sidebar.divider()
raw_vs_ai = st.sidebar.toggle("Raw Data vs AI Insights", value=False)
st.sidebar.divider()
st.sidebar.header("🤖 AI Setup")
api_key = st.sidebar.text_input("Claude API Key", type="password", help="Paste your Anthropic API key.")

# --- Process Pipeline ---
df_scored   = calculate_demand_index(df_raw, weights)
df_filtered = df_scored[df_scored['Prevalence'] >= min_prev]

if df_filtered.empty:
    st.warning("No counties match your Minimum Prevalence Filter.")
    st.stop()

df_final = run_clustering(df_filtered, n_clusters=4)
df_final = run_anomaly_detection(df_final)

if 'State' in df_final.columns and 'County' in df_final.columns:
    df_top = df_final.sort_values(by="Demand_Index", ascending=False).drop_duplicates(subset=['State','County']).head(50)
else:
    df_top = df_final.sort_values(by="Demand_Index", ascending=False).head(50)

# --- Header ---
st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📊 Strategic Decision Platform</div>
        <div class="hero-subtitle">Optimize your dental network expansion using ML-driven demographic risk and demand models.</div>
    </div>
""", unsafe_allow_html=True)

tab_overview, tab_ai, tab_recs, tab_chat = st.tabs(["🌎 Overview", "🧠 AI Insights", "✨ Recommendations", "🤖 AI Assistant"])

with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Markets", f"{len(df_final):,}")
    c2.metric("Mean Tooth-Loss Prevalence", f"{df_final['Prevalence'].mean():.1f}%")
    top_market = df_top.iloc[0]['County'] if not df_top.empty else "N/A"
    top_score  = df_top.iloc[0]['Demand_Index'] if not df_top.empty else "N/A"
    c3.metric("Highest Demand Market", top_market, f"Score: {top_score:.1f}")
    c4.metric("Strategy Mode", "AI-Assisted" if not raw_vs_ai else "Raw")
    st.write("")

    col_map, col_bar = st.columns([2, 1])

    with col_map:
        st.markdown('<div class="premium-container">', unsafe_allow_html=True)
        st.subheader("Geographic Demand Distribution")
        if 'FIPS' in df_final.columns:
            df_map = df_final.groupby('FIPS', as_index=False).agg({'Demand_Index':'mean','Prevalence':'mean','County':'first'})
            fig_map = px.choropleth(df_map, geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
                                    locations='FIPS', color='Demand_Index', color_continuous_scale="Plasma",
                                    scope="usa", hover_name="County", hover_data=["Prevalence","Demand_Index"], template="plotly_dark")
            fig_map.update_geos(bgcolor="rgba(0,0,0,0)", showcoastlines=True, coastlinecolor="rgba(255,255,255,0.2)", showland=True, landcolor="rgba(30,41,59,0.5)")
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_map, use_container_width=True)
        elif 'State' in df_final.columns:
            df_state = df_final.groupby('State')['Demand_Index'].mean().reset_index()
            fig_map = px.choropleth(df_state, locations='State', locationmode="USA-states", color='Demand_Index',
                                    scope="usa", color_continuous_scale="Plasma", template="plotly_dark")
            fig_map.update_geos(bgcolor="rgba(0,0,0,0)", showcoastlines=True, coastlinecolor="rgba(255,255,255,0.2)", showland=True, landcolor="rgba(30,41,59,0.5)")
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_bar:
        st.markdown('<div class="premium-container">', unsafe_allow_html=True)
        st.subheader("Top Counties by Demand")
        fig_bar = px.bar(df_top.head(10), x="Demand_Index", y="County", orientation='h',
                         color='Prevalence', color_continuous_scale='Purpor', template="plotly_dark")
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin={"r":0,"t":30,"l":0,"b":0},
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab_ai:
    if not raw_vs_ai:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown('<div class="premium-container">', unsafe_allow_html=True)
            st.subheader("Market Clusters (K-Means)")
            st.markdown("Counties dynamically segmented using 100% real numeric data.")
            x_col = "Prevalence"
            if "Median_Income" in df_final.columns:
                y_col = "Median_Income"
            elif "TotalPopulation" in df_final.columns:
                y_col = "TotalPopulation"
            else:
                y_col = "Demand_Index"
            if x_col in df_final.columns and y_col in df_final.columns:
                use_log = (y_col == "TotalPopulation")
                fig_cluster = px.scatter(df_final, x=x_col, y=y_col, color="Cluster_Name",
                                         hover_name="County", size="Demand_Index",
                                         log_y=use_log,
                                         color_discrete_sequence=px.colors.qualitative.Pastel, template="plotly_dark")
                fig_cluster.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin={"t":10})
                st.plotly_chart(fig_cluster, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_c2:
            st.markdown('<div class="premium-container">', unsafe_allow_html=True)
            st.subheader("Market Anomalies (Isolation Forest)")
            st.markdown("Unsupervised ML identifies statistically unusual markets based on raw features.")
            if 'Anomaly_Score' in df_final.columns and df_final['Is_Anomaly'].sum() > 0:
                df_anom = df_final[df_final['Is_Anomaly']].sort_values(by="Anomaly_Score", ascending=False).head(10)
                if not df_anom.empty:
                    fig_anom = px.bar(df_anom, x='Anomaly_Score', y='County', orientation='h',
                                      color='Anomaly_Score', color_continuous_scale='Teal', template="plotly_dark")
                    fig_anom.update_layout(yaxis={'categoryorder':'total ascending'}, margin={"r":0,"t":30,"l":0,"b":0},
                                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_anom, use_container_width=True)
            else:
                st.info("Isolation Forest requires multiple numeric columns to detect anomalies.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("AI Insights are toggled off. Toggle 'Raw Data vs AI Insights' in the sidebar to view.")

with tab_recs:
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        generate = st.button("Generate Strategy Report", use_container_width=True)
    if generate:
        with st.spinner("Compiling ML Predictions..."):
            time.sleep(0.5)
        st.subheader("Top 5 Strategic Expansion Targets")
        top_5 = df_top.head(5)
        for _, row in top_5.iterrows():
            with st.expander(f"📍 {row['County']}, {row.get('State','')} — Demand Score: {row['Demand_Index']}", expanded=True):
                r1, r2, r3 = st.columns(3)
                r1.metric("Strategic Tier", row.get('Cluster_Name', 'General Tier'))
                size = "Large" if row['Demand_Index'] > 85 else ("Medium" if row['Demand_Index'] > 60 else "Small")
                r2.metric("Recommended Format", size)
                is_anomaly = row.get('Is_Anomaly', False)
                r3.metric("Anomaly Status", "⚠️ Outlier Market" if is_anomaly else "Standard Market")
                st.markdown("**Strategic Reasoning:**")
                st.info(get_recommendation_reasoning(row))
    else:
        st.info("Click 'Generate Strategy Report' to view personalized expansion plans.")
    st.divider()
    with st.expander("Explore Full Analyzed Dataset"):
        st.dataframe(df_final, use_container_width=True)

with tab_chat:
    st.header("🤖 Live Data AI Assistant")
    st.markdown("Chat with your real data! Ask dynamic questions about market conditions, trends, or recommendations.")
    if not api_key:
        st.warning("Please paste your Claude API Key in the left sidebar to activate the AI Chatbot.")
    else:
        st.markdown('<div class="premium-container">', unsafe_allow_html=True)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I am ready to analyze your dental demand metrics. What would you like to know?"}]
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])
        user_query = st.chat_input("E.g., Which state has the most markets in the top 10?")
        if user_query:
            st.chat_message("user").write(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.spinner("AI is analyzing live data..."):
                try:
                    summary = f"Total Datapoints: {len(df_final)}\nOverall Avg Prevalence: {df_final['Prevalence'].mean():.2f}%\n"
                    top_5_markets = df_top.head(5)[['County','State','Demand_Index','Cluster_Name']].to_string()
                    prompt = f"Data Summary:\n{summary}\nTop 5 Demands:\n{top_5_markets}\n\nUser Question:\n{user_query}\n\nProvide a concise strategic answer using only the data above. Do NOT make up markets."
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(model="claude-sonnet-4-6", max_tokens=1000, messages=[{"role":"user","content":prompt}])
                    st.chat_message("assistant").write(response.content[0].text)
                    st.session_state.chat_history.append({"role":"assistant","content":response.content[0].text})
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
