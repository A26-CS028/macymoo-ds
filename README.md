# macymoo-ds

Repo Data Science proyek macymoo (UMKM macyourmoo), Capstone Asah 2026, Tim A26-CS028.
Berisi analisis data pesanan dan pembuat dataset MooLabel.

## Isi repo

| Folder | Isi |
|---|---|
| `data/dummy/` | Pembuat data pesanan dummy (`generate_orders.py`) dan hasilnya |
| `data/raw/` | Invoice asli. **Tidak di-commit** (di-.gitignore), disimpan di Drive tim |
| `data/processed/` | Data olahan. Tidak di-commit jika berasal dari invoice asli |
| `notebooks/` | `01_wrangling`, `02_pertanyaan_bisnis` (lima pertanyaan bisnis), `03_cek_ketepatan` |
| `moolabel-dataset/` | Template, pembuat, dan validator dataset MooLabel |
| `streamlit/` | Dasbor lokal, tidak di-deploy |
| `reports/` | `temuan_rekomendasi.md` |

## Dataset MooLabel

Alur di `moolabel-dataset/`:

1. `templates.csv` berisi `template_id, kalimat, label`.
2. `generate.py` membuat parafrase dari template dengan random seed tetap.
3. `validate.py` memeriksa kebocoran train/test dan contoh positif per label.
4. Hasil ada di `output/moolabel_v1.csv`.

Versi baru dibuat sebagai file baru (`v2`, `v3`), jangan menimpa versi lama.
Dataset lalu disalin ke [macymoo-ai](https://github.com/A26-CS028/macymoo-ai), dan README AI mencatat versi serta commit asalnya.

Kamus data: `moolabel-dataset/data_dictionary.md`.

## Menjalankan

(diisi setelah setup selesai)

## Temuan utama

(diisi setelah analisis selesai; lihat `reports/temuan_rekomendasi.md`)

## Repo terkait

- [macymoo-fs](https://github.com/A26-CS028/macymoo-fs): kontrak API ada di `docs/openapi.yaml`
- [macymoo-ai](https://github.com/A26-CS028/macymoo-ai)

## Aturan kerja

- `main` dilindungi: kerja di branch `feat/...`, `fix/...`, `docs/...`.
- Pull request wajib di-review rekan satu path sebelum merge.
- Tidak ada nama, HP, alamat, atau invoice asli di repo.
