# Data Dictionary macyMOO

**Versi:** 1.2 · **Tanggal:** 12 November 2026 · **Disusun oleh:** DS 2, Tim A26-CS028
**Acuan skema:** `backend/migrations/001_init.sql` repo `A26-CS028/macymoo-fs`, branch `feat/skema-db`, commit `8b21e0e` (10 Nov 2026). Review ERD dinyatakan selesai oleh Full-Stack.
**Acuan lain:** `macymoo_Keputusan_Final.md` (KF), `erd_review_notes.md`, kesepakatan label MooLabel v0.2.
**Database:** PostgreSQL (Neon) · 16 tabel · 91 kolom. Uang = `INTEGER` Rupiah bulat. Waktu = `TIMESTAMPTZ`; tanggal bisnis dihitung zona Asia/Jakarta.

Full-Stack adalah pemilik skema dan migrasi. Nama kolom di dokumen ini mengikuti SQL apa adanya; perubahan kolom harus dikabarkan ke DS agar dokumen ini diperbarui.

## Cara membaca

| Atribut | Arti |
|---|---|
| Table, Field | Nama tabel dan kolom persis seperti di SQL |
| Data type | Tipe data di SQL |
| Description | Arti dan fungsi kolom |
| Example/constraint | Contoh nilai, atau aturan di database (PK, FK, NOT NULL, UNIQUE, CHECK, DEFAULT) |
| Source/relationship | Siapa/apa yang mengisi, atau relasi ke tabel lain |
| Notes | Catatan, asumsi, aturan backend. **PII** = data pribadi |

---

## 1. menus

Daftar menu yang dijual.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| menus | `id` | INTEGER | Identitas menu | PK, identity | Sistem | |
| menus | `name` | TEXT | Nama menu | NOT NULL. Mis. `Mackster`, `Nutrimac`, `Wraphoria`, `Mac Bites` | Nabila (Kelola menu) | Tidak UNIQUE; nama tidak disalin ke `order_items` (T16) |
| menus | `price` | INTEGER | Harga dasar saat ini (Rp) | NOT NULL, CHECK ≥ 0. Mis. `35000` | Nabila | Harga saat pesan disalin ke `order_items.unit_price` |
| menus | `photo_url` | TEXT | URL foto menu | Opsional | Vercel Blob | |
| menus | `is_available` | BOOLEAN | Status tersedia/habis | NOT NULL, DEFAULT `true` | Nabila | |

## 2. menu_options

Opsi kustom per menu dan harga tambahannya.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| menu_options | `id` | INTEGER | Identitas opsi | PK, identity | Sistem | |
| menu_options | `menu_id` | INTEGER | Menu pemilik opsi | FK → `menus.id`, NOT NULL | 1 menu : N opsi | |
| menu_options | `option_group` | TEXT | Kelompok opsi | Mis. `pedas`, `keju`, `ayam`, `tanpa_makaroni`, `tanpa_brokoli` | Nabila | Tanpa CHECK; divalidasi backend (Joi). Dipakai pertanyaan bisnis 5 |
| menu_options | `name` | TEXT | Nama opsi | NOT NULL. Mis. `light`, `medium`, `spicy`, `tambah keju`, `ayam paha` | Nabila | |
| menu_options | `extra_price` | INTEGER | Harga tambahan saat ini (Rp) | NOT NULL, DEFAULT 0, CHECK ≥ 0. Mis. `3000` (tambah keju) | Nabila | Harga paha mengikuti harga pasar (KF 7) |

## 3. orders

Satu baris per pesanan.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| orders | `id` | INTEGER | Identitas pesanan | PK, identity | Sistem | |
| orders | `order_code` | TEXT | Kode pesanan untuk pelanggan | NOT NULL, UNIQUE | Backend | |
| orders | `customer_name` | TEXT | Nama pelanggan | Opsional | Form / MacLab | **PII**. NULL setelah Anonimkan |
| orders | `phone` | TEXT | Nomor HP pelanggan | Opsional, ber-index | Form / MacLab | **PII**. NULL setelah Anonimkan |
| orders | `source` | TEXT | Asal pesanan | NOT NULL, CHECK `web_form`, `admin_form` | Backend | `admin_form` = MacLab |
| orders | `status` | TEXT | Status pesanan | NOT NULL, DEFAULT `Menunggu Konfirmasi`, CHECK `Menunggu Konfirmasi`, `Menunggu Pembayaran`, `Diproses`, `Selesai`, `Dibatalkan` | Backend / Nabila | `Dibatalkan` tidak dihitung omzet |
| orders | `pay_timing` | TEXT | Pilihan waktu bayar | NOT NULL, DEFAULT `di_muka`, CHECK `di_muka`, `setelah_kirim` | Form / Nabila | KF 4 |
| orders | `pay_status` | TEXT | Status bayar (ringkasan) | NOT NULL, DEFAULT `Belum Bayar`, CHECK `Belum Bayar`, `DP`, `Lunas`, `Dikembalikan` | Backend | Sumber kebenaran tetap `payments` |
| orders | `discount` | INTEGER | Potongan harga pesanan (Rp) | NOT NULL, DEFAULT 0, CHECK ≥ 0 | Nabila | |
| orders | `public_token` | TEXT | Token link status/tagihan publik | NOT NULL, UNIQUE | Backend (acak panjang) | Jangan ditampilkan di analisis |
| orders | `invoice_sent_at` | TIMESTAMPTZ | Waktu tombol Kirim Tagihan ditekan | Opsional | Backend | Awal hitungan batas bayar 4 jam |
| orders | `created_at` | TIMESTAMPTZ | Waktu pesanan dibuat | NOT NULL, DEFAULT now() | Sistem | Dipakai sebagai tanggal pesanan. Pesanan MacLab = waktu input Nabila |

## 4. deliveries

Pengiriman per pesanan; satu pesanan bisa punya beberapa pengiriman.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| deliveries | `id` | INTEGER | Identitas pengiriman | PK, identity | Sistem | |
| deliveries | `order_id` | INTEGER | Pesanan pemilik | FK → `orders.id`, NOT NULL | 1 pesanan : N pengiriman | |
| deliveries | `delivery_date` | DATE | Tanggal kirim / tanggal masak | NOT NULL | Form / Nabila | Dasar pertanyaan bisnis 1–2 |
| deliveries | `method` | TEXT | Cara antar | NOT NULL, CHECK `antar_nabila`, `ambil_sendiri` | Form | |
| deliveries | `address` | TEXT | Alamat antar | Opsional (kosong untuk ambil sendiri) | Form | **PII**. NULL setelah Anonimkan |
| deliveries | `shipping_fee` | INTEGER | Ongkir pengiriman ini (Rp) | NOT NULL, DEFAULT 0, CHECK ≥ 0 | Nabila | Satu-satunya tempat ongkir. `ambil_sendiri` = 0 |
| deliveries | `delivery_status` | TEXT | Status kirim | NOT NULL, DEFAULT `Dijadwalkan`, CHECK `Dijadwalkan`, `Terkirim` | Nabila | |
| deliveries | `delivered_at` | TIMESTAMPTZ | Waktu terkirim | Opsional | Backend | |

## 5. order_items

Item dalam pesanan; tiap item menempel ke satu pengiriman.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| order_items | `id` | INTEGER | Identitas item | PK, identity | Sistem | |
| order_items | `order_id` | INTEGER | Pesanan pemilik | FK → `orders.id`, NOT NULL | 1 pesanan : N item | |
| order_items | `delivery_id` | INTEGER | Pengiriman item ini | FK → `deliveries.id`, NOT NULL | 1 pengiriman : N item | Backend memastikan berasal dari pesanan yang sama |
| order_items | `menu_id` | INTEGER | Menu yang dipesan | FK → `menus.id`, opsional | Form / MacLab | Wajib bila `item_type` = `menu` |
| order_items | `item_type` | TEXT | Jenis item | NOT NULL, DEFAULT `menu`, CHECK `menu`, `item_bebas`, `bundling`, `bonus`, `kolaborasi` | Form / MacLab | Pisahkan `bonus` (Rp0) di analisis menu |
| order_items | `custom_name` | TEXT | Nama item non-menu | Wajib bila `menu_id` kosong | MacLab | Mis. produk kolaborasi |
| order_items | `qty` | INTEGER | Jumlah porsi | NOT NULL, CHECK > 0 | Form / MacLab | |
| order_items | `unit_price` | INTEGER | Harga dasar per porsi saat pesan (Rp) | NOT NULL, CHECK ≥ 0 | Disalin dari `menus.price` | Tidak termasuk harga opsi |
| order_items | `note` | TEXT | Catatan bebas pelanggan | Opsional | Form | **Input MooLabel.** Bisa memuat PII jika pelanggan menuliskannya |

## 6. order_item_options

Opsi yang dipilih per item, dengan salinan harga saat pesan.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| order_item_options | `order_item_id` | INTEGER | Item pemilik | FK → `order_items.id`, NOT NULL; PK bersama `menu_option_id` | 1 item : N opsi | |
| order_item_options | `menu_option_id` | INTEGER | Opsi yang dipilih | FK → `menu_options.id`, NOT NULL | | |
| order_item_options | `extra_price` | INTEGER | Harga tambahan opsi saat pesan (Rp) | NOT NULL, CHECK ≥ 0, tanpa default | Disalin dari `menu_options.extra_price` | Backend wajib mengisi (0 bila gratis) |

## 7. order_item_labels

Hasil MooLabel; satu baris per label per item.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| order_item_labels | `id` | INTEGER | Identitas baris label | PK, identity | Sistem | |
| order_item_labels | `order_item_id` | INTEGER | Item yang diberi label | FK → `order_items.id`, NOT NULL; UNIQUE bersama `label` | 1 item : N label | |
| order_item_labels | `label` | TEXT | Nama label | NOT NULL. Salah satu dari 8 label (bagian 17) | Layanan MooLabel (FastAPI) | Tanpa CHECK di DB; divalidasi backend |
| order_item_labels | `model_version` | TEXT | Versi model pemberi label | Opsional. Mis. `linsvm-v1` | Respons API MooLabel | |

## 8. payments

Pembayaran per pesanan: DP, pelunasan, refund.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| payments | `id` | INTEGER | Identitas pembayaran | PK, identity | Sistem | |
| payments | `order_id` | INTEGER | Pesanan yang dibayar | FK → `orders.id`, NOT NULL | 1 pesanan : N pembayaran | |
| payments | `type` | TEXT | Jenis pembayaran | NOT NULL, CHECK `dp`, `pelunasan`, `refund` | Nabila | |
| payments | `method` | TEXT | Metode bayar | NOT NULL, CHECK `qris`, `transfer`, `tunai` | Nabila | |
| payments | `amount` | INTEGER | Nominal (Rp) | NOT NULL, CHECK > 0 | Nabila | Selalu positif; arah dari `type` |
| payments | `paid_at` | TIMESTAMPTZ | Waktu bayar | NOT NULL, DEFAULT now() | Nabila / sistem | |

## 9. invoices

Riwayat penerbitan invoice; tidak menyimpan nominal.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| invoices | `id` | INTEGER | Identitas invoice | PK, identity | Sistem | |
| invoices | `order_id` | INTEGER | Pesanan yang ditagih | FK → `orders.id`, NOT NULL | 1 pesanan : N invoice (revisi) | |
| invoices | `invoice_no` | TEXT | Nomor invoice | NOT NULL; UNIQUE bersama `revision`. Format `INV/YYYYMMDD/MYM/NNN` | Backend | Disimpan tanpa akhiran `-v2` |
| invoices | `revision` | INTEGER | Nomor revisi | NOT NULL, DEFAULT 1, CHECK ≥ 1 | Backend | Revisi tidak menambah omzet |
| invoices | `issued_at` | DATE | Tanggal terbit | NOT NULL | Backend (Asia/Jakarta) | |

## 10. reviews

Satu review per pesanan.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| reviews | `id` | INTEGER | Identitas review | PK, identity | Sistem | |
| reviews | `order_id` | INTEGER | Pesanan yang diulas | FK → `orders.id`, NOT NULL, UNIQUE | 1 pesanan : 0..1 review | |
| reviews | `rating` | INTEGER | Nilai | CHECK 1–5; kosong sampai dikirim | Pelanggan | |
| reviews | `comment` | TEXT | Komentar | Opsional | Pelanggan | Bisa memuat PII |
| reviews | `token` | TEXT | Token tautan review | NOT NULL, UNIQUE | Backend | Hangus setelah review terkirim |
| reviews | `token_expires_at` | TIMESTAMPTZ | Batas berlaku token | NOT NULL | Backend | 7 hari (KF 9.3) |
| reviews | `created_at` | TIMESTAMPTZ | Waktu tautan dibuat | NOT NULL, DEFAULT now() | Sistem | |
| reviews | `moderation_status` | TEXT | Status moderasi | NOT NULL, DEFAULT `pending`, CHECK `pending`, `approved`, `rejected` | Nabila | Hanya `approved` tampil di landing page |

## 11. admin_users

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| admin_users | `id` | INTEGER | Identitas admin | PK, identity | Sistem | |
| admin_users | `username` | TEXT | Nama login | NOT NULL, UNIQUE | Sistem | |
| admin_users | `password_hash` | TEXT | Hash kata sandi | NOT NULL | Backend | Tidak pernah dipakai di analisis |

## 12. order_events

Riwayat kejadian pesanan.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| order_events | `id` | INTEGER | Identitas event | PK, identity | Sistem | |
| order_events | `order_id` | INTEGER | Pesanan terkait | FK → `orders.id`, NOT NULL | 1 pesanan : N event | |
| order_events | `delivery_id` | INTEGER | Pengiriman terkait | FK → `deliveries.id`, opsional | | Diisi untuk `reschedule` satu pengiriman |
| order_events | `admin_id` | INTEGER | Admin pelaku | FK → `admin_users.id`, opsional | | |
| order_events | `event_type` | TEXT | Jenis event | NOT NULL, CHECK `status_change`, `reschedule`, `cancel`, `bill_sent` | Backend | `cancel` juga mengisi `from_status`/`to_status` |
| order_events | `from_status` | TEXT | Status sebelum | CHECK lima status pesanan | Backend | |
| order_events | `to_status` | TEXT | Status sesudah | CHECK lima status pesanan | Backend | |
| order_events | `old_date` | DATE | Tanggal kirim lama | Opsional | Backend | Untuk `reschedule` |
| order_events | `new_date` | DATE | Tanggal kirim baru | Opsional | Backend | Untuk `reschedule` |
| order_events | `reason` | TEXT | Alasan | Opsional | Nabila | Alasan jadwal ulang / batal |
| order_events | `created_at` | TIMESTAMPTZ | Waktu event | NOT NULL, DEFAULT now() | Sistem | |

Lewat batas bayar tidak dicatat sebagai event; dihitung dari `orders.invoice_sent_at` saat dibaca.

## 13. closed_dates

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| closed_dates | `id` | INTEGER | Identitas | PK, identity | Sistem | |
| closed_dates | `closed_date` | DATE | Tanggal tutup (tidak menerima kirim) | NOT NULL, UNIQUE | Nabila | Jadwal kuliah Nabila |
| closed_dates | `reason` | TEXT | Alasan tutup | Opsional | Nabila | |

## 14. settings

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| settings | `key` | TEXT | Nama pengaturan | PK | Nabila / sistem | Mis. info rekening, QRIS, `wa_number` |
| settings | `value` | TEXT | Nilai pengaturan | Opsional | Nabila | |
| settings | key `wa_number` | TEXT (di `value`) | Nomor WhatsApp Nabila, tujuan tombol Kabari Nabila (`wa_link` di `POST /orders` dan `GET /orders/status/{token}`) | `6281234567890`; hanya angka, pola `^62[0-9]{8,13}$` (divalidasi API) | Nabila lewat `PUT /admin/settings` | Belum diisi → `wa_link` `null` dan tombol disembunyikan. Boleh tampil publik; bukan PII pelanggan (KF 8, 12 Nov 2026) |

## 15. chat_logs

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| chat_logs | `id` | INTEGER | Identitas log | PK, identity | Sistem | |
| chat_logs | `user_message` | TEXT | Pertanyaan pengunjung ke MooBot | NOT NULL | Widget MooBot | Bisa memuat PII |
| chat_logs | `bot_reply` | TEXT | Jawaban MooBot | Opsional | Layanan MooBot | |
| chat_logs | `created_at` | TIMESTAMPTZ | Waktu tanya-jawab | NOT NULL, DEFAULT now() | Sistem | Untuk pembersihan log |

## 16. rate_limits

Bukan data bisnis; tidak dipakai untuk analisis.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| rate_limits | `key` | TEXT | Pembatas + hash pengenal | NOT NULL; PK bersama `window_start`. Mis. `order:<hash>` | Backend | Hash IP, bukan IP mentah |
| rate_limits | `window_start` | TIMESTAMPTZ | Awal jendela waktu | NOT NULL | Backend | |
| rate_limits | `hits` | INTEGER | Jumlah permintaan | NOT NULL, DEFAULT 1, CHECK > 0 | Backend | |

---

## 17. Nilai label MooLabel (`order_item_labels.label`)

Sesuai kesepakatan label v0.2 dengan AI Engineer. Urutan sama dengan kolom biner di dataset.

| No | Label | Definisi |
|---|---|---|
| 1 | `saus_terpisah` | Saus atau keju diminta dipisah dari makanan utama |
| 2 | `alergi` | Menyebut alergi atau intoleransi terhadap bahan |
| 3 | `kurangi_bahan` | Bahan/rasa dikurangi atau dihilangkan (termasuk brokoli, makaroni) |
| 4 | `tambah_bahan` | Bahan ditambah atau diperbanyak (termasuk keju) |
| 5 | `kemasan` | Permintaan cara membungkus |
| 6 | `alat_makan` | Sendok, garpu, tisu, termasuk penolakan |
| 7 | `waktu_antar` | Jam atau waktu tiba |
| 8 | `titip_antar` | Penitipan atau serah terima pesanan |

## 18. Rumus turunan

| Nilai | Rumus |
|---|---|
| Total item | `qty × (unit_price + SUM(order_item_options.extra_price))` |
| Total pesanan | `SUM(total item) + SUM(deliveries.shipping_fee) − orders.discount` |
| Pembayaran bersih | `SUM(amount dp + pelunasan) − SUM(amount refund)` |
| Sisa tagihan | `total pesanan − pembayaran bersih` |
| Lewat batas bayar | `pay_timing = 'di_muka'`, `invoice_sent_at + 4 jam < now()`, dan pembayaran bersih = 0 (KF 6) |
| Omzet | Hanya pesanan dengan `status <> 'Dibatalkan'` |

**Hindari hitung ganda:** agregasi `order_item_options`, `order_item_labels`, `payments`, dan `deliveries` per tabel dulu (CTE/subquery) sebelum di-join ke `orders`. Hitung pembatalan dari `orders.status = 'Dibatalkan'`, bukan dari jumlah event.

## 19. Kebutuhan data lima pertanyaan bisnis (koordinasi DS 1)

| Pertanyaan | Tabel/kolom |
|---|---|
| 1. Menu penyumbang omzet terbesar per minggu | `order_items` (`menu_id`, `item_type`, `qty`, `unit_price`), `order_item_options.extra_price`, `deliveries.delivery_date`, `orders.status` |
| 2. Porsi per tanggal masak, hari terpadat | `order_items.qty`, `order_items.delivery_id` → `deliveries.delivery_date` |
| 3. Pesanan diundur, dibatalkan, lewat batas bayar, dan alasannya | `order_events` (`event_type`, `reason`, `old_date`, `new_date`), `orders.status`, `orders.invoice_sent_at`, `payments` |
| 4. Tagihan terkirim tapi belum dibayar | `orders.invoice_sent_at`, `payments`, rumus sisa tagihan |
| 5. Opsi kustom paling sering | `order_item_options` → `menu_options` (`option_group`, `name`) |

## 20. Data pribadi (PII)

`orders.customer_name`, `orders.phone`, `deliveries.address` (di-NULL-kan saat Anonimkan), serta teks bebas `order_items.note`, `reviews.comment`, `chat_logs.user_message` yang bisa memuat data pribadi. Data analisis dan view Rekap tidak boleh memuat kolom ini.

## 21. Keterbatasan skema (diterima)

- Tidak ada `terms_accepted`, `is_anonymized`, `confirmed_at`, `updated_at` di `orders` (T13).
- Nama menu tidak disalin ke `order_items`; mengganti `menus.name` mengubah tampilan pesanan lama (T16).

## 22. Dataset MooLabel (`moolabel_v1.csv`)

File dataset, bukan tabel database. **Seluruh isi sintetis.** Rincian lengkap di `moolabel_documentation.md`.

| Table | Field | Data type | Description | Example/constraint | Source/relationship | Notes |
|---|---|---|---|---|---|---|
| moolabel_v1 | `note_id` | integer | Nomor urut catatan | Unik. Mis. `1` | `generate.py` | |
| moolabel_v1 | `note` | string | Teks catatan mentah | Tidak kosong, bukan "-". Mis. `"sausnya dipisah ya kak"` | Template atau tulisan anggota | Padanan `order_items.note` |
| moolabel_v1 | `template_id` | string | Sumber pola catatan | `T01`–`T96` = template; `M01`, `M02`, … = tulisan anggota | `templates_v1.csv` | Satu `template_id` hanya di satu split |
| moolabel_v1 | `split` | string | Pembagian data | `train` atau `test` | Ditentukan per template | `M##` selalu `test` |
| moolabel_v1 | `saus_terpisah` … `titip_antar` | integer | 8 kolom label biner | 0 atau 1; urutan seperti bagian 17 | Aturan anotasi kesepakatan v0.2 | Padanan baris di `order_item_labels` |

**Jumlah per label dan split (v1, 12 Nov 2026):**

| Label | Train | Test |
|---|---|---|
| `saus_terpisah` | 50 | 22 |
| `alergi` | 43 | 22 |
| `kurangi_bahan` | 50 | 22 |
| `tambah_bahan` | 43 | 22 |
| `kemasan` | 43 | 22 |
| `alat_makan` | 43 | 27 |
| `waktu_antar` | 43 | 22 |
| `titip_antar` | 43 | 22 |
| **Catatan** | **316** | **161** |

Tanpa label 17,0%, multi-label 26,0%. Catatan tulisan anggota (`M##`) belum dimasukkan.

## Riwayat versi

| Versi | Tanggal | Perubahan |
|---|---|---|
| 1.0 | 12 Nov 2026 | Disusun ulang dari `001_init.sql` commit `8b21e0e` (16 tabel, 91 kolom); menambahkan nilai label MooLabel v0.2, rumus, pemetaan pertanyaan bisnis, dan PII |
| 1.1 | 12 Nov 2026 | Menambahkan bagian 22: kamus kolom dan jumlah dataset MooLabel v1 |
| 1.2 | 12 Nov 2026 | Menambahkan key `wa_number` (nomor WhatsApp Nabila) di `settings`, sesuai perubahan KF 12 Nov 2026 |
