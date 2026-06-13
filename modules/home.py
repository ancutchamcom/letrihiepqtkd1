import streamlit as st
import pandas as pd
from modules import core
from modules.common import page_header, stat_row, fig, MUTED, ACCENT
import plotly.graph_objects as go


def render():
    st.markdown("# 🇻🇳 AIDEOM-VN")
    st.markdown("### *AI-Driven Economic Decision Optimization Model for Vietnam*")
    st.markdown(f"<p style='color:{MUTED}'>Web app giải <b>12 bài toán mô hình ra quyết định</b> "
                "phát triển kinh tế Việt Nam trong kỉ nguyên AI — dữ liệu thực 2020–2025.</p>",
                unsafe_allow_html=True)

    macro = core.load_macro()
    r25 = macro[macro.year == 2025].iloc[0]
    stat_row([
        ("GDP 2025", f"{r25.GDP_billion_USD:,.1f} tỷ USD", "↑ +8,02%"),
        ("Kinh tế số / GDP", f"≈{r25.digital_economy_share_GDP_pct:.1f}%", "↑ +1,2 đpt"),
        ("FDI giải ngân 2025", f"{r25.FDI_disbursed_billion_USD:,.1f} tỷ USD", "↑ +8,9%"),
        ("GDP/người 2025", f"{r25.GDP_per_capita_USD:,.0f} USD", "↑ +6,9%"),
    ])

    st.markdown("---")
    st.markdown("## 📚 12 bài toán theo 4 cấp độ")
    tiers = {
        "🟢 Cấp độ DỄ — Làm quen mô hình": [
            ("Bài 1", "Hàm sản xuất Cobb-Douglas mở rộng + AI — growth accounting, dự báo GDP 2030"),
            ("Bài 2", "LP phân bổ ngân sách 4 hạng mục — scipy.optimize, shadow price"),
            ("Bài 3", "Chỉ số ưu tiên 10 ngành — min-max norm, weighted scoring, sensitivity")],
        "🟡 Cấp độ TRUNG BÌNH — Tối ưu cổ điển": [
            ("Bài 4", "LP phân bổ ngân sách ngành-vùng (PuLP/CVXPY), ràng buộc công bằng vùng"),
            ("Bài 5", "MIP lựa chọn 15 dự án — knapsack, ràng buộc loại trừ & tiên quyết"),
            ("Bài 6", "TOPSIS xếp hạng 6 vùng — Entropy weight, AHP, sensitivity")],
        "🟠 Cấp độ KHÁ KHÓ — Tối ưu nâng cao": [
            ("Bài 7", "NSGA-II Pareto 4 mục tiêu — TOPSIS chọn nghiệm thỏa hiệp"),
            ("Bài 8", "Tối ưu động liên thời gian 2026-2035 — SLSQP, dynamics vốn"),
            ("Bài 9", "Tác động AI tới thị trường lao động — LP NetJob ròng")],
        "🔴 Cấp độ KHÓ — Bất định & học tăng cường": [
            ("Bài 10", "Stochastic programming 2 giai đoạn — VSS, EVPI (Pyomo)"),
            ("Bài 11", "Q-learning chính sách kinh tế thích nghi — MDP, π*"),
            ("Bài 12", "Đồ án tích hợp AIDEOM-VN — 6 module, 5 kịch bản")],
    }
    for tier, rows in tiers.items():
        with st.expander(tier, expanded=tier.startswith("🟢")):
            for code, desc in rows:
                st.markdown(f"**{code}** — {desc}")

    st.markdown("---")
    st.markdown("## 📊 Dữ liệu gốc")
    t1, t2, t3 = st.tabs(["Vĩ mô 2020–2025", "10 ngành 2024", "6 vùng 2024"])
    with t1:
        st.caption("vietnam_macro_2020_2025.csv — GDP, cơ cấu khu vực, FDI, XNK, kinh tế số")
        st.dataframe(macro, use_container_width=True, hide_index=True)
        f = fig([go.Scatter(x=macro.year, y=macro.GDP_trillion_VND, mode="lines+markers",
                            name="GDP (nghìn tỷ)", line=dict(color=ACCENT, width=3))],
                title="GDP Việt Nam 2020–2025 (nghìn tỷ VND)")
        st.plotly_chart(f, use_container_width=True)
    with t2:
        st.caption("vietnam_sectors_2024.csv — tỷ trọng GDP, AI readiness, rủi ro tự động hóa, R&D")
        st.dataframe(core.load_sectors(), use_container_width=True, hide_index=True)
    with t3:
        st.caption("vietnam_regions_2024.csv — GRDP, AI readiness, lao động đào tạo, Gini")
        st.dataframe(core.load_regions(), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"<p style='color:{MUTED};font-size:.8rem'>Neo chính sách: Nghị quyết 57-NQ/TW · "
                "QĐ 749/127/411/QĐ-TTg · Dữ liệu: GSO, MoST, MIC, MPI, World Bank, GII 2025</p>",
                unsafe_allow_html=True)
