import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# KONFIGURASI HALAMAN
# -----------------------------
st.set_page_config(page_title="Smart Kandep", page_icon="🍲")

# -----------------------------
# DATA MASTER TENANT
# -----------------------------
data_master = [
    {"Nama Tenant": "Seblak HoT", "Kategori": "Makanan Berat", "Rata-rata Harga": 15000, "Tags": ["Pedas", "Kuah", "Gurih"]},
    {"Nama Tenant": "Mie Ayam JayaBaya", "Kategori": "Makanan Berat", "Rata-rata Harga": 18000, "Tags": ["Mie", "Yamin", "Kenyang"]},
    {"Nama Tenant": "Garboy 88", "Kategori": "Minuman", "Rata-rata Harga": 10000, "Tags": ["Steak", "Aneka Lauk"]},
    {"Nama Tenant": "Bang Doel", "Kategori": "Camilan", "Rata-rata Harga": 8000, "Tags": ["Indomie", "Cepat Saji"]},
    {"Nama Tenant": "Kantin Bu Eti", "Kategori": "Makanan Berat", "Rata-rata Harga": 15000, "Tags": ["Nasi Rames"]},
    {"Nama Tenant": "Kantin Bundo", "Kategori": "Makanan Berat", "Rata-rata Harga": 15000, "Tags": ["Nasi Padang"]},
    {"Nama Tenant": "Kantin Pak Kumis", "Kategori": "Makanan Berat", "Rata-rata Harga": 15000, "Tags": ["Nasi Goreng"]},
    {"Nama Tenant": "Nasi Rames Bude", "Kategori": "Makanan Berat", "Rata-rata Harga": 15000, "Tags": ["Nasi Rames"]},
    {"Nama Tenant": "Watasi (Warkop)", "Kategori": "Minuman", "Rata-rata Harga": 10000, "Tags": ["Indomie", "Kopi"]}
]

df = pd.DataFrame(data_master)

# -----------------------------
# LOAD DATA CSV HASIL SURVEI
# -----------------------------
try:
    df_ai = pd.read_csv("tenant_loyalty_score.csv")
except FileNotFoundError:
    df_ai = pd.DataFrame(columns=["tenant", "loyalty_score", "sample", "avg_spending"])

for col in ["tenant", "loyalty_score", "sample", "avg_spending"]:
    if col not in df_ai.columns:
        df_ai[col] = np.nan

# -----------------------------
# DATA CLEANING
# -----------------------------
df_ai["sample"] = df_ai["sample"].fillna(0).astype(int)
df_ai["loyalty_score"] = df_ai["loyalty_score"].fillna(0.5)
df_ai["avg_spending"] = df_ai["avg_spending"].clip(lower=5000, upper=50000)

# -----------------------------
# SIDEBAR INPUT
# -----------------------------
st.sidebar.header("🔍 Filter Pencarian")

kategori_user = st.sidebar.selectbox(
    "Pilih Kategori",
    ["Semua"] + list(df["Kategori"].unique())
)

budget_user = st.sidebar.slider(
    "Maksimal Budget (Rp)",
    5000, 30000, 20000, 1000
)

# -----------------------------
# MERGE DATA
# -----------------------------
df = df.merge(df_ai, how="left", left_on="Nama Tenant", right_on="tenant")

# -----------------------------
# VALIDASI TENANT AMBIGU
# -----------------------------
tenant_tidak_terdaftar = set(df_ai["tenant"].dropna()) - set(df["Nama Tenant"])
if tenant_tidak_terdaftar:
    st.sidebar.warning(
        "⚠️ Data responden mengandung tenant tidak terdaftar: "
        + ", ".join(tenant_tidak_terdaftar)
    )

# -----------------------------
# VALIDASI HARGA
# -----------------------------
df["harga_valid"] = df["Rata-rata Harga"]

mask = (~df["avg_spending"].isna()) & (abs(df["avg_spending"] - df["Rata-rata Harga"]) > 5000)
df.loc[mask, "harga_valid"] = (
    (df.loc[mask, "avg_spending"] + df.loc[mask, "Rata-rata Harga"]) / 2
).astype(int)

# -----------------------------
# BAYESIAN SCORING
# -----------------------------
PRIOR_SCORE = 0.5
PRIOR_WEIGHT = 5

df["final_score"] = (
    (df["sample"] * df["loyalty_score"] + PRIOR_WEIGHT * PRIOR_SCORE)
    / (df["sample"] + PRIOR_WEIGHT)
)

df["confidence"] = np.where(
    df["sample"] >= 5, "Tinggi",
    np.where(df["sample"] >= 3, "Sedang", "Rendah")
)

# -----------------------------
# FILTERING
# -----------------------------
hasil = df[df["harga_valid"] <= budget_user]
if kategori_user != "Semua":
    hasil = hasil[hasil["Kategori"] == kategori_user]

hasil = hasil.sort_values(by="final_score", ascending=False)

# -----------------------------
# UI
# -----------------------------
st.title("🍊 Smart Kandep")
st.markdown("### Sistem Rekomendasi Tenant Kandep Berbasis AI")
st.divider()

def label_kunjungan(score):
    if score >= 0.7:
        return "🔥 Ramai"
    elif score >= 0.4:
        return "🙂 Cukup Ramai"
    else:
        return "😴 Sepi"

st.subheader(f"📋 Rekomendasi untuk Budget Rp {budget_user:,}")

if hasil.empty:
    st.warning("Tidak ada tenant sesuai budget.")
else:
    for _, row in hasil.iterrows():
        with st.container():
            col1, col2 = st.columns([3,1])

            with col1:
                st.subheader(f"🍴 {row['Nama Tenant']}")
                st.caption(f"Kategori: {row['Kategori']}")
                st.write(f"💰 Harga Valid: Rp {row['harga_valid']:,}")
                st.markdown(" ".join(f"`{t}`" for t in row["Tags"]))
                st.caption(label_kunjungan(row["final_score"]))
                st.caption(f"Confidence Data: {row['confidence']}")
                if row["confidence"] == "Rendah":
                    st.caption("⚠️ Data belum cukup representatif")

            with col2:
                st.metric("Probabilitas Dipilih", f"{row['final_score']*100:.0f}%")
                st.caption(f"{row['sample']} responden")

            st.divider()

st.caption("Prototipe Sistem Rekomendasi – Kelompok 1 Sains Data")
