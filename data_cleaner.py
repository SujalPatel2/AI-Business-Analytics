import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import apply_chart_theme, CHART_THEME
import io

def show_data_cleaner(df: pd.DataFrame):
    st.markdown("### 🧹 Data Quality & Cleaner")

    # ── Quality Overview ─────────────────────────────────────────────────────
    st.markdown("#### 📋 Data Quality Report")
    total = len(df)
    total_cells = df.size
    missing = df.isnull().sum()
    missing_pct = (missing / total * 100).round(2)
    dup_rows = df.duplicated().sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows", f"{total:,}")
    c2.metric("Total Columns", df.shape[1])
    c3.metric("Duplicate Rows", f"{dup_rows:,}")
    c4.metric("Missing Cells", f"{df.isnull().sum().sum():,}")

    # Missing value heatmap
    if missing.sum() > 0:
        fig = px.bar(
            x=missing[missing > 0].index,
            y=missing_pct[missing > 0].values,
            labels={"x": "Column", "y": "Missing %"},
            color=missing_pct[missing > 0].values,
            color_continuous_scale="Reds",
        )
        apply_chart_theme(fig, "⚠️ Missing Values by Column (%)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No missing values found!")

    st.markdown("---")

    # ── Column Info ──────────────────────────────────────────────────────────
    st.markdown("#### 🗂️ Column Details")
    info = pd.DataFrame({
        "Column": df.columns,
        "Dtype": df.dtypes.astype(str).values,
        "Non-Null": df.notnull().sum().values,
        "Null": df.isnull().sum().values,
        "Null %": missing_pct.values,
        "Unique": df.nunique().values,
    })
    st.dataframe(info, use_container_width=True)

    st.markdown("---")

    # ── Cleaning Operations ──────────────────────────────────────────────────
    st.markdown("#### 🔧 Apply Cleaning Operations")
    df_clean = df.copy()

    ops_col, preview_col = st.columns([1, 2])
    with ops_col:
        st.markdown("**Select operations:**")

        drop_dups = st.checkbox("🗑️ Remove duplicate rows", value=False)
        fill_missing = st.selectbox(
            "Fill numeric missing values",
            ["Don't fill", "Mean", "Median", "Zero", "Forward Fill"],
        )
        drop_high_null_cols = st.slider(
            "Drop columns with >X% nulls", 0, 100, 100
        )
        strip_whitespace = st.checkbox("✂️ Strip whitespace from text", value=True)
        lowercase_text = st.checkbox("🔡 Lowercase text columns", value=False)
        drop_selected_cols = st.multiselect(
            "🗑️ Drop specific columns", df.columns.tolist()
        )

    # Apply ops
    if drop_dups:
        df_clean = df_clean.drop_duplicates()
    if drop_selected_cols:
        df_clean = df_clean.drop(columns=drop_selected_cols, errors="ignore")
    if drop_high_null_cols < 100:
        threshold = drop_high_null_cols / 100
        df_clean = df_clean.dropna(thresh=int((1 - threshold) * len(df_clean)), axis=1)
    if fill_missing != "Don't fill":
        num_cols = df_clean.select_dtypes(include="number").columns
        for col in num_cols:
            if fill_missing == "Mean":
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            elif fill_missing == "Median":
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            elif fill_missing == "Zero":
                df_clean[col] = df_clean[col].fillna(0)
            elif fill_missing == "Forward Fill":
                df_clean[col] = df_clean[col].fillna(method="ffill")
    if strip_whitespace:
        for col in df_clean.select_dtypes(include="object").columns:
            df_clean[col] = df_clean[col].str.strip()
    if lowercase_text:
        for col in df_clean.select_dtypes(include="object").columns:
            df_clean[col] = df_clean[col].str.lower()

    with preview_col:
        st.markdown(f"**Preview (cleaned): {df_clean.shape[0]} rows × {df_clean.shape[1]} cols**")
        st.dataframe(df_clean.head(30), use_container_width=True)

    # ── Filter & Export ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔽 Filter & Export")

    filter_col = st.selectbox("Filter by column", ["None"] + df_clean.columns.tolist())
    if filter_col != "None":
        unique_vals = df_clean[filter_col].dropna().unique()
        selected = st.multiselect(f"Select values for {filter_col}", unique_vals, default=list(unique_vals[:5]))
        if selected:
            df_clean = df_clean[df_clean[filter_col].isin(selected)]
            st.info(f"Filtered: {len(df_clean):,} rows remaining")

    ecol1, ecol2 = st.columns(2)
    with ecol1:
        csv_buf = io.StringIO()
        df_clean.to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Download as CSV",
            data=csv_buf.getvalue(),
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with ecol2:
        xl_buf = io.BytesIO()
        df_clean.to_excel(xl_buf, index=False)
        st.download_button(
            "⬇️ Download as Excel",
            data=xl_buf.getvalue(),
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    return df_clean
