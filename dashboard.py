import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (apply_chart_theme, kpi_card, format_number,
                   detect_numeric_cols, detect_categorical_cols, detect_date_cols, CHART_THEME)

def show_dashboard(df: pd.DataFrame):
    num_cols = detect_numeric_cols(df)
    cat_cols = detect_categorical_cols(df)
    date_cols = detect_date_cols(df)

    st.markdown("### 📊 Auto-Generated Dashboard")

    # ── KPI ROW ──────────────────────────────────────────────────────────────
    st.markdown("#### 🔢 Key Metrics")
    kpi_items = num_cols[:5]
    cols = st.columns(len(kpi_items) if kpi_items else 1)
    icons = ["💰", "📦", "📈", "🎯", "⭐"]
    colors = ["#6C63FF", "#3ECFCF", "#FFD166", "#06D6A0", "#EF476F"]
    for i, col in enumerate(kpi_items):
        with cols[i]:
            val = df[col].sum() if df[col].dtype in [int, float] else df[col].nunique()
            kpi_card(col, format_number(val), icon=icons[i % 5], color=colors[i % 5])

    st.markdown("")

    # ── ROW 1: Distribution + Correlation ────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        if num_cols:
            sel = st.selectbox("📊 Distribution of", num_cols, key="dist_col")
            fig = px.histogram(df, x=sel, nbins=30,
                               color_discrete_sequence=[CHART_THEME["palette"][0]])
            apply_chart_theme(fig, f"Distribution — {sel}")
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if len(num_cols) >= 2:
            fig = px.imshow(
                df[num_cols].corr().round(2),
                text_auto=True,
                color_continuous_scale="Viridis",
                aspect="auto",
            )
            apply_chart_theme(fig, "🔗 Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)

    # ── ROW 2: Bar + Pie ──────────────────────────────────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        if cat_cols and num_cols:
            cat_sel = st.selectbox("📦 Group by (Bar)", cat_cols, key="bar_cat")
            num_sel = st.selectbox("Metric", num_cols, key="bar_num")
            agg = df.groupby(cat_sel)[num_sel].sum().reset_index().sort_values(num_sel, ascending=False).head(15)
            fig = px.bar(agg, x=cat_sel, y=num_sel,
                         color=cat_sel,
                         color_discrete_sequence=CHART_THEME["palette"])
            apply_chart_theme(fig, f"Total {num_sel} by {cat_sel}")
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if cat_cols and num_cols:
            pie_cat = st.selectbox("🥧 Pie — Category", cat_cols, key="pie_cat")
            pie_num = st.selectbox("Metric", num_cols, key="pie_num")
            pie_data = df.groupby(pie_cat)[pie_num].sum().reset_index()
            fig = px.pie(pie_data, names=pie_cat, values=pie_num,
                         color_discrete_sequence=CHART_THEME["palette"],
                         hole=0.4)
            apply_chart_theme(fig, f"{pie_num} Share by {pie_cat}")
            st.plotly_chart(fig, use_container_width=True)

    # ── ROW 3: Line (time) + Scatter ─────────────────────────────────────────
    c5, c6 = st.columns(2)

    with c5:
        if date_cols and num_cols:
            dc = st.selectbox("📅 Date column", date_cols, key="line_date")
            nc = st.selectbox("📈 Value", num_cols, key="line_val")
            color_by = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="line_color")
            ts = df.copy()
            ts[dc] = pd.to_datetime(ts[dc], errors="coerce")
            ts = ts.dropna(subset=[dc])
            if color_by != "None":
                agg_ts = ts.groupby([dc, color_by])[nc].mean().reset_index()
                fig = px.line(agg_ts, x=dc, y=nc, color=color_by,
                              color_discrete_sequence=CHART_THEME["palette"])
            else:
                agg_ts = ts.groupby(dc)[nc].mean().reset_index()
                fig = px.line(agg_ts, x=dc, y=nc,
                              color_discrete_sequence=[CHART_THEME["palette"][0]])
            apply_chart_theme(fig, f"📈 {nc} over Time")
            st.plotly_chart(fig, use_container_width=True)
        elif num_cols:
            st.info("No date column detected for time series.")

    with c6:
        if len(num_cols) >= 2:
            x_col = st.selectbox("X axis", num_cols, index=0, key="scatter_x")
            y_col = st.selectbox("Y axis", num_cols, index=min(1, len(num_cols)-1), key="scatter_y")
            color_col = st.selectbox("Color by", ["None"] + cat_cols, key="scatter_color")
            if color_col != "None":
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                                 color_discrete_sequence=CHART_THEME["palette"],
                                 opacity=0.75)
            else:
                fig = px.scatter(df, x=x_col, y=y_col, opacity=0.75,
                                 color_discrete_sequence=[CHART_THEME["palette"][2]])
            apply_chart_theme(fig, f"Scatter: {x_col} vs {y_col}")
            st.plotly_chart(fig, use_container_width=True)

    # ── ROW 4: Box + Top-N ───────────────────────────────────────────────────
    c7, c8 = st.columns(2)

    with c7:
        if cat_cols and num_cols:
            bx_cat = st.selectbox("Box — Group", cat_cols, key="box_cat")
            bx_num = st.selectbox("Box — Metric", num_cols, key="box_num")
            fig = px.box(df, x=bx_cat, y=bx_num,
                         color=bx_cat,
                         color_discrete_sequence=CHART_THEME["palette"])
            apply_chart_theme(fig, f"Distribution of {bx_num} by {bx_cat}")
            st.plotly_chart(fig, use_container_width=True)

    with c8:
        if cat_cols and num_cols:
            top_cat = st.selectbox("Top-N Category", cat_cols, key="top_cat")
            top_num = st.selectbox("Top-N Metric", num_cols, key="top_num")
            n = st.slider("Top N", 5, 20, 10, key="top_n")
            top_df = df.groupby(top_cat)[top_num].sum().nlargest(n).reset_index()
            fig = px.bar(top_df, x=top_num, y=top_cat, orientation="h",
                         color=top_num,
                         color_continuous_scale="Viridis")
            apply_chart_theme(fig, f"Top {n} {top_cat} by {top_num}")
            st.plotly_chart(fig, use_container_width=True)

    # ── Sunburst (if 2+ cat cols) ─────────────────────────────────────────────
    if len(cat_cols) >= 2 and num_cols:
        st.markdown("#### 🌞 Hierarchical View (Sunburst)")
        sc1, sc2 = st.columns(2)
        with sc1:
            sb_path = st.multiselect("Hierarchy (in order)", cat_cols,
                                     default=cat_cols[:2], key="sb_path")
        with sc2:
            sb_val = st.selectbox("Value", num_cols, key="sb_val")
        if len(sb_path) >= 1:
            fig = px.sunburst(df, path=sb_path, values=sb_val,
                              color_discrete_sequence=CHART_THEME["palette"])
            apply_chart_theme(fig, "Sunburst Breakdown")
            st.plotly_chart(fig, use_container_width=True)
