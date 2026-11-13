from datetime import date

from gamevault.modelos.emprestimo import Emprestimo
from gamevault.modelos.exemplar import Exemplar
from gamevault.modelos.membro import Membro


class GestorEmprestimos:
    def __init__(self):
        self._emprestimos: list[Emprestimo] = []
        self._proximo_id_emprestimo = 1

    @property
    def emprestimos(self) -> list[Emprestimo]:
        return self._emprestimos.copy()

    def registrar(
        self,
        membro: Membro,
        exemplar: Exemplar,
        data_inicio: date | None = None,
    ) -> Emprestimo:
        if not isinstance(membro, Membro):
            raise TypeError("O empréstimo deve ser registrado para um membro válido.")
        if not isinstance(exemplar, Exemplar):
            raise TypeError("O empréstimo exige um exemplar físico válido.")

        # RN01: apenas exemplares disponíveis e sem outro empréstimo ativo.
        if not exemplar.esta_disponivel() or self._tem_emprestimo_ativo(exemplar):
            raise ValueError("RN01: o exemplar não está disponível para empréstimo.")

        # RN02: cada membro pode manter no máximo três empréstimos ativos.
        if not membro.pode_emprestar():
            raise ValueError("RN02: o membro atingiu o limite de empréstimos ativos.")

        inicio = date.today() if data_inicio is None else data_inicio
        emprestimo = Emprestimo(
            self._proximo_id_emprestimo,
            membro,
            exemplar,
            inicio,
        )

        exemplar.marcar_emprestado()
        membro.adicionar_emprestimo(emprestimo)
        self._emprestimos.append(emprestimo)
        self._proximo_id_emprestimo += 1
        return emprestimo

    def buscar(self, id_emprestimo: int) -> Emprestimo | None:
        for emprestimo in self._emprestimos:
            if emprestimo.id_emprestimo == id_emprestimo:
                return emprestimo
        return None

    def devolver(
        self,
        id_emprestimo: int,
        data_devolucao: date | None = None,
    ) -> bool:
        emprestimo = self.buscar(id_emprestimo)
        if emprestimo is None or not emprestimo.esta_ativo():
            return False

        devolucao = date.today() if data_devolucao is None else data_devolucao
        # Finalizar primeiro mantém o exemplar indisponível se a data for inválida.
        emprestimo.finalizar(devolucao)
        emprestimo.exemplar.marcar_disponivel()
        return True

    def listar_ativos(self) -> list[Emprestimo]:
        return [
            emprestimo
            for emprestimo in self._emprestimos
            if emprestimo.esta_ativo()
        ]

    def _tem_emprestimo_ativo(self, exemplar: Exemplar) -> bool:
        codigo = exemplar.codigo.casefold()
        return any(
            emprestimo.esta_ativo()
            and emprestimo.exemplar.codigo.casefold() == codigo
            for emprestimo in self._emprestimos
        )
