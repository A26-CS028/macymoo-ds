# Data Limitation & Clarification Log — DS 1 Minggu 1

Cakupan: hanya 11 invoice asli (Agustus–Oktober 2026). Keterbatasan di bawah adalah kondisi bawaan data lama yang dibuat manual sebelum sistem ada, bukan kesalahan pemeriksaan.
KF = *Keputusan Final* (`docs/macymoo_Keputusan_Final.md`, versi 6 November 2026); angka di belakangnya adalah nomor bagian. ID dipakai agar mudah dirujuk di diskusi tim.

## A. Data yang tidak tersedia

| ID | Keterbatasan | Sumber | Dampak |
|---|---|---|---|
| L01 | Tidak ada status pesanan, riwayat status, alasan jadwal ulang/batal | 11 invoice | Q3 tidak dapat dijawab dari invoice |
| L02 | Tidak ada data pembayaran (jumlah, tanggal, metode, DP/pelunasan, waktu kirim tagihan) kecuali status "Lunas" pada MYM-KPZ | 11 invoice | Q4 dan bagian "lewat batas bayar" di Q3 tidak dapat dijawab |
| L03 | Tidak ada catatan/opsi kustom | 11 invoice | Q5 tidak dapat dijawab; **tidak boleh ada angka/kesimpulan** dari invoice |
| L04 | Tidak ada tanggal masak; tanggal kirim per baris hanya di WPH/003 | 11 invoice | Q2 hanya sebagian |
| L05 | Tidak ada field diskon (di aplikasi nanti diskon tampil sebagai baris, KF 6) | 11 invoice | Omzet bersih = omzet kotor (asumsi) |
| L06 | Harga komponen bundling tidak dipecah | MYM-KPZ | Omzet Nutrimac/Coklat cup tidak bisa dipisah. Di aplikasi bundling juga disimpan satu baris (item bebas, KF 10), jadi keterbatasan ini tetap berlaku |
| L07 | Invoice nomor 009 dan revisi v1/v2 dari WPH/007 tidak ada | Penomoran | Dataset mungkin tidak lengkap |
| L08 | 10/11 invoice untuk satu pelanggan dengan satu menu (juga dicatat di KF 9.5) | Inventaris | Hasil tidak mewakili seluruh penjualan; tidak cukup untuk forecasting |

## B. Format yang tidak konsisten

| ID | Inkonsistensi | Sumber |
|---|---|---|
| F01 | 3 kode brand (WPH, MCM, MYM-KPZ) dan 3 template; MYM-KPZ tanpa nomor urut. Nomor lama berlanjut lintas kode, sedangkan format baru (KF 6) memakai `MYM` dan nomor yang direset harian | Semua |
| F02 | Multi-pengiriman ditulis dengan 4 gaya: baris bertanggal (003), "Pengiriman 1/2" (004, 006), label ongkir "(2x)" (008), tanpa penanda (007-v3) | WPH/003–008 |
| F03 | Nama pelanggan yang sama ditulis berbeda antar invoice (lengkap vs. disingkat, salah eja) | WPH vs. MCM |
| F04 | Varian kadang ada ("Fresh Wrap Special"), kadang tidak (MCM/010, 011) | MCM |
| F05 | Satuan bercampur: pcs, botol, paket | MYM-KPZ |
| F06 | Ongkir gratis ditulis "FREE" (teks), lainnya angka | MYM-KPZ |
| F07 | WPH/001 berupa hasil scan/foto, kontak penjual berbeda; MCM/011 tanpa tanda tangan | WPH/001, MCM/011 |
| F08 | "Coklat 1 Liter – Paket 5 Botol" Rp17.000/botol vs. "Kopi Aren 1 Liter" Rp75.000/botol | MYM-KPZ |
| F09 | Nama file tidak berpola dan sebagian memuat nama pelanggan | Folder `invoice/` |
| F10 | Nama menu "Macbites" di invoice vs. "Mac Bites" di menu list (KF 3) | MYM-KPZ |

## C. Perlu definisi (status mengikuti KF)

| ID | Definisi | Status |
|---|---|---|
| D01 | Omzet = nilai item pesanan yang tidak Dibatalkan (KF 9.5), diakui saat ditagih, bukan saat dibayar. Ongkir **tidak** termasuk omzet. Diskon tidak dikurangkan di omzet per menu karena hanya tercatat per pesanan | **Disetujui DS 2 (12 Nov 2026).** Sesuai rumus Omzet di data dictionary v1.1 bagian 18 (`orders.status <> 'Dibatalkan'`) |
| D02 | "Minggu" = Senin–Minggu. Data aplikasi: berdasarkan `deliveries.delivery_date`. Invoice lama: tanggal invoice (A01) | **Disetujui DS 2 (12 Nov 2026)** |
| D03 | "Porsi" = qty makanan yang dimasak Nabila: 1 pcs menu = 1 porsi, 1 paket bundling = 1 porsi per komponen makanan. Minuman kolaborasi (botol) tidak dihitung porsi | **Disetujui DS 2 (12 Nov 2026)** dengan catatan: di data aplikasi bundling disimpan satu baris tanpa komponen (L06), jadi dihitung 1 porsi per paket; `item_type = kolaborasi` minuman tidak dihitung |
| D04 | Lewat batas bayar = 4 jam setelah Kirim Tagihan, hanya untuk pesanan bayar di muka (KF 6) | Final; tidak bisa diterapkan ke invoice lama |
| D05 | Bonus Rp0 dihitung sebagai porsi (beban masak) di Q2, dengan omzet 0 di Q1 | **Disetujui DS 2 (12 Nov 2026).** Di aplikasi: `item_type = bonus` |

## D. Asumsi sementara

| ID | Asumsi | Terkait |
|---|---|---|
| A01 | Tanggal invoice dipakai sebagai proksi tanggal transaksi untuk agregasi mingguan | D02, L04 |
| A02 | Ongkir Rp20.000 = 1 pengiriman (sesuai KF 3: ongkir per kirim), sehingga Rp40.000 = 2 pengiriman, termasuk WPH/007-v3 | F02 |
| A03 | WPH/007-v3 adalah versi final; v1/v2 tidak dihitung | L07 |
| A04 | Omzet menu tidak termasuk ongkir; bonus Rp0 dicatat qty-nya tetapi omzetnya 0 | D01, D05 |
| A05 | WPH, MCM, dan MYM-KPZ adalah usaha yang sama (macyMOO); Wraphoria = menu Wraphoria Rp27rb di menu list | F01 |
| A06 | "Macbites" = menu "Mac Bites" | F10 |
| A07 | Tanggal masak = tanggal kirim (`deliveries.delivery_date`); skema tidak punya kolom tanggal masak dan daftar masak dibuat per tanggal kirim (KF 4) | L04, Q2 |

## E. Pertanyaan untuk Team Lead / Nabila

1. Apakah invoice **009** ada? Jika batal atau dilewati, apa sebabnya?
2. Apa yang berubah di WPH/007 v1 → v2 → v3, dan apakah file v1/v2 masih ada?
3. KF 3 menyebut 3 invoice berisi 2 pengiriman, sedangkan pemeriksaan menemukan 5 (003, 004, 006 eksplisit; 007-v3, 008 dari ongkir). Mana yang benar? Apa tanggal kirim untuk 004, 006, 007-v3, dan 008?
4. Apakah 10 invoice selain MYM-KPZ sudah lunas, kapan, dan lewat metode apa?
5. Ongkir "FREE" di MYM-KPZ: Ambil Sendiri, atau diantar tetapi digratiskan (= diskon)?
6. Harga "Nutrimac Small" di bundling: berapa harga satuannya dibanding Nutrimac reguler Rp37rb? Berapa ukuran asli "Coklat 1 Liter – Paket 5 Botol"?
7. ~~Konfirmasi usulan definisi D01, D02, D03, dan D05~~ → sudah diputuskan DS 2 pada 12 Nov 2026 (lihat bagian C).
