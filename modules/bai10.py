import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai10()


def render():
    page_header("CẤP ĐỘ KHÓ · BÀI 10",
                "🎲 Quy hoạch ngẫu nhiên hai giai đoạn",
                "Pyomo · here-and-now vs recourse · VSS & EVPI")
    with st.spinner("Đang giải mô hình SP (Pyomo)…"):
        r = _compute()

    stat_row([
        ("Z*_SP (Stochastic)", f"{r['Z_SP']:,.0f}", "tỷ VND GDP gain"),
        ("VSS", f"{r['VSS']:,.0f}", "giá trị tư duy xác suất"),
        ("EVPI", f"{r['EVPI']:,.0f}", "giá trị thông tin hoàn hảo"),
    ])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 10.5.1 — Quyết định first-stage (here-and-now)")
        f = fig([go.Bar(x=r["J"], y=[r["x_sp"][j] for j in r["J"]], name="SP",
                        marker_color=ACCENT),
                 go.Bar(x=r["J"], y=[r["x_ev"][j] for j in r["J"]], name="EV",
                        marker_color="#62d7c0")],
                barmode="group", title="SP vs EV (nghìn tỷ VND)")
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### 10.5.2 — Lời giải xác định từng kịch bản")
        df = pd.DataFrame({"Kịch bản": list(r["det"].keys()),
                           "Xác suất": [r["p_s"][s] for s in r["det"]],
                           "Z* (Wait&See)": [round(v, 0) for v in r["det"].values()]})
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.metric("Z_WS (Wait & See)", f"{r['Z_WS']:,.0f}")

    st.markdown("#### 10.5.3 — VSS & EVPI")
    f = fig([go.Bar(x=["Z_EV", "Z_SP", "Z_WS"],
                    y=[r["Z_EV"], r["Z_SP"], r["Z_WS"]], marker_color=ACCENT,
                    text=[f"{v:,.0f}" for v in [r["Z_EV"], r["Z_SP"], r["Z_WS"]]],
                    textposition="outside")],
            title="Z_EV ≤ Z_SP ≤ Z_WS")
    st.plotly_chart(f, use_container_width=True)
    st.info(f"VSS = Z_SP − Z_EV = {r['VSS']:,.0f} · EVPI = Z_WS − Z_SP = {r['EVPI']:,.0f}. "
            "Trong mô hình đơn giản hóa này, do hệ số β tuyến tính và phần dự phòng cố định, "
            "quyết định first-stage trùng giữa SP và EV → VSS, EVPI ≈ 0. Để VSS dương cần thêm hàm "
            "phạt phi tuyến và ràng buộc liên giai đoạn chặt hơn (lưu ý sư phạm của đề bài).")

    policy_qa([
        ("a) SP đầu tư H nhiều hơn hay ít hơn xác định?",
         "SP có xu hướng giữ H cao hơn vì lao động qua đào tạo hấp thụ cú sốc tốt (β_H cao trong kịch bản "
         "khủng hoảng) — H như 'bảo hiểm'."),
        ("b) VSS dương nói lên điều gì?",
         "Khi VSS>0, cân nhắc bất định mang lại giá trị thực — tư duy xác suất giúp chính sách bền vững "
         "hơn ra quyết định theo giá trị kỳ vọng đơn thuần."),
        ("c) Bài học từ COVID-19 & bão Yagi?",
         "Các cú sốc thực tế cho thấy VN có thể đang 'dưới đầu tư' vào nhân lực số — một hàng hóa bảo "
         "hiểm trước bất định toàn cầu."),
    ])
