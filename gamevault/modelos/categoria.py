class Categoria:
    def __init__(self, id_categoria: int, nome: str):
        self._id_categoria = self._validar_id(id_categoria)
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
    def _validar_id(id_categoria: int) -> int:
        if isinstance(id_categoria, bool) or not isinstance(id_categoria, int):
            raise TypeError("O ID da categoria deve ser um número inteiro.")
        if id_categoria <= 0:
            raise ValueError("O ID da categoria deve ser positivo.")
        return id_categoria

    @staticmethod
    def _validar_nome(nome: str) -> str:
        if not isinstance(nome, str):
            raise TypeError("O nome da categoria deve ser um texto.")
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome da categoria não pode ficar vazio.")
        return nome
