import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai3()


def render():
    page_header("CẤP ĐỘ DỄ · BÀI 3",
                "📊 Chỉ số ưu tiên 10 ngành",
                "Chuẩn hóa min-max · weighted scoring · sensitivity")
    r = _compute()
    rank = r["rank"]
    top3 = list(rank["sector_name_en"][:3])

    stat_row([
        ("Hạng 1", top3[0], f"Priority {rank['Priority'].iloc[0]:.3f}"),
        ("Hạng 2", top3[1], f"Priority {rank['Priority'].iloc[1]:.3f}"),
        ("Hạng 3", top3[2], f"Priority {rank['Priority'].iloc[2]:.3f}"),
    ])

    st.markdown("#### 3.4.2 — Xếp hạng 10 ngành (trọng số mặc định)")
    f = fig([go.Bar(x=rank["Priority"][::-1], y=rank["sector_name_en"][::-1],
                    orientation="h",
                    marker_color=[ACCENT if s in top3 else "#62d7c0" for s in rank["sector_name_en"][::-1]])],
            title="Priority Score theo ngành", height=420)
    st.plotly_chart(f, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 3.4.3 — Heatmap độ nhạy theo a₆ (AI Readiness)")
        rm = r["rank_matrix"]
        f = fig([go.Heatmap(z=rm.values, x=[f"{c:.2f}" for c in r["a6_range"]],
                            y=list(rm.index), colorscale="RdYlGn_r",
                            text=rm.values, texttemplate="%{text}")],
                title="Hạng ngành khi a₆ thay đổi", height=420)
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### 3.4.4 — Hai bộ trọng số chiến lược")
        st.markdown("**📈 Định hướng Tăng trưởng** — Top 3:")
        st.write(", ".join(r["rankA"].index[:3]))
        st.markdown("**🌱 Định hướng Bao trùm** — Top 3:")
        st.write(", ".join(r["rankB"].index[:3]))
        cmp = pd.DataFrame({"Tăng trưởng": r["rankA"].round(3).values,
                            "Ngành (TT)": r["rankA"].index})
        st.dataframe(cmp.head(5), hide_index=True, use_container_width=True)

    with st.expander("Ma trận chuẩn hóa min-max (7 chỉ tiêu)"):
        st.dataframe(r["norm_matrix"].round(3), use_container_width=True)

    policy_qa([
        ("a) Ba ngành ưu tiên đẩy mạnh chuyển đổi số/AI?",
         f"{', '.join(top3)} — phù hợp tinh thần Nghị quyết 57-NQ/TW ưu tiên công nghiệp công nghệ cao, "
         "CNTT và tài chính số tạo hiệu ứng lan tỏa."),
        ("b) Vì sao Khai khoáng năng suất cao nhưng không ưu tiên?",
         "Năng suất cao do thâm dụng tài nguyên, nhưng tăng trưởng âm, rủi ro tự động hóa cao và lan tỏa "
         "thấp → không tạo động lực kinh tế số."),
        ("c) Ai nên quyết định bộ trọng số?",
         "Nên qua quy trình đối thoại công khai giữa hội đồng chính sách và chuyên gia kỹ thuật để bảo "
         "đảm tính chính danh (governance), thay vì chỉ kỹ trị."),
    ])
