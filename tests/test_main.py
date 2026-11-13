"""Testes da demonstração executável do projeto."""

import importlib
import io
import sys
import unittest
from contextlib import redirect_stdout


class TestMain(unittest.TestCase):
    def test_importar_main_nao_executa_demonstracao(self):
        sys.modules.pop("main", None)
        saida = io.StringIO()

        with redirect_stdout(saida):
            importlib.import_module("main")

        self.assertEqual("", saida.getvalue())

    def test_main_demonstra_fluxo_completo(self):
        modulo = importlib.import_module("main")
        saida = io.StringIO()

        with redirect_stdout(saida):
            modulo.main()

        texto = saida.getvalue()
        self.assertIn("CATÁLOGO", texto)
        self.assertIn("Minecraft", texto)
        self.assertIn("Stardew Valley Expanded", texto)
        self.assertIn("BLOQUEIO RN01", texto)
        self.assertIn("BLOQUEIO RN02", texto)
        self.assertIn("EXCLUSÃO BLOQUEADA", texto)
        self.assertIn("DEVOLUÇÃO", texto)
        self.assertIn("HISTÓRICO DE EMPRÉSTIMOS", texto)
        self.assertIn("EMPRÉSTIMOS ATIVOS: 0", texto)
        self.assertIn("JOGOS RESTANTES: 1", texto)


if __name__ == "__main__":
    unittest.main()
