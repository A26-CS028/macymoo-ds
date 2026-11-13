# Dokumentasi Dataset MooLabel

**Versi dataset:** v1 · **Tanggal dibuat:** 12 November 2026 · **Disusun oleh:** DS 2, Tim A26-CS028
**Acuan:** kesepakatan label MooLabel v0.3 (`docs/moolabel_label_agreement.md`, disetujui AI Engineer, dikonfirmasi Nabila), `macymoo_Keputusan_Final.md` bagian 9.4 dan 9.6, Requirements DS 2 Minggu 1 (FR-DS2-03 s.d. 06).

> ⚠️ **Seluruh isi dataset adalah DATA SINTETIS (dummy) buatan tim.** Tidak ada catatan pelanggan asli dan tidak ada data pribadi. Dataset ini **tidak mewakili distribusi catatan pelanggan nyata**.

## 1. Tujuan

Melatih dan menguji **MooLabel**, model klasifikasi multi-label yang membaca catatan bebas pelanggan (`order_items.note`) dan menandai permintaan di dalamnya untuk ditampilkan di daftar masak. Model dibangun AI Engineer (TF-IDF kata + char n-gram, Logistic Regression vs Linear SVM, F1-macro dan F1 per label).

## 2. File

| File | Isi |
|---|---|
| `output/moolabel_v1.csv` | **File utama** (sesuai kesepakatan): 477 catatan, kolom `split` |
| `output/moolabel_train.csv` | Ekspor baris `split = train` (316), nama sesuai requirement DS 2 |
| `output/moolabel_test.csv` | Ekspor baris `split = test` (161), nama sesuai requirement DS 2 |
| `templates.csv` | Daftar 96 template: id, split, label, pola kalimat (untuk audit) |
| `member_notes.csv` | Tempat catatan tulisan anggota (`M##`); saat ini **kosong** |
| `generate.py` | Pembuat dataset (random seed 42, deterministik) |
| `validate.py` | Pemeriksa aturan dataset; wajib lolos sebelum diserahkan |

Ketiga CSV berisi data yang sama; tim AI cukup memakai `moolabel_v1.csv`.

## 3. Skema kolom

| Kolom | Tipe | Keterangan |
|---|---|---|
| `note_id` | integer | Nomor urut catatan, unik |
| `note` | string | Teks catatan mentah (huruf besar, singkatan, typo, emoji dibiarkan). Diapit tanda kutip ganda. Preprocessing oleh tim AI |
| `template_id` | string | `T01`–`T96` = template; `M01`, `M02`, … = catatan tulisan anggota (satu ID per penulis) |
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
2. **Template:** 96 pola kalimat di `generate.py`:
   - 64 template satu label (8 per label: 5 train, 3 test);
   - 20 template multi-label berisi 2–3 permintaan (12 train, 8 test);
   - 12 template tanpa label (7 train, 5 test).
3. **Slot:** tiap pola punya slot yang diisi acak, mis. `{saus}`, `{alergen}`, `{kurang}`, `{tambah}`, `{jam}`, `{penerima}`, sapaan `{kak}`, `{ya}`.
4. **Variasi gaya informal:** singkatan (yg, jgn, gk, tlg, kalo, bgt, pake) ±30%; huruf berulang (yaaa, kakk) ±15%; typo tukar huruf ±7%; huruf awal kapital ±25%; emoji ±10%.
5. **Deduplikasi:** catatan yang sama setelah huruf kecil dan spasi dirapikan dibuang.
6. **Catatan tulisan anggota** dari `member_notes.csv` (jika ada) digabung ke split `test`.

Membuat ulang: dari root repository, jalankan `python3 moolabel-dataset/generate.py` lalu `python3 moolabel-dataset/validate.py`. Seed tetap, jadi hasilnya identik.

## 7. Jumlah contoh

| Label | Train | Test | Total | Template (train/test) |
|---|---|---|---|---|
| `saus_terpisah` | 50 | 22 | 72 | 9 / 5 |
| `alergi` | 43 | 22 | 65 | 8 / 5 |
| `kurangi_bahan` | 50 | 22 | 72 | 9 / 5 |
| `tambah_bahan` | 43 | 22 | 65 | 8 / 5 |
| `kemasan` | 43 | 22 | 65 | 8 / 5 |
| `alat_makan` | 43 | 27 | 70 | 8 / 6 |
| `waktu_antar` | 43 | 22 | 65 | 8 / 5 |
| `titip_antar` | 43 | 22 | 65 | 8 / 5 |
| **Catatan** | **316** | **161** | **477** | |

| Komposisi | Jumlah | Persentase | Target kesepakatan |
|---|---|---|---|
| Tanpa label | 81 | 17,0% | 15–20% ✓ |
| Satu label | 272 | 57,0% | — |
| Multi-label (2–3 label) | 124 | 26,0% | 20–30% ✓ |
| Rasio label terbanyak : tersedikit | 72 : 65 | 1,11× | ≤ 2× ✓ |

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
| Keseimbangan label ≤ 2× | OK (1,11×) |
| Tanpa label 15–20%, multi-label 20–30% | OK (17,0% dan 26,0%) |
| Catatan tulisan anggota ≥ 5 per label | **PERLU tindak lanjut** (belum ada) |

Validator juga diuji dengan data yang sengaja dirusak (template bocor, catatan "-", nilai label 2); ketiganya tertangkap dan skrip keluar dengan kode 1.

## 10. Status dan langkah tersisa

| Item | Status |
|---|---|
| Dataset dari template | Selesai, lolos validasi |
| Catatan tulisan anggota di luar tim AI (min. 5 per label, semua test) | **Belum.** Isi `member_notes.csv` (kolom `note`, `template_id` M##, 8 kolom label), lalu jalankan ulang generate dan validate |
| Cek ulang 20 baris acak oleh DS (Baskara) | **Belum** |
| Serah terima ke AI Engineer | Menunggu dua item di atas |

## 11. Keterbatasan dan risiko bias

- **Sintetis.** Skor evaluasi apa pun akan lebih optimis daripada kinerja pada catatan pelanggan asli. Validasi sesungguhnya baru bisa dilakukan dengan catatan asli setelah aplikasi dipakai.
- **Distribusi buatan.** Proporsi label sengaja seimbang; pada data asli, kemungkinan besar sebagian besar catatan kosong atau hanya satu permintaan.
- **Kosakata terbatas.** Nama bahan, alergen, jam, dan penerima berasal dari daftar slot yang ditulis tim. Template test berbeda dari train, tetapi slotnya sama, sehingga model tetap bisa mengandalkan kata kunci tersebut.
- **Gaya tulis seragam.** Semua template ditulis tim DS; catatan tulisan anggota lain diperlukan untuk menambah keragaman gaya.
- **Catatan ambigu dibuang** (aturan 5), padahal pelanggan asli bisa menulis seperti itu; penanganannya diserahkan ke backend/Nabila.
- **Belum dikonfirmasi Nabila secara terpisah**; label dicatat sebagai disepakati tim (kesepakatan bagian 10).

## 12. Riwayat versi

| Versi | Tanggal | Perubahan |
|---|---|---|
| v1 | 12 Nov 2026 | Dataset awal dari 96 template, mengikuti kesepakatan label v0.2. 477 catatan (316 train, 161 test). Catatan tulisan anggota belum dimasukkan |

Perubahan label atau format membuat versi file baru (`moolabel_v2.csv`); file lama tidak ditimpa.
