import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai1()


def render():
    page_header("CẤP ĐỘ DỄ · BÀI 1",
                "🌱 Hàm sản xuất Cobb-Douglas mở rộng + AI",
                "Ước lượng TFP, phân rã tăng trưởng (Δln) và dự báo GDP 2030")
    r = _compute()

    stat_row([
        ("MAPE (Cobb-Douglas)", f"{r['MAPE']:.2f}%", "độ chính xác rất tốt (<5–10%)"),
        ("Ā (TFP trung bình)", f"{r['A_mean']:.4f}", "2020–2025"),
        ("GDP 2030 dự báo", f"{r['Y30']:,.0f} ngh.tỷ", f"CAGR {r['cagr']:.2f}%/năm"),
    ])

    st.markdown("#### 1.4.1 — Năng suất nhân tố tổng hợp (TFP) A_t")
    f1 = fig([go.Scatter(x=r["years"], y=r["A"], mode="lines+markers",
                         line=dict(color=ACCENT, width=3), name="A_t")],
             title="TFP A_t — Việt Nam 2020–2025", xaxis_title="Năm", yaxis_title="A_t")
    st.plotly_chart(f1, use_container_width=True)
    st.caption("TFP tăng đều từ ~27,7 (2020) lên ~34,9 (2025) → chất lượng tăng trưởng cải thiện.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 1.4.2 — Dự báo Ŷ vs GDP thực")
        f2 = fig([go.Bar(x=r["years"], y=r["Y"], name="Y thực", marker_color="#62d7c0"),
                  go.Bar(x=r["years"], y=r["Y_hat"], name="Ŷ dự báo", marker_color=ACCENT)],
                 barmode="group", title=f"MAPE = {r['MAPE']:.2f}%")
        st.plotly_chart(f2, use_container_width=True)
    with c2:
        st.markdown("#### 1.4.3 — Phân rã đóng góp tăng trưởng")
        sh = r["shares"]
        order = sorted(sh, key=sh.get, reverse=True)
        f3 = fig([go.Bar(x=[sh[k] for k in order], y=order, orientation="h",
                         marker_color=ACCENT)],
                 title="Tỷ trọng đóng góp bình quân (%)")
        st.plotly_chart(f3, use_container_width=True)

    st.markdown("##### Bảng phân rã theo năm (điểm % tăng trưởng GDP)")
    st.dataframe(r["decomp"], use_container_width=True, hide_index=True)

    st.markdown(f"#### 1.4.4 — Dự báo GDP 2030: **{r['Y30']:,.0f} nghìn tỷ VND**")
    st.caption("Kịch bản: D=30%, AI=100K DN, H=35%, K&L +6%/năm, TFP +1,2%/năm.")

    policy_qa([
        ("a) TFP tăng hay giảm?",
         "TFP tăng liên tục (~+1,4/năm), bước nhảy lớn 2021→2022 phản ánh phục hồi sau COVID và "
         "đẩy mạnh chuyển đổi số — tăng trưởng dần dựa vào hiệu quả tổng hợp, không chỉ tích lũy vốn."),
        ("b) Yếu tố mới nào (D, AI, H) đóng góp nhiều nhất?",
         "Số hóa D đóng góp lớn nhất trong nhóm yếu tố mới nhờ tốc độ tăng nhanh của tỷ trọng kinh tế số; "
         "tuy nhiên K và TFP vẫn là động lực chính của tăng trưởng."),
        ("c) Mục tiêu 30% kinh tế số/GDP 2030 có khả thi?",
         "Khả thi nếu duy trì đầu tư số và H song hành; mô hình cho thấy cần ràng buộc tăng tốc D "
         "(~+11 đpt trong 5 năm) đi kèm nâng vốn nhân lực số H."),
    ])
