# 🤖 AI Business Analytics Assistant

> An AI-powered, full-featured business analytics web app built with Streamlit + Groq AI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📂 **Data Upload** | Upload CSV / Excel files or use 3 built-in sample datasets |
| 📊 **Auto Dashboard** | 8+ charts auto-generated: bar, line, pie, scatter, box, heatmap, sunburst |
| 💬 **AI Chat** | Ask plain-English questions like "Why did sales drop in March?" |
| 🔍 **AI Insights** | Auto-generate executive-level business intelligence reports |
| 📈 **Trend Predictor** | Polynomial regression ML forecast with 95% confidence bands |
| 🎨 **Custom Chart Builder** | Build 15+ chart types with any columns, aggregations, palettes |
| 🧹 **Data Cleaner** | Handle missing values, duplicates, filter, and export cleaned data |
| 📋 **Raw Data Explorer** | Search, filter, view stats, and download |
| 🔐 **Auth System** | Login/Signup with bcrypt-hashed passwords |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Login
- Demo account: **username:** `demo` | **password:** `demo123`
- Or create a new account via Sign Up

### 4. Enable AI Features
- Go to sidebar → Settings → Enter your **Groq API key**
- Get a free key at: https://console.groq.com
- AI Model used: `llama-3.3-70b-versatile` (free, fast, powerful)

---

## 📁 Project Structure

```
AI_Business_Analytics/
├── app.py              # Main Streamlit app & all tabs
├── auth.py             # Login / Signup system (bcrypt)
├── dashboard.py        # Auto-dashboard (8+ charts)
├── ai_engine.py        # Groq AI chat + insights
├── predictor.py        # ML trend forecasting
├── custom_charts.py    # Custom chart builder (15 chart types)
├── data_cleaner.py     # Data quality & cleaning tools
├── sample_data.py      # 3 realistic sample datasets
├── utils.py            # Shared helpers, themes, KPI cards
├── requirements.txt    # Python dependencies
└── .streamlit/
    └── config.toml     # Dark theme config
```

---

## 🛠 Tech Stack

- **Python** — Core language
- **Streamlit** — Web framework
- **Pandas** — Data manipulation
- **Plotly** — Interactive charts
- **Scikit-learn** — ML forecasting
- **Groq + LLaMA 3.3** — AI insights & chat
- **Bcrypt** — Secure password hashing

---

## 🌐 Deploy to Streamlit Cloud

1. Push to GitHub:
```bash
git init
git add .
git commit -m "AI Business Analytics App"
git remote add origin https://github.com/YOUR_USERNAME/AI-Business-Analytics.git
git push -u origin main
```

2. Go to https://share.streamlit.io
3. Connect your repo → set main file as `app.py`
4. Add `GROQ_API_KEY` in Secrets settings

---

## 💡 Example Questions to Ask AI

- *"Why did sales decrease in March?"*
- *"What is the best performing product category?"*
- *"Which region has the highest profit margin?"*
- *"Are there any seasonal trends in this data?"*
- *"What are the key risk areas I should focus on?"*

---

Built with ❤️ using Streamlit + Groq AI
