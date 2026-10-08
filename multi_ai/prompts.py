from pathlib import Path


MODE_INSTRUCTIONS = {
    "code": """
FOCO: CÓDIGO E DEBUG.

Analise:
1. causa raiz
2. arquivos envolvidos
3. trechos relevantes
4. solução técnica
5. riscos
6. implementação recomendada

Priorize evidências encontradas no código.
""",

    "plan": """
FOCO: PLANEJAMENTO.

Apresente:
1. entendimento do objetivo
2. estado atual
3. solução proposta
4. etapas de implementação
5. dependências
6. riscos
7. ordem de execução
""",

    "architecture": """
FOCO: ARQUITETURA DE SOFTWARE.

Analise:
1. arquitetura atual
2. componentes envolvidos
3. arquitetura proposta
4. responsabilidades
5. fluxo de dados
6. integrações
7. escalabilidade
8. riscos e trade-offs
""",

    "docs": """
FOCO: DOCUMENTAÇÃO TÉCNICA.

Identifique:
1. finalidade do projeto
2. arquitetura
3. componentes
4. configuração
5. instalação
6. execução
7. fluxos importantes
8. pontos não confirmados pelos arquivos
""",

    "review": """
FOCO: CODE REVIEW.

Procure:
1. bugs
2. problemas de lógica
3. segurança
4. concorrência
5. tratamento de erros
6. manutenção
7. duplicação
8. melhorias justificadas
""",

    "quick": """
Responda de maneira curta e objetiva.

Use o projeto como fonte quando necessário.
""",

    "general": """
Faça uma análise técnica objetiva da solicitação.

Use evidências existentes no projeto e diferencie fatos de hipóteses.
""",
}


def build_primary_prompt(
    user_prompt: str,
    task_mode: str,
    project: Path,
    conversation_context: str = "",
) -> str:

    instruction = MODE_INSTRUCTIONS.get(
        task_mode,
        MODE_INSTRUCTIONS["general"],
    )

    memory = build_memory_section(conversation_context)

    return f"""
Você é o especialista principal desta tarefa.

PROJETO:
{project}

{memory}

====================================================
SOLICITAÇÃO ATUAL
====================================================

{user_prompt}

REGRAS:
- Não altere arquivos.
- Não exclua arquivos.
- Não instale dependências.
- Não execute comandos destrutivos.
- Não faça git push.
- Investigue os arquivos do projeto quando necessário.
- Não invente informações.
- Informe quando algo não puder ser confirmado.
- A solicitação atual prevalece sobre o contexto anterior.

{instruction}
""".strip()

def build_memory_section(conversation_context: str) -> str:
    if not conversation_context:
        return ""

    return f"""
====================================================
CONTEXTO DA CONVERSA
====================================================

{conversation_context}

Use esse contexto apenas quando for relevante para a solicitação atual.
A solicitação atual tem prioridade sobre instruções anteriores.
Não trate hipóteses de respostas anteriores como fatos confirmados.
""".strip()

def build_review_prompt(
    user_prompt: str,
    task_mode: str,
    primary_name: str,
    primary_response: str,
    project: Path,
    conversation_context: str = "",
) -> str:

    memory = build_memory_section(conversation_context)

    return f"""
Você é o segundo especialista de uma análise técnica.

PROJETO:
{project}

{memory}

SOLICITAÇÃO ORIGINAL:
{user_prompt}

TIPO DE TAREFA:
{task_mode}

O especialista principal ({primary_name}) produziu esta análise:

================ ANÁLISE PRINCIPAL ================

{primary_response}

====================================================

Sua função NÃO é simplesmente produzir outra resposta do zero.
Revise criticamente a análise acima.
Verifique no projeto quando necessário.

Identifique:
1. O que está correto
2. O que está incorreto ou não comprovado
3. O que foi ignorado
4. Riscos não considerados
5. Melhorias na solução
6. Divergências importantes

REGRAS:
- Não altere arquivos.
- Não execute comandos destrutivos.
- Não faça git push.
- Não concorde automaticamente com o primeiro especialista.
- Não invente informações.
- Diferencie fatos encontrados no projeto de hipóteses.
""".strip()


def build_synthesis_prompt(
    user_prompt: str,
    task_mode: str,
    primary_name: str,
    primary_response: str,
    reviewer_name: str,
    review_response: str,
    project: Path,
    conversation_context: str = "",
) -> str:

    memory = build_memory_section(conversation_context)

    return f"""
Você é responsável pela SÍNTESE FINAL de uma análise técnica multi-agente.

PROJETO:
{project}

{memory}

SOLICITAÇÃO ORIGINAL:
{user_prompt}

TIPO DE TAREFA:
{task_mode}

====================================================
ANÁLISE DO ESPECIALISTA PRINCIPAL
{primary_name}
====================================================

{primary_response}

====================================================
REVISÃO DO SEGUNDO ESPECIALISTA
{reviewer_name}
====================================================

{review_response}

====================================================

Agora produza UMA resposta final consolidada.

REGRAS:
- Não apenas resuma as duas respostas.
- Resolva divergências quando houver evidência suficiente.
- Se uma divergência não puder ser resolvida, deixe isso explícito.
- Remova duplicações.
- Corrija afirmações que o revisor demonstrou estarem erradas.
- Preserve descobertas importantes do especialista principal.
- Não invente fatos.
- Diferencie fatos confirmados de hipóteses.
- Priorize evidências encontradas no projeto.
- A solicitação atual prevalece sobre o contexto anterior.
- Não altere arquivos.
- Não execute comandos destrutivos.
- Não faça git push.

A resposta deve ser útil diretamente para o usuário.

Estruture, quando aplicável, em:
1. Diagnóstico final
2. Evidências
3. Solução recomendada
4. Riscos
5. Próximos passos

Não mencione o processo interno de agentes, a menos que exista
uma divergência relevante que o usuário precise conhecer.
""".strip()