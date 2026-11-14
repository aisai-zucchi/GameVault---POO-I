import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from gamevault.interface.estilos import CORES, FONTE
from gamevault.modelos.exemplar import Exemplar
from gamevault.modelos.jogo import JogoFisico
from gamevault.sistema import SistemaGameVault


class FormularioExemplar(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        sistema: SistemaGameVault,
        jogo: JogoFisico,
        ao_salvar: Callable[[Exemplar], None] | None = None,
    ):
        if not isinstance(jogo, JogoFisico):
            raise TypeError("Exemplares só podem ser adicionados a jogos físicos.")
        super().__init__(master)
        self.sistema = sistema
        self.jogo = jogo
        self.ao_salvar = ao_salvar
        self.codigo_var = tk.StringVar()
        self.erro_var = tk.StringVar()

        self.title("Adicionar exemplar")
        self.geometry("430x285")
        self.resizable(False, False)
        self.configure(bg=CORES["fundo"])
        self.transient(master.winfo_toplevel())
        self.columnconfigure(0, weight=1)

        self._criar_conteudo()
        self.bind("<Escape>", lambda _evento: self.destroy())
        self._centralizar(430, 285)
        self._ativar()

    def _criar_conteudo(self) -> None:
        ttk.Label(
            self,
            text="Novo exemplar",
            style="PageTitle.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(22, 2))
        ttk.Label(
            self,
            text=self.jogo.titulo,
            style="PageSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 15))

        card = tk.Frame(
            self,
            bg=CORES["superficie"],
            highlightthickness=1,
            highlightbackground=CORES["borda"],
            padx=14,
            pady=13,
        )
        card.grid(row=2, column=0, sticky="ew", padx=24)
        card.columnconfigure(0, weight=1, uniform="acoes")
        card.columnconfigure(1, weight=1, uniform="acoes")

        tk.Label(
            card,
            text="CÓDIGO *",
            bg=CORES["superficie"],
            fg=CORES["texto_sutil"],
            font=(FONTE, 8, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.campo_codigo = ttk.Entry(
            card,
            textvariable=self.codigo_var,
            style="Input.TEntry",
        )
        self.campo_codigo.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.erro = tk.Label(
            card,
            textvariable=self.erro_var,
            bg=CORES["superficie"],
            fg=CORES["erro"],
            font=(FONTE, 9),
            anchor="w",
        )
        self.erro.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(7, 8))

        ttk.Button(
            card,
            text="Cancelar",
            style="Secondary.TButton",
            command=self.destroy,
        ).grid(row=3, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(
            card,
            text="Adicionar",
            style="Primary.TButton",
            command=self._salvar,
        ).grid(row=3, column=1, sticky="ew", padx=(5, 0))

    def _ativar(self) -> None:
        if not self.winfo_exists():
            return
        self.grab_set()
        self.campo_codigo.focus_set()

    def _centralizar(self, largura: int, altura: int) -> None:
        self.update_idletasks()
        pai = self.master.winfo_toplevel()
        x = pai.winfo_rootx() + max(0, (pai.winfo_width() - largura) // 2)
        y = pai.winfo_rooty() + max(0, (pai.winfo_height() - altura) // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _salvar(self) -> None:
        try:
            if self.jogo.id_jogo is None:
                raise ValueError("O jogo precisa estar cadastrado.")
            exemplar = Exemplar(self.codigo_var.get())
            self.sistema.cadastrar_exemplar(self.jogo.id_jogo, exemplar)
        except (TypeError, ValueError) as erro:
            self.erro_var.set(str(erro))
            return

        if self.ao_salvar is not None:
            self.ao_salvar(exemplar)
        self.destroy()
