import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute(n):
    return core.bai11(n)


def render():
    page_header("CẤP ĐỘ KHÓ · BÀI 11",
                "🤖 Q-learning cho chính sách kinh tế thích nghi",
                "MDP 81 trạng thái · 5 hành động ngân sách · π* = argmax Q")
    n = st.select_slider("Số episode huấn luyện", [2000, 4000, 6000, 8000], value=6000)
    with st.spinner(f"Đang huấn luyện Q-learning ({n} episodes)…"):
        r = _compute(n)

    comp = r["comp"]
    best = max(comp, key=comp.get)
    stat_row([
        ("π* (Q-learning)", f"{comp['π* (Q-learning)']:.2f}", "phúc lợi tích lũy TB"),
        ("Tốt nhất", best, f"{comp[best]:.2f}"),
        ("π* hơn ngẫu nhiên", f"+{comp['π* (Q-learning)']-comp['Ngẫu nhiên']:.2f}", "cải thiện"),
    ])

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown("#### 11.3.4 — Learning curve")
        hist = np.array(r["hist"])
        w = 200
        sm = np.convolve(hist, np.ones(w)/w, mode="valid")
        f = fig([go.Scatter(y=sm, mode="lines", line=dict(color=ACCENT))],
                title="Phúc lợi tích lũy (trượt 200 ep)", xaxis_title="Episode")
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### So sánh chính sách")
        f = fig([go.Bar(x=list(comp.keys()), y=list(comp.values()), marker_color=ACCENT,
                        text=[f"{v:.1f}" for v in comp.values()], textposition="outside")],
                title="Phúc lợi TB theo chính sách")
        f.update_xaxes(tickangle=-25)
        st.plotly_chart(f, use_container_width=True)

    st.markdown("#### 11.3.3 — Chính sách tối ưu π*(s) tại các trạng thái")
    df = pd.DataFrame(r["policy"], columns=["Trạng thái khởi đầu", "π* (hành động chọn)"])
    st.dataframe(df, hide_index=True, use_container_width=True)

    policy_qa([
        ("a) GDP thấp, D thấp, U cao → π* chọn gì?",
         "Agent thường chọn hành động đẩy số hóa/cân bằng để tạo 'quick win' phục hồi tăng trưởng và "
         "giảm thất nghiệp."),
        ("b) GDP cao, AI cao, U thấp → π* chọn gì?",
         "Khi nền kinh tế đã mạnh, agent nghiêng về củng cố (consolidation) — cân bằng hoặc bao trùm để "
         "giữ ổn định, giảm rủi ro an ninh."),
        ("c) Tích hợp π* vào hoạch định mà không vi phạm nguyên tắc?",
         "Dùng π* như công cụ tư vấn/cảnh báo (decision-support), giữ quyết định cuối cùng cho hội đồng "
         "chính sách — AI hỗ trợ, không thay thế trách nhiệm chính trị."),
    ])
