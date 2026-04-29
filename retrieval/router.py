"""
retrieval/router.py — Query classifier and dataset router.

route_dataset()  → 'urdu_A' | 'urdu_B' | 'both'   (keyword-based, no LLM cost)
classify_query() → genre label for Urdu B pipelines (LLM-based, ~50 tokens)
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
# Genre classifier for Urdu B (LLM-based)
# ---------------------------------------------------------------------------

ALLOWED_GENRES: frozenset[str] = frozenset({
    "letter", "application", "essay", "story",
    "ap_beti", "receipt", "dialogue", "grammar",
})

_SYSTEM = """\
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


async def classify_query(user_query: str) -> str:
    """
    Classify user_query into one Urdu B genre label.
    Falls back to 'essay' on any error or unrecognised label.
    """
    messages = [
        {"role": "system", "content": _SYSTEM},
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
        return label if label in ALLOWED_GENRES else "essay"
    except Exception:
        return "essay"
