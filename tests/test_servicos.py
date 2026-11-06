import unittest

from gamevault import (
    CadastroMembros,
    Catalogo,
    Categoria,
    Exemplar,
    JogoDigital,
    JogoFisico,
    Membro,
)


class TestCadastroMembros(unittest.TestCase):
    def test_cadastra_e_busca_membro(self):
        cadastro = CadastroMembros()
        membro = Membro(1, "Ana", "ana@example.com")

        self.assertTrue(cadastro.cadastrar(membro))
        self.assertIs(membro, cadastro.buscar(1))
        self.assertIsNone(cadastro.buscar(2))

    def test_recusa_id_duplicado(self):
        cadastro = CadastroMembros()
        cadastro.cadastrar(Membro(1, "Ana", "ana@example.com"))

        self.assertFalse(cadastro.cadastrar(Membro(1, "Bia", "bia@example.com")))

    def test_listagem_de_membros_e_uma_copia(self):
        cadastro = CadastroMembros()
        cadastro.cadastrar(Membro(1, "Ana", "ana@example.com"))

        membros = cadastro.listar()
        membros.clear()

        self.assertEqual(1, len(cadastro.listar()))

    def test_propriedade_membros_e_uma_copia(self):
        cadastro = CadastroMembros()
        cadastro.cadastrar(Membro(1, "Ana", "ana@example.com"))

        membros = cadastro.membros
        membros.clear()

        self.assertEqual(1, len(cadastro.membros))


class TestCatalogo(unittest.TestCase):
    def test_cadastra_e_lista_jogos(self):
        catalogo = Catalogo()
        jogo = JogoDigital("Stardew Valley", 2016, "Steam")

        catalogo.cadastrar_jogo(jogo)

        self.assertEqual([jogo], catalogo.listar_jogos())

    def test_listagem_de_jogos_e_uma_copia(self):
        catalogo = Catalogo()
        catalogo.cadastrar_jogo(JogoDigital("Stardew Valley", 2016, "Steam"))

        jogos = catalogo.listar_jogos()
        jogos.clear()

        self.assertEqual(1, len(catalogo.listar_jogos()))

    def test_atribui_ids_automaticos_sequenciais(self):
        catalogo = Catalogo()
        primeiro = JogoFisico("Minecraft", 2011)
        segundo = JogoDigital("Stardew Valley", 2016, "Steam")

        self.assertEqual(1, catalogo.cadastrar(primeiro))
        self.assertEqual(2, catalogo.cadastrar(segundo))
        self.assertIs(primeiro, catalogo.buscar(1))
        self.assertIsNone(catalogo.buscar(3))

    def test_preserva_id_explicito_e_recusa_duplicado(self):
        catalogo = Catalogo()
        catalogo.cadastrar_jogo(JogoFisico("Minecraft", 2011, id_jogo=10))

        with self.assertRaises(ValueError):
            catalogo.cadastrar_jogo(JogoFisico("Terraria", 2011, id_jogo=10))

        proximo = JogoDigital("Stardew Valley", 2016, "Steam")
        self.assertEqual(11, catalogo.cadastrar_jogo(proximo))

    def test_atualiza_jogo_e_loja_digital(self):
        catalogo = Catalogo()
        jogo = JogoDigital("Stardew", 2015, "GOG")
        id_jogo = catalogo.cadastrar_jogo(jogo)

        atualizado = catalogo.atualizar(
            id_jogo,
            titulo="Stardew Valley",
            ano=2016,
            loja_origem="Steam",
        )

        self.assertIs(jogo, atualizado)
        self.assertEqual("Stardew Valley", jogo.titulo)
        self.assertEqual(2016, jogo.ano)
        self.assertEqual("Steam", jogo.loja_origem)

    def test_atualizacao_incompativel_nao_altera_jogo(self):
        catalogo = Catalogo()
        jogo = JogoFisico("Minecraft", 2011)
        id_jogo = catalogo.cadastrar_jogo(jogo)

        with self.assertRaises(ValueError):
            catalogo.atualizar_jogo(
                id_jogo,
                titulo="Minecraft Java",
                loja_origem="Steam",
            )

        self.assertEqual("Minecraft", jogo.titulo)

    def test_exclui_jogo_sem_emprestimo_ativo(self):
        catalogo = Catalogo()
        jogo = JogoFisico("Minecraft", 2011)
        id_jogo = catalogo.cadastrar_jogo(jogo)

        self.assertIs(jogo, catalogo.excluir(id_jogo))
        self.assertIsNone(catalogo.buscar_jogo(id_jogo))

    def test_nao_exclui_jogo_com_exemplar_emprestado(self):
        catalogo = Catalogo()
        jogo = JogoFisico("Minecraft", 2011)
        id_jogo = catalogo.cadastrar_jogo(jogo)
        exemplar = Exemplar("MC-001")
        catalogo.cadastrar_exemplar(id_jogo, exemplar)
        exemplar.marcar_emprestado()

        with self.assertRaises(ValueError):
            catalogo.excluir_jogo(id_jogo)

    def test_cadastra_e_lista_categorias_sem_expor_colecao(self):
        catalogo = Catalogo()
        categoria = Categoria(1, "Aventura")
        catalogo.cadastrar_categoria(categoria)

        categorias = catalogo.listar_categorias()
        categorias.clear()

        self.assertIs(categoria, catalogo.buscar_categoria(1))
        self.assertEqual([categoria], catalogo.categorias)
        with self.assertRaises(ValueError):
            catalogo.cadastrar_categoria(Categoria(1, "RPG"))

    def test_filtra_jogos_por_titulo_ano_e_tipo(self):
        catalogo = Catalogo()
        minecraft = JogoFisico("Minecraft", 2011)
        stardew = JogoDigital("Stardew Valley", 2016, "Steam")
        catalogo.cadastrar_jogo(minecraft)
        catalogo.cadastrar_jogo(stardew)

        self.assertEqual([minecraft], catalogo.filtrar_jogos(titulo="craft"))
        self.assertEqual([stardew], catalogo.filtrar_jogos(ano=2016))
        self.assertEqual([minecraft], catalogo.filtrar_jogos(tipo="fisico"))

    def test_localiza_exemplar_e_recusa_codigo_duplicado(self):
        catalogo = Catalogo()
        primeiro = JogoFisico("Minecraft", 2011)
        segundo = JogoFisico("Terraria", 2011)
        id_primeiro = catalogo.cadastrar_jogo(primeiro)
        id_segundo = catalogo.cadastrar_jogo(segundo)
        exemplar = Exemplar("MC-001")
        catalogo.cadastrar_exemplar(id_primeiro, exemplar)

        self.assertIs(exemplar, catalogo.localizar_exemplar("mc-001"))
        with self.assertRaises(ValueError):
            catalogo.cadastrar_exemplar(id_segundo, Exemplar("MC-001"))

    def test_nao_adiciona_exemplar_a_jogo_digital(self):
        catalogo = Catalogo()
        id_jogo = catalogo.cadastrar_jogo(
            JogoDigital("Stardew Valley", 2016, "Steam")
        )

        with self.assertRaises(ValueError):
            catalogo.cadastrar_exemplar(id_jogo, Exemplar("SD-001"))


if __name__ == "__main__":
    unittest.main()
