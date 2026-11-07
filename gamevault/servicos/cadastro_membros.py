from gamevault.modelos.membro import Membro


class CadastroMembros:
    def __init__(self):
        self.membros: list[Membro] = []

    def cadastrar(self, membro: Membro) -> bool:
        if self.buscar(membro.id_membro) is not None:
            return False
        self.membros.append(membro)
        return True

    def buscar(self, id_membro: int) -> Membro | None:
        for membro in self.membros:
            if membro.id_membro == id_membro:
                return membro
        return None

    def listar(self) -> list[Membro]:
        return self.membros.copy()
