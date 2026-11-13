from gamevault.modelos.membro import Membro


class CadastroMembros:
    def __init__(self):
        self._membros: list[Membro] = []

    @property
    def membros(self) -> list[Membro]:
        return self._membros.copy()

    def cadastrar(self, membro: Membro) -> bool:
        if not isinstance(membro, Membro):
            raise TypeError("Apenas membros válidos podem ser cadastrados.")
        if self.buscar(membro.id_membro) is not None:
            return False
        self._membros.append(membro)
        return True

    def buscar(self, id_membro: int) -> Membro | None:
        for membro in self._membros:
            if membro.id_membro == id_membro:
                return membro
        return None

    def listar(self) -> list[Membro]:
        return self._membros.copy()
