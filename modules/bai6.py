import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai6()


def render():
    page_header("CẤP ĐỘ TRUNG BÌNH · BÀI 6",
                "🏆 TOPSIS xếp hạng 6 vùng theo sẵn sàng AI",
                "Chuẩn hóa vector · trọng số Entropy · phân tích độ nhạy")
    r = _compute()
    res = r["res"].sort_values("Hạng_Expert")
    short = ["NMM", "RRD", "NCC", "CH", "SE", "MD"]

    top = res.iloc[0]["Vùng"]
    stat_row([
        ("Vùng dẫn đầu (Expert)", top, f"C* = {res.iloc[0]['C*_Expert']:.3f}"),
        ("Vùng hạng 2", res.iloc[1]["Vùng"], f"C* = {res.iloc[1]['C*_Expert']:.3f}"),
        ("Top-3 ổn định", "✓ khi w_AI 0.10→0.40", "kết quả bền vững"),
    ])

    st.markdown("#### 6.4.1 & 6.4.2 — TOPSIS Expert vs Entropy")
    f = fig([go.Bar(x=short, y=r["C_exp"], name="Expert", marker_color=ACCENT),
             go.Bar(x=short, y=r["C_ent"], name="Entropy", marker_color="#62d7c0")],
            barmode="group", title="Điểm gần gũi C* theo hai bộ trọng số")
    st.plotly_chart(f, use_container_width=True)
    st.dataframe(res, hide_index=True, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Trọng số Expert vs Entropy")
        crit = ["GRDP/cap", "FDI", "Digital", "AI-Ready", "Trained", "R&D", "Internet", "Gini"]
        f = fig([go.Bar(x=crit, y=r["w_exp"], name="Expert", marker_color=ACCENT),
                 go.Bar(x=crit, y=r["w_ent"], name="Entropy", marker_color="#62d7c0")],
                barmode="group", title="So sánh trọng số")
        f.update_xaxes(tickangle=-30)
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### 6.4.3 — Độ nhạy theo w_AI")
        traces = [go.Scatter(x=r["a_range"], y=r["sens"][:, i], mode="lines", name=short[i])
                  for i in range(6)]
        f = fig(traces, title="C* theo w_AI (0.10 → 0.40)", xaxis_title="w_AI")
        st.plotly_chart(f, use_container_width=True)

    policy_qa([
        ("a) Vùng nào triển khai TT AI quốc gia đầu tiên?",
         f"{top} dẫn đầu nhất quán nhờ AI-readiness, Digital và R&D vượt trội — là lựa chọn hợp lý cho "
         "trung tâm AI quốc gia đầu tiên."),
        ("b) Vùng thay đổi hạng lớn nhất khi dùng Entropy?",
         "Entropy đề cao FDI & GRDP/capita (phân kỳ dữ liệu lớn), khiến một số vùng giữa bảng đảo nhẹ; "
         "Top-2 (SE, RRD) vẫn ổn định."),
        ("c) AI-Readiness & Internet tương quan cao thì sao?",
         "Đa cộng tuyến làm TOPSIS đếm trùng thông tin; nên gộp/giảm chiều (PCA) hoặc dùng trọng số "
         "Entropy để giảm thiên lệch."),
        ("d) Chọn 3 vùng xây TT AI theo QĐ 127/QĐ-TTg?",
         "Đông Nam Bộ, ĐB sông Hồng và Bắc&Nam Trung Bộ — cân bằng năng lực số và phân bố địa lý 3 miền."),
    ])
