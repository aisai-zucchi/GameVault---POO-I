"""Testes integrados das regras de negócio do GameVault."""

import unittest
from datetime import date

from gamevault import (
    CadastroMembros,
    Catalogo,
    Categoria,
    Emprestimo,
    Exemplar,
    GestorEmprestimos,
    JogoDigital,
    JogoFisico,
    Membro,
    SistemaGameVault,
)


DATA_INICIO = date(2026, 11, 13)
DATA_DEVOLUCAO = date(2026, 11, 14)


class TestEmprestimo(unittest.TestCase):
    def setUp(self):
        self.membro = Membro(1, "Ana", "ana@example.com")
        self.exemplar = Exemplar("MC-001")
        self.emprestimo = Emprestimo(
            1,
            self.membro,
            self.exemplar,
            DATA_INICIO,
        )

    def test_cria_emprestimo_ativo_com_associacoes(self):
        self.assertEqual(1, self.emprestimo.id_emprestimo)
        self.assertIs(self.membro, self.emprestimo.membro)
        self.assertIs(self.exemplar, self.emprestimo.exemplar)
        self.assertEqual(DATA_INICIO, self.emprestimo.data_inicio)
        self.assertIsNone(self.emprestimo.data_devolucao)
        self.assertTrue(self.emprestimo.esta_ativo())

    def test_propriedades_sao_somente_leitura(self):
        atributos = {
            "id_emprestimo": 2,
            "membro": Membro(2, "Bia", "bia@example.com"),
            "exemplar": Exemplar("MC-002"),
            "data_inicio": DATA_DEVOLUCAO,
            "data_devolucao": DATA_DEVOLUCAO,
        }
        for atributo, valor in atributos.items():
            with self.subTest(atributo=atributo):
                with self.assertRaises(AttributeError):
                    setattr(self.emprestimo, atributo, valor)

    def test_finaliza_na_mesma_data_do_inicio(self):
        self.emprestimo.finalizar(DATA_INICIO)

        self.assertFalse(self.emprestimo.esta_ativo())
        self.assertEqual(DATA_INICIO, self.emprestimo.data_devolucao)

    def test_recusa_data_anterior_sem_alterar_estado(self):
        with self.assertRaises(ValueError):
            self.emprestimo.finalizar(date(2026, 11, 12))

        self.assertTrue(self.emprestimo.esta_ativo())
        self.assertIsNone(self.emprestimo.data_devolucao)

    def test_recusa_segunda_finalizacao_e_preserva_historico(self):
        self.emprestimo.finalizar(DATA_DEVOLUCAO)

        with self.assertRaises(ValueError):
            self.emprestimo.finalizar(date(2026, 11, 15))

        self.assertEqual(DATA_DEVOLUCAO, self.emprestimo.data_devolucao)


class TestGestorEmprestimos(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorEmprestimos()
        self.membro = Membro(1, "Ana", "ana@example.com")

    def test_registrar_atualiza_exemplar_e_historicos(self):
        exemplar = Exemplar("MC-001")

        emprestimo = self.gestor.registrar(self.membro, exemplar, DATA_INICIO)

        self.assertEqual(1, emprestimo.id_emprestimo)
        self.assertFalse(exemplar.esta_disponivel())
        self.assertEqual([emprestimo], self.membro.emprestimos)
        self.assertEqual([emprestimo], self.gestor.emprestimos)
        self.assertEqual([emprestimo], self.gestor.listar_ativos())

    def test_rn01_recusa_exemplar_indisponivel_sem_efeitos(self):
        exemplar = Exemplar("MC-001")
        exemplar.marcar_emprestado()

        with self.assertRaisesRegex(ValueError, "RN01"):
            self.gestor.registrar(self.membro, exemplar, DATA_INICIO)

        self.assertEqual([], self.gestor.emprestimos)
        self.assertEqual([], self.membro.emprestimos)

    def test_rn01_consulta_historico_ativo_mesmo_com_status_adulterado(self):
        exemplar = Exemplar("MC-001")
        primeiro = self.gestor.registrar(self.membro, exemplar, DATA_INICIO)
        exemplar.marcar_disponivel()

        with self.assertRaisesRegex(ValueError, "RN01"):
            self.gestor.registrar(self.membro, exemplar, DATA_INICIO)

        self.assertEqual([primeiro], self.gestor.emprestimos)

    def test_rn02_recusa_quarto_ativo_sem_consumir_id(self):
        exemplares = [Exemplar(f"MC-{numero:03d}") for numero in range(1, 5)]
        emprestimos = [
            self.gestor.registrar(self.membro, exemplar, DATA_INICIO)
            for exemplar in exemplares[:3]
        ]

        with self.assertRaisesRegex(ValueError, "RN02"):
            self.gestor.registrar(self.membro, exemplares[3], DATA_INICIO)

        self.assertTrue(exemplares[3].esta_disponivel())
        self.assertEqual(3, len(self.gestor.emprestimos))
        self.gestor.devolver(emprestimos[0].id_emprestimo, DATA_DEVOLUCAO)
        novo = self.gestor.registrar(self.membro, exemplares[3], DATA_DEVOLUCAO)
        self.assertEqual(4, novo.id_emprestimo)

    def test_devolucao_retroativa_preserva_emprestimo_e_status(self):
        exemplar = Exemplar("MC-001")
        emprestimo = self.gestor.registrar(self.membro, exemplar, DATA_INICIO)

        with self.assertRaises(ValueError):
            self.gestor.devolver(emprestimo.id_emprestimo, date(2026, 11, 12))

        self.assertTrue(emprestimo.esta_ativo())
        self.assertFalse(exemplar.esta_disponivel())

    def test_devolver_libera_exemplar_e_preserva_historico(self):
        exemplar = Exemplar("MC-001")
        primeiro = self.gestor.registrar(self.membro, exemplar, DATA_INICIO)

        self.assertTrue(self.gestor.devolver(primeiro.id_emprestimo, DATA_DEVOLUCAO))
        segundo = self.gestor.registrar(self.membro, exemplar, DATA_DEVOLUCAO)

        self.assertFalse(exemplar.esta_disponivel())
        self.assertEqual([primeiro, segundo], self.gestor.emprestimos)
        self.assertEqual([primeiro, segundo], self.membro.emprestimos)
        self.assertEqual([segundo], self.gestor.listar_ativos())

    def test_devolver_inexistente_ou_finalizado_retorna_falso(self):
        exemplar = Exemplar("MC-001")
        emprestimo = self.gestor.registrar(self.membro, exemplar, DATA_INICIO)

        self.assertFalse(self.gestor.devolver(999, DATA_DEVOLUCAO))
        self.assertTrue(self.gestor.devolver(emprestimo.id_emprestimo, DATA_DEVOLUCAO))
        self.assertFalse(self.gestor.devolver(emprestimo.id_emprestimo, DATA_DEVOLUCAO))

    def test_listagens_sao_copias(self):
        emprestimo = self.gestor.registrar(
            self.membro,
            Exemplar("MC-001"),
            DATA_INICIO,
        )

        historico = self.gestor.emprestimos
        ativos = self.gestor.listar_ativos()
        historico.clear()
        ativos.clear()

        self.assertEqual([emprestimo], self.gestor.emprestimos)
        self.assertEqual([emprestimo], self.gestor.listar_ativos())


class TestSistemaGameVault(unittest.TestCase):
    def setUp(self):
        self.catalogo = Catalogo()
        self.cadastro = CadastroMembros()
        self.gestor = GestorEmprestimos()
        self.sistema = SistemaGameVault(
            self.catalogo,
            self.cadastro,
            self.gestor,
        )
        self.membro = Membro(1, "Ana", "ana@example.com")
        self.jogo = JogoFisico("Minecraft", 2011)
        self.exemplar = Exemplar("MC-001")
        self.id_jogo = self.sistema.cadastrar_jogo(self.jogo)
        self.sistema.cadastrar_exemplar(self.id_jogo, self.exemplar)
        self.sistema.cadastrar_membro(self.membro)

    def test_integra_servicos_e_registra_por_id_e_codigo(self):
        emprestimo = self.sistema.registrar_emprestimo(
            self.membro.id_membro,
            self.exemplar.codigo,
            DATA_INICIO,
        )

        self.assertIs(self.catalogo, self.sistema.catalogo)
        self.assertIs(self.cadastro, self.sistema.cadastro_membros)
        self.assertIs(self.gestor, self.sistema.gestor_emprestimos)
        self.assertIs(self.membro, emprestimo.membro)
        self.assertIs(self.exemplar, emprestimo.exemplar)

    def test_fachada_gerencia_jogo_e_categoria(self):
        categoria = Categoria(1, "Aventura")
        self.sistema.cadastrar_categoria(categoria)
        digital = JogoDigital("Stardew", 2015, "GOG")
        id_digital = self.sistema.cadastrar_jogo(digital)

        atualizado = self.sistema.atualizar_jogo(
            id_digital,
            titulo="Stardew Valley",
            ano=2016,
            loja_origem="Steam",
            plataforma="PC",
            id_categoria=1,
        )
        renomeada = self.sistema.renomear_categoria(1, "Indie")

        self.assertIs(digital, atualizado)
        self.assertEqual("Stardew Valley", digital.titulo)
        self.assertEqual("Steam", digital.loja_origem)
        self.assertIs(categoria, renomeada)
        self.assertEqual("Indie", categoria.nome)

    def test_recusa_membro_nao_cadastrado(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_emprestimo(999, self.exemplar, DATA_INICIO)

        impostor = Membro(1, "Impostor", "impostor@example.com")
        with self.assertRaises(ValueError):
            self.sistema.registrar_emprestimo(impostor, self.exemplar, DATA_INICIO)

    def test_recusa_exemplar_fora_do_acervo(self):
        with self.assertRaises(ValueError):
            self.sistema.registrar_emprestimo(
                self.membro,
                "INEXISTENTE",
                DATA_INICIO,
            )

        impostor = Exemplar(self.exemplar.codigo)
        with self.assertRaises(ValueError):
            self.sistema.registrar_emprestimo(self.membro, impostor, DATA_INICIO)

    def test_emprestimo_bloqueia_exclusao_ate_a_devolucao(self):
        emprestimo = self.sistema.registrar_emprestimo(
            self.membro,
            self.exemplar,
            DATA_INICIO,
        )

        self.exemplar.marcar_disponivel()
        with self.assertRaises(ValueError):
            self.sistema.excluir_jogo(self.id_jogo)

        self.assertTrue(
            self.sistema.devolver_emprestimo(
                emprestimo.id_emprestimo,
                DATA_DEVOLUCAO,
            )
        )
        self.assertIs(self.jogo, self.sistema.excluir_jogo(self.id_jogo))


class TestRelacoesEConsultas(unittest.TestCase):
    def test_categoria_e_plataforma_sao_objetos_e_dados_consultaveis(self):
        catalogo = Catalogo()
        aventura = Categoria(1, "Aventura")
        rpg = Categoria(2, "RPG")
        catalogo.cadastrar_categoria(aventura)
        catalogo.cadastrar_categoria(rpg)
        fisico = JogoFisico(
            "Minecraft",
            2011,
            plataforma="PC",
            categoria=aventura,
        )
        digital = JogoDigital(
            "Stardew Valley",
            2016,
            "Steam",
            plataforma="PC",
            categoria=rpg,
        )
        id_fisico = catalogo.cadastrar_jogo(fisico)
        catalogo.cadastrar_jogo(digital)

        self.assertIs(aventura, fisico.categoria)
        self.assertEqual([fisico], catalogo.filtrar_jogos(categoria=1))
        self.assertEqual([digital], catalogo.filtrar_jogos(categoria="rpg"))
        self.assertEqual([fisico, digital], catalogo.filtrar_jogos(plataforma="pc"))

        catalogo.atualizar_jogo(id_fisico, plataforma="Switch", id_categoria=2)
        self.assertEqual("Switch", fisico.plataforma)
        self.assertIs(rpg, fisico.categoria)

    def test_polimorfismo_produz_resumos_distintos(self):
        fisico = JogoFisico("Minecraft", 2011)
        fisico.adicionar_exemplar(Exemplar("MC-001"))
        digital = JogoDigital("Stardew Valley", 2016, "Steam")

        resumos = [jogo.resumo_disponibilidade() for jogo in (fisico, digital)]

        self.assertEqual("Exemplares disponíveis: 1", resumos[0])
        self.assertEqual("Jogo digital - somente catalogo", resumos[1])


if __name__ == "__main__":
    unittest.main()
