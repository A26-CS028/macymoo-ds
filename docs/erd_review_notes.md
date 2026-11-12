# Catatan Review ERD macymoo: `001_init.sql`

**Status:** v0.3 (selesai). Dikirim ke Full-Stack 10 November 2026; Full-Stack sudah merevisi SQL (lihat bagian 9)
**Tanggal:** 10 November 2026 · **Reviewer:** Daffa (DS 2), Tim A26-CS028
**Objek review:** `001_init.sql` dari Full-Stack (versi awal: 15 tabel, 81 kolom; versi revisi: 15 tabel, 88 kolom)
**Acuan:** `macymoo_Keputusan_Final.md` (KF), Requirements DS 2 Minggu 1 (FR-DS2-01), dan ERD draft v0.1
**Peran DS:** mereview kebutuhan data dan menyampaikan rekomendasi. Perubahan skema dan migrasi tetap dilakukan Full-Stack.

---

## 1. Ringkasan

**Yang sudah sesuai**
- Ke-14 tabel yang disebut KF bagian 10 semuanya ada, ditambah `order_item_options` (total 15).
- Ongkir hanya ada di `deliveries`, dan tidak ada kolom total di `orders` maupun `invoices`. Ini mencegah hitung ganda pada total.
- Satu pesanan dapat punya banyak pengiriman, banyak pembayaran, dan banyak revisi invoice.
- `order_item_labels` berbentuk satu baris per label dan `order_items.note` bernama sama dengan kontrak API MooLabel (KF 9.6), jadi integrasi MooLabel dapat langsung berjalan.
- `reviews.order_id` bersifat `UNIQUE`; `order_events.admin_id` boleh kosong; `chat_logs.created_at` ada untuk pembersihan log.

**Yang perlu diperbaiki**
- SQL ini **bukan salinan ERD v0.1**: 22 dari 100 kolom di ERD v0.1 tidak ada, dan 3 kolom baru muncul (`order_items.custom_price`, `admin_users.role`, `closed_dates.id`). Header file menyebut `erd_macyourmoo`, bukan `erd_draft_v0.1`. Perlu dipastikan ERD mana yang menjadi acuan.
- Ada **4 temuan Prioritas 1** (butuh perbaikan sebelum fitur dibangun di atasnya): item tidak terhubung ke pengiriman, harga opsi tidak disalin (snapshot) dan makna kolom harga ambigu, `order_code` dan `public_token` tidak unik, dan `invoice_no` tidak unik.
- Skema sangat longgar: **0 `CHECK`**, hanya **1 `UNIQUE`** (`reviews.order_id`), dan `NOT NULL` hanya pada kolom FK.

---

## 2. Pemeriksaan terhadap FR-DS2-01

| Tabel | Hal yang diperiksa (requirement) | Status | Catatan |
|---|---|---|---|
| `orders` | Tanggal pesanan, sumber, status, waktu kirim tagihan, waktu bayar | Sebagian | `source`, `status`, `invoice_sent_at` ada. Tanggal pesanan hanya `created_at`. Waktu bayar ada di `payments.paid_at`; `pay_timing` hanya pilihan waktu bayar (T13). |
| `deliveries` | Tanggal, cara antar, alamat, ongkir, status kirim; banyak per pesanan | Sesuai | Semua kolom ada. Perlu `delivered_at` (opsional) dan nilai default ongkir. |
| `order_items` | Opsi terstruktur, catatan bebas, item bebas, bundling, bonus, kolaborasi | Sebagian | Opsi (lewat `order_item_options`), catatan (`note`), dan item bebas (`custom_name`) ada. Bundling, bonus, dan kolaborasi tidak bisa dibedakan (T6). Item tidak terhubung ke pengiriman (T1). |
| `menus` | Nama, foto, tersedia/habis | Sesuai | `name`, `photo_url`, `is_available` ada. |
| `menu_options` | Opsi per menu dan harga tambahan | Sebagian | Tidak ada kelompok opsi (T7). |
| `order_item_labels` | Hubungan label MooLabel dengan item | Sebagian | Relasi benar; belum ada `UNIQUE` dan `model_version` (T8). |
| `payments` | Banyak pembayaran: DP, pelunasan, refund; QRIS, transfer, tunai | Sesuai | Struktur benar; nilai dan tanda `amount` belum dibakukan (T11). |
| `invoices` | Nomor, revisi, tanggal terbit | Sebagian | Kolom ada, tetapi nomor belum dijamin unik (T4). |
| `order_events` | Riwayat status, jadwal ulang, pembatalan, alasan | Sesuai | Pada pesanan multi-pengiriman, belum jelas pengiriman mana yang dijadwalkan ulang (T12). |

---

## 3. Temuan

### Prioritas 1: perbaiki sebelum dipakai

| ID | Lokasi | Temuan | Dasar | Dampak | Rekomendasi |
|---|---|---|---|---|---|
| **T1** | `order_items` | Tidak ada `delivery_id`. Item tidak diketahui masuk pengiriman yang mana. | KF 3 dan 19 (satu invoice merekap beberapa tanggal kirim), 9.2 (daftar masak per tanggal), kasus uji 3; FR-DS2-01 (relasi `deliveries` dan `order_items`) | Porsi per tanggal masak tidak bisa dihitung untuk pesanan multi-pengiriman. Invoice tidak bisa menampilkan rincian per pengiriman. Pertanyaan bisnis 1 dan 2 terganggu. | Tambah `order_items.delivery_id INTEGER REFERENCES deliveries(id)` (`NOT NULL` jika tabel masih kosong). |
| **T2** | `order_items`, `order_item_options` | (a) Harga tambahan opsi tidak disalin saat pesan; harganya hanya ada di `menu_options.extra_price`. (b) `custom_price` dan `unit_price` sama-sama ada, sehingga tidak jelas harga mana yang dipakai. | KF 9.2 ("harga baru hanya berlaku untuk pesanan berikutnya"), KF 7 (harga paha mengikuti harga pasar, diubah Nabila), kasus uji 17; FR-DS2-01 (potensi hitung ganda) | Saat Nabila mengubah harga keju atau ayam, total pesanan lama ikut berubah. Jika `unit_price` sudah memuat harga opsi lalu opsi dijumlahkan lagi dari `menu_options`, total terhitung ganda. | Tambah `order_item_options.extra_price` (salinan harga saat pesan). Putuskan satu aturan: `unit_price` = harga dasar saja, total = `qty * (unit_price + SUM(opsi))`. Hapus `custom_price` atau definisikan jelas bedanya. |
| **T3** | `orders` | `order_code` dan `public_token` tidak `UNIQUE` dan tidak `NOT NULL`. | KF 12 aturan 1 (token acak panjang), kasus uji 6 | Pencarian link status bisa mengembalikan lebih dari satu pesanan, atau mencocokkan token kosong. | Tambah `UNIQUE` pada keduanya dan `NOT NULL`. |
| **T4** | `invoices` | `invoice_no` tidak `UNIQUE`. Tidak ada kolom tanggal atau nomor urut terpisah untuk penomoran harian. | KF 6 (format `INV/YYYYMMDD/MYM/NNN`, reset harian, revisi `-v2`), kasus uji 5 | Dua invoice dapat memperoleh nomor sama, terutama pada serverless dengan permintaan bersamaan. | Tambah `UNIQUE (invoice_no, revision)`, atau `UNIQUE (invoice_no)` bila `-v2` ikut disimpan di nomor. Putuskan satu cara dan dokumentasikan. |

### Prioritas 2: sebaiknya diperbaiki di minggu 1-2

| ID | Lokasi | Temuan | Rekomendasi |
|---|---|---|---|
| **T5** | `reviews` (tambahan) | Tidak ada `created_at` atau `token_expires_at`; `token` tidak `UNIQUE`. Token berlaku 7 hari dan hangus setelah dipakai (KF 9.3, kasus uji 10). | Tambah `created_at`, `token_expires_at`, dan `UNIQUE (token)`. |
| **T6** | `order_items` | Tidak ada `item_type`. Bundling, bonus Rp0, item bebas, dan kolaborasi tidak bisa dibedakan (KF 6, FR-DS2-01). | Tambah `item_type` dengan nilai `menu`, `item_bebas`, `bundling`, `bonus`, `kolaborasi`. Tanpa ini, bonus Rp0 ikut terhitung sebagai item menu di analisis. |
| **T7** | `menu_options` | Hanya `name`; tidak ada kelompok. Tingkat pedas harus tepat satu pilihan (light, medium, spicy), sedangkan tambah keju dan ayam punya aturan lain (KF 7). | Tambah `option_group` (`pedas`, `keju`, `ayam`, `tanpa_makaroni`, `tanpa_brokoli`). Berguna untuk validasi pilihan dan pertanyaan bisnis 5. |
| **T8** | `order_item_labels` | Tanpa `UNIQUE (order_item_id, label)`; tanpa `model_version`. KF 9.6 mengembalikan `model_version`, dan requirement DS 2 menuntut versioning (NFR). | Tambah `UNIQUE (order_item_id, label)` dan `model_version`. `source` (model atau manual) opsional. |
| **T9** | 7 kolom uang | `NUMERIC(12,2)`, padahal KF 9.8 menetapkan uang sebagai Rupiah bulat (integer). Driver `pg` mengembalikan `NUMERIC` sebagai string. | Pakai `INTEGER`, atau pastikan konversi di backend dan jangan ada nilai desimal. |
| **T10** | Seluruh tabel | 0 `CHECK` dan hampir tanpa `NOT NULL`. Nilai status dan enum bebas diisi teks apa saja. | Bakukan nilai (bagian 6) dan tambah `CHECK` atau `NOT NULL` pada kolom kunci: `orders.status`, `orders.source`, `order_items.qty`, `payments.type`, `payments.amount`, `deliveries.delivery_date`. |
| **T11** | `payments` | Nilai `type` dan `method`, serta tanda `amount`, belum ditetapkan. | Aturan usulan: `amount` selalu positif, arah ditentukan `type` (`dp`, `pelunasan`, `refund`). Pembayaran bersih = (DP + pelunasan) - refund. |
| **T12** | `order_events` | `old_date` dan `new_date` tidak menyebut pengiriman mana yang dijadwalkan ulang. | Tambah `delivery_id` (boleh kosong). |

### Prioritas 3: catatan kecil

| ID | Lokasi | Temuan |
|---|---|---|
| **T13** | `orders` | Tidak ada `terms_accepted` (bukti persetujuan Aturan Pemesanan, KF 9.1 dan 12), `is_anonymized` (penanda anonimisasi, KF 9.3), `confirmed_at`, dan `updated_at`. Tanggal pesanan hanya `created_at`; tanyakan apakah cukup untuk pesanan MacLab hari H. |
| **T14** | `admin_users` | `username` tidak `UNIQUE`. Kolom `role` tidak ada di KF; tanyakan kegunaannya (KF hanya menyebut satu admin). |
| **T15** | `closed_dates` | `closed_date` tidak `UNIQUE`, sehingga satu tanggal bisa tertutup ganda. |
| **T16** | `menus`, `order_items` | `menus.name` tidak `UNIQUE` dan tidak ada `updated_at`. Nama menu tidak disalin ke `order_items`, jadi mengganti nama menu mengubah pesanan lama. |
| **T17** | `invoices`, umum | `issued_at` bertipe `DATE`; pastikan tanggal dihitung zona Asia/Jakarta (KF 9.8) agar nomor urut reset tepat tengah malam WIB. ID memakai `INTEGER` (bukan `BIGINT`); cukup untuk skala ini. |
| **T18** | `deliveries` | Tidak ada `delivered_at`; `shipping_fee` tanpa nilai default 0 dan tanpa `CHECK >= 0` (ongkir Rp0 untuk Ambil Sendiri, KF 4). |

---

## 4. Dampak ke lima pertanyaan bisnis dan kasus uji

| Pertanyaan / uji | Bisa dijawab dari skema sekarang? | Kendala |
|---|---|---|
| 1. Menu penyumbang omzet terbesar per minggu | Sebagian | Minggu menurut tanggal kirim butuh T1. Harga opsi berubah mengubah hasil (T2). Bonus tidak bisa dipisah (T6). |
| 2. Porsi per tanggal masak dan hari terpadat | Hanya pesanan satu pengiriman | Butuh T1. |
| 3. Pesanan diundur, dibatalkan, lewat batas bayar, dan alasan | Ya | `order_events`, `invoice_sent_at`, dan `payments`. Pengiriman yang dijadwalkan ulang belum jelas (T12). |
| 4. Tagihan terkirim, belum dibayar | Ya, jika total konsisten | Bergantung pada T2 dan T9. |
| 5. Opsi kustom paling sering | Ya | Ringkasan per kelompok butuh T7. |
| Uji 3 (MacLab, 2 pengiriman, Rp310.000) | Total bisa dicapai (`qty` 10 x 27.000 + 2 x 20.000) | Rincian per pengiriman tidak bisa dibuat (T1). |
| Uji 5 (nomor invoice) | Tidak terjamin | T4. |
| Uji 6 (token salah ditolak) | Tidak terjamin | T3. |
| Uji 10 (review 7 hari) | Tidak bisa | T5. |
| Uji 11 (anonimkan) | Ya (nama, HP, alamat di-NULL-kan) | Tanpa penanda `is_anonymized` (T13). |

---

## 5. Perbedaan nama kolom: ERD v0.1 dan `001_init.sql`

Data dictionary DS mengikuti nama di SQL, karena Full-Stack pemilik skema.

| Tabel | ERD v0.1 | `001_init.sql` |
|---|---|---|
| semua | `order_id`, `menu_id`, `delivery_id`, dst. sebagai PK | `id` |
| `orders` | `customer_phone`, `payment_timing`, `payment_status`, `discount_amount`, `order_date` | `phone`, `pay_timing`, `pay_status`, `discount`, `created_at` (padanan terdekat) |
| `deliveries` | `delivery_method` | `method` |
| `menus` | `base_price` | `price` |
| `menu_options` | `option_value` | `name` |
| `order_items` | `item_name`, `quantity`, `customer_note` | `custom_name` (hanya item bebas), `qty`, `note` |
| `order_item_options` | `option_id` | `menu_option_id` |
| `payments` | `payment_type` | `type` |
| `invoices` | `invoice_number`, `invoice_date`, `seq_no` | `invoice_no`; `invoice_date` dan `seq_no` tidak ada |
| `order_events` | `created_by`, `old_delivery_date`, `new_delivery_date` | `admin_id`, `old_date`, `new_date` |
| `settings` | `setting_key`, `setting_value` | `key`, `value` |
| `chat_logs` | `role`, `message` (satu baris per pesan) | `user_message`, `bot_reply` (satu baris per tanya-jawab) |

**Kolom di ERD v0.1 yang tidak ada di SQL (22):** `orders` (`terms_accepted`, `is_anonymized`, `order_date`, `confirmed_at`, `updated_at`), `deliveries.delivered_at`, `menus.updated_at`, `menu_options` (`option_group`, `is_available`), `order_items` (`delivery_id`, `parent_item_id`, `item_type`), `order_item_options.extra_price`, `order_item_labels` (`source`, `model_version`, `created_at`), `payments` (`recorded_by`, `note`), `invoices` (`invoice_date`, `seq_no`), `reviews` (`token_expires_at`, `created_at`).

---

## 6. Nilai yang perlu dibakukan

| Kolom | Nilai menurut KF |
|---|---|
| `orders.status` | Menunggu Konfirmasi, Menunggu Pembayaran, Diproses, Selesai, Dibatalkan (penulisan persis belum ditetapkan) |
| `orders.source` | web_form dan admin_form (MacLab) |
| `orders.pay_timing` | bayar di muka, bayar setelah kirim |
| `orders.pay_status` | Belum Bayar, DP, Lunas, Dikembalikan |
| `deliveries.method` | Antar Nabila, Ambil Sendiri |
| `deliveries.delivery_status` | Dijadwalkan, Terkirim |
| `payments.type` | DP, pelunasan, refund |
| `payments.method` | QRIS, transfer, tunai |
| `menu_options` pedas | light, medium, spicy |
| `order_events.event_type` | belum ada daftar |
| `reviews.moderation_status` | belum ada daftar |
| `order_item_labels.label` | menunggu daftar label final (DS dan AI Engineer) |

---

## 7. Usulan perubahan (untuk Full-Stack)

Contoh migrasi `002`, hanya untuk Prioritas 1 dan perbaikan murah lainnya. Keputusan akhir ada pada Full-Stack.

```sql
-- P1
ALTER TABLE orders ADD CONSTRAINT orders_order_code_key UNIQUE (order_code);
ALTER TABLE orders ADD CONSTRAINT orders_public_token_key UNIQUE (public_token);
ALTER TABLE order_items ADD COLUMN delivery_id INTEGER REFERENCES deliveries(id);
ALTER TABLE order_item_options ADD COLUMN extra_price NUMERIC(12,2);
ALTER TABLE invoices ADD CONSTRAINT invoices_no_rev_key UNIQUE (invoice_no, revision);

-- P2 (murah, sekalian)
ALTER TABLE order_items ADD COLUMN item_type TEXT;       -- menu | item_bebas | bundling | bonus | kolaborasi
ALTER TABLE menu_options ADD COLUMN option_group TEXT;   -- pedas | keju | ayam | tanpa_makaroni | tanpa_brokoli
ALTER TABLE order_item_labels ADD COLUMN model_version TEXT;
ALTER TABLE order_item_labels ADD CONSTRAINT labels_item_label_key UNIQUE (order_item_id, label);
ALTER TABLE reviews ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE reviews ADD COLUMN token_expires_at TIMESTAMPTZ;
ALTER TABLE reviews ADD CONSTRAINT reviews_token_key UNIQUE (token);
ALTER TABLE order_events ADD COLUMN delivery_id INTEGER REFERENCES deliveries(id);
ALTER TABLE order_items ADD CONSTRAINT order_items_qty_pos CHECK (qty > 0);
ALTER TABLE payments ADD CONSTRAINT payments_amount_pos CHECK (amount > 0);
ALTER TABLE admin_users ADD CONSTRAINT admin_users_username_key UNIQUE (username);
```

Jika tabel masih kosong, `order_items.delivery_id` sebaiknya `NOT NULL`, dan kolom kunci lain bisa langsung diberi `NOT NULL`.

---

## 8. Pertanyaan untuk Full-Stack

1. ERD mana yang menjadi acuan `001_init.sql` ("erd_macyourmoo")? Apakah sama dengan ERD draft v0.1 dari DS, dan apakah file ini versi minimal yang akan dilengkapi `002`?
2. Apakah migrasi sudah dijalankan di Neon? Jika belum, perbaikan T1-T4 paling murah dilakukan sekarang.
3. Setujukah dengan T1-T4? Jika tidak, bagaimana pesanan multi-pengiriman dan harga opsi dicatat?
4. Aturan perhitungan total yang dipakai backend: `unit_price` memuat harga opsi atau tidak? Untuk apa `custom_price`?
5. Tipe uang: `INTEGER` atau tetap `NUMERIC(12,2)`?
6. Penulisan nilai pada bagian 6 (khususnya `orders.status`).
7. Untuk apa `admin_users.role`?

---

## 9. Tindak lanjut: SQL revisi dari Full-Stack (10 November 2026)

Full-Stack mengirim `001_init.sql` revisi (15 tabel, 88 kolom). Header file menyebut skema "direvisi sesuai catatan review DS". Status tiap temuan:

| ID | Status | Keterangan pada SQL revisi |
|---|---|---|
| T1 | Selesai | `order_items.delivery_id INTEGER NOT NULL REFERENCES deliveries(id)`. |
| T2 | Selesai | `order_item_options.extra_price` ditambahkan; `custom_price` dihapus; `unit_price` = harga dasar. Rumus di header: `qty * (unit_price + SUM(extra_price opsi))`. |
| T3 | Selesai | `order_code` dan `public_token` `NOT NULL UNIQUE`. |
| T4 | Selesai | `UNIQUE (invoice_no, revision)`; `invoice_no` disimpan tanpa `-v2`. Nomor urut harian tetap diambil dari `invoice_no`. |
| T5 | Selesai | `reviews`: `token UNIQUE`, `token_expires_at`, `created_at`; `rating` ber-CHECK 1-5. |
| T6 | Selesai | `order_items.item_type` dengan CHECK lima nilai; CHECK `menu_id` atau `custom_name` terisi. |
| T7 | Selesai | `menu_options.option_group`, sengaja tanpa CHECK (divalidasi Joi). |
| T8 | Selesai | `order_item_labels.model_version` dan `UNIQUE (order_item_id, label)`. |
| T9 | Selesai | Semua kolom uang `INTEGER`. |
| T10 | Sebagian | CHECK dan NOT NULL ditambahkan pada status, source, pay_timing, pay_status, method, delivery_status, payments, item_type, moderation_status. Masih terbuka: `order_events.event_type` tanpa CHECK dan tanpa daftar nilai; `from_status` dan `to_status` tanpa CHECK. |
| T11 | Selesai | `payments.type` dan `method` ber-CHECK; `amount > 0`. |
| T12 | Selesai | `order_events.delivery_id` ditambahkan. |
| T13 | Tidak diubah | `terms_accepted`, `is_anonymized`, `confirmed_at`, `updated_at` tetap tidak ada. Prioritas rendah, diterima. |
| T14 | Selesai | `admin_users.username UNIQUE`; kolom `role` dihapus. |
| T15 | Selesai | `closed_dates.closed_date NOT NULL UNIQUE`. |
| T16 | Terbuka | `menus.name` tidak UNIQUE dan nama menu tidak disalin ke item pesanan. Prioritas rendah. |
| T17 | Selesai | Komentar SQL: `issued_at` dihitung zona Asia/Jakarta di backend. |
| T18 | Selesai | `deliveries.delivered_at` ditambahkan; `shipping_fee` default 0 dan CHECK `>= 0`. |

**Jawaban atas pertanyaan bagian 8:** (1) header baru menyebut skema direvisi sesuai catatan review DS; (5) tipe uang menjadi `INTEGER`; (6) nilai status sudah dibakukan lewat CHECK; (7) `role` dihapus. Pertanyaan 2 (apakah migrasi sudah dijalankan di Neon) belum terjawab; header menyatakan skrip "dijalankan sekali, di database kosong".

**Isu yang masih terbuka**
1. Daftar nilai `order_events.event_type` belum ada. Pertanyaan bisnis 3 membutuhkannya untuk membedakan jadwal ulang dan pembatalan.
2. Usulan kecil: tambah `CHECK (item_type <> 'menu' OR menu_id IS NOT NULL)`, karena CHECK yang ada masih meloloskan item bertipe `menu` tanpa `menu_id` asal `custom_name` terisi.
3. `order_item_options.extra_price` bernilai default 0. Backend wajib menyalin harga saat pesan; perlu diuji.
4. T13 dan T16 (prioritas rendah) dicatat sebagai keterbatasan.

## 10. Persetujuan

| Item | Status |
|---|---|
| Review ERD telah dilakukan | Selesai |
| Masukan disampaikan ke Full-Stack | Sudah (10 Nov 2026), disertai file ini |
| Tanggapan Full-Stack | Sudah: SQL direvisi; 15 dari 18 temuan selesai, 1 sebagian, 2 tidak diubah atau terbuka (prioritas rendah) |
| Isu terbuka | `event_type`, saran CHECK `item_type`, T13, T16 |
| Data dictionary mengikuti SQL revisi | Sudah (v0.4, 88 kolom) |
| Persetujuan akhir Full-Stack atas SQL revisi | Menunggu konfirmasi tertulis dari Full-Stack |

## 11. Penutupan review (12 November 2026)

Full-Stack mengirim revisi ketiga `001_init.sql` (branch `feat/skema-db`, commit `8b21e0e`, 16 tabel, 91 kolom). Hasil pengecekan DS (rincian dan screenshot bukti di `Review_Skema_DB_macyMOO.docx`):

- Daftar `order_events.event_type` sudah ada: `status_change`, `reschedule`, `cancel`, `bill_sent`; `from_status` dan `to_status` ber-CHECK.
- `CHECK (item_type <> 'menu' OR menu_id IS NOT NULL)` sudah ditambahkan.
- `order_item_options.extra_price` tanpa default; `orders.pay_timing` default `di_muka`; tabel baru `rate_limits` (bukan data bisnis).
- Status akhir: **16 dari 18 temuan selesai**; T13 dan T16 diterima sebagai keterbatasan.
- Tiga catatan kecil (pembatalan tidak boleh tercatat dua event, `order_item_labels.label` divalidasi backend, merge ke `main`) sudah disampaikan dan **dijawab Full-Stack**.
- Untuk analisis, pembatalan dihitung dari `orders.status = 'Dibatalkan'`.

**Review ERD dinyatakan selesai.** Data dictionary v1.0 mengikuti commit `8b21e0e`.

| Versi | Tanggal | Perubahan |
|---|---|---|
| 0.1 | 10 Nov 2026 | Review awal atas `001_init.sql`. |
| 0.2 | 10 Nov 2026 | Menambahkan tindak lanjut atas SQL revisi Full-Stack. |
| 0.3 | 12 Nov 2026 | Penutupan review: revisi ketiga SQL dicek, catatan terakhir dijawab Full-Stack. |
