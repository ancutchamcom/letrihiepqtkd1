"""
AIDEOM-VN — Lõi tính toán (computation engine) cho cả 12 bài toán.
Tái hiện trung thực các mô hình trong notebook hiep1.ipynb.
Mỗi hàm được cache bằng st.cache_data ở tầng module render để tránh tính lại.
"""
import os
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


# =====================================================================
# NẠP DỮ LIỆU
# =====================================================================
def load_macro():
    df = pd.read_csv(os.path.join(DATA_DIR, "vietnam_macro_2020_2025.csv"))
    return df.sort_values("year").reset_index(drop=True)


def load_sectors():
    return pd.read_csv(os.path.join(DATA_DIR, "vietnam_sectors_2024.csv"))


def load_regions():
    return pd.read_csv(os.path.join(DATA_DIR, "vietnam_regions_2024.csv"))


# Chuỗi đầu vào sản xuất (Bài 1) — theo bảng 1.3 của đề bài
K_SERIES  = np.array([16500, 17800, 19600, 21300, 23500, 25900], dtype=float)
L_SERIES  = np.array([53.6, 50.5, 51.7, 52.4, 52.9, 53.4], dtype=float)
D_SERIES  = np.array([12.0, 12.7, 14.3, 16.5, 18.3, 19.5], dtype=float)
AI_SERIES = np.array([55.6, 60.2, 65.4, 67.0, 73.8, 80.1], dtype=float)
H_SERIES  = np.array([24.1, 26.1, 26.2, 27.0, 28.4, 29.2], dtype=float)
ALPHA, BETA, GAMMA, DELTA, THETA = 0.33, 0.42, 0.10, 0.08, 0.07


# =====================================================================
# BÀI 1 — Cobb-Douglas mở rộng + Growth accounting
# =====================================================================
def bai1():
    df = load_macro()
    years = df["year"].values
    Y = df["GDP_trillion_VND"].values
    K, L, D, AI, H = K_SERIES, L_SERIES, D_SERIES, AI_SERIES, H_SERIES

    A = Y / (K**ALPHA * L**BETA * D**GAMMA * AI**DELTA * H**THETA)
    A_mean = A.mean()
    Y_hat = A_mean * (K**ALPHA * L**BETA * D**GAMMA * AI**DELTA * H**THETA)
    APE = np.abs((Y - Y_hat) / Y) * 100
    MAPE = APE.mean()

    # Growth accounting (Δln)
    g_Y = np.diff(np.log(Y)) * 100
    g_K = np.diff(np.log(K)) * 100
    g_L = np.diff(np.log(L)) * 100
    g_D = np.diff(np.log(D)) * 100
    g_AI = np.diff(np.log(AI)) * 100
    g_H = np.diff(np.log(H)) * 100
    g_A = np.diff(np.log(A)) * 100
    c_K, c_L, c_D, c_AI, c_H, c_TFP = (
        ALPHA*g_K, BETA*g_L, GAMMA*g_D, DELTA*g_AI, THETA*g_H, g_A)
    means = {"K": c_K.mean(), "L": c_L.mean(), "D": c_D.mean(),
             "AI": c_AI.mean(), "H": c_H.mean(), "TFP": c_TFP.mean()}
    total = sum(means.values())
    shares = {k: v/total*100 for k, v in means.items()}

    decomp = pd.DataFrame({
        "Năm": years[1:], "K": c_K.round(2), "L": c_L.round(2), "D": c_D.round(2),
        "AI": c_AI.round(2), "H": c_H.round(2), "TFP": c_TFP.round(2),
        "g_Y": g_Y.round(2)})

    # Dự báo 2030
    n = 5
    K30 = K[-1]*(1.06**n); L30 = L[-1]*(1.06**n)
    D30, AI30, H30 = 30.0, 100.0, 35.0
    A30 = A_mean*(1.012**n)
    Y30 = A30*(K30**ALPHA*L30**BETA*D30**GAMMA*AI30**DELTA*H30**THETA)
    cagr = ((Y30/Y[-1])**(1/n)-1)*100

    return dict(years=years, Y=Y, A=A, A_mean=A_mean, Y_hat=Y_hat, APE=APE,
                MAPE=MAPE, decomp=decomp, means=means, shares=shares, total=total,
                Y30=Y30, cagr=cagr, K=K, L=L, D=D, AI=AI, H=H)


# =====================================================================
# BÀI 2 — LP phân bổ ngân sách số 4 hạng mục (scipy)
# =====================================================================
def _solve_lp_bai2(budget=100, x3_min=20):
    from scipy.optimize import linprog
    c = [-0.85, -1.20, -0.95, -1.35]
    A_ub = [[1, 1, 1, 1], [-1, 0, 0, 0], [0, -1, 0, 0],
            [0, 0, -1, 0], [0, 0, 0, -1], [0.35, -0.65, 0.35, -0.65]]
    b_ub = [budget, -25, -15, -x3_min, -10, 0]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)]*4, method="highs")
    if res.success:
        return True, -res.fun, res.x, -res.ineqlin.marginals
    return False, None, None, None


def bai2():
    ok, Z, x, duals = _solve_lp_bai2(100, 20)
    budgets = list(range(70, 181, 5))
    curve = []
    for B in budgets:
        o, z, xx, d = _solve_lp_bai2(B, 20)
        if o:
            curve.append((B, z, xx[0], xx[1], xx[2], xx[3]))
    ok30, Z30, x30, d30 = _solve_lp_bai2(100, 30)
    return dict(Z=Z, x=x, duals=duals, curve=curve,
                Z30=Z30, x30=x30, d30=d30, feasible30=ok30)


# =====================================================================
# BÀI 3 — Chỉ số ưu tiên 10 ngành (min-max + weighted scoring)
# =====================================================================
def bai3():
    df = load_sectors().copy()
    cols_good = ["growth_rate_2024_pct", "gdp_share_2024_pct", "spillover_coef_0_1",
                 "export_billion_USD", "labor_million", "ai_readiness_0_100"]
    col_bad = "automation_risk_pct"

    def nrm(s): return (s - s.min())/(s.max()-s.min())
    Xg = df[cols_good].apply(nrm)
    Xb = nrm(df[col_bad])

    def priority(wg, wr): return Xg.values @ np.array(wg) - wr*Xb.values

    w_def = [0.15, 0.15, 0.20, 0.15, 0.10, 0.20]; wr_def = 0.15
    df["Priority"] = priority(w_def, wr_def)
    rank = df[["sector_name_en", "Priority"]].sort_values(
        "Priority", ascending=False).reset_index(drop=True)
    rank.index += 1

    # độ nhạy a6
    a6_range = np.round(np.arange(0.05, 0.41, 0.05), 2)
    base_others = np.array([0.15, 0.15, 0.20, 0.15, 0.10, 0.15])
    sens = {}
    for a6 in a6_range:
        scale = (1-a6)/base_others.sum()
        wsc = base_others*scale
        wg = [wsc[0], wsc[1], wsc[2], wsc[3], wsc[4], a6]; wr = wsc[5]
        sens[a6] = pd.Series(priority(wg, wr), index=df["sector_name_en"]).rank(ascending=False).astype(int)
    rank_matrix = pd.DataFrame(sens)

    # hai bộ trọng số chiến lược
    WA = priority([0.25, 0.20, 0.10, 0.25, 0.05, 0.10], 0.05)
    WB = priority([0.10, 0.10, 0.20, 0.10, 0.25, 0.10], 0.15)
    rankA = pd.Series(WA, index=df["sector_name_en"]).sort_values(ascending=False)
    rankB = pd.Series(WB, index=df["sector_name_en"]).sort_values(ascending=False)

    norm_matrix = Xg.copy()
    norm_matrix["risk_inv"] = (df[col_bad].max()-df[col_bad])/(df[col_bad].max()-df[col_bad].min())
    norm_matrix.index = df["sector_name_en"]
    return dict(rank=rank, rank_matrix=rank_matrix, a6_range=a6_range,
                rankA=rankA, rankB=rankB, norm_matrix=norm_matrix, df=df)


# =====================================================================
# BÀI 4 — LP phân bổ ngân sách số ngành-vùng (PuLP/CBC)
# =====================================================================
REGIONS = ["NMM", "RRD", "NCC", "CH", "SE", "MD"]
ITEMS = ["I", "D", "AI", "H"]
REGION_NAMES = {"NMM": "Trung du & MN phía Bắc", "RRD": "ĐB sông Hồng",
                "NCC": "Bắc&Nam Trung Bộ", "CH": "Tây Nguyên",
                "SE": "Đông Nam Bộ", "MD": "ĐB sông Cửu Long"}
BETA4 = {
    ("NMM", "I"): 1.15, ("NMM", "D"): 0.85, ("NMM", "AI"): 0.55, ("NMM", "H"): 1.30,
    ("RRD", "I"): 0.95, ("RRD", "D"): 1.25, ("RRD", "AI"): 1.40, ("RRD", "H"): 1.05,
    ("NCC", "I"): 1.05, ("NCC", "D"): 0.95, ("NCC", "AI"): 0.85, ("NCC", "H"): 1.15,
    ("CH", "I"): 1.20, ("CH", "D"): 0.75, ("CH", "AI"): 0.45, ("CH", "H"): 1.35,
    ("SE", "I"): 0.90, ("SE", "D"): 1.30, ("SE", "AI"): 1.55, ("SE", "H"): 1.00,
    ("MD", "I"): 1.10, ("MD", "D"): 0.85, ("MD", "AI"): 0.65, ("MD", "H"): 1.25}
D0_R = {"NMM": 38, "RRD": 78, "NCC": 55, "CH": 32, "SE": 82, "MD": 48}


def _solve_bai4(with_c5=True, lam=0.65):
    import pulp
    gamma = 0.002
    BUDGET, MIN_R, MAX_R, MIN_H = 50000, 5000, 12000, 12000
    m = pulp.LpProblem("VN_Digital", pulp.LpMaximize)
    x = pulp.LpVariable.dicts("x", (REGIONS, ITEMS), lowBound=0)
    m += pulp.lpSum(BETA4[(r, j)]*x[r][j] for r in REGIONS for j in ITEMS)
    m += pulp.lpSum(x[r][j] for r in REGIONS for j in ITEMS) <= BUDGET
    for r in REGIONS:
        m += pulp.lpSum(x[r][j] for j in ITEMS) >= MIN_R
        m += pulp.lpSum(x[r][j] for j in ITEMS) <= MAX_R
    m += pulp.lpSum(x[r]["H"] for r in REGIONS) >= MIN_H
    if with_c5:
        M = pulp.LpVariable("Dmax", lowBound=0)
        for r in REGIONS:
            m += D0_R[r] + gamma*x[r]["D"] <= M
            m += D0_R[r] + gamma*x[r]["D"] >= lam*M
        m += M <= max(D0_R.values()) + gamma*MAX_R
    m.solve(pulp.PULP_CBC_CMD(msg=0))
    mat = np.array([[pulp.value(x[r][j]) or 0 for j in ITEMS] for r in REGIONS])
    return pulp.value(m.objective), mat


def bai4():
    z_c5, mat_c5 = _solve_bai4(True, 0.65)
    z_no, mat_no = _solve_bai4(False)
    equity_cost = z_no - z_c5
    return dict(z_c5=z_c5, mat_c5=mat_c5, z_no=z_no, mat_no=mat_no,
                equity_cost=equity_cost, lam=0.65)


# =====================================================================
# BÀI 5 — MIP lựa chọn 15 dự án (PuLP/CBC)
# =====================================================================
C5_COST = {1: 12000, 2: 11500, 3: 18000, 4: 4500, 5: 3200, 6: 5800, 7: 6500,
           8: 15000, 9: 2500, 10: 7200, 11: 4800, 12: 8500, 13: 20000, 14: 3800, 15: 1500}
C5_C1 = {1: 8500, 2: 7500, 3: 12000, 4: 3500, 5: 2500, 6: 4000, 7: 4500, 8: 9000,
         9: 1800, 10: 5000, 11: 3500, 12: 5500, 13: 13000, 14: 2800, 15: 1200}
C5_B = {1: 21500, 2: 20800, 3: 32500, 4: 9200, 5: 6800, 6: 11400, 7: 12200, 8: 28500,
        9: 5800, 10: 13800, 11: 8500, 12: 16200, 13: 35000, 14: 7500, 15: 3800}
C5_NAMES = {1: "TT dữ liệu QG Hòa Lạc", 2: "TT dữ liệu QG phía Nam", 3: "5G toàn quốc",
            4: "VNeID 2.0", 5: "Cổng DVC v3", 6: "Y tế số QG", 7: "Giáo dục số K-12",
            8: "TT AI QG + supercomputing", 9: "Sandbox fintech", 10: "Logistics thông minh",
            11: "Nông nghiệp số ĐBSCL", 12: "Đào tạo 50k kỹ sư AI", 13: "KCN bán dẫn BN-BG",
            14: "An ninh mạng QG (SOC)", 15: "Open Data QG"}
_INFRA, _EGOV, _AISD = {3, 8, 14}, {1, 2, 12}, {7, 10, 13}
P_RISK = {i: 0.85 if i in _INFRA else 0.75 if i in _EGOV else 0.65 if i in _AISD else 0.80
          for i in range(1, 16)}


def _solve_bai5(budget1=80000, budget2=40000, force_p1p2=False, expected=False):
    from pulp import LpProblem, LpMaximize, LpVariable, LpStatus, lpSum, value, PULP_CBC_CMD
    P = list(range(1, 16))
    m = LpProblem("sel", LpMaximize)
    y = LpVariable.dicts("y", P, cat="Binary")
    if expected:
        m += lpSum(P_RISK[i]*C5_B[i]*y[i] for i in P)
    else:
        m += lpSum(C5_B[i]*y[i] for i in P)
    m += lpSum(C5_COST[i]*y[i] for i in P) <= budget1
    m += lpSum(C5_C1[i]*y[i] for i in P) <= budget2
    if force_p1p2:
        m += y[1] == 1
        m += y[2] == 1
    else:
        m += y[1] + y[2] <= 1
    m += y[8] <= y[12]
    m += y[13] <= y[12]
    m += y[4] + y[5] >= 1
    m += y[14] >= 1
    m += lpSum(y[i] for i in P) >= 7
    m += lpSum(y[i] for i in P) <= 11
    m.solve(PULP_CBC_CMD(msg=False))
    status = LpStatus[m.status]
    if status != "Optimal":
        return dict(status=status, sel=None, Z=None)
    sel = [i for i in P if y[i].value() > 0.5]
    return dict(status=status, sel=sel, Z=value(m.objective),
                tc1=sum(C5_COST[i] for i in sel), tc2=sum(C5_C1[i] for i in sel),
                tb=sum(C5_B[i] for i in sel))


def bai5():
    return dict(base=_solve_bai5(80000, 40000),
                expand=_solve_bai5(100000, 40000),
                force=_solve_bai5(80000, 40000, force_p1p2=True),
                risk=_solve_bai5(80000, 40000, expected=True))


# =====================================================================
# BÀI 6 — TOPSIS 6 vùng (Expert + Entropy + AHP)
# =====================================================================
def _topsis(X, w, is_ben):
    R = X/np.sqrt((X**2).sum(0)); V = R*w
    ib = np.array(is_ben)
    Ap = np.where(ib, V.max(0), V.min(0))
    An = np.where(ib, V.min(0), V.max(0))
    Sp = np.sqrt(((V-Ap)**2).sum(1))
    Sn = np.sqrt(((V-An)**2).sum(1))
    return Sn/(Sp+Sn)


def _entropy_w(X):
    P = X/X.sum(0); k = 1/np.log(len(X))
    E = -k*np.nansum(P*np.log(P+1e-12), 0); d = 1-E
    return d/d.sum()


def bai6():
    df = load_regions().copy()
    crit = ["grdp_per_capita_million_VND", "fdi_registered_billion_USD",
            "digital_index_0_100", "ai_readiness_0_100", "trained_labor_pct",
            "rd_intensity_pct", "internet_penetration_pct", "gini_coef"]
    is_ben = [True, True, True, True, True, True, True, False]
    w_exp = np.array([0.10, 0.10, 0.15, 0.20, 0.15, 0.15, 0.05, 0.10])
    X = df[crit].values.astype(float)
    C_exp = _topsis(X, w_exp, is_ben)
    w_ent = _entropy_w(X)
    C_ent = _topsis(X, w_ent, is_ben)

    def rank(a): return (-a).argsort().argsort()+1
    res = pd.DataFrame({
        "Vùng": df["region_name_en"],
        "C*_Expert": C_exp.round(4), "Hạng_Expert": rank(C_exp),
        "C*_Entropy": C_ent.round(4), "Hạng_Entropy": rank(C_ent)})

    # độ nhạy w_AI
    a_range = np.round(np.arange(0.10, 0.41, 0.02), 2)
    sens = []
    for wa in a_range:
        wn = w_exp.copy()
        rem = 1-wa; old = w_exp.sum()-w_exp[3]
        for i in range(len(wn)):
            if i != 3:
                wn[i] = w_exp[i]/old*rem
        wn[3] = wa; wn = wn/wn.sum()
        sens.append(_topsis(X, wn, is_ben))
    sens = np.array(sens)
    return dict(df=df, crit=crit, res=res, C_exp=C_exp, C_ent=C_ent,
                w_exp=w_exp, w_ent=w_ent, a_range=a_range, sens=sens)


# =====================================================================
# BÀI 7 — NSGA-II Pareto (4 mục tiêu)
# =====================================================================
def bai7():
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.optimize import minimize
    from pymoo.termination import get_termination

    beta = np.column_stack([
        np.array([0.000085, 0.000045, 0.000065, 0.000092, 0.000040, 0.000078]),
        np.array([0.000072, 0.000095, 0.000082, 0.000058, 0.000105, 0.000068]),
        np.array([0.000055, 0.000115, 0.000078, 0.000042, 0.000125, 0.000060]),
        np.array([0.000068, 0.000088, 0.000075, 0.000062, 0.000095, 0.000055])])
    e = np.array([0.42, 0.55, 0.48, 0.32, 0.62, 0.38])
    rho = np.array([0.18, 0.45, 0.28, 0.12, 0.52, 0.22])
    sig = np.array([0.32, 0.28, 0.30, 0.35, 0.25, 0.30])
    TOTAL = 60000
    grdp = np.array([810, 3580, 1820, 420, 3050, 1409], float)
    region_min = grdp/grdp.sum()*TOTAL*0.50
    cat_min = np.array([8000, 10000, 12000, 8000])

    class P(ElementwiseProblem):
        def __init__(s):
            super().__init__(n_var=24, n_obj=4, n_ieq_constr=12,
                             xl=np.zeros(24), xu=np.ones(24)*12000)

        def _evaluate(s, x, out, *a, **k):
            X = x.reshape(6, 4)
            f1 = -(beta*X).sum()
            sums = X.sum(1); f2 = np.abs(sums-sums.mean()).mean()
            f3 = (e*(X[:, 0]+X[:, 2])).sum()
            f4 = (rho*X[:, 2]).sum()-(sig*X[:, 3]).sum()
            out["F"] = [f1, f2, f3, f4]
            tot = X.sum()
            g = [tot-TOTAL, 0.85*TOTAL-tot]
            for i in range(6):
                g.append(region_min[i]-X[i].sum())
            for j in range(4):
                g.append(cat_min[j]-X[:, j].sum())
            out["G"] = g

    res = minimize(P(), NSGA2(pop_size=100), get_termination("n_gen", 120),
                   seed=42, verbose=False)
    F = res.F.copy(); Xp = res.X.copy()
    GDP = -F[:, 0]; Gini = F[:, 1]; CO2 = F[:, 2]; Sec = F[:, 3]

    # TOPSIS chọn nghiệm thỏa hiệp
    w = np.array([0.40, 0.25, 0.20, 0.15])
    norm = np.sqrt((F**2).sum(0)); V = (F/norm)*w
    Ap = V.min(0); An = V.max(0)
    dp = np.sqrt(((V-Ap)**2).sum(1)); dn = np.sqrt(((V-An)**2).sum(1))
    Cs = dn/(dp+dn)
    bt = int(np.argmax(Cs)); bg = int(np.argmax(GDP))
    return dict(GDP=GDP, Gini=Gini, CO2=CO2, Sec=Sec, n=len(F),
                topsis=(GDP[bt], Gini[bt], CO2[bt], Sec[bt]),
                growth=(GDP[bg], Gini[bg], CO2[bg], Sec[bg]),
                Xtopsis=Xp[bt].reshape(6, 4), Xgrowth=Xp[bg].reshape(6, 4))


# =====================================================================
# BÀI 8 — Tối ưu động liên thời gian 2026-2035 (SLSQP)
# =====================================================================
def bai8():
    from scipy.optimize import minimize
    a, bc, gd, dai, th = 0.33, 0.42, 0.10, 0.08, 0.07
    dK, dD, dAI, thH, mu = 0.05, 0.12, 0.15, 0.8, 0.02
    p1, p2, p3, rho, gcr = 0.003, 0.002, 0.004, 0.97, 1.5
    T = 10
    K0, L0, D0, AI0, H0, Y0 = 27500.0, 53.9, 20.3, 86.0, 30.0, 12847.6
    A0 = Y0/(K0**a*L0**bc*D0**gd*AI0**dai*H0**th)
    L = np.array([L0*1.009**t for t in range(T+1)])

    def traj(u):
        IK, ID, IAI, IH = u[0::4], u[1::4], u[2::4], u[3::4]
        K = np.zeros(T+1); D = np.zeros(T+1); AI = np.zeros(T+1)
        H = np.zeros(T+1); A = np.zeros(T+1); Y = np.zeros(T+1); C = np.zeros(T)
        K[0], D[0], AI[0], H[0], A[0] = K0, D0, AI0, H0, A0
        for t in range(T):
            Y[t] = A[t]*K[t]**a*L[t]**bc*D[t]**gd*AI[t]**dai*H[t]**th
            C[t] = Y[t]-IK[t]-ID[t]-IAI[t]-IH[t]
            if C[t] <= 0:
                return None
            K[t+1] = (1-dK)*K[t]+IK[t]; D[t+1] = (1-dD)*D[t]+ID[t]
            AI[t+1] = (1-dAI)*AI[t]+IAI[t]; H[t+1] = H[t]+thH*IH[t]-mu*H[t]
            A[t+1] = A[t]*(1+p1*(D[t]/100)+p2*(AI[t]/100)+p3*(H[t]/100))
        Y[T] = A[T]*K[T]**a*L[T]**bc*D[T]**gd*AI[T]**dai*H[T]**th
        return K, D, AI, H, Y, C, A

    def welfare(u):
        r = traj(u)
        if r is None or np.any(r[5] <= 0):
            return 1e15
        C = r[5]
        return -sum(rho**t*(C[t]**(1-gcr)-1)/(1-gcr) for t in range(T))

    inv = 14000*0.15
    u0 = np.tile([inv*0.40, inv*0.25, inv*0.20, inv*0.15], T)
    cons = [{"type": "ineq", "fun": lambda u: (min(traj(u)[5])-1) if traj(u) else -1e10}]
    res = minimize(welfare, u0, method="SLSQP", bounds=[(0, None)]*(T*4),
                   constraints=cons, options={"maxiter": 400, "ftol": 1e-7})
    K, D, AI, H, Y, C, A = traj(res.x)
    years = np.arange(2026, 2026+T+1)

    # 8.3.4 so sánh chiến lược
    u_even = u0.copy()
    u_front = np.zeros(T*4)
    for t in range(T):
        f = 1.5 if t < 3 else 0.7
        u_front[t*4:(t+1)*4] = [inv*0.40*f, inv*0.25*f, inv*0.20*f, inv*0.15*f]
    return dict(years=years, K=K, D=D, AI=AI, H=H, Y=Y, C=C, A=A, W=-res.fun,
                W_even=-welfare(u_even), W_front=-welfare(u_front), u=res.x, T=T)


# =====================================================================
# BÀI 9 — Tác động AI tới thị trường lao động (LP)
# =====================================================================
def bai9():
    from scipy.optimize import linprog
    N = 8
    sectors = ["Nông-LT", "CN chế biến", "Xây dựng", "Bán buôn-lẻ",
               "Tài chính-NH", "Logistics", "CNTT-TT", "Giáo dục-ĐT"]
    L = np.array([13.20, 11.50, 4.80, 7.80, 0.55, 1.95, 0.62, 2.15])
    risk = np.array([18, 42, 25, 38, 52, 35, 28, 22])/100
    a1 = np.array([8.5, 32.5, 12.8, 22.4, 45.8, 28.5, 62.5, 18.5])
    b1 = np.array([45, 28, 35, 32, 22, 30, 20, 55])
    c1 = np.array([5.2, 62.4, 18.5, 48.2, 72.5, 42.8, 32.5, 12.5])
    d1 = np.array([50, 32, 42, 38, 26, 36, 24, 62])
    coeff = a1-c1*risk
    c_obj = np.concatenate([-coeff, -b1])
    A1 = np.concatenate([np.ones(N), np.ones(N)]).reshape(1, -1)
    A1b = np.concatenate([-np.ones(N), np.zeros(N)]).reshape(1, -1)
    A2 = np.zeros((N, 2*N)); A3 = np.zeros((N, 2*N))
    for i in range(N):
        A2[i, i] = -coeff[i]; A2[i, N+i] = -b1[i]
        A3[i, i] = c1[i]*risk[i]; A3[i, N+i] = -d1[i]
    A_ub = np.vstack([A1, A1b, A2, A3])
    b_ub = np.concatenate([[30000], [-9000], np.zeros(N), np.zeros(N)])
    res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)]*(2*N), method="highs")
    xA, xH = res.x[:N], res.x[N:]
    NetJob = coeff*xA + b1*xH
    Displaced = c1*risk*xA

    # 9.4.4 ràng buộc ≤5% L
    A4 = np.zeros((N, 2*N))
    for i in range(N):
        A4[i, i] = c1[i]*risk[i]
    res4 = linprog(c_obj, A_ub=np.vstack([A_ub, A4]),
                   b_ub=np.concatenate([b_ub, 0.05*L*1e6]),
                   bounds=[(0, None)]*(2*N), method="highs")
    tbl = pd.DataFrame({
        "Ngành": sectors, "x_AI": xA.round(0), "x_H": xH.round(0),
        "Displaced": Displaced.round(0), "NetJob": NetJob.round(0)})
    return dict(tbl=tbl, total_netjob=-res.fun, sectors=sectors, L=L,
                netjob_5pct=(-res4.fun if res4.success else None),
                feasible_5pct=res4.success, xA=xA, xH=xH, NetJob=NetJob)


# =====================================================================
# BÀI 10 — Stochastic Programming 2 giai đoạn (VSS/EVPI)
# =====================================================================
def bai10():
    import pyomo.environ as pyo
    J = ["I", "D", "AI", "H"]; S = ["s1", "s2", "s3", "s4"]
    p_s = {"s1": 0.30, "s2": 0.45, "s3": 0.20, "s4": 0.05}
    beta_base = {"I": 1.00, "D": 1.10, "AI": 1.25, "H": 0.95}
    beta_s = {
        ("s1", "I"): 1.25, ("s1", "D"): 1.35, ("s1", "AI"): 1.55, ("s1", "H"): 1.05,
        ("s2", "I"): 1.00, ("s2", "D"): 1.10, ("s2", "AI"): 1.25, ("s2", "H"): 0.95,
        ("s3", "I"): 0.75, ("s3", "D"): 0.85, ("s3", "AI"): 0.90, ("s3", "H"): 1.00,
        ("s4", "I"): 0.40, ("s4", "D"): 0.50, ("s4", "AI"): 0.55, ("s4", "H"): 1.10}

    def solve(m):
        for name in ["appsi_highs", "glpk", "cbc"]:
            try:
                s = pyo.SolverFactory(name)
                if s.available():
                    s.solve(m, tee=False)
                    return
            except Exception:
                continue
        pyo.SolverFactory("glpk").solve(m, tee=False)

    def build(scn=None, fx=None):
        m = pyo.ConcreteModel()
        Sset = S if scn is None else [scn]
        m.J = pyo.Set(initialize=J); m.S = pyo.Set(initialize=Sset)
        if fx is None:
            m.x = pyo.Var(m.J, within=pyo.NonNegativeReals)
            m.b1 = pyo.Constraint(expr=sum(m.x[j] for j in J) <= 65000)
        m.y = pyo.Var(m.S, m.J, within=pyo.NonNegativeReals)
        m.b2 = pyo.Constraint(m.S, rule=lambda mm, s: sum(mm.y[s, j] for j in J) <= 15000)
        xh = (lambda: m.x["H"]) if fx is None else (lambda: fx["H"])
        m.aic = pyo.Constraint(m.S, rule=lambda mm, s: mm.y[s, "AI"] <= 0.5*(mm.x["H"] if fx is None else fx["H"]))

        def obj(mm):
            first = sum(beta_base[j]*(mm.x[j] if fx is None else fx[j]) for j in J)
            second = sum((p_s[s] if scn is None else 1.0)*sum(beta_s[s, j]*mm.y[s, j] for j in J) for s in Sset)
            return first+second
        m.obj = pyo.Objective(rule=obj, sense=pyo.maximize)
        return m

    m_sp = build(); solve(m_sp)
    x_sp = {j: pyo.value(m_sp.x[j]) for j in J}
    Z_SP = pyo.value(m_sp.obj)
    y_sp = {s: {j: pyo.value(m_sp.y[s, j]) for j in J} for s in S}

    det = {}
    for s in S:
        md = build(scn=s); solve(md)
        det[s] = pyo.value(md.obj)
    Z_WS = sum(p_s[s]*det[s] for s in S)

    beta_avg = {j: sum(p_s[s]*beta_s[s, j] for s in S) for j in J}
    m_ev = pyo.ConcreteModel(); m_ev.J = pyo.Set(initialize=J)
    m_ev.x = pyo.Var(m_ev.J, within=pyo.NonNegativeReals)
    m_ev.b = pyo.Constraint(expr=sum(m_ev.x[j] for j in J) <= 65000)
    m_ev.o = pyo.Objective(expr=sum(beta_avg[j]*m_ev.x[j] for j in J), sense=pyo.maximize)
    solve(m_ev)
    x_ev = {j: pyo.value(m_ev.x[j]) for j in J}
    Z_EV = sum(beta_base[j]*x_ev[j] for j in J)
    for s in S:
        mt = build(scn=s, fx=x_ev); solve(mt)
        Z_EV += p_s[s]*sum(beta_s[s, j]*pyo.value(mt.y[s, j]) for j in J)

    return dict(x_sp=x_sp, Z_SP=Z_SP, y_sp=y_sp, x_ev=x_ev, Z_EV=Z_EV,
                Z_WS=Z_WS, VSS=Z_SP-Z_EV, EVPI=Z_WS-Z_SP, det=det, J=J, S=S, p_s=p_s)


# =====================================================================
# BÀI 11 — Q-learning chính sách kinh tế thích nghi
# =====================================================================
def bai11(n_episodes=6000):
    alloc = {0: np.array([0.70, 0.10, 0.10, 0.10]), 1: np.array([0.40, 0.25, 0.15, 0.20]),
             2: np.array([0.25, 0.45, 0.15, 0.15]), 3: np.array([0.20, 0.20, 0.45, 0.15]),
             4: np.array([0.30, 0.20, 0.10, 0.40])}
    names = ["Truyền thống", "Cân bằng", "Số hóa nhanh", "AI dẫn dắt", "Bao trùm"]
    w = np.array([0.40, 0.25, 0.20, 0.15])

    def reset(rng, state=None):
        st = np.array(state) if state is not None else rng.integers(0, 3, 4)
        return dict(state=st, t=0, K=27500.0, D=20.3, AI=86.0, H=30.0, Y_prev=12847.6)

    def step(env, action):
        a = alloc[action]; budget = 2100.0
        env["K"] = 0.95*env["K"]+a[0]*budget
        env["D"] = 0.88*env["D"]+a[1]*budget*0.01
        env["AI"] = 0.85*env["AI"]+a[2]*budget*0.05
        env["H"] = env["H"]+0.8*a[3]*budget*0.01-0.02*env["H"]
        A = 33.70*(1+0.003*(env["D"]/100)+0.002*(env["AI"]/100)+0.004*(env["H"]/100))**env["t"]
        L = 53.9*1.009**env["t"]
        Y = A*env["K"]**0.33*L**0.42*env["D"]**0.10*env["AI"]**0.08*env["H"]**0.07
        dgdp = (Y-env["Y_prev"])/env["Y_prev"]
        dun = max(0, -dgdp*0.5)
        cyber = (env["AI"]/(env["H"]+1))*0.01
        emis = (env["K"]+env["AI"])*0.0001
        r = w[0]*dgdp*100 - w[1]*dun*100 - w[2]*cyber - w[3]*emis
        env["Y_prev"] = Y; env["t"] += 1
        gl = 0 if dgdp < 0.03 else (1 if dgdp < 0.06 else 2)
        dl = 0 if env["D"] < 25 else (1 if env["D"] < 35 else 2)
        al = 0 if env["AI"] < 100 else (1 if env["AI"] < 200 else 2)
        hl = 0 if env["H"] < 35 else (1 if env["H"] < 50 else 2)
        env["state"] = np.array([gl, dl, al, hl])
        return env["state"].copy(), r, env["t"] >= 10

    rng = np.random.default_rng(0)
    Q = np.zeros((3, 3, 3, 3, 5)); hist = []
    for ep in range(n_episodes):
        env = reset(rng); s = env["state"]; tot = 0
        eps = max(0.05, 1-ep/(n_episodes*0.5))
        while True:
            a = rng.integers(5) if rng.random() < eps else int(np.argmax(Q[tuple(s)]))
            s2, r, done = step(env, a)
            Q[tuple(s)+(a,)] += 0.1*(r+0.95*np.max(Q[tuple(s2)])*(1-done)-Q[tuple(s)+(a,)])
            tot += r; s = s2
            if done:
                break
        hist.append(tot)

    test_states = [([1, 1, 0, 1], "VN 2026 (GDP↑med, D med, AI low, H med)"),
                   ([0, 0, 0, 2], "Xấu (GDP low, D low, AI low, H high)"),
                   ([2, 2, 2, 2], "Tốt (mọi chỉ số cao)"),
                   ([0, 1, 0, 0], "Sau khủng hoảng (GDP low, H low)"),
                   ([1, 0, 2, 1], "AI mạnh, D yếu")]
    policy = [(d, names[int(np.argmax(Q[tuple(s)]))]) for s, d in test_states]

    def evalp(fn, n=300):
        out = []
        for _ in range(n):
            env = reset(rng); s = env["state"]; t = 0
            while True:
                s, r, done = step(env, fn(s)); t += r
                if done:
                    break
            out.append(t)
        return np.mean(out)
    comp = {"π* (Q-learning)": evalp(lambda s: int(np.argmax(Q[tuple(s)]))),
            "Luôn Cân bằng (a1)": evalp(lambda s: 1),
            "Luôn AI dẫn dắt (a3)": evalp(lambda s: 3),
            "Ngẫu nhiên": evalp(lambda s: rng.integers(5))}
    return dict(hist=hist, policy=policy, comp=comp, names=names)


# =====================================================================
# BÀI 12 — AIDEOM-VN tích hợp 6 module
# =====================================================================
def bai12_m1():
    a, b, g, d, th = 0.33, 0.42, 0.10, 0.08, 0.07
    K0, L0, D0, AI0, H0, A0 = 27500, 53.9, 20.3, 86, 30, 33.70
    T = 4; years = list(range(2026, 2031)); budget = 3000

    def fc(alloc):
        K, D, AI, H, A = K0, D0, AI0, H0, A0
        out = [A*K**a*L0**b*D**g*AI**d*H**th]
        for t in range(T):
            K = 0.95*K+alloc["K"]*budget; D = 0.88*D+alloc["D"]*budget*0.01
            AI = 0.85*AI+alloc["AI"]*budget*0.05; H = H+0.8*alloc["H"]*budget*0.01-0.02*H
            A = A*(1+0.003*(D/100)+0.002*(AI/100)+0.004*(H/100))
            L = L0*1.009**(t+1)
            out.append(A*K**a*L**b*D**g*AI**d*H**th)
        return out
    scn = {"S1 Truyền thống": {"K": 0.70, "D": 0.10, "AI": 0.10, "H": 0.10},
           "S2 Số hóa nhanh": {"K": 0.25, "D": 0.45, "AI": 0.15, "H": 0.15},
           "S3 AI dẫn dắt": {"K": 0.20, "D": 0.20, "AI": 0.45, "H": 0.15},
           "S4 Bao trùm": {"K": 0.30, "D": 0.20, "AI": 0.10, "H": 0.40},
           "S5 Tối ưu cân bằng": {"K": 0.25, "D": 0.25, "AI": 0.30, "H": 0.20}}
    return years, {n: fc(al) for n, al in scn.items()}
