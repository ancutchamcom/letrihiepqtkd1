"""Giao diện dùng chung: theme tối, accent crimson/pink, stat card, helper Plotly."""
import streamlit as st
import plotly.graph_objects as go

ACCENT = "#ff4d6d"
ACCENT2 = "#ff8fa3"
BG = "#0e1117"
CARD = "#1a1d27"
TEXT = "#e6e6e6"
MUTED = "#9aa0aa"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT, family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=["#62d7c0", "#fff3a3", "#9aa0aa", "#ff8fa3", "#7fb3ff", "#ffb86b"],
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def inject_css():
    st.markdown(f"""
    <style>
    .stApp {{ background:{BG}; }}
    section[data-testid="stSidebar"] {{ background:#13151c; border-right:1px solid #23262f; }}
    h1,h2,h3,h4 {{ color:{TEXT}; }}
    .big-accent {{ color:{ACCENT}; font-weight:800; font-size:2.1rem; line-height:1.1; }}
    .stat-label {{ color:{MUTED}; font-size:.8rem; letter-spacing:.04em; text-transform:uppercase; }}
    .stat-card {{ background:{CARD}; border:1px solid #23262f; border-radius:14px;
                  padding:16px 18px; }}
    .pill {{ display:inline-block; background:rgba(255,77,109,.16); color:{ACCENT2};
             padding:3px 10px; border-radius:999px; font-size:.72rem; font-weight:600;
             border:1px solid rgba(255,77,109,.3); }}
    .sb-name {{ color:{TEXT}; font-size:.86rem; font-weight:600; }}
    .sb-meta {{ color:{MUTED}; font-size:.78rem; }}
    .qa {{ background:{CARD}; border-left:3px solid {ACCENT}; border-radius:8px;
           padding:12px 16px; margin:8px 0; color:{TEXT}; }}
    .qa b {{ color:{ACCENT2}; }}
    div[data-testid="stMetricValue"] {{ color:{ACCENT}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap:6px; }}
    .stTabs [data-baseweb="tab"] {{ background:{CARD}; border-radius:8px 8px 0 0;
            padding:8px 16px; }}
    .stTabs [aria-selected="true"] {{ background:rgba(255,77,109,.18); }}
    </style>
    """, unsafe_allow_html=True)


def page_header(badge, title, subtitle):
    st.markdown(f"<span class='pill'>{badge}</span>", unsafe_allow_html=True)
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<p style='color:{MUTED};margin-top:-8px'>{subtitle}</p>",
                    unsafe_allow_html=True)


def stat_row(items):
    cols = st.columns(len(items))
    for c, (label, value, sub) in zip(cols, items):
        with c:
            st.markdown(
                f"<div class='stat-card'><div class='stat-label'>{label}</div>"
                f"<div class='big-accent'>{value}</div>"
                f"<div style='color:{MUTED};font-size:.78rem'>{sub or ''}</div></div>",
                unsafe_allow_html=True)


def policy_qa(items):
    st.markdown("#### 💬 Thảo luận chính sách")
    for q, a in items:
        st.markdown(f"<div class='qa'><b>{q}</b><br>{a}</div>", unsafe_allow_html=True)


def fig(traces, **layout):
    f = go.Figure(traces)
    lay = dict(PLOTLY_LAYOUT)
    lay.update(layout)
    f.update_layout(**lay)
    f.update_xaxes(gridcolor="#23262f", zerolinecolor="#23262f")
    f.update_yaxes(gridcolor="#23262f", zerolinecolor="#23262f")
    return f
