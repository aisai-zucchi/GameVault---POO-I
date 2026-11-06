from typing import Protocol


class _EmprestimoAtivo(Protocol):
    def esta_ativo(self) -> bool:
        """Informa se o emprestimo esta ativo."""


class Membro:
    def __init__(self, id_membro: int, nome: str, email: str):
        nome = nome.strip()
        email = email.strip()
        if not nome:
            raise ValueError("O nome do membro não pode ficar vazio.")
        if not email:
            raise ValueError("O e-mail do membro não pode ficar vazio.")
        self._id_membro = id_membro
        self._nome = nome
        self._email = email
        self._emprestimos: list[_EmprestimoAtivo] = []

    @property
    def id_membro(self) -> int:
        return self._id_membro

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def email(self) -> str:
        return self._email

    @property
    def emprestimos(self) -> list[_EmprestimoAtivo]:
        return self._emprestimos.copy()

    def adicionar_emprestimo(self, emprestimo: _EmprestimoAtivo) -> None:
        self._emprestimos.append(emprestimo)

    def contar_ativos(self) -> int:
        return sum(1 for emprestimo in self._emprestimos if emprestimo.esta_ativo())

    def pode_emprestar(self) -> bool:
        return self.contar_ativos() < 3
