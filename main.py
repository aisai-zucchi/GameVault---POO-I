class Jogo:
    def __init__(self, titulo, ano):
        self.titulo = titulo
        self.ano = ano

    def resumo_disponibilidade(self):
        pass

class JogoFisico(Jogo):
    def __init__(self, titulo, ano, quantidade):
        super().__init__(titulo, ano)
        self.quantidade = quantidade

    def resumo_disponibilidade(self):
        return f"{self.quantidade} exemplares cadastrados"


jogo = JogoFisico("Minecraft", 2011, 3)

print(jogo.titulo)
print(jogo.resumo_disponibilidade())
