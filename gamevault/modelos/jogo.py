from abc import ABC, abstractmethod

from gamevault.modelos.exemplar import Exemplar


class Jogo(ABC):
    def __init__(self, titulo: str, ano: int):
        self.titulo = titulo
        self.ano = ano

    @abstractmethod
    def resumo_disponibilidade(self) -> str:
        """Retorna um resumo da disponibilidade do jogo."""


class JogoFisico(Jogo):
    def __init__(self, titulo: str, ano: int):
        super().__init__(titulo, ano)
        self.exemplares: list[Exemplar] = []

    def adicionar_exemplar(self, exemplar: Exemplar) -> None:
        self.exemplares.append(exemplar)

    def obter_disponivel(self) -> Exemplar | None:
        for exemplar in self.exemplares:
            if exemplar.esta_disponivel():
                return exemplar
        return None

    def resumo_disponibilidade(self) -> str:
        quantidade = sum(1 for exemplar in self.exemplares if exemplar.esta_disponivel())
        return f"Exemplares disponíveis: {quantidade}"


class JogoDigital(Jogo):
    def __init__(self, titulo: str, ano: int, loja_origem: str):
        super().__init__(titulo, ano)
        self.loja_origem = loja_origem

    def resumo_disponibilidade(self) -> str:
        return "Jogo digital - somente catalogo"
