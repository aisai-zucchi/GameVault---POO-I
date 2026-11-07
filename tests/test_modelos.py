import unittest

from gamevault import Categoria, Exemplar, Jogo, JogoDigital, JogoFisico, Membro


class EmprestimoFalso:
    def __init__(self, ativo: bool):
        self.ativo = ativo

    def esta_ativo(self) -> bool:
        return self.ativo


class TestCategoria(unittest.TestCase):
    def test_renomear_categoria(self):
        categoria = Categoria(1, "Aventura")

        categoria.renomear("Sobrevivencia")

        self.assertEqual("Sobrevivencia", categoria.nome)

    def test_nao_aceita_nome_vazio(self):
        categoria = Categoria(1, "Aventura")

        with self.assertRaises(ValueError):
            categoria.renomear("   ")


class TestExemplar(unittest.TestCase):
    def test_controlar_disponibilidade(self):
        exemplar = Exemplar("MC-001")

        self.assertTrue(exemplar.esta_disponivel())
        exemplar.marcar_emprestado()
        self.assertFalse(exemplar.esta_disponivel())
        exemplar.marcar_disponivel()
        self.assertTrue(exemplar.esta_disponivel())

    def test_nao_empresta_exemplar_indisponivel(self):
        exemplar = Exemplar("MC-001")
        exemplar.marcar_emprestado()

        with self.assertRaises(ValueError):
            exemplar.marcar_emprestado()


class TestJogos(unittest.TestCase):
    def test_jogo_e_abstrato(self):
        with self.assertRaises(TypeError):
            Jogo("Jogo", 2026)

    def test_jogo_fisico_retorna_primeiro_exemplar_disponivel(self):
        jogo = JogoFisico("Minecraft", 2011)
        primeiro = Exemplar("MC-001")
        segundo = Exemplar("MC-002")
        jogo.adicionar_exemplar(primeiro)
        jogo.adicionar_exemplar(segundo)

        self.assertIs(primeiro, jogo.obter_disponivel())
        primeiro.marcar_emprestado()
        self.assertIs(segundo, jogo.obter_disponivel())
        self.assertEqual("Exemplares disponíveis: 1", jogo.resumo_disponibilidade())

    def test_jogo_fisico_sem_exemplar_disponivel(self):
        jogo = JogoFisico("Minecraft", 2011)

        self.assertIsNone(jogo.obter_disponivel())
        self.assertEqual("Exemplares disponíveis: 0", jogo.resumo_disponibilidade())

    def test_jogo_digital_preserva_loja(self):
        jogo = JogoDigital("Stardew Valley", 2016, "Steam")

        self.assertEqual("Steam", jogo.loja_origem)
        self.assertEqual("Jogo digital - somente catalogo", jogo.resumo_disponibilidade())


class TestMembro(unittest.TestCase):
    def test_conta_somente_emprestimos_ativos(self):
        membro = Membro(1, "Ana", "ana@example.com")
        membro.emprestimos.extend([EmprestimoFalso(True), EmprestimoFalso(False)])

        self.assertEqual(1, membro.contar_ativos())
        self.assertTrue(membro.pode_emprestar())

    def test_limita_tres_emprestimos_ativos(self):
        membro = Membro(1, "Ana", "ana@example.com")
        membro.emprestimos.extend(EmprestimoFalso(True) for _ in range(3))

        self.assertFalse(membro.pode_emprestar())


if __name__ == "__main__":
    unittest.main()
