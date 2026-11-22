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
| `docs/` | Kamus data (`data_dictionary.md`), aturan dan keterbatasan data termasuk definisi omzet D01/D02 (`data_limitation_log.md`), pertanyaan bisnis, review ERD dan invoice |

## Dataset MooLabel

Alur di `moolabel-dataset/`:

1. `templates.csv` berisi `template_id, split, labels, pattern`.
2. `generate.py` membuat parafrase dari template dengan random seed tetap.
3. `validate.py` memeriksa kebocoran train/test dan contoh positif per label.
4. Hasil ada di `output/moolabel_v2.csv` (v1 tetap disimpan).

Versi baru dibuat sebagai file baru (`v2`, `v3`), jangan menimpa versi lama.
Dataset lalu disalin ke [macymoo-ai](https://github.com/A26-CS028/macymoo-ai), dan README AI mencatat versi serta commit asalnya.

Kamus data: `moolabel-dataset/data_dictionary.md`.

## Menjalankan

```bash
pip install -r requirements.txt
python3 data/dummy/generate_orders.py   # buat ulang data/dummy/*_dummy.csv (DATA DUMMY, seed 42)
jupyter notebook notebooks/02_pertanyaan_bisnis.ipynb   # omzet harian dan mingguan
streamlit run streamlit/app.py          # prototipe Rekap, lokal saja
```

## Temuan utama

(diisi setelah analisis selesai; lihat `reports/temuan_rekomendasi.md`)

## Repo terkait

- [macymoo-fs](https://github.com/A26-CS028/macymoo-fs): kontrak API ada di `docs/openapi.yaml`
- [macymoo-ai](https://github.com/A26-CS028/macymoo-ai)

## Aturan kerja

- `main` dilindungi: kerja di branch `feat/...`, `fix/...`, `docs/...`.
- Pull request wajib di-review rekan satu path sebelum merge.
- Tidak ada nama, HP, alamat, atau invoice asli di repo.
