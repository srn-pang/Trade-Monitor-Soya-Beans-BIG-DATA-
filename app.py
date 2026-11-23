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
    page_title="Trade Monitor — Kedelai (Soya Beans)",
    page_icon="🌐",
    layout="wide"
)

st.title("Global Trade Monitor: Analisis & Prediksi Harga Kedelai")
st.markdown(
    "Pantau dari mana kedelai Indonesia berasal, cek negara pengekspor alternatif selain pemasok utama, "
    "perkiraan harga kedelai lokal saat pasokan dunia atau nilai tukar berubah."
)

# ==============================================================================
# 2. LOAD DATA (MASTER DATASET, COMTRADE & HASIL KLASTERING ORANGE)
# ==============================================================================
@st.cache_data
def load_all_data():
    df_master = pd.read_csv("Master_Dataset.csv")
    df_master["Tanggal"] = pd.to_datetime(df_master["Period"].astype(str), format="%Y%m")
    df_master["Harga_Dunia_2Bln_Lalu"] = df_master["Harga_Global_USD_Ton"].shift(2).bfill()

    # Load rincian negara pemasok dari Excel (skiprows=3 karena header ada di baris ke-4)
    df_partners = None
    try:
        import glob
        xlsx_files = glob.glob("*.xlsx")
        if xlsx_files:
            df_comtrade = pd.read_excel(xlsx_files[0], sheet_name="Comtrade_Gabungan", skiprows=3)
            df_partners = df_comtrade[df_comtrade["Partner_Code"] != 0].copy()
    except Exception:
        df_partners = None

    # Fallback otomatis dari data hasil klastering eksportir jika file Excel belum terbaca
    try:
        df_cluster = pd.read_csv("hasil_klaster_negara.csv", skiprows=lambda x: x in [1, 2] if "hasil_klaster" else [])
        df_cluster = df_cluster[~df_cluster["Area"].isin(["string", "discrete", "continuous", "meta", "class", ""])].dropna(subset=["Area"])
        for col in df_cluster.columns:
            if col not in ["Area", "Cluster"]:
                df_cluster[col] = pd.to_numeric(df_cluster[col], errors="ignore")
    except Exception:
        df_cluster = pd.read_csv("Dataset_Orange_Eksportir.csv")
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

    return df_master, df_partners, df_cluster

df, df_partners, df_cluster = load_all_data()

# ==============================================================================
# 3. SIDEBAR FILTER & SIMULATOR DISRUPSI PASOKAN (WHAT-IF ANALYSIS)
# ==============================================================================
st.sidebar.header("Pengaturan & Simulasi Harga")

tahun_list = sorted(df["Tahun"].unique())
selected_years = st.sidebar.slider(
    "Rentang Tahun Historis",
    min_value=int(min(tahun_list)),
    max_value=int(max(tahun_list)),
    value=(int(min(tahun_list)), int(max(tahun_list)))
)

st.sidebar.markdown("---")
st.sidebar.subheader("Simulasi Kondisi Pasar Global")
st.sidebar.caption("Geser parameter berikut untuk menguji sensitivitas harga kedelai domestik Indonesia:")

delta_pasokan = st.sidebar.slider("Perubahan Pasokan Global (%)", -40, 30, 0, step=5)
delta_harga_global = st.sidebar.slider("Perubahan Harga Kedelai Dunia (%)", -30, 60, 0, step=5)
target_hhi = st.sidebar.slider(
    "Tingkat Ketergantungan pada Satu Negara Pemasok",
    min_value=1500,
    max_value=9500,
    value=int(df["Skor_HHI"].iloc[-1]),
    step=250,
    help="Angka tinggi (>7.000) berarti impor hampir semuanya dari AS. Geser ke kiri untuk simulasi jika Indonesia mulai membeli kedelai dari negara lain seperti Brasil dan Kanada."
)
sim_kurs = st.sidebar.slider(
    "Asumsi Kurs USD/IDR (Rp)",
    min_value=13500,
    max_value=19000,
    value=int(round(df["Kurs_USD_IDR"].iloc[-1], -2)),
    step=100
)

df_filtered = df[(df["Tahun"] >= selected_years[0]) & (df["Tahun"] <= selected_years[1])].copy()

# ==============================================================================
# 4. KPI CARDS (RINGKASAN KONDISI TERKINI)
# ==============================================================================
latest = df_filtered.iloc[-1]
prev = df_filtered.iloc[-2] if len(df_filtered) > 1 else latest

col1, col2, col3, col4 = st.columns(4)

with col1:
    vol_delta = ((latest["Volume_Impor_ID_Ton"] - prev["Volume_Impor_ID_Ton"]) / prev["Volume_Impor_ID_Ton"]) * 100
    st.metric(
        label=f"Volume Impor ({int(latest['Period'])})",
        value=f"{latest['Volume_Impor_ID_Ton']:,.0f} Ton",
        delta=f"{vol_delta:+.1f}% vs bln lalu"
    )

with col2:
    hhi_val = latest["Skor_HHI"]
    hhi_status = "High Risk (>2500)" if hhi_val > 2500 else ("Moderate" if hhi_val > 1500 else "Low Risk")
    st.metric(
        label="Indeks Konsentrasi Impor (HHI)",
        value=f"{hhi_val:,.0f}",
        delta=hhi_status,
        delta_color="inverse"
    )

with col3:
    cif_delta = latest["Harga_Impor_CIF_USD_Ton"] - prev["Harga_Impor_CIF_USD_Ton"]
    st.metric(
        label="Harga Impor CIF Pelabuhan",
        value=f"${latest['Harga_Impor_CIF_USD_Ton']:,.2f}/Ton",
        delta=f"{cif_delta:+.2f} USD/Ton",
        delta_color="inverse"
    )

with col4:
    dom_delta = latest["Est_Harga_Domestik_IDR_Kg"] - prev["Est_Harga_Domestik_IDR_Kg"]
    st.metric(
        label="Est. Harga Jual Domestik",
        value=f"Rp {latest['Est_Harga_Domestik_IDR_Kg']:,.0f}/kg",
        delta=f"Rp {dom_delta:+,.0f}/kg",
        delta_color="inverse"
    )

st.markdown("---")

# ==============================================================================
# 5. TAB NAVIGASI ANALISIS
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "Rantai Pasok & Risiko HHI",
    "Profil Negara Pemasok (Klaster Orange)",
    "Prediksi Harga & Simulator Krisis"
])

# ------------------------------------------------------------------------------
# TAB 1: RANTAI PASOK & TRANSMISI HARGA
# ------------------------------------------------------------------------------
with tab1:
    c_left, c_right = st.columns([1.1, 1.3])

    with c_left:
        st.subheader("Matriks Ketergantungan Negara Pemasok")
        if df_partners is not None:
            p_sub = df_partners[(df_partners["Tahun"] >= selected_years[0]) & (df_partners["Tahun"] <= selected_years[1])].copy()
            # Hitung ulang volume dari Net_Weight_Kg agar tidak bergantung pada cache rumus Excel
            p_sub["Volume_Hitung_Ton"] = pd.to_numeric(p_sub["Net_Weight_Kg"], errors="coerce") / 1000.0
            top_p = p_sub.groupby("Negara_Pemasok")["Volume_Hitung_Ton"].sum().sort_values(ascending=False).reset_index()
            top_display = top_p.head(6).copy()
            fig_pie = px.pie(
                top_display,
                names="Negara_Pemasok",
                values="Volume_Hitung_Ton",
                hole=0.45,
                title=f"Pangsa Volume Impor Kedelai Indonesia ({selected_years[0]}–{selected_years[1]})",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            top_orange = df_cluster[df_cluster["Total_Impor_ke_Indonesia_Ton"] > 0].sort_values(
                "Total_Impor_ke_Indonesia_Ton", ascending=False
            ).head(6)
            fig_pie = px.pie(
                top_orange,
                names="Area",
                values="Total_Impor_ke_Indonesia_Ton",
                hole=0.45,
                title="Porsi Negara Pemasok Kedelai Indonesia (2021–2025)",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

    with c_right:
        st.subheader("Dinamika Skor HHI Bulanan Indonesia")
        fig_hhi = go.Figure()
        fig_hhi.add_trace(go.Scatter(
            x=df_filtered["Tanggal"],
            y=df_filtered["Skor_HHI"],
            mode="lines+markers",
            name="Skor HHI Bulanan",
            line=dict(color="#1F3A52", width=2.5)
        ))
        fig_hhi.add_hline(
            y=2500,
            line_dash="dash",
            line_color="#C0392B",
            annotation_text="Ambang Batas Risiko Tinggi (HHI = 2.500)"
        )
        fig_hhi.update_layout(
            title="Tren Konsentrasi Pemasok Impor (Skala 0–10.000)",
            yaxis_title="Skor HHI",
            xaxis_title="Periode",
            height=400
        )
        st.plotly_chart(fig_hhi, use_container_width=True)

    st.subheader("Pergerakan Harga Beli Impor dan Harga Jual Kedelai Lokal")
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(
        x=df_filtered["Tanggal"],
        y=df_filtered["Harga_Impor_CIF_IDR_Kg"],
        name="Harga Impor CIF (Rp/kg)",
        line=dict(color="#2E86C1", width=2)
    ))
    fig_price.add_trace(go.Scatter(
        x=df_filtered["Tanggal"],
        y=df_filtered["Est_Harga_Domestik_IDR_Kg"],
        name="Est. Harga Jual Domestik (Rp/kg)",
        line=dict(color="#D35400", width=2.5)
    ))
    fig_price.update_layout(
        yaxis_title="Harga (Rp / kg)",
        xaxis_title="Periode",
        hovermode="x unified",
        height=380
    )
    st.plotly_chart(fig_price, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2: SEGMENTASI EKSPROTIR GLOBAL (ORANGE CLUSTERING)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Pemetaan Pemasok Alternatif Berdasarkan Hasil Hierarchical Clustering")
    st.markdown(
        "Grafik ini memetakan **25 negara pengekspor kedelai terbesar di dunia** berdasarkan jumlah pasokan ekspor, "
        "harga jual per ton, dan porsi kirimannya ke Indonesia untuk mencari negara pemasok alternatif selain Amerika Serikat."
    )

    fig_scatter = px.scatter(
        df_cluster,
        x="Harga_Ekspor_USD_Ton",
        y="Rata2_Ekspor_Global_Ton",
        size="Rata2_Ekspor_Global_Ton",
        color="Cluster" if "Cluster" in df_cluster.columns else None,
        hover_name="Area",
        log_y=True,
        size_max=55,
        labels={
            "Harga_Ekspor_USD_Ton": "Rata-rata Harga Ekspor (USD/Ton)",
            "Rata2_Ekspor_Global_Ton": "Rata-rata Ekspor Global (Ton - Skala Log)",
            "Cluster": "Klaster Profil Negara"
        },
        title="Peta Posisi Eksportir Kedelai Dunia: Kapasitas Ekspor vs Harga Jual"
    )
    fig_scatter.update_layout(height=460)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("**Tabel Detail Profil Negara Eksportir:**")
    st.dataframe(df_cluster, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 3: MODEL PREDIKSI & SIMULATOR DISRUPSI
# ------------------------------------------------------------------------------
with tab3:
    # Latih Model Regresi (Multiple Linear / Ridge Regression)
    features = ["Pasokan_Global_Ton", "Harga_Dunia_2Bln_Lalu", "Skor_HHI", "Kurs_USD_IDR"]
    target = "Est_Harga_Domestik_IDR_Kg"

    X = df[features]
    y = df[target]

    reg_model = Ridge(alpha=1.0)
    reg_model.fit(X, y)
    y_pred = reg_model.predict(X)

    r2 = r2_score(y, y_pred)
    mape = mean_absolute_percentage_error(y, y_pred) * 100

    # Hitung Nilai Simulasi berdasarkan Slider di Sidebar
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

    st.subheader("1. Hasil Simulasi Skenario Disrupsi Pasokan (What-If Analysis)")
    s1, s2, s3 = st.columns(3)
    s1.metric("Harga Domestik Baseline (Aktual Terakhir)", f"Rp {baseline_harga:,.0f}/kg")
    s2.metric(
        "Prediksi Harga Domestik (Skenario Simulasi)",
        f"Rp {pred_harga_sim:,.0f}/kg",
        delta=f"Rp {diff_rp:+,.0f}/kg ({diff_pct:+.2f}%)",
        delta_color="inverse"
    )
    s3.metric(
        label="Tingkat Akurasi Prediksi",
        value=f"{100 - mape:.1f}%",
        delta=f"Meleset ±{mape:.1f}% (R² = {r2:.2f})",
        delta_color="off"
    )

    st.markdown("---")
    st.subheader("2. Proyeksi Tren Harga Domestik 12 Bulan Ke Depan (Holt-Winters Forecasting)")

    n_months = st.slider("Horizon Proyeksi (Bulan ke Depan)", 3, 24, 12)
    ts_data = df.set_index("Tanggal")[target].asfreq("MS")
    hw_model = ExponentialSmoothing(ts_data, trend="add", seasonal="add", seasonal_periods=12).fit()
    forecast_vals = hw_model.forecast(n_months)

    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(
        x=ts_data.index,
        y=ts_data.values,
        mode="lines",
        name="Data Historis (2021–2025)",
        line=dict(color="#1F3A52", width=2.5)
    ))
    fig_fc.add_trace(go.Scatter(
        x=forecast_vals.index,
        y=forecast_vals.values,
        mode="lines+markers",
        name=f"Proyeksi {n_months} Bulan Ke Depan",
        line=dict(color="#E67E22", width=2.5, dash="dash")
    ))
    fig_fc.update_layout(
        title="Kurva Proyeksi Harga Kedelai Domestik Indonesia (Rp/kg)",
        yaxis_title="Estimasi Harga Domestik (Rp/kg)",
        xaxis_title="Periode",
        hovermode="x unified",
        height=420
    )
    st.plotly_chart(fig_fc, use_container_width=True)
