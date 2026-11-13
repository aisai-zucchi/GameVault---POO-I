class Exemplar:
    DISPONIVEL = "disponivel"
    EMPRESTADO = "emprestado"

    def __init__(self, codigo: str):
        if not isinstance(codigo, str):
            raise TypeError("O código do exemplar deve ser um texto.")
        codigo = codigo.strip()
        if not codigo:
            raise ValueError("O código do exemplar não pode ficar vazio.")
        self._codigo = codigo
        self._status = self.DISPONIVEL

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def status(self) -> str:
        return self._status

    def esta_disponivel(self) -> bool:
        return self._status == self.DISPONIVEL

    def marcar_emprestado(self) -> None:
        if not self.esta_disponivel():
            raise ValueError("O exemplar não está disponível.")
        self._status = self.EMPRESTADO

    def marcar_disponivel(self) -> None:
        self._status = self.DISPONIVEL

    def atualizar_status(self, novo_status: str) -> None:
        if novo_status == self.DISPONIVEL:
            self.marcar_disponivel()
            return
        if novo_status == self.EMPRESTADO:
            self.marcar_emprestado()
            return
        raise ValueError("O status deve ser 'disponivel' ou 'emprestado'.")
