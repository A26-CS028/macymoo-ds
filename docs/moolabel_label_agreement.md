# Kesepakatan Label MooLabel

**Status:** v0.2, disetujui AI Engineer (Rio) · disepakati tim (tanpa persetujuan terpisah dari Nabila)
**Tanggal:** 10 November 2026 · **Disusun oleh:** Daffa (DS 2), direvisi bersama AI Engineer, Tim A26-CS028
**Acuan:** `macymoo_Keputusan_Final.md` bagian 9.4 dan 9.6, Requirements DS 2 (FR-DS2-03 sampai 05), `macymoo_Struktur_Repository.md`

---

## 1. Cakupan MooLabel

MooLabel membaca **catatan bebas** pelanggan (`order_items.note`) dan menandai permintaan di dalamnya. Satu catatan boleh memuat beberapa permintaan (multi-label).

**Prinsip utama: label ditentukan dari teks catatan saja.** Model tidak melihat opsi yang dipilih pelanggan di form. Pertentangan antara catatan dan opsi (misalnya menulis "tanpa brokoli" tanpa mencentang opsinya) ditandai aturan backend, bukan model (KF 9.4).

## 2. Daftar label (8 label, urutan tetap)

| No | Label | Definisi |
|---|---|---|
| 1 | `saus_terpisah` | Saus atau keju diminta dipisah dari makanan utama. |
| 2 | `alergi` | Catatan **menyebut alergi atau intoleransi** terhadap bahan tertentu. |
| 3 | `kurangi_bahan` | Bahan atau rasa diminta dikurangi atau dihilangkan, termasuk bahan yang punya opsi di form (brokoli, makaroni). |
| 4 | `tambah_bahan` | Bahan diminta ditambah atau diperbanyak, termasuk bahan yang punya opsi di form (keju). |
| 5 | `kemasan` | Permintaan tentang cara membungkus. |
| 6 | `alat_makan` | Permintaan tentang sendok, garpu, tisu, atau alat makan lain, termasuk penolakan. |
| 7 | `waktu_antar` | Permintaan jam atau waktu tiba. |
| 8 | `titip_antar` | Instruksi penitipan atau serah terima pesanan. |

## 3. Batas tiap label

| Contoh catatan | Label |
|---|---|
| "sausnya dipisah ya" | `saus_terpisah` |
| "tanpa saus" | `kurangi_bahan` (bukan `saus_terpisah`) |
| "sausnya dibanyakin" | `tambah_bahan` (bukan `saus_terpisah`) |
| "alergi kacang", "intoleransi laktosa" | `alergi` |
| "gak bisa makan susu" (tanpa kata alergi atau intoleransi) | `kurangi_bahan` |
| "maag", "lagi diet" | tidak berlabel |
| "brokolinya gak usah", "tanpa makaroni" | `kurangi_bahan` |
| "jangan terlalu pedas", "pedes banget ya" | tidak berlabel (opsi tingkat pedas) |
| "ayamnya pakai paha aja" | tidak berlabel (opsi jenis ayam) |
| "kejunya dibanyakin" | `tambah_bahan` |
| "dibungkus terpisah per porsi", "dibungkus rapi" | `kemasan` |
| "minta sendok 2", "gak usah sendok" | `alat_makan` |
| "kirim sebelum jam 7" | `waktu_antar` |
| "kirim besok" | tidak berlabel (tanggal sudah dipilih di form) |
| "titip ke satpam", "taruh di pagar" | `titip_antar` |
| "makasih kak, semangat jualannya" | tidak berlabel |

## 4. Aturan anotasi

1. **Satu permintaan, satu label.** Catatan dengan beberapa permintaan diberi beberapa label.
2. **Label mengikuti isi permintaan, bukan alasannya.** "jangan pakai mentega, lagi diet" diberi `kurangi_bahan`; "lagi diet" saja tidak berlabel.
3. **Pilihan varian tidak diberi label.** Tingkat pedas (light, medium, spicy) dan jenis ayam (dada, paha) ditangani opsi dan backend.
4. **Penambahan atau penghilangan bahan selalu diberi label**, walaupun bahannya punya opsi di form. Jika tidak cocok dengan opsi yang dipilih, backend yang menandai agar Nabila mengecek (termasuk konfirmasi harga tambah keju).
5. **Tambah dan kurangi untuk bahan yang sama dalam satu catatan dianggap ambigu** dan dikeluarkan dari dataset (contoh A15). Tambah dan kurangi untuk bahan yang berbeda sah diberi dua label (contoh A14).
6. **Catatan kosong atau "-"** tidak dikirim ke model dan tidak masuk dataset.
7. **Tidak ada data pribadi** (nama, nomor HP, alamat nyata) dalam catatan.

## 5. Kasus ambigu (sudah disepakati)

| No | Catatan | Label | Alasan |
|---|---|---|---|
| A1 | "jangan terlalu pedas" | tidak berlabel | Opsi tingkat pedas (aturan 3) |
| A2 | "tolong alat masaknya dipastikan bersih" tanpa menyebut alergi | tidak berlabel | Tidak menyebut alergi atau intoleransi |
| A3 | "jangan pakai mentega karena alergi susu" | `alergi`, `kurangi_bahan` | Dua permintaan |
| A4 | "gak usah pakai sendok" | `alat_makan` | Penolakan tetap topik alat makan |
| A5 | "kirim jam 7 pagi, titip satpam kalau belum bangun" | `waktu_antar`, `titip_antar` | Dua permintaan |
| A6 | "tanpa kornet" | `kurangi_bahan` | Menghilangkan bahan |
| A7 | "buat hadiah, tolong dibungkus rapi" | `kemasan` | Permintaan pembungkusan |
| A8 | "lagi diet" | tidak berlabel | Tidak ada permintaan |
| A9 | "maag, jangan pedas" | tidak berlabel | Maag bukan alergi; "jangan pedas" ditangani opsi. **Diubah dari v0.1** |
| A10 | "sausnya pisah yaa, sendoknya jgn lupa" | `saus_terpisah`, `alat_makan` | Bahasa santai tetap dikenali |
| A11 | "brokolinya gak usah ya kak" | `kurangi_bahan` | Aturan 4. **Baru** |
| A12 | "gak bisa makan susu" | `kurangi_bahan` | Tidak menyebut alergi atau intoleransi. **Baru** |
| A13 | "kirim besok aja" | tidak berlabel | Tanggal ada di form. **Baru** |
| A14 | "kejunya banyakin, jangan pakai mentega" | `tambah_bahan`, `kurangi_bahan` | Bahan berbeda (aturan 5). **Baru** |
| A15 | "kejunya banyakin tapi jangan kebanyakan" | dikeluarkan dari dataset | Bahan sama, bertentangan (aturan 5). **Baru** |

## 6. Format dataset

Satu file per versi, dengan kolom `split`. Versi baru dibuat sebagai file baru (`moolabel_v2.csv`), file lama tidak ditimpa.

| Lokasi | Path |
|---|---|
| Repo DS (sumber) | `moolabel-dataset/output/moolabel_v1.csv` |
| Repo AI (salinan) | `data/moolabel/moolabel_v1.csv`; versi dan commit asal dicatat di README AI |

| Kolom | Isi |
|---|---|
| `note_id` | Nomor urut contoh |
| `note` | Teks catatan mentah (huruf besar, singkatan, typo, emoji dibiarkan); preprocessing oleh tim AI |
| `template_id` | Wajib. `T01`, `T02`, … untuk template; `M01`, `M02`, … untuk catatan tulisan anggota (satu ID per penulis) |
| `split` | `train` atau `test` |
| 8 kolom label | 0 atau 1, urutan seperti bagian 2 |

- Encoding UTF-8; teks catatan diapit tanda kutip ganda.
- Urutan label wajib sama di kolom CSV dan di `labels.py` (repo AI). Di respons API, `scores` berupa objek JSON berkunci nama label, sehingga urutannya tidak berpengaruh.
- **Tidak ada kolom penanda sumber.** Sumber data (template atau tulisan anggota) dibedakan lewat awalan `template_id` dan dijelaskan di `data_dictionary.md`.

```csv
note_id,note,template_id,split,saus_terpisah,alergi,kurangi_bahan,tambah_bahan,kemasan,alat_makan,waktu_antar,titip_antar
1,"sausnya dipisah ya kak",T03,train,1,0,0,0,0,0,0,0
2,"saya alergi kacang, sausnya pisah",T07,train,1,1,0,0,0,0,0,0
3,"kejunya dikit aja",T11,test,0,0,1,0,0,0,0,0
4,"bungkus terpisah per porsi",T15,test,0,0,0,0,1,0,0,0
5,"saus dipisah, bungkus terpisah, sendok 2",T21,train,1,0,0,0,1,1,0,0
6,"pedes banget ya kak",T30,train,0,0,0,0,0,0,0,0
7,"brokoli ga usah, sendok 1 aja",M01,test,0,0,1,0,0,1,0,0
```

Contoh ini hanya ilustrasi format. Seluruh isi dataset **sintetis**.

## 7. Target komposisi dataset

| Target | Angka | Tujuan |
|---|---|---|
| Total catatan | sekitar 470 | |
| Template per label | minimal 6 (4 train, 2 test) | Data uji berasal dari pola kalimat yang tidak ada di data latih |
| Catatan tulisan anggota di luar tim AI | minimal 5 per label, semuanya `test` | Gaya tulis berbeda dari template |
| Contoh positif per label di train | minimal 40 | Cukup bahan belajar |
| Contoh positif per label di test | minimal 20 | Satu kesalahan hanya menggeser nilai label sekitar 5 poin |
| Keseimbangan antar-label | label terbanyak maksimal 2× label tersedikit | Mencegah model condong ke label yang sering muncul |
| Catatan tanpa label | 15–20% | Model belajar bahwa tidak semua catatan berisi permintaan |
| Catatan multi-label | 20–30% | Sesuai sifat catatan nyata |
| Variasi gaya | singkatan (yg, jgn, gk), typo, huruf berulang, emoji, sapaan "kak" | Catatan pelanggan umumnya informal |

## 8. Pembuatan dan validasi

- **Seed:** 16 contoh di KF 9.6, diperbanyak dengan template dan parafrase.
- **`generate.py`** memakai random seed tetap supaya dataset bisa dibuat ulang.
- **Pemisahan per template**, bukan per baris. Satu `template_id` hanya boleh berada di satu split.
- **`validate.py`** wajib lolos sebelum dataset diserahkan ke tim AI:
  1. Setiap `template_id` hanya ada di satu split.
  2. Tidak ada catatan yang sama (setelah huruf kecil dan spasi dirapikan) di train dan test.
  3. Setiap label memenuhi target minimum di bagian 7 pada kedua split.
  4. Tidak ada catatan kosong atau "-".
- Pelabelan acak 20 baris dicek ulang oleh anggota DS yang lain.
- Jumlah akhir per label dan per split dilaporkan di `data_dictionary.md`. Evaluasi model dilakukan AI Engineer.

## 9. Keterbatasan

Seluruh data dibuat tim, sehingga skor evaluasi apa pun akan lebih optimis daripada kinerja pada catatan pelanggan asli. Keterbatasan ini ditulis di README DS dan README AI. Validasi sesungguhnya baru bisa dilakukan dengan catatan asli setelah aplikasi dipakai.

## 10. Persetujuan

| Item | Status |
|---|---|
| Daftar label dan definisi | Disetujui |
| Batas label, aturan anotasi, kasus ambigu | Disetujui |
| Format CSV dan path | Disetujui |
| Target komposisi dan validasi | Disetujui |
| Persetujuan Nabila | Tidak diminta terpisah; dicatat sebagai **disepakati tim** |

| Versi | Tanggal | Perubahan |
|---|---|---|
| 0.1 | 10 Nov 2026 | Draf awal dari contoh Keputusan Final |
| 0.2 | 10 Nov 2026 | Prinsip label dari teks saja; definisi `alergi` dipersempit (A9 diubah); tambah tabel batas label dan kasus A11–A15; aturan 5 dipersempit ke bahan yang sama; `template_id` `M##` untuk tulisan anggota; satu file per versi dengan kolom `split`; tanpa kolom penanda sumber; target komposisi sekitar 470 catatan; aturan `validate.py`; bagian keterbatasan |
