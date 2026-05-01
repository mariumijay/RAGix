RAG_MODES = {
    "mcq": {
        "MAX_CONTEXT_CHUNKS": 4,
        "MAX_TOKENS_PER_CHUNK": 300,
        "MAX_OUTPUT_TOKENS": 800,
        "TOP_K": 4
    },
    "short": {
        "MAX_CONTEXT_CHUNKS": 5,
        "MAX_TOKENS_PER_CHUNK": 350,
        "MAX_OUTPUT_TOKENS": 1200,
        "TOP_K": 5
    },
    "tashreeh": {
        "MAX_CONTEXT_CHUNKS": 8,
        "MAX_TOKENS_PER_CHUNK": 500,
        "MAX_OUTPUT_TOKENS": 2500,
        "TOP_K": 8
    },
    "essay": {
        "MAX_CONTEXT_CHUNKS": 6,
        "MAX_TOKENS_PER_CHUNK": 450,
        "MAX_OUTPUT_TOKENS": 3000,
        "TOP_K": 6
    }
}

CHUNK_OVERLAP = 100