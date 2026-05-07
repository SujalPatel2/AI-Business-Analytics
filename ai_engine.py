import os
import streamlit as st
from groq import Groq
from utils import get_df_summary

MODEL = "llama-3.3-70b-versatile"

def get_client():
    api_key = st.session_state.get("groq_api_key", "")
    if not api_key:
        api_key = os.environ.get("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", "")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def ai_chat(df, user_question: str, history: list) -> str:
    client = get_client()
    if not client:
        return "⚠️ Please enter your Groq API key in the sidebar Settings to enable AI features."

    summary = get_df_summary(df)
    system_prompt = f"""You are an expert business data analyst and AI assistant.
The user has uploaded a dataset with the following characteristics:

{summary}

Your job:
- Answer questions about this data clearly and concisely
- Provide business insights, not just statistics
- Suggest visualizations when useful
- If a question is about a trend or anomaly (like "Why did sales decrease in March?"), 
  analyze the data context and give a smart, reasoned explanation
- Use bullet points, emojis, and clear formatting
- Always respond as a confident data analyst would

Keep responses focused and helpful. Never say you can't access the data — the summary above IS the data context.
"""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-6:]:  # last 3 turns
        messages.append(msg)
    messages.append({"role": "user", "content": user_question})

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=800,
            temperature=0.5,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ AI Error: {str(e)}"


def generate_insights(df) -> str:
    client = get_client()
    if not client:
        return "⚠️ Please enter your Groq API key in the sidebar Settings."

    summary = get_df_summary(df)
    prompt = f"""You are a senior business analyst generating an executive insights report.

Dataset Summary:
{summary}

Generate a comprehensive business intelligence report with:

1. 📊 **Executive Summary** (2-3 sentences)
2. 🔑 **Key Findings** (5+ bullet points with specific numbers)
3. ⚠️ **Risk Areas & Anomalies** (what looks concerning)
4. 💡 **Opportunities & Recommendations** (3-5 actionable items)
5. 📈 **Predicted Outlook** (what trends suggest for next period)

Be specific, data-driven, and use business language. Include actual numbers from the summary.
Format with clear headers and emojis for readability.
"""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"


def generate_column_insight(df, col: str) -> str:
    client = get_client()
    if not client:
        return "⚠️ API key required."
    s = df[col]
    stats = f"Column: {col}\nMin: {s.min()}, Max: {s.max()}, Mean: {s.mean():.2f}, Median: {s.median():.2f}, Std: {s.std():.2f}"
    if hasattr(s, "value_counts"):
        stats += f"\nTop values: {s.value_counts().head(5).to_dict()}"
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": f"As a business analyst, give 3 quick insights about this column in 4-5 lines:\n{stats}"
            }],
            max_tokens=200,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
