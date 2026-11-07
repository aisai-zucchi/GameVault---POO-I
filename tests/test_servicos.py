import unittest

from gamevault import CadastroMembros, Catalogo, JogoDigital, Membro


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


if __name__ == "__main__":
    unittest.main()
