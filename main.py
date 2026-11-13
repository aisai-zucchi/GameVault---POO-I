import sys
from datetime import date

from gamevault import (
    CadastroMembros,
    Catalogo,
    Categoria,
    Exemplar,
    GestorEmprestimos,
    JogoDigital,
    JogoFisico,
    Membro,
    SistemaGameVault,
)


def _exibir_catalogo(catalogo: Catalogo) -> None:
    print("\nCATÁLOGO")
    for jogo in catalogo.listar_jogos():
        categoria = (
            jogo.categoria.nome if jogo.categoria is not None else "Sem categoria"
        )
        plataforma = jogo.plataforma or "Plataforma não informada"
        print(
            f"- #{jogo.id_jogo} {jogo.titulo} ({jogo.ano}) | "
            f"{categoria} | {plataforma} | {jogo.resumo_disponibilidade()}"
        )


def _exibir_historico(gestor: GestorEmprestimos) -> None:
    print("\nHISTÓRICO DE EMPRÉSTIMOS")
    for emprestimo in gestor.emprestimos:
        situacao = "ativo" if emprestimo.esta_ativo() else "devolvido"
        print(
            f"- Empréstimo #{emprestimo.id_emprestimo}: "
            f"{emprestimo.membro.nome} / {emprestimo.exemplar.codigo} / {situacao}"
        )


def _configurar_saida_utf8() -> None:
    reconfigurar = getattr(sys.stdout, "reconfigure", None)
    if reconfigurar is not None:
        reconfigurar(encoding="utf-8")


def main() -> None:
    catalogo = Catalogo()
    cadastro_membros = CadastroMembros()
    gestor_emprestimos = GestorEmprestimos()
    sistema = SistemaGameVault(catalogo, cadastro_membros, gestor_emprestimos)

    aventura = Categoria(1, "Aventura")
    catalogo.cadastrar_categoria(aventura)

    minecraft = JogoFisico(
        "Minecraft",
        2011,
        plataforma="PC",
        categoria=aventura,
    )
    stardew_valley = JogoDigital(
        "Stardew Valley",
        2016,
        "Steam",
        plataforma="PC",
        categoria=aventura,
    )
    id_minecraft = sistema.cadastrar_jogo(minecraft)
    id_stardew = sistema.cadastrar_jogo(stardew_valley)

    for numero in range(1, 5):
        sistema.cadastrar_exemplar(
            id_minecraft,
            Exemplar(f"MC-{numero:03d}"),
        )

    ana = Membro(1, "Ana", "ana@example.com")
    bruno = Membro(2, "Bruno", "bruno@example.com")
    sistema.cadastrar_membro(ana)
    sistema.cadastrar_membro(bruno)

    catalogo.atualizar_jogo(
        id_stardew,
        titulo="Stardew Valley Expanded",
        loja_origem="Steam",
    )
    _exibir_catalogo(catalogo)

    hoje = date.today()
    primeiro = sistema.registrar_emprestimo(ana, "MC-001", hoje)
    print(f"\nSUCESSO: empréstimo #{primeiro.id_emprestimo} registrado para Ana.")

    try:
        sistema.registrar_emprestimo(bruno, "MC-001", hoje)
    except ValueError as erro:
        print(f"BLOQUEIO RN01: {erro}")

    segundo = sistema.registrar_emprestimo(ana, "MC-002", hoje)
    terceiro = sistema.registrar_emprestimo(ana, "MC-003", hoje)

    try:
        sistema.registrar_emprestimo(ana, "MC-004", hoje)
    except ValueError as erro:
        print(f"BLOQUEIO RN02: {erro}")

    try:
        sistema.excluir_jogo(id_minecraft)
    except ValueError as erro:
        print(f"EXCLUSÃO BLOQUEADA: {erro}")

    sistema.devolver_emprestimo(primeiro.id_emprestimo, hoje)
    quarto = sistema.registrar_emprestimo(ana, "MC-004", hoje)
    print(
        "DEVOLUÇÃO: MC-001 liberado; "
        f"novo empréstimo #{quarto.id_emprestimo} registrado."
    )

    for emprestimo in (segundo, terceiro, quarto):
        sistema.devolver_emprestimo(emprestimo.id_emprestimo, hoje)

    jogo_removido = sistema.excluir_jogo(id_minecraft)
    print(f"EXCLUSÃO CONCLUÍDA: {jogo_removido.titulo} removido após as devoluções.")

    _exibir_historico(gestor_emprestimos)
    print(f"\nEMPRÉSTIMOS ATIVOS: {len(sistema.listar_emprestimos_ativos())}")
    print(f"JOGOS RESTANTES: {len(catalogo.listar_jogos())}")


if __name__ == "__main__":
    _configurar_saida_utf8()
    main()
