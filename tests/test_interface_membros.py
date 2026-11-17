import tkinter as tk
import unittest

from gamevault import Exemplar, JogoFisico, Membro, SistemaGameVault
from gamevault.interface.estilos import configurar_estilos
from gamevault.interface.tela_membros import TelaMembros


class TestTelaMembros(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        configurar_estilos(self.root)
        self.sistema = SistemaGameVault()
        self.notificacoes: list[tuple[str, str]] = []
        self.tela = TelaMembros(
            self.root,
            self.sistema,
            ao_notificar=lambda mensagem, tipo: self.notificacoes.append(
                (mensagem, tipo)
            ),
        )
        self.tela.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

    def tearDown(self):
        self.root.destroy()

    def test_estado_vazio(self):
        self.assertEqual(0, len(self.tela.tabela.get_children()))
        self.assertTrue(self.tela.estado_vazio.place_info())

    def test_cadastra_membro_e_atualiza_tabela(self):
        self.tela._novo_membro()
        formulario = self.tela._formulario
        formulario.id_var.set("7")
        formulario.nome_var.set("Ana")
        formulario.email_var.set("ana@example.com")

        formulario._salvar()
        self.root.update_idletasks()

        membro = self.sistema.cadastro_membros.buscar(7)
        self.assertEqual("Ana", membro.nome)
        self.assertEqual(1, len(self.tela.tabela.get_children()))
        self.assertEqual("1 membro", self.tela.contagem_var.get())
        self.assertEqual(("Membro cadastrado.", "sucesso"), self.notificacoes[-1])

    def test_recusa_id_duplicado(self):
        self.sistema.cadastrar_membro(Membro(1, "Ana", "ana@example.com"))
        self.tela.atualizar()
        self.tela._novo_membro()
        formulario = self.tela._formulario
        formulario.id_var.set("1")
        formulario.nome_var.set("Bia")
        formulario.email_var.set("bia@example.com")

        formulario._salvar()

        self.assertIn("Já existe", formulario.erro_var.get())
        self.assertEqual(1, len(self.sistema.cadastro_membros.listar()))
        formulario.destroy()

    def test_valida_id_nome_e_email(self):
        self.tela._novo_membro()
        formulario = self.tela._formulario
        formulario.id_var.set("abc")
        formulario._salvar()
        self.assertIn("número inteiro", formulario.erro_var.get())

        formulario.id_var.set("2")
        formulario.nome_var.set(" ")
        formulario.email_var.set("bia@example.com")
        formulario._salvar()
        self.assertIn("nome", formulario.erro_var.get().lower())

        formulario.nome_var.set("Bia")
        formulario.email_var.set(" ")
        formulario._salvar()
        self.assertIn("e-mail", formulario.erro_var.get().lower())
        formulario.destroy()

    def test_mostra_quantidade_de_emprestimos_ativos(self):
        membro = Membro(1, "Ana", "ana@example.com")
        self.sistema.cadastrar_membro(membro)
        jogo = JogoFisico("Minecraft", 2011)
        id_jogo = self.sistema.cadastrar_jogo(jogo)
        self.sistema.cadastrar_exemplar(id_jogo, Exemplar("MC-001"))
        self.sistema.registrar_emprestimo(membro, "MC-001")

        self.tela.atualizar()
        valores = self.tela.tabela.item("membro-1", "values")

        self.assertEqual("1", valores[3])
        self.assertEqual(1, membro.contar_ativos())


if __name__ == "__main__":
    unittest.main()
