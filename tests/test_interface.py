import importlib
import tkinter as tk
import unittest
from unittest.mock import patch

from gamevault import (
    Categoria,
    Exemplar,
    JogoDigital,
    JogoFisico,
    Membro,
    SistemaGameVault,
)
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

    def test_cadastra_jogo_fisico_e_atualiza_catalogo(self):
        self.tela._novo_jogo()
        formulario = self.tela._formulario_jogo
        formulario.titulo_var.set("Celeste")
        formulario.ano_var.set("2018")
        formulario.plataforma_var.set("PC")
        formulario.categoria_var.set(
            next(iter(formulario._categorias_por_rotulo))
        )

        formulario._salvar()
        self.app.update_idletasks()

        jogo = self.sistema.catalogo.buscar_jogo(3)
        self.assertIsInstance(jogo, JogoFisico)
        self.assertEqual("Celeste", jogo.titulo)
        self.assertIs(self.fisico.categoria, jogo.categoria)
        self.assertEqual(3, len(self.tela.tabela.get_children()))
        self.assertEqual("Jogo cadastrado.", self.app.status_var.get())

    def test_cadastro_digital_exige_loja(self):
        self.tela._novo_jogo()
        formulario = self.tela._formulario_jogo
        formulario.titulo_var.set("Hades")
        formulario.ano_var.set("2020")
        formulario.plataforma_var.set("PC")
        formulario.tipo_var.set("Digital")
        formulario._atualizar_tipo()

        formulario._salvar()

        self.assertIn("loja de origem", formulario.erro_var.get().lower())
        self.assertEqual(2, len(self.sistema.catalogo.listar_jogos()))
        self.assertEqual("grid", formulario.loja_entry.winfo_manager())

        formulario.loja_var.set("Steam")
        formulario._salvar()

        jogo = self.sistema.catalogo.buscar_jogo(3)
        self.assertIsInstance(jogo, JogoDigital)
        self.assertEqual("Steam", jogo.loja_origem)

    def test_edita_jogo_sem_alterar_tipo(self):
        self.tela._editar_jogo()
        formulario = self.tela._formulario_jogo

        self.assertEqual("disabled", str(formulario.tipo_combo.cget("state")))
        formulario.titulo_var.set("Minecraft Java")
        formulario.ano_var.set("2012")
        formulario.plataforma_var.set("Windows")
        formulario._salvar()
        self.app.update_idletasks()

        self.assertIsInstance(self.fisico, JogoFisico)
        self.assertEqual("Minecraft Java", self.fisico.titulo)
        self.assertEqual(2012, self.fisico.ano)
        self.assertEqual("Windows", self.fisico.plataforma)
        self.assertEqual("Jogo atualizado.", self.app.status_var.get())

    def test_exclusao_cancelada_e_confirmada(self):
        with patch(
            "gamevault.interface.tela_catalogo.messagebox.askyesno",
            return_value=False,
        ):
            self.tela._excluir_jogo()

        self.assertIs(self.fisico, self.sistema.catalogo.buscar_jogo(1))

        with patch(
            "gamevault.interface.tela_catalogo.messagebox.askyesno",
            return_value=True,
        ):
            self.tela._excluir_jogo()

        self.assertIsNone(self.sistema.catalogo.buscar_jogo(1))
        self.assertEqual(1, len(self.tela.tabela.get_children()))
        self.assertEqual("Jogo excluído.", self.app.status_var.get())

    def test_exclusao_bloqueada_por_emprestimo_ativo(self):
        membro = Membro(1, "Ana", "ana@example.com")
        self.sistema.cadastrar_membro(membro)
        self.sistema.registrar_emprestimo(membro, "MC-001")

        with patch(
            "gamevault.interface.tela_catalogo.messagebox.askyesno",
            return_value=True,
        ):
            self.tela._excluir_jogo()

        self.assertIs(self.fisico, self.sistema.catalogo.buscar_jogo(1))
        self.assertIn("empréstimo ativo", self.app.status_var.get())

    def test_cadastra_e_renomeia_categoria(self):
        self.tela._abrir_categorias()
        janela = self.tela._janela_categorias
        janela.nome_var.set("RPG")
        janela._cadastrar()

        rpg = self.sistema.catalogo.buscar_categoria(2)
        self.assertEqual("RPG", rpg.nome)

        janela.tabela.selection_set("categoria-1")
        janela._ao_selecionar(None)
        janela.nome_var.set("Exploração")
        janela._renomear()
        self.app.update_idletasks()

        self.assertEqual("Exploração", self.fisico.categoria.nome)
        self.assertIn("Exploração", self.tela.categoria_combo.cget("values"))
        janela.destroy()

    def test_adiciona_exemplar_e_recusa_codigo_repetido(self):
        self.tela._adicionar_exemplar()
        formulario = self.tela._formulario_exemplar
        formulario.codigo_var.set("MC-001")
        formulario._salvar()

        self.assertIn("Já existe", formulario.erro_var.get())
        self.assertEqual(1, len(self.fisico.exemplares))

        formulario.codigo_var.set("MC-002")
        formulario._salvar()
        self.app.update_idletasks()

        self.assertEqual(2, len(self.fisico.exemplares))
        self.assertEqual("2/2 disponíveis", disponibilidade(self.fisico))
        self.assertEqual("Exemplar cadastrado.", self.app.status_var.get())


if __name__ == "__main__":
    unittest.main()
