class Categoria:
    def __init__(self, id_categoria: int, nome: str):
        self._id_categoria = id_categoria
        self._nome = self._validar_nome(nome)

    @property
    def id_categoria(self) -> int:
        return self._id_categoria

    @property
    def nome(self) -> str:
        return self._nome

    def renomear(self, novo_nome: str) -> None:
        self._nome = self._validar_nome(novo_nome)

    @staticmethod
    def _validar_nome(nome: str) -> str:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome da categoria não pode ficar vazio.")
        return nome
