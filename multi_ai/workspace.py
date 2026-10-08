from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class WorkspaceType(str, Enum):
    GIT_WORKTREE = "git_worktree"
    STAGING_COPY = "staging_copy"
    NEW_PROJECT = "new_project"


@dataclass(frozen=True)
class WorkspacePlan:
    workspace_type: WorkspaceType
    source: Path | None
    target: Path
    project_name: str
    is_git: bool
    is_new_project: bool


class WorkspaceManager:
    def __init__(
        self,
        project: Path,
        workspace_root: Path | None = None,
    ):
        self.project = project.resolve()

        if workspace_root is None:
            workspace_root = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "workspaces"
            )

        self.workspace_root = workspace_root.resolve()

    # ---------------------------------------------------------
    # DETECÇÃO
    # ---------------------------------------------------------

    def is_git_project(self) -> bool:
        """
        Verificação conservadora.

        Nesta primeira versão consideramos Git quando existe
        .git diretamente na raiz do projeto.

        Depois evoluiremos para `git rev-parse`.
        """

        return (self.project / ".git").exists()

    def project_exists(self) -> bool:
        return self.project.exists()

    # ---------------------------------------------------------
    # PLANEJAMENTO
    # ---------------------------------------------------------

    def plan_existing(self) -> WorkspacePlan:
        """
        Planeja um workspace para um projeto existente.

        NÃO cria arquivos.
        NÃO executa Git.
        NÃO copia o projeto.
        """

        if not self.project_exists():
            raise ValueError(
                f"Projeto não encontrado: {self.project}"
            )

        project_name = self.project.name

        if self.is_git_project():
            workspace_type = WorkspaceType.GIT_WORKTREE
        else:
            workspace_type = WorkspaceType.STAGING_COPY

        target = (
            self.workspace_root
            / project_name
            / "workspace"
        )

        return WorkspacePlan(
            workspace_type=workspace_type,
            source=self.project,
            target=target,
            project_name=project_name,
            is_git=self.is_git_project(),
            is_new_project=False,
        )

    def plan_new(
        self,
        project_name: str,
    ) -> WorkspacePlan:
        """
        Planeja a criação de um projeto novo.

        O projeto será inicialmente construído em staging,
        e não diretamente no diretório final.
        """

        project_name = project_name.strip()

        if not project_name:
            raise ValueError(
                "Nome do projeto não pode ser vazio."
            )

        # Evita que o nome do projeto seja usado como caminho.
        if Path(project_name).name != project_name:
            raise ValueError(
                "Nome de projeto inválido."
            )

        if project_name in {".", ".."}:
            raise ValueError(
                "Nome de projeto inválido."
            )

        target = (
            self.workspace_root
            / project_name
            / "workspace"
        )

        return WorkspacePlan(
            workspace_type=WorkspaceType.NEW_PROJECT,
            source=None,
            target=target,
            project_name=project_name,
            is_git=False,
            is_new_project=True,
        )