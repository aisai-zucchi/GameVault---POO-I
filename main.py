class Membro:
    def __init__(self, id_membro: int, nome: str, email: str):
        self.id_membro = id_membro
        self.nome = nome
        self.email = email
        self.emprestimos = []

    def contar_ativos(self) -> int:
        return sum(1 for emp in self.emprestimos if emp.esta_ativo())

    def pode_emprestar(self) -> bool:
        return self.contar_ativos() < 3
class Jogo:
    def __init__(self, titulo, ano):
        self.titulo = titulo
        self.ano = ano

    def resumo_disponibilidade(self) -> str:
        return""

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

class CadastroMembros:
    def __init__(self):
        self.membros: list[Membro] = []

    def cadastrar(self, membro: Membro) -> bool:
        if self.buscar(membro.id_membro) is not None:
            return False
        self.membros.append(membro)
        return True

    def buscar(self, id_membro: int) -> Membro | None:
        for membro in self.membros:
            if membro.id_membro == id_membro:
                return membro
        return None

    def listar(self) -> list[Membro]:
        return self.membros.copy()

catalogo = Catalogo()

jogo1 = JogoFisico("Minecraft", 2011, 3)
jogo2 = JogoDigital("Stardew Valley", 2016, "Steam")

catalogo.cadastrar_jogo(jogo1)
catalogo.cadastrar_jogo(jogo2)

for jogo in catalogo.listar_jogos():
    print(jogo.titulo, "-", jogo.resumo_disponibilidade())
