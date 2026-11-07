from gamevault import Catalogo, Exemplar, JogoDigital, JogoFisico


def main() -> None:
    catalogo = Catalogo()

<<<<<<< HEAD
    def resumo_disponibilidade(self) -> str:
        return""
=======
    minecraft = JogoFisico("Minecraft", 2011)
    minecraft.adicionar_exemplar(Exemplar("MC-001"))
>>>>>>> 18c65c847b266eb5c7a1a6272754a3884e9e36f2

    stardew_valley = JogoDigital("Stardew Valley", 2016, "Steam")

    catalogo.cadastrar_jogo(minecraft)
    catalogo.cadastrar_jogo(stardew_valley)

    for jogo in catalogo.listar_jogos():
        print(jogo.titulo, "-", jogo.resumo_disponibilidade())


<<<<<<< HEAD
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
=======
if __name__ == "__main__":
    main()
>>>>>>> 18c65c847b266eb5c7a1a6272754a3884e9e36f2
