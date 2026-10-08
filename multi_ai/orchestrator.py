import time
from pathlib import Path

from multi_ai.agents import run_antigravity, run_codex
from multi_ai.config import ROUTES, SPECIALISTS
from multi_ai.prompts import (
    build_primary_prompt,
    build_review_prompt,
    build_synthesis_prompt,
)


def run_specialist(
    specialist_key: str,
    prompt: str,
    project: Path,
):
    specialist = SPECIALISTS[specialist_key]

    if specialist.provider == "codex":
        return run_codex(
            prompt=prompt,
            project=project,
        )

    if specialist.provider == "antigravity":
        return run_antigravity(
            prompt=prompt,
            project=project,
            model=specialist.model,
        )

    raise ValueError(
        f"Provider desconhecido: {specialist.provider}"
    )


def print_result(title, result):
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)

    if result is None:
        print("Nenhum resultado.")
        return

    if result.success:
        print(result.content)
    else:
        print("ERRO:")
        print(result.error)


def execute(
    user_prompt: str,
    task_mode: str,
    project: Path,
    conversation_context: str = "",
):
    route = ROUTES[task_mode]

    primary_key = route["primary"]
    reviewer_key = route["reviewer"]

    primary_specialist = SPECIALISTS[primary_key]

    reviewer_specialist = (
        SPECIALISTS[reviewer_key]
        if reviewer_key
        else None
    )

    print()
    print(f"[ROUTER] Tarefa      : {task_mode.upper()}")
    print(f"[ROUTER] Principal   : {primary_specialist.label}")

    if reviewer_specialist:
        print(
            f"[ROUTER] Revisor     : "
            f"{reviewer_specialist.label}"
        )
        print(
            f"[ROUTER] Sintetizador: "
            f"{primary_specialist.label}"
        )
    else:
        print("[ROUTER] Revisor     : nenhum")
        print("[ROUTER] Sintetizador: desnecessário")

    print()

    start = time.time()

    # ========================================================
    # ETAPA 1 — ESPECIALISTA PRINCIPAL
    # ========================================================

    primary_prompt = build_primary_prompt(
        user_prompt=user_prompt,
        task_mode=task_mode,
        project=project,
        conversation_context=conversation_context,
    )

    print(
        f"[1/3] {primary_specialist.label}: "
        "analisando..."
    )

    primary_result = run_specialist(
        specialist_key=primary_key,
        prompt=primary_prompt,
        project=project,
    )

    # --------------------------------------------------------
    # FALHA TOTAL — PRINCIPAL FALHOU
    # --------------------------------------------------------

    if not primary_result.success:
        elapsed = time.time() - start

        print_result(
            f"ERRO — {primary_specialist.label}",
            primary_result,
        )

        print()
        print(f"Execução falhou em {elapsed:.1f}s")
        print()

        return {
            "status": "failed",
            "mode": task_mode,
            "primary": primary_result,
            "review": None,
            "synthesis": None,
            "elapsed": elapsed,
        }

    # ========================================================
    # QUICK — NÃO PRECISA REVISÃO
    # ========================================================

    if not reviewer_key:
        elapsed = time.time() - start

        print_result(
            f"RESPOSTA — {primary_specialist.label}",
            primary_result,
        )

        print()
        print(f"Concluído em {elapsed:.1f}s")
        print()

        return {
            "status": "success",
            "mode": task_mode,
            "primary": primary_result,
            "review": None,
            "synthesis": primary_result,
            "elapsed": elapsed,
        }

    # ========================================================
    # ETAPA 2 — REVISÃO
    # ========================================================

    review_prompt = build_review_prompt(
        user_prompt=user_prompt,
        task_mode=task_mode,
        primary_name=primary_specialist.label,
        primary_response=primary_result.content,
        project=project,
        conversation_context=conversation_context,
    )

    print(
        f"[2/3] {reviewer_specialist.label}: "
        "revisando..."
    )

    review_result = run_specialist(
        specialist_key=reviewer_key,
        prompt=review_prompt,
        project=project,
    )

    # --------------------------------------------------------
    # PARCIAL — PRINCIPAL OK, REVISOR FALHOU
    # --------------------------------------------------------

    if not review_result.success:
        elapsed = time.time() - start

        print_result(
            f"RESPOSTA — {primary_specialist.label}",
            primary_result,
        )

        print_result(
            f"REVISÃO FALHOU — {reviewer_specialist.label}",
            review_result,
        )

        print()
        print(
            "A síntese não foi executada porque "
            "a revisão falhou."
        )
        print(f"Concluído parcialmente em {elapsed:.1f}s")
        print()

        return {
            "status": "partial",
            "mode": task_mode,
            "primary": primary_result,
            "review": review_result,
            "synthesis": None,
            "elapsed": elapsed,
        }

    # ========================================================
    # ETAPA 3 — SÍNTESE
    # ========================================================

    synthesis_prompt = build_synthesis_prompt(
        user_prompt=user_prompt,
        task_mode=task_mode,
        primary_name=primary_specialist.label,
        primary_response=primary_result.content,
        reviewer_name=reviewer_specialist.label,
        review_response=review_result.content,
        project=project,
        conversation_context=conversation_context,
    )

    print(
        f"[3/3] {primary_specialist.label}: "
        "consolidando..."
    )

    synthesis_result = run_specialist(
        specialist_key=primary_key,
        prompt=synthesis_prompt,
        project=project,
    )

    elapsed = time.time() - start

    # ========================================================
    # SAÍDA
    # ========================================================

    if synthesis_result.success:
        print_result(
            "RESPOSTA FINAL",
            synthesis_result,
        )

    else:
        print()
        print("A síntese final falhou.")

        print_result(
            f"ANÁLISE — {primary_specialist.label}",
            primary_result,
        )

        print_result(
            f"REVISÃO — {reviewer_specialist.label}",
            review_result,
        )

        print_result(
            "ERRO NA SÍNTESE",
            synthesis_result,
        )

    print()
    print("-" * 70)
    print("EXECUÇÃO")
    print("-" * 70)

    print(
        f"Principal : {primary_specialist.label} "
        f"({primary_result.elapsed:.1f}s)"
    )

    print(
        f"Revisor   : {reviewer_specialist.label} "
        f"({review_result.elapsed:.1f}s)"
    )

    print(
        f"Síntese   : {primary_specialist.label} "
        f"({synthesis_result.elapsed:.1f}s)"
    )

    print(f"Total     : {elapsed:.1f}s")

    # --------------------------------------------------------
    # STATUS FINAL
    # --------------------------------------------------------

    if synthesis_result.success:
        execution_status = "success"
        print("Status    : SUCCESS")
    else:
        execution_status = "partial"
        print("Status    : PARTIAL")

    print()

    return {
        "status": execution_status,
        "mode": task_mode,
        "primary": primary_result,
        "review": review_result,
        "synthesis": synthesis_result,
        "elapsed": elapsed,
    }