from datetime import date

from gamevault.modelos.categoria import Categoria
from gamevault.modelos.emprestimo import Emprestimo
from gamevault.modelos.exemplar import Exemplar
from gamevault.modelos.jogo import Jogo, JogoFisico
from gamevault.modelos.membro import Membro
from gamevault.servicos.cadastro_membros import CadastroMembros
from gamevault.servicos.catalogo import Catalogo
from gamevault.servicos.gestor_emprestimos import GestorEmprestimos


class SistemaGameVault:
    def __init__(
        self,
        catalogo: Catalogo | None = None,
        cadastro_membros: CadastroMembros | None = None,
        gestor_emprestimos: GestorEmprestimos | None = None,
    ):
        self._catalogo = catalogo if catalogo is not None else Catalogo()
        self._cadastro_membros = (
            cadastro_membros if cadastro_membros is not None else CadastroMembros()
        )
        self._gestor_emprestimos = (
            gestor_emprestimos
            if gestor_emprestimos is not None
            else GestorEmprestimos()
        )

    @property
    def catalogo(self) -> Catalogo:
        return self._catalogo

    @property
    def cadastro_membros(self) -> CadastroMembros:
        return self._cadastro_membros

    @property
    def gestor_emprestimos(self) -> GestorEmprestimos:
        return self._gestor_emprestimos

    def cadastrar_jogo(self, jogo: Jogo) -> int:
        return self._catalogo.cadastrar_jogo(jogo)

    def atualizar_jogo(
        self,
        id_jogo: int,
        titulo: str | None = None,
        ano: int | None = None,
        loja_origem: str | None = None,
        plataforma: str | None = None,
        id_categoria: int | None = None,
    ) -> Jogo:
        return self._catalogo.atualizar_jogo(
            id_jogo,
            titulo,
            ano,
            loja_origem,
            plataforma,
            id_categoria,
        )

    def cadastrar_categoria(self, categoria: Categoria) -> None:
        self._catalogo.cadastrar_categoria(categoria)

    def renomear_categoria(
        self,
        id_categoria: int,
        novo_nome: str,
    ) -> Categoria:
        return self._catalogo.renomear_categoria(id_categoria, novo_nome)

    def cadastrar_membro(self, membro: Membro) -> bool:
        return self._cadastro_membros.cadastrar(membro)

    def cadastrar_exemplar(self, id_jogo: int, exemplar: Exemplar) -> None:
        self._catalogo.cadastrar_exemplar(id_jogo, exemplar)

    def excluir_jogo(self, id_jogo: int) -> Jogo:
        jogo = self._catalogo.buscar_jogo(id_jogo)
        if jogo is None:
            raise ValueError("Jogo não encontrado.")
        if isinstance(jogo, JogoFisico) and any(
            emprestimo.esta_ativo()
            and any(
                emprestimo.exemplar is exemplar
                for exemplar in jogo.exemplares
            )
            for emprestimo in self._gestor_emprestimos.emprestimos
        ):
            raise ValueError(
                "Não é possível excluir um jogo com empréstimo ativo."
            )
        return self._catalogo.excluir_jogo(id_jogo)

    def registrar_emprestimo(
        self,
        membro: Membro | int,
        exemplar: Exemplar | str,
        data_inicio: date | None = None,
    ) -> Emprestimo:
        membro_cadastrado = self._resolver_membro(membro)
        exemplar_cadastrado = self._resolver_exemplar(exemplar)
        return self._gestor_emprestimos.registrar(
            membro_cadastrado,
            exemplar_cadastrado,
            data_inicio,
        )

    def devolver_emprestimo(
        self,
        id_emprestimo: int,
        data_devolucao: date | None = None,
    ) -> bool:
        return self._gestor_emprestimos.devolver(id_emprestimo, data_devolucao)

    def listar_emprestimos_ativos(self) -> list[Emprestimo]:
        return self._gestor_emprestimos.listar_ativos()

    def _resolver_membro(self, membro: Membro | int) -> Membro:
        if isinstance(membro, Membro):
            cadastrado = self._cadastro_membros.buscar(membro.id_membro)
            if cadastrado is not membro:
                raise ValueError("O membro informado não está cadastrado no sistema.")
            return cadastrado
        if isinstance(membro, bool) or not isinstance(membro, int):
            raise TypeError("Informe um membro ou um ID de membro válido.")

        cadastrado = self._cadastro_membros.buscar(membro)
        if cadastrado is None:
            raise ValueError("O membro informado não está cadastrado no sistema.")
        return cadastrado

    def _resolver_exemplar(self, exemplar: Exemplar | str) -> Exemplar:
        if isinstance(exemplar, Exemplar):
            cadastrado = self._catalogo.localizar_exemplar(exemplar.codigo)
            if cadastrado is not exemplar:
                raise ValueError("O exemplar informado não pertence ao acervo.")
            return cadastrado
        if not isinstance(exemplar, str):
            raise TypeError("Informe um exemplar ou um código de exemplar válido.")

        cadastrado = self._catalogo.localizar_exemplar(exemplar)
        if cadastrado is None:
            raise ValueError("O exemplar informado não pertence ao acervo.")
        return cadastrado
