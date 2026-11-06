from gamevault.modelos.categoria import Categoria
from gamevault.modelos.exemplar import Exemplar
from gamevault.modelos.jogo import Jogo, JogoDigital, JogoFisico


class Catalogo:
    def __init__(self):
        self._jogos: dict[int, Jogo] = {}
        self._categorias: dict[int, Categoria] = {}
        self._proximo_id_jogo = 1

    @property
    def jogos(self) -> list[Jogo]:
        return self.listar_jogos()

    @property
    def categorias(self) -> list[Categoria]:
        return self.listar_categorias()

    def cadastrar_jogo(self, jogo: Jogo) -> int:
        id_jogo = jogo.id_jogo
        if id_jogo is None:
            id_jogo = self._proximo_id_disponivel()
            jogo._atribuir_id(id_jogo)
        if id_jogo in self._jogos:
            raise ValueError("Já existe um jogo com este ID.")
        self._jogos[id_jogo] = jogo
        self._proximo_id_jogo = max(self._proximo_id_jogo, id_jogo + 1)
        return id_jogo

    def buscar_jogo(self, id_jogo: int) -> Jogo | None:
        return self._jogos.get(id_jogo)

    def listar_jogos(self) -> list[Jogo]:
        return list(self._jogos.values())

    def atualizar_jogo(
        self,
        id_jogo: int,
        titulo: str | None = None,
        ano: int | None = None,
        loja_origem: str | None = None,
    ) -> Jogo:
        jogo = self.buscar_jogo(id_jogo)
        if jogo is None:
            raise ValueError("Jogo não encontrado.")
        if loja_origem is not None:
            if not isinstance(jogo, JogoDigital):
                raise ValueError("Somente jogos digitais possuem loja de origem.")
            loja_origem = loja_origem.strip()
            if not loja_origem:
                raise ValueError("A loja de origem não pode ficar vazia.")
        jogo.atualizar_dados(titulo, ano)
        if loja_origem is not None:
            jogo.alterar_loja_origem(loja_origem)
        return jogo

    def excluir_jogo(self, id_jogo: int) -> Jogo:
        jogo = self.buscar_jogo(id_jogo)
        if jogo is None:
            raise ValueError("Jogo não encontrado.")
        if isinstance(jogo, JogoFisico) and any(
            not exemplar.esta_disponivel() for exemplar in jogo.exemplares
        ):
            raise ValueError(
                "Não é possível excluir um jogo com empréstimo ativo."
            )
        return self._jogos.pop(id_jogo)

    def cadastrar_categoria(self, categoria: Categoria) -> None:
        if categoria.id_categoria in self._categorias:
            raise ValueError("Já existe uma categoria com este ID.")
        self._categorias[categoria.id_categoria] = categoria

    def buscar_categoria(self, id_categoria: int) -> Categoria | None:
        return self._categorias.get(id_categoria)

    def listar_categorias(self) -> list[Categoria]:
        return list(self._categorias.values())

    def filtrar_jogos(
        self,
        titulo: str | None = None,
        ano: int | None = None,
        tipo: str | None = None,
    ) -> list[Jogo]:
        tipo_normalizado = tipo.casefold() if tipo is not None else None
        if tipo_normalizado not in (None, "fisico", "digital"):
            raise ValueError("O tipo deve ser 'fisico' ou 'digital'.")

        resultado = self.listar_jogos()
        if titulo is not None:
            termo = titulo.casefold()
            resultado = [jogo for jogo in resultado if termo in jogo.titulo.casefold()]
        if ano is not None:
            resultado = [jogo for jogo in resultado if jogo.ano == ano]
        if tipo_normalizado == "fisico":
            resultado = [jogo for jogo in resultado if isinstance(jogo, JogoFisico)]
        elif tipo_normalizado == "digital":
            resultado = [jogo for jogo in resultado if isinstance(jogo, JogoDigital)]
        return resultado

    def localizar_exemplar(self, codigo: str) -> Exemplar | None:
        codigo_normalizado = codigo.casefold()
        for jogo in self._jogos.values():
            if not isinstance(jogo, JogoFisico):
                continue
            for exemplar in jogo.exemplares:
                if exemplar.codigo.casefold() == codigo_normalizado:
                    return exemplar
        return None

    def cadastrar_exemplar(self, id_jogo: int, exemplar: Exemplar) -> None:
        jogo = self.buscar_jogo(id_jogo)
        if jogo is None:
            raise ValueError("Jogo não encontrado.")
        if not isinstance(jogo, JogoFisico):
            raise ValueError("Exemplares só podem ser adicionados a jogos físicos.")
        if self.localizar_exemplar(exemplar.codigo) is not None:
            raise ValueError("Já existe um exemplar com este código.")
        jogo.adicionar_exemplar(exemplar)

    def cadastrar(self, jogo: Jogo) -> int:
        return self.cadastrar_jogo(jogo)

    def buscar(self, id_jogo: int) -> Jogo | None:
        return self.buscar_jogo(id_jogo)

    def listar(self) -> list[Jogo]:
        return self.listar_jogos()

    def atualizar(
        self,
        id_jogo: int,
        titulo: str | None = None,
        ano: int | None = None,
        loja_origem: str | None = None,
    ) -> Jogo:
        return self.atualizar_jogo(id_jogo, titulo, ano, loja_origem)

    def excluir(self, id_jogo: int) -> Jogo:
        return self.excluir_jogo(id_jogo)

    def _proximo_id_disponivel(self) -> int:
        while self._proximo_id_jogo in self._jogos:
            self._proximo_id_jogo += 1
        return self._proximo_id_jogo
