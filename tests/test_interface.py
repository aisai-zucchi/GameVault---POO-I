import importlib
import tkinter as tk
import unittest

from gamevault import Categoria, Exemplar, JogoDigital, JogoFisico, SistemaGameVault
from gamevault.interface.app import GameVaultApp
from gamevault.interface.tela_catalogo import disponibilidade, filtrar_catalogo


class TestImportacaoInterface(unittest.TestCase):
    def test_importar_modulo_nao_cria_janela(self):
        import gamevault.interface.app as modulo

        importlib.reload(modulo)

        self.assertIsNone(tk._default_root)


class TestTelaCatalogo(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaGameVault()
        aventura = Categoria(1, "Aventura")
        self.sistema.catalogo.cadastrar_categoria(aventura)

        self.fisico = JogoFisico(
            "Minecraft",
            2011,
            plataforma="PC",
            categoria=aventura,
        )
        self.digital = JogoDigital(
            "Stardew Valley",
            2016,
            "Steam",
            plataforma="PC",
            categoria=aventura,
        )
        id_fisico = self.sistema.cadastrar_jogo(self.fisico)
        self.sistema.cadastrar_jogo(self.digital)
        self.sistema.cadastrar_exemplar(id_fisico, Exemplar("MC-001"))

        self.app = GameVaultApp(self.sistema)
        self.app.withdraw()
        self.app.update_idletasks()
        self.tela = self.app.tela_catalogo

    def tearDown(self):
        self.app.destroy()

    def test_janela_tem_titulo_legitimo(self):
        titulo = self.app.title()

        self.assertEqual("GameVault | Catálogo de Jogos", titulo)

    def test_logo_e_carregada(self):
        self.assertIsNotNone(self.app._logo)

    def test_catalogo_exibe_jogos_e_detalhe_inicial(self):
        self.assertEqual(2, len(self.tela.tabela.get_children()))
        self.assertEqual("Minecraft", self.tela.titulo_detalhe.cget("text"))
        self.assertEqual("1/1 disponíveis", disponibilidade(self.fisico))
        self.assertEqual("Acesso digital", disponibilidade(self.digital))

    def test_pesquisa_filtra_titulo_e_atualiza_detalhe(self):
        self.tela.busca_var.set("star")
        self.app.update_idletasks()

        self.assertEqual(1, len(self.tela.tabela.get_children()))
        self.assertEqual("Stardew Valley", self.tela.titulo_detalhe.cget("text"))

    def test_filtros_delegam_consulta_ao_catalogo(self):
        encontrados = filtrar_catalogo(
            self.sistema.catalogo,
            tipo="Físicos",
            categoria="Aventura",
            plataforma="PC",
        )

        self.assertEqual([self.fisico], encontrados)

    def test_estado_vazio_aparece_quando_nao_ha_resultados(self):
        self.tela.busca_var.set("inexistente")
        self.app.update_idletasks()

        self.assertEqual(0, len(self.tela.tabela.get_children()))
        self.assertTrue(self.tela.estado_vazio.place_info())


if __name__ == "__main__":
    unittest.main()
