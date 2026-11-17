import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE
from gamevault.modelos.membro import Membro
from gamevault.sistema import SistemaGameVault


class FormularioMembro(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        ao_salvar: Callable[[Membro], None] | None = None,
    ):
        super().__init__(master)
        self.sistema = sistema
        self.ao_salvar = ao_salvar
        self.id_var = tk.StringVar()
        self.nome_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.erro_var = tk.StringVar()

        self.title("Novo membro")
        self.geometry("480x440")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self.transient(master.winfo_toplevel())

        self._criar_conteudo()
        self.bind("<Escape>", lambda _evento: self.destroy())
        self._centralizar(480, 440)
        self.grab_set()
        self.campo_id.focus_set()

    def _criar_conteudo(self) -> None:
        cabecalho = tk.Frame(self, bg=CORES["fundo"])
        cabecalho.pack(fill=tk.X, padx=28, pady=(24, 18))
        tk.Label(
            cabecalho,
            text="Novo membro",
            bg=CORES["fundo"],
            fg=CORES["texto"],
            font=(FONTE, 20, "bold"),
        ).pack(anchor="w")
        tk.Label(
            cabecalho,
            text="Preencha os dados do cadastro.",
            bg=CORES["fundo"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9),
        ).pack(anchor="w", pady=(4, 0))

        formulario = tk.Frame(self, bg=CORES["fundo"])
        formulario.pack(fill=tk.BOTH, expand=True, padx=28)
        formulario.columnconfigure(0, weight=1)

        self.campo_id = self._criar_campo(
            formulario,
            0,
            "ID *",
            self.id_var,
        )
        self._criar_campo(formulario, 2, "Nome *", self.nome_var)
        self._criar_campo(formulario, 4, "E-mail *", self.email_var)

        tk.Label(
            formulario,
            textvariable=self.erro_var,
            bg=CORES["fundo"],
            fg=CORES["erro"],
            font=(FONTE, 9),
            justify=tk.LEFT,
            wraplength=410,
        ).grid(row=6, column=0, sticky="w", pady=(2, 8))

        acoes = tk.Frame(self, bg=CORES["fundo"])
        acoes.pack(fill=tk.X, padx=28, pady=(8, 24))
        ttk.Button(
            acoes,
            text="Cancelar",
            style="Secondary.TButton",
            command=self.destroy,
        ).pack(side=tk.RIGHT)
        ttk.Button(
            acoes,
            text="Cadastrar",
            style="Primary.TButton",
            command=self._salvar,
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def _criar_campo(
        self,
        master: tk.Misc,
        linha: int,
        rotulo: str,
        variavel: tk.StringVar,
    ) -> ttk.Entry:
        tk.Label(
            master,
            text=rotulo,
            bg=CORES["fundo"],
            fg=CORES["texto_secundario"],
            font=(FONTE, 9, "bold"),
        ).grid(row=linha, column=0, sticky="w", pady=(0, 5))
        campo = ttk.Entry(
            master,
            textvariable=variavel,
            style="Input.TEntry",
        )
        campo.grid(row=linha + 1, column=0, sticky="ew", pady=(0, 12))
        return campo

    def _salvar(self) -> None:
        try:
            try:
                id_membro = int(self.id_var.get().strip())
            except ValueError as erro:
                raise ValueError("O ID deve ser um número inteiro.") from erro
            membro = Membro(
                id_membro,
                self.nome_var.get(),
                self.email_var.get(),
            )
            if not self.sistema.cadastrar_membro(membro):
                raise ValueError("Já existe um membro com este ID.")
        except (TypeError, ValueError) as erro:
            self.erro_var.set(str(erro))
            return

        if self.ao_salvar is not None:
            self.ao_salvar(membro)
        self.destroy()

    def _centralizar(self, largura: int, altura: int) -> None:
        self.update_idletasks()
        pai = self.master.winfo_toplevel()
        x = pai.winfo_rootx() + max(0, (pai.winfo_width() - largura) // 2)
        y = pai.winfo_rooty() + max(0, (pai.winfo_height() - altura) // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")
