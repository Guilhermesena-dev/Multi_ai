from dataclasses import dataclass
from pathlib import Path


PROJECT = Path.cwd()

DEFAULT_TIMEOUT = 600


@dataclass(frozen=True)
class Specialist:
    provider: str
    model: str | None
    label: str


SPECIALISTS = {
    "codex": Specialist(
        provider="codex",
        model=None,  # usa o default da conta; hoje gpt-6-astra
        label="Codex (default)",
    ),

    "opus": Specialist(
        provider="antigravity",
        model="claude-opus-4-6-thinking",
        label="Claude Opus 4.6 Thinking",
    ),

    "sonnet": Specialist(
        provider="antigravity",
        model="claude-sonnet-4-6",
        label="Claude Sonnet 4.6 Thinking",
    ),

    "gemini_pro": Specialist(
        provider="antigravity",
        model="gemini-3.1-pro-high",
        label="Gemini 3.1 Pro High",
    ),

    "gemini_flash": Specialist(
        provider="antigravity",
        model="gemini-3.8-flash-high",
        label="Gemini 3.8 Flash High",
    ),

    "gemini_fast": Specialist(
        provider="antigravity",
        model="gemini-3.8-flash-medium",
        label="Gemini 3.8 Flash Medium",
    ),
}


ROUTES = {
    "code": {
        "primary": "codex",
        "reviewer": "sonnet",
    },

    "plan": {
        "primary": "opus",
        "reviewer": "gemini_pro",
    },

    "architecture": {
        "primary": "gemini_pro",
        "reviewer": "opus",
    },

    "docs": {
        "primary": "gemini_flash",
        "reviewer": "codex",
    },

    "review": {
        "primary": "sonnet",
        "reviewer": "codex",
    },

    "quick": {
        "primary": "gemini_fast",
        "reviewer": None,
    },

    "general": {
        "primary": "codex",
        "reviewer": "sonnet",
    },
}


VALID_MODES = {
    "auto": "Automático",
    "code": "Código / Debug",
    "plan": "Planejamento",
    "architecture": "Arquitetura",
    "docs": "Documentação",
    "review": "Code Review",
    "quick": "Rápido",
}