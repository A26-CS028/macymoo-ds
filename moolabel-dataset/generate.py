"""Pembuat dataset MooLabel v1 (DS 2, Minggu 1).

SELURUH CATATAN ADALAH DATA SINTETIS buatan tim, bukan catatan pelanggan asli.
Acuan aturan: docs/moolabel_label_agreement.md v0.2 (disetujui AI Engineer).

- Train/test dipisah per template: satu template_id hanya ada di satu split.
- Catatan tulisan anggota (template_id M01, M02, ...) dibaca dari
  moolabel-dataset/member_notes.csv bila ada isinya, dan selalu masuk split test.

Jalankan dari root repository:  python3 moolabel-dataset/generate.py
"""
import csv
import random
from pathlib import Path

SEED = 42
VERSION = "v1"
ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "output"

# Urutan wajib sama dengan kolom CSV dan labels.py di repo AI (kesepakatan bagian 2).
LABELS = ["saus_terpisah", "alergi", "kurangi_bahan", "tambah_bahan",
          "kemasan", "alat_makan", "waktu_antar", "titip_antar"]

SLOTS = {
    "ya": ["ya", "yaa", "yah", "", "yaaa"],
    "kak": ["kak", "ka", "kakak", "", "kaa", "min"],
    "dong": ["dong", "ya", "pls", "", "dongg"],
    "saus": ["sausnya", "saus kejunya", "saosnya", "kejunya", "saus"],
    "alergen": ["kacang", "udang", "seafood", "telur", "susu", "kacang tanah", "gluten"],
    "kurang": ["mentega", "micin", "bawang", "brokoli", "makaroni", "kornet", "mayo",
               "minyak", "keju", "saus", "daun bawang"],
    "rasa": ["asin", "manis", "berminyak", "gurih"],
    "tambah": ["keju", "kornet", "saus", "saus keju", "ayam", "mayo", "oregano", "bawang goreng"],
    # Untuk template gabungan tambah + kurangi: dua daftar ini sengaja tidak beririsan (aturan 5).
    "tambah_x": ["keju", "kornet", "ayam", "oregano"],
    "kurang_x": ["mentega", "bawang", "brokoli", "micin", "mayo"],
    "acara": ["hadiah", "arisan", "temen kantor", "ultah", "acara kampus", "bekal anak"],
    "alat": ["sendok", "garpu", "tisu", "sendok garpu"],
    "n": ["1", "2", "3", "4", "dua", "tiga"],
    "jam": ["7", "8", "9", "10", "11", "12", "6"],
    "kegiatan": ["kuliah", "kerja", "rapat", "kelas pagi", "ngantor", "berangkat"],
    "penerima": ["satpam", "resepsionis", "ibu kos", "tetangga sebelah", "penjaga kos", "pos satpam"],
    "tempat": ["pagar", "meja depan", "lobby", "depan pintu", "pos satpam", "teras"],
}

# (label, split, pola). Urutan daftar menentukan nomor template_id (T01, T02, ...).
SINGLE = [
    # saus_terpisah
    ("saus_terpisah", "train", "{saus} dipisah {ya}"),
    ("saus_terpisah", "train", "tolong {saus} dipisah {kak}"),
    ("saus_terpisah", "train", "{saus} jangan dicampur {ya}"),
    ("saus_terpisah", "train", "minta {saus} taruh di wadah sendiri {kak}"),
    ("saus_terpisah", "train", "{saus} pisahin aja {kak}"),
    ("saus_terpisah", "test", "{saus} dikasih terpisah dari makaroninya bisa {kak}?"),
    ("saus_terpisah", "test", "biar ga lembek, {saus} jangan disiram dulu {ya}"),
    ("saus_terpisah", "test", "{saus} taruh di cup kecil aja {kak}"),
    # alergi
    ("alergi", "train", "saya alergi {alergen} {kak}"),
    ("alergi", "train", "alergi {alergen} {ya}"),
    ("alergi", "train", "aku alergi {alergen}, tolong alat masaknya dipastikan bersih"),
    ("alergi", "train", "mohon perhatian {kak}, ada alergi {alergen}"),
    ("alergi", "train", "aku intoleransi laktosa {kak}, mohon diperhatikan"),
    ("alergi", "test", "anak saya punya alergi {alergen} {kak}"),
    ("alergi", "test", "aku ada riwayat alergi {alergen} {ya}"),
    ("alergi", "test", "punya intoleransi {alergen}, hati-hati {ya}"),
    # kurangi_bahan
    ("kurangi_bahan", "train", "jangan pakai {kurang} {ya}"),
    ("kurangi_bahan", "train", "{kurang}nya dikit aja {kak}"),
    ("kurangi_bahan", "train", "tanpa {kurang} {kak}"),
    ("kurangi_bahan", "train", "{kurang} gak usah {ya}"),
    ("kurangi_bahan", "train", "jangan terlalu {rasa} {ya} {kak}"),
    ("kurangi_bahan", "test", "{kurang} skip aja {kak}"),
    ("kurangi_bahan", "test", "kalau bisa {kurang} dikurangi setengah"),
    ("kurangi_bahan", "test", "aku gak bisa makan {kurang} {kak}"),
    # tambah_bahan
    ("tambah_bahan", "train", "{tambah}nya dibanyakin {dong}"),
    ("tambah_bahan", "train", "minta extra {tambah} {ya}"),
    ("tambah_bahan", "train", "tambahin {tambah} {kak}"),
    ("tambah_bahan", "train", "{tambah}nya yang banyak {ya}"),
    ("tambah_bahan", "train", "porsi {tambah} dilebihin {dong}"),
    ("tambah_bahan", "test", "boleh lebihin {tambah}? nanti aku tambah bayar"),
    ("tambah_bahan", "test", "double {tambah} {dong}"),
    ("tambah_bahan", "test", "{tambah} agak dibanyakin kalau bisa {kak}"),
    # kemasan
    ("kemasan", "train", "dibungkus terpisah per porsi {ya}"),
    ("kemasan", "train", "bungkus satu-satu {ya}, buat {acara}"),
    ("kemasan", "train", "packing yang rapi soalnya buat {acara}"),
    ("kemasan", "train", "pisah per box {ya} {kak}"),
    ("kemasan", "train", "buat {acara}, tolong dibungkus rapi {kak}"),
    ("kemasan", "test", "tolong pakai box yang bisa ditumpuk {kak}"),
    ("kemasan", "test", "minta dipisah plastiknya, mau dibagi ke {acara}"),
    ("kemasan", "test", "kemasannya dobel biar ga tumpah {ya}"),
    # alat_makan
    ("alat_makan", "train", "minta {alat} {n} {ya}"),
    ("alat_makan", "train", "{alat}nya jangan lupa {kak}"),
    ("alat_makan", "train", "gak usah pakai {alat} {ya}"),
    ("alat_makan", "train", "tolong sertain {alat} {n}"),
    ("alat_makan", "train", "alat makannya {n} {ya}"),
    ("alat_makan", "test", "ga perlu alat makan {kak}, mau dimakan di rumah"),
    ("alat_makan", "test", "sumpit ada ga {kak}? kalau ada minta {n}"),
    ("alat_makan", "test", "cutlery-nya {n} set {ya}"),
    # waktu_antar
    ("waktu_antar", "train", "kirim sebelum jam {jam} {ya}"),
    ("waktu_antar", "train", "tolong sampai jam {jam}an {kak}"),
    ("waktu_antar", "train", "antar pagi {ya}, soalnya mau {kegiatan}"),
    ("waktu_antar", "train", "kirim sebelum jam {jam} soalnya mau {kegiatan}"),
    ("waktu_antar", "train", "sampainya jam {jam} pas {ya}"),
    ("waktu_antar", "test", "jangan lewat dari jam {jam} {kak}"),
    ("waktu_antar", "test", "aku cuma di rumah sampai jam {jam}"),
    ("waktu_antar", "test", "usahain datang sebelum {kegiatan} {ya}"),
    # titip_antar
    ("titip_antar", "train", "kalau saya belum keluar, titip ke {penerima}"),
    ("titip_antar", "train", "titipin ke {penerima} aja {kak}"),
    ("titip_antar", "train", "taruh di {tempat} {ya}"),
    ("titip_antar", "train", "titip {penerima} aja kalau aku belum bangun"),
    ("titip_antar", "train", "langsung kasih ke {penerima} {ya}"),
    ("titip_antar", "test", "kalau ga ada orang, kasih ke {penerima}"),
    ("titip_antar", "test", "boleh dititip di {tempat}, nanti aku ambil"),
    ("titip_antar", "test", "serahin ke {penerima} aja {kak}"),
]

# Gabungan beberapa permintaan dalam satu catatan.
MULTI = [
    (("saus_terpisah", "alat_makan"), "train", "{saus} dipisah {ya}, {alat}nya jangan lupa"),
    (("saus_terpisah", "kemasan", "alat_makan"), "train", "saus dipisah, bungkus terpisah, sendok {n}"),
    (("alergi", "kurangi_bahan"), "train", "jangan pakai mentega karena alergi susu {kak}"),
    (("alergi", "kurangi_bahan"), "train", "tanpa {alergen} {ya}, aku alergi"),
    (("waktu_antar", "titip_antar"), "train", "kirim jam {jam} pagi, titip {penerima} kalau belum bangun"),
    (("tambah_bahan", "kurangi_bahan"), "train", "{tambah_x}nya banyakin, jangan pakai {kurang_x}"),
    (("kemasan", "waktu_antar"), "train", "dibungkus per porsi {ya}, sampai sebelum jam {jam}"),
    (("alergi", "alat_makan"), "train", "alergi {alergen} {kak}, sama minta {alat} {n}"),
    (("tambah_bahan", "saus_terpisah"), "train", "{tambah_x}nya dibanyakin tapi {saus} dipisah"),
    (("kurangi_bahan", "titip_antar"), "train", "{kurang_x}nya dikit aja, kalau aku ga ada titip ke {penerima}"),
    (("kemasan", "titip_antar"), "train", "bungkus rapi buat {acara}, taruh di {tempat} {ya}"),
    (("saus_terpisah", "tambah_bahan", "waktu_antar"), "train", "{saus} dipisah, {tambah_x} dibanyakin, sampai jam {jam}an {ya}"),
    (("saus_terpisah", "kurangi_bahan"), "test", "{saus} taruh di cup kecil, {kurang_x} skip aja"),
    (("alergi", "waktu_antar"), "test", "anak saya alergi {alergen}, usahain datang sebelum {kegiatan}"),
    (("kemasan", "alat_makan"), "test", "kemasannya dobel biar ga tumpah, cutlery {n} set"),
    (("tambah_bahan", "titip_antar"), "test", "double {tambah_x} {dong}, kalau ga ada orang kasih ke {penerima}"),
    (("kurangi_bahan", "alat_makan"), "test", "{kurang_x} ga usah, {alat} {n} aja"),
    (("waktu_antar", "titip_antar", "kemasan"), "test", "aku cuma di rumah sampai jam {jam}, kalau lewat titip {penerima}, plastiknya dipisah per porsi"),
    (("alergi", "saus_terpisah"), "test", "punya riwayat alergi {alergen}, {saus} dikasih terpisah {ya}"),
    (("tambah_bahan", "alat_makan"), "test", "{tambah_x} agak dibanyakin, ga perlu alat makan {kak}"),
]

# Tidak berlabel: tanpa permintaan, atau permintaan yang sudah ditangani opsi/form (aturan 3, A1, A2, A8, A9, A13).
NONE = [
    ("train", "makasih {kak}, semangat jualannya"),
    ("train", "lagi diet {kak}"),
    ("train", "pedes banget {ya} {kak}"),
    ("train", "ayamnya pakai paha aja {kak}"),
    ("train", "kirim besok aja {ya}"),
    ("train", "tolong alat masaknya dipastikan bersih {ya}"),
    ("train", "udah langganan nih, enak banget {kak}"),
    ("test", "first time order, penasaran rasanya {kak}"),
    ("test", "maag, jangan pedas {ya}"),
    ("test", "ganti ke ayam dada {ya} {kak}"),
    ("test", "semoga laris {kak}"),
    ("test", "jangan terlalu pedas {kak}"),
]

# Jumlah baris per kelompok (total sekitar 470, sesuai kesepakatan bagian 7).
ROWS = {
    ("single", "train"): 22,  # per label
    ("single", "test"): 12,   # per label
    ("multi", "train"): 7,    # per template
    ("multi", "test"): 5,     # per template
    ("none", "train"): 8,     # per template
    ("none", "test"): 5,      # per template
}

ABBREV = {"yang": "yg", "jangan": "jgn", "gak": "gk", "tolong": "tlg", "aja": "aj",
          "sama": "sm", "kalau": "kalo", "banget": "bgt", "udah": "udh", "pakai": "pake",
          "dong": "dongg", "nggak": "ngga", "bisa": "bs"}
EMOJI = [" 🙏", " 😊", " 🙂", " 🙏🙏", " ❤️"]


def fill(rng, pattern):
    text = " ".join(pattern.format(**{k: rng.choice(v) for k, v in SLOTS.items()}).split())
    return text.replace(" ,", ",").replace(" ?", "?")  # slot kosong tidak menyisakan spasi sebelum tanda baca


def noise(rng, text):
    """Gaya ketik informal: singkatan, huruf berulang, typo ringan, emoji, kapital."""
    words = text.split()
    if rng.random() < 0.3:
        words = [ABBREV.get(w, w) if rng.random() < 0.7 else w for w in words]
    if rng.random() < 0.15 and words[-1] in ("ya", "kak", "dong", "aja"):
        words[-1] += words[-1][-1] * rng.randint(1, 3)
    if rng.random() < 0.07:
        long = [i for i, w in enumerate(words) if len(w) >= 5 and w.isalpha()]
        if long:
            i = rng.choice(long)
            j = rng.randint(1, len(words[i]) - 2)
            w = words[i]
            words[i] = w[:j] + w[j + 1] + w[j] + w[j + 2:]
    text = " ".join(words)
    if rng.random() < 0.25:
        text = text[0].upper() + text[1:]
    if rng.random() < 0.1:
        text += rng.choice(EMOJI)
    return text


def norm(text):
    return " ".join(text.lower().split())


def spread(total, k):
    """Bagi `total` baris ke `k` template serata mungkin."""
    return [total // k + (1 if i < total % k else 0) for i in range(k)]


def build_templates():
    out, n = [], 0
    for lab, split, pat in SINGLE:
        n += 1
        out.append({"template_id": f"T{n:02d}", "split": split, "labels": (lab,), "pattern": pat, "kind": "single"})
    for labs, split, pat in MULTI:
        n += 1
        out.append({"template_id": f"T{n:02d}", "split": split, "labels": labs, "pattern": pat, "kind": "multi"})
    for split, pat in NONE:
        n += 1
        out.append({"template_id": f"T{n:02d}", "split": split, "labels": (), "pattern": pat, "kind": "none"})
    return out


def target_rows(templates):
    """Jumlah baris yang diminta per template."""
    want = {}
    for split in ("train", "test"):
        for lab in LABELS:
            ts = [t for t in templates if t["kind"] == "single" and t["split"] == split and t["labels"] == (lab,)]
            for t, k in zip(ts, spread(ROWS[("single", split)], len(ts))):
                want[t["template_id"]] = k
    for t in templates:
        if t["kind"] != "single":
            want[t["template_id"]] = ROWS[(t["kind"], t["split"])]
    return want


def read_member_notes():
    path = ROOT / "member_notes.csv"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("note") or "").strip()]
    return [{"note": r["note"].strip(), "template_id": r["template_id"].strip(), "split": "test",
             "labels": tuple(lab for lab in LABELS if str(r.get(lab, "0")).strip() == "1")} for r in rows]


def generate():
    rng = random.Random(SEED)
    templates = build_templates()
    want = target_rows(templates)
    rows, seen = [], set()
    for t in templates:
        got = 0
        for _ in range(want[t["template_id"]] * 200):
            if got == want[t["template_id"]]:
                break
            text = noise(rng, fill(rng, t["pattern"]))
            if norm(text) in seen or norm(text) in ("", "-"):
                continue
            seen.add(norm(text))
            rows.append({"note": text, "template_id": t["template_id"], "split": t["split"], "labels": t["labels"]})
            got += 1
        if got < want[t["template_id"]]:
            print(f"PERINGATAN: {t['template_id']} hanya {got}/{want[t['template_id']]} baris unik")
    for r in read_member_notes():
        if norm(r["note"]) not in seen:
            seen.add(norm(r["note"]))
            rows.append(r)
    rng.shuffle(rows)
    rows.sort(key=lambda r: r["split"] != "train")  # train dulu, urutan dalam split tetap acak
    for i, r in enumerate(rows, 1):
        r["note_id"] = i
    return templates, rows


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(",".join(["note_id", "note", "template_id", "split", *LABELS]) + "\n")
        for r in rows:
            note = '"' + r["note"].replace('"', '""') + '"'
            flags = ",".join("1" if lab in r["labels"] else "0" for lab in LABELS)
            f.write(f'{r["note_id"]},{note},{r["template_id"]},{r["split"]},{flags}\n')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    templates, rows = generate()
    write_csv(OUT_DIR / f"moolabel_{VERSION}.csv", rows)
    write_csv(OUT_DIR / "moolabel_train.csv", [r for r in rows if r["split"] == "train"])
    write_csv(OUT_DIR / "moolabel_test.csv", [r for r in rows if r["split"] == "test"])
    with open(ROOT / "templates.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["template_id", "split", "labels", "pattern"])
        for t in templates:
            w.writerow([t["template_id"], t["split"], "+".join(t["labels"]) or "(tidak berlabel)", t["pattern"]])
    member = ROOT / "member_notes.csv"
    if not member.exists():
        with open(member, "w", encoding="utf-8", newline="") as f:
            f.write(",".join(["note", "template_id", *LABELS]) + "\n")
    print(f"Tertulis {len(rows)} catatan ke {OUT_DIR}")


if __name__ == "__main__":
    main()
