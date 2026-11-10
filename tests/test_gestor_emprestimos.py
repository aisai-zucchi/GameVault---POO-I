import unittest
from datetime import date

from gamevault import Exemplar, GestorEmprestimos, Membro


class TestGestorEmprestimos(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorEmprestimos()
        self.membro = Membro(1, "Ana", "ana@example.com")
        self.exemplar = Exemplar("MC-001")
        self.inicio = date(2026, 11, 1)

    def _exemplares(self, quantidade: int) -> list[Exemplar]:
        return [Exemplar(f"EX-{numero:03}") for numero in range(quantidade)]

    # Registro com sucesso e efeitos colaterais
    def test_registrar_cria_emprestimo_ativo(self):
        emprestimo = self.gestor.registrar(self.membro, self.exemplar, self.inicio)

        self.assertEqual(1, emprestimo.id_emprestimo)
        self.assertIs(self.membro, emprestimo.membro)
        self.assertIs(self.exemplar, emprestimo.exemplar)
        self.assertEqual(self.inicio, emprestimo.data_inicio)
        self.assertTrue(emprestimo.esta_ativo())

    def test_registrar_marca_exemplar_emprestado_e_vincula_ao_membro(self):
        emprestimo = self.gestor.registrar(self.membro, self.exemplar, self.inicio)

        self.assertFalse(self.exemplar.esta_disponivel())
        self.assertEqual([emprestimo], self.membro.emprestimos)
        self.assertEqual(1, self.membro.contar_ativos())

    def test_ids_sao_sequenciais(self):
        primeiro, segundo = self._exemplares(2)

        id_primeiro = self.gestor.registrar(self.membro, primeiro, self.inicio).id_emprestimo
        id_segundo = self.gestor.registrar(self.membro, segundo, self.inicio).id_emprestimo

        self.assertEqual([1, 2], [id_primeiro, id_segundo])

    # RN01 - limite do membro
    def test_rn01_recusa_quarto_emprestimo_ativo(self):
        for exemplar in self._exemplares(3):
            self.gestor.registrar(self.membro, exemplar, self.inicio)
        quarto = Exemplar("EX-999")

        with self.assertRaises(ValueError):
            self.gestor.registrar(self.membro, quarto, self.inicio)

        self.assertTrue(quarto.esta_disponivel())
        self.assertEqual(3, len(self.gestor.listar_ativos()))
        self.assertEqual(3, len(self.gestor.listar_historico()))

    def test_rn01_libera_novo_emprestimo_apos_devolucao(self):
        emprestimos = [
            self.gestor.registrar(self.membro, exemplar, self.inicio)
            for exemplar in self._exemplares(3)
        ]
        self.gestor.devolver(emprestimos[0].id_emprestimo, date(2026, 11, 5))

        novo = self.gestor.registrar(self.membro, Exemplar("EX-999"), date(2026, 11, 6))

        self.assertTrue(novo.esta_ativo())
        self.assertEqual(3, self.membro.contar_ativos())

    def test_rn01_limite_vale_por_membro(self):
        outro = Membro(2, "Bia", "bia@example.com")
        for exemplar in self._exemplares(3):
            self.gestor.registrar(self.membro, exemplar, self.inicio)

        emprestimo = self.gestor.registrar(outro, Exemplar("EX-999"), self.inicio)

        self.assertTrue(emprestimo.esta_ativo())

    # RN02 - disponibilidade do exemplar
    def test_rn02_recusa_exemplar_indisponivel(self):
        self.exemplar.marcar_emprestado()

        with self.assertRaises(ValueError):
            self.gestor.registrar(self.membro, self.exemplar, self.inicio)

        self.assertEqual([], self.membro.emprestimos)
        self.assertEqual([], self.gestor.listar_historico())

    def test_impede_emprestimo_simultaneo_do_mesmo_exemplar(self):
        outro = Membro(2, "Bia", "bia@example.com")
        self.gestor.registrar(self.membro, self.exemplar, self.inicio)

        with self.assertRaises(ValueError):
            self.gestor.registrar(outro, self.exemplar, self.inicio)

        self.assertEqual([], outro.emprestimos)
        self.assertEqual(1, len(self.gestor.listar_ativos()))

    def test_impede_simultaneidade_mesmo_com_status_alterado_por_fora(self):
        self.gestor.registrar(self.membro, self.exemplar, self.inicio)
        self.exemplar.marcar_disponivel()

        with self.assertRaises(ValueError):
            self.gestor.registrar(Membro(2, "Bia", "bia@example.com"), self.exemplar, self.inicio)

    # Devolucao
    def test_devolver_finaliza_e_libera_exemplar(self):
        emprestimo = self.gestor.registrar(self.membro, self.exemplar, self.inicio)
        fim = date(2026, 11, 6)

        devolvido = self.gestor.devolver(emprestimo.id_emprestimo, fim)

        self.assertIs(emprestimo, devolvido)
        self.assertFalse(devolvido.esta_ativo())
        self.assertEqual(fim, devolvido.data_devolucao)
        self.assertTrue(self.exemplar.esta_disponivel())
        self.assertEqual(0, self.membro.contar_ativos())

    def test_exemplar_pode_ser_emprestado_novamente_apos_devolucao(self):
        outro = Membro(2, "Bia", "bia@example.com")
        primeiro = self.gestor.registrar(self.membro, self.exemplar, self.inicio)
        self.gestor.devolver(primeiro.id_emprestimo, date(2026, 11, 3))

        segundo = self.gestor.registrar(outro, self.exemplar, date(2026, 11, 4))

        self.assertTrue(segundo.esta_ativo())
        self.assertEqual(2, segundo.id_emprestimo)

    def test_devolver_com_data_anterior_ao_inicio_nao_altera_nada(self):
        emprestimo = self.gestor.registrar(self.membro, self.exemplar, self.inicio)

        with self.assertRaises(ValueError):
            self.gestor.devolver(emprestimo.id_emprestimo, date(2026, 10, 31))

        self.assertTrue(emprestimo.esta_ativo())
        self.assertFalse(self.exemplar.esta_disponivel())
        self.assertEqual([emprestimo], self.gestor.listar_ativos())

    def test_devolver_emprestimo_inexistente(self):
        with self.assertRaises(ValueError):
            self.gestor.devolver(99, date(2026, 11, 6))

    def test_nao_devolve_duas_vezes_o_mesmo_emprestimo(self):
        emprestimo = self.gestor.registrar(self.membro, self.exemplar, self.inicio)
        self.gestor.devolver(emprestimo.id_emprestimo, date(2026, 11, 3))
        self.exemplar.marcar_emprestado()  # exemplar em uso por outro fluxo

        with self.assertRaises(ValueError):
            self.gestor.devolver(emprestimo.id_emprestimo, date(2026, 11, 4))

        self.assertFalse(self.exemplar.esta_disponivel())
        self.assertEqual(date(2026, 11, 3), emprestimo.data_devolucao)

    # Listagens e historico
    def test_listar_ativos_exclui_devolvidos(self):
        primeiro, segundo = self._exemplares(2)
        devolvido = self.gestor.registrar(self.membro, primeiro, self.inicio)
        ativo = self.gestor.registrar(self.membro, segundo, self.inicio)
        self.gestor.devolver(devolvido.id_emprestimo, date(2026, 11, 3))

        self.assertEqual([ativo], self.gestor.listar_ativos())

    def test_historico_preserva_emprestimos_devolvidos(self):
        emprestimo = self.gestor.registrar(self.membro, self.exemplar, self.inicio)
        self.gestor.devolver(emprestimo.id_emprestimo, date(2026, 11, 3))

        self.assertEqual([], self.gestor.listar_ativos())
        self.assertEqual([emprestimo], self.gestor.listar_historico())
        self.assertEqual([emprestimo], self.membro.emprestimos)

    def test_listagens_sao_copias(self):
        self.gestor.registrar(self.membro, self.exemplar, self.inicio)

        self.gestor.listar_ativos().clear()
        self.gestor.listar_historico().clear()

        self.assertEqual(1, len(self.gestor.listar_ativos()))
        self.assertEqual(1, len(self.gestor.listar_historico()))


if __name__ == "__main__":
    unittest.main()
