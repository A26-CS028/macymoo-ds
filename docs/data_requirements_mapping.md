# Data Requirements Mapping — DS 1 Minggu 1

Status "Tersedia?" adalah hasil pemeriksaan 11 invoice (`invoice_review_notes.md`). Nama tabel di kolom "Sumber di aplikasi" mengikuti data dictionary v1.1 (DS 2, dari skema final `001_init.sql`), berdasarkan ERD yang disetujui Full-Stack. KF = *Keputusan Final* (`docs/macymoo_Keputusan_Final.md`); angka di belakangnya adalah nomor bagian.

| Pertanyaan | Kolom/atribut yang dibutuhkan | Tersedia di invoice? | Sumber di aplikasi | Catatan |
|---|---|---|---|---|
| Omzet per menu per minggu | Menu, varian, qty, harga, harga tambahan opsi, tanggal | **Sebagian** | `order_items`, `order_item_options` (harga tambahan), `orders` (status), `deliveries` (tanggal) | Menu, qty, harga, dan total baris tersedia. Tanggal: hanya tanggal invoice. Bundling tidak dipecah. Diskon tidak dikurangkan per menu (lihat Q1). |
| Porsi per tanggal | Tanggal kirim/masak, item, qty | **Sebagian** | `deliveries`, `order_items` | Tanggal kirim per baris hanya ada di WPH/003. Ada 5 invoice berisi 2 pengiriman. |
| Pesanan diundur/dibatalkan/lewat batas | Status, riwayat status, alasan, waktu kirim tagihan, waktu bayar | **Tidak** | `orders` (status, `pay_timing`, `invoice_sent_at`), `order_events`, `payments` (`paid_at`) | Batas bayar 4 jam, hanya untuk bayar di muka (KF 6, Final). |
| Tagihan belum dibayar | Total tagihan, pembayaran, status bayar, waktu kirim tagihan | **Sebagian kecil** | `orders` (`invoice_sent_at`, `pay_status`, diskon), `payments`, `order_items`, `deliveries` (ongkir) | Status bayar hanya ada di MYM-KPZ ("Lunas"). `invoices` tidak menyimpan nominal; total dihitung dengan rumus Sisa tagihan di data dictionary bagian 18. |
| Opsi kustom | Opsi pesanan | **Tidak ada pada 11 invoice** | `order_item_options`, `menu_options` | Daftar opsi resmi ada di KF 7. |

## Masukan untuk Full-Stack: status setelah ERD disetujui

Skema milik Full-Stack (KF 10). Status kebutuhan analisis yang diajukan DS 1:

| # | Kebutuhan | Status |
|---|---|---|
| 1 | `order_items` terhubung ke `deliveries`, supaya porsi per tanggal kirim bisa dihitung | ✅ Ada (`order_items.delivery_id`) |
| 2 | Penanda **bundling** dan **bonus**, serta harga atau komponen bundling | ⚠️ Sebagian: penanda ada (`item_type`), tetapi bundling disimpan satu baris, jadi komponennya tidak dipecah. L06 juga berlaku untuk data aplikasi. |
| 3 | `orders` menyimpan **waktu kirim tagihan** | ✅ Ada (`orders.invoice_sent_at`) |
| 4 | `order_events` menyimpan tanggal lama, tanggal baru, dan alasan jadwal ulang | ✅ Ada |
| 5 | View Rekap tanpa nama, HP, dan alamat | ✅ Disepakati (KF 10) |

## Daftar metrik awal untuk Minggu 2

| Metrik | Definisi | Dari 11 invoice? |
|---|---|---|
| Omzet ditagih per menu | Σ line_total per menu (tanpa ongkir) | Ya |
| Omzet ditagih per minggu | Σ subtotal per minggu `invoice_date` | Ya (asumsi A01) |
| Total ongkir dan jumlah pengiriman | Σ ongkir; count pengiriman | Ya (asumsi A02) |
| Porsi per tanggal kirim | Σ qty per delivery_date | Sebagian (hanya WPH/003) |
| Rata-rata nilai invoice (AOV) | mean grand_total | Ya |
| Konsentrasi pelanggan | % omzet dari pelanggan teratas | Ya (C01 = 10/11 invoice) |
| Item bonus Rp0 | count item bonus | Ya |
| Kesesuaian harga dengan menu list | harga invoice vs. harga KF 3 | Ya |
| Tagihan terbuka dan umur tagihan | Sisa tagihan (data dictionary bagian 18); umur dari `invoice_sent_at` | Tidak (data aplikasi/dummy) |
| Tingkat jadwal ulang/batal/lewat batas | count per kejadian / total pesanan; lewat batas hanya bayar di muka | Tidak (data aplikasi/dummy) |
| Frekuensi opsi kustom | count per opsi per menu; sebaran tingkat pedas | Tidak (data aplikasi/dummy) |
