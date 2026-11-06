class Exemplar:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.status = "disponivel"

    def esta_disponivel(self) -> bool:
        return self.status == "disponivel"

    def marcar_emprestado(self) -> None:
        if not self.esta_disponivel():
            raise ValueError("O exemplar não está disponível.")
        self.status = "emprestado"

    def marcar_disponivel(self) -> None:
        self.status = "disponivel"
