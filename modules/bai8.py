import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules import core
from modules.common import page_header, stat_row, policy_qa, fig, ACCENT, PLOTLY_LAYOUT


@st.cache_data(show_spinner=False)
def _compute():
    return core.bai8()


def render():
    page_header("CẤP ĐỘ KHÁ KHÓ · BÀI 8",
                "📈 Tối ưu động liên thời gian 2026–2035",
                "SLSQP · dynamics vốn · hàm thỏa dụng CRRA")
    with st.spinner("Đang tối ưu quỹ đạo 10 năm (SLSQP)…"):
        r = _compute()

    stat_row([
        ("Phúc lợi W* (tối ưu)", f"{r['W']:.2f}", "tổng chiết khấu ρ=0,97"),
        ("Đầu tư đều", f"{r['W_even']:.2f}", "chiến lược (i)"),
        ("Front-load", f"{r['W_front']:.2f}", "chiến lược (ii)"),
    ])

    st.markdown("#### 8.3.2 — Quỹ đạo tối ưu của K, D, AI, H, Y, C")
    yrs = r["years"]
    fig_t = make_subplots(rows=2, cols=3,
                          subplot_titles=("K (vốn vật chất)", "D (hạ tầng số)", "AI (nghìn DN)",
                                          "H (nhân lực)", "Y & C", "A (TFP)"))
    series = [(r["K"], 1, 1), (r["D"], 1, 2), (r["AI"], 1, 3), (r["H"], 2, 1), (r["A"], 2, 3)]
    for data, row, col in series:
        fig_t.add_trace(go.Scatter(x=yrs, y=data, mode="lines+markers",
                                   line=dict(color=ACCENT)), row=row, col=col)
    fig_t.add_trace(go.Scatter(x=yrs, y=r["Y"], mode="lines+markers", name="Y",
                               line=dict(color=ACCENT)), row=2, col=2)
    fig_t.add_trace(go.Scatter(x=yrs[:-1], y=r["C"], mode="lines+markers", name="C",
                               line=dict(color="#62d7c0")), row=2, col=2)
    fig_t.update_layout(height=520, showlegend=False, **{k: v for k, v in PLOTLY_LAYOUT.items()
                                                          if k not in ("margin",)})
    fig_t.update_xaxes(gridcolor="#23262f"); fig_t.update_yaxes(gridcolor="#23262f")
    st.plotly_chart(fig_t, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Tỷ lệ đầu tư / GDP theo năm")
        u = r["u"]; T = r["T"]
        shares = {"I_K": [], "I_D": [], "I_AI": [], "I_H": []}
        keys = list(shares.keys())
        for t in range(T):
            for k_i, k in enumerate(keys):
                shares[k].append(u[t*4+k_i]/r["Y"][t]*100)
        f = fig([go.Bar(x=yrs[:-1], y=shares[k], name=k) for k in keys],
                barmode="stack", title="Cơ cấu đầu tư/GDP (%)")
        st.plotly_chart(f, use_container_width=True)
    with c2:
        st.markdown("#### 8.3.4 — So sánh phúc lợi 3 chiến lược")
        f = fig([go.Bar(x=["Tối ưu", "Đầu tư đều", "Front-load"],
                        y=[r["W"], r["W_even"], r["W_front"]], marker_color=ACCENT,
                        text=[f"{v:.1f}" for v in [r["W"], r["W_even"], r["W_front"]]],
                        textposition="outside")],
                title="Phúc lợi tổng W")
        st.plotly_chart(f, use_container_width=True)

    policy_qa([
        ("a) Quỹ đạo front-loaded hay back-loaded?",
         "Mô hình ưu tiên đầu tư sớm (front-load nhẹ) vào K, D, AI để tích lũy vốn và nâng TFP nội sinh, "
         "tạo dư địa tiêu dùng các năm sau."),
        ("b) Tỷ lệ đầu tư AI/H có ổn định?",
         "Đầu tư H đi trước hoặc đồng thời với AI — vì AI chỉ phát huy khi có nền tảng nhân lực số hấp thụ "
         "công nghệ."),
        ("c) ρ=0,97 vs ρ=0,90?",
         "ρ thấp (ngắn hạn hơn) làm giảm đầu tư dài hạn vào R&D/AI — lý giải vì sao chính phủ thường "
         "'dưới đầu tư' khi tầm nhìn ngắn."),
    ])
