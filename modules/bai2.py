import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai2()


def render():
    page_header("CẤP ĐỘ DỄ · BÀI 2",
                "💰 LP phân bổ ngân sách số 4 hạng mục",
                "scipy.optimize.linprog · shadow price · phân tích độ nhạy")
    r = _compute()
    names = ["x₁ Hạ tầng số", "x₂ AI & dữ liệu", "x₃ Nhân lực số", "x₄ R&D"]
    rois = [0.85, 1.20, 0.95, 1.35]

    stat_row([
        ("Z* (tăng GDP kỳ vọng)", f"{r['Z']:.3f}", "nghìn tỷ VND"),
        ("Shadow price ngân sách", f"{r['duals'][0]:.3f}", "ΔZ* / 1 ngh.tỷ B"),
        ("Z* khi x₃≥30", f"{r['Z30']:.3f}", "vẫn KHẢ THI"),
    ])

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 2.4.1 — Phân bổ tối ưu (B=100)")
        f = fig([go.Bar(x=names, y=r["x"], marker_color=ACCENT,
                        text=[f"{v:.1f}" for v in r["x"]], textposition="outside")],
                title="Phân bổ tối ưu (nghìn tỷ VND)")
        st.plotly_chart(f, use_container_width=True)
        st.dataframe(pd.DataFrame({"Hạng mục": names, "ROI": rois,
                                   "Phân bổ": [round(v, 2) for v in r["x"]]}),
                     hide_index=True, use_container_width=True)
    with c2:
        st.markdown("#### 2.4.3 — Đường cong Z*(B)")
        B = [c[0] for c in r["curve"]]; Z = [c[1] for c in r["curve"]]
        f = fig([go.Scatter(x=B, y=Z, mode="lines+markers", line=dict(color=ACCENT, width=3))],
                title="Độ nhạy Z* theo ngân sách B", xaxis_title="Ngân sách B", yaxis_title="Z*")
        st.plotly_chart(f, use_container_width=True)
        st.markdown("##### Phân bổ tối ưu theo B")
        df = pd.DataFrame(r["curve"], columns=["B", "Z*", "x₁", "x₂", "x₃", "x₄"])
        ff = fig([go.Scatter(x=df.B, y=df[c], mode="lines", name=c) for c in ["x₁", "x₂", "x₃", "x₄"]],
                 title="Phân bổ x_i theo B")
        st.plotly_chart(ff, use_container_width=True)

    st.markdown(f"#### 2.4.2 — Shadow price ngân sách = **{r['duals'][0]:.4f}**")
    st.caption("Tăng 1 nghìn tỷ ngân sách → Z* tăng thêm ~1,35 đơn vị, đúng bằng ROI của hạng mục "
               "biên (R&D). Ràng buộc ngân sách đang 'binding' — còn dư địa hiệu quả.")

    st.markdown(f"#### 2.4.4 — Ràng buộc x₃ ≥ 30 (ưu tiên nhân lực số)")
    st.markdown(f"Bài toán **vẫn khả thi** (25+15+30+10=80 ≤ 100). Z* giảm còn **{r['Z30']:.3f}** "
                f"(− {r['Z']-r['Z30']:.3f}), là chi phí cơ hội của chính sách ưu tiên nhân lực.")

    policy_qa([
        ("a) GDP kỳ vọng tăng bao nhiêu khi B tăng 1 tỷ?",
         f"≈ {r['duals'][0]:.2f} đơn vị — đây là cận trên hợp lý của chi phí cơ hội của vốn công."),
        ("b) Vì sao R&D hệ số cao nhất nhưng sàn thấp nhất?",
         "R&D có tác động lan tỏa dài hạn (ROI 1,35) nhưng năng lực hấp thụ hạn chế và rủi ro cao, "
         "nên đặt sàn thấp để tránh dồn vốn quá sớm."),
        ("c) Tỷ lệ 35% công nghệ chiến lược có khả thi?",
         "Thách thức khi ngân sách thực tế ưu tiên hạ tầng giao thông & an sinh; cần lộ trình tăng dần "
         "và huy động vốn tư nhân/PPP cho AI và R&D."),
    ])
