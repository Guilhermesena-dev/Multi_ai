import os
import sys
from pathlib import Path

from multi_ai.config import ROUTES, SPECIALISTS, VALID_MODES
from multi_ai.memory import SessionMemory
from multi_ai.orchestrator import execute
from multi_ai.router import detect_mode


PROJECT = Path.cwd()
MODE = "auto"

# Memória compartilhada durante esta execução do Multi-AI.
MEMORY = SessionMemory(
    project=PROJECT,
    max_turns=6,
)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    print()
    print("=" * 70)
    print(" MULTI-AI CLI")
    print("=" * 70)
    print(f" Projeto : {PROJECT}")
    print(f" Modo    : {VALID_MODES[MODE]}")
    print(f" Memória : {len(MEMORY.turns)} turno(s)")
    print("=" * 70)
    print()


def print_help():
    print("""
Comandos:

  /auto           seleção automática
  /code           código e debug
  /plan           planejamento
  /architecture   arquitetura
  /docs           documentação
  /review         revisão de código
  /quick          resposta rápida

  /context        mostra o contexto enviado aos agentes
  /history        mostra o histórico da sessão
  /new            inicia uma nova conversa

  /status         configuração atual
  /clear          limpa a tela
  /help           ajuda
  /exit           sair

Exemplos:

  ai> analise a arquitetura deste projeto
  ai> agora aprofunde o segundo problema
  ai> como você corrigiria isso?

Seleção manual:

  ai> /code
  ai> analise esse erro
""")


def status():
    print()
    print(f"Projeto : {PROJECT}")
    print(f"Modo    : {VALID_MODES[MODE]}")
    print(f"Memória : {len(MEMORY.turns)}/{MEMORY.max_turns} turno(s)")
    print()

    print("Especialistas:")
    print()

    for mode, route in ROUTES.items():
        primary = SPECIALISTS[route["primary"]]

        reviewer_key = route["reviewer"]

        reviewer = (
            SPECIALISTS[reviewer_key].label
            if reviewer_key
            else "Nenhum"
        )

        print(
            f"  {mode.upper():13} "
            f"{primary.label} -> {reviewer}"
        )

    print()

    print("Segurança:")
    print("  Codex       : sandbox read-only")
    print(
        "  Antigravity : mode plan + "
        "permissões auto-aprovadas"
    )

    print()


def resolve_mode(prompt):
    if MODE == "auto":
        return detect_mode(prompt)

    return MODE


def get_final_response(result):
    """
    Obtém a melhor resposta disponível da execução.

    Ordem:
    1. síntese
    2. resposta principal
    """

    if not result:
        return None

    synthesis = result.get("synthesis")

    if (
        synthesis is not None
        and synthesis.success
        and synthesis.content
    ):
        return synthesis.content

    primary = result.get("primary")

    if (
        primary is not None
        and primary.success
        and primary.content
    ):
        return primary.content

    return None


def process_prompt(prompt):
    task_mode = resolve_mode(prompt)

    conversation_context = MEMORY.build_context()

    result = execute(
        user_prompt=prompt,
        task_mode=task_mode,
        project=PROJECT,
        conversation_context=conversation_context,
    )

    final_response = get_final_response(result)

    if final_response:
        MEMORY.add(
            user=prompt,
            assistant=final_response,
        )

        print(
            f"[MEMÓRIA] "
            f"{len(MEMORY.turns)}/"
            f"{MEMORY.max_turns} turno(s)"
        )
        print()

    return result


def change_mode(new_mode):
    global MODE

    MODE = new_mode

    print()
    print(
        f"Modo alterado para: "
        f"{VALID_MODES[MODE]}"
    )
    print()


def show_history():
    print()
    print("=" * 70)
    print(" HISTÓRICO DA SESSÃO")
    print("=" * 70)
    print()

    print(MEMORY.display())

    print()


def show_context():
    print()
    print("=" * 70)
    print(" CONTEXTO DOS AGENTES")
    print("=" * 70)
    print()

    context = MEMORY.build_context()

    if context:
        print(context)
    else:
        print("Nenhum contexto nesta sessão.")

    print()


def new_conversation():
    MEMORY.clear()

    print()
    print("Nova conversa iniciada.")
    print("A memória da sessão foi limpa.")
    print()


def handle_command(command):
    command = command.strip().lower()

    if command == "/exit":
        print()
        print("Encerrando Multi-AI.")
        return False

    if command == "/help":
        print_help()
        return True

    if command == "/status":
        status()
        return True

    if command == "/history":
        show_history()
        return True

    if command == "/context":
        show_context()
        return True

    if command == "/new":
        new_conversation()
        return True

    if command == "/clear":
        clear_screen()
        print_header()
        return True

    mode_commands = {
        "/auto": "auto",
        "/code": "code",
        "/plan": "plan",
        "/architecture": "architecture",
        "/docs": "docs",
        "/review": "review",
        "/quick": "quick",
    }

    if command in mode_commands:
        change_mode(mode_commands[command])
        return True

    print()
    print(f"Comando desconhecido: {command}")
    print("Digite /help para ver os comandos.")
    print()

    return True


def interactive_cli():
    clear_screen()
    print_header()

    print("Digite sua solicitação ou /help.")
    print()

    while True:
        try:
            user_input = input("ai> ").strip()

            if not user_input:
                continue

            if user_input.startswith("/"):
                if not handle_command(user_input):
                    break

                continue

            process_prompt(user_input)

        except KeyboardInterrupt:
            print()
            print()
            print("Use /exit para encerrar.")

        except EOFError:
            print()
            break

def run():
    # Modo one-shot:
    # ai "analise este projeto"
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])

        result = process_prompt(prompt)

        if not result:
            return 1

        status = result.get("status")

        if status == "success":
            return 0

        if status == "partial":
            return 2

        return 1

    # Modo interativo:
    # ai
    interactive_cli()

    return 0