import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai4()


def render():
    page_header("CẤP ĐỘ TRUNG BÌNH · BÀI 4",
                "🗺️ LP phân bổ ngân sách số ngành–vùng",
                "PuLP/CBC · ràng buộc công bằng vùng miền (C5)")
    r = _compute()
    regs = [core.REGION_NAMES[x] for x in core.REGIONS]

    stat_row([
        ("Z* (có công bằng C5)", f"{r['z_c5']:,.0f}", "tỷ VND GDP gain"),
        ("Z* (không C5)", f"{r['z_no']:,.0f}", "tỷ VND"),
        ("Chi phí công bằng", f"{r['equity_cost']:,.0f}", f"{r['equity_cost']/r['z_no']*100:.2f}% GDP gain"),
    ])

    st.markdown("#### 4.4.3 — Heatmap phân bổ tối ưu (có C5)")
    f = fig([go.Heatmap(z=r["mat_c5"], x=core.ITEMS, y=regs, colorscale="Reds",
                        text=r["mat_c5"].round(0), texttemplate="%{text}")],
            title="Phân bổ x_{j,r} (tỷ VND)", height=420)
    st.plotly_chart(f, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Tổng ngân sách theo vùng")
        tot_c5 = r["mat_c5"].sum(1); tot_no = r["mat_no"].sum(1)
        f = fig([go.Bar(x=regs, y=tot_c5, name="Có C5", marker_color=ACCENT),
                 go.Bar(x=regs, y=tot_no, name="Không C5", marker_color="#62d7c0")],
                barmode="group", title="Có C5 vs Không C5")
        f.update_xaxes(tickangle=-30)
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### Tổng theo hạng mục (có C5)")
        f = fig([go.Bar(x=core.ITEMS, y=r["mat_c5"].sum(0), marker_color=ACCENT,
                        text=r["mat_c5"].sum(0).round(0), textposition="outside")],
                title="Phân bổ theo hạng mục đầu tư")
        st.plotly_chart(f, use_container_width=True)

    st.markdown(f"#### 4.4.4 — Chi phí kinh tế của công bằng = **{r['equity_cost']:,.0f} tỷ VND** "
                f"({r['equity_cost']/r['z_no']*100:.2f}%)")
    st.caption("Đây là GDP gain bị hy sinh để đảm bảo tỷ lệ công bằng số hóa min/max ≥ λ=0,65. "
               "Ngưỡng λ tối đa khả thi ≈ 0,683 do giới hạn cấu trúc của hệ số γ và trần ngân sách.")

    policy_qa([
        ("a) Nếu bỏ công bằng, vốn chảy về đâu?",
         "Vốn dồn về Đông Nam Bộ & ĐB sông Hồng (β_AI cao nhất). Hậu quả dài hạn: khoét sâu khoảng "
         "cách số vùng miền, kéo theo bất bình đẳng xã hội."),
        ("b) Trần ngân sách vùng (C3) như phân quyền?",
         "C3 giới hạn 12.000 tỷ/vùng, buộc phân tán nguồn lực — giảm Z* nhẹ nhưng chấp nhận được để "
         "tránh tập trung quá mức."),
        ("c) Tây Nguyên: đầu tư AI hay H & I?",
         "Mô hình ưu tiên H và I (β_H=1,35 cao nhất, β_AI=0,45 thấp) — nên xây nền tảng nhân lực & hạ "
         "tầng trước khi đầu tư AI."),
    ])
