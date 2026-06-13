"""
AIDEOM-VN — AI-Driven Economic Decision Optimization Model for Vietnam
Web app giải 12 bài toán mô hình ra quyết định phát triển kinh tế VN 2020-2025.

Chạy:  streamlit run app.py
"""
import streamlit as st
from modules.common import inject_css, MUTED, ACCENT, TEXT

st.set_page_config(page_title="AIDEOM-VN — Mô hình ra quyết định",
                   page_icon="🇻🇳", layout="wide",
                   initial_sidebar_state="expanded")
inject_css()

from modules import (home, bai1, bai2, bai3, bai4, bai5, bai6,
                     bai7, bai8, bai9, bai10, bai11, bai12)

PAGES = {
    "🏠 Trang chủ": home,
    "🌱 Bài 1 — Cobb-Douglas + AI": bai1,
    "💰 Bài 2 — LP ngân sách số": bai2,
    "📊 Bài 3 — Priority 10 ngành": bai3,
    "🗺️ Bài 4 — LP ngành-vùng": bai4,
    "🧩 Bài 5 — MIP 15 dự án": bai5,
    "🏆 Bài 6 — TOPSIS 6 vùng": bai6,
    "🎯 Bài 7 — NSGA-II Pareto": bai7,
    "📈 Bài 8 — Động 2026-2035": bai8,
    "👷 Bài 9 — Lao động & AI": bai9,
    "🎲 Bài 10 — Stochastic SP": bai10,
    "🤖 Bài 11 — Q-learning RL": bai11,
    "🇻🇳 Bài 12 — AIDEOM tích hợp": bai12,
}

with st.sidebar:
    st.markdown(f"<h3 style='color:{ACCENT};margin-bottom:0'>🇻🇳 AIDEOM-VN</h3>"
                f"<p style='color:{MUTED};font-size:.78rem;margin-top:2px'>"
                "Mô hình ra quyết định phát triển kinh tế VN trong kỉ nguyên AI</p>",
                unsafe_allow_html=True)
    choice = st.radio("Mục lục", list(PAGES.keys()), label_visibility="collapsed")

    st.markdown("<hr style='border-color:#23262f'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='sb-name'>Họ và tên: Lê Trí Hiệp</div>"
        f"<div class='sb-meta'>Mã sinh viên: 23051240</div>"
        f"<div class='sb-meta'>Bài tập lớn: Các mô hình ra quyết định</div>",
        unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};font-size:.72rem;margin-top:14px'>"
                "Dữ liệu: GSO, MoST, MIC, MPI, WB, GII 2025</p>", unsafe_allow_html=True)

PAGES[choice].render()
