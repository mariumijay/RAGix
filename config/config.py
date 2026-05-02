RAG_MODES = {
    "mcq": {
        "MAX_CONTEXT_CHUNKS": 4,
        "MAX_TOKENS_PER_CHUNK": 300,
        "MAX_OUTPUT_TOKENS": 800,
        "TOP_K": 4
    },
    "short": {
        "MAX_CONTEXT_CHUNKS": 5,
        "MAX_TOKENS_PER_CHUNK": 500,
        "MAX_OUTPUT_TOKENS": 3045,
        "TOP_K": 5
    },
    "tashreeh": {
        "MAX_CONTEXT_CHUNKS": 5,
        "MAX_TOKENS_PER_CHUNK": 400,
        "MAX_OUTPUT_TOKENS": 2000,
        "TOP_K": 5
    },
    "essay": {
        "MAX_CONTEXT_CHUNKS": 6,
        "MAX_TOKENS_PER_CHUNK": 450,
        "MAX_OUTPUT_TOKENS": 3000,
        "TOP_K": 6
    }
}

CHUNK_OVERLAP = 100

# Maps intent/genre labels to RAG modes
GENRE_TO_MODE: dict[str, str] = {
    # lean/fast
    "mcq":                 "mcq",
    "receipt":             "mcq",
    "word_meanings":       "mcq",
    "sentence_correction": "mcq",
    "punctuation":         "mcq",
    "narration_change":    "mcq",
    # medium
    "letter":              "short",
    "application":         "short",
    "dialogue":            "short",
    "story":               "short",
    "ap_beti":             "short",
    "paragraph_writing":   "short",
    "summary":             "short",
    "comprehension":       "short",
    "translation":         "short",
    "general_qa":          "short",
    # heavy
    "grammar":             "tashreeh",
    "poem_explanation":    "tashreeh",
    # longest
    "essay":               "essay",
}