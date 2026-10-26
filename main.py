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

class JogoDigital(Jogo):
    def __init__(self, titulo, ano, loja_origem):
        super().__init__(titulo, ano)
        self.loja_origem = loja_origem

    def resumo_disponibilidade(self):
        return "Jogo digital - somente catalogo"

class Catalogo:
    def __init__(self):
        self.jogos = []

    def cadastrar_jogo(self, jogo):
        self.jogos.append(jogo)

    def listar_jogos(self):
        return self.jogos

catalogo = Catalogo()

jogo1 = JogoFisico("Minecraft", 2011, 3)
jogo2 = JogoDigital("Stardew Valley", 2016, "Steam")

catalogo.cadastrar_jogo(jogo1)
catalogo.cadastrar_jogo(jogo2)

for jogo in catalogo.listar_jogos():
    print(jogo.titulo, "-", jogo.resumo_disponibilidade())