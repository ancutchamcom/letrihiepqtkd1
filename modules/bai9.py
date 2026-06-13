import streamlit as st
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai9()


def render():
    page_header("CẤP ĐỘ KHÁ KHÓ · BÀI 9",
                "👷 Tác động AI tới thị trường lao động",
                "LP tối đa NetJob ròng · 8 ngành · ràng buộc đào tạo lại")
    r = _compute()

    stat_row([
        ("Tổng NetJob ròng", f"{r['total_netjob']:,.0f}", "việc làm tạo/giữ"),
        ("NetJob (ràng buộc ≤5% L)", f"{r['netjob_5pct']:,.0f}" if r["netjob_5pct"] else "—",
         "khả thi" if r["feasible_5pct"] else "vô nghiệm"),
        ("Ngân sách", "30.000 tỷ", "x_AI + x_H"),
    ])

    st.markdown("#### 9.4.1 — Phân bổ tối ưu & NetJob theo ngành")
    st.dataframe(r["tbl"], hide_index=True, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        f = fig([go.Bar(x=r["sectors"], y=r["xA"], name="x_AI", marker_color=ACCENT),
                 go.Bar(x=r["sectors"], y=r["xH"], name="x_H", marker_color="#62d7c0")],
                barmode="group", title="Phân bổ x_AI vs x_H (tỷ VND)")
        f.update_xaxes(tickangle=-35)
        st.plotly_chart(f, use_container_width=True)
    with c2:
        f = fig([go.Bar(x=r["sectors"], y=r["NetJob"], marker_color=ACCENT)],
                title="NetJob ròng theo ngành")
        f.update_xaxes(tickangle=-35)
        st.plotly_chart(f, use_container_width=True)

    st.markdown("#### 9.4.3 — Luồng dịch chuyển lao động nhóm dễ bị tổn thương")
    vuln = [0, 2, 3]
    names = [r["sectors"][i] for i in vuln]
    kept, retrain, lost = [], [], []
    tbl = r["tbl"]
    for i in vuln:
        disp = tbl.iloc[i]["Displaced"]
        kept.append(r["L"][i]*1e6 - disp)
        retrain.append(disp)
        lost.append(0)
    f = fig([go.Bar(x=names, y=kept, name="Giữ việc", marker_color="#62d7c0"),
             go.Bar(x=names, y=retrain, name="Đào tạo lại", marker_color="#fff3a3")],
            barmode="stack", title="Swimming lane — nhóm Nông-LT, Xây dựng, Bán buôn")
    st.plotly_chart(f, use_container_width=True)

    st.markdown(f"#### 9.4.4 — Ràng buộc Displaced ≤ 5% lao động ngành")
    if r["feasible_5pct"]:
        diff = r["total_netjob"] - r["netjob_5pct"]
        st.markdown(f"Bài toán **vẫn khả thi**. NetJob giảm còn **{r['netjob_5pct']:,.0f}** "
                    f"(giảm {diff:,.0f} ≈ {diff/r['total_netjob']*100:.1f}%) — chi phí của an sinh xã hội.")
    else:
        st.warning("Bài toán không còn khả thi với ràng buộc 5%.")

    policy_qa([
        ("a) Ngành nào cần đào tạo lại nhiều nhất?",
         "CN chế biến chế tạo và Bán buôn-bán lẻ — lực lượng lớn, rủi ro tự động hóa cao; khớp thực tế VN."),
        ("b) Chiến lược cho Tài chính-Ngân hàng (risk 52%)?",
         "Vừa tự động hóa mạnh vừa hệ số tạo việc mới cao → đầu tư song song AI và đào tạo nâng kỹ năng "
         "(reskill) để chuyển dịch nội ngành."),
        ("c) Có nên đầu tư AI vào Nông-Lâm-Thủy sản?",
         "Hệ số tạo việc AI thấp (8,5) nhưng lao động dịch chuyển lớn → mô hình ưu tiên x_H (đào tạo lại) "
         "hơn x_AI ở ngành này."),
        ("d) 'Tốc độ tự động hóa ≤ năng lực đào tạo lại' là ràng buộc nào?",
         "Displaced_i ≤ RetrainingCapacity_i (c₁·risk·x_AI ≤ d₁·x_H). Có thể bổ sung trần dịch chuyển "
         "tuyệt đối/năm để bảo đảm an sinh."),
    ])
