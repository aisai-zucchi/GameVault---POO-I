import unittest
from datetime import date
import sys
import os

# Adiciona o diretório principal ao caminho para encontrar a pasta models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.emprestimo import Emprestimo

class TestEmprestimo(unittest.TestCase):
    def setUp(self):
        self.emprestimo = Emprestimo(
            id_emprestimo=1,
            membro="Membro Mock",
            exemplar="Exemplar Mock",
            data_inicio=date(2026, 11, 1)
        )

    def test_inicializacao_emprestimo_ativo(self):
        self.assertEqual(self.emprestimo.id_emprestimo, 1)
        self.assertTrue(self.emprestimo.esta_ativo())
        self.assertIsNone(self.emprestimo.data_devolucao)

    def test_finalizar_emprestimo_com_sucesso(self):
        data_fim = date(2026, 11, 6)
        self.emprestimo.finalizar(data_fim)
        self.assertFalse(self.emprestimo.esta_ativo())
        self.assertEqual(self.emprestimo.data_devolucao, data_fim)

    def test_finalizar_com_data_retroativa_levanta_excecao(self):
        data_invalida = date(2026, 10, 31)
        with self.assertRaises(ValueError):
            self.emprestimo.finalizar(data_invalida)

if __name__ == '__main__':
    unittest.main()