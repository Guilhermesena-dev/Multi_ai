from dataclasses import dataclass
from enum import Enum


class Capability(str, Enum):
    READ = "read"
    WORKSPACE = "workspace"
    SYSTEM = "system"
    PUBLISH = "publish"


@dataclass(frozen=True)
class ExecutionProfile:
    name: str
    capability: Capability
    description: str

    can_read: bool
    can_write_workspace: bool
    can_change_system: bool
    can_publish: bool

    requires_isolated_workspace: bool
    requires_approval: bool


PROFILES = {
    "analysis": ExecutionProfile(
        name="analysis",
        capability=Capability.READ,
        description="Análise somente leitura",
        can_read=True,
        can_write_workspace=False,
        can_change_system=False,
        can_publish=False,
        requires_isolated_workspace=False,
        requires_approval=False,
    ),

    "workspace": ExecutionProfile(
        name="workspace",
        capability=Capability.WORKSPACE,
        description="Criação ou alteração em workspace isolado",
        can_read=True,
        can_write_workspace=True,
        can_change_system=False,
        can_publish=False,
        requires_isolated_workspace=True,
        requires_approval=False,
    ),

    "system": ExecutionProfile(
        name="system",
        capability=Capability.SYSTEM,
        description="Alterações no ambiente ou dependências",
        can_read=True,
        can_write_workspace=True,
        can_change_system=True,
        can_publish=False,
        requires_isolated_workspace=True,
        requires_approval=True,
    ),

    "publish": ExecutionProfile(
        name="publish",
        capability=Capability.PUBLISH,
        description="Publicação, merge, push ou deploy",
        can_read=True,
        can_write_workspace=True,
        can_change_system=True,
        can_publish=True,
        requires_isolated_workspace=True,
        requires_approval=True,
    ),
}


def get_profile(name: str) -> ExecutionProfile:
    try:
        return PROFILES[name]
    except KeyError as exc:
        raise ValueError(
            f"Perfil de execução desconhecido: {name}"
        ) from exc


def profile_for_action(action: str) -> ExecutionProfile:
    """
    Retorna o nível mínimo necessário para uma ação conhecida.

    Esta função NÃO concede permissão.
    Apenas classifica a operação.
    """

    action = action.strip().lower()

    mapping = {
        # Somente leitura
        "analyze": "analysis",
        "review": "analysis",
        "plan": "analysis",
        "architecture": "analysis",
        "docs": "analysis",

        # Escrita isolada
        "fix": "workspace",
        "create": "workspace",
        "feature": "workspace",
        "refactor": "workspace",
        "test": "workspace",

        # Ambiente
        "install": "system",
        "dependency": "system",
        "system": "system",

        # Publicação
        "merge": "publish",
        "push": "publish",
        "deploy": "publish",
        "publish": "publish",
    }

    profile_name = mapping.get(action)

    if profile_name is None:
        raise ValueError(
            f"Ação desconhecida: {action}"
        )

    return get_profile(profile_name)