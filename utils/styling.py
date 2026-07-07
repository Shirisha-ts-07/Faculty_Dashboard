"""
styling.py
----------------
Centralised CSS + small UI helpers so app.py isn't cluttered with
raw HTML strings. Gives the dashboard a clean, "professional SaaS"
look rather than default Streamlit styling.
"""

import streamlit as st

PRIMARY = "#2E5CE6"
SUCCESS = "#1FA97C"
DANGER = "#E45858"
NEUTRAL_BG = "#F7F9FC"
TEXT_MUTED = "#6B7280"


def inject_global_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {NEUTRAL_BG};
        }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        /* KPI card */
        .kpi-card {{
            background: white;
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 4px rgba(16, 24, 40, 0.08);
            border: 1px solid #EEF1F6;
            height: 100%;
        }}
        .kpi-label {{
            font-size: 0.80rem;
            font-weight: 600;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 0.35rem;
        }}
        .kpi-value {{
            font-size: 1.9rem;
            font-weight: 700;
            color: #111827;
            line-height: 1.1;
        }}
        .kpi-sub {{
            font-size: 0.78rem;
            color: {TEXT_MUTED};
            margin-top: 0.25rem;
        }}
        .section-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #111827;
            margin: 1.2rem 0 0.6rem 0;
            border-left: 4px solid {PRIMARY};
            padding-left: 0.6rem;
        }}
        h1 {{
            font-weight: 800 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str = "", color: str = "#111827"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value" style="color:{color};">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f"<div class='section-title'>{text}</div>", unsafe_allow_html=True)
