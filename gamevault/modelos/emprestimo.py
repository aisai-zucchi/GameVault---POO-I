from datetime import date, datetime

from gamevault.modelos.exemplar import Exemplar
from gamevault.modelos.membro import Membro


class Emprestimo:
    def __init__(
        self,
        id_emprestimo: int,
        membro: Membro,
        exemplar: Exemplar,
        data_inicio: date,
        data_devolucao: date | None = None,
    ):
        if isinstance(id_emprestimo, bool) or not isinstance(id_emprestimo, int):
            raise TypeError("O ID do empréstimo deve ser um número inteiro.")
        if id_emprestimo <= 0:
            raise ValueError("O ID do empréstimo deve ser positivo.")
        if not isinstance(membro, Membro):
            raise TypeError("O empréstimo deve estar associado a um membro válido.")
        if not isinstance(exemplar, Exemplar):
            raise TypeError("O empréstimo deve estar associado a um exemplar válido.")

        self._id_emprestimo = id_emprestimo
        self._membro = membro
        self._exemplar = exemplar
        self._data_inicio = self._validar_data(data_inicio, "início")
        self._data_devolucao: date | None = None

        if data_devolucao is not None:
            self.finalizar(data_devolucao)

    @property
    def id_emprestimo(self) -> int:
        return self._id_emprestimo

    @property
    def membro(self) -> Membro:
        return self._membro

    @property
    def exemplar(self) -> Exemplar:
        return self._exemplar

    @property
    def data_inicio(self) -> date:
        return self._data_inicio

    @property
    def data_devolucao(self) -> date | None:
        return self._data_devolucao

    def esta_ativo(self) -> bool:
        return self._data_devolucao is None

    def finalizar(self, data_devolucao: date) -> None:
        if not self.esta_ativo():
            raise ValueError("O empréstimo já foi finalizado.")

        data_devolucao = self._validar_data(data_devolucao, "devolução")
        if data_devolucao < self._data_inicio:
            raise ValueError(
                "A data de devolução não pode ser anterior à data de início."
            )
        self._data_devolucao = data_devolucao

    @staticmethod
    def _validar_data(valor: date, nome: str) -> date:
        if isinstance(valor, datetime) or not isinstance(valor, date):
            raise TypeError(f"A data de {nome} deve ser do tipo date.")
        return valor
