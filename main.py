from gamevault import Catalogo, Exemplar, JogoDigital, JogoFisico


def main() -> None:
    catalogo = Catalogo()

    minecraft = JogoFisico("Minecraft", 2011)
    minecraft.adicionar_exemplar(Exemplar("MC-001"))

    stardew_valley = JogoDigital("Stardew Valley", 2016, "Steam")

    catalogo.cadastrar_jogo(minecraft)
    catalogo.cadastrar_jogo(stardew_valley)

    for jogo in catalogo.listar_jogos():
        print(jogo.titulo, "-", jogo.resumo_disponibilidade())


if __name__ == "__main__":
    main()
