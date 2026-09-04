"""
SOUL FORGE AI MODEL ROUTER

Ruflo = orchestration
AI providers = model intelligence

Primary providers:
- OpenAI
- Google Gemini
- Anthropic Claude
"""

SOUL_FORGE_AI_ROUTING = {
    "UNDERSTAND": {
        "provider": "gemini",
    },
    "PLAN": {
        "provider": "openai",
    },
    "IMPLEMENT": {
        "provider": "anthropic",
    },
    "VALIDATE": {
        "provider": "openai",
    },
    "REVIEW": {
        "provider": "anthropic",
    },
    "FINALIZE": {
        "provider": "openai",
    },
    "EXPLAIN": {
        "provider": "gemini",
    },
}
