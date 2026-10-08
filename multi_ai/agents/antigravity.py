import json
import subprocess
import time
from pathlib import Path
from typing import Any

from multi_ai.agents.base import AgentResult
from multi_ai.config import DEFAULT_TIMEOUT


def _parse_result_event(stdout: str) -> dict[str, Any] | None:
    """
    Procura o último evento terminal `result` emitido pelo
    Antigravity no stream NDJSON.

    Linhas inválidas ou eventos JSON inesperados são ignorados
    sem interromper o processamento do restante do stream.
    """

    final_result = None

    for raw_line in stdout.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        # JSON válido não significa necessariamente objeto.
        # Exemplos possíveis:
        # null
        # []
        # "texto"
        # 123
        if not isinstance(event, dict):
            continue

        if event.get("event") != "result":
            continue

        result_data = event.get("result")

        if not isinstance(result_data, dict):
            continue

        final_result = result_data

    return final_result


def _safe_string(value: Any) -> str:
    """
    Converte apenas strings válidas.

    Evita erros como:
        None.strip()
        dict.strip()
        list.strip()
    """

    if not isinstance(value, str):
        return ""

    return value.strip()


def run_antigravity(
    prompt: str,
    project: Path,
    model: str,
) -> AgentResult:

    start = time.time()

    try:
        command = [
            "agy",
            "--model",
            model,
            "--mode",
            "plan",
            "--dangerously-skip-permissions",
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
            "--print=",
        ]

        message = {
            "event": "user",
            "message": {
                "content": prompt,
            },
        }

        stdin_data = (
            json.dumps(
                message,
                ensure_ascii=False,
            )
            + "\n"
        )

        result = subprocess.run(
            command,
            input=stdin_data,
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

        # -----------------------------------------------------
        # Localiza o evento terminal
        # -----------------------------------------------------

        final_event = _parse_result_event(stdout)

        if final_event is None:
            error_message = (
                stderr
                or stdout
                or "Antigravity não retornou evento result válido."
            )

            return AgentResult(
                success=False,
                error=error_message,
                provider="antigravity",
                model=model,
                elapsed=elapsed,
            )

        # -----------------------------------------------------
        # Campos do evento result
        # -----------------------------------------------------

        status = _safe_string(
            final_event.get("status")
        )

        response = _safe_string(
            final_event.get("response")
        )

        error = _safe_string(
            final_event.get("error")
        )

        # -----------------------------------------------------
        # Status informado pelo Antigravity
        # -----------------------------------------------------

        if status != "SUCCESS":
            return AgentResult(
                success=False,
                error=(
                    error
                    or stderr
                    or (
                        "Antigravity terminou com "
                        f"status {status or 'desconhecido'}."
                    )
                ),
                provider="antigravity",
                model=model,
                elapsed=elapsed,
            )

        # -----------------------------------------------------
        # Exit code do processo
        # -----------------------------------------------------

        if result.returncode != 0:
            return AgentResult(
                success=False,
                error=(
                    error
                    or stderr
                    or (
                        "Antigravity terminou com "
                        f"código {result.returncode}."
                    )
                ),
                provider="antigravity",
                model=model,
                elapsed=elapsed,
            )

        # -----------------------------------------------------
        # Resposta vazia
        # -----------------------------------------------------

        if not response:
            return AgentResult(
                success=False,
                error=(
                    error
                    or stderr
                    or "Antigravity retornou resposta vazia."
                ),
                provider="antigravity",
                model=model,
                elapsed=elapsed,
            )

        # -----------------------------------------------------
        # Sucesso
        # -----------------------------------------------------

        return AgentResult(
            success=True,
            content=response,
            provider="antigravity",
            model=model,
            elapsed=elapsed,
        )

    except subprocess.TimeoutExpired:
        return AgentResult(
            success=False,
            error="Tempo limite do Antigravity excedido.",
            provider="antigravity",
            model=model,
            elapsed=time.time() - start,
        )

    except Exception as exc:
        return AgentResult(
            success=False,
            error=str(exc),
            provider="antigravity",
            model=model,
            elapsed=time.time() - start,
        )