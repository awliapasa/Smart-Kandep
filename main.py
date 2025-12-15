import streamlit as st
import pandas as pd

# -----------------------------
# KONFIGURASI HALAMAN
# -----------------------------
st.set_page_config(page_title="Smart Kandep", page_icon="🍲")

# -----------------------------
# 1. INFORMASI IDENTITAS TENANT
# -----------------------------
data_master = [
    {
        "Nama Tenant": "Seblak HoT",
        "Kategori": "Makanan Berat",
        "Rata-rata Harga": 15000,
        "Tags": ["Pedas", "Kuah", "Gurih"]
    },
    {
        "Nama Tenant": "Mie Ayam JayaBaya",
        "Kategori": "Makanan Berat",
        "Rata-rata Harga": 18000,
        "Tags": ["Mie", "Yamin", "Kenyang"]
    },
    {
        "Nama Tenant": "Garboy 88",
        "Kategori": "Minuman",
        "Rata-rata Harga": 10000,
        "Tags": ["Steak", "Aneka Lauk", "Cemilan Gurih"]
    },
    {
        "Nama Tenant": "Bang Doel",
        "Kategori": "Camilan",
        "Rata-rata Harga": 8000,
        "Tags": ["Indomie", "Cepat Saji", "Aneka Minuman", "Jus Buah"]
    },
    {
        "Nama Tenant": "Kantin Bu Eti",
        "Kategori": "Makanan Berat",
        "Rata-rata Harga": 15000,
        "Tags": ["Nasi Rames", "Aneka Lauk", "Nasi Goreng"]
    },
    {
        "Nama Tenant": "Kantin Bundo",
        "Kategori": "Makanan Berat",
        "Rata-rata Harga": 15000,
        "Tags": ["Nasi Padang", "Aneka Lauk"]
    },
    {
        "Nama Tenant": "Kantin Pak Kumis",
        "Kategori": "Makanan Berat",
        "Rata-rata Harga": 15000,
        "Tags": ["Nasi Goreng"]
    },
    {
        "Nama Tenant": "Nasi Rames Bude",
        "Kategori": "Makanan Berat",
        "Rata-rata Harga": 15000,
        "Tags": ["Nasi Rames", "Aneka Lauk"]
    },
    {
        "Nama Tenant": "Watasi (Warkop)",
        "Kategori": "Minuman",
        "Rata-rata Harga": 10000,
        "Tags": ["Indomie", "Kopi"]
    }
]

# Ubah jadi DataFrame (Tabel)
df = pd.DataFrame(data_master)

# -----------------------------
# 1B. LOAD HASIL AI (CSV)
# -----------------------------
try:
    df_ai = pd.read_csv("tenant_loyalty_score.csv")
except FileNotFoundError:
    df_ai = pd.DataFrame(columns=["tenant", "loyalty_score"])

# Input Kategori
kategori_list = ["Semua"] + list(df["Kategori"].unique())
kategori_user = st.sidebar.selectbox("Pilih Kategori", options=kategori_list)

df = df.merge(
    df_ai,
    how="left",
    left_on="Nama Tenant",
    right_on="tenant"
)

df["loyalty_score"] = df["loyalty_score"].fillna(0)
df["sample"] = df["sample"].fillna(0).astype(int)

df["loyalty_score_adj"] = (
    df["loyalty_score"] * (df["sample"] / (df["sample"] + 3))
)
# -----------------------------
# UI & JUDUL
# -----------------------------
st.title("🍊 Smart Kandep")
st.markdown("### Sistem Rekomendasi Tenant Kandep Berbasis AI")
st.markdown("Aplikasi ini membantu kamu memilih makanan berdasarkan **Budget** dan **Popularitas**.")
st.divider()

# -----------------------------
# SIDEBAR: INPUT USER
# -----------------------------
st.sidebar.header("🔍 Filter Pencarian")

# Input Budget
budget_user = st.sidebar.slider(
    "Maksimal Budget (Rp)",
    min_value=5000,
    max_value=30000,
    step=1000,
    value=20000
)

# -----------------------------
# LOGIKA FILTERING (AI SEDERHANA)
# -----------------------------
# 1. Filter berdasarkan Budget
hasil_filter = df[df["Rata-rata Harga"] <= budget_user]

# 2. Filter berdasarkan Kategori (Kalau user tidak pilih 'Semua')
if kategori_user != "Semua":
    hasil_filter = hasil_filter[hasil_filter["Kategori"] == kategori_user]

# 3. Urutkan berdasarkan Rating Tertinggi (Rekomendasi Terbaik)
hasil_rekomendasi = hasil_filter.sort_values(
    by="loyalty_score_adj",
    ascending=False
)

# -----------------------------
# OUTPUT HASIL
# -----------------------------
st.subheader(f"📋 Rekomendasi untuk Budget Rp {budget_user:,}")

def label_kunjungan(score): 
    if score >= 0.7:
        return "🔥 Ramai"
    elif score >= 0.4:
        return "🙂 Cukup Ramai"
    else:
        return "😴 Sepi"

if hasil_rekomendasi.empty:
    st.warning("Yah, tidak ada tenant yang sesuai budget kamu. Coba naikkan sedikit!")
else:
    # Tampilkan pakai Kartu (Container)
    for index, row in hasil_rekomendasi.iterrows():
        with st.container():
            # Buat layout kolom: Kiri (Info), Kanan (Skor)
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"🍴 {row['Nama Tenant']}")
                st.caption(f"Kategori: {row['Kategori']}")
                st.write(f"💰 Harga: **Rp {row['Rata-rata Harga']:,}**")
                
                # Tampilkan Tags
                tags_str = " ".join([f"`{t}`" for t in row['Tags']])
                st.markdown(tags_str)

            with col2:
                st.metric(
                "Sering dikunjungi", 
                f"⭐{row['loyalty_score_adj']*100:.0f}%"
            )
            st.caption(f"Berdasarkan {int(row['sample'])} responden")
            st.caption(label_kunjungan(row["loyalty_score_adj"]))
            st.divider()

# Footer
st.caption("Prototipe Sistem Rekomendasi - Kelompok 1 Sains Data bismillah")
