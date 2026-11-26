import glob
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_percentage_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# ==============================================================================
# 1. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="æ-TRADE // Global Soybean Monitor",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN SYSTEM: AESPA CYBER-CHROME + ANIMATED TOP-RIGHT MINI-DOCK
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

:root {
    --ae-obsidian: #090D16;
    --ae-navy: #111936;
    --ae-cobalt: #2563EB;
    --ae-violet: #7C3AED;
    --ae-lime: #BEF264;
    --ae-bg: #F1F5F9;
    --ae-card: #FFFFFF;
    --ae-text: #0F172A;
    --ae-muted: #475569;
    --ae-border: rgba(15, 23, 42, 0.09);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--ae-text);
}

.stApp {
    background-color: var(--ae-bg);
    background-image:
        radial-gradient(at 6% 4%, rgba(37, 99, 235, 0.07) 0px, transparent 40%),
        radial-gradient(at 94% 6%, rgba(124, 58, 237, 0.07) 0px, transparent 40%);
}

.block-container {
    padding-top: 1.1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1420px;
}

/* Animasi: Overview mengecil ke pojok kanan atas saat pindah modul */
@keyframes shrinkToTopRight {
    0% {
        opacity: 0.25;
        transform: translate(-60px, 36px) scale(1.12);
        transform-origin: top right;
    }
    100% {
        opacity: 1;
        transform: translate(0, 0) scale(1);
        transform-origin: top right;
    }
}

/* Animasi: Overview kembali membesar penuh saat pilih 00 */
@keyframes expandOverview {
    0% {
        opacity: 0.4;
        transform: translate(30px, -18px) scale(0.95);
        transform-origin: top right;
    }
    100% {
        opacity: 1;
        transform: translate(0, 0) scale(1);
        transform-origin: top right;
    }
}

/* Animasi: Halaman modul baru masuk halus ke layar */
@keyframes pageSlideIn {
    0% {
        opacity: 0;
        transform: translateY(16px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-dock-shrink {
    animation: shrinkToTopRight 0.48s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-overview-expand {
    animation: expandOverview 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-page-enter {
    animation: pageSlideIn 0.42s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Sidebar: KWANGYA Midnight Cyber */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090D16 0%, #111A3A 60%, #172554 100%) !important;
    border-right: 1px solid rgba(190, 242, 100, 0.25);
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

section[data-testid="stSidebar"] .stSlider label {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: #E2E8F0 !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(148, 163, 184, 0.22) !important;
}

.ae-sidebar-box {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.32), rgba(124, 58, 237, 0.26));
    border: 1px solid rgba(190, 242, 100, 0.5);
    border-radius: 14px;
    padding: 13px 15px;
    margin-bottom: 14px;
}

.ae-synk-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #BEF264;
    color: #090D16 !important;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    padding: 2px 9px;
    border-radius: 999px;
    margin-bottom: 6px;
}

/* Top Header Cards (Self-Contained High-Contrast Dark Cards) */
.ae-brand-card {
    background: linear-gradient(135deg, #090D16 0%, #131C42 58%, #1D4ED8 100%);
    border: 1.5px solid rgba(190, 242, 100, 0.45);
    border-radius: 18px;
    padding: 16px 22px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.14);
    min-height: 118px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.ae-badge-row {
    display: flex;
    align-items: center;
    gap: 7px;
    flex-wrap: wrap;
    margin-bottom: 7px;
}

.ae-pill-neon {
    background: #BEF264;
    color: #090D16;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    padding: 3px 10px;
    border-radius: 999px;
}

.ae-pill-dark {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.28);
    color: #FFFFFF;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
}

.ae-hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.38rem;
    font-weight: 700;
    color: #FFFFFF !important;
    margin: 0 0 4px 0;
    line-height: 1.2;
}

.ae-hero-sub {
    font-size: 0.83rem;
    color: #CBD5E1 !important;
    margin: 0;
    line-height: 1.4;
}

/* Switcher Dropdown Styling (High Contrast Dark Obsidian) */
div[data-testid="stSelectbox"] > label {
    display: none !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #090D16 !important;
    border: 2px solid #2563EB !important;
    border-radius: 14px !important;
    min-height: 44px !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.1) !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
    fill: #BEF264 !important;
}

.ae-switcher-caption {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: #1E3A8A;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
}

/* Compact Top-Right Mini-Dock HUD (Muncul saat Modul 01/02/03 dipilih) */
.ae-mini-dock {
    background: #090D16;
    border: 1.5px solid #BEF264;
    border-radius: 14px;
    padding: 8px 12px;
    margin-top: 6px;
    box-shadow: 0 6px 18px rgba(9, 13, 22, 0.18);
}

.ae-dock-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.66rem;
    font-weight: 700;
    color: #BEF264;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}

.ae-dock-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
}

.ae-dock-chip {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 9px;
    padding: 4px 7px;
}

.ae-dock-lbl {
    font-size: 0.62rem;
    color: #94A3B8;
    line-height: 1.1;
}

.ae-dock-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    color: #FFFFFF;
    font-variant-numeric: tabular-nums;
    margin-top: 2px;
}

/* Full KPI Cards (Equal Height 164px -> 2 rows + 12px gap = 340px, exact match with left chart!) */
.ae-kpi-card {
    background: #FFFFFF;
    border: 1px solid var(--ae-border);
    border-radius: 16px;
    padding: 14px 16px;
    height: 164px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.ae-kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3.5px;
    background: linear-gradient(90deg, #2563EB, #7C3AED, #84CC16);
}

.ae-kpi-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.ae-kpi-left {
    display: flex;
    align-items: center;
    gap: 9px;
}

.ae-icon-chrome {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: #EEF2FF;
    border: 1px solid rgba(37, 99, 235, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.ae-kpi-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: #334155;
    line-height: 1.25;
}

.ae-kpi-code {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    color: #1D4ED8;
    background: #DBEAFE;
    padding: 2px 8px;
    border-radius: 999px;
}

.ae-kpi-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.38rem;
    font-weight: 700;
    color: #0F172A;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
}

/* Status Pills */
.ae-status-pill {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
}

.st-lime {
    background: #DCFCE7;
    color: #166534;
    border: 1px solid #86EFAC;
}

.st-danger {
    background: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FCA5A5;
}

.st-warn {
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FCD34D;
}

.st-cyber {
    background: #DBEAFE;
    color: #1E40AF;
    border: 1px solid #93C5FD;
}

/* Simulator 3-Card Row (Equal Height) */
.ae-sim-card {
    background: #FFFFFF;
    border: 1px solid var(--ae-border);
    border-radius: 16px;
    padding: 14px 18px;
    height: 122px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 12px;
}

/* Active Page Header Bar */
.ae-page-header {
    background: #FFFFFF;
    border: 1px solid var(--ae-border);
    border-left: 5px solid #2563EB;
    border-radius: 14px;
    padding: 10px 16px;
    margin: 4px 0 14px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
}

.ae-page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.02rem;
    font-weight: 700;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 8px;
}

.ae-page-hint {
    font-size: 0.76rem;
    font-weight: 600;
    color: #475569;
    background: #F1F5F9;
    padding: 4px 10px;
    border-radius: 999px;
}

/* Plotly Chart Container */
div[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid var(--ae-border);
    border-radius: 16px;
    padding: 12px 14px 6px 14px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}

/* Dataframe Container */
div[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border: 1px solid var(--ae-border);
    border-radius: 16px;
    padding: 6px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. IKON VECTOR & HELPER GRAFIK PLOTLY (ANTI-TUMPANG TINDIH)
# ==============================================================================
AE_ICONS = {
    "star": """<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0L14.6 9.4L24 12L14.6 14.6L12 24L9.4 14.6L0 12L9.4 9.4L12 0Z"/></svg>""",
    "box": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>""",
    "shield": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>""",
    "globe": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0891B2" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>""",
    "tag": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1D4ED8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>"""
}

AESPA_PALETTE = ["#2563EB", "#7C3AED", "#65A30D", "#0891B2", "#DB2777", "#D97706"]

def style_aespa_chart(fig, title="", height=320, top_margin=64):
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Space Grotesk, sans-serif", size=14, color="#0F172A"),
            x=0.01,
            y=0.96,
            yanchor="top"
        ),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11.5, color="#0F172A"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        height=height,
        margin=dict(l=24, r=20, t=top_margin, b=28),
        legend=dict(
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(15, 23, 42, 0.12)",
            borderwidth=1,
            font=dict(size=11, color="#0F172A")
        ),
        xaxis=dict(
            showgrid=False,
            linecolor="rgba(15, 23, 42, 0.18)",
            tickfont=dict(color="#334155", size=11),
            title_font=dict(color="#0F172A", size=11.5)
        ),
        yaxis=dict(
            gridcolor="rgba(15, 23, 42, 0.07)",
            zeroline=False,
            tickfont=dict(color="#334155", size=11),
            title_font=dict(color="#0F172A", size=11.5)
        )
    )
    return fig

# ==============================================================================
# 4. LOAD DATA
# ==============================================================================
@st.cache_data
def load_all_data():
    df_master = pd.read_csv("Master_Dataset.csv")
    df_master["Tanggal"] = pd.to_datetime(df_master["Period"].astype(str), format="%Y%m")
    df_master["Harga_Dunia_2Bln_Lalu"] = df_master["Harga_Global_USD_Ton"].shift(2).bfill()

    df_partners = None
    try:
        xlsx_files = glob.glob("*.xlsx")
        if xlsx_files:
            df_comtrade = pd.read_excel(xlsx_files[0], sheet_name="Comtrade_Gabungan", skiprows=3)
            df_partners = df_comtrade[df_comtrade["Partner_Code"] != 0].copy()
    except Exception:
        df_partners = None

    df_raw_orange = None
    try:
        df_raw_orange = pd.read_csv("Dataset_Orange_Eksportir.csv")
    except Exception:
        df_raw_orange = None

    try:
        df_cluster = pd.read_csv("hasil_klaster_negara.csv", skiprows=lambda x: x in [1, 2])
        df_cluster = df_cluster[~df_cluster["Area"].isin(["string", "discrete", "continuous", "meta", "class", ""])].dropna(subset=["Area"]).copy()
        for col in df_cluster.columns:
            if col not in ["Area", "Cluster"]:
                df_cluster[col] = pd.to_numeric(df_cluster[col], errors="coerce")

        if df_raw_orange is not None and "Cluster" in df_cluster.columns:
            df_cluster = pd.merge(
                df_raw_orange,
                df_cluster[["Area", "Cluster"]],
                on="Area",
                how="inner"
            )
    except Exception:
        df_cluster = df_raw_orange.copy()
        conditions = [
            df_cluster["Area"] == "United States of America",
            df_cluster["Area"] == "Brazil",
            df_cluster["Rata2_Ekspor_Global_Ton"] >= 1_000_000,
        ]
        choices = [
            "Kelompok 1: Pemasok Utama Indonesia",
            "Kelompok 2: Raksasa Global (Kandidat Alternatif)",
            "Kelompok 3: Pemasok Menengah & Penyangga",
        ]
        df_cluster["Cluster"] = np.select(conditions, choices, default="Kelompok 4: Eksportir Regional/Khusus")

    exp_vals = pd.to_numeric(df_cluster["Rata2_Ekspor_Global_Ton"], errors="coerce").fillna(0)
    if (exp_vals <= 0).any():
        min_val = exp_vals.min()
        df_cluster["Bubble_Size"] = (exp_vals - min_val) + 1.0
    else:
        df_cluster["Bubble_Size"] = exp_vals

    return df_master, df_partners, df_cluster

df, df_partners, df_cluster = load_all_data()

# ==============================================================================
# 5. SIDEBAR: SYNK CONTROL TERMINAL
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
<div class="ae-sidebar-box">
    <div class="ae-synk-tag">{AE_ICONS['star']} SYNK // CONTROL</div>
    <div style="font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:700; line-height:1.25;">
        Simulasi &amp; Filter Pasar Global
    </div>
</div>
""", unsafe_allow_html=True)

    tahun_list = sorted(df["Tahun"].unique())
    selected_years = st.slider(
        "Rentang Tahun Historis",
        min_value=int(min(tahun_list)),
        max_value=int(max(tahun_list)),
        value=(int(min(tahun_list)), int(max(tahun_list)))
    )

    st.markdown("---")
    st.markdown("**Parameter What-If Disrupsi**")
    st.caption("Geser parameter di bawah untuk menguji sensitivitas harga lokal:")

    delta_pasokan = st.slider("Perubahan Pasokan Global (%)", -40, 30, 0, step=5)
    delta_harga_global = st.slider("Perubahan Harga Dunia (%)", -30, 60, 0, step=5)
    target_hhi = st.slider(
        "Target Skor Ketergantungan (HHI)",
        min_value=1500,
        max_value=9500,
        value=int(df["Skor_HHI"].iloc[-1]),
        step=250,
        help="Geser ke kiri (<2500) untuk simulasi diversifikasi pemasok ke Brasil dan Kanada."
    )
    sim_kurs = st.slider(
        "Asumsi Kurs USD/IDR (Rp)",
        min_value=13500,
        max_value=19000,
        value=int(round(df["Kurs_USD_IDR"].iloc[-1], -2)),
        step=100
    )

df_filtered = df[(df["Tahun"] >= selected_years[0]) & (df["Tahun"] <= selected_years[1])].copy()
latest = df_filtered.iloc[-1]
prev = df_filtered.iloc[-2] if len(df_filtered) > 1 else latest

vol_delta = ((latest["Volume_Impor_ID_Ton"] - prev["Volume_Impor_ID_Ton"]) / prev["Volume_Impor_ID_Ton"]) * 100
hhi_val = latest["Skor_HHI"]
hhi_status = "High Risk (>2500)" if hhi_val > 2500 else ("Moderate" if hhi_val > 1500 else "Low Risk")
hhi_pill = "st-danger" if hhi_val > 2500 else ("st-warn" if hhi_val > 1500 else "st-lime")
cif_delta = latest["Harga_Impor_CIF_USD_Ton"] - prev["Harga_Impor_CIF_USD_Ton"]
dom_delta = latest["Est_Harga_Domestik_IDR_Kg"] - prev["Est_Harga_Domestik_IDR_Kg"]

# ==============================================================================
# 6. HEADER BAR: HERO CARD (KIRI) + DROPDOWN & ANIMATED MINI-DOCK HUD (KANAN)
# ==============================================================================
MODE_OPTIONS = [
    "00 • Overview Utama (Transmisi & KPI)",
    "01 • Rantai Pasok & Risiko HHI",
    "02 • Eksportir Alternatif (Klaster Orange)",
    "03 • Simulator Krisis & Proyeksi"
]

top_left, top_right = st.columns([1.45, 1.0], gap="medium")

with top_left:
    st.markdown(f"""
<div class="ae-brand-card">
    <div class="ae-badge-row">
        <span class="ae-pill-neon">✦ æ-TRADE ENGINE</span>
        <span class="ae-pill-dark">PERIODE {selected_years[0]}–{selected_years[1]}</span>
        <span class="ae-pill-dark">UPDATE {int(latest['Period'])}</span>
    </div>
    <h1 class="ae-hero-title">Global Trade Monitor: Kedelai Indonesia</h1>
    <p class="ae-hero-sub">
        Pantau rantai pasok impor kedelai, petakan eksportir alternatif global, dan simulasikan harga domestik.
    </p>
</div>
""", unsafe_allow_html=True)

with top_right:
    st.markdown("""
<div class="ae-switcher-caption">
    <span>✦ NAVIGASI HALAMAN ANALISIS</span>
    <span>PILIH MODE</span>
</div>
""", unsafe_allow_html=True)

    selected_mode = st.selectbox(
        "Pilih Halaman Analisis",
        options=MODE_OPTIONS,
        index=0,
        label_visibility="collapsed"
    )

    is_overview = (selected_mode == MODE_OPTIONS[0])

    # Jika sedang membuka Modul 01/02/03, Overview mengecil dengan animasi ke pojok kanan atas!
    if not is_overview:
        st.markdown(f"""
<div class="ae-mini-dock animate-dock-shrink">
    <div class="ae-dock-header">
        <span>✦ RINGKASAN TERKINI (DOCKED)</span>
        <span>PILIH 00 UNTUK PERBESAR</span>
    </div>
    <div class="ae-dock-grid">
        <div class="ae-dock-chip">
            <div class="ae-dock-lbl">Vol. Impor</div>
            <div class="ae-dock-num">{latest['Volume_Impor_ID_Ton']/1000:,.1f}K T</div>
        </div>
        <div class="ae-dock-chip">
            <div class="ae-dock-lbl">Skor HHI</div>
            <div class="ae-dock-num" style="color:#FCA5A5;">{hhi_val:,.0f}</div>
        </div>
        <div class="ae-dock-chip">
            <div class="ae-dock-lbl">Harga CIF</div>
            <div class="ae-dock-num">${latest['Harga_Impor_CIF_USD_Ton']:,.1f}</div>
        </div>
        <div class="ae-dock-chip">
            <div class="ae-dock-lbl">Domestik</div>
            <div class="ae-dock-num" style="color:#BEF264;">Rp {latest['Est_Harga_Domestik_IDR_Kg']:,.0f}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:#FFFFFF; border:1px solid rgba(15,23,42,0.08); border-radius:12px; padding:9px 14px; margin-top:6px; font-size:0.78rem; color:#334155;">
    💡 <strong>Tip:</strong> Pilih modul <strong>01</strong>, <strong>02</strong>, atau <strong>03</strong> di dropdown atas—ringkasan di bawah akan otomatis mengecil ke pojok ini.
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. KONTEN UTAMA (LANGSUNG TAMPIL DI LAYAR TANPA SCROLL MANUAL)
# ==============================================================================
if is_overview:
    st.markdown('<div class="animate-overview-expand"></div>', unsafe_allow_html=True)
    ov_left, ov_right = st.columns([1.45, 1.0], gap="medium")

    with ov_left:
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(
            x=df_filtered["Tanggal"],
            y=df_filtered["Harga_Impor_CIF_IDR_Kg"],
            name="Harga Impor CIF (Rp/kg)",
            line=dict(color="#2563EB", width=2.6),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.07)"
        ))
        fig_price.add_trace(go.Scatter(
            x=df_filtered["Tanggal"],
            y=df_filtered["Est_Harga_Domestik_IDR_Kg"],
            name="Est. Harga Domestik (Rp/kg)",
            line=dict(color="#7C3AED", width=2.6)
        ))
        # Height 322 + padding 18 = 340px (sama persis dengan 2 baris kartu KPI di kanan)
        fig_price = style_aespa_chart(
            fig_price,
            "Transmisi Harga Beli Impor ke Harga Jual Domestik (Rp/kg)",
            height=322,
            top_margin=72
        )
        fig_price.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0)
        )
        st.plotly_chart(fig_price, use_container_width=True)

    with ov_right:
        r1_c1, r1_c2 = st.columns(2, gap="small")
        with r1_c1:
            vol_pill = "st-lime" if vol_delta >= 0 else "st-warn"
            st.markdown(f"""
<div class="ae-kpi-card">
    <div class="ae-kpi-top">
        <div class="ae-kpi-left">
            <div class="ae-icon-chrome">{AE_ICONS['box']}</div>
            <div class="ae-kpi-title">Volume Impor<br>({int(latest['Period'])})</div>
        </div>
        <span class="ae-kpi-code">01</span>
    </div>
    <div class="ae-kpi-val">{latest['Volume_Impor_ID_Ton']:,.0f} T</div>
    <span class="ae-status-pill {vol_pill}">{vol_delta:+.1f}% vs bln lalu</span>
</div>
""", unsafe_allow_html=True)

        with r1_c2:
            st.markdown(f"""
<div class="ae-kpi-card">
    <div class="ae-kpi-top">
        <div class="ae-kpi-left">
            <div class="ae-icon-chrome">{AE_ICONS['shield']}</div>
            <div class="ae-kpi-title">Konsentrasi<br>(Skor HHI)</div>
        </div>
        <span class="ae-kpi-code">02</span>
    </div>
    <div class="ae-kpi-val">{hhi_val:,.0f}</div>
    <span class="ae-status-pill {hhi_pill}">{hhi_status}</span>
</div>
""", unsafe_allow_html=True)

        r2_c1, r2_c2 = st.columns(2, gap="small")
        with r2_c1:
            cif_pill = "st-danger" if cif_delta > 0 else "st-lime"
            st.markdown(f"""
<div class="ae-kpi-card">
    <div class="ae-kpi-top">
        <div class="ae-kpi-left">
            <div class="ae-icon-chrome">{AE_ICONS['globe']}</div>
            <div class="ae-kpi-title">Harga Impor<br>CIF Pelabuhan</div>
        </div>
        <span class="ae-kpi-code">03</span>
    </div>
    <div class="ae-kpi-val">${latest['Harga_Impor_CIF_USD_Ton']:,.1f}</div>
    <span class="ae-status-pill {cif_pill}">{cif_delta:+.2f} USD/Ton</span>
</div>
""", unsafe_allow_html=True)

        with r2_c2:
            dom_pill = "st-danger" if dom_delta > 0 else "st-lime"
            st.markdown(f"""
<div class="ae-kpi-card">
    <div class="ae-kpi-top">
        <div class="ae-kpi-left">
            <div class="ae-icon-chrome">{AE_ICONS['tag']}</div>
            <div class="ae-kpi-title">Est. Harga<br>Domestik</div>
        </div>
        <span class="ae-kpi-code">04</span>
    </div>
    <div class="ae-kpi-val">Rp {latest['Est_Harga_Domestik_IDR_Kg']:,.0f}</div>
    <span class="ae-status-pill {dom_pill}">Rp {dom_delta:+,.0f}/kg</span>
</div>
""", unsafe_allow_html=True)

elif selected_mode == MODE_OPTIONS[1]:
    st.markdown(f"""
<div class="ae-page-header animate-page-enter">
    <div class="ae-page-title">{AE_ICONS['star']} {selected_mode}</div>
    <span class="ae-page-hint">Analisis Pangsa Pemasok &amp; Risiko Monopoli Impor</span>
</div>
""", unsafe_allow_html=True)

    t1_left, t1_right = st.columns([1.0, 1.35], gap="medium")

    with t1_left:
        if df_partners is not None:
            p_sub = df_partners[(df_partners["Tahun"] >= selected_years[0]) & (df_partners["Tahun"] <= selected_years[1])].copy()
            p_sub["Volume_Hitung_Ton"] = pd.to_numeric(p_sub["Net_Weight_Kg"], errors="coerce") / 1000.0
            top_p = p_sub.groupby("Negara_Pemasok")["Volume_Hitung_Ton"].sum().sort_values(ascending=False).reset_index()
            top_display = top_p.head(6).copy()
            fig_pie = px.pie(
                top_display,
                names="Negara_Pemasok",
                values="Volume_Hitung_Ton",
                hole=0.55,
                color_discrete_sequence=AESPA_PALETTE
            )
        else:
            top_orange = df_cluster[df_cluster["Total_Impor_ke_Indonesia_Ton"] > 0].sort_values(
                "Total_Impor_ke_Indonesia_Ton", ascending=False
            ).head(6)
            fig_pie = px.pie(
                top_orange,
                names="Area",
                values="Total_Impor_ke_Indonesia_Ton",
                hole=0.55,
                color_discrete_sequence=AESPA_PALETTE
            )

        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(line=dict(color="#FFFFFF", width=2))
        )
        fig_pie = style_aespa_chart(
            fig_pie,
            f"Pangsa Negara Pemasok ({selected_years[0]}–{selected_years[1]})",
            height=380,
            top_margin=54
        )
        fig_pie.update_layout(
            margin=dict(l=16, r=16, t=54, b=56),
            legend=dict(orientation="h", yanchor="top", y=-0.04, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with t1_right:
        fig_hhi = go.Figure()
        fig_hhi.add_trace(go.Scatter(
            x=df_filtered["Tanggal"],
            y=df_filtered["Skor_HHI"],
            mode="lines+markers",
            name="Skor HHI Bulanan",
            line=dict(color="#2563EB", width=2.6),
            marker=dict(size=6, color="#BEF264", line=dict(color="#0F172A", width=1.2)),
            fill="tozeroy",
            fillcolor="rgba(124, 58, 237, 0.08)"
        ))
        fig_hhi.add_hline(
            y=2500,
            line_dash="dash",
            line_width=1.8,
            line_color="#DB2777",
            annotation_text="Batas Risiko Tinggi (2.500)",
            annotation_position="top left",
            annotation_font=dict(color="#9D174D", size=11.5)
        )
        fig_hhi = style_aespa_chart(
            fig_hhi,
            "Dinamika Skor HHI Bulanan (Skala 0–10.000)",
            height=380,
            top_margin=54
        )
        fig_hhi.update_yaxes(title_text="Skor HHI", range=[0, 10500])
        st.plotly_chart(fig_hhi, use_container_width=True)

elif selected_mode == MODE_OPTIONS[2]:
    st.markdown(f"""
<div class="ae-page-header animate-page-enter">
    <div class="ae-page-title">{AE_ICONS['star']} {selected_mode}</div>
    <span class="ae-page-hint">Pemetaan 25 Negara Eksportir Global (Hierarchical Clustering)</span>
</div>
""", unsafe_allow_html=True)

    m2_left, m2_right = st.columns([1.35, 1.0], gap="medium")

    with m2_left:
        use_log_y = bool((df_cluster["Rata2_Ekspor_Global_Ton"] > 0).all())
        fig_scatter = px.scatter(
            df_cluster,
            x="Harga_Ekspor_USD_Ton",
            y="Rata2_Ekspor_Global_Ton",
            size="Bubble_Size",
            color="Cluster" if "Cluster" in df_cluster.columns else None,
            hover_name="Area",
            hover_data={"Bubble_Size": False, "Rata2_Ekspor_Global_Ton": ":,.0f", "Harga_Ekspor_USD_Ton": ":,.2f"},
            log_y=use_log_y,
            size_max=44,
            color_discrete_sequence=AESPA_PALETTE,
            labels={
                "Harga_Ekspor_USD_Ton": "Harga Ekspor (USD/Ton)",
                "Rata2_Ekspor_Global_Ton": "Ekspor Global (Ton)",
                "Cluster": "Klaster"
            }
        )
        fig_scatter.update_traces(marker=dict(line=dict(width=1.3, color="#FFFFFF"), opacity=0.9))
        fig_scatter = style_aespa_chart(
            fig_scatter,
            "Kapasitas Ekspor Global vs Harga Jual (USD/Ton)",
            height=395,
            top_margin=78
        )
        fig_scatter.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with m2_right:
        display_cols = [c for c in df_cluster.columns if c != "Bubble_Size"]
        st.dataframe(df_cluster[display_cols], use_container_width=True, hide_index=True, height=413)

else:
    st.markdown(f"""
<div class="ae-page-header animate-page-enter">
    <div class="ae-page-title">{AE_ICONS['star']} {selected_mode}</div>
    <span class="ae-page-hint">Model Ridge Regression &amp; Proyeksi Holt-Winters</span>
</div>
""", unsafe_allow_html=True)

    features = ["Pasokan_Global_Ton", "Harga_Dunia_2Bln_Lalu", "Skor_HHI", "Kurs_USD_IDR"]
    target = "Est_Harga_Domestik_IDR_Kg"

    X = df[features]
    y = df[target]

    reg_model = Ridge(alpha=1.0)
    reg_model.fit(X, y)
    y_pred = reg_model.predict(X)

    r2 = r2_score(y, y_pred)
    mape = mean_absolute_percentage_error(y, y_pred) * 100

    base_row = df.iloc[-1]
    sim_pasokan = base_row["Pasokan_Global_Ton"] * (1 + delta_pasokan / 100.0)
    sim_harga_global = base_row["Harga_Dunia_2Bln_Lalu"] * (1 + delta_harga_global / 100.0)

    X_sim = pd.DataFrame([{
        "Pasokan_Global_Ton": sim_pasokan,
        "Harga_Dunia_2Bln_Lalu": sim_harga_global,
        "Skor_HHI": float(target_hhi),
        "Kurs_USD_IDR": float(sim_kurs)
    }])

    pred_harga_sim = reg_model.predict(X_sim)[0]
    baseline_harga = base_row[target]
    diff_rp = pred_harga_sim - baseline_harga
    diff_pct = (diff_rp / baseline_harga) * 100

    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        st.markdown(f"""
<div class="ae-sim-card">
    <div style="font-size:0.78rem; font-weight:700; color:#475569;">Harga Domestik Baseline</div>
    <div class="ae-kpi-val">Rp {baseline_harga:,.0f}/kg</div>
    <span class="ae-status-pill st-cyber">Data Aktual Terakhir</span>
</div>
""", unsafe_allow_html=True)

    with s2:
        sim_pill = "st-danger" if diff_rp > 0 else "st-lime"
        st.markdown(f"""
<div class="ae-sim-card" style="background: linear-gradient(135deg, #EFF6FF 0%, #F5F3FF 100%); border: 1.5px solid #2563EB;">
    <div style="font-size:0.78rem; font-weight:700; color:#1E40AF;">Prediksi Skenario Simulasi</div>
    <div class="ae-kpi-val" style="color:#1D4ED8;">Rp {pred_harga_sim:,.0f}/kg</div>
    <span class="ae-status-pill {sim_pill}">Rp {diff_rp:+,.0f}/kg ({diff_pct:+.2f}%)</span>
</div>
""", unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
<div class="ae-sim-card">
    <div style="font-size:0.78rem; font-weight:700; color:#475569;">Akurasi Model Regresi</div>
    <div class="ae-kpi-val">{100 - mape:.1f}%</div>
    <span class="ae-status-pill st-lime">MAPE ±{mape:.1f}% • R² = {r2:.2f}</span>
</div>
""", unsafe_allow_html=True)

    fc_ctrl, fc_chart = st.columns([0.38, 1.62], gap="medium")
    with fc_ctrl:
        st.markdown("""
<div style="background:#FFFFFF; border:1px solid rgba(15,23,42,0.09); border-radius:16px; padding:14px 16px; margin-bottom:10px;">
    <div style="font-family:'Space Grotesk',sans-serif; font-size:0.86rem; font-weight:700; color:#0F172A; margin-bottom:4px;">Horizon Proyeksi</div>
    <div style="font-size:0.76rem; color:#475569;">Atur jumlah bulan ke depan untuk kurva Holt-Winters:</div>
</div>
""", unsafe_allow_html=True)
        n_months = st.slider("Bulan ke Depan", 3, 24, 12)

    with fc_chart:
        ts_data = df.set_index("Tanggal")[target].asfreq("MS")
        hw_model = ExponentialSmoothing(ts_data, trend="add", seasonal="add", seasonal_periods=12).fit()
        forecast_vals = hw_model.forecast(n_months)

        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=ts_data.index,
            y=ts_data.values,
            mode="lines",
            name="Data Historis (2021–2025)",
            line=dict(color="#2563EB", width=2.6)
        ))
        fig_fc.add_trace(go.Scatter(
            x=forecast_vals.index,
            y=forecast_vals.values,
            mode="lines+markers",
            name=f"Proyeksi {n_months} Bulan",
            line=dict(color="#7C3AED", width=2.6, dash="dash"),
            marker=dict(size=6, color="#BEF264", line=dict(color="#0F172A", width=1.2))
        ))
        fig_fc = style_aespa_chart(
            fig_fc,
            "Proyeksi Tren Harga Kedelai Domestik Indonesia (Rp/kg)",
            height=290,
            top_margin=66
        )
        fig_fc.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0)
        )
        st.plotly_chart(fig_fc, use_container_width=True)
