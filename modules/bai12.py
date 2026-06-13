import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT, MUTED


@st.cache_data(show_spinner=False)
def _m1():
    return core.bai12_m1()


@st.cache_data(show_spinner=False)
def _m2():
    return core.bai6()


@st.cache_data(show_spinner=False)
def _m3():
    return core.bai4()


@st.cache_data(show_spinner=False)
def _m4():
    return core.bai9()


@st.cache_data(show_spinner=False)
def _m5():
    return core.bai7(), core.bai10()


def render():
    page_header("CẤP ĐỘ KHÓ · BÀI 12 — ĐỒ ÁN TÍCH HỢP",
                "🇻🇳 AIDEOM-VN — Nguyên mẫu tích hợp 6 module",
                "Tích hợp Bài 1–11 thành hệ hỗ trợ ra quyết định · 5 kịch bản chính sách")

    years, fc = _m1()
    r25 = core.load_macro().iloc[-1]
    stat_row([
        ("GDP 2025 nền", f"{r25.GDP_trillion_VND:,.0f} ngh.tỷ", "điểm xuất phát"),
        ("Kịch bản tốt nhất 2030", "S5 Tối ưu", f"{fc['S5 Tối ưu cân bằng'][-1]:,.0f} ngh.tỷ"),
        ("Số module tích hợp", "6", "M1 → M6"),
    ])

    st.markdown("<p style='color:%s'>Sáu module được tổ chức thành <b>4 tab</b>: "
                "<b>Tổng quan (M1–M2)</b> · <b>Phân bổ (M3)</b> · <b>5 Kịch bản (M6)</b> · "
                "<b>Cảnh báo rủi ro (M4–M5)</b>.</p>" % MUTED, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Tổng quan (M1–M2)", "🎯 Phân bổ (M3)",
        "📋 5 Kịch bản (M6)", "⚠️ Cảnh báo rủi ro (M4–M5)"])

    # ---- TAB 1: M1 + M2 ----
    with tab1:
        st.markdown("### M1 — Dự báo kinh tế (Cobb-Douglas) 2026–2030")
        f = fig([go.Scatter(x=years, y=traj, mode="lines+markers", name=name)
                 for name, traj in fc.items()],
                title="GDP dự báo theo 5 kịch bản (nghìn tỷ VND)", xaxis_title="Năm")
        st.plotly_chart(f, use_container_width=True)
        df1 = pd.DataFrame(fc, index=years).T
        df1.columns = [str(y) for y in years]
        st.dataframe(df1.round(0), use_container_width=True)

        st.markdown("### M2 — Đánh giá sẵn sàng số (TOPSIS + Entropy)")
        m2 = _m2()
        short = ["NMM", "RRD", "NCC", "CH", "SE", "MD"]
        f = fig([go.Bar(x=short, y=m2["C_exp"], name="Expert", marker_color=ACCENT),
                 go.Bar(x=short, y=m2["C_ent"], name="Entropy", marker_color="#62d7c0")],
                barmode="group", title="Chỉ số sẵn sàng AI 6 vùng (C*)")
        st.plotly_chart(f, use_container_width=True)

    # ---- TAB 2: M3 ----
    with tab2:
        st.markdown("### M3 — Tối ưu phân bổ ngành–vùng (LP) + Dynamic")
        m3 = _m3()
        regs = [core.REGION_NAMES[x] for x in core.REGIONS]
        st.metric("LP Z* (có ràng buộc công bằng C5)", f"{m3['z_c5']:,.0f} tỷ VND")
        f = fig([go.Heatmap(z=m3["mat_c5"], x=core.ITEMS, y=regs, colorscale="Reds",
                            text=m3["mat_c5"].round(0), texttemplate="%{text}")],
                title="Phân bổ tối ưu x_{j,r} (tỷ VND)", height=420)
        st.plotly_chart(f, use_container_width=True)
        st.caption(f"Chi phí kinh tế của công bằng vùng = {m3['equity_cost']:,.0f} tỷ VND "
                   f"({m3['equity_cost']/m3['z_no']*100:.2f}%). Liên kết động: phân bổ này nâng TFP nội "
                   "sinh ~3,2%/năm qua tích lũy D, AI, H (mô hình Bài 8).")

    # ---- TAB 3: M6 — 5 scenarios ----
    with tab3:
        st.markdown("### M6 — Dashboard so sánh 5 kịch bản chính sách 2030")
        kpi = pd.DataFrame({
            "Kịch bản": list(fc.keys()),
            "GDP 2030 (ngh.tỷ)": [round(v[-1], 0) for v in fc.values()],
            "Tăng so 2026 (%)": [round((v[-1]/v[0]-1)*100, 1) for v in fc.values()]})
        kpi = kpi.sort_values("GDP 2030 (ngh.tỷ)", ascending=False)
        st.dataframe(kpi, hide_index=True, use_container_width=True)
        f = fig([go.Bar(x=kpi["Kịch bản"], y=kpi["GDP 2030 (ngh.tỷ)"], marker_color=ACCENT,
                        text=kpi["GDP 2030 (ngh.tỷ)"], textposition="outside")],
                title="GDP 2030 theo kịch bản chính sách")
        f.update_xaxes(tickangle=-15)
        st.plotly_chart(f, use_container_width=True)
        st.success("Kịch bản **S5 Tối ưu cân bằng** (25% K · 25% D · 30% AI · 20% H) cho GDP 2030 cao "
                   "nhất, cân bằng giữa số hóa nhanh và bao trùm — là khuyến nghị của mô hình AIDEOM-VN.")

    # ---- TAB 4: M4 + M5 ----
    with tab4:
        st.markdown("### M4 — Mô phỏng thị trường lao động (NetJob)")
        m4 = _m4()
        st.metric("Tổng NetJob ròng", f"{m4['total_netjob']:,.0f} việc làm")
        f = fig([go.Bar(x=m4["sectors"], y=m4["NetJob"], marker_color=ACCENT)],
                title="NetJob ròng theo ngành")
        f.update_xaxes(tickangle=-35)
        st.plotly_chart(f, use_container_width=True)

        st.markdown("### M5 — Đánh giá rủi ro (đa mục tiêu + ngẫu nhiên)")
        with st.spinner("Đang tính M5 (NSGA-II + SP)…"):
            m7, m10 = _m5()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Rủi ro môi trường & an ninh (Pareto)**")
            f = fig([go.Scatter(x=m7["CO2"], y=m7["Sec"], mode="markers",
                                marker=dict(color=m7["GDP"], colorscale="Plasma", size=6))],
                    title="CO₂ vs Rủi ro an ninh", xaxis_title="Phát thải CO₂",
                    yaxis_title="Rủi ro an ninh")
            st.plotly_chart(f, use_container_width=True)
        with c2:
            st.markdown("**Rủi ro bất định (VSS/EVPI)**")
            st.metric("VSS", f"{m10['VSS']:,.0f}")
            st.metric("EVPI", f"{m10['EVPI']:,.0f}")
            st.caption("Cảnh báo: nền kinh tế độ mở cao → cần dự phòng ngân sách và đầu tư nhân lực số như "
                       "lớp bảo hiểm trước cú sốc toàn cầu.")

    policy_qa([
        ("Khuyến nghị chính sách tổng hợp của AIDEOM-VN?",
         "Theo đuổi kịch bản cân bằng (S5): đẩy số hóa & AI nhưng giữ tỷ trọng nhân lực số ~20% và ràng "
         "buộc công bằng vùng miền — tối đa GDP 2030 mà vẫn bao trùm, bám Nghị quyết 57-NQ/TW."),
        ("Hạn chế & hướng mở rộng?",
         "Mô hình SP đơn giản hóa cho VSS≈0; hướng phát triển: CGE/DSGE-AI, dữ liệu thời gian thực, và "
         "Multi-Agent RL theo bộ-ngành."),
    ])
