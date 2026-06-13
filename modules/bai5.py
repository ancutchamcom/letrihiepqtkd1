import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai5()


def render():
    page_header("CẤP ĐỘ TRUNG BÌNH · BÀI 5",
                "🧩 MIP lựa chọn 15 dự án chuyển đổi số",
                "PuLP/CBC · knapsack · ràng buộc loại trừ & tiên quyết")
    r = _compute()
    base = r["base"]

    stat_row([
        ("Z* (gốc, 80k/40k)", f"{base['Z']:,.0f}", f"{len(base['sel'])} dự án"),
        ("Z* (nới 100k)", f"{r['expand']['Z']:,.0f}", f"{len(r['expand']['sel'])} dự án"),
        ("Bắt buộc P1+P2", r["force"]["status"],
         f"{len(r['force']['sel'])} dự án" if r["force"]["sel"] else "—"),
    ])

    st.markdown("#### 5.4.1 — Dự án được chọn (bài toán gốc)")
    sel = base["sel"]
    df = pd.DataFrame({
        "Mã": [f"P{i}" for i in sel],
        "Tên": [core.C5_NAMES[i] for i in sel],
        "Chi phí (tỷ)": [core.C5_COST[i] for i in sel],
        "Lợi ích NPV": [core.C5_B[i] for i in sel],
        "p (rủi ro)": [core.P_RISK[i] for i in sel]})
    st.dataframe(df, hide_index=True, use_container_width=True)
    st.caption(f"Tổng chi phí: {base['tc1']+base['tc2']:,.0f} tỷ · Tổng lợi ích Z* = {base['Z']:,.0f} tỷ "
               f"· NPV biên = {base['Z']/(base['tc1']+base['tc2']):.3f}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Lợi ích/chi phí 15 dự án")
        P = list(range(1, 16))
        ratio = [core.C5_B[i]/core.C5_COST[i] for i in P]
        f = fig([go.Bar(x=[f"P{i}" for i in P], y=ratio,
                        marker_color=[ACCENT if i in sel else "#3a3d47" for i in P])],
                title="B/C ratio (đỏ = được chọn)")
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### So sánh 4 kịch bản")
        rows = [("5.4.1 Gốc", base), ("5.4.2 Nới 100k", r["expand"]),
                ("5.4.3 Bắt buộc P1+P2", r["force"]), ("5.4.4 Rủi ro E[Z]", r["risk"])]
        cmp = pd.DataFrame({
            "Kịch bản": [n for n, _ in rows],
            "Z*/E[Z]": [f"{x['Z']:,.0f}" if x["Z"] else x["status"] for _, x in rows],
            "# dự án": [len(x["sel"]) if x["sel"] else "–" for _, x in rows]})
        st.dataframe(cmp, hide_index=True, use_container_width=True)

    st.markdown("#### 5.4.4 — Tối đa lợi ích kỳ vọng E[Z]")
    if r["risk"]["sel"]:
        st.write("Dự án chọn:", ", ".join(f"P{i}" for i in r["risk"]["sel"]))
        st.caption("Khi tính rủi ro hoàn thành (p), mô hình ưu tiên dự án hạ tầng (p=0,85) và hạn chế "
                   "AI/bán dẫn (p=0,65) dù lợi ích danh nghĩa cao.")

    policy_qa([
        ("a) Vì sao bỏ P15 (Open Data) dù B/C cao?",
         "P15 quy mô nhỏ; ràng buộc số dự án (≤11) và ngân sách năm 1-2 khiến mô hình ưu tiên dự án lớn "
         "tạo lợi ích tuyệt đối cao hơn — không nhất thiết tối ưu về chính sách dữ liệu mở."),
        ("b) Bắt buộc P14 (an ninh mạng) có giảm Z*?",
         "P14 chi phí thấp, lợi ích khá nên ràng buộc bắt buộc gần như không giảm Z*; hợp lý vì an ninh "
         "mạng là điều kiện nền tảng."),
        ("c) Mô hình hóa hiệu ứng cộng hưởng P8–P13?",
         "Thêm biến phụ z = y₈·y₁₃ (linear hóa McCormick) và cộng phần lợi ích bổ sung khi cả hai cùng "
         "được chọn."),
    ])
