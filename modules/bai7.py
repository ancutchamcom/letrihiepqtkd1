import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai7()


def render():
    page_header("CẤP ĐỘ KHÁ KHÓ · BÀI 7",
                "🎯 NSGA-II — Tối ưu đa mục tiêu Pareto",
                "4 mục tiêu xung đột · pymoo · TOPSIS chọn nghiệm thỏa hiệp")
    with st.spinner("Đang chạy NSGA-II (pop=100, gen=120)…"):
        r = _compute()
    tp = r["topsis"]; gr = r["growth"]

    stat_row([
        ("Nghiệm Pareto", f"{r['n']}", "tập không trội"),
        ("GDP gain (thỏa hiệp)", f"{tp[0]:.3f}", "nghiệm TOPSIS"),
        ("GDP gain (cao nhất)", f"{gr[0]:.3f}", "hy sinh bao trùm & môi trường"),
    ])

    st.markdown("#### 7.4.2 — Đường biên Pareto 3D (f₁, f₂, f₃; màu = f₄ an ninh)")
    f3d = go.Figure(go.Scatter3d(
        x=r["GDP"], y=r["Gini"], z=r["CO2"], mode="markers",
        marker=dict(color=r["Sec"], colorscale="Plasma", size=4, opacity=0.85,
                    colorbar=dict(title="f₄ An ninh")),
        hovertemplate="GDP=%{x:.3f}<br>Bất BĐ=%{y:.2f}<br>CO₂=%{z:.2f}<extra></extra>"))
    f3d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e6e6e6"),
        height=560, margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis=dict(title="f₁: GDP gain", backgroundcolor="#0e1117",
                       gridcolor="#23262f", color="#e6e6e6"),
            yaxis=dict(title="f₂: Bất bình đẳng", backgroundcolor="#0e1117",
                       gridcolor="#23262f", color="#e6e6e6"),
            zaxis=dict(title="f₃: Phát thải CO₂", backgroundcolor="#0e1117",
                       gridcolor="#23262f", color="#e6e6e6")))
    st.plotly_chart(f3d, use_container_width=True)
    st.caption("Mỗi điểm là một nghiệm Pareto. Có thể xoay/zoom để quan sát đánh đổi giữa "
               "tăng trưởng, bao trùm và môi trường; màu sắc thể hiện rủi ro an ninh dữ liệu.")

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("##### Chiếu 2D: Tăng trưởng vs Bao trùm")
        f = fig([go.Scatter(x=r["GDP"], y=r["Gini"], mode="markers",
                            marker=dict(color=r["CO2"], colorscale="YlOrRd", size=7,
                                        colorbar=dict(title="CO₂")))],
                title="f₁ (GDP) vs f₂ (bất bình đẳng); màu = CO₂",
                xaxis_title="GDP gain", yaxis_title="Bất bình đẳng (MAD)")
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### 7.4.3 — Nghiệm thỏa hiệp (TOPSIS)")
        st.caption("Trọng số: TT 0,40 · Bao trùm 0,25 · Môi trường 0,20 · An ninh 0,15")
        cmp = pd.DataFrame({
            "Mục tiêu": ["GDP gain", "Bất bình đẳng", "Phát thải CO₂", "Rủi ro an ninh"],
            "Thỏa hiệp": [f"{v:.3f}" for v in tp],
            "GDP cao nhất": [f"{v:.3f}" for v in gr]})
        st.dataframe(cmp, hide_index=True, use_container_width=True)

    st.markdown("#### Parallel coordinates — toàn bộ Pareto (4 mục tiêu)")
    import numpy as np
    F = np.column_stack([r["GDP"], r["Gini"], r["CO2"], r["Sec"]])
    Fn = (F - F.min(0))/(F.max(0)-F.min(0)+1e-9)
    f = go.Figure(go.Parcoords(
        line=dict(color=r["GDP"], colorscale="Viridis"),
        dimensions=[dict(label=l, values=Fn[:, i]) for i, l in
                    enumerate(["f₁ GDP", "f₂ Bất BĐ", "f₃ CO₂", "f₄ An ninh"])]))
    f.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e6e6e6"), height=360)
    st.plotly_chart(f, use_container_width=True)

    policy_qa([
        ("a) Đánh đổi tăng trưởng vs bao trùm có rõ?",
         "Đường Pareto cho thấy đánh đổi rõ: nghiệm GDP cao nhất làm tăng bất bình đẳng vùng — phản ánh "
         "cơ cấu kinh tế tập trung ở Đông Nam Bộ & ĐBSH."),
        ("b) Trọng số (0,40;0,25;0,20;0,15) đúng ưu tiên VN?",
         "Phù hợp định hướng tăng trưởng nhanh đi đôi bao trùm của Đại hội XIII; để bám COP26 nên tăng "
         "trọng số môi trường lên ~0,25."),
        ("c) NSGA-II khác LP đơn mục tiêu thế nào?",
         "NSGA-II cung cấp cả tập phương án đánh đổi, không thay thế quyết định chính trị mà hỗ trợ nhà "
         "hoạch định lựa chọn trong không gian Pareto."),
    ])
