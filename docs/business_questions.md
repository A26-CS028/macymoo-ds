# Business Questions — DS 1 Minggu 1

Sumber:
- 11 invoice asli (`invoice/`, Agustus–Oktober 2026). Detailnya ada di `invoice_review_notes.md`.
- *macymoo: Keputusan Final Fitur* (rapat 4 November 2026, versi 6 November 2026), disingkat **KF** (`docs/macymoo_Keputusan_Final.md`). Angka di belakang KF adalah nomor bagian.
- Nama tabel dan kolom aplikasi mengikuti data dictionary v1.1 (DS 2, dari skema final `001_init.sql`), berdasarkan ERD yang disetujui Full-Stack.

Rencana data menurut KF 9.5: analisis memakai **11 invoice asli (dianonimkan) dan data dummy**. Pertanyaan yang tidak bisa dijawab dari invoice nantinya dijawab dari data aplikasi atau data dummy yang diberi label jelas sebagai dummy, bukan dari asumsi.

| Status | Arti |
|---|---|
| ✅ | Dapat dijawab dari 11 invoice |
| ⚠️ | Dapat dijawab sebagian, dengan asumsi yang harus dikonfirmasi |
| ❌ | Tidak dapat dijawab dari 11 invoice; butuh data aplikasi atau dummy |

---

## Q1. Menu mana yang menyumbang omzet terbesar per minggu? — ⚠️

- **Tujuan:** mengetahui menu andalan di antara 4 menu (Mackster Rp35rb, Nutrimac Rp37rb, Wraphoria Rp27rb, Mac Bites Rp25rb — KF 3).
- **Metrik (usulan DS 1, konfirmasi DS 2):** omzet kotor per menu per minggu = Σ(`unit_price` × `quantity`) + Σ(`extra_price` opsi × `quantity`). Juga share omzet per menu (%).
  - Diskon **tidak** dikurangkan, karena diskon hanya tercatat per pesanan (`orders.discount`) dan tidak bisa dibagi ke menu.
  - Ongkir tidak dihitung, dan pesanan Dibatalkan tidak dihitung (KF 9.5).
  - Item tanpa `menu_id` (bundling, bonus, kolaborasi, item bebas seperti "Nutrimac Small") dikelompokkan sebagai **"Lainnya"**, tidak masuk ranking 4 menu.
  - Minggu = Senin–Minggu berdasarkan `deliveries.delivery_date` (lihat D02).
- **Kolom:** menu, varian, qty, harga satuan, total baris, harga tambahan opsi, tanggal kirim, jenis item (menu/bundling/bonus/kolaborasi/item bebas).
- **Keterbatasan invoice:**
  - Tidak ada tanggal kirim (kecuali WPH/003), jadi minggu diambil dari tanggal invoice (A01).
  - Bundling tidak dipecah per komponen.
  - Tidak ada field diskon.
  - 10 dari 11 invoice hanya berisi Wraphoria dari satu pelanggan, sehingga ranking menu belum bermakna.

## Q2. Berapa porsi per tanggal masak, dan hari apa paling padat? — ⚠️

- **Tujuan:** perencanaan kapasitas. Nabila memasak sendiri dan kapasitasnya tidak tetap (KF 1).
- **Metrik:** total porsi per tanggal masak, rata-rata porsi per hari dalam seminggu, dan hari tersibuk.
- **Definisi:** tanggal masak = `deliveries.delivery_date` (A07). Porsi mengikuti D03 dan D05.
- **Kolom:** tanggal kirim per pengiriman, item, qty, satuan.
- **Keterbatasan invoice:**
  - Tanggal masak tidak tercatat.
  - Tanggal kirim per baris hanya ada di WPH/003.
  - WPH/004 dan 006 hanya bertuliskan "Pengiriman 1/2".
  - WPH/007-v3 dan 008 menggabungkan 10 pcs dalam satu baris.
  - Satuan bercampur (pcs/botol/paket).

## Q3. Berapa pesanan diundur, dibatalkan, atau lewat batas bayar, dan apa alasannya? — ❌

- **Tujuan:** memahami gangguan operasional dan risiko pembayaran.
- **Metrik:** jumlah dan persentase pesanan dijadwal ulang, Dibatalkan, dan lewat batas bayar; distribusi alasan.
- **Definisi (KF 6, Final):**
  - Batas bayar = 4 jam setelah Nabila menekan Kirim Tagihan (`orders.invoice_sent_at`). **Hanya untuk pesanan `pay_timing = di_muka`.** Lewat batas hanya menjadi tanda, bukan batal otomatis; dihitung saat query (KF 11).
  - Jadwal ulang dan pembatalan dicatat beserta alasannya di riwayat (`order_events`).
- **Keterbatasan invoice:** invoice tidak memuat status, riwayat, alasan, maupun waktu kirim tagihan. Sumber datanya adalah tabel `orders`, `order_events`, dan `payments` di aplikasi, atau data dummy.

## Q4. Berapa tagihan yang sudah dikirim tetapi belum dibayar? — ❌

- **Tujuan:** memantau tagihan terbuka. Bayar setelah kirim diizinkan untuk pelanggan tertentu (KF 4).
- **Metrik:** jumlah dan nilai tagihan dengan status bayar Belum Bayar atau DP, sisa tagihan, dan umur tagihan (dihitung dari `invoice_sent_at`).
- **Definisi (KF 4–5, Final):** status bayar = Belum Bayar / DP / Lunas / Dikembalikan. Pesanan Selesai dengan status Belum Bayar = tagihan terbuka. Sisa tagihan memakai rumus Sisa tagihan di data dictionary bagian 18 (grand total − pembayaran bersih).
- **Keterbatasan invoice:** hanya MYM-KPZ yang berstatus "Lunas / Final". 10 invoice lain tidak memiliki data pembayaran. Sumber datanya adalah `orders` dan `payments` di aplikasi, atau data dummy. Tabel `invoices` tidak menyimpan nominal.

## Q5. Opsi kustom apa yang paling sering diminta? — ❌

- **Tujuan:** mengetahui opsi yang paling sering muncul di daftar masak, untuk persiapan bahan.
- **Metrik:** frekuensi tiap opsi per menu, dan persentase item yang memakai opsi kustom. Untuk tingkat pedas, yang dilihat adalah sebaran light/medium/spicy (jika pedas wajib dipilih, persentase pemakaiannya selalu 100% dan tidak informatif; menunggu konfirmasi Full-Stack).
- **Opsi resmi (KF 7, Final):**

  | Menu | Opsi |
  |---|---|
  | Mackster | tingkat pedas; tambah keju |
  | Nutrimac | tingkat pedas; tambah keju; tanpa makaroni; tanpa brokoli; ayam dada/paha |
  | Wraphoria | tingkat pedas; tambah keju; ayam dada/paha |
  | Mac Bites | tingkat pedas; tambah keju; ayam dada/paha |

  - Tingkat pedas: light, medium, spicy.
  - Tambah keju: +Rp3.000. Selisih ayam paha vs dada mengikuti harga pasar (diatur Nabila).

- **Keterbatasan invoice:** **tidak ada satu pun catatan atau opsi kustom di 11 invoice.** Pertanyaan ini tidak boleh dijawab dengan angka dari invoice. Sumber datanya adalah `order_item_options` + `menu_options` setelah aplikasi berjalan, atau data dummy (dilabeli sebagai dummy).
