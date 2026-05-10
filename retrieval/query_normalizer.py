import os
import re
import unicodedata

# ── Script-detection helpers ───────────────────────────────────────────────

_URDU_RE = re.compile(
    r"[\u0600-\u06FF"
    r"\u0750-\u077F"
    r"\uFB50-\uFDFF"
    r"\uFE70-\uFEFF]"
)

_ROMAN_URDU_WORDS = {
    "hai", "hain", "tha", "thi", "the", "aur", "ya", "yeh", "woh",
    "mein", "se", "ko", "ka", "ki", "ke", "ne", "par", "kya",
    "nahi", "nahin", "koi", "sab", "bhi", "sirf", "lekin", "phir",
    "aap", "hum", "tum", "main", "ap", "iska", "uska", "unka",
    "kitaab", "kitab", "baat", "waqt", "log", "din", "raat",
    "kab", "kahan", "kyun", "kaise", "kaun", "kis", "kuch",
}

_HINGLISH_MARKERS = {
    "the", "is", "are", "was", "were", "have", "has", "had",
    "will", "would", "should", "could", "can", "do", "does", "did",
    "aur", "ya", "lekin", "toh", "na", "hi", "bhi", "bahut",
}


def _urdu_script_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    urdu_chars = sum(1 for c in chars if _URDU_RE.match(c))
    return urdu_chars / len(chars)


def _is_latin(text: str) -> bool:
    chars = [c for c in text if c.isalpha()]
    if not chars:
        return False
    latin = sum(1 for c in chars if unicodedata.name(c, "").startswith(("LATIN", "BASIC LATIN")))
    return latin / len(chars) > 0.5


def _detect_language(text: str) -> str:
    ratio = _urdu_script_ratio(text)
    if ratio >= 0.5:
        return "urdu"

    tokens = set(re.findall(r"[a-zA-Z]+", text.lower()))
    roman_hits = len(tokens & _ROMAN_URDU_WORDS)
    hinglish_hits = len(tokens & _HINGLISH_MARKERS)
    english_common = {"the", "is", "are", "was", "were", "have", "has"}
    has_english = bool(tokens & english_common)

    if has_english and (roman_hits > 0 or hinglish_hits > 0):
        return "hinglish"
    if _is_latin(text) and roman_hits > 0:
        return "roman_urdu"
    if _is_latin(text):
        return "roman_urdu"
    return "urdu"


# ── Conversion via Groq (same API used for all other LLM calls) ────────────

def _convert_to_urdu(text: str) -> str:
    """Convert Roman Urdu / Hinglish text to Urdu script using Groq."""
    try:
        from groq import Groq
        from generation.llm import API_KEYS

        client = Groq(api_key=API_KEYS[0])
        response = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Convert the following Roman Urdu or Hinglish text into pure Urdu script. "
                        "Return ONLY the converted Urdu text — no explanation, no extra words."
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.0,
            max_tokens=200,
        )
        converted = response.choices[0].message.content.strip()
        if converted and _urdu_script_ratio(converted) > 0.3:
            return converted
        return text
    except Exception as e:
        # Silently fall back — the original text is still usable
        return text

# ── Public API ──────────────────────────────────────────────────────────────

def normalize_query(query: str) -> tuple[str, str]:
    """
    Normalize a query to Urdu script.

    Returns (urdu_query, detected_lang) where detected_lang is one of
    'urdu' | 'roman_urdu' | 'hinglish'.
    """
    query = query.strip()
    if not query:
        return query, "urdu"

    lang = _detect_language(query)
    if lang == "urdu":
        return query, lang

    urdu_query = _convert_to_urdu(query)
    return urdu_query, lang
