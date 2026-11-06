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

    def test_main_exibe_catalogo(self):
        modulo = importlib.import_module("main")
        saida = io.StringIO()

        with redirect_stdout(saida):
            modulo.main()

        self.assertIn("Minecraft - Exemplares disponíveis: 1", saida.getvalue())
        self.assertIn("Stardew Valley - Jogo digital - somente catalogo", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
