"""
retrieval/query_normalizer.py
==============================
Detects whether a query is in:
  • Urdu script  (native — returned as-is)
  • Roman Urdu   (transliterated Latin → converted to Urdu script via Qwen/Ollama)
  • Hinglish     (Hindi/English mix   → converted to Urdu script via Qwen/Ollama)

Public API
----------
    from retrieval.query_normalizer import normalize_query

    urdu_query, lang = normalize_query("yeh kitaab kis baray mein hai?")
    # → ("یہ کتاب کس بارے میں ہے؟", "roman_urdu")
"""

import os
import re
import unicodedata

import httpx

_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")
_TIMEOUT = 60.0

import requests

HF_TOKEN = os.getenv("HF_TOKEN")

HF_URL = f"https://api-inference.huggingface.co/models/{_MODEL}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}
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


# ── Conversion via Qwen/Ollama ─────────────────────────────────────────────

_CONVERSION_PROMPT = """\
آپ کا کام یہ ہے کہ نیچے دیے گئے متن کو خالص اردو رسم الخط میں تبدیل کریں۔
صرف تبدیل شدہ اردو متن واپس کریں — کوئی وضاحت، کوئی اضافی الفاظ نہیں۔

متن: {text}

اردو ترجمہ:"""


def _convert_to_urdu(text: str) -> str:
    prompt = f"""
آپ کا کام یہ ہے کہ درج ذیل متن کو خالص اردو رسم الخط میں تبدیل کریں۔
صرف اردو میں جواب دیں:

{text}
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.0,
            "max_new_tokens": 200
        }
    }

    try:
        resp = requests.post(HF_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        output = resp.json()

        if isinstance(output, list):
            converted = output[0].get("generated_text", "")
        else:
            converted = output.get("generated_text", "")

        converted = converted.strip()

        if converted and _urdu_script_ratio(converted) > 0.3:
            return converted

        return text

    except Exception as e:
        print(f"[HF conversion failed] {e}")
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
