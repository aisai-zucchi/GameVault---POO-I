import tkinter as tk
import unittest
from datetime import date

from gamevault import Exemplar, JogoFisico, Membro, SistemaGameVault
from gamevault.interface.estilos import configurar_estilos
from gamevault.interface.tela_emprestimos import (
    SEM_EXEMPLARES,
    SEM_MEMBROS,
    TelaEmprestimos,
    converter_data,
)


DATA_INICIO = date(2026, 11, 13)
DATA_DEVOLUCAO = date(2026, 11, 14)


class TestTelaEmprestimos(unittest.TestCase):
    def setUp(self):
        self.sistema = SistemaGameVault()
        self.membro = Membro(1, "Ana", "ana@example.com")
        self.sistema.cadastrar_membro(self.membro)
        self.jogo = JogoFisico("Minecraft", 2011, plataforma="PC")
        self.id_jogo = self.sistema.cadastrar_jogo(self.jogo)
        self.exemplares = [
            Exemplar(f"MC-{numero:03d}") for numero in range(1, 5)
        ]
        for exemplar in self.exemplares:
            self.sistema.cadastrar_exemplar(self.id_jogo, exemplar)

        self.root = tk.Tk()
        self.root.withdraw()
        configurar_estilos(self.root)
        self.notificacoes: list[tuple[str, str]] = []
        self.tela = TelaEmprestimos(
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

    def _selecionar_membro(self) -> None:
        rotulo = next(
            rotulo
            for rotulo, membro in self.tela._membros_por_rotulo.items()
            if membro is self.membro
        )
        self.tela.membro_var.set(rotulo)

    def _selecionar_exemplar(self, exemplar: Exemplar) -> None:
        rotulo = next(
            rotulo
            for rotulo, cadastrado in self.tela._exemplares_por_rotulo.items()
            if cadastrado is exemplar
        )
        self.tela.exemplar_var.set(rotulo)

    def test_registra_emprestimo_e_atualiza_listas(self):
        self._selecionar_membro()
        self._selecionar_exemplar(self.exemplares[0])
        self.tela.data_inicio_var.set("13/11/2026")

        self.tela._registrar()

        ativos = self.sistema.listar_emprestimos_ativos()
        self.assertEqual(1, len(ativos))
        self.assertIs(self.exemplares[0], ativos[0].exemplar)
        self.assertFalse(self.exemplares[0].esta_disponivel())
        self.assertEqual(1, len(self.tela.tabela.get_children()))
        self.assertNotIn(
            self.exemplares[0],
            self.tela._exemplares_por_rotulo.values(),
        )
        self.assertEqual("Empréstimo registrado.", self.tela.feedback_var.get())

    def test_devolve_emprestimo_e_libera_exemplar(self):
        emprestimo = self.sistema.registrar_emprestimo(
            self.membro,
            self.exemplares[0],
            DATA_INICIO,
        )
        self.tela.atualizar()
        item = f"emprestimo-{emprestimo.id_emprestimo}"
        self.tela.tabela.selection_set(item)
        self.tela._ao_selecionar(None)
        self.tela.data_devolucao_var.set("14/11/2026")

        self.tela._devolver()

        self.assertFalse(emprestimo.esta_ativo())
        self.assertTrue(self.exemplares[0].esta_disponivel())
        self.assertEqual([], self.sistema.listar_emprestimos_ativos())
        self.assertEqual(0, len(self.tela.tabela.get_children()))
        self.assertIn(
            self.exemplares[0],
            self.tela._exemplares_por_rotulo.values(),
        )
        self.assertEqual("Devolução registrada.", self.tela.feedback_var.get())

    def test_datas_invalidas_nao_alteram_estado(self):
        self._selecionar_membro()
        self._selecionar_exemplar(self.exemplares[0])
        self.tela.data_inicio_var.set("31/02/2026")

        self.tela._registrar()

        self.assertEqual([], self.sistema.listar_emprestimos_ativos())
        self.assertIn("DD/MM/AAAA", self.tela.feedback_var.get())

        emprestimo = self.sistema.registrar_emprestimo(
            self.membro,
            self.exemplares[0],
            DATA_INICIO,
        )
        self.tela.atualizar()
        item = f"emprestimo-{emprestimo.id_emprestimo}"
        self.tela.tabela.selection_set(item)
        self.tela._ao_selecionar(None)
        self.tela.data_devolucao_var.set("12/11/2026")

        self.tela._devolver()

        self.assertTrue(emprestimo.esta_ativo())
        self.assertFalse(self.exemplares[0].esta_disponivel())
        self.assertIn("anterior", self.tela.feedback_var.get())

    def test_rn01_e_mostrada_sem_duplicar_regra(self):
        self._selecionar_membro()
        self._selecionar_exemplar(self.exemplares[0])
        self.exemplares[0].marcar_emprestado()
        self.tela.data_inicio_var.set("13/11/2026")

        self.tela._registrar()

        self.assertEqual([], self.sistema.listar_emprestimos_ativos())
        self.assertIn("RN01", self.tela.feedback_var.get())

    def test_rn02_e_mostrada_sem_duplicar_regra(self):
        for exemplar in self.exemplares[:3]:
            self.sistema.registrar_emprestimo(
                self.membro,
                exemplar,
                DATA_INICIO,
            )
        self.tela.atualizar()
        self._selecionar_membro()
        self._selecionar_exemplar(self.exemplares[3])
        self.tela.data_inicio_var.set("13/11/2026")

        self.tela._registrar()

        self.assertEqual(3, len(self.sistema.listar_emprestimos_ativos()))
        self.assertTrue(self.exemplares[3].esta_disponivel())
        self.assertIn("RN02", self.tela.feedback_var.get())

    def test_listas_vazias_apresentam_estado_claro(self):
        self.tela.destroy()
        vazio = SistemaGameVault()
        self.tela = TelaEmprestimos(self.root, vazio)
        self.tela.pack(fill=tk.BOTH, expand=True)
        self.root.update_idletasks()

        self.assertEqual(SEM_MEMBROS, self.tela.membro_var.get())
        self.assertEqual(SEM_EXEMPLARES, self.tela.exemplar_var.get())
        self.assertEqual(0, len(self.tela.tabela.get_children()))
        self.assertTrue(self.tela.estado_vazio.place_info())

        self.tela._registrar()

        self.assertEqual("Selecione um membro.", self.tela.feedback_var.get())

    def test_converter_data_usa_formato_brasileiro(self):
        self.assertEqual(
            date(2026, 11, 13),
            converter_data("13/11/2026", "início"),
        )
        with self.assertRaises(ValueError):
            converter_data("2026-11-13", "início")


if __name__ == "__main__":
    unittest.main()
