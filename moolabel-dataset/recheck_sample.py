"""Ambil 20 baris acak dari moolabel_v2.csv untuk dicek ulang manual oleh DS.

Hasil: recheck_20_v2.csv. Pemeriksa mengisi setuju_ya_tidak (ya/tidak),
label_seharusnya (bila tidak setuju), dan catatan_pemeriksa.
Seed tetap, jadi sampel selalu sama. File yang sudah ada tidak ditimpa
(isian pemeriksa bisa hilang), kecuali dengan --timpa.

Jalankan:  python3 moolabel-dataset/recheck_sample.py
"""
import csv
import random
import sys
from pathlib import Path

LABELS = ["saus_terpisah", "alergi", "kurangi_bahan", "tambah_bahan",
          "kemasan", "alat_makan", "waktu_antar", "titip_antar"]
SEED = 20261120
N = 20

folder = Path(__file__).resolve().parent
src = folder / "output/moolabel_v2.csv"
out = folder / "recheck_20_v2.csv"

if out.exists() and "--timpa" not in sys.argv:
    sys.exit(f"{out.name} sudah ada; tidak ditimpa (pakai --timpa bila memang ingin membuat ulang)")

with open(src, encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

sampel = sorted(random.Random(SEED).sample(rows, N), key=lambda r: int(r["note_id"]))

with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["note_id", "note", "split", "label", "setuju_ya_tidak", "label_seharusnya", "catatan_pemeriksa"])
    for r in sampel:
        label = "; ".join(l for l in LABELS if r[l] == "1") or "(tanpa label)"
        w.writerow([r["note_id"], r["note"], r["split"], label, "", "", ""])

print(f"{out.name}: {N} baris dari {src.name} (seed {SEED})")
