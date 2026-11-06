from gamevault.modelos.jogo import Jogo


class Catalogo:
    def __init__(self):
        self.jogos: list[Jogo] = []

    def cadastrar_jogo(self, jogo: Jogo) -> None:
        self.jogos.append(jogo)

    def listar_jogos(self) -> list[Jogo]:
        return self.jogos.copy()
