import streamlit as st
import pandas as pd
import numpy as np
import io
import time

# ── Page config (MUST be first) ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Business Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ─────────────────────────────────────────────────────────────
from auth import show_auth_page, ensure_demo_user
from sample_data import SAMPLE_DATASETS
from utils import detect_numeric_cols, detect_categorical_cols, detect_date_cols
from dashboard import show_dashboard
from data_cleaner import show_data_cleaner
from custom_charts import show_custom_charts
from predictor import run_forecast, moving_average_chart
from ai_engine import ai_chat, generate_insights, generate_column_insight

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px; background: #1A1D2E;
        padding: 6px 8px; border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent; border-radius: 8px;
        padding: 8px 16px; font-weight: 500;
        color: #888; border: none;
    }
    .stTabs [aria-selected="true"] {
        background: #6C63FF !important; color: white !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #6C63FF, #3ECFCF);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; padding: 0.5rem 1rem;
    }
    .stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }

    .sidebar-header {
        background: linear-gradient(135deg, #6C63FF22, #3ECFCF11);
        border: 1px solid #6C63FF44; border-radius: 10px;
        padding: 1rem; text-align: center; margin-bottom: 1rem;
    }
    .chat-user {
        background: #6C63FF22; border-left: 3px solid #6C63FF;
        padding: 0.7rem 1rem; border-radius: 0 10px 10px 0;
        margin: 0.4rem 0;
    }
    .chat-ai {
        background: #1A1D2E; border-left: 3px solid #3ECFCF;
        padding: 0.7rem 1rem; border-radius: 0 10px 10px 0;
        margin: 0.4rem 0;
    }
    div[data-testid="metric-container"] {
        background: #1A1D2E; border: 1px solid #2A2D3E;
        border-radius: 10px; padding: 0.8rem;
    }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stAlert { border-radius: 10px; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Auth gate ─────────────────────────────────────────────────────────────────
ensure_demo_user()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_auth_page()
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    name = st.session_state.get("name", "User")
    st.markdown(f"""
    <div class="sidebar-header">
        <div style="font-size:2rem;">🤖</div>
        <div style="font-weight:700; color:#6C63FF; font-size:1rem;">AI Business Analytics</div>
        <div style="color:#888; font-size:0.8rem;">Welcome, {name}!</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Load Data")
    data_source = st.radio("Source", ["📤 Upload File", "📊 Sample Dataset"])

    df = None

    if data_source == "📤 Upload File":
        uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                else:
                    xl = pd.ExcelFile(uploaded)
                    sheet = st.selectbox("Sheet", xl.sheet_names)
                    df = pd.read_excel(uploaded, sheet_name=sheet)
                st.success(f"✅ Loaded: {df.shape[0]} rows × {df.shape[1]} cols")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        dataset_name = st.selectbox("Choose Dataset", list(SAMPLE_DATASETS.keys()))
        if st.button("Load Dataset"):
            with st.spinner("Loading..."):
                df = SAMPLE_DATASETS[dataset_name]()
                st.session_state["df"] = df
                st.success(f"✅ Loaded: {df.shape[0]} rows × {df.shape[1]} cols")

    # Persist df in session
    if df is not None:
        st.session_state["df"] = df
    df = st.session_state.get("df", None)

    # ── Settings ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    with st.expander("🔑 Groq API Key (AI Features)"):
        api_key = st.text_input("API Key", type="password",
                                value=st.session_state.get("groq_api_key", ""),
                                placeholder="gsk_...")
        if api_key:
            st.session_state["groq_api_key"] = api_key
            st.success("Key saved ✓")
        st.markdown("[Get free key →](https://console.groq.com)", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Dataset quick info
    if df is not None:
        st.markdown("---")
        st.markdown("### 📋 Dataset Info")
        st.caption(f"**Rows:** {df.shape[0]:,}  |  **Cols:** {df.shape[1]}")
        st.caption(f"**Numeric:** {len(detect_numeric_cols(df))} cols")
        st.caption(f"**Categorical:** {len(detect_categorical_cols(df))} cols")
        st.caption(f"**Missing:** {df.isnull().sum().sum():,} cells")

# ── Main content ──────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='
    background: linear-gradient(135deg, #6C63FF, #3ECFCF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 2rem; font-weight: 800; margin: 0 0 0.2rem 0;
'>🤖 AI Business Analytics Assistant</h1>
<p style='color:#888; margin-bottom: 1.5rem; font-size: 0.95rem;'>
    Upload your data → get dashboards, AI insights, forecasts, and chat with your data instantly
</p>
""", unsafe_allow_html=True)

if df is None:
    st.info("👈 Load a dataset from the sidebar to get started. Try a sample dataset!", icon="📂")
    st.markdown("""
    <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-top:1rem;">
        <div style="background:#1A1D2E; border:1px solid #2A2D3E; border-radius:10px; padding:1.2rem; flex:1; min-width:200px;">
            <div style="font-size:1.5rem;">📊</div>
            <div style="font-weight:600; margin:0.3rem 0;">Auto Dashboard</div>
            <div style="color:#888; font-size:0.85rem;">8+ charts generated automatically from your data</div>
        </div>
        <div style="background:#1A1D2E; border:1px solid #2A2D3E; border-radius:10px; padding:1.2rem; flex:1; min-width:200px;">
            <div style="font-size:1.5rem;">💬</div>
            <div style="font-weight:600; margin:0.3rem 0;">AI Chat</div>
            <div style="color:#888; font-size:0.85rem;">Ask anything — "Why did sales drop in March?"</div>
        </div>
        <div style="background:#1A1D2E; border:1px solid #2A2D3E; border-radius:10px; padding:1.2rem; flex:1; min-width:200px;">
            <div style="font-size:1.5rem;">📈</div>
            <div style="font-weight:600; margin:0.3rem 0;">Trend Predictor</div>
            <div style="color:#888; font-size:0.85rem;">ML-based forecasting with confidence intervals</div>
        </div>
        <div style="background:#1A1D2E; border:1px solid #2A2D3E; border-radius:10px; padding:1.2rem; flex:1; min-width:200px;">
            <div style="font-size:1.5rem;">🔍</div>
            <div style="font-weight:600; margin:0.3rem 0;">AI Insights</div>
            <div style="color:#888; font-size:0.85rem;">Executive report with risks & recommendations</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Dashboard",
    "💬 AI Chat",
    "🔍 AI Insights",
    "📈 Trend Predictor",
    "🎨 Custom Charts",
    "🧹 Data Cleaner",
    "📋 Raw Data",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    show_dashboard(df)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: AI CHAT
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("### 💬 Chat with Your Data")
    st.markdown("Ask any question about your dataset in plain English.")

    # Quick prompts
    st.markdown("**Quick questions:**")
    qp_cols = st.columns(4)
    quick_prompts = [
        "📉 Why did values decrease?",
        "🏆 What is the top performing category?",
        "📊 Summarize key trends",
        "⚠️ Any anomalies or outliers?",
    ]
    for i, qp in enumerate(quick_prompts):
        with qp_cols[i]:
            if st.button(qp, key=f"qp_{i}", use_container_width=True):
                st.session_state["chat_input"] = qp

    st.markdown("---")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 <b>AI:</b><br>{msg["content"]}</div>',
                        unsafe_allow_html=True)

    # Input
    user_input = st.chat_input("Ask anything about your data...")
    if "chat_input" in st.session_state and st.session_state["chat_input"]:
        user_input = st.session_state["chat_input"]
        st.session_state["chat_input"] = ""

    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.spinner("🤖 Analyzing..."):
            reply = ai_chat(df, user_input, st.session_state["chat_history"])
        st.session_state["chat_history"].append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state["chat_history"]:
        if st.button("🗑️ Clear Chat"):
            st.session_state["chat_history"] = []
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: AI INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("### 🔍 AI Insights Generator")
    st.markdown("Generate a full executive-level business intelligence report powered by AI.")

    c_btn, c_tip = st.columns([1, 3])
    with c_btn:
        gen_btn = st.button("🚀 Generate Full Report", use_container_width=True)
    with c_tip:
        st.info("💡 Add your Groq API key in sidebar Settings to enable AI-powered reports.")

    if gen_btn:
        with st.spinner("🤖 Generating executive insights report..."):
            report = generate_insights(df)
        st.session_state["insights_report"] = report

    if "insights_report" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["insights_report"])
        st.download_button(
            "⬇️ Download Report",
            data=st.session_state["insights_report"],
            file_name="ai_insights_report.txt",
            mime="text/plain",
        )

    # Column-level insights
    st.markdown("---")
    st.markdown("#### 🔬 Column-Level AI Analysis")
    num_cols = detect_numeric_cols(df)
    if num_cols:
        col_sel = st.selectbox("Pick a column for deep-dive", num_cols)
        if st.button("Analyze This Column"):
            with st.spinner("Analyzing..."):
                col_insight = generate_column_insight(df, col_sel)
            st.markdown(col_insight)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: TREND PREDICTOR
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("### 📈 AI Trend Predictor")
    st.markdown("Machine learning-based forecasting with confidence intervals.")

    num_cols = detect_numeric_cols(df)
    date_cols = detect_date_cols(df)

    if not date_cols:
        st.warning("⚠️ No date column detected. Trend predictor needs a date/time column.")
    elif not num_cols:
        st.warning("⚠️ No numeric columns found.")
    else:
        cfg1, cfg2, cfg3, cfg4 = st.columns(4)
        with cfg1:
            date_col = st.selectbox("Date Column", date_cols)
        with cfg2:
            val_col = st.selectbox("Value to Forecast", num_cols)
        with cfg3:
            periods = st.slider("Forecast Periods", 3, 24, 6)
        with cfg4:
            degree = st.select_slider("Model Complexity", [1, 2, 3], value=2,
                                      help="1=Linear, 2=Quadratic, 3=Cubic")

        if st.button("🚀 Run Forecast", use_container_width=False):
            with st.spinner("Training model & generating forecast..."):
                try:
                    fig, metrics, forecast_df = run_forecast(df, date_col, val_col, periods, degree)
                    st.session_state["forecast"] = (fig, metrics, forecast_df)
                except Exception as e:
                    st.error(f"Forecast error: {e}")

        if "forecast" in st.session_state:
            fig, metrics, forecast_df = st.session_state["forecast"]
            st.plotly_chart(fig, use_container_width=True)

            # Metrics
            m_cols = st.columns(len(metrics))
            for i, (k, v) in enumerate(metrics.items()):
                m_cols[i].metric(k, v)

            # Forecast table
            st.markdown("#### 📋 Forecast Values")
            st.dataframe(forecast_df, use_container_width=True)

            # Moving average
            st.markdown("---")
            st.markdown("#### 📊 Moving Average Analysis")
            ma_fig = moving_average_chart(df, date_col, val_col)
            st.plotly_chart(ma_fig, use_container_width=True)

            # Download
            csv_buf = io.StringIO()
            forecast_df.to_csv(csv_buf, index=False)
            st.download_button("⬇️ Download Forecast CSV", csv_buf.getvalue(),
                               "forecast.csv", "text/csv")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: CUSTOM CHARTS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    show_custom_charts(df)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: DATA CLEANER
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    cleaned_df = show_data_cleaner(df)
    if st.button("✅ Use Cleaned Data for Analysis"):
        st.session_state["df"] = cleaned_df
        st.success("Switched to cleaned dataset! Navigate to Dashboard tab.")
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: RAW DATA
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown("### 📋 Raw Data Explorer")

    r1, r2, r3 = st.columns(3)
    with r1:
        search_col = st.selectbox("Search in column", ["All"] + df.columns.tolist())
    with r2:
        search_val = st.text_input("Search value", "")
    with r3:
        rows_to_show = st.selectbox("Show rows", [50, 100, 500, "All"])

    display_df = df.copy()
    if search_val:
        if search_col == "All":
            mask = display_df.astype(str).apply(lambda row: row.str.contains(search_val, case=False, na=False)).any(axis=1)
        else:
            mask = display_df[search_col].astype(str).str.contains(search_val, case=False, na=False)
        display_df = display_df[mask]

    if rows_to_show != "All":
        display_df = display_df.head(rows_to_show)

    st.markdown(f"Showing **{len(display_df):,}** rows × **{df.shape[1]}** columns")
    st.dataframe(display_df, use_container_width=True, height=500)

    st.markdown("#### 📊 Descriptive Statistics")
    st.dataframe(df.describe().round(3), use_container_width=True)

    # Export
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    st.download_button("⬇️ Download Full Data as CSV", csv_buf.getvalue(),
                       "data.csv", "text/csv")
