from dataclasses import dataclass


@dataclass
class AgentResult:
    success: bool
    content: str = ""
    error: str = ""
    provider: str = ""
    model: str = ""
    elapsed: float = 0.0