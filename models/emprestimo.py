from datetime import date

class Emprestimo:
    def __init__(self, id_emprestimo: int, membro, exemplar, data_inicio: date):
        self._id_emprestimo = id_emprestimo
        self._membro = membro
        self._exemplar = exemplar
        self._data_inicio = data_inicio
        self._data_devolucao = None

    @property
    def id_emprestimo(self) -> int:
        return self._id_emprestimo

    @property
    def membro(self):
        return self._membro

    @property
    def exemplar(self):
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
        if data_devolucao < self._data_inicio:
            raise ValueError("A data de devolução não pode ser anterior à data de início.")
        self._data_devolucao = data_devolucao