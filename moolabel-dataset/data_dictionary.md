# Dokumentasi Dataset MooLabel

**Versi dataset:** v2 · **Tanggal dibuat:** 16 November 2026 (v1: 12 November 2026) · **Disusun oleh:** DS 2, Tim A26-CS028
**Acuan:** kesepakatan label MooLabel v0.3 (`docs/moolabel_label_agreement.md`, disetujui AI Engineer, dikonfirmasi Nabila), `macymoo_Keputusan_Final.md` bagian 9.4 dan 9.6, Requirements DS 2 Minggu 1 (FR-DS2-03 s.d. 06).

> ⚠️ **Seluruh isi dataset adalah DATA SINTETIS (dummy) buatan tim.** Tidak ada catatan pelanggan asli dan tidak ada data pribadi. Dataset ini **tidak mewakili distribusi catatan pelanggan nyata**.

## 1. Tujuan

Melatih dan menguji **MooLabel**, model klasifikasi multi-label yang membaca catatan bebas pelanggan (`order_items.note`) dan menandai permintaan di dalamnya untuk ditampilkan di daftar masak. Model dibangun AI Engineer (TF-IDF kata + char n-gram, Logistic Regression vs Linear SVM, F1-macro dan F1 per label).

## 2. File

| File | Isi |
|---|---|
| `output/moolabel_v2.csv` | **File utama** (sesuai kesepakatan): 540 catatan, kolom `split` |
| `output/moolabel_v1.csv` | Versi sebelumnya (477 catatan); tidak diubah |
| `output/moolabel_v2_train.csv` | Ekspor baris `split = train` (316) dari v2 |
| `output/moolabel_v2_test.csv` | Ekspor baris `split = test` (224) dari v2 |
| `output/moolabel_train.csv`, `output/moolabel_test.csv` | Ekspor v1; tidak diubah |
| `templates.csv` | Daftar 102 template: id, split, label, pola kalimat (untuk audit) |
| `member_notes.csv` | Catatan tulisan anggota (`M##`); saat ini 63 catatan dari `M01`–`M04` |
| `generate.py` | Pembuat dataset (random seed 42, deterministik) |
| `validate.py` | Pemeriksa aturan dataset; wajib lolos sebelum diserahkan |

File v2 (`moolabel_v2.csv`, `_train`, `_test`) berisi data yang sama; tim AI cukup memakai `moolabel_v2.csv`.

## 3. Skema kolom

| Kolom | Tipe | Keterangan |
|---|---|---|
| `note_id` | integer | Nomor urut catatan, unik |
| `note` | string | Teks catatan mentah (huruf besar, singkatan, typo, emoji dibiarkan). Diapit tanda kutip ganda. Preprocessing oleh tim AI |
| `template_id` | string | `T01`–`T102` = template; `M01`, `M02`, … = catatan tulisan anggota (satu ID per penulis) |
| `split` | string | `train` atau `test` |
| 8 kolom label | integer 0/1 | Urutan tetap: `saus_terpisah`, `alergi`, `kurangi_bahan`, `tambah_bahan`, `kemasan`, `alat_makan`, `waktu_antar`, `titip_antar` |

Encoding UTF-8. Tidak ada kolom penanda sintetis (sesuai kesepakatan); status sintetis dinyatakan di dokumen ini.

## 4. Daftar label

| No | Label | Definisi |
|---|---|---|
| 1 | `saus_terpisah` | Saus atau keju diminta dipisah dari makanan utama |
| 2 | `alergi` | Catatan menyebut alergi atau intoleransi terhadap bahan tertentu |
| 3 | `kurangi_bahan` | Bahan atau rasa diminta dikurangi/dihilangkan, termasuk bahan yang punya opsi di form (brokoli, makaroni) |
| 4 | `tambah_bahan` | Bahan diminta ditambah/diperbanyak, termasuk bahan yang punya opsi di form (keju) |
| 5 | `kemasan` | Permintaan tentang cara membungkus |
| 6 | `alat_makan` | Sendok, garpu, tisu, atau alat makan lain, termasuk penolakan |
| 7 | `waktu_antar` | Permintaan jam atau waktu tiba |
| 8 | `titip_antar` | Instruksi penitipan atau serah terima pesanan |

## 5. Aturan anotasi

Prinsip utama: **label ditentukan dari teks catatan saja**; model tidak melihat opsi yang dipilih di form.

1. Satu permintaan, satu label; beberapa permintaan → beberapa label.
2. Label mengikuti isi permintaan, bukan alasannya ("jangan pakai mentega, lagi diet" → `kurangi_bahan`; "lagi diet" saja → tidak berlabel).
3. Pilihan varian (tingkat pedas, ayam dada/paha) tidak diberi label; konflik dengan opsi ditangani backend.
4. Penambahan atau penghilangan bahan selalu diberi label, walau bahannya punya opsi di form.
5. Tambah dan kurangi untuk **bahan yang sama** dalam satu catatan dianggap ambigu dan tidak dibuat. Di template gabungan, daftar bahan tambah (`keju, kornet, ayam, oregano`) dan kurangi (`mentega, bawang, brokoli, micin, mayo`) sengaja tidak beririsan.
6. Catatan kosong atau "-" tidak masuk dataset.
7. Tidak ada data pribadi (nama, nomor HP, alamat nyata).

Kasus ambigu A1–A15 di kesepakatan diterapkan langsung di template, mis. A3 "jangan pakai mentega karena alergi susu" → `alergi` + `kurangi_bahan` (T67, T68); A2 "tolong alat masaknya dipastikan bersih" tanpa kata alergi → tidak berlabel (T90); A9 "maag, jangan pedas" → tidak berlabel (T93); A12 "aku gak bisa makan …" → `kurangi_bahan` (T24); A13 "kirim besok aja" → tidak berlabel (T89).

## 6. Cara pembuatan

1. **Seed:** 16 contoh catatan di Keputusan Final 9.6, ditambah kasus A1–A15 di kesepakatan label.
2. **Template:** 102 pola kalimat di `generate.py`:
   - 70 template satu label (8 per label: 5 train, 3 test; v2 menambah 1 train dan 1 test untuk `saus_terpisah` (T97, T98), `kemasan` (T99, T100), dan `alat_makan` (T101, T102));
   - 20 template multi-label berisi 2–3 permintaan (12 train, 8 test);
   - 12 template tanpa label (7 train, 5 test).
   Template v2 ditaruh di akhir daftar, jadi `T01`–`T96` tidak bergeser dari v1.
3. **Slot:** tiap pola punya slot yang diisi acak, mis. `{saus}`, `{alergen}`, `{kurang}`, `{tambah}`, `{jam}`, `{penerima}`, sapaan `{kak}`, `{ya}`.
4. **Variasi gaya informal:** singkatan (yg, jgn, gk, tlg, kalo, bgt, pake) ±30%; huruf berulang (yaaa, kakk) ±15%; typo tukar huruf ±7%; huruf awal kapital ±25%; emoji ±10%.
5. **Deduplikasi:** catatan yang sama setelah huruf kecil dan spasi dirapikan dibuang.
6. **Catatan tulisan anggota** dari `member_notes.csv` (63 catatan dari empat penulis, `M01`–`M04`) digabung ke split `test`.

Membuat ulang: dari root repository, jalankan `python3 moolabel-dataset/generate.py` lalu `python3 moolabel-dataset/validate.py`. Seed tetap, jadi hasilnya identik.

## 7. Jumlah contoh

| Label | Train | Test | Total | Template (train/test) |
|---|---|---|---|---|
| `saus_terpisah` | 50 | 31 | 81 | 10 / 6 |
| `alergi` | 43 | 30 | 73 | 8 / 5 |
| `kurangi_bahan` | 50 | 32 | 82 | 9 / 5 |
| `tambah_bahan` | 43 | 32 | 75 | 8 / 5 |
| `kemasan` | 43 | 31 | 74 | 9 / 6 |
| `alat_makan` | 43 | 36 | 79 | 9 / 7 |
| `waktu_antar` | 43 | 27 | 70 | 8 / 5 |
| `titip_antar` | 43 | 31 | 74 | 8 / 5 |
| **Catatan** | **316** | **224** | **540** | |

Dari 540 catatan, 477 berasal dari template (jumlah sama dengan v1, teks dibuat ulang karena jumlah template per label berubah) dan 63 dari tulisan anggota (`M01`–`M04`, semuanya test). Jumlah template per label hanya menghitung `T##`.

| Komposisi | Jumlah | Persentase | Target kesepakatan |
|---|---|---|---|
| Tanpa label | 82 | 15,2% | 15–20% ✓ |
| Satu label | 327 | 60,6% | — |
| Multi-label (2–3 label) | 131 | 24,3% | 20–30% ✓ |
| Rasio label terbanyak : tersedikit | 82 : 70 | 1,17× | ≤ 2× ✓ |

Catatan tulisan anggota per label (semua test): `saus_terpisah` 9, `alergi` 8, `kurangi_bahan` 10, `tambah_bahan` 10, `kemasan` 9, `alat_makan` 9, `waktu_antar` 5, `titip_antar` 9.

## 8. Pemisahan train/test

- Pemisahan **per template**, bukan acak per baris. Setiap `template_id` hanya ada di satu split, sehingga pola kalimat di test tidak pernah dilihat model saat latihan.
- Template multi-label hanya memakai pola miliknya sendiri, jadi tidak ada potongan kalimat train yang masuk test.
- Catatan tulisan anggota (`M##`) selalu masuk test.
- Daftar template dan split-nya ada di `templates.csv` untuk audit.

## 9. Hasil validasi (`validate.py`)

| Pemeriksaan | Hasil |
|---|---|
| Kolom dan urutan sesuai kontrak | OK |
| Nilai split dan label valid; `note_id` unik | OK |
| Tidak ada catatan kosong atau "-" | OK |
| Setiap `template_id` hanya di satu split | OK |
| Tidak ada catatan sama di train dan test | OK (0) |
| Positif per label: train ≥ 40, test ≥ 20 | OK |
| Template per label: train ≥ 4, test ≥ 2 | OK |
| Keseimbangan label ≤ 2× | OK (1,17×) |
| Tanpa label 15–20%, multi-label 20–30% | OK (15,2% dan 24,3%) |
| Catatan tulisan anggota ≥ 5 per label | OK (minimal 5 per label) |

Validator juga diuji dengan data yang sengaja dirusak (template bocor, catatan "-", nilai label 2); ketiganya tertangkap dan skrip keluar dengan kode 1.

## 10. Status dan langkah tersisa

| Item | Status |
|---|---|
| Dataset dari template | Selesai, lolos validasi |
| Catatan tulisan anggota di luar tim AI (min. 5 per label, semua test) | Selesai: 63 catatan dari empat penulis di luar tim AI: Daffa (`M01`), Baskara (`M02`), Darnel (`M03`), Rama (`M04`); lolos validasi
| Cek ulang 20 baris acak oleh DS (Baskara) | **Selesai 24 Nov 2026.** `recheck_20_v2.csv` (dibuat `recheck_sample.py`, seed 20261120): 20/20 setuju, tidak ada label yang perlu diubah. `recheck_20.csv` adalah cek ulang v1 (20/20 setuju); hanya 6 barisnya yang masih ada di v2 |
| Serah terima ke AI Engineer | Data uji v2 dibekukan 18 Nov 2026 (`3bf5980`) dan sudah dipakai macymoo-ai PR #22, sebelum cek ulang v2 selesai |

## 11. Keterbatasan dan risiko bias

- **Sintetis.** Skor evaluasi apa pun akan lebih optimis daripada kinerja pada catatan pelanggan asli. Validasi sesungguhnya baru bisa dilakukan dengan catatan asli setelah aplikasi dipakai.
- **Distribusi buatan.** Proporsi label sengaja seimbang; pada data asli, kemungkinan besar sebagian besar catatan kosong atau hanya satu permintaan.
- **Kosakata terbatas.** Nama bahan, alergen, jam, dan penerima berasal dari daftar slot yang ditulis tim. Template test berbeda dari train, tetapi slotnya sama, sehingga model tetap bisa mengandalkan kata kunci tersebut.
- **Gaya tulis seragam.** Semua template ditulis tim DS; catatan tulisan anggota lain diperlukan untuk menambah keragaman gaya.
- **Catatan ambigu dibuang** (aturan 5), padahal pelanggan asli bisa menulis seperti itu; penanganannya diserahkan ke backend/Nabila.
- **Label dikonfirmasi Nabila pada 13 November 2026** (kesepakatan v0.3); daftar dan definisi label tidak berubah dari v0.2.

## 12. Riwayat versi

| Versi | Tanggal | Perubahan |
|---|---|---|
| v1 | 12 Nov 2026 | Dataset awal dari 96 template, mengikuti kesepakatan label v0.2. 477 catatan (316 train, 161 test). Catatan tulisan anggota belum dimasukkan |
| v2 | 16 Nov 2026 | Mengikuti kesepakatan label v0.3 (8 label sama dengan v0.2). Tambah 6 template untuk `saus_terpisah`, `kemasan`, `alat_makan` (T97–T102) dan 63 catatan tulisan anggota (`M01`–`M04`). 540 catatan (316 train, 224 test). Tiga catatan pertanyaan estimasi waktu tiba ("jam berapa sampai?") tidak dimasukkan karena bukan permintaan waktu. Data uji dibekukan Rabu 18 Nov 2026, 20.00 WIB; perubahan sesudahnya masuk v3 |

Perubahan label atau format membuat versi file baru (`moolabel_v3.csv` dan seterusnya); file lama tidak ditimpa.
