import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

CHART_THEME = {
    "template": "plotly_dark",
    "paper_bgcolor": "#1A1D2E",
    "plot_bgcolor": "#1A1D2E",
    "font_color": "#FAFAFA",
    "colorscale": px.colors.sequential.Viridis,
    "palette": ["#6C63FF", "#3ECFCF", "#FF6584", "#FFD166", "#06D6A0", "#EF476F", "#118AB2"],
}

def apply_chart_theme(fig, title=""):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(color=CHART_THEME["font_color"], family="Inter, sans-serif"),
        title=dict(text=title, font=dict(size=16, color="#FAFAFA"), x=0.02),
        margin=dict(l=40, r=20, t=50, b=40),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.1)"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig

def kpi_card(label, value, delta=None, delta_label="vs prev", icon="📊", color="#6C63FF"):
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        clr = "#06D6A0" if delta >= 0 else "#EF476F"
        delta_html = f"<span style='color:{clr}; font-size:0.8rem;'>{arrow} {abs(delta):.1f}% {delta_label}</span>"
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}22, {color}08);
        border: 1px solid {color}44;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        height: 130px;
        display: flex; flex-direction: column; justify-content: center;
    ">
        <div style="font-size: 1.8rem;">{icon}</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: {color}; margin: 0.2rem 0;">{value}</div>
        <div style="font-size: 0.75rem; color: #aaa; margin-bottom: 0.2rem;">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def format_number(n):
    if isinstance(n, float):
        if abs(n) >= 1e6:
            return f"{n/1e6:.2f}M"
        if abs(n) >= 1e3:
            return f"{n/1e3:.1f}K"
        return f"{n:.2f}"
    if isinstance(n, int):
        if abs(n) >= 1e6:
            return f"{n/1e6:.2f}M"
        if abs(n) >= 1e3:
            return f"{n/1e3:.1f}K"
        return str(n)
    return str(n)

def detect_numeric_cols(df):
    return df.select_dtypes(include="number").columns.tolist()

def detect_categorical_cols(df):
    return df.select_dtypes(include=["object", "category"]).columns.tolist()

def detect_date_cols(df):
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    for col in df.select_dtypes(include="object").columns:
        try:
            parsed = pd.to_datetime(df[col], errors="raise", infer_datetime_format=True)
            if parsed.notna().sum() > len(df) * 0.8:
                date_cols.append(col)
        except Exception:
            pass
    return date_cols

def get_df_summary(df: pd.DataFrame) -> str:
    num_cols = detect_numeric_cols(df)
    cat_cols = detect_categorical_cols(df)
    lines = [
        f"Dataset: {df.shape[0]} rows × {df.shape[1]} columns",
        f"Numeric columns: {', '.join(num_cols) if num_cols else 'None'}",
        f"Categorical columns: {', '.join(cat_cols) if cat_cols else 'None'}",
    ]
    for col in num_cols[:6]:
        s = df[col]
        lines.append(
            f"  - {col}: min={s.min():.2f}, max={s.max():.2f}, mean={s.mean():.2f}, sum={s.sum():.2f}"
        )
    for col in cat_cols[:4]:
        top = df[col].value_counts().head(3).to_dict()
        lines.append(f"  - {col} top values: {top}")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        lines.append(f"Missing values: {missing.to_dict()}")
    return "\n".join(lines)
