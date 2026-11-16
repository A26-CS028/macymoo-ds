"""Prototipe Rekap omzet macyMOO (lokal saja, tidak di-deploy).

Jalankan dari root repository:  streamlit run streamlit/app.py
Sumber: data/dummy/*_dummy.csv (DATA DUMMY). Aturan omzet sama dengan
notebooks/02_pertanyaan_bisnis.ipynb: tanpa ongkir, tanpa pesanan dibatalkan,
minggu Senin–Minggu dari deliveries.delivery_date. Tidak menampilkan data pribadi.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).resolve().parent.parent / "data" / "dummy"


@st.cache_data
def load_rekap():
    orders = pd.read_csv(DATA / "orders_dummy.csv", usecols=["id", "status"])  # tanpa kolom PII
    deliveries = pd.read_csv(DATA / "deliveries_dummy.csv", usecols=["id", "order_id", "delivery_date", "shipping_fee"],
                             parse_dates=["delivery_date"])
    items = pd.read_csv(DATA / "order_items_dummy.csv")
    opts = pd.read_csv(DATA / "order_item_options_dummy.csv")

    # Agregasi tabel anak dulu agar tidak terhitung ganda: opsi → item → pengiriman.
    opsi = opts.groupby("order_item_id")["extra_price"].sum()
    items["total_item"] = items["qty"] * (items["unit_price"] + items["id"].map(opsi).fillna(0))
    per_kirim = items.groupby("delivery_id")["total_item"].sum()

    kirim = deliveries.assign(omzet=deliveries["id"].map(per_kirim).fillna(0).astype(int))
    kirim["status"] = kirim["order_id"].map(orders.set_index("id")["status"])
    return kirim


st.set_page_config(page_title="Rekap macyMOO", layout="wide")
st.title("Rekap omzet macyMOO")
st.warning("**DATA DUMMY**: bukan pesanan asli. Prototipe lokal, tidak di-deploy.")

kirim = load_rekap()
valid = kirim[kirim["status"] != "dibatalkan"]

lo, hi = kirim["delivery_date"].min().date(), kirim["delivery_date"].max().date()
with st.sidebar:
    rentang = st.date_input("Tanggal kirim", (lo, hi), min_value=lo, max_value=hi)
    periode = st.radio("Periode", ["Harian", "Mingguan (Senin–Minggu)"])
if len(rentang) != 2:
    st.stop()  # tanggal akhir belum dipilih
mulai, akhir = map(pd.Timestamp, rentang)
dalam = lambda df: df[df["delivery_date"].between(mulai, akhir)]
valid, semua = dalam(valid), dalam(kirim)

kunci = valid["delivery_date"]
if periode.startswith("Mingguan"):
    kunci = kunci - pd.to_timedelta(kunci.dt.day_of_week, unit="D")
rekap = (valid.groupby(kunci)
         .agg(omzet=("omzet", "sum"), ongkir=("shipping_fee", "sum"), pesanan=("order_id", "nunique"))
         .rename_axis("tanggal" if periode == "Harian" else "minggu_mulai")
         .reset_index())

c1, c2, c3, c4 = st.columns(4)
rp = lambda v: f"Rp{v:,.0f}".replace(",", ".")
c1.metric("Omzet (tanpa ongkir)", rp(valid["omzet"].sum()))
c2.metric("Pesanan dihitung", valid["order_id"].nunique())
c3.metric("Ongkir (info, bukan omzet)", rp(valid["shipping_fee"].sum()))
c4.metric("Pesanan dibatalkan", semua.loc[semua["status"] == "dibatalkan", "order_id"].nunique())

st.bar_chart(rekap, x=rekap.columns[0], y="omzet", y_label="Omzet (Rp)")
st.dataframe(rekap, hide_index=True, width="stretch")
st.download_button("Unduh CSV", rekap.to_csv(index=False).encode("utf-8"),
                   file_name=f"rekap_{periode.split()[0].lower()}_dummy.csv", mime="text/csv")
