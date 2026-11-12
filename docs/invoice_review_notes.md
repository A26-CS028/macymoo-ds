# Invoice Review Notes — DS 1 Minggu 1

Sumber: folder `invoice/` (11 file PDF, periode 1 Agustus – 20 Oktober 2026). Harga pembanding diambil dari menu list di *Keputusan Final* (KF) bagian 3 (`docs/macymoo_Keputusan_Final.md`).

## Metode

- Setiap PDF dibuka dan dibaca manual satu per satu (teks + tampilan halaman). Tidak ada ekstraksi otomatis.
- Kunci telusur utama adalah **nomor invoice**. Nama file asli tidak dicantumkan karena sebagian memuat nama pelanggan (F09); dokumen dicari lewat nomor invoice yang tercetak di dalamnya.
- Nilai ditulis persis seperti tercetak di invoice. Hal yang tidak tercetak ditulis "tidak tercatat", tidak ditebak.
- Anonimisasi: `C01` = pelanggan kafe B2B (10 dari 11 invoice ditujukan ke sana), `C02` = pelanggan perorangan/grup dengan tujuan sekolah. Nama, nomor HP, dan alamat pelanggan tidak ditulis.

## 1. Inventaris

| # | No. invoice | Tgl invoice | Kode | Pelanggan |
|---|---|---|---|---|
| 1 | INV/20260801/WPH/001 | 01-08-2026 | WPH | C01 |
| 2 | INV/20260806/WPH/002 | 06-08-2026 | WPH | C01 |
| 3 | INV/20260814/WPH/003 | 14-08-2026 | WPH | C01 |
| 4 | INV/20260821/MYM-KPZ | 21-08-2026 | MYM-KPZ | C02 |
| 5 | INV/20260822/WPH/004 | 22-08-2026 | WPH | C01 |
| 6 | INV/20260830/WPH/005 | 30-08-2026 | WPH | C01 |
| 7 | INV/20260903/WPH/006 | 03-09-2026 | WPH | C01 |
| 8 | INV/20260912/WPH/007-v3 | 12-09-2026 | WPH | C01 |
| 9 | INV/20260918/WPH/008 | 18-09-2026 | WPH | C01 |
| 10 | INV/20261003/MCM/010 | 03-10-2026 | MCM | C01 |
| 11 | INV/20261020/MCM/011 | 20-10-2026 | MCM | C01 |

11 dari 11 invoice tersedia. Nama file tidak mengikuti pola tertentu dan sebagian memuat nama pelanggan, jadi nomor invoice yang dipakai sebagai ID.

### Kode brand dan penomoran

- **Format nomor:** `INV/YYYYMMDD/<KODE>/<NNN>`. Tanggal di nomor selalu sama dengan field "Tanggal".
- **WPH** (header "WRAPHORIA"): 001–008. **MCM** (header "MAC YOR MOO"): 010–011. Nomor urut **berlanjut lintas kode** (WPH/008 lalu MCM/010).
- **Nomor 009 tidak ada** di dataset. Belum diketahui apakah invoice-nya hilang, batal, atau nomornya dilewati.
- **MYM-KPZ** (header "MACYOURMOO X KOPIAZA", kolaborasi) **tidak punya nomor urut** dan memakai template yang berbeda.
- **Revisi:** `WPH/007-v3` berarti ada v1 dan v2 yang tidak ada di dataset. Isi revisi sebelumnya tidak diketahui.
- C01 ditagih dengan kode WPH sampai September, lalu dengan kode MCM mulai Oktober, untuk produk dan harga yang sama.

## 2. Ringkasan isi per invoice

| No. invoice | Item (qty × harga) | Subtotal | Ongkir | Grand total | Jumlah pengiriman |
|---|---|---|---|---|---|
| WPH/001 | Wraphoria – Fresh Wrap Special 5 × 27.000 | 135.000 | 20.000 | 155.000 | 1 |
| WPH/002 | idem 5 × 27.000 | 135.000 | 20.000 | 155.000 | 1 |
| WPH/003 | 5 × 27.000 (Selasa 11-08-2026) + 5 × 27.000 (Jumat 14-08-2026) | 270.000 | 40.000 | 310.000 | **2 (tanggal tertulis)** |
| MYM-KPZ | lihat §3 | 536.000 | FREE | 536.000 | tidak tercatat |
| WPH/004 | 5 × 27.000 (Pengiriman 1) + 5 × 27.000 (Pengiriman 2) | 270.000 | 40.000 | 310.000 | **2 (tanpa tanggal)** |
| WPH/005 | 5 × 27.000 | 135.000 | 20.000 | 155.000 | 1 |
| WPH/006 | 5 × 27.000 (Pengiriman 1) + 5 × 27.000 (Pengiriman 2) | 270.000 | 40.000 | 310.000 | **2 (tanpa tanggal)** |
| WPH/007-v3 | 10 × 27.000 dalam satu baris | 270.000 | 40.000 | 310.000 | **tersirat 2** (dari ongkir 40.000) |
| WPH/008 | 10 × 27.000 dalam satu baris | 270.000 | 40.000 "(2x)" | 310.000 | **2 (tertulis "2x")** |
| MCM/010 | Wraphoria 5 × 27.000 | 135.000 | 20.000 | 155.000 | 1 |
| MCM/011 | Wraphoria 5 × 27.000 | 135.000 | 20.000 | 155.000 | 1 |

**Cek aritmetika:** qty × harga = total baris, Σ baris = subtotal, dan subtotal + ongkir = grand total. Ketiganya cocok di 11 invoice.
Total kontrol: subtotal Rp2.561.000 + ongkir Rp300.000 = grand total **Rp2.861.000**.
Angka ini hanya untuk validasi pembacaan, **bukan omzet**, karena status bayarnya tidak diketahui (lihat limitation log).

## 3. Struktur invoice (FR-DS1-03)

| Aspek | Temuan |
|---|---|
| **Nama menu dan variasi** | Ada dua level: nama produk (bold) dan deskripsi/varian (teks kecil), misalnya "Wraphoria" / "Fresh Wrap Special". MCM/010 dan 011 hanya mencantumkan "Wraphoria" tanpa varian. `Nutrimac Small` hanya muncul **di dalam bundling** MYM-KPZ. Adanya "Small" menandakan ada ukuran lain yang tidak terlihat di data. |
| **Bundling** | MYM-KPZ: "Nutrimac Small + Coklat (Cup)", 1 paket Rp40.000, ditulis sebagai satu baris. Harga per komponen tidak tersedia. |
| **Bonus Rp0** | MYM-KPZ: "Macbites FREE – Bonus Promo", 2 pcs, Rp0. Bonus dicatat sebagai baris item, bukan sebagai diskon. |
| **Produk kolaborasi** | MYM-KPZ memuat produk minuman (Kopi Aren 1 Liter, Coklat 1 Liter) dan makanan (Wraphoria, Mackster, Nutrimac, Macbites) dalam satu invoice. Pembagian produk/pendapatan antar brand tidak tercatat. |
| **Kuantitas dan satuan** | Satuan yang dipakai beragam: `pcs`, `botol`, `paket`. "Coklat 1 Liter – Paket 5 Botol" berharga Rp17.000/botol, padahal "Kopi Aren 1 Liter" Rp75.000/botol. Kemungkinan ukurannya bukan 1 liter per botol, jadi perlu klarifikasi. |
| **Diskon** | **Tidak ada field diskon** di 11 invoice. |
| **Ongkir** | Selalu satu angka total. Rp20.000 per pengiriman (konsisten). Hanya WPH/008 yang menulis "(2x)". MYM-KPZ menulis "FREE". |
| **Pembayaran** | Hanya MYM-KPZ yang punya field status: "Lunas / Final". Invoice lain tidak mencatat status, DP, pelunasan, metode, maupun tanggal bayar. Kode QR pembayaran tercetak di 10 invoice WPH/MCM. Hanya WPH/001 yang memberi label "Pembayaran QRIS (GoPay, OVO, ShopeePay, BCA…)". |
| **Tanggal pengiriman** | Hanya WPH/003 yang mencatat tanggal kirim per baris. Di sana tanggal pengiriman pertama (11-08) **lebih awal** dari tanggal invoice (14-08), jadi tanggal invoice ≠ tanggal kirim/masak. |
| **Template** | Ada 3 tampilan: (a) WPH dengan blok alamat pengiriman; (b) MCM tanpa blok alamat dan dengan nama pelanggan disingkat; (c) MYM-KPZ dengan template lain yang memiliki field Status. WPH/001 berupa **hasil scan/foto** (bukan PDF teks) dan kontak penjualnya berbeda dari invoice lain. MCM/011 tidak bertanda tangan. |

## 4. Invoice dengan lebih dari satu pengiriman

| No. invoice | Bukti | Kejelasan |
|---|---|---|
| WPH/003 | 2 baris + tanggal + ongkir 40.000 | Jelas |
| WPH/004 | 2 baris "Pengiriman 1/2" + ongkir 40.000 | Jumlah jelas, tanggal tidak ada |
| WPH/006 | 2 baris "Pengiriman 1/2" + ongkir 40.000 | Jumlah jelas, tanggal tidak ada |
| WPH/008 | 1 baris 10 pcs + "Ongkos Kirim (2x)" | Jumlah jelas, pembagian porsi per kirim tidak ada |
| WPH/007-v3 | 1 baris 10 pcs + ongkir 40.000 | Hanya tersirat dari tarif 2 × 20.000 |

KF bagian 3 menyebut **3** invoice yang merekap 2 pengiriman. Pemeriksaan ini menemukan **3 yang eksplisit per baris** (003, 004, 006) ditambah **2 yang tersirat dari ongkir** (007-v3, 008). Selisih ini masuk ke clarification log.

## 5. Kesesuaian harga dengan menu list (KF 3)

| Menu | Harga menu list | Harga di invoice | Cocok? |
|---|---|---|---|
| Wraphoria | Rp27.000 | Rp27.000 (11 invoice) | Ya |
| Mackster | Rp35.000 | Rp35.000 (MYM-KPZ) | Ya |
| Nutrimac | Rp37.000 | hanya muncul sebagai "Nutrimac Small" dalam bundling Rp40.000 | Tidak dapat dibandingkan |
| Mac Bites | Rp25.000 | "Macbites" sebagai bonus Rp0 | Tidak dapat dibandingkan (bonus) |
| Kopi Aren 1 Liter, Coklat 1 Liter | tidak ada di menu list | Rp75.000, Rp17.000 | Produk kolaborasi, di luar 4 menu |
