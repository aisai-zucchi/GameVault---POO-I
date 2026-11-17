import tkinter as tk
import unittest
from datetime import date

from gamevault import Exemplar, JogoFisico, Membro, SistemaGameVault
from gamevault.interface.estilos import configurar_estilos
from gamevault.interface.tela_historico import TelaHistorico, filtrar_historico


class TestTelaHistorico(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaGameVault()
        self.membro = Membro(1, "Ana", "ana@example.com")
        self.sistema.cadastrar_membro(self.membro)
        jogo = JogoFisico("Minecraft", 2011, plataforma="PC")
        id_jogo = self.sistema.cadastrar_jogo(jogo)
        self.sistema.cadastrar_exemplar(id_jogo, Exemplar("MC-001"))
        self.sistema.cadastrar_exemplar(id_jogo, Exemplar("MC-002"))

        self.finalizado = self.sistema.registrar_emprestimo(
            self.membro,
            "MC-001",
            date(2026, 1, 1),
        )
        self.sistema.devolver_emprestimo(
            self.finalizado.id_emprestimo,
            date(2026, 1, 2),
        )
        self.ativo = self.sistema.registrar_emprestimo(
            self.membro,
            "MC-002",
            date(2026, 1, 2),
        )

        self.root = tk.Tk()
        self.root.withdraw()
        configurar_estilos(self.root)
        self.tela = TelaHistorico(self.root, self.sistema)
        self.tela.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

    def tearDown(self):
        self.root.destroy()

    def test_lista_ativos_e_finalizados(self):
        itens = self.tela.tabela.get_children()
        valores = [self.tela.tabela.item(item, "values") for item in itens]

        self.assertEqual(2, len(itens))
        self.assertEqual("Finalizado", valores[0][5])
        self.assertEqual("02/01/2026", valores[0][4])
        self.assertEqual("Ativo", valores[1][5])
        self.assertEqual("—", valores[1][4])

    def test_filtra_por_status(self):
        self.tela.status_var.set("Ativos")
        self.tela.atualizar()

        itens = self.tela.tabela.get_children()
        self.assertEqual(("emprestimo-2",), itens)

        self.tela.status_var.set("Finalizados")
        self.tela.atualizar()

        self.assertEqual(("emprestimo-1",), self.tela.tabela.get_children())

    def test_busca_por_membro_e_exemplar(self):
        por_membro = filtrar_historico(
            self.sistema.gestor_emprestimos.emprestimos,
            busca="ana",
        )
        por_exemplar = filtrar_historico(
            self.sistema.gestor_emprestimos.emprestimos,
            busca="mc-002",
        )

        self.assertEqual([self.finalizado, self.ativo], por_membro)
        self.assertEqual([self.ativo], por_exemplar)

        self.tela.busca_var.set("inexistente")
        self.root.update_idletasks()

        self.assertEqual((), self.tela.tabela.get_children())
        self.assertTrue(self.tela.estado_vazio.place_info())

    def test_historico_permanece_apos_devolucao(self):
        self.sistema.devolver_emprestimo(
            self.ativo.id_emprestimo,
            date(2026, 1, 3),
        )
        self.tela.atualizar()

        itens = self.tela.tabela.get_children()
        status = [self.tela.tabela.item(item, "values")[5] for item in itens]
        self.assertEqual(["Finalizado", "Finalizado"], status)

    def test_estado_vazio_sem_historico(self):
        tela = TelaHistorico(self.root, SistemaGameVault())
        tela.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

        self.assertEqual((), tela.tabela.get_children())
        self.assertIn("não há", tela.estado_vazio.cget("text"))
        tela.destroy()


if __name__ == "__main__":
    unittest.main()
