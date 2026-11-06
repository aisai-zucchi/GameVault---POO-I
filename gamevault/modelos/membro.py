from typing import Protocol


class _EmprestimoAtivo(Protocol):
    def esta_ativo(self) -> bool:
        """Informa se o emprestimo esta ativo."""


class Membro:
    def __init__(self, id_membro: int, nome: str, email: str):
        self.id_membro = id_membro
        self.nome = nome
        self.email = email
        self.emprestimos: list[_EmprestimoAtivo] = []

    def contar_ativos(self) -> int:
        return sum(1 for emprestimo in self.emprestimos if emprestimo.esta_ativo())

    def pode_emprestar(self) -> bool:
        return self.contar_ativos() < 3
