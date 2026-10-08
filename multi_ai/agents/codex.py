import subprocess
import time
from pathlib import Path

from multi_ai.agents.base import AgentResult
from multi_ai.config import DEFAULT_TIMEOUT


def run_codex(
    prompt: str,
    project: Path,
) -> AgentResult:

    start = time.time()

    try:
        command = [
            "codex",
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "-C",
            str(project),

            # O "-" informa ao Codex:
            # leia o prompt através do stdin.
            "-",
        ]

        result = subprocess.run(
            command,

            # Prompt não vai mais na linha de comando.
            input=prompt,

            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DEFAULT_TIMEOUT,
            cwd=str(project),
        )

        elapsed = time.time() - start

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return AgentResult(
                success=False,
                error=stderr or stdout or (
                    f"Codex terminou com código "
                    f"{result.returncode}"
                ),
                provider="codex",
                model="default",
                elapsed=elapsed,
            )

        if not stdout:
            return AgentResult(
                success=False,
                error=stderr or "Codex não retornou conteúdo.",
                provider="codex",
                model="default",
                elapsed=elapsed,
            )

        return AgentResult(
            success=True,
            content=stdout,
            provider="codex",
            model="default",
            elapsed=elapsed,
        )

    except subprocess.TimeoutExpired:
        return AgentResult(
            success=False,
            error="Tempo limite do Codex excedido.",
            provider="codex",
            model="default",
            elapsed=time.time() - start,
        )

    except Exception as exc:
        return AgentResult(
            success=False,
            error=str(exc),
            provider="codex",
            model="default",
            elapsed=time.time() - start,
        )