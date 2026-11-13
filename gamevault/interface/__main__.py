import argparse
from datetime import date

from gamevault import (
    Categoria,
    Exemplar,
    JogoDigital,
    JogoFisico,
    Membro,
    SistemaGameVault,
)
from gamevault.interface.app import executar


def criar_sistema_demonstracao() -> SistemaGameVault:
    sistema = SistemaGameVault()
    aventura = Categoria(1, "Aventura")
    estrategia = Categoria(2, "Estratégia")
    acao = Categoria(3, "Ação")
    for categoria in (aventura, estrategia, acao):
        sistema.catalogo.cadastrar_categoria(categoria)

    minecraft = JogoFisico(
        "Minecraft",
        2011,
        plataforma="PC",
        categoria=aventura,
    )
    hollow_knight = JogoFisico(
        "Hollow Knight",
        2017,
        plataforma="Nintendo Switch",
        categoria=aventura,
    )
    hades = JogoDigital(
        "Hades",
        2020,
        "Steam",
        plataforma="PC",
        categoria=acao,
    )
    age_of_empires = JogoDigital(
        "Age of Empires II: Definitive Edition",
        2019,
        "Steam",
        plataforma="PC",
        categoria=estrategia,
    )

    id_minecraft = sistema.cadastrar_jogo(minecraft)
    id_hollow_knight = sistema.cadastrar_jogo(hollow_knight)
    sistema.cadastrar_jogo(hades)
    sistema.cadastrar_jogo(age_of_empires)

    for codigo in ("MC-001", "MC-002", "MC-003"):
        sistema.cadastrar_exemplar(id_minecraft, Exemplar(codigo))
    sistema.cadastrar_exemplar(id_hollow_knight, Exemplar("HK-001"))

    membro = Membro(1, "Ana Demo", "ana.demo@example.com")
    sistema.cadastrar_membro(membro)
    sistema.registrar_emprestimo(membro, "MC-002", date.today())
    return sistema


def main() -> None:
    parser = argparse.ArgumentParser(description="Interface gráfica do GameVault")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="abre a interface com dados de exemplo",
    )
    argumentos = parser.parse_args()
    sistema = criar_sistema_demonstracao() if argumentos.demo else None
    executar(sistema, modo_demonstracao=argumentos.demo)


if __name__ == "__main__":
    main()
