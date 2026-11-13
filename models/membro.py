class Membro:
    def __init__(self, id_membro: int, nome: str, email: str):
        self.id_membro = id_membro
        self.nome = nome
        self.email = email
        self.emprestimos = []

    def contar_ativos(self) -> int:
        return sum(1 for emp in self.emprestimos if emp.esta_ativo())

    def pode_emprestar(self) -> bool:
        return self.contar_ativos() < 3
