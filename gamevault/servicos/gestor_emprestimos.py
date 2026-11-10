from datetime import date

from gamevault.modelos.exemplar import Exemplar
from gamevault.modelos.membro import Membro
from models.emprestimo import Emprestimo


class GestorEmprestimos:
    """Registra e devolve emprestimos aplicando as regras RN01 e RN02.

    RN01: um membro nao pode ter mais emprestimos ativos que o seu limite.
    RN02: somente exemplares disponiveis podem ser emprestados.
    """

    def __init__(self):
        self._emprestimos: list[Emprestimo] = []
        self._proximo_id: int = 1

    def registrar(self, membro: Membro, exemplar: Exemplar, data_inicio: date) -> Emprestimo:
        if not membro.pode_emprestar():
            raise ValueError("O membro atingiu o limite de empréstimos ativos.")
        if not exemplar.esta_disponivel() or self._exemplar_em_emprestimo_ativo(exemplar):
            raise ValueError("O exemplar não está disponível.")

        emprestimo = Emprestimo(self._proximo_id, membro, exemplar, data_inicio)
        exemplar.marcar_emprestado()
        membro.emprestimos.append(emprestimo)
        self._emprestimos.append(emprestimo)
        self._proximo_id += 1
        return emprestimo

    def devolver(self, id_emprestimo: int, data_devolucao: date) -> Emprestimo:
        emprestimo = self._buscar(id_emprestimo)
        if emprestimo is None:
            raise ValueError("Empréstimo não encontrado.")
        if not emprestimo.esta_ativo():
            raise ValueError("O empréstimo já foi finalizado.")

        # Valida a data antes de liberar o exemplar: se falhar, nada muda.
        emprestimo.finalizar(data_devolucao)
        emprestimo.exemplar.marcar_disponivel()
        return emprestimo

    def listar_ativos(self) -> list[Emprestimo]:
        return [emprestimo for emprestimo in self._emprestimos if emprestimo.esta_ativo()]

    def listar_historico(self) -> list[Emprestimo]:
        return self._emprestimos.copy()

    def _buscar(self, id_emprestimo: int) -> Emprestimo | None:
        for emprestimo in self._emprestimos:
            if emprestimo.id_emprestimo == id_emprestimo:
                return emprestimo
        return None

    def _exemplar_em_emprestimo_ativo(self, exemplar: Exemplar) -> bool:
        return any(
            emprestimo.exemplar is exemplar and emprestimo.esta_ativo()
            for emprestimo in self._emprestimos
        )
