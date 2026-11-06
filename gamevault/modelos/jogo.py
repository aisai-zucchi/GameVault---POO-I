from abc import ABC, abstractmethod

from gamevault.modelos.exemplar import Exemplar


class Jogo(ABC):
    def __init__(self, titulo: str, ano: int, id_jogo: int | None = None):
        self._id_jogo: int | None = None
        self._titulo = self._validar_titulo(titulo)
        self._ano = self._validar_ano(ano)
        if id_jogo is not None:
            self._atribuir_id(id_jogo)

    @property
    def id_jogo(self) -> int | None:
        return self._id_jogo

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def ano(self) -> int:
        return self._ano

    def atualizar_dados(self, titulo: str | None = None, ano: int | None = None) -> None:
        novo_titulo = self._titulo if titulo is None else self._validar_titulo(titulo)
        novo_ano = self._ano if ano is None else self._validar_ano(ano)
        self._titulo = novo_titulo
        self._ano = novo_ano

    def _atribuir_id(self, id_jogo: int) -> None:
        if isinstance(id_jogo, bool) or not isinstance(id_jogo, int) or id_jogo <= 0:
            raise ValueError("O ID do jogo deve ser um inteiro positivo.")
        if self._id_jogo is not None and self._id_jogo != id_jogo:
            raise ValueError("O ID de um jogo não pode ser alterado.")
        self._id_jogo = id_jogo

    @staticmethod
    def _validar_titulo(titulo: str) -> str:
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("O título do jogo não pode ficar vazio.")
        return titulo

    @staticmethod
    def _validar_ano(ano: int) -> int:
        if isinstance(ano, bool) or not isinstance(ano, int) or ano <= 0:
            raise ValueError("O ano do jogo deve ser um inteiro positivo.")
        return ano

    @abstractmethod
    def resumo_disponibilidade(self) -> str:
        """Retorna um resumo da disponibilidade do jogo."""


class JogoFisico(Jogo):
    def __init__(self, titulo: str, ano: int, id_jogo: int | None = None):
        super().__init__(titulo, ano, id_jogo)
        self._exemplares: list[Exemplar] = []

    @property
    def exemplares(self) -> list[Exemplar]:
        return self._exemplares.copy()

    def adicionar_exemplar(self, exemplar: Exemplar) -> None:
        self._exemplares.append(exemplar)

    def obter_disponivel(self) -> Exemplar | None:
        for exemplar in self._exemplares:
            if exemplar.esta_disponivel():
                return exemplar
        return None

    def resumo_disponibilidade(self) -> str:
        quantidade = sum(
            1 for exemplar in self._exemplares if exemplar.esta_disponivel()
        )
        return f"Exemplares disponíveis: {quantidade}"


class JogoDigital(Jogo):
    def __init__(
        self,
        titulo: str,
        ano: int,
        loja_origem: str,
        id_jogo: int | None = None,
    ):
        super().__init__(titulo, ano, id_jogo)
        self._loja_origem = self._validar_loja_origem(loja_origem)

    @property
    def loja_origem(self) -> str:
        return self._loja_origem

    def alterar_loja_origem(self, nova_loja: str) -> None:
        self._loja_origem = self._validar_loja_origem(nova_loja)

    @staticmethod
    def _validar_loja_origem(loja: str) -> str:
        loja = loja.strip()
        if not loja:
            raise ValueError("A loja de origem não pode ficar vazia.")
        return loja

    def resumo_disponibilidade(self) -> str:
        return "Jogo digital - somente catalogo"
