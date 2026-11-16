"""Pembuat data pesanan DUMMY macyMOO (DS 2, Minggu 2).

SELURUH DATA ADALAH DUMMY buatan tim, bukan pesanan asli. Tidak ada nama, HP,
atau alamat asli: nama berbentuk "Pelanggan Dummy NNN", HP kosong, alamat "Alamat dummy".

Acuan:
- Kolom dan enum: docs/data_dictionary.md v1.3 (skema 001_init.sql commit 250911f).
- Perpindahan status: KF bagian 5. Menu dan harga: KF bagian 3. Opsi: KF bagian 7.
- Batas bayar 4 jam setelah Kirim Tagihan: KF bagian 6.

Satu file CSV per tabel (orders_dummy.csv, deliveries_dummy.csv, ...) supaya bisa
di-join seperti tabel database. Kejadian sesudah NOW tidak dibuat, jadi pesanan
terbaru masih berstatus menunggu/diproses.

Jalankan dari root repository:  python3 data/dummy/generate_orders.py
"""
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SEED = 42
N_ORDERS = 180
WIB = ZoneInfo("Asia/Jakarta")
START = datetime(2026, 9, 1, 8, 0, tzinfo=WIB)
NOW = datetime(2026, 11, 15, 20, 0, tzinfo=WIB)  # batas data: tidak ada kejadian sesudah ini
OUT_DIR = Path(__file__).resolve().parent

ORDER_STATUS = ["menunggu_konfirmasi", "menunggu_pembayaran", "diproses", "selesai", "dibatalkan"]
EVENT_TYPES = ["order_created", "confirmed", "bill_sent", "rescheduled",
               "delivery_delivered", "payment_recorded", "cancelled", "completed"]
# KF 5. None = pesanan baru. Perpindahan di luar daftar ini ditolak sistem.
ALLOWED = {
    (None, "menunggu_konfirmasi"),             # form web
    (None, "menunggu_pembayaran"), (None, "diproses"),  # MacLab
    ("menunggu_konfirmasi", "menunggu_pembayaran"),
    ("menunggu_konfirmasi", "diproses"),
    ("menunggu_konfirmasi", "dibatalkan"),
    ("menunggu_pembayaran", "diproses"),
    ("menunggu_pembayaran", "dibatalkan"),
    ("diproses", "dibatalkan"),
    ("diproses", "selesai"),
}

# KF 3
MENUS = [(1, "Mackster", 35000), (2, "Nutrimac", 37000), (3, "Wraphoria", 27000), (4, "Mac Bites", 25000)]
MENU_WEIGHTS = [0.25, 0.20, 0.35, 0.20]
# KF 7. Harga paha mengikuti harga pasar; Rp2.000 hanya angka dummy.
OPTION_GROUPS = {
    "pedas": [("light", 0), ("medium", 0), ("spicy", 0)],
    "keju": [("tambah keju", 3000)],
    "ayam": [("ayam dada", 0), ("ayam paha", 2000)],
    "tanpa_makaroni": [("tanpa makaroni", 0)],
    "tanpa_brokoli": [("tanpa brokoli", 0)],
}
MENU_GROUPS = {
    1: ["pedas", "keju"],
    2: ["pedas", "keju", "tanpa_makaroni", "tanpa_brokoli", "ayam"],
    3: ["pedas", "keju", "ayam"],
    4: ["pedas", "keju", "ayam"],
}
# Item MacLab di luar 4 menu (KF 3, temuan invoice). Harga dummy.
MACLAB_EXTRA = [
    ("item_bebas", "Nutrimac Small", 30000),
    ("bundling", "Paket bundling (dummy)", 60000),
    ("kolaborasi", "Minuman kolaborasi (dummy)", 15000),
]
FEES = [10000, 15000, 20000]
CANCEL_REASONS = {
    "menunggu_konfirmasi": ["Tanggal kirim penuh (dummy)", "Pelanggan minta batal (dummy)"],
    "menunggu_pembayaran": ["Pelanggan minta batal (dummy)"],
}
RESCHEDULE_REASONS = ["Jadwal kuliah Nabila padat (dummy)", "Bahan belum tersedia (dummy)"]


class LewatNow(Exception):
    """Kejadian berikutnya ada sesudah NOW, jadi belum terjadi."""


def hours(rng, lo, hi):
    return timedelta(hours=rng.uniform(lo, hi))


def build_menu_tables():
    menus = [{"id": i, "name": n, "description": "", "price": p, "photo_url": "", "is_available": "true"}
             for i, n, p in MENUS]
    options, by_menu = [], {}
    for menu_id, groups in MENU_GROUPS.items():
        for g in groups:
            for name, extra in OPTION_GROUPS[g]:
                row = {"id": len(options) + 1, "menu_id": menu_id, "option_group": g,
                       "name": name, "extra_price": extra}
                options.append(row)
                by_menu.setdefault((menu_id, g), []).append(row)
    return menus, options, by_menu


def generate(rng):
    menus, menu_options, opt_by_menu = build_menu_tables()
    price = {i: p for i, _, p in MENUS}
    T = {k: [] for k in ["orders", "deliveries", "order_items", "order_item_options", "payments", "order_events"]}
    span = (NOW - START).total_seconds()

    for oid in range(1, N_ORDERS + 1):
        if oid > N_ORDERS - 12:  # pesanan 1,5 hari terakhir, supaya ada yang masih menunggu
            created = NOW - hours(rng, 0.3, 36)
        else:
            created = START + timedelta(seconds=rng.uniform(0, span))
            created = min(created.replace(hour=rng.randint(7, 21)), NOW - timedelta(hours=1))
        maclab = rng.random() < 0.2
        di_muka = rng.random() < 0.8
        order = {"id": oid, "order_code": f"DUMMY-{oid:04d}",
                 "customer_name": f"Pelanggan Dummy {rng.randint(1, 60):03d}", "phone": "",
                 "source": "admin_form" if maclab else "web_form", "status": None,
                 "pay_timing": "di_muka" if di_muka else "setelah_kirim", "pay_status": None,
                 "discount": 5000 if rng.random() < 0.05 else 0,
                 "public_token": f"dummy-token-{oid:04d}", "invoice_sent_at": None,
                 "created_at": created}

        # Pengiriman: form web paling cepat besok (KF 6); MacLab boleh hari H dan beberapa tanggal.
        first = created.date() + timedelta(days=0 if maclab and rng.random() < 0.5 else rng.randint(1, 5))
        dates = [first] + ([first + timedelta(days=rng.randint(2, 7))] if maclab and rng.random() < 0.4 else [])
        dels = []
        for d in dates:
            antar = rng.random() < 0.6
            dels.append({"id": len(T["deliveries"]) + 1, "order_id": oid, "delivery_date": d,
                         "method": "antar_nabila" if antar else "ambil_sendiri",
                         "address": "Alamat dummy" if antar else "",
                         "shipping_fee": rng.choice(FEES) if antar else 0,
                         "delivery_status": "dijadwalkan", "delivered_at": None})
            T["deliveries"].append(dels[-1])

        item_total = 0

        def add_item(delivery_id, menu_id, item_type, custom_name, qty, unit_price):
            nonlocal item_total
            item = {"id": len(T["order_items"]) + 1, "order_id": oid, "delivery_id": delivery_id,
                    "menu_id": menu_id, "item_type": item_type, "custom_name": custom_name,
                    "qty": qty, "unit_price": unit_price, "note": ""}
            T["order_items"].append(item)
            extra = 0
            if item_type == "menu":
                picks = [rng.choice(opt_by_menu[(menu_id, "pedas")])]
                if rng.random() < 0.3:
                    picks += opt_by_menu[(menu_id, "keju")]
                if (menu_id, "ayam") in opt_by_menu and rng.random() < 0.6:
                    picks.append(rng.choice(opt_by_menu[(menu_id, "ayam")]))
                for g in ("tanpa_makaroni", "tanpa_brokoli"):
                    if (menu_id, g) in opt_by_menu and rng.random() < 0.12:
                        picks += opt_by_menu[(menu_id, g)]
                for o in picks:
                    T["order_item_options"].append({"order_item_id": item["id"], "menu_option_id": o["id"],
                                                    "extra_price": o["extra_price"]})
                    extra += o["extra_price"]
            item_total += qty * (unit_price + extra)

        for dl in dels:
            for _ in range(rng.randint(1, 3)):
                m = rng.choices(MENUS, MENU_WEIGHTS)[0][0]
                add_item(dl["id"], m, "menu", "", rng.randint(1, 6 if maclab else 3), price[m])
            if maclab and rng.random() < 0.3:
                add_item(dl["id"], 4, "bonus", "", 2, 0)  # bonus Rp0 (D05)
            if maclab and rng.random() < 0.25:
                kind, name, p = rng.choice(MACLAB_EXTRA)
                add_item(dl["id"], None, kind, name, rng.randint(1, 5), p)
        total = item_total + sum(d["shipping_fee"] for d in dels) - order["discount"]

        # Riwayat status (KF 5). ev() menolak perpindahan yang tidak ada di tabel.
        state = {"status": None, "paid": 0, "refunded": 0}

        def ev(kind, t, to=None, delivery_id=None, old_date=None, new_date=None, reason=None):
            if t > NOW:
                raise LewatNow
            frm = state["status"] if to else None
            if to:
                assert (frm, to) in ALLOWED, (oid, frm, to)
                state["status"] = to
            T["order_events"].append({
                "id": len(T["order_events"]) + 1, "order_id": oid, "delivery_id": delivery_id,
                "admin_id": None if kind == "order_created" and not maclab else 1,
                "event_type": kind, "from_status": frm, "to_status": to,
                "old_date": old_date, "new_date": new_date, "reason": reason, "created_at": t})

        def pay(ptype, t, amount, to=None):
            ev("payment_recorded", t, to=to)
            T["payments"].append({"id": len(T["payments"]) + 1, "order_id": oid, "type": ptype,
                                  "method": rng.choices(["qris", "transfer", "tunai"], [0.5, 0.35, 0.15])[0],
                                  "amount": amount, "paid_at": t})
            if ptype == "refund":
                state["refunded"] += amount
            else:
                state["paid"] += amount

        def cancel(t, reason):
            ev("cancelled", t, to="dibatalkan", reason=reason)
            if state["paid"]:
                pay("refund", t + hours(rng, 2, 30), state["paid"])

        def bill(t):
            ev("bill_sent", t)
            order["invoice_sent_at"] = t

        t = created
        try:
            if maclab:
                ev("order_created", t, to="menunggu_pembayaran" if di_muka else "diproses")
            else:
                ev("order_created", t, to="menunggu_konfirmasi")
                t += hours(rng, 0.5, 6)
                if rng.random() < 0.08:
                    cancel(t, rng.choice(CANCEL_REASONS["menunggu_konfirmasi"]))
                    raise LewatNow
                ev("confirmed", t, to="menunggu_pembayaran" if di_muka else "diproses")

            if state["status"] == "menunggu_pembayaran":
                t += hours(rng, 0.1, 1)
                bill(t)
                r = rng.random()
                if r < 0.06:  # lewat batas bayar 4 jam, Nabila memilih batal
                    cancel(t + hours(rng, 5, 20), "Lewat batas bayar (dummy)")
                    raise LewatNow
                if r < 0.10:
                    cancel(t + hours(rng, 0.5, 3), rng.choice(CANCEL_REASONS["menunggu_pembayaran"]))
                    raise LewatNow
                # Sebagian dibayar lewat batas 4 jam tapi tetap dilanjutkan (KF 6: hanya tanda).
                t += hours(rng, 4.5, 12) if r < 0.15 else hours(rng, 0.2, 3.5)
                if rng.random() < 0.25:
                    pay("dp", t, round(total * 0.5, -3), to="diproses")
                else:
                    pay("pelunasan", t, total, to="diproses")

            # Jadwal ulang satu pengiriman, hanya jika tanggalnya belum lewat.
            dl = rng.choice(dels)
            if rng.random() < 0.10 and t.date() < dl["delivery_date"]:
                t += hours(rng, 1, 10)
                old = dl["delivery_date"]
                dl["delivery_date"] = old + timedelta(days=rng.randint(1, 3))
                ev("rescheduled", t, delivery_id=dl["id"], old_date=old, new_date=dl["delivery_date"],
                   reason=rng.choice(RESCHEDULE_REASONS))
                if rng.random() < 0.3:
                    cancel(t + hours(rng, 1, 8), "Pelanggan menolak jadwal ulang (dummy)")
                    raise LewatNow
            if rng.random() < 0.03:
                cancel(t + hours(rng, 1, 8), "Pelanggan minta refund (dummy)")
                raise LewatNow

            for dl in sorted(dels, key=lambda d: d["delivery_date"]):
                start = datetime.combine(dl["delivery_date"], datetime.min.time(), WIB)
                t = max(start + hours(rng, 10, 16), t + timedelta(minutes=30))
                ev("delivery_delivered", t, delivery_id=dl["id"])
                dl["delivery_status"], dl["delivered_at"] = "terkirim", t
            if 0 < state["paid"] < total:  # sisa DP dilunasi saat terima
                pay("pelunasan", t + timedelta(minutes=5), total - state["paid"])
            t += hours(rng, 1, 4)
            ev("completed", t, to="selesai")

            if not di_muka:  # bayar setelah kirim: tagihan dikirim sesudah selesai
                t += hours(rng, 0.5, 3)
                bill(t)
                if rng.random() < 0.8:
                    pay("pelunasan", t + hours(rng, 2, 96), total)
        except LewatNow:
            pass

        order["status"] = state["status"]
        net = state["paid"] - state["refunded"]
        order["pay_status"] = ("dikembalikan" if state["refunded"] else "belum_bayar" if net == 0
                               else "lunas" if net >= total else "dp")
        T["orders"].append(order)

    T["menus"], T["menu_options"] = menus, menu_options
    return T


def check(T):
    """Cek cepat: enum v1.3, transisi KF 5, dan konsistensi status."""
    assert {o["status"] for o in T["orders"]} == set(ORDER_STATUS), "semua status harus muncul"
    assert {e["event_type"] for e in T["order_events"]} == set(EVENT_TYPES), "8 event_type harus muncul"
    last = {}
    for e in T["order_events"]:
        if e["to_status"]:
            assert (e["from_status"], e["to_status"]) in ALLOWED
            last[e["order_id"]] = e["to_status"]
    for o in T["orders"]:
        assert last[o["id"]] == o["status"], o["id"]
        assert o["pay_status"] in {"belum_bayar", "dp", "lunas", "dikembalikan"}
    assert all(p["amount"] > 0 for p in T["payments"])
    assert sum(e["event_type"] == "cancelled" for e in T["order_events"]) == \
        sum(o["status"] == "dibatalkan" for o in T["orders"]), "satu pembatalan = satu event cancelled"


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, datetime):
        return v.isoformat(timespec="seconds")
    if isinstance(v, date):
        return v.isoformat()
    return v


def main():
    T = generate(random.Random(SEED))
    check(T)
    for name, rows in T.items():
        with open(OUT_DIR / f"{name}_dummy.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows({k: fmt(v) for k, v in r.items()} for r in rows)
        print(f"{name}_dummy.csv: {len(rows)} baris")


if __name__ == "__main__":
    main()
