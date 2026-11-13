from abc import ABC, abstractmethod

from gamevault.modelos.categoria import Categoria
from gamevault.modelos.exemplar import Exemplar


class Jogo(ABC):
    def __init__(
        self,
        titulo: str,
        ano: int,
        id_jogo: int | None = None,
        plataforma: str | None = None,
        categoria: Categoria | None = None,
    ):
        self._id_jogo: int | None = None
        self._titulo = self._validar_titulo(titulo)
        self._ano = self._validar_ano(ano)
        self._plataforma = self._validar_plataforma(plataforma)
        self._categoria: Categoria | None = None
        if categoria is not None:
            self.definir_categoria(categoria)
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

    @property
    def plataforma(self) -> str | None:
        return self._plataforma

    @property
    def categoria(self) -> Categoria | None:
        return self._categoria

    def atualizar_dados(
        self,
        titulo: str | None = None,
        ano: int | None = None,
        plataforma: str | None = None,
    ) -> None:
        novo_titulo = self._titulo if titulo is None else self._validar_titulo(titulo)
        novo_ano = self._ano if ano is None else self._validar_ano(ano)
        nova_plataforma = (
            self._plataforma
            if plataforma is None
            else self._validar_plataforma(plataforma)
        )
        self._titulo = novo_titulo
        self._ano = novo_ano
        self._plataforma = nova_plataforma

    def definir_categoria(self, categoria: Categoria) -> None:
        if not isinstance(categoria, Categoria):
            raise TypeError("A categoria do jogo deve ser uma Categoria válida.")
        self._categoria = categoria

    def _atribuir_id(self, id_jogo: int) -> None:
        if isinstance(id_jogo, bool) or not isinstance(id_jogo, int) or id_jogo <= 0:
            raise ValueError("O ID do jogo deve ser um inteiro positivo.")
        if self._id_jogo is not None and self._id_jogo != id_jogo:
            raise ValueError("O ID de um jogo não pode ser alterado.")
        self._id_jogo = id_jogo

    @staticmethod
    def _validar_titulo(titulo: str) -> str:
        if not isinstance(titulo, str):
            raise TypeError("O título do jogo deve ser um texto.")
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("O título do jogo não pode ficar vazio.")
        return titulo

    @staticmethod
    def _validar_ano(ano: int) -> int:
        if isinstance(ano, bool) or not isinstance(ano, int) or ano <= 0:
            raise ValueError("O ano do jogo deve ser um inteiro positivo.")
        return ano

    @staticmethod
    def _validar_plataforma(plataforma: str | None) -> str | None:
        if plataforma is None:
            return None
        if not isinstance(plataforma, str):
            raise TypeError("A plataforma do jogo deve ser um texto.")
        plataforma = plataforma.strip()
        if not plataforma:
            raise ValueError("A plataforma do jogo não pode ficar vazia.")
        return plataforma

    @abstractmethod
    def resumo_disponibilidade(self) -> str:
        """Retorna um resumo da disponibilidade do jogo."""


class JogoFisico(Jogo):
    def __init__(
        self,
        titulo: str,
        ano: int,
        id_jogo: int | None = None,
        plataforma: str | None = None,
        categoria: Categoria | None = None,
    ):
        super().__init__(titulo, ano, id_jogo, plataforma, categoria)
        self._exemplares: list[Exemplar] = []

    @property
    def exemplares(self) -> list[Exemplar]:
        return self._exemplares.copy()

    def adicionar_exemplar(self, exemplar: Exemplar) -> None:
        if not isinstance(exemplar, Exemplar):
            raise TypeError("Apenas exemplares válidos podem ser adicionados.")
        if any(
            existente.codigo.casefold() == exemplar.codigo.casefold()
            for existente in self._exemplares
        ):
            raise ValueError("Já existe um exemplar com este código no jogo.")
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
        plataforma: str | None = None,
        categoria: Categoria | None = None,
    ):
        super().__init__(titulo, ano, id_jogo, plataforma, categoria)
        self._loja_origem = self._validar_loja_origem(loja_origem)

    @property
    def loja_origem(self) -> str:
        return self._loja_origem

    def alterar_loja_origem(self, nova_loja: str) -> None:
        self._loja_origem = self._validar_loja_origem(nova_loja)

    @staticmethod
    def _validar_loja_origem(loja: str) -> str:
        if not isinstance(loja, str):
            raise TypeError("A loja de origem deve ser um texto.")
        loja = loja.strip()
        if not loja:
            raise ValueError("A loja de origem não pode ficar vazia.")
        return loja

    def resumo_disponibilidade(self) -> str:
        return "Jogo digital - somente catalogo"
