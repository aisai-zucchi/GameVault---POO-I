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
        if not isinstance(jogo, Jogo):
            raise TypeError("Apenas jogos válidos podem ser cadastrados.")
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
        plataforma: str | None = None,
        id_categoria: int | None = None,
    ) -> Jogo:
        jogo = self.buscar_jogo(id_jogo)
        if jogo is None:
            raise ValueError("Jogo não encontrado.")
        categoria = None
        if id_categoria is not None:
            categoria = self.buscar_categoria(id_categoria)
            if categoria is None:
                raise ValueError("Categoria não encontrada.")
        if loja_origem is not None:
            if not isinstance(jogo, JogoDigital):
                raise ValueError("Somente jogos digitais possuem loja de origem.")
            loja_origem = loja_origem.strip()
            if not loja_origem:
                raise ValueError("A loja de origem não pode ficar vazia.")
        jogo.atualizar_dados(titulo, ano, plataforma)
        if loja_origem is not None:
            jogo.alterar_loja_origem(loja_origem)
        if categoria is not None:
            jogo.definir_categoria(categoria)
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
        if not isinstance(categoria, Categoria):
            raise TypeError("Apenas categorias válidas podem ser cadastradas.")
        if categoria.id_categoria in self._categorias:
            raise ValueError("Já existe uma categoria com este ID.")
        self._categorias[categoria.id_categoria] = categoria

    def buscar_categoria(self, id_categoria: int) -> Categoria | None:
        return self._categorias.get(id_categoria)

    def listar_categorias(self) -> list[Categoria]:
        return list(self._categorias.values())

    def renomear_categoria(
        self,
        id_categoria: int,
        novo_nome: str,
    ) -> Categoria:
        categoria = self.buscar_categoria(id_categoria)
        if categoria is None:
            raise ValueError("Categoria não encontrada.")
        categoria.renomear(novo_nome)
        return categoria

    def filtrar_jogos(
        self,
        titulo: str | None = None,
        ano: int | None = None,
        tipo: str | None = None,
        categoria: Categoria | int | str | None = None,
        plataforma: str | None = None,
    ) -> list[Jogo]:
        if titulo is not None and not isinstance(titulo, str):
            raise TypeError("O título da consulta deve ser um texto.")
        if tipo is not None and not isinstance(tipo, str):
            raise TypeError("O tipo da consulta deve ser um texto.")
        if categoria is not None and (
            isinstance(categoria, bool)
            or not isinstance(categoria, (Categoria, int, str))
        ):
            raise TypeError("A categoria deve ser informada por objeto, ID ou nome.")
        if plataforma is not None and not isinstance(plataforma, str):
            raise TypeError("A plataforma da consulta deve ser um texto.")

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
        if categoria is not None:
            resultado = [
                jogo
                for jogo in resultado
                if self._corresponde_categoria(jogo, categoria)
            ]
        if plataforma is not None:
            termo_plataforma = plataforma.casefold()
            resultado = [
                jogo
                for jogo in resultado
                if jogo.plataforma is not None
                and jogo.plataforma.casefold() == termo_plataforma
            ]
        return resultado

    def localizar_exemplar(self, codigo: str) -> Exemplar | None:
        if not isinstance(codigo, str):
            raise TypeError("O código do exemplar deve ser um texto.")
        codigo_normalizado = codigo.strip().casefold()
        if not codigo_normalizado:
            raise ValueError("O código do exemplar não pode ficar vazio.")
        for jogo in self._jogos.values():
            if not isinstance(jogo, JogoFisico):
                continue
            for exemplar in jogo.exemplares:
                if exemplar.codigo.casefold() == codigo_normalizado:
                    return exemplar
        return None

    def cadastrar_exemplar(self, id_jogo: int, exemplar: Exemplar) -> None:
        if not isinstance(exemplar, Exemplar):
            raise TypeError("Apenas exemplares válidos podem ser cadastrados.")
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
        plataforma: str | None = None,
        id_categoria: int | None = None,
    ) -> Jogo:
        return self.atualizar_jogo(
            id_jogo,
            titulo,
            ano,
            loja_origem,
            plataforma,
            id_categoria,
        )

    def excluir(self, id_jogo: int) -> Jogo:
        return self.excluir_jogo(id_jogo)

    def _proximo_id_disponivel(self) -> int:
        while self._proximo_id_jogo in self._jogos:
            self._proximo_id_jogo += 1
        return self._proximo_id_jogo

    @staticmethod
    def _corresponde_categoria(
        jogo: Jogo,
        categoria: Categoria | int | str,
    ) -> bool:
        categoria_jogo = jogo.categoria
        if categoria_jogo is None:
            return False
        if isinstance(categoria, Categoria):
            return categoria_jogo is categoria
        if isinstance(categoria, bool):
            return False
        if isinstance(categoria, int):
            return categoria_jogo.id_categoria == categoria
        if isinstance(categoria, str):
            return categoria_jogo.nome.casefold() == categoria.casefold()
        raise TypeError("A categoria deve ser informada por objeto, ID ou nome.")
