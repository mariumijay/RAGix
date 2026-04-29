"""generation/prompt.py — prompt builders for the Urdu A (textbook Q&A) pipeline."""
from __future__ import annotations

SYSTEM_PROMPT = (
    "آپ پنجاب بورڈ جماعت نہم و دہم کے اردو مضمون کے ماہر استاد ہیں۔\n"
    "صرف فراہم کردہ نصابی سیاق (context) کی بنیاد پر جواب دیں۔\n"
    "جواب رسمی اردو میں دیں۔ اگر جواب سیاق میں موجود نہ ہو تو لکھیں: "
    "\"یہ معلومات دستیاب نہیں\"\n\n"
    "جواب کی شکل سوال کی نوعیت کے مطابق رکھیں:\n"
    "- تعریف/مطلب → صرف 2-3 سطریں\n"
    "- اقسام/فہرست → نمبر شدہ یا بلٹ پوائنٹس\n"
    "- مثالیں → مختصر فہرست\n"
    "- مضمون/سوال → تب ہی مضمون لکھیں جب سوال میں 'مضمون لکھیں' ہو\n"
    "- فالتو تعارف، خاتمہ، یا اشعار شامل نہ کریں جب تک نہ مانگے جائیں\n"
)


def build_prompt(query: str, context_chunks: list[dict]) -> list[dict]:
    context_text = "\n\n".join(
        f"[{i + 1}] {c.get('text', '').strip()}"
        for i, c in enumerate(context_chunks)
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"CONTEXT (نصاب سے):\n{context_text}\n\nسوال: {query}",
        },
    ]


def build_citations(chunks: list[dict]) -> list[dict]:
    return [
        {
            "chunk_id": c.get("chunk_id"),
            "chapter":  c.get("chapter"),
            "page":     c.get("page_start"),
            "text":     c.get("text", "")[:120],
        }
        for c in chunks
        if c.get("text")
    ]


# ── ADDITIONS BELOW — keep everything above this line unchanged ──────────────

PAPER_SYSTEM_PROMPT = """
You are a Punjab Board Urdu exam paper setter for Class 9-10.
Generate a COMPLETE model paper using this EXACT structure and marks:

━━━ OBJECTIVE — 20 marks ━━━
سوال نمبر 1 (الف) — MCQs (15 × 1 = 15 marks)
  Topics: textbook متن، قواعد، محاورات، ضرب الامثال
سوال نمبر 1 (ب) — Short questions / fill blanks (5 marks)

━━━ SUBJECTIVE — 56 marks ━━━
سوال نمبر 2 — نثر (10 marks)
  (i)  خلاصہ / مرکزی خیال of a prose passage (5 marks)
  (ii) 5 سوالات on the passage (1 mark each)

سوال نمبر 3 — نظم (10 marks)
  (i)  کسی بند کی تشریح (5 marks)
  (ii) 5 سوالات on the poem (1 mark each)

سوال نمبر 4 — قواعد (12 marks)
  (i)   جملوں کی درستی — 3 sentences (3 marks)
  (ii)  واحد/جمع OR مذکر/مؤنث — 4 words (4 marks)
  (iii) محاورے یا ضرب الامثال — 2 items (4 marks)
  (iv)  اوقاف لگائیں — short passage (1 mark)

سوال نمبر 5 — مضمون / خط / درخواست (10 marks)
  Write ONE of: (a) مضمون (b) خط (c) درخواست
  [always give 3 options — student picks one]

سوال نمبر 6 — انشاء (14 marks)
  (i)  کہانی / آپ بیتی / مکالمہ (7 marks)
  (ii) پیراگراف نویسی (4 marks)
  (iii) رسید یا اشتہار (3 marks)

RULES:
- Total = 75 marks
- Include نوٹ (instructions) at top of each section
- Add choice where board gives it (سوال 5 always has 3 options)
- Use authentic Class 9 Urdu textbook content for passages
- Never repeat the same passage in سوال 2 and سوال 3
- Formal paper layout — add roll number / name / date fields at top
"""

STUDENT_UX_RULES = """
STUDENT-FRIENDLY OUTPUT RULES (apply to every response):
1. After every درخواست / خط / مضمون — add a 3-line "✅ امتحانی نکات" checklist
2. After every grammar answer — state the قاعدہ in one line
3. For MCQs — explain WHY the correct option is right (one sentence)
4. For poem/شعر — always mention شاعر کا نام
5. Tone: warm, encouraging — like a senior student tutoring a junior
6. If student writes in English — respond in BOTH Urdu and English
7. If query is outside Class 9-10 Urdu scope — respond:
   "یہ سوال نصاب سے باہر ہے، لیکن میں مدد کر سکتا ہوں اگر آپ وضاحت کریں۔"
"""

INTENT_TABLE = {
    # writing genres → prompt_b.py handles these
    "درخواست": "application",
    "application": "application",
    "خط": "letter",
    "letter": "letter",
    "مضمون": "essay",
    "essay": "essay",
    "کہانی": "story",
    "story": "story",
    "آپ بیتی": "ap_beti",
    "ap_beti": "ap_beti",
    "رسید": "receipt",
    "receipt": "receipt",
    "مکالمہ": "dialogue",
    "dialogue": "dialogue",
    # grammar / knowledge → prompt.py (urdu_A pipeline) handles these
    "قاعدہ": "grammar",
    "grammar": "grammar",
    "mcq": "mcq",
    "ایم سی کیو": "mcq",
    "خلاصہ": "summary",
    "summary": "summary",
    "سوالات": "comprehension",
    "تشریح": "poem_explanation",
    "آسان": "translation",
    "بیان": "narration_change",
    "درست": "sentence_correction",
    "اوقاف": "punctuation",
    "پیراگراف": "paragraph_writing",
    "معنی": "word_meanings",
    # paper generator
    "پرچہ": "paper",
    "paper": "paper",
    "ماڈل پیپر": "paper",
    "model paper": "paper",
    "past paper": "paper",
}


def detect_intent(query: str) -> str:
    """
    Lightweight keyword-based intent detector.
    Returns a genre string or 'paper' or 'unknown'.
    Called BEFORE the LLM router in main.py for fast-path detection.
    """
    q = query.strip().lower()
    for keyword, intent in INTENT_TABLE.items():
        if keyword in q:
            return intent
    return "unknown"


def build_paper_prompt(query: str) -> list[dict]:
    """Build messages for paper generation — no RAG context needed."""
    return [
        {"role": "system", "content": PAPER_SYSTEM_PROMPT + "\n\n" + STUDENT_UX_RULES},
        {"role": "user",   "content": f"Generate a complete Urdu model paper. Topic hint: {query}"},
    ]