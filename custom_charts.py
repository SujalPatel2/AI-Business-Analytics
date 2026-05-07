import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import apply_chart_theme, detect_numeric_cols, detect_categorical_cols, detect_date_cols, CHART_THEME
import io

CHART_TYPES = [
    "Bar", "Horizontal Bar", "Line", "Area",
    "Scatter", "Bubble", "Pie", "Donut",
    "Box", "Violin", "Histogram", "Funnel",
    "Treemap", "Sunburst", "Heatmap (Pivot)"
]

def show_custom_charts(df: pd.DataFrame):
    num_cols = detect_numeric_cols(df)
    cat_cols = detect_categorical_cols(df)
    date_cols = detect_date_cols(df)
    all_cols = df.columns.tolist()

    st.markdown("### 🎨 Custom Chart Builder")
    st.markdown("Build any chart you want — choose type, axes, colors, and more.")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        chart_type = st.selectbox("Chart Type", CHART_TYPES)
    with c2:
        x_col = st.selectbox("X Axis / Category", all_cols)
    with c3:
        y_col = st.selectbox("Y Axis / Value", num_cols if num_cols else all_cols)

    c4, c5, c6 = st.columns(3)
    with c4:
        color_col = st.selectbox("Color by", ["None"] + cat_cols)
        color_col = None if color_col == "None" else color_col
    with c5:
        agg_func = st.selectbox("Aggregation", ["Sum", "Mean", "Count", "Max", "Min"])
    with c6:
        palette = st.selectbox("Color Palette", ["Default", "Viridis", "Plasma", "Turbo", "Sunset", "Teal"])

    color_map = {
        "Default": CHART_THEME["palette"],
        "Viridis": px.colors.sequential.Viridis,
        "Plasma": px.colors.sequential.Plasma,
        "Turbo": px.colors.sequential.Turbo,
        "Sunset": px.colors.sequential.Sunset,
        "Teal": px.colors.sequential.Teal,
    }
    palette_colors = color_map[palette]

    # Aggregate data
    if agg_func == "Count":
        plot_df = df.groupby([x_col] + ([color_col] if color_col else [])).size().reset_index(name=y_col)
    else:
        agg_map = {"Sum": "sum", "Mean": "mean", "Max": "max", "Min": "min"}
        grp_cols = [x_col] + ([color_col] if color_col else [])
        plot_df = df.groupby(grp_cols)[y_col].agg(agg_map[agg_func]).reset_index()

    # Build figure
    fig = None
    try:
        if chart_type == "Bar":
            fig = px.bar(plot_df, x=x_col, y=y_col, color=color_col,
                         color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Horizontal Bar":
            fig = px.bar(plot_df, x=y_col, y=x_col, orientation="h", color=color_col,
                         color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Line":
            fig = px.line(plot_df, x=x_col, y=y_col, color=color_col,
                          color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Area":
            fig = px.area(plot_df, x=x_col, y=y_col, color=color_col,
                          color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                             color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Bubble":
            size_col = st.selectbox("Bubble Size column", num_cols)
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col,
                             color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Pie":
            fig = px.pie(plot_df, names=x_col, values=y_col,
                         color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Donut":
            fig = px.pie(plot_df, names=x_col, values=y_col, hole=0.5,
                         color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Box":
            fig = px.box(df, x=x_col, y=y_col, color=color_col,
                         color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Violin":
            fig = px.violin(df, x=x_col, y=y_col, color=color_col, box=True,
                            color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=y_col, color=color_col, nbins=30,
                               color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Funnel":
            fig = px.funnel(plot_df, x=y_col, y=x_col,
                            color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Treemap":
            path = [x_col] + ([color_col] if color_col else [])
            fig = px.treemap(df, path=path, values=y_col,
                             color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Sunburst":
            path = [x_col] + ([color_col] if color_col else [])
            fig = px.sunburst(df, path=path, values=y_col,
                              color_discrete_sequence=palette_colors if isinstance(palette_colors, list) else None)
        elif chart_type == "Heatmap (Pivot)":
            if cat_cols and num_cols:
                pivot_col = st.selectbox("Pivot Column", cat_cols)
                pivot_df = df.pivot_table(index=x_col, columns=pivot_col, values=y_col, aggfunc="mean")
                fig = px.imshow(pivot_df, text_auto=True, color_continuous_scale="Viridis", aspect="auto")

        if fig:
            apply_chart_theme(fig, f"{chart_type}: {y_col} by {x_col}")
            st.plotly_chart(fig, use_container_width=True)

            dl1, dl2 = st.columns(2)
            with dl1:
                html_str = fig.to_html(full_html=True, include_plotlyjs="cdn")
                st.download_button(
                    "⬇️ Download as HTML",
                    data=html_str,
                    file_name=f"{chart_type.lower()}_{x_col}_{y_col}.html",
                    mime="text/html",
                    use_container_width=True,
                )
            with dl2:
                try:
                    import kaleido  # noqa
                    img_bytes = fig.to_image(format="png", width=1200, height=600)
                    st.download_button(
                        "⬇️ Download as PNG",
                        data=img_bytes,
                        file_name=f"{chart_type.lower()}_{x_col}_{y_col}.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                except ImportError:
                    st.info("💡 PNG ke liye: pip install kaleido", icon="ℹ️")

    except Exception as e:
        st.error(f"Chart error: {e}. Try a different combination.")
