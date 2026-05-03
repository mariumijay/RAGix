"""
split_books.py
==============
Splits book.txt (Urdu A) and Quaid-e-Inshah_Full_OCR.txt (Urdu B)
into genre-specific files and organizes them into:

    data/
      urdu_A/
        nasar_tashreeh.txt      ← sabaq / prose lessons
        tashreeh_ghazal.txt     ← ghazals
        tashreeh_nazam.txt      ← nazams / poems
        short_question.txt      ← short Q&A
        markazi_khyal.txt       ← central idea / themes
        khulasa.txt             ← summaries

      urdu_B/
        letter.txt              ← خطوط نویسی
        application.txt         ← عرائض نویسی (درخواستیں)
        dialogue.txt            ← مکالمہ نگاری
        story.txt               ← کہانی
        sentence_correction.txt ← رموز اوقاف / grammar
        zarbul_imsal.txt        ← ضرب الامثال
        nasar_tashreeh.txt      ← تفہیم عبارت (comprehension)

      manifest.json             ← auto-generated for ingest_b.py

Run:
    python split_books.py
"""

import json
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR       = Path("data")
BOOK_A         = DATA_DIR / "book.txt"
BOOK_B         = DATA_DIR / "bookb.txt"

# Fallback: use project files if data/ copies not present
PROJECT_BOOK_A = Path("Quaid-e-Inshah_Full_OCR.txt")   # this is actually Urdu B
PROJECT_BOOK_B = Path("Quaid-e-Inshah_Full_OCR.txt")
PROJECT_A_ORIG = Path("book.txt")

URDU_A_DIR = DATA_DIR / "urdu_A"
URDU_B_DIR = DATA_DIR / "urdu_B"


def read_file(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def write_genre_file(folder: Path, filename: str, lines: list[str]) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / filename
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {out}  ({len(lines)} lines)")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# URDU B  —  Quaid-e-Inshah_Full_OCR.txt
#
# Section boundaries (line numbers in the file):
#   رموز اوقاف (sentence_correction)   → line 1121
#   ضرب الامثال  (zarbul_imsal)         → line 1781
#   خطوط نویسی  (letter)               → line 2173
#   عرائض نویسی (application)          → line 2452
#   مکالمہ نگاری (dialogue)             → line 2518 (PAGE 86)
#   کہانی لکھنا  (story)               → line 3731
#   مضمون نگاری (story/essay)          → line 3928
#   تفہیم عبارت (nasar_tashreeh)       → discovered below
# ─────────────────────────────────────────────────────────────────────────────

URDU_B_SECTIONS = {
    # genre_name : (start_line_1indexed, end_line_1indexed_inclusive)
    # Lines are 1-indexed as shown by grep
    "sentence_correction": (1121, 1780),
    "zarbul_imsal":        (1781, 2172),
    "letter":              (2173, 2451),
    "application":         (2452, 2517),
    "dialogue":            (2518, 3730),
    "story":               (3731, 3927),
    "nasar_tashreeh":      (3928, 9999),   # rest of file = tafheem / comprehension
}


def split_urdu_b(src: Path) -> list[dict]:
    """Split Urdu B file into genre files. Returns manifest entries."""
    lines = read_file(src)
    total = len(lines)
    manifest = []

    TOPIC_MAP = {
        "sentence_correction": "رموز اوقاف اور جملہ درستی",
        "zarbul_imsal":        "ضرب الامثال اور محاورات",
        "letter":              "خطوط نویسی",
        "application":         "عرائض نویسی (درخواستیں)",
        "dialogue":            "مکالمہ نگاری اور کہانیاں",
        "story":               "کہانی نگاری",
        "nasar_tashreeh":      "تفہیم عبارت",
    }

    for genre, (start, end) in URDU_B_SECTIONS.items():
        s = start - 1           # convert to 0-indexed
        e = min(end, total)     # clamp to file length
        section_lines = lines[s:e]
        if not section_lines:
            print(f"  ⚠ {genre}: no lines found (check line numbers)")
            continue
        filename = f"{genre}.txt"
        write_genre_file(URDU_B_DIR, filename, section_lines)
        manifest.append({
            "file":           filename,
            "genre":          genre,
            "sub_type":       genre,
            "topic":          TOPIC_MAP.get(genre, genre),
            "format_section": "full",
            "source":         "urdu_B",
            "board":          "lahore",
            "grade":          "9",
        })

    return manifest


# ─────────────────────────────────────────────────────────────────────────────
# URDU A  —  book.txt
#
# book.txt is the main Urdu A textbook. It contains:
#   - Prose lessons (nasar / sabaq)
#   - Ghazals
#   - Nazams (poems)
#   - Short questions after each lesson
#   - Khulasa / markazi khyal sections
#
# Strategy: detect by heading keywords since book.txt has no PAGE markers
# ─────────────────────────────────────────────────────────────────────────────

GHAZAL_MARKERS  = ["غزل", "(غزل)", "غزل)"]
NAZAM_MARKERS   = ["نظم", "(نظم)", "نظم)"]
SABAQ_MARKERS   = ["سبق", "افسانہ", "مضمون", "آرام و سکون", "نام دیو مالی",
                   "اپنی مدد آپ", "بھیڑیا", "اخلاق حسنہ", "ابتدائی حساب",
                   "لڑی میں پروئے", "کلیم اور مرزا"]
QUESTION_MARKERS= ["سوال", "مشق", "سوالات", "جوابات", "مختصر سوالات",
                   "معروضی سوالات", "انشائی سوالات"]
KHULASA_MARKERS = ["خلاصہ", "خلاصۂ"]
MARKAZI_MARKERS = ["مرکزی خیال", "مرکزی موضوع"]


def classify_line(line: str) -> str | None:
    """Return genre hint if this line is a section heading."""
    for m in GHAZAL_MARKERS:
        if m in line and len(line.strip()) < 80:
            return "tashreeh_ghazal"
    for m in NAZAM_MARKERS:
        if m in line and len(line.strip()) < 80:
            return "tashreeh_nazam"
    for m in KHULASA_MARKERS:
        if m in line and len(line.strip()) < 60:
            return "khulasa"
    for m in MARKAZI_MARKERS:
        if m in line:
            return "markazi_khyal"
    for m in QUESTION_MARKERS:
        if m in line and len(line.strip()) < 60:
            return "short_question"
    for m in SABAQ_MARKERS:
        if m in line and len(line.strip()) < 80:
            return "nasar_tashreeh"
    return None


def split_urdu_a(src: Path) -> None:
    """Split Urdu A book into genre buckets."""
    lines = read_file(src)
    buckets: dict[str, list[str]] = {
        "nasar_tashreeh":  [],
        "tashreeh_ghazal": [],
        "tashreeh_nazam":  [],
        "short_question":  [],
        "khulasa":         [],
        "markazi_khyal":   [],
    }

    current_genre = "nasar_tashreeh"  # default

    for line in lines:
        hint = classify_line(line)
        if hint:
            current_genre = hint
        buckets[current_genre].append(line)

    for genre, content in buckets.items():
        if content:
            write_genre_file(URDU_A_DIR, f"{genre}.txt", content)
        else:
            print(f"  ⚠ urdu_A/{genre}: empty — no lines matched")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    DATA_DIR.mkdir(exist_ok=True)

    # Resolve source files — support both data/ copies and project root copies
    book_a_src = BOOK_A if BOOK_A.exists() else PROJECT_A_ORIG
    book_b_src = BOOK_B if BOOK_B.exists() else PROJECT_BOOK_B

    if not book_a_src.exists():
        print(f"⚠ Urdu A source not found: {book_a_src}")
    if not book_b_src.exists():
        print(f"⚠ Urdu B source not found: {book_b_src}")
        return

    # ── Split Urdu A ──────────────────────────────────────────────────────────
    if book_a_src.exists():
        print(f"\n📖 Splitting Urdu A: {book_a_src}")
        split_urdu_a(book_a_src)
        print(f"   → Files written to {URDU_A_DIR}/")

    # ── Split Urdu B ──────────────────────────────────────────────────────────
    print(f"\n📖 Splitting Urdu B: {book_b_src}")
    manifest = split_urdu_b(book_b_src)
    print(f"   → Files written to {URDU_B_DIR}/")

    # ── Write manifest.json ───────────────────────────────────────────────────
    # Update file paths to be relative to urdu_B subfolder
    manifest_path = URDU_B_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n✅ manifest.json → {manifest_path}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("DONE. Final structure:")
    print(f"  {URDU_A_DIR}/")
    for p in sorted(URDU_A_DIR.glob("*.txt")):
        lines = len(p.read_text(encoding="utf-8").splitlines())
        print(f"    {p.name:<35} {lines:>6} lines")
    print(f"  {URDU_B_DIR}/")
    for p in sorted(URDU_B_DIR.glob("*.txt")):
        lines = len(p.read_text(encoding="utf-8").splitlines())
        print(f"    {p.name:<35} {lines:>6} lines")
    print(f"    manifest.json")
    print()
    print("Next steps:")
    print("  1. python preprocess.py --book data/urdu_A/   ← Urdu A ingestion")
    print("  2. python -m ingestion.ingest_b data/urdu_B   ← Urdu B ingestion")


if __name__ == "__main__":
    main()