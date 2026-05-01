"""
retrieval/router.py — Query classifier and dataset router.

route_dataset()        → 'urdu_A' | 'urdu_B' | 'both'   (keyword-based, no LLM cost)
classify_query()       → genre label for Urdu B pipelines (LLM-based, ~50 tokens)
classify_query_full()  → all intent types including Urdu A tasks (LLM-based)
"""

from __future__ import annotations

from generation.llm import _create_completion, DEFAULT_MODEL

# ---------------------------------------------------------------------------
# Dataset routing — keyword signal
# ---------------------------------------------------------------------------

_KW_B: frozenset[str] = frozenset({
    "درخواست", "خط", "مضمون", "کہانی", "آپ بیتی", "رسید", "مکالمہ",
    "محاورہ", "ضرب المثل", "جملے کی درستی", "انشاء", "تحریر",
    "لکھیں", "لکھو", "تیار کریں",
})

_KW_A: frozenset[str] = frozenset({
    "شاعر", "شاعری", "غزل", "نظم", "نثر", "سبق", "افسانہ", "مصنف",
    "تشریح", "خلاصہ", "سوال", "جواب", "حوالہ", "ادب", "کتاب",
})


def route_dataset(query: str) -> str:
    """
    Return 'urdu_A', 'urdu_B', or 'both' based on keyword presence.
    'both' means the query is ambiguous or explicitly spans both datasets.
    """
    has_b = any(kw in query for kw in _KW_B)
    has_a = any(kw in query for kw in _KW_A)
    if has_b and has_a:
        return "both"
    if has_b:
        return "urdu_B"
    if has_a:
        return "urdu_A"
    return "both"   # generic query — search everywhere


# ---------------------------------------------------------------------------
# Shared intent set (used by both classifiers)
# ---------------------------------------------------------------------------

ALL_INTENTS: frozenset[str] = frozenset({
    # Urdu B — writing genres
    "letter", "application", "essay", "story",
    "ap_beti", "receipt", "dialogue",
    # Urdu B — knowledge / textbook tasks
    "grammar", "mcq", "summary", "comprehension",
    "poem_explanation", "translation", "narration_change",
    "sentence_correction", "punctuation", "paragraph_writing",
    "word_meanings",
    # Special
    "paper",
    # Urdu A fallback
    "general_qa",
})

# Subset used by the original narrow B-only classifier
_B_ALLOWED: frozenset[str] = frozenset({
    "letter", "application", "essay", "story",
    "ap_beti", "receipt", "dialogue", "grammar",
})

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

_B_SYSTEM = """\
You are a query classifier for a Pakistani Urdu exam assistant.
Read the query and return ONLY one label from this list:
letter, application, essay, story, ap_beti, receipt, dialogue, grammar

Rules:
- خط or لکھیں دوست کو → letter
- درخواست or پرنسپل کو → application
- مضمون or موضوع پر لکھیں → essay
- کہانی or سبق آموز → story
- آپ بیتی or اپنا واقعہ → ap_beti
- رسید → receipt
- مکالمہ → dialogue
- جملہ or محاورہ or ضرب المثل or گرامر → grammar

Return ONLY the label. No explanation. No Urdu. Just the English label."""


_FULL_SYSTEM = """\
You are a query classifier for a Pakistani Urdu Class 9-10 exam assistant.
Read the query and return ONLY one label from this exact list:

letter, application, essay, story, ap_beti, receipt, dialogue,
grammar, mcq, summary, comprehension, poem_explanation, translation,
narration_change, sentence_correction, punctuation, paragraph_writing,
word_meanings, paper, general_qa

Rules:
- خط / دوست کو لکھیں          → letter
- درخواست / پرنسپل کو          → application
- مضمون / موضوع پر             → essay
- کہانی / سبق آموز             → story
- آپ بیتی / اپنا واقعہ         → ap_beti
- رسید                        → receipt
- مکالمہ                      → dialogue
- واحد/جمع / محاورہ / قاعدہ    → grammar
- MCQ / ایم سی کیو             → mcq
- خلاصہ / مرکزی خیال          → summary
- سوالات (comprehension)       → comprehension
- تشریح / شعر                 → poem_explanation
- آسان اردو / ترجمہ            → translation
- بیان بدلیں                  → narration_change
- جملے درست                   → sentence_correction
- اوقاف                       → punctuation
- پیراگراف                    → paragraph_writing
- معنی / مطلب                 → word_meanings
- پرچہ / ماڈل پیپر            → paper
- anything else                → general_qa

Return ONLY the label. No explanation."""


# ---------------------------------------------------------------------------
# Genre classifier for Urdu B only  (original — kept for compatibility)
# ---------------------------------------------------------------------------

async def classify_query(user_query: str) -> str:
    """
    Classify user_query into one Urdu B genre label.
    Falls back to 'essay' on any error or unrecognised label.
    """
    messages = [
        {"role": "system", "content": _B_SYSTEM},
        {"role": "user",   "content": f"Query: {user_query}"},
    ]
    try:
        response = await _create_completion(
            DEFAULT_MODEL,
            messages,
            False,
            temperature=0.0,
            max_tokens=10,
        )
        label = response.choices[0].message.content.strip().lower()
        return label if label in _B_ALLOWED else "essay"
    except Exception:
        return "essay"


# ---------------------------------------------------------------------------
# Full intent classifier — covers ALL intent types including Urdu A tasks
# ---------------------------------------------------------------------------

async def classify_query_full(user_query: str) -> str:
    """
    Classify into ALL intent types including Urdu A knowledge tasks.
    Falls back to 'general_qa' on any error or unrecognised label.
    """
    messages = [
        {"role": "system", "content": _FULL_SYSTEM},
        {"role": "user",   "content": f"Query: {user_query}"},
    ]
    try:
        response = await _create_completion(
            DEFAULT_MODEL,
            messages,
            False,
            temperature=0.0,
            max_tokens=10,
        )
        label = response.choices[0].message.content.strip().lower()
        return label if label in ALL_INTENTS else "general_qa"
    except Exception:
        return "general_qa"