def detect_mode(prompt: str) -> str:
    text = prompt.lower()

    architecture_words = [
        "arquitetura",
        "arquitetar",
        "desenhe a arquitetura",
        "arquitetura do sistema",
        "arquitetura do projeto",
    ]

    docs_words = [
        "documente",
        "documentação",
        "documentacao",
        "readme",
        "manual",
        "documentar",
    ]

    plan_words = [
        "planeje",
        "planejamento",
        "planejar",
        "estratégia",
        "estrategia",
        "estruture",
        "como devo implementar",
        "plano de implementação",
        "plano de implementacao",
    ]

    review_words = [
        "code review",
        "review",
        "revisar código",
        "revisar codigo",
        "revise o código",
        "revise o codigo",
        "analise meu código",
        "analise meu codigo",
    ]

    code_words = [
        "erro",
        "bug",
        "corrija",
        "corrigir",
        "implemente",
        "implementar",
        "refatore",
        "refatorar",
        "traceback",
        "exception",
        "endpoint",
        "função",
        "funcao",
        "classe",
        "não funciona",
        "nao funciona",
    ]

    quick_words = [
        "explique rapidamente",
        "resuma",
        "resumo",
        "o que é",
        "o que e",
    ]

    if any(word in text for word in architecture_words):
        return "architecture"

    if any(word in text for word in docs_words):
        return "docs"

    if any(word in text for word in plan_words):
        return "plan"

    if any(word in text for word in review_words):
        return "review"

    if any(word in text for word in code_words):
        return "code"

    if any(word in text for word in quick_words):
        return "quick"

    return "general"