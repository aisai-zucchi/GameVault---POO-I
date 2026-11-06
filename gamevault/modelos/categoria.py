class Categoria:
    def __init__(self, id_categoria: int, nome: str):
        self.id_categoria = id_categoria
        self.nome = nome

    def renomear(self, novo_nome: str) -> None:
        if not novo_nome.strip():
            raise ValueError("O nome da categoria não pode ficar vazio.")
        self.nome = novo_nome
