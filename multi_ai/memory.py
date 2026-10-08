import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sessions"


@dataclass
class ConversationTurn:
    user: str
    assistant: str


@dataclass
class SessionMemory:
    project: Path
    max_turns: int = 6
    turns: list[ConversationTurn] = field(default_factory=list)

    def __post_init__(self):
        self.project = self.project.resolve()
        self.load()

    # ---------------------------------------------------------
    # Identificação da sessão
    # ---------------------------------------------------------

    def session_id(self) -> str:
        normalized = str(self.project).lower()

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()[:16]

    def session_file(self) -> Path:
        return DATA_DIR / f"{self.session_id()}.json"

    # ---------------------------------------------------------
    # Persistência
    # ---------------------------------------------------------

    def save(self) -> None:
        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "project": str(self.project),
            "turns": [
                asdict(turn)
                for turn in self.turns
            ],
        }

        temp_file = self.session_file().with_suffix(".tmp")

        temp_file.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        # Escrita atômica:
        # primeiro cria .tmp e depois substitui o JSON.
        temp_file.replace(self.session_file())

    def load(self) -> None:
        path = self.session_file()

        if not path.exists():
            return

        try:
            data = json.loads(
                path.read_text(
                    encoding="utf-8",
                )
            )

            saved_project = data.get("project")

            if saved_project != str(self.project):
                return

            loaded_turns = []

            for item in data.get("turns", []):
                if not isinstance(item, dict):
                    continue

                user = item.get("user")
                assistant = item.get("assistant")

                if not isinstance(user, str):
                    continue

                if not isinstance(assistant, str):
                    continue

                loaded_turns.append(
                    ConversationTurn(
                        user=user,
                        assistant=assistant,
                    )
                )

            self.turns = loaded_turns[-self.max_turns:]

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
        ):
            # Uma sessão corrompida não deve impedir
            # o Multi-AI de iniciar.
            self.turns = []

    # ---------------------------------------------------------
    # Memória
    # ---------------------------------------------------------

    def add(
        self,
        user: str,
        assistant: str,
    ) -> None:

        self.turns.append(
            ConversationTurn(
                user=user.strip(),
                assistant=assistant.strip(),
            )
        )

        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

        self.save()

    def clear(self) -> None:
        self.turns.clear()

        path = self.session_file()

        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass

    def is_empty(self) -> bool:
        return not self.turns

    # ---------------------------------------------------------
    # Contexto enviado aos modelos
    # ---------------------------------------------------------

    def build_context(self) -> str:
        if not self.turns:
            return ""

        parts = [
            "CONTEXTO DA CONVERSA ATUAL:",
            "",
        ]

        for index, turn in enumerate(
            self.turns,
            start=1,
        ):
            parts.extend(
                [
                    f"[TURNO {index}]",
                    "USUÁRIO:",
                    turn.user,
                    "",
                    "RESPOSTA ANTERIOR:",
                    turn.assistant,
                    "",
                ]
            )

        return "\n".join(parts).strip()

    # ---------------------------------------------------------
    # Exibição
    # ---------------------------------------------------------

    def display(self) -> str:
        if not self.turns:
            return "Nenhum histórico nesta sessão."

        parts = []

        for index, turn in enumerate(
            self.turns,
            start=1,
        ):
            parts.extend(
                [
                    f"--- TURNO {index} ---",
                    f"Você: {turn.user}",
                    "",
                    f"AI: {turn.assistant}",
                    "",
                ]
            )

        return "\n".join(parts).strip()