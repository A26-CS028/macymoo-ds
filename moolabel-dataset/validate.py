"""Validasi dataset MooLabel sebelum diserahkan ke tim AI.

Aturan dari kesepakatan label v0.2 bagian 7 dan 8. Keluar dengan kode 1 jika ada GAGAL.
Jalankan:  python3 moolabel-dataset/validate.py [path_csv]
"""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

LABELS = ["saus_terpisah", "alergi", "kurangi_bahan", "tambah_bahan",
          "kemasan", "alat_makan", "waktu_antar", "titip_antar"]
COLUMNS = ["note_id", "note", "template_id", "split", *LABELS]
MIN_POS = {"train": 40, "test": 20}
MIN_TEMPLATES = {"train": 4, "test": 2}
MIN_MEMBER_PER_LABEL = 5

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "output/moolabel_v1.csv"
fails, warns = [], []


def check(ok, msg, warn=False):
    print(("OK    " if ok else ("PERLU " if warn else "GAGAL ")) + msg)
    if not ok:
        (warns if warn else fails).append(msg)


with open(path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    header = reader.fieldnames
    rows = list(reader)

norm = lambda s: " ".join(s.lower().split())
n = len(rows)
print(f"File: {path} ({n} catatan)\n")

check(header == COLUMNS, f"Kolom dan urutan sesuai kontrak: {','.join(COLUMNS)}")
check(all(r["split"] in ("train", "test") for r in rows), "Nilai split hanya train/test")
check(all(r[lab] in ("0", "1") for r in rows for lab in LABELS), "Semua kolom label bernilai 0 atau 1")
check(all(norm(r["note"]) not in ("", "-") for r in rows), "Tidak ada catatan kosong atau '-'")
check(len({r["note_id"] for r in rows}) == n, "note_id unik")

splits_of = defaultdict(set)
for r in rows:
    splits_of[r["template_id"]].add(r["split"])
leak = [t for t, s in splits_of.items() if len(s) > 1]
check(not leak, f"Setiap template_id hanya di satu split{' (bocor: ' + ', '.join(leak) + ')' if leak else ''}")

tr = {norm(r["note"]) for r in rows if r["split"] == "train"}
te = {norm(r["note"]) for r in rows if r["split"] == "test"}
check(not tr & te, f"Tidak ada catatan sama di train dan test ({len(tr & te)} duplikat)")
check(all(r["template_id"][0] == "T" or r["split"] == "test" for r in rows), "Catatan tulisan anggota (M##) hanya di test")

print("\nJumlah positif per label:")
pos = {s: Counter() for s in ("train", "test")}
tmpl = {s: defaultdict(set) for s in ("train", "test")}
for r in rows:
    for lab in LABELS:
        if r[lab] == "1":
            pos[r["split"]][lab] += 1
            if r["template_id"].startswith("T"):
                tmpl[r["split"]][lab].add(r["template_id"])
print(f"  {'label':15s} {'train':>6s} {'test':>6s}  template(train/test)")
for lab in LABELS:
    print(f"  {lab:15s} {pos['train'][lab]:6d} {pos['test'][lab]:6d}  {len(tmpl['train'][lab])}/{len(tmpl['test'][lab])}")
for s in ("train", "test"):
    low = [lab for lab in LABELS if pos[s][lab] < MIN_POS[s]]
    check(not low, f"Positif per label di {s} >= {MIN_POS[s]}{' (kurang: ' + ', '.join(low) + ')' if low else ''}")
    few = [lab for lab in LABELS if len(tmpl[s][lab]) < MIN_TEMPLATES[s]]
    check(not few, f"Template per label di {s} >= {MIN_TEMPLATES[s]}{' (kurang: ' + ', '.join(few) + ')' if few else ''}")

total_pos = {lab: pos["train"][lab] + pos["test"][lab] for lab in LABELS}
ratio = max(total_pos.values()) / max(1, min(total_pos.values()))
check(ratio <= 2, f"Label terbanyak <= 2x label tersedikit (rasio {ratio:.2f})")

n_lab = [sum(r[lab] == "1" for lab in LABELS) for r in rows]
none_pct = 100 * sum(k == 0 for k in n_lab) / n
multi_pct = 100 * sum(k >= 2 for k in n_lab) / n
check(15 <= none_pct <= 20, f"Catatan tanpa label 15-20% ({none_pct:.1f}%)")
check(20 <= multi_pct <= 30, f"Catatan multi-label 20-30% ({multi_pct:.1f}%)")

member = Counter()
for r in rows:
    if r["template_id"].startswith("M"):
        for lab in LABELS:
            member[lab] += r[lab] == "1"
short = [lab for lab in LABELS if member[lab] < MIN_MEMBER_PER_LABEL]
check(not short, f"Catatan tulisan anggota >= {MIN_MEMBER_PER_LABEL} per label"
      f"{' (belum cukup: ' + ', '.join(f'{l}={member[l]}' for l in short) + ')' if short else ''}", warn=True)

print(f"\nTrain {sum(r['split'] == 'train' for r in rows)} · Test {sum(r['split'] == 'test' for r in rows)} · Total {n}")
print(f"Hasil: {len(fails)} GAGAL, {len(warns)} PERLU tindak lanjut")
sys.exit(1 if fails else 0)
