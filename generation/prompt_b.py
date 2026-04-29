"""generation/prompt_b.py — per-genre prompt templates for the Urdu B pipeline."""
from __future__ import annotations

_TEMPLATES: dict[str, dict[str, str]] = {
    "application": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write درخواست: open with بسم اللہ، address جناب پرنسپل صاحب، 3 paragraphs "
            "(request reason, supporting details, polite close), end with آپ کا اطاعت گزار۔\n"
            "Rules: 150-180 words, formal Urdu, no English."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write درخواست: {user_query}",
    },
    "letter": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write خط: date at top, appropriate greeting, 3 paragraphs, "
            "close with آپ کا مخلص (informal) or آپ کا شاکر (formal). "
            "Include at least one شعر or محاورہ.\n"
            "Rules: 150-200 words, correct Urdu register."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write خط: {user_query}",
    },
    "essay": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write مضمون with structure: تعارف → اہمیت → اصل بحث (2 paragraphs) → خلاصہ\n"
            "Include at least one شعر. Use ربط الفاظ: چنانچہ، لہٰذا، بلاشبہ۔\n"
            "Rules: 250-300 words, flowing prose, no bullet points, formal Urdu."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write مضمون on: {user_query}",
    },
    "story": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write کہانی with: عنوان، characters introduced, conflict, resolution، سبق at end.\n"
            "Rules: 180-220 words, narrative prose, moral lesson at the close."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write کہانی: {user_query}",
    },
    "ap_beti": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write آپ بیتی in first person (میں) only, chronological order, include feelings.\n"
            "Rules: 180-200 words, personal narrative style, no English."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write آپ بیتی: {user_query}",
    },
    "receipt": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write رسید with fields: رسید نمبر | تاریخ | رقم (figures and words) | مقصد | دستخط\n"
            "Rules: 50-100 words, structured format."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write رسید: {user_query}",
    },
    "dialogue": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write مکالمہ: at least 8 exchanges, clearly labelled speakers, conclusive ending.\n"
            "Rules: 150-200 words, natural dialogue, no English."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write مکالمہ: {user_query}",
    },
    "grammar": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Answer grammar questions: واحد/جمع، مذکر/مؤنث، محاورہ، ضرب الامثال، اوقاف، فعل کی گردان۔\n"
            "Format: rule statement + example. Always state قاعدہ in one line at end."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Grammar question: {user_query}",
    },
    "mcq": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Answer MCQs with format: نمبر → درست آپشن — وجہ (one sentence)\n"
            "Rules: one answer per question, always explain why in Urdu, "
            "ONLY from retrieved context — if not found: \"جواب دستیاب نہیں\""
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Answer these MCQs: {user_query}",
    },
    "summary": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write خلاصہ with structure:\n"
            "1. مرکزی خیال: one sentence stating the main topic\n"
            "2. اہم نکات: 3-4 sentences covering key ideas\n"
            "3. نتیجہ: one sentence conclusion\n"
            "Rules: own words only — never copy from passage, "
            "120-150 words, formal prose, no bullet points."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Write خلاصہ of: {user_query}",
    },
    "comprehension": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Answer comprehension سوالات with format:\n"
            "سوال → جواب (2-3 formal Urdu sentences, 40-60 words each)\n"
            "Rules: answers must stay within passage content, "
            "no English, quote passage phrase only if essential."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Answer these سوالات: {user_query}",
    },
    "poem_explanation": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Explain شعر / بند with format:\n"
            "1. شاعر کا نام + مختصر تعارف\n"
            "2. لفظی مطلب: meanings of difficult words\n"
            "3. مفہوم: overall meaning (3-4 sentences)\n"
            "4. مرکزی خیال: central message (1-2 sentences)\n"
            "Rules: 100-130 words, do not copy verse into explanation body."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: Explain: {user_query}",
    },
    "translation": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Translate passage into آسان اردو:\n"
            "- Natural sentence flow — not word-for-word\n"
            "- Replace difficult/classical words with everyday Urdu\n"
            "- Preserve original meaning faithfully\n"
            "Rules: same length as original, no English."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: آسان اردو میں لکھیں: {user_query}",
    },
    "narration_change": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Change narration with format: اصل جملہ | بدلا ہوا جملہ | قاعدہ\n"
            "Direct→Indirect: remove quotes, add کہ, shift pronouns\n"
            "Indirect→Direct: add quotes, restore pronouns\n"
            "Rules: show both sentences clearly, state the rule applied."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: بیان بدلیں: {user_query}",
    },
    "sentence_correction": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Correct sentences with format: غلط جملہ | درست جملہ | وجہ\n"
            "Check: اعراب، واحد/جمع، مذکر/مؤنث، فعل کی گردان، محل استعمال\n"
            "Rules: one row per sentence, name the grammar rule in وجہ column, "
            "if already correct write: درست ہے۔"
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: جملے درست کریں: {user_query}",
    },
    "punctuation": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Add اوقاف to the passage using: ۔ ، ؟ ! : ؛ '' \n"
            "Rules: return COMPLETE passage with marks inserted, "
            "do not change any words, briefly explain 2-3 key choices."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: اوقاف لگائیں: {user_query}",
    },
    "paragraph_writing": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Write a پیراگراف with structure:\n"
            "1. موضوعاتی جملہ: 1 sentence stating main idea\n"
            "2. تفصیلی جملے: 3-4 sentences with details\n"
            "3. اختتامی جملہ: 1 concluding sentence\n"
            "Rules: 80-100 words, single focused topic, no subheadings, formal Urdu."
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: پیراگراف لکھیں: {user_query}",
    },
    "word_meanings": {
        "system": (
            "Punjab Board Urdu exam expert Class 9-10.\n"
            "Give word meanings with format: لفظ | معنی | مثال جملہ\n"
            "Include متضاد and مترادف only if specifically asked.\n"
            "CRITICAL: answer ONLY from retrieved context — "
            "if word not found: \"یہ لفظ سیاق میں موجود نہیں\""
        ),
        "user": "CONTEXT:\n{retrieved_chunks}\n\nTASK: معنی بتائیں: {user_query}",
    },
}


def _fmt_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return "کوئی سیاق دستیاب نہیں"
    return "\n\n".join(
        f"[{i + 1}] {c.get('text', '').strip()}"
        for i, c in enumerate(chunks)
    )


def get_prompt(genre: str, retrieved_chunks: list[dict], user_query: str) -> list[dict]:
    """
    Build the messages list for the Groq chat API.

    Args:
        genre:            Genre label from INTENT_TABLE or classify_query().
        retrieved_chunks: Reranked chunk dicts (must have a 'text' key).
        user_query:       Normalized Urdu query string.

    Returns:
        List of {role, content} message dicts for _create_completion.
    """
    from generation.prompt import STUDENT_UX_RULES  # avoid circular import

    template = _TEMPLATES.get(genre, _TEMPLATES["essay"])

    system_with_ux = template["system"] + "\n\n" + STUDENT_UX_RULES

    user_content = template["user"].format(
        retrieved_chunks=_fmt_chunks(retrieved_chunks),
        user_query=user_query,
    )
    return [
        {"role": "system", "content": system_with_ux},
        {"role": "user",   "content": user_content},
    ]
