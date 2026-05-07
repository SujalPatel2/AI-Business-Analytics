import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score
from utils import apply_chart_theme


def _estimate_freq(dt_index: pd.DatetimeIndex) -> str:
    if len(dt_index) < 2:
        return "MS"
    try:
        deltas = pd.Series(dt_index).diff().dropna()
        median_days = deltas.dt.days.median()
        if pd.isna(median_days):
            return "MS"
        median_days = float(median_days)
        if median_days <= 1:    return "D"
        elif median_days <= 8:  return "W"
        elif median_days <= 16: return "2W"
        elif median_days <= 35: return "MS"
        elif median_days <= 100: return "QS"
        else:                   return "YS"
    except Exception:
        return "MS"


def run_forecast(df: pd.DataFrame, date_col: str, value_col: str,
                 periods: int = 6, degree: int = 2):

    # ── Step 1: Copy & clean ─────────────────────────────────────────────────
    work = df[[date_col, value_col]].copy()

    # .astype(str) pehle — mixed types (int dates, strings) sab handle ho jaate hain
    work[date_col] = pd.to_datetime(work[date_col].astype(str), errors="coerce")

    # Value column ko numeric force karo — string values NaN ban jaayengi
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")

    # NaN rows drop karo
    work = work.dropna(subset=[date_col, value_col]).copy()

    if len(work) < 3:
        raise ValueError(
            f"Sirf {len(work)} valid rows mili. "
            "Sahi Date aur Value column select karo."
        )

    # ── Step 2: Aggregate duplicate dates ───────────────────────────────────
    work = (
        work
        .groupby(date_col, as_index=False)[value_col]
        .mean()
        .sort_values(date_col)
        .reset_index(drop=True)
    )
    # groupby ke baad dobara datetime enforce karo
    work[date_col] = pd.to_datetime(work[date_col])

    # ── Step 3: X aur y arrays ───────────────────────────────────────────────
    X = np.arange(len(work), dtype=float).reshape(-1, 1)
    y = work[value_col].values.astype(float)

    # ── Step 4: Model fit ────────────────────────────────────────────────────
    poly  = PolynomialFeatures(degree=degree, include_bias=False)
    Xp    = poly.fit_transform(X)
    model = LinearRegression().fit(Xp, y)
    y_pred = model.predict(Xp)

    # ── Step 5: Metrics ──────────────────────────────────────────────────────
    r2       = float(r2_score(y, y_pred))
    std_res  = float(np.std(y - y_pred))

    try:
        from sklearn.metrics import mean_absolute_percentage_error
        mape = float(mean_absolute_percentage_error(y, y_pred) * 100)
    except Exception:
        mape = None

    # ── Step 6: Future X ─────────────────────────────────────────────────────
    future_X  = np.arange(len(work), len(work) + periods, dtype=float).reshape(-1, 1)
    future_Xp = poly.transform(future_X)
    future_y  = model.predict(future_Xp).astype(float)

    # ── Step 7: Future dates ──────────────────────────────────────────────────
    dt_index = pd.DatetimeIndex(work[date_col])
    last_date = dt_index[-1]

    # Pehle infer_freq try karo
    freq = None
    try:
        freq = pd.infer_freq(dt_index)
    except Exception:
        pass

    # Nahi mila toh estimate karo
    if not freq:
        freq = _estimate_freq(dt_index)

    # Future dates generate karo
    try:
        future_dates = pd.date_range(
            start=last_date, periods=periods + 1, freq=freq
        )[1:]
    except Exception:
        # Last fallback: median delta use karo
        try:
            delta = int(pd.Series(dt_index).diff().dt.days.dropna().median())
        except Exception:
            delta = 30
        future_dates = pd.DatetimeIndex([
            last_date + pd.Timedelta(days=delta * (i + 1))
            for i in range(periods)
        ])

    # ── Step 8: Confidence interval ───────────────────────────────────────────
    upper = (future_y + 1.96 * std_res).astype(float)
    lower = (future_y - 1.96 * std_res).astype(float)

    # ── Step 9: Figure ────────────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=work[date_col], y=y,
        mode="lines+markers", name="Actual",
        line=dict(color="#6C63FF", width=2.5),
        marker=dict(size=5),
    ))

    fig.add_trace(go.Scatter(
        x=work[date_col], y=y_pred,
        mode="lines", name="Trend Fit",
        line=dict(color="#3ECFCF", width=1.5, dash="dot"),
    ))

    fig.add_trace(go.Scatter(
        x=list(future_dates), y=list(future_y),
        mode="lines+markers", name="Forecast",
        line=dict(color="#FFD166", width=2.5, dash="dash"),
        marker=dict(size=8, symbol="diamond"),
    ))

    fig.add_trace(go.Scatter(
        x=list(future_dates) + list(future_dates[::-1]),
        y=list(upper) + list(lower[::-1]),
        fill="toself",
        fillcolor="rgba(255, 209, 102, 0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        name="95% Confidence",
        showlegend=True,
        hoverinfo="skip",
    ))

    try:
        fig.add_vline(
            x=str(last_date), line_dash="dot",
            line_color="rgba(255,255,255,0.3)",
            annotation_text="Forecast Start",
            annotation_font=dict(color="#aaa", size=11),
        )
    except Exception:
        pass

    apply_chart_theme(fig, f"📈 {value_col} — Trend & {periods}-Period Forecast")

    # ── Step 10: Output ───────────────────────────────────────────────────────
    forecast_df = pd.DataFrame({
        "Date": future_dates.strftime("%Y-%m-%d"),
        f"Predicted_{value_col}": np.round(future_y, 2),
        "Lower_CI (95%)": np.round(lower, 2),
        "Upper_CI (95%)": np.round(upper, 2),
    })

    metrics = {
        "R² Score": round(r2, 4),
        "MAPE": f"{round(mape,2)}%" if mape is not None else "N/A",
        "Std Residual": round(std_res, 2),
        "Model": f"Poly deg={degree}",
        "Freq": str(freq),
    }

    return fig, metrics, forecast_df


def moving_average_chart(df: pd.DataFrame, date_col: str,
                         value_col: str, windows=(7, 30)):
    work = df[[date_col, value_col]].copy()
    work[date_col] = pd.to_datetime(work[date_col].astype(str), errors="coerce")
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna().sort_values(date_col)
    work = work.groupby(date_col, as_index=False)[value_col].mean()
    work[date_col] = pd.to_datetime(work[date_col])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=work[date_col], y=work[value_col].astype(float),
        mode="lines", name="Raw", opacity=0.35,
        line=dict(color="#6C63FF", width=1),
    ))

    colors = ["#3ECFCF", "#FFD166"]
    for w, c in zip(windows, colors):
        if len(work) > w:
            ma = work[value_col].astype(float).rolling(window=w, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=work[date_col], y=ma,
                mode="lines", name=f"MA-{w}",
                line=dict(color=c, width=2),
            ))

    apply_chart_theme(fig, f"Moving Average — {value_col}")
    return fig
