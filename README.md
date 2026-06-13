# AIDEOM-VN — AI-Driven Economic Decision Optimization Model for Vietnam

Web app Streamlit giải **12 bài toán mô hình ra quyết định** phát triển kinh tế Việt Nam
trong kỉ nguyên AI, dùng dữ liệu thực 2020–2025. Đồ án Bài tập lớn môn *Các mô hình ra quyết định*.

**Sinh viên:** Lê Trí Hiệp — **MSSV:** 23051240

## Chạy local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Mở `http://localhost:8501`.

## Cấu trúc

```
AIDEOM_VN/
├── app.py                 # Điều hướng, mục lục bên trái, thông tin sinh viên
├── requirements.txt       # Thư viện Python
├── packages.txt           # Solver hệ thống cho Streamlit Cloud (GLPK, CBC)
├── .streamlit/config.toml # Theme tối, accent crimson/pink
├── data/                  # 3 tệp CSV gốc Việt Nam
└── modules/
    ├── core.py            # Lõi tính toán cả 12 bài (cache)
    ├── common.py          # Theme, CSS, helper Plotly
    ├── home.py            # Trang chủ: dữ liệu gốc + nội dung bài tập
    └── bai1.py … bai12.py # Mỗi bài một module, có hàm render()
```

## Nội dung 12 bài

| Cấp độ | Bài | Kỹ thuật chính |
|---|---|---|
| Dễ | 1–3 | Cobb-Douglas + growth accounting, LP scipy, weighted scoring |
| Trung bình | 4–6 | LP PuLP/CBC, MIP knapsack, TOPSIS + Entropy + AHP |
| Khá khó | 7–9 | NSGA-II Pareto (pymoo), tối ưu động SLSQP, LP lao động |
| Khó | 10–12 | Stochastic SP (Pyomo, VSS/EVPI), Q-learning RL, tích hợp 6 module |

**Bài 12** tích hợp 6 module (M1–M6) chia thành **4 tab**: Tổng quan (M1–M2),
Phân bổ (M3), 5 Kịch bản (M6), Cảnh báo rủi ro (M4–M5).

Neo chính sách: Nghị quyết 57-NQ/TW · QĐ 749/127/411/QĐ-TTg.
Dữ liệu: GSO, MoST, MIC, MPI, World Bank, GII 2025.
