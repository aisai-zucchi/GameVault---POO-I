class Exemplar:
    def __init__(self, codigo: str):
        codigo = codigo.strip()
        if not codigo:
            raise ValueError("O código do exemplar não pode ficar vazio.")
        self._codigo = codigo
        self._status = "disponivel"

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def status(self) -> str:
        return self._status

    def esta_disponivel(self) -> bool:
        return self._status == "disponivel"

    def marcar_emprestado(self) -> None:
        if not self.esta_disponivel():
            raise ValueError("O exemplar não está disponível.")
        self._status = "emprestado"

    def marcar_disponivel(self) -> None:
        self._status = "disponivel"
